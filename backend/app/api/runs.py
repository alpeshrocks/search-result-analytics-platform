
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models import Run, Result, Query, Metric
from app.services.engines import fetch_results
from app.services.metrics import compute_all_metrics
from datetime import datetime

router = APIRouter()

class RunCreate(BaseModel):
    query_id: str
    engine: str = "fixture"   # 'fixture','bing','google','brave','serpapi'
    params: dict | None = None
    k: int = 10

@router.post("", response_model=dict)
def create_run(payload: RunCreate, db: Session = Depends(get_db)):
    q = db.query(Query).get(payload.query_id)
    if not q:
        raise HTTPException(404, "query not found")
    run = Run(query_id=q.id, engine=payload.engine, params=payload.params or {}, status="ok")
    db.add(run)
    db.commit(); db.refresh(run)

    try:
        results = fetch_results(engine=payload.engine, query_text=q.text, params=payload.params or {}, k=payload.k)
        # persist results
        for i, r in enumerate(results, start=1):
            db.add(Result(run_id=run.id, position=i, url=r["url"], domain=r["domain"], title=r["title"], snippet=r.get("snippet",""), type=r.get("type","organic"), extra=r.get("extra",{})))
        run.finished_at = datetime.utcnow()
        db.commit()
        # compute metrics
        compute_all_metrics(db, run.id)
        db.commit()
    except Exception as e:
        run.status = "error"
        run.error = str(e)
        db.commit()
        raise

    return {"run_id": run.id}

@router.get("/{run_id}", response_model=dict)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).get(run_id)
    if not run:
        raise HTTPException(404, "run not found")
    results = db.query(Result).filter(Result.run_id==run.id).order_by(Result.position).all()
    metrics = db.query(Metric).filter(Metric.run_id==run.id).all()
    return {
        "id": run.id,
        "query_id": run.query_id,
        "engine": run.engine,
        "status": run.status,
        "started_at": str(run.started_at) if run.started_at else None,
        "finished_at": str(run.finished_at) if run.finished_at else None,
        "results": [{
            "position": r.position, "url": r.url, "domain": r.domain, "title": r.title, "snippet": r.snippet, "type": r.type
        } for r in results],
        "metrics": [{ "name": m.name, "value": m.value, "meta": m.meta } for m in metrics]
    }
