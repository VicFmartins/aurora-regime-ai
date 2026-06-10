"""External and manual data sources for historical prices."""

from __future__ import annotations

from pathlib import Path
from warnings import warn

import pandas as pd
import yfinance as yf

from aurora.config import ProjectConfig

MANUAL_PRICE_FILE = "prices.csv"
PRICE_CACHE_FILE = "prices.parquet"
YFINANCE_UNSUPPORTED_TICKERS = frozenset({"CDI"})


def fetch_yfinance_prices(config: ProjectConfig) -> pd.DataFrame:
    """Download price history from Yahoo Finance for supported tickers."""
    tickers = [ticker for ticker in config.assets if ticker not in YFINANCE_UNSUPPORTED_TICKERS]
    if not tickers:
        return pd.DataFrame()

    end_date = (pd.Timestamp(config.end_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        history = yf.download(
            tickers=tickers,
            start=config.start_date,
            end=end_date,
            auto_adjust=False,
            progress=False,
            actions=False,
            group_by="column",
            threads=False,
        )
    except Exception as exc:
        raise RuntimeError(_build_download_error_message(config)) from exc

    if history.empty:
        raise RuntimeError(_build_download_error_message(config))

    return _select_price_field(history=history, tickers=tickers)


def load_manual_price_data(config: ProjectConfig) -> pd.DataFrame:
    """Load optional manual price data from ``data/raw/prices.csv``."""
    manual_path = Path(config.raw_data_dir) / MANUAL_PRICE_FILE
    if not manual_path.exists():
        return pd.DataFrame()

    try:
        manual_data = pd.read_csv(manual_path, index_col=0, parse_dates=True)
    except Exception as exc:
        raise RuntimeError(
            "Nao foi possivel ler o arquivo manual de precos em "
            f"'{manual_path.as_posix()}'. Verifique o CSV e tente novamente."
        ) from exc

    manual_data.index = pd.to_datetime(manual_data.index)
    manual_data = manual_data.sort_index()
    manual_data.index.name = "Date"
    return manual_data


def merge_price_sources(
    config: ProjectConfig,
    downloaded_prices: pd.DataFrame,
    manual_prices: pd.DataFrame,
) -> pd.DataFrame:
    """Merge downloaded and manual prices, preserving the configured ticker order."""
    merged = downloaded_prices.copy()

    if manual_prices.empty:
        manual_prices = pd.DataFrame(index=downloaded_prices.index)

    for ticker in config.assets:
        if ticker in manual_prices.columns and ticker in merged.columns:
            merged[ticker] = merged[ticker].combine_first(manual_prices[ticker])
        elif ticker in manual_prices.columns:
            merged[ticker] = manual_prices[ticker]

    merged = merged.sort_index()
    merged.index.name = "Date"
    return merged.reindex(columns=list(config.assets))


def get_cache_path(config: ProjectConfig) -> Path:
    """Return the parquet cache path for price history."""
    return Path(config.cache_dir) / PRICE_CACHE_FILE


def _build_download_error_message(config: ProjectConfig) -> str:
    manual_path = Path(config.raw_data_dir) / MANUAL_PRICE_FILE
    return (
        "Falha ao baixar os precos historicos via yfinance. "
        "Tente novamente mais tarde ou forneca um CSV manual em "
        f"'{manual_path.as_posix()}' com a primeira coluna de data e as demais "
        "colunas nomeadas pelos tickers configurados."
    )


def _select_price_field(history: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    if isinstance(history.columns, pd.MultiIndex):
        selected = _select_multiindex_price_field(history)
    else:
        selected = _select_single_ticker_price_field(history, tickers[0])

    selected.index = pd.to_datetime(selected.index)
    selected = selected.sort_index()
    selected.index.name = "Date"
    return selected.reindex(columns=tickers)


def _select_multiindex_price_field(history: pd.DataFrame) -> pd.DataFrame:
    first_level = history.columns.get_level_values(0)
    if "Adj Close" in first_level:
        return history["Adj Close"].copy()
    if "Close" in first_level:
        warn(
            "Campo 'Adj Close' indisponivel no retorno do Yahoo Finance. "
            "Usando 'Close' como fallback.",
            RuntimeWarning,
            stacklevel=2,
        )
        return history["Close"].copy()
    raise RuntimeError("O retorno do Yahoo Finance nao contem colunas 'Adj Close' ou 'Close'.")


def _select_single_ticker_price_field(history: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if "Adj Close" in history.columns:
        selected = history[["Adj Close"]].copy()
    elif "Close" in history.columns:
        warn(
            "Campo 'Adj Close' indisponivel no retorno do Yahoo Finance. "
            "Usando 'Close' como fallback.",
            RuntimeWarning,
            stacklevel=2,
        )
        selected = history[["Close"]].copy()
    else:
        raise RuntimeError("O retorno do Yahoo Finance nao contem colunas 'Adj Close' ou 'Close'.")

    selected.columns = [ticker]
    return selected
