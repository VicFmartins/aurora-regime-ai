"""Performance summary tables for Aurora strategies and benchmarks."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from aurora.analysis.metrics import (
    compute_annualized_return,
    compute_annualized_volatility,
    compute_best_period_return,
    compute_calmar_ratio,
    compute_cumulative_return,
    compute_hit_rate,
    compute_max_drawdown,
    compute_sharpe_ratio,
    compute_worst_period_return,
)
from aurora.config import ProjectConfig, load_config


def summarize_performance(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series | pd.DataFrame,
    *,
    risk_free_rate: float = 0.0,
    rebalance_log: pd.DataFrame | None = None,
    periods_per_year: int = 12,
) -> pd.DataFrame:
    """Build a performance summary table for strategy and benchmarks."""
    frames = {"strategy": strategy_returns}
    frames.update(_coerce_benchmark_frames(benchmark_returns))

    summary_rows = {
        name: _summarize_single_series(
            returns=returns,
            risk_free_rate=risk_free_rate,
            rebalance_log=rebalance_log if name == "strategy" else None,
            periods_per_year=periods_per_year,
        )
        for name, returns in frames.items()
    }
    return pd.DataFrame.from_dict(summary_rows, orient="index")


def build_performance_table(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series | pd.DataFrame,
    *,
    config: ProjectConfig | None = None,
    risk_free_rate: float = 0.0,
    rebalance_log: pd.DataFrame | None = None,
    periods_per_year: int = 12,
) -> pd.DataFrame:
    """Build the summary table and export it to CSV under reports/tables."""
    resolved_config = config or load_config()
    summary = summarize_performance(
        strategy_returns=strategy_returns,
        benchmark_returns=benchmark_returns,
        risk_free_rate=risk_free_rate,
        rebalance_log=rebalance_log,
        periods_per_year=periods_per_year,
    )

    output_path = Path(resolved_config.reports_tables_dir) / "performance_summary.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=True)
    return summary


def _coerce_benchmark_frames(
    benchmark_returns: pd.Series | pd.DataFrame,
) -> dict[str, pd.Series]:
    if isinstance(benchmark_returns, pd.Series):
        name = benchmark_returns.name or "benchmark"
        return {name: benchmark_returns}
    return {str(column): benchmark_returns[column] for column in benchmark_returns.columns}


def _summarize_single_series(
    *,
    returns: pd.Series,
    risk_free_rate: float,
    rebalance_log: pd.DataFrame | None,
    periods_per_year: int,
) -> dict[str, float]:
    return {
        "cumulative_return": compute_cumulative_return(returns),
        "annualized_return": compute_annualized_return(
            returns,
            periods_per_year=periods_per_year,
        ),
        "annualized_volatility": compute_annualized_volatility(
            returns,
            periods_per_year=periods_per_year,
        ),
        "sharpe_ratio": compute_sharpe_ratio(
            returns,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
        ),
        "max_drawdown": compute_max_drawdown(returns),
        "calmar_ratio": compute_calmar_ratio(
            returns,
            periods_per_year=periods_per_year,
        ),
        "hit_rate": compute_hit_rate(returns),
        "best_month": compute_best_period_return(returns),
        "worst_month": compute_worst_period_return(returns),
        "num_rebalances": _get_num_rebalances(rebalance_log),
        "average_turnover": _get_average_turnover(rebalance_log),
    }


def _get_num_rebalances(rebalance_log: pd.DataFrame | None) -> float:
    if rebalance_log is None:
        return float("nan")
    return float(len(rebalance_log))


def _get_average_turnover(rebalance_log: pd.DataFrame | None) -> float:
    if rebalance_log is None or "turnover" not in rebalance_log.columns or rebalance_log.empty:
        return float("nan")
    return float(rebalance_log["turnover"].mean())
