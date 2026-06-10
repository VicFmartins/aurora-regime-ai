"""Feature engineering utilities for market regime signals."""

from aurora.features.indicators import (
    compute_drawdown,
    compute_momentum,
    compute_rolling_correlation,
    compute_volatility,
    compute_zscore,
)
from aurora.features.pipeline import build_feature_set
from aurora.features.returns import compute_log_returns, compute_returns

__all__ = [
    "build_feature_set",
    "compute_drawdown",
    "compute_log_returns",
    "compute_momentum",
    "compute_returns",
    "compute_rolling_correlation",
    "compute_volatility",
    "compute_zscore",
]
