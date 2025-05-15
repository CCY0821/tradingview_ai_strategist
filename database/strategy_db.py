"""database/strategy_db.py
Provides functions to persist and query TradingView strategy backtest runs."""
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from database.models import Strategy as StrategyModel
from database.db_handler import get_session

def save_strategy(
    generation: int,
    score: float,
    code: str,
    meta: Optional[Dict[str, Any]] = None
) -> None:
    """Save a backtest strategy run into the database."""
    session: Session = get_session()
    record = StrategyModel(
        generation=generation,
        score=score,
        code=code,
        meta=meta or {},
    )
    session.add(record)
    session.commit()
    session.close()

def get_strategies(
    generation: Optional[int] = None,
    limit: Optional[int] = None
) -> List[StrategyModel]:
    """
    Retrieve strategies, optionally filtering by generation and limiting count.

    By default, only strategies with generation >= 1 are returned to exclude
    placeholder or pre-test records.
    """
    session: Session = get_session()
    query = session.query(StrategyModel)

    # Default filter: only real generations (>=1)
    if generation is None:
        query = query.filter(StrategyModel.generation >= 1)
    else:
        query = query.filter(StrategyModel.generation == generation)

    if limit is not None:
        query = query.order_by(StrategyModel.score.desc()).limit(limit)

    results = query.all()
    session.close()
    return results

__all__ = ["save_strategy", "get_strategies"]
