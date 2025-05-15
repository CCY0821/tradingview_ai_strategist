from core.scorer import DefaultScorer, ScoreConfig
from core.result_extractor import BacktestResult

def test_default_scorer():
    cfg = ScoreConfig(profit_w=1, drawdown_w=1, sharpe_w=1, winrate_w=1, tradecount_w=1)
    scorer = DefaultScorer(cfg)
    br = BacktestResult(net_profit_pct=10, max_drawdown_pct=5, sharpe_ratio=2, total_trades=100, win_rate=0.6)
    score = scorer.score(br)
    assert 0 <= score <= 5
