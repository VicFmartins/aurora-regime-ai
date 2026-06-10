from __future__ import annotations

import pandas as pd
import pytest

from aurora.config import ProjectConfig
from aurora.data.validation import (
    PriceDataValidationReport,
    calculate_null_percentages,
    calculate_observation_counts,
    validate_price_data,
)


def test_validate_price_data_returns_report_for_valid_frame() -> None:
    config = ProjectConfig(
        min_observations_per_asset=3,
        max_null_ratio_per_asset=0.40,
    )
    price_data = _build_valid_price_frame()

    report = validate_price_data(price_data=price_data, config=config)

    assert isinstance(report, PriceDataValidationReport)
    assert report.observation_counts["BOVA11.SA"] == 4
    assert report.null_percentages["CDI"] == pytest.approx(0.25)


def test_validate_price_data_rejects_non_datetime_index() -> None:
    config = ProjectConfig(min_observations_per_asset=1)
    price_data = _build_valid_price_frame().copy()
    price_data.index = [0, 1, 2, 3]

    with pytest.raises(ValueError, match="DatetimeIndex"):
        validate_price_data(price_data=price_data, config=config)


def test_validate_price_data_rejects_unsorted_dates() -> None:
    config = ProjectConfig(min_observations_per_asset=1)
    price_data = _build_valid_price_frame().sort_index(ascending=False)

    with pytest.raises(ValueError, match="ordenadas"):
        validate_price_data(price_data=price_data, config=config)


def test_validate_price_data_rejects_duplicate_dates() -> None:
    config = ProjectConfig(min_observations_per_asset=1)
    price_data = _build_valid_price_frame()
    duplicated_index = pd.DatetimeIndex(
        [price_data.index[0], price_data.index[0], price_data.index[2], price_data.index[3]]
    )
    price_data.index = duplicated_index

    with pytest.raises(ValueError, match="duplicadas"):
        validate_price_data(price_data=price_data, config=config)


def test_validate_price_data_rejects_low_observation_assets() -> None:
    config = ProjectConfig(min_observations_per_asset=4, max_null_ratio_per_asset=0.80)
    price_data = _build_valid_price_frame()
    price_data.loc[price_data.index[-1], "USDBRL=X"] = pd.NA

    with pytest.raises(ValueError, match="observacoes insuficientes"):
        validate_price_data(price_data=price_data, config=config)


def test_validate_price_data_rejects_high_null_ratio_assets() -> None:
    config = ProjectConfig(min_observations_per_asset=1, max_null_ratio_per_asset=0.10)
    price_data = _build_valid_price_frame()

    with pytest.raises(ValueError, match="percentual de nulos"):
        validate_price_data(price_data=price_data, config=config)


def test_calculate_validation_metrics() -> None:
    price_data = _build_valid_price_frame()

    observation_counts = calculate_observation_counts(price_data)
    null_percentages = calculate_null_percentages(price_data)

    assert observation_counts["CDI"] == 3
    assert null_percentages["CDI"] == pytest.approx(0.25)


def _build_valid_price_frame() -> pd.DataFrame:
    index = pd.date_range("2024-01-31", periods=4, freq="ME")
    return pd.DataFrame(
        {
            "BOVA11.SA": [100.0, 101.0, 102.0, 103.0],
            "IVVB11.SA": [200.0, 202.0, 204.0, 206.0],
            "IMAB11.SA": [300.0, 301.0, 302.0, 303.0],
            "USDBRL=X": [4.9, 5.0, 5.1, 5.2],
            "CDI": [13.15, 13.20, pd.NA, 13.25],
        },
        index=index,
    )
