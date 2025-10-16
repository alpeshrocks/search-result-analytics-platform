
from .session import SessionLocal, engine, Base
from .models import Query, Run, Result, Metric, Annotation
from .session import get_db

def init_db():
    Base.metadata.create_all(bind=engine)
