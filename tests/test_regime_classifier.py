from __future__ import annotations

import pandas as pd

from aurora.config import ProjectConfig
from aurora.regime import MarketRegime, classify_regime_row, classify_regimes


def test_classify_regime_row_identifies_estresse() -> None:
    config = ProjectConfig()
    row = _build_feature_row(
        config=config,
        drawdown=-0.20,
        volatility=0.18,
        momentum_63=-0.03,
        momentum_126=-0.02,
        momentum_252=-0.01,
        zscore=-1.4,
        zscore_delta=-0.1,
    )

    result = classify_regime_row(row=row, config=config)

    assert result["regime"] == MarketRegime.ESTRESSE
    assert "estresse" in result["reason"].lower()


def test_classify_regime_row_identifies_tendencia_positiva() -> None:
    config = ProjectConfig()
    row = _build_feature_row(
        config=config,
        drawdown=-0.03,
        volatility=0.12,
        momentum_63=0.04,
        momentum_126=0.08,
        momentum_252=0.14,
        zscore=0.7,
        zscore_delta=0.02,
    )

    result = classify_regime_row(row=row, config=config)

    assert result["regime"] == MarketRegime.TENDENCIA_POSITIVA
    assert "momentum" in result["reason"].lower()


def test_classify_regime_row_identifies_recuperacao() -> None:
    config = ProjectConfig()
    row = _build_feature_row(
        config=config,
        drawdown=-0.08,
        volatility=0.20,
        momentum_63=0.03,
        momentum_126=-0.01,
        momentum_252=-0.05,
        zscore=-0.8,
        zscore_delta=0.15,
    )

    result = classify_regime_row(row=row, config=config)

    assert result["regime"] == MarketRegime.RECUPERACAO
    assert "recuperacao" in result["reason"].lower()


def test_classify_regime_row_identifies_lateralizacao() -> None:
    config = ProjectConfig()
    row = _build_feature_row(
        config=config,
        drawdown=-0.02,
        volatility=0.18,
        momentum_63=-0.01,
        momentum_126=0.0,
        momentum_252=-0.01,
        zscore=0.05,
        zscore_delta=-0.01,
    )

    result = classify_regime_row(row=row, config=config)

    assert result["regime"] == MarketRegime.LATERALIZACAO
    assert "lateralizacao" in result["reason"].lower()


def test_classify_regimes_returns_regime_reason_and_signals() -> None:
    config = ProjectConfig()
    features = pd.DataFrame(
        [
            _build_feature_row(
                config=config,
                drawdown=-0.20,
                volatility=0.18,
                momentum_63=-0.03,
                momentum_126=-0.02,
                momentum_252=-0.01,
                zscore=-1.4,
                zscore_delta=-0.1,
            ),
            _build_feature_row(
                config=config,
                drawdown=-0.03,
                volatility=0.12,
                momentum_63=0.04,
                momentum_126=0.08,
                momentum_252=0.14,
                zscore=0.7,
                zscore_delta=0.02,
            ),
            _build_feature_row(
                config=config,
                drawdown=-0.08,
                volatility=0.20,
                momentum_63=0.03,
                momentum_126=-0.01,
                momentum_252=-0.05,
                zscore=-0.8,
                zscore_delta=0.15,
            ),
            _build_feature_row(
                config=config,
                drawdown=-0.02,
                volatility=0.18,
                momentum_63=-0.01,
                momentum_126=0.0,
                momentum_252=-0.01,
                zscore=0.05,
                zscore_delta=-0.01,
            ),
        ],
        index=pd.date_range("2024-01-31", periods=4, freq="ME"),
    )

    result = classify_regimes(features=features, config=config)

    assert list(result.columns) == ["regime", "reason", "signals"]
    assert list(result["regime"]) == [
        MarketRegime.ESTRESSE.value,
        MarketRegime.TENDENCIA_POSITIVA.value,
        MarketRegime.RECUPERACAO.value,
        MarketRegime.LATERALIZACAO.value,
    ]
    assert isinstance(result.iloc[0]["signals"], dict)
    assert "drawdown" in result.iloc[0]["signals"]


def _build_feature_row(
    config: ProjectConfig,
    drawdown: float,
    volatility: float,
    momentum_63: float,
    momentum_126: float,
    momentum_252: float,
    zscore: float,
    zscore_delta: float,
) -> pd.Series:
    asset = config.regime_target_asset
    return pd.Series(
        {
            f"drawdown_{config.drawdown_window}__{asset}": drawdown,
            f"volatility_{config.volatility_window}__{asset}": volatility,
            f"momentum_{config.recovery_momentum_window}__{asset}": momentum_63,
            f"momentum_{config.trend_medium_momentum_window}__{asset}": momentum_126,
            f"momentum_{config.trend_long_momentum_window}__{asset}": momentum_252,
            f"zscore_{config.zscore_window}__{asset}": zscore,
            f"zscore_delta_{config.zscore_window}__{asset}": zscore_delta,
        }
    )
