import os
import pytest
from sqlalchemy import inspect
from database.db_handler import init_db, get_engine, get_session

@pytest.fixture(autouse=True)
def use_memory_db(monkeypatch):
    # 在記憶體裡初始化資料庫
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    yield

def test_init_db_creates_tables():
    # init_db 後，應該有 strategies 表
    init_db()
    engine = get_engine()  # ← 改用 get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "strategies" in tables

def test_get_session_returns_session():
    init_db()
    sess = get_session()
    # Session 必須可新增並查詢
    from database.models import Strategy
    new = Strategy(generation=0, score=0.0, code="x", meta={})
    sess.add(new)
    sess.commit()
    assert sess.query(Strategy).count() == 1
    sess.close()
