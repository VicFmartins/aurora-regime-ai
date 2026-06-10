"""External data sources for historical prices."""

from __future__ import annotations

from pathlib import Path
from warnings import warn

import pandas as pd
import yfinance as yf
from requests.exceptions import RequestException

from aurora.config import ProjectConfig

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
    except (AttributeError, KeyError, RequestException, TypeError, ValueError) as exc:
        raise RuntimeError(_build_download_error_message(config)) from exc

    if history.empty:
        raise RuntimeError(_build_download_error_message(config))

    return _select_price_field(history=history, tickers=tickers)


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
    manual_path = Path(config.raw_data_dir) / "prices.csv"
    return (
        "Falha ao baixar os precos historicos via yfinance. "
        "Tente novamente mais tarde ou forneca um CSV manual em "
        f"'{manual_path.as_posix()}'. Sao aceitos os formatos wide "
        "('date' + colunas por ticker) e long ('date', 'ticker', 'price')."
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
