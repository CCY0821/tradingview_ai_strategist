import os
import pytest
from database.strategy_db import save_strategy, get_strategies
from database.db_handler import init_db

@pytest.fixture(autouse=True)
def use_memory_db(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    init_db()
    yield

def test_save_and_get_single():
    save_strategy(1, 1.23, "code", {"a":1})
    results = get_strategies()
    assert len(results) == 1
    rec = results[0]
    assert rec.generation == 1
    assert pytest.approx(rec.score) == 1.23
    assert rec.code == "code"
    assert rec.meta == {"a":1}

def test_get_with_filters():
    # 多筆不同 generation
    save_strategy(1, 0.1, "c1", {})
    save_strategy(2, 0.2, "c2", {})
    res1 = get_strategies(generation=1)
    assert all(r.generation == 1 for r in res1)
    top1 = get_strategies(limit=1)
    assert len(top1) == 1
