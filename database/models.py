"""database/models.py
=====================
SQLAlchemy ORM models for persisting backtest strategies and results."""
from sqlalchemy import Column, Integer, Float, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Strategy(Base):  # type: ignore[name-defined]
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    generation = Column(Integer, nullable=False, index=True)
    score = Column(Float, nullable=False, index=True)
    code = Column(Text, nullable=False)#Pine Script
    meta = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Strategy id={self.id} gen={self.generation} score={self.score:.4f}>"
