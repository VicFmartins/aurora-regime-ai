from __future__ import annotations

import pandas as pd
import pytest

from aurora.backtest import BacktestResult, run_backtest
from aurora.config import ProjectConfig


def test_run_backtest_returns_structured_result() -> None:
    prices = _build_prices()
    target_weights = _build_target_weights()
    config = ProjectConfig(transaction_cost_bps=0)

    result = run_backtest(prices=prices, target_weights=target_weights, config=config)

    assert isinstance(result, BacktestResult)
    assert list(result.portfolio_returns.index) == list(
        pd.to_datetime(["2024-02-29", "2024-03-31", "2024-04-30"])
    )
    assert list(result.weights_history.columns) == list(config.assets)
    assert list(result.rebalance_log["rebalance_date"]) == list(result.portfolio_returns.index)


def test_run_backtest_applies_previous_period_signal() -> None:
    prices = _build_prices()
    target_weights = _build_target_weights()
    config = ProjectConfig(transaction_cost_bps=0)

    result = run_backtest(prices=prices, target_weights=target_weights, config=config)

    assert result.weights_history.loc[pd.Timestamp("2024-02-29"), "BOVA11.SA"] == pytest.approx(1.0)
    assert result.weights_history.loc[pd.Timestamp("2024-03-31"), "BOVA11.SA"] == pytest.approx(0.0)
    assert result.weights_history.loc[pd.Timestamp("2024-04-30"), "BOVA11.SA"] == pytest.approx(1.0)

    assert result.portfolio_returns.loc[pd.Timestamp("2024-02-29")] == pytest.approx(0.10)
    assert result.portfolio_returns.loc[pd.Timestamp("2024-03-31")] == pytest.approx(0.0)
    assert result.portfolio_returns.loc[pd.Timestamp("2024-04-30")] == pytest.approx(0.10)


def test_run_backtest_applies_transaction_costs() -> None:
    prices = _build_prices()
    target_weights = _build_target_weights()
    config = ProjectConfig(transaction_cost_bps=100)

    result = run_backtest(prices=prices, target_weights=target_weights, config=config)

    assert result.rebalance_log.iloc[0]["turnover"] == pytest.approx(1.0)
    assert result.rebalance_log.iloc[0]["transaction_cost"] == pytest.approx(0.01)
    assert result.portfolio_returns.loc[pd.Timestamp("2024-02-29")] == pytest.approx(0.09)


def test_run_backtest_equity_curve_matches_expected_path() -> None:
    prices = _build_prices()
    target_weights = _build_target_weights()
    config = ProjectConfig(initial_capital=100000.0, transaction_cost_bps=0)

    result = run_backtest(prices=prices, target_weights=target_weights, config=config)

    expected_equity = pd.Series(
        [110000.0, 110000.0, 121000.0],
        index=pd.to_datetime(["2024-02-29", "2024-03-31", "2024-04-30"]),
        name="equity_curve",
    )

    pd.testing.assert_series_equal(result.equity_curve, expected_equity)


def _build_prices() -> pd.DataFrame:
    index = pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-31", "2024-04-30"])
    return pd.DataFrame(
        {
            "BOVA11.SA": [100.0, 110.0, 121.0, 133.1],
            "IVVB11.SA": [100.0, 100.0, 100.0, 100.0],
            "IMAB11.SA": [100.0, 100.0, 100.0, 100.0],
            "USDBRL=X": [100.0, 100.0, 100.0, 100.0],
            "CDI": [100.0, 100.0, 100.0, 100.0],
        },
        index=index,
    )


def _build_target_weights() -> pd.DataFrame:
    index = pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-31"])
    return pd.DataFrame(
        [
            {
                "BOVA11.SA": 1.0,
                "IVVB11.SA": 0.0,
                "IMAB11.SA": 0.0,
                "USDBRL=X": 0.0,
                "CDI": 0.0,
            },
            {
                "BOVA11.SA": 0.0,
                "IVVB11.SA": 1.0,
                "IMAB11.SA": 0.0,
                "USDBRL=X": 0.0,
                "CDI": 0.0,
            },
            {
                "BOVA11.SA": 1.0,
                "IVVB11.SA": 0.0,
                "IMAB11.SA": 0.0,
                "USDBRL=X": 0.0,
                "CDI": 0.0,
            },
        ],
        index=index,
    )
