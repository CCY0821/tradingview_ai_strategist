"""core/controller.py
====================
Orchestrates full pipeline: generate → back-test → score → evolve, and persist.

Usage:
    python core/controller.py --mode ga --generations 10 --pop-size 20 --verbose
"""
import argparse
import logging
from core.strategy_generator import generate_strategy
from core.backtest_runner import run_backtest, BacktestResult
from core.scorer import scorer_factory
from core.reinforcement import TrainerFactory
from database.db_handler import init_db
from database.strategy_db import save_strategy


def create_initial_population(size: int):
    """Generate an initial population of random Pine Script strategies."""
    population = []
    for _ in range(size):
        code = generate_strategy("產生一個隨機 Pine Script 策略")
        population.append({"code": code, "score": 0.0, "meta": {}})
    return population


def run_pipeline(mode: str, generations: int, pop_size: int, verbose: bool):
    """Run the full GA/PPO pipeline and persist results to the database."""
    init_db()
    trainer = TrainerFactory.get_trainer(mode)
    population = create_initial_population(pop_size)
    for gen in range(1, generations + 1):
        if verbose:
            logging.info(f"=== Generation {gen} ===")
        population = trainer.train_epoch(population)
        for indiv in population:
            save_strategy(
                generation=gen,
                score=indiv.get("score", 0.0),
                code=indiv.get("code", ""),
                meta=indiv.get("meta", {}),
            )
    if verbose:
        logging.info("Pipeline completed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["ga", "ppo"], required=True)
    parser.add_argument("--generations", type=int, required=True)
    parser.add_argument("--pop-size", type=int, required=True)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    run_pipeline(args.mode, args.generations, args.pop_size, args.verbose)


if __name__ == "__main__":
    main()
