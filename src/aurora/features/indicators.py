"""Indicator computations for Aurora market regimes."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_momentum(
    prices: pd.DataFrame,
    windows: tuple[int, ...] = (63, 126, 252),
) -> dict[int, pd.DataFrame]:
    """Compute trailing price momentum for each requested window.

    Momentum is returned as raw trailing information. The one-period shift used to
    avoid look-ahead bias is intentionally applied only inside ``build_feature_set``.
    """
    return {window: prices.pct_change(periods=window) for window in windows}


def compute_volatility(
    returns: pd.DataFrame,
    window: int = 21,
    annualize: bool = True,
) -> pd.DataFrame:
    """Compute rolling volatility from returns without shifting the result.

    The one-period shift used to avoid look-ahead bias is intentionally applied only
    inside ``build_feature_set`` after the raw rolling statistic is computed.
    """
    volatility = returns.rolling(window=window, min_periods=window).std(ddof=0)
    if annualize:
        volatility = volatility * np.sqrt(252.0)
    return volatility


def compute_drawdown(
    prices: pd.DataFrame,
    window: int = 252,
) -> pd.DataFrame:
    """Compute rolling drawdown relative to the trailing window high.

    Drawdown is returned as a raw trailing statistic. The one-period shift used to
    avoid look-ahead bias is intentionally applied only inside ``build_feature_set``.
    """
    rolling_peak = prices.rolling(window=window, min_periods=window).max()
    return prices.div(rolling_peak).sub(1.0)


def compute_zscore(
    returns: pd.DataFrame,
    window: int = 252,
) -> pd.DataFrame:
    """Compute rolling z-score from returns without shifting the result.

    The one-period shift used to avoid look-ahead bias is intentionally applied only
    inside ``build_feature_set`` after the raw statistic is computed. Divisions by
    zero are converted to ``NaN`` instead of infinities.
    """
    rolling_mean = returns.rolling(window=window, min_periods=window).mean()
    rolling_std = returns.rolling(window=window, min_periods=window).std(ddof=0)
    safe_std = rolling_std.where(rolling_std != 0.0, np.nan)
    return returns.sub(rolling_mean).div(safe_std)


def compute_rolling_correlation(
    returns: pd.DataFrame,
    asset_a: str,
    asset_b: str,
    window: int = 60,
) -> pd.Series:
    """Compute trailing rolling correlation between two assets without shifting it.

    The one-period shift used to avoid look-ahead bias is intentionally applied only
    inside ``build_feature_set`` after the raw rolling correlation is computed.
    """
    if asset_a not in returns.columns or asset_b not in returns.columns:
        raise KeyError(
            "Os ativos informados para correlacao precisam existir no DataFrame de retornos."
        )

    correlation = returns[asset_a].rolling(window=window, min_periods=window).corr(returns[asset_b])
    correlation.name = f"correlation__{asset_a}__{asset_b}__{window}"
    return correlation
