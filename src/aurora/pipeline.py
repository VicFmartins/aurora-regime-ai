"""End-to-end execution pipeline for Aurora Regime AI."""

from __future__ import annotations

from dataclasses import dataclass
from json import dumps
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from aurora.analysis import build_performance_table
from aurora.backtest import (
    BacktestResult,
    build_benchmark_equity_curve,
    build_benchmark_suite,
    run_backtest,
)
from aurora.config import ProjectConfig
from aurora.data import get_price_data, load_prices_from_csv
from aurora.features import build_feature_set
from aurora.portfolio import build_target_weights
from aurora.regime import classify_regimes
from aurora.visualization import (
    plot_drawdown,
    plot_equity_curves,
    plot_performance_table,
    plot_period_returns,
    plot_regimes,
    plot_weights,
    save_figure,
)


@dataclass(frozen=True)
class LoadedPriceData:
    """Price dataset plus provenance metadata for pipeline execution."""

    prices: pd.DataFrame
    source: str
    notes: str | None = None


@dataclass(frozen=True)
class PipelineResult:
    """Structured output of the full Aurora research pipeline."""

    config: ProjectConfig
    data_source: str
    prices: pd.DataFrame
    features: pd.DataFrame
    regimes: pd.DataFrame
    target_weights: pd.DataFrame
    backtest: BacktestResult
    benchmark_returns: pd.DataFrame
    benchmark_equity_curves: pd.DataFrame
    performance_summary: pd.DataFrame
    saved_tables: dict[str, Path]
    saved_figures: dict[str, Path]
    metadata: dict[str, Any]


def run_full_pipeline(
    config: ProjectConfig,
    force_download: bool = False,
) -> PipelineResult:
    """Run the complete Aurora workflow from data loading to report artifacts.

    The function first attempts the normal online flow via cache/manual sources/yfinance.
    If that online step fails with a download-oriented runtime error, the pipeline falls
    back to the offline mode automatically.
    """
    _ensure_runtime_directories(config)

    try:
        loaded_prices = _load_online_prices(config=config, force_download=force_download)
    except RuntimeError as exc:
        loaded_prices = _load_offline_prices(config=config, reason=str(exc))

    return _run_pipeline_from_prices(config=config, loaded_prices=loaded_prices)


def run_offline_pipeline(config: ProjectConfig) -> PipelineResult:
    """Run the Aurora workflow using only offline-compatible local/synthetic inputs."""
    _ensure_runtime_directories(config)
    loaded_prices = _load_offline_prices(
        config=config,
        reason="Execucao offline solicitada explicitamente.",
    )
    return _run_pipeline_from_prices(config=config, loaded_prices=loaded_prices)


def format_pipeline_summary(result: PipelineResult) -> str:
    """Build a concise terminal summary for a completed pipeline run."""
    summary_table = result.performance_summary.round(4).to_string()
    saved_tables = "\n".join(
        f"- {name}: {path.as_posix()}" for name, path in sorted(result.saved_tables.items())
    )
    saved_figures = "\n".join(
        f"- {name}: {path.as_posix()}" for name, path in sorted(result.saved_figures.items())
    )

    return (
        "Aurora Regime AI pipeline concluido.\n"
        f"Fonte de dados: {result.data_source}\n"
        f"Observacoes de preco: {len(result.prices)}\n"
        "Janela de dados: "
        f"{result.prices.index.min().date()} -> {result.prices.index.max().date()}\n"
        f"Rebalanceamentos: {result.backtest.metadata['num_rebalances']}\n"
        "\n"
        "Resumo de performance:\n"
        f"{summary_table}\n"
        "\n"
        "Tabelas salvas:\n"
        f"{saved_tables}\n"
        "\n"
        "Figuras salvas:\n"
        f"{saved_figures}"
    )


