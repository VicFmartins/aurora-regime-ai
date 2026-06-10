from __future__ import annotations

from aurora import ProjectConfig, load_config
from aurora.analysis import summarize_performance
from aurora.backtest import build_benchmark_suite, run_backtest
from aurora.data import get_price_data
from aurora.features import __doc__ as features_doc
from aurora.features import build_feature_set
from aurora.portfolio import build_target_weights
from aurora.regime import __doc__ as regime_doc
from aurora.regime import classify_regimes
from aurora.visualization import plot_equity_curves


def test_basic_imports_and_settings() -> None:
    config = load_config()

    assert isinstance(config, ProjectConfig)
    assert config.frequency == "monthly"
    assert config.rebalance_frequency == "M"
    assert callable(summarize_performance)
    assert callable(run_backtest)
    assert callable(build_benchmark_suite)
    assert callable(get_price_data)
    assert callable(build_feature_set)
    assert callable(classify_regimes)
    assert callable(build_target_weights)
    assert callable(plot_equity_curves)
    assert features_doc is not None
    assert regime_doc is not None
