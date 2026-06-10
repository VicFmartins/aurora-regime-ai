"""Validation helpers for historical price data."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from aurora.config import ProjectConfig


@dataclass(frozen=True)
class PriceDataValidationReport:
    """Summary of observation and null quality checks by ticker."""

    observation_counts: pd.Series
    null_percentages: pd.Series


def calculate_observation_counts(price_data: pd.DataFrame) -> pd.Series:
    """Return non-null observation counts for each ticker."""
    return price_data.notna().sum().sort_index()


def calculate_null_percentages(price_data: pd.DataFrame) -> pd.Series:
    """Return null percentages for each ticker."""
    return price_data.isna().mean().sort_index()


def validate_price_data(
    price_data: pd.DataFrame,
    config: ProjectConfig,
) -> PriceDataValidationReport:
    """Validate basic structure and minimum data-quality rules for prices."""
    errors: list[str] = []

    if not isinstance(price_data.index, pd.DatetimeIndex):
        errors.append("O indice de price_data deve ser um pandas.DatetimeIndex.")

    if (
        isinstance(price_data.index, pd.DatetimeIndex)
        and not price_data.index.is_monotonic_increasing
    ):
        errors.append("As datas em price_data devem estar ordenadas de forma crescente.")

    if price_data.index.has_duplicates:
        errors.append("price_data nao pode conter datas duplicadas no indice.")

    missing_tickers = [ticker for ticker in config.assets if ticker not in price_data.columns]
    if missing_tickers:
        errors.append(
            "price_data nao contem todos os tickers configurados. "
            f"Faltando: {', '.join(missing_tickers)}."
        )

    observation_counts = calculate_observation_counts(price_data)
    null_percentages = calculate_null_percentages(price_data)

    low_observation_tickers = observation_counts[
        observation_counts < config.min_observations_per_asset
    ]
    if not low_observation_tickers.empty:
        formatted_counts = ", ".join(
            f"{ticker}={count}" for ticker, count in low_observation_tickers.sort_index().items()
        )
        errors.append(
            "Ativos com observacoes insuficientes para analise: "
            f"{formatted_counts}. Minimo esperado: {config.min_observations_per_asset}."
        )

    high_null_tickers = null_percentages[null_percentages > config.max_null_ratio_per_asset]
    if not high_null_tickers.empty:
        formatted_nulls = ", ".join(
            f"{ticker}={null_ratio:.2%}"
            for ticker, null_ratio in high_null_tickers.sort_index().items()
        )
        errors.append(
            "Ativos com percentual de nulos acima do permitido: "
            f"{formatted_nulls}. Maximo esperado: {config.max_null_ratio_per_asset:.2%}."
        )

    if errors:
        raise ValueError(" ".join(errors))

    return PriceDataValidationReport(
        observation_counts=observation_counts,
        null_percentages=null_percentages,
    )
