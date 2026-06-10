"""Rule-based market regime classifier."""

from __future__ import annotations

from typing import Any

import pandas as pd

from aurora.config import ProjectConfig
from aurora.regime.rules import MarketRegime, build_signal_column_map


def classify_regime_row(
    row: pd.Series,
    config: ProjectConfig,
) -> dict[str, Any]:
    """Classify one feature row into a market regime with an explanation.

    This classifier consumes the already shifted feature set produced by
    ``build_feature_set``. The rule thresholds come from ``ProjectConfig`` and are
    intentionally fixed ex ante instead of optimized on final backtest performance.
    """
    signal_columns = build_signal_column_map(config)
    signals = {
        signal_name: row.get(column_name, pd.NA)
        for signal_name, column_name in signal_columns.items()
    }

    if _is_stress(signals=signals, config=config):
        return {
            "regime": MarketRegime.ESTRESSE,
            "reason": (
                "Drawdown em zona de estresse ou volatilidade acima do limite "
                "metodologico configurado."
            ),
            "signals": signals,
        }

    if _is_positive_trend(signals=signals, config=config):
        return {
            "regime": MarketRegime.TENDENCIA_POSITIVA,
            "reason": ("Momentum de medio e longo prazo positivo com volatilidade controlada."),
            "signals": signals,
        }

    if _is_recovery(signals=signals, config=config):
        return {
            "regime": MarketRegime.RECUPERACAO,
            "reason": (
                "Drawdown ainda negativo, mas momentum curto positivo e z-score em "
                "melhora, sugerindo recuperacao."
            ),
            "signals": signals,
        }

    return {
        "regime": MarketRegime.LATERALIZACAO,
        "reason": (
            "Sem sinais suficientes de estresse, tendencia positiva ou recuperacao; "
            "regime residual classificado como lateralizacao."
        ),
        "signals": signals,
    }


def classify_regimes(
    features: pd.DataFrame,
    config: ProjectConfig,
) -> pd.DataFrame:
    """Classify each timestamp in the feature set into one of the supported regimes."""
    classified_rows = [
        classify_regime_row(row=row, config=config) for _, row in features.iterrows()
    ]
    result = pd.DataFrame(classified_rows, index=features.index)
    result["regime"] = result["regime"].map(lambda regime: regime.value)
    return result


def _is_stress(
    signals: dict[str, Any],
    config: ProjectConfig,
) -> bool:
    drawdown = signals["drawdown"]
    volatility = signals["volatility"]
    return (_is_notna(drawdown) and drawdown <= config.stress_drawdown_threshold) or (
        _is_notna(volatility) and volatility > config.high_volatility_threshold
    )


def _is_positive_trend(
    signals: dict[str, Any],
    config: ProjectConfig,
) -> bool:
    momentum_126 = signals["momentum_medium"]
    momentum_252 = signals["momentum_long"]
    volatility = signals["volatility"]
    return (
        _is_notna(momentum_126)
        and _is_notna(momentum_252)
        and _is_notna(volatility)
        and momentum_126 > config.positive_momentum_threshold
        and momentum_252 > config.positive_momentum_threshold
        and volatility <= config.high_volatility_threshold
    )


def _is_recovery(
    signals: dict[str, Any],
    config: ProjectConfig,
) -> bool:
    drawdown = signals["drawdown"]
    momentum_63 = signals["momentum_short"]
    zscore_delta = signals["zscore_delta"]
    return (
        _is_notna(drawdown)
        and _is_notna(momentum_63)
        and _is_notna(zscore_delta)
        and drawdown < 0.0
        and momentum_63 > config.positive_momentum_threshold
        and zscore_delta > config.recovery_zscore_improvement_threshold
    )


def _is_notna(value: Any) -> bool:
    return pd.notna(value)
