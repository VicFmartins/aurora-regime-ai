from __future__ import annotations

import pandas as pd

from aurora.genai import (
    MISSING_VALUE_PLACEHOLDER,
    build_bias_review_prompt,
    build_executive_summary_prompt,
    build_limitations_prompt,
    build_prompt_bundle,
    build_regime_analysis_prompt,
    build_technical_defense_prompt,
)


def test_executive_summary_prompt_contains_real_metrics() -> None:
    prompt = build_executive_summary_prompt(
        _build_performance_summary(),
        metadata=_build_metadata(),
    )

    assert "Aurora Regime AI" in prompt
    assert "retorno anualizado: 12.34%" in prompt
    assert "sharpe ratio: 1.2100" in prompt
    assert "buy_and_hold__BOVA11.SA" in prompt
    assert "nao recomendar investimento" in prompt


def test_regime_analysis_prompt_contains_distribution_and_signals() -> None:
    prompt = build_regime_analysis_prompt(
        _build_performance_summary(),
        regimes=_build_regimes(),
        metadata=_build_metadata(),
    )

    assert "ultimo regime observado: RECUPERACAO" in prompt
    assert "- ESTRESSE: 1 observacoes (33.33%)" in prompt
    assert "- RECUPERACAO: 2 observacoes (66.67%)" in prompt
    assert "- momentum_short: 0.0500" in prompt
    assert "- zscore_delta: 0.4000" in prompt


def test_prompt_bundle_uses_placeholders_when_data_is_missing() -> None:
    prompt_bundle = build_prompt_bundle()

    assert prompt_bundle["executive_summary"]
    assert prompt_bundle["regime_analysis"]
    assert prompt_bundle["limitations_analysis"]
    assert prompt_bundle["bias_review"]
    assert prompt_bundle["technical_defense"]
    assert MISSING_VALUE_PLACEHOLDER in prompt_bundle["executive_summary"]
    assert MISSING_VALUE_PLACEHOLDER in prompt_bundle["regime_analysis"]


def test_bias_and_limitations_prompts_keep_expected_fields() -> None:
    performance_summary = _build_performance_summary()
    metadata = _build_metadata()

    bias_prompt = build_bias_review_prompt(performance_summary, metadata=metadata)
    limitations_prompt = build_limitations_prompt(performance_summary, metadata=metadata)
    defense_prompt = build_technical_defense_prompt(performance_summary, metadata=metadata)

    assert "look-ahead bias" in bias_prompt
    assert "frequencia de rebalanceamento: M" in bias_prompt
    assert "max drawdown da estrategia: -8.90%" in limitations_prompt
    assert "numero de ativos: 5" in defense_prompt
    assert "por que GenAI nao decide alocacao" in defense_prompt


def _build_performance_summary() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cumulative_return": {"strategy": 0.4567, "buy_and_hold__BOVA11.SA": 0.3891},
            "annualized_return": {"strategy": 0.1234, "buy_and_hold__BOVA11.SA": 0.0987},
            "annualized_volatility": {"strategy": 0.0678, "buy_and_hold__BOVA11.SA": 0.1123},
            "sharpe_ratio": {"strategy": 1.21, "buy_and_hold__BOVA11.SA": 0.88},
            "max_drawdown": {"strategy": -0.089, "buy_and_hold__BOVA11.SA": -0.153},
            "calmar_ratio": {"strategy": 1.39, "buy_and_hold__BOVA11.SA": 0.64},
            "hit_rate": {"strategy": 0.58, "buy_and_hold__BOVA11.SA": 0.52},
            "best_month": {"strategy": 0.045, "buy_and_hold__BOVA11.SA": 0.061},
            "worst_month": {"strategy": -0.021, "buy_and_hold__BOVA11.SA": -0.048},
            "num_rebalances": {"strategy": 24.0, "buy_and_hold__BOVA11.SA": float("nan")},
            "average_turnover": {"strategy": 0.14, "buy_and_hold__BOVA11.SA": float("nan")},
        }
    )


def _build_regimes() -> pd.DataFrame:
    index = pd.date_range("2024-01-31", periods=3, freq="ME")
    return pd.DataFrame(
        {
            "regime": ["ESTRESSE", "RECUPERACAO", "RECUPERACAO"],
            "signals": [
                {"drawdown": -0.2, "volatility": 0.31},
                {"momentum_short": 0.03, "zscore_delta": 0.2},
                {"momentum_short": 0.05, "zscore_delta": 0.4},
            ],
        },
        index=index,
    )


def _build_metadata() -> dict[str, object]:
    return {
        "data_source": "synthetic",
        "start_date": "2020-01-01",
        "end_date": "2024-12-31",
        "num_assets": 5,
        "num_features": 19,
        "num_observations": 60,
    }
