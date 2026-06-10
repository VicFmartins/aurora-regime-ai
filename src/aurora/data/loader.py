"""Load, cache and validate historical price data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from aurora.config import ProjectConfig, load_config
from aurora.data.sources import (
    fetch_yfinance_prices,
    get_cache_path,
    merge_price_sources,
)
from aurora.data.validation import validate_price_data

CSV_LONG_REQUIRED_COLUMNS = {"date", "ticker", "price"}


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
        manual_prices = _load_manual_price_data(config)
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


def load_prices_from_csv(
    path: str | Path,
    config: ProjectConfig | None = None,
) -> pd.DataFrame:
    """Load manual prices from CSV in wide or long format and validate them."""
    resolved_config = config or load_config()
    csv_path = Path(path)

    try:
        raw_data = pd.read_csv(csv_path)
    except (
        FileNotFoundError,
        OSError,
        UnicodeDecodeError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
    ) as exc:
        raise RuntimeError(
            f"Nao foi possivel ler o arquivo CSV em '{csv_path.as_posix()}'."
        ) from exc

    normalized_columns = {column.lower(): column for column in raw_data.columns}
    if "date" not in normalized_columns:
        raise ValueError(
            "CSV manual invalido. O arquivo precisa conter a coluna 'date' em formato wide "
            "ou as colunas 'date', 'ticker' e 'price' em formato long."
        )

    price_data = _parse_long_csv(raw_data, normalized_columns)
    if price_data is None:
        price_data = _parse_wide_csv(raw_data, normalized_columns)

    price_data.index = pd.to_datetime(price_data.index)
    price_data = price_data.sort_index()
    price_data.index.name = "Date"
    price_data = price_data.reindex(columns=list(resolved_config.assets))
    validate_price_data(price_data=price_data, config=resolved_config)
    return price_data


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_manual_price_data(config: ProjectConfig) -> pd.DataFrame:
    manual_path = Path(config.raw_data_dir) / "prices.csv"
    if not manual_path.exists():
        return pd.DataFrame()

    return load_prices_from_csv(path=manual_path, config=config)


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


def _parse_long_csv(
    raw_data: pd.DataFrame,
    normalized_columns: dict[str, str],
) -> pd.DataFrame | None:
    if not CSV_LONG_REQUIRED_COLUMNS.issubset(normalized_columns):
        return None

    long_data = raw_data[
        [
            normalized_columns["date"],
            normalized_columns["ticker"],
            normalized_columns["price"],
        ]
    ].copy()
    long_data.columns = ["date", "ticker", "price"]
    long_data["date"] = pd.to_datetime(long_data["date"])
    long_data["price"] = pd.to_numeric(long_data["price"], errors="coerce")

    duplicated_pairs = long_data.duplicated(subset=["date", "ticker"])
    if duplicated_pairs.any():
        raise ValueError(
            "CSV manual invalido. O formato long nao pode conter pares duplicados de date e ticker."
        )

    return long_data.pivot(index="date", columns="ticker", values="price")


def _parse_wide_csv(
    raw_data: pd.DataFrame,
    normalized_columns: dict[str, str],
) -> pd.DataFrame:
    if set(normalized_columns) == {"date"}:
        raise ValueError(
            "CSV manual invalido. No formato wide, alem da coluna 'date', o arquivo "
            "precisa conter ao menos uma coluna de ticker."
        )

    wide_data = raw_data.copy()
    wide_data = wide_data.rename(columns={normalized_columns["date"]: "date"})
    wide_data["date"] = pd.to_datetime(wide_data["date"])
    wide_data = wide_data.set_index("date")
    wide_data = wide_data.apply(_coerce_numeric_values)
    return wide_data


def _coerce_numeric_values(column: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(column):
        return column
    return pd.to_numeric(column, errors="coerce")
