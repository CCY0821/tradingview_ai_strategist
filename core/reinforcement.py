"""core/reinforcement.py
===================
Evolutionary and reinforcement‑learning training loops that iteratively
**generate → back‑test → score → evolve** Pine Script trading strategies.

Provides:
- Genetic Algorithm (GA) trainer
- Scaffolding for Proximal Policy Optimization (PPO) trainer
"""
import logging
import random
from typing import List, Dict, Any

from core.backtest_runner import BacktestRunner
from core.scorer import BaseScorer, scorer_factory

logger = logging.getLogger(__name__)

StrategyGenome = Dict[str, Any]

class BaseTrainer:
    """Abstract trainer interface."""
    def train_epoch(self, population: List[StrategyGenome]) -> List[StrategyGenome]:
        raise NotImplementedError

class GATrainer(BaseTrainer):
    """Simple Genetic Algorithm trainer."""
    def __init__(self, runner: BacktestRunner = None, scorer: BaseScorer = None):
        self.runner = runner or BacktestRunner()
        self.scorer = scorer or scorer_factory()
        # default GA params; could be loaded from config
        self.elitism_rate = 0.2
        self.crossover_rate = 0.5
        self.mutation_rate = 0.1

    def train_epoch(self, population: List[StrategyGenome]) -> List[StrategyGenome]:
        # Sort by score descending
        sorted_pop = sorted(population, key=lambda g: g["score"], reverse=True)
        elite_count = max(1, int(len(sorted_pop) * self.elitism_rate))
        new_pop = sorted_pop[:elite_count]

        # Generate children
        while len(new_pop) < len(population):
            parent1, parent2 = random.sample(sorted_pop[:elite_count], 2)
            # Crossover
            if random.random() < self.crossover_rate:
                cut = len(parent1["code"]) // 2
                child_code = parent1["code"][ :cut] + parent2["code"][cut: ]
            else:
                child_code = parent1["code"]
            # Mutation
            if random.random() < self.mutation_rate:
                child_code += "\n// mutation"
            # Evaluate
            result = self.runner.run_backtest(child_code)
            score = self.scorer.score(result)
            new_pop.append({"code": child_code, "score": score, "meta": {}})
        return new_pop

class PPOTrainer(BaseTrainer):
    """Placeholder for PPO trainer."""
    def __init__(self, runner: BacktestRunner = None, scorer: BaseScorer = None):
        self.runner = runner or BacktestRunner()
        self.scorer = scorer or scorer_factory()

    def train_epoch(self, population: List[StrategyGenome]) -> List[StrategyGenome]:
        logger.info("PPOTrainer: not implemented; returning input population.")
        return population

class TrainerFactory:
    """Factory for creating trainers based on mode."""
    @staticmethod
    def get_trainer(mode: str) -> BaseTrainer:
        if mode == "ga":
            return GATrainer()
        elif mode == "ppo":
            return PPOTrainer()
        else:
            raise ValueError(f"Unknown training mode: {mode}")
