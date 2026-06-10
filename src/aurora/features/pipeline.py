"""Feature-set assembly for regime classification."""

from __future__ import annotations

from itertools import combinations

import pandas as pd

from aurora.config import ProjectConfig
from aurora.features.indicators import (
    compute_drawdown,
    compute_momentum,
    compute_rolling_correlation,
    compute_volatility,
    compute_zscore,
)
from aurora.features.returns import compute_log_returns, compute_returns


def build_feature_set(
    prices: pd.DataFrame,
    config: ProjectConfig,
) -> pd.DataFrame:
    """Build the regime feature set and shift every decision feature by one period.

    The explicit ``shift(1)`` happens at the end of this pipeline so the backtest can
    consume only information that would have been available before the next decision.
    This is the project-level safeguard against look-ahead bias.
    """
    simple_returns = compute_returns(prices, method="simple")
    log_returns = compute_log_returns(prices)

    feature_frames: list[pd.DataFrame] = [
        _rename_columns(simple_returns, prefix="return"),
        _rename_columns(log_returns, prefix="log_return"),
    ]

    momentum_features = compute_momentum(prices, windows=config.momentum_windows)
    for window, momentum in momentum_features.items():
        feature_frames.append(_rename_columns(momentum, prefix=f"momentum_{window}"))

    volatility = compute_volatility(
        simple_returns,
        window=config.volatility_window,
        annualize=True,
    )
    feature_frames.append(
        _rename_columns(volatility, prefix=f"volatility_{config.volatility_window}")
    )

    drawdown = compute_drawdown(prices, window=config.drawdown_window)
    feature_frames.append(_rename_columns(drawdown, prefix=f"drawdown_{config.drawdown_window}"))

    zscore = compute_zscore(simple_returns, window=config.zscore_window)
    feature_frames.append(_rename_columns(zscore, prefix=f"zscore_{config.zscore_window}"))
    feature_frames.append(
        _rename_columns(
            zscore.diff(),
            prefix=f"zscore_delta_{config.zscore_window}",
        )
    )

    correlation_features = _build_correlation_features(
        returns=simple_returns,
        assets=list(prices.columns),
        window=config.correlation_window,
    )
    if not correlation_features.empty:
        feature_frames.append(correlation_features)

    raw_feature_set = pd.concat(feature_frames, axis=1).sort_index()
    return raw_feature_set.shift(1)


def _rename_columns(feature_frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    renamed = feature_frame.copy()
    renamed.columns = [f"{prefix}__{column}" for column in renamed.columns]
    return renamed


def _build_correlation_features(
    returns: pd.DataFrame,
    assets: list[str],
    window: int,
) -> pd.DataFrame:
    correlation_series = [
        compute_rolling_correlation(returns, asset_a=asset_a, asset_b=asset_b, window=window)
        for asset_a, asset_b in combinations(assets, 2)
    ]
    if not correlation_series:
        return pd.DataFrame(index=returns.index)
    return pd.concat(correlation_series, axis=1)
