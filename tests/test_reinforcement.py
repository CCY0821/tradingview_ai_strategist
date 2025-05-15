from core.reinforcement import GATrainer, StrategyGenome
from core.backtest_runner import BacktestRunner
from core.scorer import BaseScorer

class DummyRunner:
    def run_backtest(self, code): return None

class DummyScorer(BaseScorer):
    def score(self, _: any): return 0.5

def test_ga_trainer():
    trainer = GATrainer(runner=DummyRunner(), scorer=DummyScorer())
    pop = [{"code":"a","score":0,"meta":{}} for _ in range(10)]
    new_pop = trainer.train_epoch(pop)
    assert all(isinstance(g, dict) and "code" in g and "score" in g for g in new_pop)
