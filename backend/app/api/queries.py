
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Query

router = APIRouter()

class QueryCreate(BaseModel):
    text: str
    locale: str = "en-US"
    country: str = "US"
    device: str = "desktop"

@router.post("", response_model=dict)
def create_query(payload: QueryCreate, db: Session = Depends(get_db)):
    q = Query(text=payload.text, locale=payload.locale, country=payload.country, device=payload.device)
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"id": q.id}

@router.get("", response_model=list[dict])
def list_queries(db: Session = Depends(get_db)):
    rows = db.query(Query).order_by(Query.created_at.desc()).all()
    return [{
        "id": r.id, "text": r.text, "locale": r.locale, "country": r.country, "device": r.device, "created_at": str(r.created_at)
    } for r in rows]

@router.delete("/{qid}", response_model=dict)
def delete_query(qid: str, db: Session = Depends(get_db)):
    q = db.query(Query).get(qid)
    if not q:
        raise HTTPException(404, "query not found")
    db.delete(q)
    db.commit()
    return {"ok": True}
