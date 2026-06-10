from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from aurora.config import ProjectConfig
from aurora.data.loader import load_prices_from_csv


def test_load_prices_from_csv_supports_wide_format(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices_wide.csv"
    csv_path.write_text(
        "\n".join(
            [
                "date,BOVA11.SA,IVVB11.SA,IMAB11.SA,USDBRL=X,CDI",
                "2024-01-31,100.0,200.0,300.0,4.90,13.10",
                "2024-02-29,101.0,201.0,301.0,4.95,13.15",
                "2024-03-31,102.0,202.0,302.0,5.00,13.20",
            ]
        ),
        encoding="utf-8",
    )

    config = ProjectConfig(min_observations_per_asset=3, max_null_ratio_per_asset=0.0)
    price_data = load_prices_from_csv(path=csv_path, config=config)

    assert isinstance(price_data.index, pd.DatetimeIndex)
    assert list(price_data.columns) == list(config.assets)
    assert price_data.loc[pd.Timestamp("2024-02-29"), "IVVB11.SA"] == pytest.approx(201.0)


def test_load_prices_from_csv_supports_long_format(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices_long.csv"
    csv_path.write_text(
        "\n".join(
            [
                "date,ticker,price",
                "2024-01-31,BOVA11.SA,100.0",
                "2024-01-31,IVVB11.SA,200.0",
                "2024-01-31,IMAB11.SA,300.0",
                "2024-01-31,USDBRL=X,4.90",
                "2024-01-31,CDI,13.10",
                "2024-02-29,BOVA11.SA,101.0",
                "2024-02-29,IVVB11.SA,201.0",
                "2024-02-29,IMAB11.SA,301.0",
                "2024-02-29,USDBRL=X,4.95",
                "2024-02-29,CDI,13.15",
                "2024-03-31,BOVA11.SA,102.0",
                "2024-03-31,IVVB11.SA,202.0",
                "2024-03-31,IMAB11.SA,302.0",
                "2024-03-31,USDBRL=X,5.00",
                "2024-03-31,CDI,13.20",
            ]
        ),
        encoding="utf-8",
    )

    config = ProjectConfig(min_observations_per_asset=3, max_null_ratio_per_asset=0.0)
    price_data = load_prices_from_csv(path=csv_path, config=config)

    assert isinstance(price_data.index, pd.DatetimeIndex)
    assert price_data.index.is_monotonic_increasing
    assert price_data.loc[pd.Timestamp("2024-03-31"), "CDI"] == pytest.approx(13.20)


def test_load_prices_from_csv_rejects_invalid_format(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices_invalid.csv"
    csv_path.write_text(
        "\n".join(
            [
                "when,symbol,value",
                "2024-01-31,BOVA11.SA,100.0",
            ]
        ),
        encoding="utf-8",
    )

    config = ProjectConfig(min_observations_per_asset=1, max_null_ratio_per_asset=1.0)
    with pytest.raises(ValueError, match="CSV manual invalido"):
        load_prices_from_csv(path=csv_path, config=config)
