from __future__ import annotations

from pathlib import Path

import pandas as pd

from aurora.config import ProjectConfig
from aurora.pipeline import run_full_pipeline, run_offline_pipeline


def test_run_full_pipeline_with_stubbed_price_loader(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config = _build_test_config(tmp_path)
    stubbed_prices = _build_test_prices(config)

    monkeypatch.setattr("aurora.pipeline.get_price_data", lambda **_: stubbed_prices)

    result = run_full_pipeline(config)

    assert result.data_source == "yfinance"
    assert not result.performance_summary.empty
    assert "strategy" in result.performance_summary.index
    assert result.saved_tables["performance_summary"].exists()
    assert result.saved_figures["equity_curve"].exists()


def test_run_offline_pipeline_uses_synthetic_fallback(tmp_path: Path) -> None:
    config = _build_test_config(tmp_path)

    result = run_offline_pipeline(config)

    assert result.data_source == "synthetic"
    assert result.metadata["data_notes"] is not None
    assert result.saved_tables["monthly_returns"].exists()
    assert result.saved_figures["weights"].exists()


def test_run_offline_pipeline_uses_example_csv_when_valid(tmp_path: Path) -> None:
    config = _build_test_config(tmp_path)
    example_path = Path("data/raw/example_prices.csv")
    target_path = config.raw_data_dir / "example_prices.csv"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")

    result = run_offline_pipeline(config)

    assert result.data_source == "example_csv"
    assert "dados ficticios de exemplo" in (result.metadata["data_notes"] or "")
    assert result.saved_tables["performance_summary"].exists()


def _build_test_config(tmp_path: Path) -> ProjectConfig:
    return ProjectConfig(
        start_date="2020-01-01",
        end_date="2020-12-31",
        momentum_windows=(5, 10, 20),
        volatility_window=5,
        drawdown_window=20,
        zscore_window=20,
        correlation_window=10,
        min_observations_per_asset=60,
        max_null_ratio_per_asset=0.05,
        raw_data_dir=tmp_path / "data" / "raw",
        processed_data_dir=tmp_path / "data" / "processed",
        cache_dir=tmp_path / "data" / "cache",
        reports_figures_dir=tmp_path / "reports" / "figures",
        reports_tables_dir=tmp_path / "reports" / "tables",
    )


def _build_test_prices(config: ProjectConfig) -> pd.DataFrame:
    dates = pd.bdate_range(config.start_date, config.end_date)
    index = pd.Series(range(len(dates)), index=dates, dtype=float)
    prices = pd.DataFrame(
        {
            "BOVA11.SA": 100.0 + index * 0.4,
            "IVVB11.SA": 110.0 + index * 0.35,
            "IMAB11.SA": 90.0 + index * 0.1,
            "USDBRL=X": 4.8 + index * 0.002,
            "CDI": 1.0 + index * 0.001,
        },
        index=dates,
    )
    prices.index.name = "Date"
    return prices
