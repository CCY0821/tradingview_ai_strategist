"""core/controller.py
====================
Orchestrates full pipeline: generate strategies, back‑test, score, evolve, and persist to database.

Usage:
    python -m core.controller --mode ga --generations 10 --pop-size 20

Functions:
- initialize_db(): Create tables
- run_pipeline(): Single run of GA/PPO loop and persistence
- main(): CLI entrypoint
"""
import argparse
import logging
from core.strategy_generator import generate_strategy
from core.backtest_runner import run_backtest, BacktestResult
from core.scorer import scorer_factory, DefaultScorer, ScoreConfig
from core.reinforcement import TrainerFactory
from database.db_handler import init_db
from database.strategy_db import save_strategy

logger = logging.getLogger(__name__)


def initialize_db():
    init_db()
    logger.info("Database initialized.")


def run_pipeline(mode: str, generations: int, pop_size: int):
    # Configure trainer
    trainer = TrainerFactory.create(mode)
    # Initial population: generate random strategies
    population = []
    for i in range(pop_size):
        code = generate_strategy(f"隨機生成策略 {i}")
        population.append({'code': code, 'score': 0.0, 'meta': {}})

    # Evolution loop
    for gen in range(1, generations + 1):
        logger.info(f"=== Generation {gen} ===")
        population = trainer.train_epoch(population)
        # Persist top strategy
        best = max(population, key=lambda g: g['score'])
        save_strategy(generation=gen, score=best['score'], code=best['code'], meta=best.get('meta'))
        logger.info(f"Saved best strategy of gen {gen} with score {best['score']}")

    # Final best
    final_best = max(population, key=lambda g: g['score'])
    logger.info(f"=== Final best strategy score: {final_best['score']} ===")
    print(final_best['code'])


def main():
    parser = argparse.ArgumentParser(description="TradingView Strategy Evolver")
    parser.add_argument('--mode', choices=['ga', 'ppo'], default='ga', help='Training mode')
    parser.add_argument('--generations', type=int, default=5, help='Number of generations')
    parser.add_argument('--pop-size', type=int, default=10, help='Population size')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    initialize_db()
    run_pipeline(args.mode, args.generations, args.pop_size)


if __name__ == '__main__':
    main()
