"""Central configuration for the Aurora Regime AI project."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectConfig:
    """Single source of truth for project-level methodological parameters."""

    assets: dict[str, str] = field(
        default_factory=lambda: {
            "BOVA11.SA": "renda variavel Brasil",
            "IVVB11.SA": "exposicao internacional",
            "IMAB11.SA": "renda fixa inflacao",
            "USDBRL=X": "protecao cambial",
            "CDI": "caixa defensivo/proxy",
        }
    )
    asset_weights: dict[str, float] = field(
        default_factory=lambda: {
            "BOVA11.SA": 0.20,
            "IVVB11.SA": 0.20,
            "IMAB11.SA": 0.20,
            "USDBRL=X": 0.20,
            "CDI": 0.20,
        }
    )
    start_date: str = "2015-01-01"
    end_date: str = "2024-12-31"
    frequency: str = "monthly"
    initial_capital: float = 100000.0
    momentum_windows: tuple[int, int, int] = (63, 126, 252)
    volatility_window: int = 21
    drawdown_window: int = 252
    zscore_window: int = 252
    correlation_window: int = 60
    stress_drawdown_threshold: float = -0.15
    high_volatility_threshold: float = 0.30
    positive_momentum_threshold: float = 0.0
    rebalance_frequency: str = "M"
    transaction_cost_bps: int = 0
    raw_data_dir: Path = Path("data/raw")
    processed_data_dir: Path = Path("data/processed")
    cache_dir: Path = Path("data/cache")
    reports_figures_dir: Path = Path("reports/figures")
    reports_tables_dir: Path = Path("reports/tables")

    def required_directories(self) -> tuple[Path, ...]:
        """Return all directories that should exist for local project execution."""
        return (
            self.raw_data_dir,
            self.processed_data_dir,
            self.cache_dir,
            self.reports_figures_dir,
            self.reports_tables_dir,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the configuration into JSON-friendly primitives."""
        serialized: dict[str, Any] = {}
        for key, value in asdict(self).items():
            if isinstance(value, Path):
                serialized[key] = value.as_posix()
            else:
                serialized[key] = value
        return serialized


@lru_cache(maxsize=1)
def load_config() -> ProjectConfig:
    """Load the default Aurora configuration."""
    return ProjectConfig()
