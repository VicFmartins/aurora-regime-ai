"""Benchmark construction for Aurora backtests."""

from __future__ import annotations

import pandas as pd

from aurora.config import ProjectConfig


def build_buy_and_hold_benchmark(
    config: ProjectConfig,
    *,
    prices: pd.DataFrame | None = None,
    returns: pd.DataFrame | None = None,
    align_to: pd.Index | None = None,
    asset: str = "BOVA11.SA",
) -> pd.Series:
    """Return buy-and-hold benchmark returns for the main risk asset."""
    asset_returns = _coerce_returns(prices=prices, returns=returns, config=config)[asset]
    return _align_series(asset_returns, align_to=align_to, name=f"buy_and_hold__{asset}")


def build_cash_benchmark(
    config: ProjectConfig,
    *,
    prices: pd.DataFrame | None = None,
    returns: pd.DataFrame | None = None,
    align_to: pd.Index | None = None,
    asset: str = "CDI",
) -> pd.Series:
    """Return cash benchmark returns when a defensive cash proxy exists in the dataset."""
    normalized_returns = _coerce_returns(prices=prices, returns=returns, config=config)
    if asset not in normalized_returns.columns:
        raise ValueError(f"O benchmark de caixa requer o ativo '{asset}' presente no dataset.")
    return _align_series(normalized_returns[asset], align_to=align_to, name=f"cash__{asset}")


def build_static_allocation_benchmark(
    config: ProjectConfig,
    *,
    prices: pd.DataFrame | None = None,
    returns: pd.DataFrame | None = None,
    align_to: pd.Index | None = None,
) -> pd.Series:
    """Return a static diversified 60/40 benchmark over the available assets."""
    normalized_returns = _coerce_returns(prices=prices, returns=returns, config=config)
    static_weights = {
        "BOVA11.SA": 0.30,
        "IVVB11.SA": 0.30,
        "IMAB11.SA": 0.20,
        "USDBRL=X": 0.10,
        "CDI": 0.10,
    }
    benchmark_returns = _weighted_portfolio_returns(
        returns=normalized_returns,
        weights=static_weights,
    )
    return _align_series(benchmark_returns, align_to=align_to, name="static_allocation_60_40")


def build_equal_weight_benchmark(
    config: ProjectConfig,
    *,
    prices: pd.DataFrame | None = None,
    returns: pd.DataFrame | None = None,
    align_to: pd.Index | None = None,
) -> pd.Series:
    """Return an equal-weight benchmark across the available assets."""
    normalized_returns = _coerce_returns(prices=prices, returns=returns, config=config)
    available_assets = list(normalized_returns.columns)
    equal_weight = 1.0 / len(available_assets)
    weights = {asset: equal_weight for asset in available_assets}
    benchmark_returns = _weighted_portfolio_returns(
        returns=normalized_returns,
        weights=weights,
    )
    return _align_series(benchmark_returns, align_to=align_to, name="equal_weight")


def build_benchmark_equity_curve(
    benchmark_returns: pd.Series,
    config: ProjectConfig,
) -> pd.Series:
    """Transform benchmark returns into an equity curve comparable to the strategy."""
    equity_curve = (1.0 + benchmark_returns).cumprod() * config.initial_capital
    equity_curve.name = f"{benchmark_returns.name}__equity_curve"
    return equity_curve


def build_benchmark_suite(
    config: ProjectConfig,
    *,
    prices: pd.DataFrame | None = None,
    returns: pd.DataFrame | None = None,
    align_to: pd.Index | None = None,
) -> pd.DataFrame:
    """Return the core benchmark return series aligned to the strategy window."""
    benchmark_series = [
        build_buy_and_hold_benchmark(
            config=config,
            prices=prices,
            returns=returns,
            align_to=align_to,
        ),
        build_static_allocation_benchmark(
            config=config,
            prices=prices,
            returns=returns,
            align_to=align_to,
        ),
        build_equal_weight_benchmark(
            config=config,
            prices=prices,
            returns=returns,
            align_to=align_to,
        ),
    ]

    normalized_returns = _coerce_returns(prices=prices, returns=returns, config=config)
    if "CDI" in normalized_returns.columns:
        benchmark_series.append(
            build_cash_benchmark(
                config=config,
                returns=normalized_returns,
                align_to=align_to,
            )
        )

    return pd.concat(benchmark_series, axis=1)


def _coerce_returns(
    *,
    prices: pd.DataFrame | None,
    returns: pd.DataFrame | None,
    config: ProjectConfig,
) -> pd.DataFrame:
    if returns is None and prices is None:
        raise ValueError("Informe prices ou returns para construir benchmarks.")

    if returns is not None:
        normalized_returns = returns.copy()
    else:
        normalized_returns = prices.pct_change()

    normalized_returns.index = pd.to_datetime(normalized_returns.index)
    normalized_returns = normalized_returns.sort_index()
    normalized_returns = normalized_returns.reindex(
        columns=_available_assets(normalized_returns, config)
    )
    normalized_returns = normalized_returns.dropna(how="all")
    return normalized_returns


def _weighted_portfolio_returns(
    returns: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series:
    available_weights = {
        asset: weight for asset, weight in weights.items() if asset in returns.columns
    }
    total_weight = sum(available_weights.values())
    if total_weight <= 0.0:
        raise ValueError("Nao ha ativos suficientes para construir o benchmark solicitado.")

    normalized_weights = {
        asset: weight / total_weight for asset, weight in available_weights.items()
    }
    weights_series = pd.Series(normalized_weights)
    benchmark_returns = returns[weights_series.index].mul(weights_series, axis=1).sum(axis=1)
    return benchmark_returns


def _align_series(
    series: pd.Series,
    *,
    align_to: pd.Index | None,
    name: str,
) -> pd.Series:
    aligned_series = series.copy()
    aligned_series.name = name
    if align_to is None:
        return aligned_series
    aligned_series = aligned_series.reindex(pd.to_datetime(align_to))
    return aligned_series


def _available_assets(
    frame: pd.DataFrame,
    config: ProjectConfig,
) -> list[str]:
    configured_assets = list(config.assets)
    return [asset for asset in configured_assets if asset in frame.columns]
