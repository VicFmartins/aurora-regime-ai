from __future__ import annotations

import pandas as pd
import pytest

from aurora.backtest import (
    build_benchmark_equity_curve,
    build_benchmark_suite,
    build_buy_and_hold_benchmark,
    build_cash_benchmark,
    build_equal_weight_benchmark,
    build_static_allocation_benchmark,
)
from aurora.config import ProjectConfig


def test_buy_and_hold_benchmark_matches_main_risk_asset_returns() -> None:
    config = ProjectConfig()
    prices = _build_prices()
    align_to = prices.index[1:]

    benchmark = build_buy_and_hold_benchmark(config=config, prices=prices, align_to=align_to)

    expected = pd.Series(
        [0.10, 0.10, 0.10],
        index=align_to,
        name="buy_and_hold__BOVA11.SA",
    )
    pd.testing.assert_series_equal(benchmark, expected)


def test_cash_benchmark_uses_cdi_when_available() -> None:
    config = ProjectConfig()
    prices = _build_prices()
    align_to = prices.index[1:]

    benchmark = build_cash_benchmark(config=config, prices=prices, align_to=align_to)

    expected = pd.Series(
        [0.01, 0.01, 0.01],
        index=align_to,
        name="cash__CDI",
    )
    pd.testing.assert_series_equal(benchmark, expected)


def test_static_allocation_benchmark_respects_same_window() -> None:
    config = ProjectConfig()
    prices = _build_prices()
    align_to = prices.index[2:]

    benchmark = build_static_allocation_benchmark(config=config, prices=prices, align_to=align_to)

    assert list(benchmark.index) == list(align_to)
    assert benchmark.iloc[0] == pytest.approx(0.047)


def test_equal_weight_benchmark_is_reproducible() -> None:
    config = ProjectConfig()
    prices = _build_prices()
    returns = prices.pct_change().dropna(how="all")

    benchmark = build_equal_weight_benchmark(
        config=config,
        returns=returns,
        align_to=returns.index,
    )

    expected = pd.Series(
        [0.03, 0.03, 0.03],
        index=returns.index,
        name="equal_weight",
    )
    pd.testing.assert_series_equal(benchmark, expected)


def test_benchmark_equity_curve_is_comparable_to_strategy_equity() -> None:
    config = ProjectConfig(initial_capital=100000.0)
    benchmark_returns = pd.Series(
        [0.10, 0.00, 0.10],
        index=pd.to_datetime(["2024-02-29", "2024-03-31", "2024-04-30"]),
        name="buy_and_hold__BOVA11.SA",
    )

    equity_curve = build_benchmark_equity_curve(benchmark_returns=benchmark_returns, config=config)

    expected = pd.Series(
        [110000.0, 110000.0, 121000.0],
        index=benchmark_returns.index,
        name="buy_and_hold__BOVA11.SA__equity_curve",
    )
    pd.testing.assert_series_equal(equity_curve, expected)


def test_benchmark_suite_returns_comparable_columns() -> None:
    config = ProjectConfig()
    prices = _build_prices()
    align_to = prices.index[1:]

    suite = build_benchmark_suite(config=config, prices=prices, align_to=align_to)

    assert list(suite.index) == list(align_to)
    assert {
        "buy_and_hold__BOVA11.SA",
        "static_allocation_60_40",
        "equal_weight",
        "cash__CDI",
    }.issubset(set(suite.columns))


def _build_prices() -> pd.DataFrame:
    index = pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-31", "2024-04-30"])
    return pd.DataFrame(
        {
            "BOVA11.SA": [100.0, 110.0, 121.0, 133.1],
            "IVVB11.SA": [100.0, 105.0, 110.25, 115.7625],
            "IMAB11.SA": [100.0, 102.0, 104.04, 106.1208],
            "USDBRL=X": [100.0, 97.0, 94.09, 91.2673],
            "CDI": [100.0, 101.0, 102.01, 103.0301],
        },
        index=index,
    )
