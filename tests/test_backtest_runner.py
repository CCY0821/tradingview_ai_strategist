import pytest
from core.backtest_runner import run_backtest, BacktestResult

def test_run_backtest_with_dummy_runner(monkeypatch):
    """
    模擬 BacktestRunner 執行，確保 run_backtest 回傳正確的 BacktestResult 物件
    """
    # DummyRunner 只回傳一個預先定義的 BacktestResult
    class DummyRunner:
        def run_backtest(self, code: str) -> BacktestResult:
            return BacktestResult(
                net_profit_pct=1.0,
                max_drawdown_pct=0.2,
                profit_factor=1.5,
                sharpe_ratio=2.0,
                total_trades=10,
                win_rate=0.6
            )

    # 替換 core.backtest_runner.BacktestRunner
    monkeypatch.setattr("core.backtest_runner.BacktestRunner", lambda: DummyRunner())

    # 呼叫 run_backtest，傳入任意 Pine Script
    result = run_backtest("dummy pine script")

    # 驗證回傳型別與各欄位值
    assert isinstance(result, BacktestResult)
    assert result.net_profit_pct == 1.0
    assert result.max_drawdown_pct == 0.2
    assert result.profit_factor == 1.5
    assert result.sharpe_ratio == 2.0
    assert result.total_trades == 10
    assert result.win_rate == pytest.approx(0.6)
