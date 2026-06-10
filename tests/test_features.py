from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from aurora.config import ProjectConfig
from aurora.features import (
    build_feature_set,
    compute_drawdown,
    compute_log_returns,
    compute_returns,
    compute_zscore,
)


def test_compute_returns_with_known_small_series() -> None:
    prices = pd.DataFrame(
        {"BOVA11.SA": [100.0, 110.0, 121.0]},
        index=pd.date_range("2024-01-31", periods=3, freq="ME"),
    )

    returns = compute_returns(prices)
    log_returns = compute_log_returns(prices)

    assert np.isnan(returns.iloc[0, 0])
    assert returns.iloc[1, 0] == pytest.approx(0.10)
    assert returns.iloc[2, 0] == pytest.approx(0.10)
    assert log_returns.iloc[1, 0] == pytest.approx(np.log(1.10))


def test_compute_drawdown_with_controlled_case() -> None:
    prices = pd.DataFrame(
        {"BOVA11.SA": [100.0, 120.0, 90.0, 95.0]},
        index=pd.date_range("2024-01-31", periods=4, freq="ME"),
    )

    drawdown = compute_drawdown(prices, window=2)

    assert np.isnan(drawdown.iloc[0, 0])
    assert drawdown.iloc[1, 0] == pytest.approx(0.0)
    assert drawdown.iloc[2, 0] == pytest.approx(-0.25)
    assert drawdown.iloc[3, 0] == pytest.approx(0.0)


def test_compute_zscore_avoids_division_by_zero() -> None:
    returns = pd.DataFrame(
        {"BOVA11.SA": [0.01, 0.01, 0.01, 0.01]},
        index=pd.date_range("2024-01-31", periods=4, freq="ME"),
    )

    zscore = compute_zscore(returns, window=3)

    assert np.isnan(zscore.iloc[2, 0])
    assert np.isnan(zscore.iloc[3, 0])
    assert not np.isinf(zscore.to_numpy(dtype=float)).any()


def test_build_feature_set_returns_clear_columns() -> None:
    prices = _build_price_frame()
    config = ProjectConfig(
        momentum_windows=(2, 3),
        volatility_window=2,
        drawdown_window=2,
        zscore_window=2,
        correlation_window=2,
    )

    feature_set = build_feature_set(prices=prices, config=config)

    expected_columns = {
        "return__BOVA11.SA",
        "log_return__IVVB11.SA",
        "momentum_2__BOVA11.SA",
        "momentum_3__CDI",
        "volatility_2__IMAB11.SA",
        "drawdown_2__USDBRL=X",
        "zscore_2__CDI",
        "zscore_delta_2__BOVA11.SA",
        "correlation__BOVA11.SA__IVVB11.SA__2",
    }
    assert expected_columns.issubset(set(feature_set.columns))


def test_build_feature_set_shifts_decision_features_by_one_period() -> None:
    prices = _build_price_frame()
    config = ProjectConfig(
        momentum_windows=(2,),
        volatility_window=2,
        drawdown_window=2,
        zscore_window=2,
        correlation_window=2,
    )

    raw_returns = compute_returns(prices)
    raw_drawdown = compute_drawdown(prices, window=2)
    feature_set = build_feature_set(prices=prices, config=config)

    target_date = prices.index[3]
    previous_date = prices.index[2]

    assert feature_set.loc[target_date, "return__BOVA11.SA"] == pytest.approx(
        raw_returns.loc[previous_date, "BOVA11.SA"]
    )
    assert feature_set.loc[target_date, "drawdown_2__BOVA11.SA"] == pytest.approx(
        raw_drawdown.loc[previous_date, "BOVA11.SA"]
    )


def _build_price_frame() -> pd.DataFrame:
    index = pd.date_range("2024-01-31", periods=6, freq="ME")
    return pd.DataFrame(
        {
            "BOVA11.SA": [100.0, 102.0, 101.0, 104.0, 106.0, 107.0],
            "IVVB11.SA": [200.0, 201.0, 203.0, 202.0, 205.0, 207.0],
            "IMAB11.SA": [300.0, 301.0, 302.0, 303.0, 304.0, 305.0],
            "USDBRL=X": [4.90, 4.95, 5.00, 4.98, 5.01, 5.05],
            "CDI": [13.10, 13.12, 13.14, 13.16, 13.18, 13.20],
        },
        index=index,
    )
