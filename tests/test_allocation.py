from __future__ import annotations

import pandas as pd
import pytest

from aurora.config import ProjectConfig
from aurora.portfolio import AllocationPolicy, build_target_weights, get_weights_for_regime
from aurora.regime import MarketRegime


def test_all_regime_policies_sum_to_one() -> None:
    config = ProjectConfig()

    for regime in MarketRegime:
        policy = get_weights_for_regime(regime=regime, config=config)

        assert isinstance(policy, AllocationPolicy)
        assert sum(policy.weights.values()) == pytest.approx(1.0)


def test_all_regime_policies_are_long_only() -> None:
    config = ProjectConfig()

    for regime in MarketRegime:
        policy = get_weights_for_regime(regime=regime, config=config)
        assert all(weight >= 0.0 for weight in policy.weights.values())


def test_all_regimes_have_defined_policy() -> None:
    config = ProjectConfig()

    policies = {
        regime: get_weights_for_regime(regime=regime, config=config) for regime in MarketRegime
    }

    assert set(policies) == set(MarketRegime)
    assert (
        policies[MarketRegime.ESTRESSE].weights["CDI"]
        > policies[MarketRegime.TENDENCIA_POSITIVA].weights["CDI"]
    )


def test_build_target_weights_preserves_dates() -> None:
    config = ProjectConfig()
    regime_series = pd.Series(
        [
            MarketRegime.ESTRESSE.value,
            MarketRegime.RECUPERACAO.value,
            MarketRegime.LATERALIZACAO.value,
            MarketRegime.TENDENCIA_POSITIVA.value,
        ],
        index=pd.date_range("2024-01-31", periods=4, freq="ME"),
        name="regime",
    )

    weights = build_target_weights(regime_series=regime_series, config=config)

    assert list(weights.index) == list(regime_series.index)
    assert list(weights.columns) == list(config.assets)
    assert weights.loc[regime_series.index[0], "CDI"] == pytest.approx(0.40)
    assert weights.loc[regime_series.index[-1], "BOVA11.SA"] == pytest.approx(0.40)
