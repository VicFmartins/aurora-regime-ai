"""Rule helpers and shared types for regime classification."""

from __future__ import annotations

from enum import Enum

from aurora.config import ProjectConfig


class MarketRegime(str, Enum):
    """Supported market regimes for Aurora's initial rule-based classifier."""

    TENDENCIA_POSITIVA = "TENDENCIA_POSITIVA"
    ESTRESSE = "ESTRESSE"
    LATERALIZACAO = "LATERALIZACAO"
    RECUPERACAO = "RECUPERACAO"


def build_signal_column_map(config: ProjectConfig) -> dict[str, str]:
    """Return the feature-column names used by the regime rules."""
    asset = config.regime_target_asset
    return {
        "drawdown": f"drawdown_{config.drawdown_window}__{asset}",
        "volatility": f"volatility_{config.volatility_window}__{asset}",
        "momentum_short": f"momentum_{config.recovery_momentum_window}__{asset}",
        "momentum_medium": f"momentum_{config.trend_medium_momentum_window}__{asset}",
        "momentum_long": f"momentum_{config.trend_long_momentum_window}__{asset}",
        "zscore": f"zscore_{config.zscore_window}__{asset}",
        "zscore_delta": f"zscore_delta_{config.zscore_window}__{asset}",
    }
