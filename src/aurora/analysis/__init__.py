"""Performance analysis utilities for Aurora backtests."""

from aurora.analysis.metrics import (
    compute_annualized_return,
    compute_annualized_volatility,
    compute_calmar_ratio,
    compute_cumulative_return,
    compute_hit_rate,
    compute_max_drawdown,
    compute_sharpe_ratio,
)
from aurora.analysis.tables import build_performance_table, summarize_performance

__all__ = [
    "build_performance_table",
    "compute_annualized_return",
    "compute_annualized_volatility",
    "compute_calmar_ratio",
    "compute_cumulative_return",
    "compute_hit_rate",
    "compute_max_drawdown",
    "compute_sharpe_ratio",
    "summarize_performance",
]
