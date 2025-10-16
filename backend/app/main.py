
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import queries, runs, analytics, fixtures
from app.db import init_db

app = FastAPI(title="SERP Lab API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(queries.router, prefix="/queries", tags=["queries"])
app.include_router(runs.router, prefix="/runs", tags=["runs"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(fixtures.router, prefix="/fixtures", tags=["fixtures"])
