"""core.scorer
===============
Score a TradingView back‑test result with a single scalar **fitness value** for
use by the evolutionary or reinforcement‑learning engine.

The module fulfils the user's design constraints:
* **SRP** – one purpose: convert a `BacktestResult` into a number.
* **OCP** – extend by inheriting `BaseScorer` without modifying existing code.
* **DIP** – high‑level GA/PPO loops depend on the abstract `BaseScorer`.
* **Google‑style docstrings** and straightforward logging.

Example
-------
```python
from core.result_extractor import BacktestResult
from core.scorer import scorer_factory

result = BacktestResult(
    net_profit_pct=25.4,
    max_drawdown_pct=-7.8,
    profit_factor=2.31,
    sharpe_ratio=1.42,
    total_trades=85,
    win_rate=0.64,
)

scorer = scorer_factory()
print(scorer.score(result))  # → 0.83 (depends on config)
```
"""

from __future__ import annotations

import logging
import math
import pathlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Final, Protocol

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None  # graceful degradation if PyYAML not installed

from core.result_extractor import BacktestResult

__all__: Final = [
    "ScoreConfig",
    "BaseScorer",
    "DefaultScorer",
    "scorer_factory",
]

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

_CONFIG_PATH: Final = pathlib.Path(__file__).with_suffix(".yaml")


def _load_yaml_config() -> dict[str, float]:
    """Load weight coefficients from *scorer.yaml* if present and PyYAML available."""
    if not _CONFIG_PATH.exists() or yaml is None:  # pragma: no cover
        return {}

    try:
        with _CONFIG_PATH.open("r", encoding="utf-8") as fh:
            data: dict[str, float] | None = yaml.safe_load(fh)
            return data or {}
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to load scorer config: %s", exc)
        return {}


@dataclass(slots=True, frozen=True)
class ScoreConfig:
    """Weight coefficients for composing the fitness score."""

    profit_w: float = 0.35  #: Weight for *net profit %*
    drawdown_w: float = 0.25  #: Weight for *max drawdown %* (negative contribution)
    sharpe_w: float = 0.20  #: Weight for *Sharpe ratio*
    winrate_w: float = 0.15  #: Weight for *win rate*
    tradecount_w: float = 0.05  #: Weight for *total trades* (promotes liquidity)

    @classmethod
    def from_yaml(cls) -> "ScoreConfig":  # pragma: no cover
        """Create a :class:`ScoreConfig` from ``scorer.yaml`` (if available)."""
        data = _load_yaml_config()
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})  # type: ignore[arg-type]


class BaseScorer(ABC):
    """Abstract scorer interface for dependency inversion purposes."""

    @abstractmethod
    def score(self, result: BacktestResult) -> float:  # noqa: D401
        """Return a fitness value in the closed interval ``[0, 1]``."""


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _clamp01(value: float) -> float:
    """Clamp *value* into the closed unit interval ``[0, 1]``."""
    return max(0.0, min(1.0, value))


def _safe_div(numerator: float, denominator: float, *, default: float = 0.0) -> float:
    """Division that returns *default* when *denominator* is zero."""
    return numerator / denominator if denominator else default


# ---------------------------------------------------------------------------
# Default scorer implementation
# ---------------------------------------------------------------------------

class DefaultScorer(BaseScorer):
    """Default weighted‑sum scorer with linear normalisation of metrics."""

    #: Empirical boundaries for min/max normalisation (can be tuned)
    _MAX_PROFIT: Final = 100.0  # +100 % net profit
    _MIN_DRAWDOWN: Final = -50.0  # –50 % drawdown
    _MAX_SHARPE: Final = 3.0
    _MAX_TRADECOUNT: Final = 500

    def __init__(self, config: ScoreConfig | None = None) -> None:  # noqa: D401
        self._cfg: Final = config or ScoreConfig.from_yaml()

    # ---------------------------------------------------------------------
    # BaseScorer API
    # ---------------------------------------------------------------------

    def score(self, result: BacktestResult) -> float:  # noqa: D401
        """Compute the scalar fitness score in ``[0, 1]``.

        Parameters
        ----------
        result
            Parsed back‑test statistics.

        Returns
        -------
        float
            A value where **1.0** is ideal and **0.0** is the worst.
        """
        p = _clamp01(result.net_profit_pct / self._MAX_PROFIT)
        dd = _clamp01(1.0 - _safe_div(abs(result.max_drawdown_pct), abs(self._MIN_DRAWDOWN)))
        s = _clamp01(result.sharpe_ratio / self._MAX_SHARPE)
        wr = _clamp01(result.win_rate)
        tc = _clamp01(result.total_trades / self._MAX_TRADECOUNT)

        logger.debug("Normalised metrics – profit=%.3f drawdown=%.3f sharpe=%.3f"
                     " winrate=%.3f trades=%.3f", p, dd, s, wr, tc)

        cfg = self._cfg
        score = (
            p * cfg.profit_w
            + dd * cfg.drawdown_w
            + s * cfg.sharpe_w
            + wr * cfg.winrate_w
            + tc * cfg.tradecount_w
        )
        score = _clamp01(score)
        logger.debug("Computed fitness score: %.3f", score)
        return score


# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------

def scorer_factory(config: ScoreConfig | None = None) -> BaseScorer:  # noqa: D401
    """Return the default scorer.

    This wrapper exists to keep the creation site in one place so that future
    custom scorers (e.g. non‑linear, ML‑based) can be injected via config.
    """
    return DefaultScorer(config)
