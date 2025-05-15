"""core/result_extractor.py
====================
Utilities for extracting numerical performance metrics from a TradingView
back‑test HTML report.

Dependencies:
- No external HTML parser required; uses regex.
"""
import re
from dataclasses import dataclass
from typing import Dict

@dataclass
class BacktestResult:
    net_profit_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    total_trades: int
    win_rate: float
    profit_factor: float = 0.0  # Default to 0.0 if not provided


def _parse_number(s: str) -> float:
    s = s.strip().replace(',', '')
    if s.endswith('%'):
        return float(s.rstrip('%'))
    return float(s)


def extract_from_html(html: str) -> Dict[str, float]:
    """Extract metrics from TradingView backtest HTML string."""
    fields = {
        'net_profit_pct': r'Net profit[\s\S]*?>([\d\.]+)%',
        'max_drawdown_pct': r'Max drawdown[\s\S]*?>([\d\.]+)%',
        'profit_factor': r'Profit factor[\s\S]*?>([\d\.]+)',
        'sharpe_ratio': r'Sharpe ratio[\s\S]*?>([\d\.]+)',
        'total_trades': r'Total closed trades[\s\S]*?>(\d+)',
        'win_rate': r'Win rate[\s\S]*?>([\d\.]+)%',
    }
    results: Dict[str, float] = {}
    for key, pattern in fields.items():
        m = re.search(pattern, html, re.IGNORECASE)
        if not m:
            raise ValueError(f"Could not extract {key} from HTML")
        value = m.group(1)
        results[key] = int(value) if key == 'total_trades' else float(value)
    return results
