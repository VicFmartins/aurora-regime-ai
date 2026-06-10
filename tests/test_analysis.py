from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from aurora.analysis import (
    build_performance_table,
    compute_annualized_return,
    compute_annualized_volatility,
    compute_cumulative_return,
    compute_hit_rate,
    compute_max_drawdown,
    compute_sharpe_ratio,
    summarize_performance,
)
from aurora.config import ProjectConfig


def test_metrics_compute_expected_values() -> None:
    returns = pd.Series(
        [0.10, -0.05, 0.02],
        index=pd.date_range("2024-01-31", periods=3, freq="ME"),
    )

    assert compute_cumulative_return(returns) == pytest.approx(0.0659)
    assert compute_annualized_return(returns, periods_per_year=12) == pytest.approx(0.2908204847)
    assert compute_annualized_volatility(returns, periods_per_year=12) == pytest.approx(
        0.2122891110
    )
    assert compute_max_drawdown(returns) == pytest.approx(-0.05)
    assert compute_hit_rate(returns) == pytest.approx(2.0 / 3.0)


def test_sharpe_ratio_returns_nan_for_zero_volatility() -> None:
    returns = pd.Series(
        [0.01, 0.01, 0.01],
        index=pd.date_range("2024-01-31", periods=3, freq="ME"),
    )

    sharpe = compute_sharpe_ratio(returns, periods_per_year=12)

    assert pd.isna(sharpe)


def test_summarize_performance_builds_dataframe() -> None:
    strategy_returns = pd.Series(
        [0.10, -0.05, 0.02],
        index=pd.date_range("2024-01-31", periods=3, freq="ME"),
        name="strategy",
    )
    benchmark_returns = pd.DataFrame(
        {
            "buy_and_hold": [0.08, -0.02, 0.01],
            "cash": [0.01, 0.01, 0.01],
        },
        index=strategy_returns.index,
    )
    rebalance_log = pd.DataFrame({"turnover": [1.0, 0.4, 0.2]})

    summary = summarize_performance(
        strategy_returns=strategy_returns,
        benchmark_returns=benchmark_returns,
        rebalance_log=rebalance_log,
    )

    assert list(summary.index) == ["strategy", "buy_and_hold", "cash"]
    assert "sharpe_ratio" in summary.columns
    assert summary.loc["strategy", "num_rebalances"] == pytest.approx(3.0)
    assert summary.loc["strategy", "average_turnover"] == pytest.approx((1.0 + 0.4 + 0.2) / 3.0)
    assert pd.isna(summary.loc["buy_and_hold", "num_rebalances"])


def test_build_performance_table_exports_csv(tmp_path: Path) -> None:
    strategy_returns = pd.Series(
        [0.10, -0.05, 0.02],
        index=pd.date_range("2024-01-31", periods=3, freq="ME"),
        name="strategy",
    )
    benchmark_returns = pd.Series(
        [0.08, -0.02, 0.01],
        index=strategy_returns.index,
        name="buy_and_hold",
    )
    config = ProjectConfig(reports_tables_dir=tmp_path / "tables")

    summary = build_performance_table(
        strategy_returns=strategy_returns,
        benchmark_returns=benchmark_returns,
        config=config,
    )

    output_path = config.reports_tables_dir / "performance_summary.csv"
    assert output_path.exists()
    exported = pd.read_csv(output_path, index_col=0)
    assert "cumulative_return" in summary.columns
    assert "cumulative_return" in exported.columns
