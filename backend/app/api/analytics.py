
from fastapi import APIRouter, Depends, HTTPException, Query as QParam
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models import Run, Result, Metric

router = APIRouter()

@router.get("/metrics/time_series", response_model=list[dict])
def metrics_time_series(name: str = "ndcg@10", db: Session = Depends(get_db)):
    rows = db.query(Metric).filter(Metric.name==name).order_by(Metric.computed_at).all()
    return [{"run_id": r.run_id, "value": r.value, "computed_at": str(r.computed_at)} for r in rows]

@router.get("/compare", response_model=dict)
def compare_runs(a: str, b: str, db: Session = Depends(get_db)):
    ra = db.query(Run).get(a); rb = db.query(Run).get(b)
    if not (ra and rb): 
        raise HTTPException(404, "run not found")
    # fetch their results
    def to_map(run_id):
        rows = db.query(Result).filter(Result.run_id==run_id).all()
        return { r.url: r.position for r in rows }
    A = to_map(a); B = to_map(b)
    # simple overlap & displacement
    overlap = sorted(set(A.keys()) & set(B.keys()))
    displacement = { url: abs(A[url]-B[url]) for url in overlap }
    churn_k = len(set(A.keys()) ^ set(B.keys()))
    return {
        "overlap_count": len(overlap),
        "overlap_urls": overlap[:50],
        "avg_displacement": sum(displacement.values())/len(displacement) if displacement else 0.0,
        "churn": churn_k
    }
