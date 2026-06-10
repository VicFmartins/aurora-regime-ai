from __future__ import annotations

from datetime import date

import pytest

from aurora.config import ProjectConfig, load_config


def test_load_config_returns_default_project_config() -> None:
    config = load_config()

    assert isinstance(config, ProjectConfig)
    assert config.start_date == "2015-01-01"
    assert config.end_date == "2024-12-31"
    assert config.initial_capital == 100000.0


def test_default_assets_exist() -> None:
    config = load_config()

    assert config.assets == {
        "BOVA11.SA": "renda variavel Brasil",
        "IVVB11.SA": "exposicao internacional",
        "IMAB11.SA": "renda fixa inflacao",
        "USDBRL=X": "protecao cambial",
        "CDI": "caixa defensivo/proxy",
    }


def test_weights_and_parameters_are_coherent() -> None:
    config = load_config()

    assert set(config.asset_weights) == set(config.assets)
    assert sum(config.asset_weights.values()) == pytest.approx(1.0)
    assert all(weight >= 0.0 for weight in config.asset_weights.values())
    assert config.momentum_windows == tuple(sorted(config.momentum_windows))
    assert config.volatility_window > 0
    assert config.drawdown_window >= config.volatility_window
    assert config.zscore_window > 0
    assert config.correlation_window > 0
    assert config.stress_drawdown_threshold < 0.0
    assert config.high_volatility_threshold > 0.0
    assert config.positive_momentum_threshold == 0.0
    assert config.transaction_cost_bps >= 0
    assert config.min_observations_per_asset > 0
    assert 0.0 <= config.max_null_ratio_per_asset <= 1.0
    assert config.rebalance_frequency == "M"
    assert date.fromisoformat(config.start_date) < date.fromisoformat(config.end_date)


def test_relative_paths_can_be_created(tmp_path) -> None:
    config = load_config()

    for relative_dir in config.required_directories():
        assert not relative_dir.is_absolute()
        target_dir = tmp_path / relative_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        assert target_dir.exists()
        assert target_dir.is_dir()