def _run_pipeline_from_prices(
    config: ProjectConfig,
    loaded_prices: LoadedPriceData,
) -> PipelineResult:
    prices = loaded_prices.prices
    features = build_feature_set(prices=prices, config=config)
    regimes = classify_regimes(features=features, config=config)
    target_weights = build_target_weights(regime_series=regimes["regime"], config=config)
    backtest_result = run_backtest(prices=prices, target_weights=target_weights, config=config)

    benchmark_returns = build_benchmark_suite(
        config=config,
        prices=prices,
        align_to=backtest_result.portfolio_returns.index,
    )
    benchmark_equity_curves = _build_benchmark_equity_curves(
        benchmark_returns=benchmark_returns,
        config=config,
    )

    monthly_strategy_returns = _compound_period_returns(
        backtest_result.portfolio_returns,
        frequency="M",
    )
    monthly_benchmark_returns = _compound_period_returns(benchmark_returns, frequency="M")
    performance_summary = build_performance_table(
        strategy_returns=monthly_strategy_returns,
        benchmark_returns=monthly_benchmark_returns,
        config=config,
        rebalance_log=backtest_result.rebalance_log,
        periods_per_year=12,
    )

    saved_tables = _save_tabular_artifacts(
        config=config,
        prices=prices,
        features=features,
        regimes=regimes,
        target_weights=target_weights,
        backtest_result=backtest_result,
        benchmark_returns=benchmark_returns,
        monthly_strategy_returns=monthly_strategy_returns,
        monthly_benchmark_returns=monthly_benchmark_returns,
    )
    saved_figures = _save_visual_artifacts(
        config=config,
        backtest_result=backtest_result,
        benchmark_equity_curves=benchmark_equity_curves,
        benchmark_returns=benchmark_returns,
        regimes=regimes,
        performance_summary=performance_summary,
    )

    metadata = {
        "data_source": loaded_prices.source,
        "data_notes": loaded_prices.notes,
        "end_date": str(prices.index.max().date()),
        "num_assets": len(prices.columns),
        "num_features": len(features.columns),
        "num_observations": len(prices),
        "num_regime_rows": len(regimes),
        "start_date": str(prices.index.min().date()),
    }

    return PipelineResult(
        config=config,
        data_source=loaded_prices.source,
        prices=prices,
        features=features,
        regimes=regimes,
        target_weights=target_weights,
        backtest=backtest_result,
        benchmark_returns=benchmark_returns,
        benchmark_equity_curves=benchmark_equity_curves,
        performance_summary=performance_summary,
        saved_tables=saved_tables,
        saved_figures=saved_figures,
        metadata=metadata,
    )


def _load_online_prices(
    config: ProjectConfig,
    force_download: bool,
) -> LoadedPriceData:
    cache_path = Path(config.cache_dir) / "prices.parquet"
    manual_path = Path(config.raw_data_dir) / "prices.csv"
    cache_available = cache_path.exists() and not force_download

    prices = get_price_data(config=config, force_download=force_download)

    if cache_available:
        source = "cache"
        notes = f"Precos carregados do cache local em '{cache_path.as_posix()}'."
    elif manual_path.exists():
        source = "manual_or_hybrid"
        notes = (
            "Precos carregados com suporte de CSV manual em "
            f"'{manual_path.as_posix()}', possivelmente combinados com yfinance."
        )
    else:
        source = "yfinance"
        notes = "Precos carregados a partir do fluxo principal online."

    return LoadedPriceData(prices=prices, source=source, notes=notes)


def _load_offline_prices(
    config: ProjectConfig,
    *,
    reason: str,
) -> LoadedPriceData:
    example_path = Path(config.raw_data_dir) / "example_prices.csv"
    if example_path.exists():
        try:
            example_prices = load_prices_from_csv(example_path, config=config)
        except ValueError:
            synthetic_prices = _build_synthetic_prices(config)
            return LoadedPriceData(
                prices=synthetic_prices,
                source="synthetic",
                notes=(
                    f"{reason} O arquivo de exemplo '{example_path.as_posix()}' existe, "
                    "mas nao atende aos thresholds atuais da configuracao; a pipeline "
                    "gerou dados sinteticos deterministas para prosseguir."
                ),
            )

        return LoadedPriceData(
            prices=example_prices,
            source="example_csv",
            notes=(
                f"{reason} Precos carregados do arquivo demonstrativo '{example_path.as_posix()}'."
            ),
        )

    synthetic_prices = _build_synthetic_prices(config)
    return LoadedPriceData(
        prices=synthetic_prices,
        source="synthetic",
        notes=(
            f"{reason} Nenhum CSV offline valido foi encontrado; a pipeline gerou dados "
            "sinteticos deterministas para manter o fluxo reprodutivel."
        ),
    )


def _build_synthetic_prices(config: ProjectConfig) -> pd.DataFrame:
    dates = pd.bdate_range(config.start_date, config.end_date)
    if len(dates) == 0:
        raise RuntimeError(
            "Nao foi possivel gerar dados sinteticos porque a janela de datas configurada e vazia."
        )

    index = np.arange(len(dates), dtype=float)
    synthetic_prices = pd.DataFrame(
        {
            "BOVA11.SA": 100.0 * np.exp(0.00035 * index + 0.08 * np.sin(index / 42.0)),
            "IVVB11.SA": 120.0 * np.exp(0.00028 * index + 0.06 * np.cos(index / 55.0)),
            "IMAB11.SA": 90.0 * np.exp(0.00016 * index + 0.02 * np.sin(index / 80.0)),
            "USDBRL=X": 4.2 * np.exp(0.00005 * index + 0.04 * np.sin(index / 65.0)),
            "CDI": 1.0 * np.exp(0.00010 * index),
        },
        index=dates,
    )
    synthetic_prices.index.name = "Date"

    if len(synthetic_prices) < config.min_observations_per_asset:
        raise RuntimeError(
            "Modo offline sintetico indisponivel para a configuracao atual: a janela "
            "de datas gera menos observacoes que o minimo exigido. Ajuste as datas ou "
            "reduza 'min_observations_per_asset' para testes locais."
        )

    return synthetic_prices


