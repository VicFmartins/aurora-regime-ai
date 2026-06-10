"""Load, cache and validate historical price data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from aurora.config import ProjectConfig
from aurora.data.sources import (
    fetch_yfinance_prices,
    get_cache_path,
    load_manual_price_data,
    merge_price_sources,
)
from aurora.data.validation import validate_price_data


def get_price_data(
    config: ProjectConfig,
    force_download: bool = False,
) -> pd.DataFrame:
    """Return standardized price data from cache or fresh download."""
    cache_path = get_cache_path(config)
    _ensure_parent_dir(cache_path)

    if cache_path.exists() and not force_download:
        price_data = pd.read_parquet(cache_path)
    else:
        manual_prices = load_manual_price_data(config)
        try:
            downloaded_prices = fetch_yfinance_prices(config)
        except RuntimeError:
            if manual_prices.empty:
                raise
            downloaded_prices = pd.DataFrame()

        price_data = merge_price_sources(
            config=config,
            downloaded_prices=downloaded_prices,
            manual_prices=manual_prices,
        )
        _ensure_required_tickers_present(price_data=price_data, config=config)
        price_data.to_parquet(cache_path)

    price_data.index = pd.to_datetime(price_data.index)
    price_data = price_data.sort_index()
    price_data = price_data.reindex(columns=list(config.assets))
    validate_price_data(price_data=price_data, config=config)
    return price_data


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _ensure_required_tickers_present(
    price_data: pd.DataFrame,
    config: ProjectConfig,
) -> None:
    missing_tickers = [
        ticker
        for ticker in config.assets
        if ticker not in price_data.columns or price_data[ticker].dropna().empty
    ]
    if not missing_tickers:
        return

    raise RuntimeError(
        "Nao foi possivel obter dados para todos os tickers configurados. "
        f"Faltando: {', '.join(missing_tickers)}. "
        "Tente novamente mais tarde ou forneca esses ativos manualmente em "
        f"'{(Path(config.raw_data_dir) / 'prices.csv').as_posix()}'."
    )
