"""Portfolio allocation policies driven by market regime."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from aurora.config import ProjectConfig
from aurora.regime.rules import MarketRegime


@dataclass(frozen=True)
class AllocationPolicy:
    """Long-only target weights defined ex ante for a given market regime."""

    regime: MarketRegime
    weights: dict[str, float]
    rationale: str

    def validate(self, config: ProjectConfig, tolerance: float = 1e-9) -> None:
        """Validate that the policy is long-only and sums to 100%."""
        missing_assets = [asset for asset in config.assets if asset not in self.weights]
        if missing_assets:
            raise ValueError(
                "Politica de alocacao incompleta. Faltando pesos para: "
                f"{', '.join(missing_assets)}."
            )

        negative_weights = [asset for asset, weight in self.weights.items() if weight < 0.0]
        if negative_weights:
            raise ValueError(
                "Politica de alocacao invalida. Pesos negativos encontrados em: "
                f"{', '.join(negative_weights)}."
            )

        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > tolerance:
            raise ValueError(
                "Politica de alocacao invalida. A soma dos pesos deve ser 1.0, "
                f"mas foi {total_weight:.10f}."
            )


def get_weights_for_regime(
    regime: MarketRegime | str,
    config: ProjectConfig,
) -> AllocationPolicy:
    """Return the validated long-only allocation policy for one regime."""
    normalized_regime = _normalize_regime(regime)
    policy = _build_policies(config)[normalized_regime]
    policy.validate(config=config)
    return policy


def build_target_weights(
    regime_series: pd.Series,
    config: ProjectConfig,
) -> pd.DataFrame:
    """Convert a regime time series into a DataFrame of target portfolio weights."""
    weight_rows = []
    for _, regime in regime_series.items():
        policy = get_weights_for_regime(regime=regime, config=config)
        weight_rows.append(policy.weights)

    weights = pd.DataFrame(weight_rows, index=regime_series.index)
    weights = weights.reindex(columns=list(config.assets))
    return weights


def _build_policies(config: ProjectConfig) -> dict[MarketRegime, AllocationPolicy]:
    balanced_weights = dict(config.asset_weights)

    policies = {
        MarketRegime.TENDENCIA_POSITIVA: AllocationPolicy(
            regime=MarketRegime.TENDENCIA_POSITIVA,
            weights={
                "BOVA11.SA": 0.40,
                "IVVB11.SA": 0.30,
                "IMAB11.SA": 0.10,
                "USDBRL=X": 0.05,
                "CDI": 0.15,
            },
            rationale=(
                "Maior exposicao a risco em tendencia positiva, preservando alguma "
                "diversificacao defensiva."
            ),
        ),
        MarketRegime.ESTRESSE: AllocationPolicy(
            regime=MarketRegime.ESTRESSE,
            weights={
                "BOVA11.SA": 0.05,
                "IVVB11.SA": 0.05,
                "IMAB11.SA": 0.30,
                "USDBRL=X": 0.20,
                "CDI": 0.40,
            },
            rationale=(
                "Protecao defensiva com foco em caixa, renda fixa e hedge cambial durante estresse."
            ),
        ),
        MarketRegime.LATERALIZACAO: AllocationPolicy(
            regime=MarketRegime.LATERALIZACAO,
            weights=balanced_weights,
            rationale=("Distribuicao equilibrada quando nao ha direcionalidade clara de mercado."),
        ),
        MarketRegime.RECUPERACAO: AllocationPolicy(
            regime=MarketRegime.RECUPERACAO,
            weights={
                "BOVA11.SA": 0.30,
                "IVVB11.SA": 0.20,
                "IMAB11.SA": 0.20,
                "USDBRL=X": 0.10,
                "CDI": 0.20,
            },
            rationale=(
                "Reentrada gradual em risco com reforco ainda relevante em ativos defensivos."
            ),
        ),
    }

    return policies


def _normalize_regime(regime: MarketRegime | str) -> MarketRegime:
    if isinstance(regime, MarketRegime):
        return regime
    return MarketRegime(regime)
