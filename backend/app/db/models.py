
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.session import Base

def gen_uuid():
    return str(uuid.uuid4())

class Query(Base):
    __tablename__ = "query"
    id = Column(String, primary_key=True, default=gen_uuid)
    text = Column(Text, nullable=False)
    locale = Column(String, default="en-US")
    country = Column(String, default="US")
    device = Column(String, default="desktop")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    runs = relationship("Run", back_populates="query")

class Run(Base):
    __tablename__ = "run"
    id = Column(String, primary_key=True, default=gen_uuid)
    query_id = Column(String, ForeignKey("query.id"), nullable=False)
    engine = Column(String)  # 'google', 'bing', 'brave', 'fixture'
    params = Column(JSON)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    status = Column(String)  # 'ok','error','partial'
    error = Column(Text)

    query = relationship("Query", back_populates="runs")
    results = relationship("Result", back_populates="run", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="run", cascade="all, delete-orphan")

class Result(Base):
    __tablename__ = "result"
    id = Column(String, primary_key=True, default=gen_uuid)
    run_id = Column(String, ForeignKey("run.id"), nullable=False)
    position = Column(Integer)
    url = Column(Text)
    domain = Column(Text)
    title = Column(Text)
    snippet = Column(Text)
    type = Column(String)  # 'organic','ad','news','video','map_pack','paa'
    extra = Column(JSON)

    run = relationship("Run", back_populates="results")

class Metric(Base):
    __tablename__ = "metric"
    id = Column(String, primary_key=True, default=gen_uuid)
    run_id = Column(String, ForeignKey("run.id"), nullable=False)
    name = Column(String)
    value = Column(Float)
    meta = Column(JSON)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    run = relationship("Run", back_populates="metrics")

class Annotation(Base):
    __tablename__ = "annotation"
    id = Column(String, primary_key=True, default=gen_uuid)
    query_id = Column(String, ForeignKey("query.id"), nullable=False)
    label = Column(String)   # e.g., 'intent=informational'
    source = Column(String)  # 'heuristic','llm','manual'
    confidence = Column(Float)
