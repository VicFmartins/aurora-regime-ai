"""Backtesting namespace."""

from aurora.backtest.benchmarks import (
    build_benchmark_equity_curve,
    build_benchmark_suite,
    build_buy_and_hold_benchmark,
    build_cash_benchmark,
    build_equal_weight_benchmark,
    build_static_allocation_benchmark,
)
from aurora.backtest.engine import BacktestResult, run_backtest

__all__ = [
    "BacktestResult",
    "build_benchmark_equity_curve",
    "build_benchmark_suite",
    "build_buy_and_hold_benchmark",
    "build_cash_benchmark",
    "build_equal_weight_benchmark",
    "build_static_allocation_benchmark",
    "run_backtest",
]
