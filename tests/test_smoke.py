from __future__ import annotations

from aurora import ProjectConfig, load_config
from aurora.data import get_price_data
from aurora.features import __doc__ as features_doc
from aurora.regime import __doc__ as regime_doc


def test_basic_imports_and_settings() -> None:
    config = load_config()

    assert isinstance(config, ProjectConfig)
    assert config.frequency == "monthly"
    assert config.rebalance_frequency == "M"
    assert callable(get_price_data)
    assert features_doc is not None
    assert regime_doc is not None
