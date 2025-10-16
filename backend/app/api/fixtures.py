
from fastapi import APIRouter
from app.services.fixtures import SAMPLE_QUERIES, FIXTURE_ENGINES

router = APIRouter()

@router.get("/queries", response_model=list[str])
def sample_queries():
    return SAMPLE_QUERIES

@router.get("/engines", response_model=list[str])
def engines():
    return FIXTURE_ENGINES