def _build_benchmark_equity_curves(
    benchmark_returns: pd.DataFrame,
    config: ProjectConfig,
) -> pd.DataFrame:
    equity_curves = []
    for column in benchmark_returns.columns:
        curve = build_benchmark_equity_curve(benchmark_returns[column], config=config)
        curve.name = str(column)
        equity_curves.append(curve)
    return pd.concat(equity_curves, axis=1)


def _compound_period_returns(
    returns: pd.Series | pd.DataFrame,
    *,
    frequency: str,
) -> pd.Series | pd.DataFrame:
    if isinstance(returns, pd.Series):
        frame = returns.to_frame(name=returns.name or "series")
    else:
        frame = returns
    normalized = frame.copy()
    normalized.index = pd.to_datetime(normalized.index)
    normalized = normalized.sort_index()

    compounded = normalized.groupby(normalized.index.to_period(frequency)).apply(
        lambda period_frame: (1.0 + period_frame).prod() - 1.0
    )
    compounded.index = compounded.index.to_timestamp(how="end").normalize()

    if isinstance(returns, pd.Series):
        series = compounded.iloc[:, 0]
        series.name = returns.name
        return series
    return compounded


def _save_tabular_artifacts(
    *,
    config: ProjectConfig,
    prices: pd.DataFrame,
    features: pd.DataFrame,
    regimes: pd.DataFrame,
    target_weights: pd.DataFrame,
    backtest_result: BacktestResult,
    benchmark_returns: pd.DataFrame,
    monthly_strategy_returns: pd.Series,
    monthly_benchmark_returns: pd.DataFrame,
) -> dict[str, Path]:
    processed_dir = Path(config.processed_data_dir)
    reports_dir = Path(config.reports_tables_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    prices_path = processed_dir / "prices_used.parquet"
    features_path = processed_dir / "features.parquet"
    regimes_path = processed_dir / "regimes.parquet"
    weights_path = processed_dir / "target_weights.parquet"
    serializable_regimes = regimes.copy()
    if "signals" in serializable_regimes.columns:
        serializable_regimes["signals"] = serializable_regimes["signals"].map(
            lambda value: dumps(value, sort_keys=True, default=str)
        )

    prices.to_parquet(prices_path)
    features.to_parquet(features_path)
    serializable_regimes.to_parquet(regimes_path)
    target_weights.to_parquet(weights_path)

    strategy_returns_path = reports_dir / "strategy_returns.csv"
    benchmark_returns_path = reports_dir / "benchmark_returns.csv"
    monthly_returns_path = reports_dir / "monthly_returns.csv"
    regimes_report_path = reports_dir / "classified_regimes.csv"
    weights_report_path = reports_dir / "target_weights.csv"
    rebalance_log_path = reports_dir / "rebalance_log.csv"
    performance_summary_path = reports_dir / "performance_summary.csv"

    backtest_result.portfolio_returns.to_csv(strategy_returns_path, header=True)
    benchmark_returns.to_csv(benchmark_returns_path, index=True)
    pd.concat(
        [monthly_strategy_returns.rename("strategy"), monthly_benchmark_returns],
        axis=1,
    ).to_csv(monthly_returns_path, index=True)
    regimes.to_csv(regimes_report_path, index=True)
    target_weights.to_csv(weights_report_path, index=True)
    backtest_result.rebalance_log.to_csv(rebalance_log_path, index=False)

    return {
        "benchmark_returns": benchmark_returns_path,
        "classified_regimes": regimes_report_path,
        "monthly_returns": monthly_returns_path,
        "performance_summary": performance_summary_path,
        "rebalance_log": rebalance_log_path,
        "strategy_returns": strategy_returns_path,
        "target_weights": weights_report_path,
    }


def _save_visual_artifacts(
    *,
    config: ProjectConfig,
    backtest_result: BacktestResult,
    benchmark_equity_curves: pd.DataFrame,
    benchmark_returns: pd.DataFrame,
    regimes: pd.DataFrame,
    performance_summary: pd.DataFrame,
) -> dict[str, Path]:
    figures_dir = Path(config.reports_figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    strategy_equity = backtest_result.equity_curve.rename("strategy")
    return_series = pd.concat(
        [backtest_result.portfolio_returns.rename("strategy"), benchmark_returns],
        axis=1,
    )

    figures = {
        "drawdown": plot_drawdown(return_series),
        "equity_curve": plot_equity_curves(strategy_equity, benchmark_equity_curves),
        "performance_table": plot_performance_table(performance_summary),
        "period_returns": plot_period_returns(return_series, frequency="M"),
        "regimes": plot_regimes(regimes),
        "weights": plot_weights(backtest_result.weights_history),
    }

    saved_paths: dict[str, Path] = {}
    for name, figure in figures.items():
        saved_paths[name] = save_figure(figure, figures_dir / f"{name}.html")
    return saved_paths


def _ensure_runtime_directories(config: ProjectConfig) -> None:
    for directory in config.required_directories():
        Path(directory).mkdir(parents=True, exist_ok=True)
