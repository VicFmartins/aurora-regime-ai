"""Prompt assembly helpers for Aurora's GenAI support layer."""

from __future__ import annotations

from typing import Any

import pandas as pd

from aurora.config import ProjectConfig, load_config
from aurora.genai.prompts import MISSING_VALUE_PLACEHOLDER, PROMPT_TEMPLATES


def build_executive_summary_prompt(
    performance_summary: pd.DataFrame | None = None,
    *,
    config: ProjectConfig | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Build the executive-summary prompt from real performance metrics when available."""
    context = _build_prompt_context(
        performance_summary=performance_summary,
        config=config,
        metadata=metadata,
    )
    return PROMPT_TEMPLATES["executive_summary"].substitute(context)


def build_regime_analysis_prompt(
    performance_summary: pd.DataFrame | None = None,
    *,
    regimes: pd.DataFrame | pd.Series | None = None,
    config: ProjectConfig | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Build the regime-analysis prompt from real regime outputs when available."""
    context = _build_prompt_context(
        performance_summary=performance_summary,
        regimes=regimes,
        config=config,
        metadata=metadata,
    )
    return PROMPT_TEMPLATES["regime_analysis"].substitute(context)


def build_limitations_prompt(
    performance_summary: pd.DataFrame | None = None,
    *,
    config: ProjectConfig | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Build the limitations-analysis prompt from observed metrics and metadata."""
    context = _build_prompt_context(
        performance_summary=performance_summary,
        config=config,
        metadata=metadata,
    )
    return PROMPT_TEMPLATES["limitations_analysis"].substitute(context)


def build_bias_review_prompt(
    performance_summary: pd.DataFrame | None = None,
    *,
    config: ProjectConfig | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Build the bias-review prompt with configuration and execution evidence."""
    context = _build_prompt_context(
        performance_summary=performance_summary,
        config=config,
        metadata=metadata,
    )
    return PROMPT_TEMPLATES["bias_review"].substitute(context)


def build_technical_defense_prompt(
    performance_summary: pd.DataFrame | None = None,
    *,
    config: ProjectConfig | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Build the technical-defense prompt from real metrics and project configuration."""
    context = _build_prompt_context(
        performance_summary=performance_summary,
        config=config,
        metadata=metadata,
    )
    return PROMPT_TEMPLATES["technical_defense"].substitute(context)


def build_prompt_bundle(
    performance_summary: pd.DataFrame | None = None,
    *,
    regimes: pd.DataFrame | pd.Series | None = None,
    config: ProjectConfig | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Return the full bundle of Aurora GenAI prompts."""
    return {
        "executive_summary": build_executive_summary_prompt(
            performance_summary,
            config=config,
            metadata=metadata,
        ),
        "regime_analysis": build_regime_analysis_prompt(
            performance_summary,
            regimes=regimes,
            config=config,
            metadata=metadata,
        ),
        "limitations_analysis": build_limitations_prompt(
            performance_summary,
            config=config,
            metadata=metadata,
        ),
        "bias_review": build_bias_review_prompt(
            performance_summary,
            config=config,
            metadata=metadata,
        ),
        "technical_defense": build_technical_defense_prompt(
            performance_summary,
            config=config,
            metadata=metadata,
        ),
    }


def _build_prompt_context(
    *,
    performance_summary: pd.DataFrame | None,
    regimes: pd.DataFrame | pd.Series | None = None,
    config: ProjectConfig | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, str]:
    resolved_config = config or load_config()
    normalized_metadata = metadata or {}
    strategy_row = _extract_row(performance_summary, "strategy")

    context = {
        "benchmark_summary": _build_benchmark_summary(performance_summary),
        "data_source": _string_or_placeholder(normalized_metadata.get("data_source")),
        "date_range": _build_date_range(normalized_metadata),
        "high_volatility_threshold": _format_percent(resolved_config.high_volatility_threshold),
        "latest_regime": _extract_latest_regime(regimes),
        "num_assets": _string_or_placeholder(normalized_metadata.get("num_assets")),
        "num_features": _string_or_placeholder(normalized_metadata.get("num_features")),
        "num_observations": _string_or_placeholder(normalized_metadata.get("num_observations")),
        "positive_momentum_threshold": _format_percent(resolved_config.positive_momentum_threshold),
        "rebalance_frequency": resolved_config.rebalance_frequency,
        "recent_signal_snapshot": _build_recent_signal_snapshot(regimes),
        "regime_distribution": _build_regime_distribution(regimes),
        "regime_target_asset": resolved_config.regime_target_asset,
        "stress_drawdown_threshold": _format_percent(resolved_config.stress_drawdown_threshold),
        "strategy_annualized_return": _metric_from_row(strategy_row, "annualized_return", pct=True),
        "strategy_annualized_volatility": _metric_from_row(
            strategy_row,
            "annualized_volatility",
            pct=True,
        ),
        "strategy_average_turnover": _metric_from_row(strategy_row, "average_turnover", pct=True),
        "strategy_calmar_ratio": _metric_from_row(strategy_row, "calmar_ratio"),
        "strategy_cumulative_return": _metric_from_row(strategy_row, "cumulative_return", pct=True),
        "strategy_hit_rate": _metric_from_row(strategy_row, "hit_rate", pct=True),
        "strategy_max_drawdown": _metric_from_row(strategy_row, "max_drawdown", pct=True),
        "strategy_num_rebalances": _metric_from_row(strategy_row, "num_rebalances", integer=True),
        "strategy_sharpe_ratio": _metric_from_row(strategy_row, "sharpe_ratio"),
    }
    return context


def _extract_row(
    performance_summary: pd.DataFrame | None,
    index_label: str,
) -> pd.Series | None:
    if performance_summary is None or index_label not in performance_summary.index:
        return None
    return performance_summary.loc[index_label]


def _metric_from_row(
    row: pd.Series | None,
    column: str,
    *,
    pct: bool = False,
    integer: bool = False,
) -> str:
    if row is None or column not in row.index:
        return MISSING_VALUE_PLACEHOLDER

    value = row[column]
    if pd.isna(value):
        return MISSING_VALUE_PLACEHOLDER

    if integer:
        return str(int(round(float(value))))
    if pct:
        return _format_percent(float(value))
    return _format_float(float(value))


def _build_benchmark_summary(
    performance_summary: pd.DataFrame | None,
) -> str:
    if performance_summary is None or performance_summary.empty:
        return f"- benchmark: {MISSING_VALUE_PLACEHOLDER}"

    benchmark_lines = []
    benchmark_rows = performance_summary.drop(index="strategy", errors="ignore")
    if benchmark_rows.empty:
        return f"- benchmark: {MISSING_VALUE_PLACEHOLDER}"

    for benchmark_name, row in benchmark_rows.iterrows():
        benchmark_lines.append(
            f"- {benchmark_name}: "
            f"retorno anualizado={_metric_from_row(row, 'annualized_return', pct=True)}, "
            f"sharpe={_metric_from_row(row, 'sharpe_ratio')}, "
            f"max_drawdown={_metric_from_row(row, 'max_drawdown', pct=True)}"
        )
    return "\n".join(benchmark_lines)


def _build_regime_distribution(
    regimes: pd.DataFrame | pd.Series | None,
) -> str:
    regime_series = _extract_regime_series(regimes)
    if regime_series is None or regime_series.empty:
        return f"- regime: {MISSING_VALUE_PLACEHOLDER}"

    counts = regime_series.value_counts(dropna=True)
    total = int(counts.sum())
    lines = []
    for regime_name, count in counts.items():
        share = count / total if total > 0 else float("nan")
        lines.append(f"- {regime_name}: {count} observacoes ({_format_percent(share)})")
    return "\n".join(lines)


def _build_recent_signal_snapshot(
    regimes: pd.DataFrame | pd.Series | None,
) -> str:
    if not isinstance(regimes, pd.DataFrame) or regimes.empty:
        return f"- sinais recentes: {MISSING_VALUE_PLACEHOLDER}"

    latest_row = regimes.iloc[-1]
    signals = latest_row.get("signals")
    if not isinstance(signals, dict) or not signals:
        return f"- sinais recentes: {MISSING_VALUE_PLACEHOLDER}"

    signal_lines = []
    for signal_name, signal_value in sorted(signals.items()):
        signal_lines.append(f"- {signal_name}: {_format_optional_value(signal_value)}")
    return "\n".join(signal_lines)


def _extract_latest_regime(
    regimes: pd.DataFrame | pd.Series | None,
) -> str:
    regime_series = _extract_regime_series(regimes)
    if regime_series is None or regime_series.dropna().empty:
        return MISSING_VALUE_PLACEHOLDER
    return str(regime_series.dropna().iloc[-1])


def _extract_regime_series(
    regimes: pd.DataFrame | pd.Series | None,
) -> pd.Series | None:
    if regimes is None:
        return None
    if isinstance(regimes, pd.Series):
        return regimes
    if "regime" in regimes.columns:
        return regimes["regime"]
    return None


def _build_date_range(metadata: dict[str, Any]) -> str:
    start_date = metadata.get("start_date")
    end_date = metadata.get("end_date")
    if start_date is None or end_date is None:
        return MISSING_VALUE_PLACEHOLDER
    return f"{start_date} -> {end_date}"


def _string_or_placeholder(value: Any) -> str:
    if value is None:
        return MISSING_VALUE_PLACEHOLDER
    return str(value)


def _format_percent(value: float) -> str:
    return f"{value:.2%}"


def _format_float(value: float) -> str:
    return f"{value:.4f}"


def _format_optional_value(value: Any) -> str:
    if value is None or pd.isna(value):
        return MISSING_VALUE_PLACEHOLDER
    if isinstance(value, float):
        return _format_float(value)
    return str(value)
