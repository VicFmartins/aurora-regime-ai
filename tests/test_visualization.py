from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from aurora.analysis import summarize_performance
from aurora.visualization import (
    plot_drawdown,
    plot_equity_curves,
    plot_performance_table,
    plot_period_returns,
    plot_regimes,
    plot_weights,
    save_figure,
)


def test_plot_equity_curves_returns_figure() -> None:
    strategy_equity, benchmark_equity, *_ = _build_visual_inputs()
    figure = plot_equity_curves(strategy_equity, benchmark_equity)
    assert isinstance(figure, go.Figure)


def test_plot_drawdown_returns_figure() -> None:
    _, _, returns, _, _, _ = _build_visual_inputs()
    figure = plot_drawdown(returns)
    assert isinstance(figure, go.Figure)


def test_plot_regimes_returns_figure() -> None:
    _, _, _, regimes, _, _ = _build_visual_inputs()
    figure = plot_regimes(regimes)
    assert isinstance(figure, go.Figure)


def test_plot_weights_returns_figure() -> None:
    _, _, _, _, weights, _ = _build_visual_inputs()
    figure = plot_weights(weights)
    assert isinstance(figure, go.Figure)


def test_plot_period_returns_returns_figure() -> None:
    _, _, returns, _, _, _ = _build_visual_inputs()
    figure = plot_period_returns(returns)
    assert isinstance(figure, go.Figure)


def test_plot_performance_table_returns_figure() -> None:
    _, _, _, _, _, summary = _build_visual_inputs()
    figure = plot_performance_table(summary)
    assert isinstance(figure, go.Figure)


def test_save_figure_writes_html(tmp_path: Path) -> None:
    strategy_equity, benchmark_equity, *_ = _build_visual_inputs()
    figure = plot_equity_curves(strategy_equity, benchmark_equity)

    output_path = save_figure(figure, tmp_path / "equity_curve.html")

    assert output_path.exists()


def _build_visual_inputs() -> tuple[
    pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    index = pd.date_range("2024-01-31", periods=4, freq="ME")

    strategy_equity = pd.Series(
        [100000.0, 102000.0, 101000.0, 105000.0],
        index=index,
        name="strategy",
    )
    benchmark_equity = pd.DataFrame(
        {
            "buy_and_hold": [100000.0, 101000.0, 103000.0, 104000.0],
            "equal_weight": [100000.0, 100500.0, 101500.0, 103000.0],
        },
        index=index,
    )
    returns = pd.Series([0.02, -0.01, 0.04, 0.01], index=index, name="strategy")
    regimes = pd.DataFrame(
        {"regime": ["ESTRESSE", "RECUPERACAO", "LATERALIZACAO", "TENDENCIA_POSITIVA"]},
        index=index,
    )
    weights = pd.DataFrame(
        {
            "BOVA11.SA": [0.1, 0.2, 0.2, 0.4],
            "IVVB11.SA": [0.1, 0.2, 0.2, 0.3],
            "IMAB11.SA": [0.3, 0.2, 0.2, 0.1],
            "USDBRL=X": [0.2, 0.1, 0.2, 0.05],
            "CDI": [0.3, 0.3, 0.2, 0.15],
        },
        index=index,
    )
    summary = summarize_performance(
        strategy_returns=returns,
        benchmark_returns=pd.DataFrame({"buy_and_hold": [0.01, 0.0, 0.03, 0.01]}, index=index),
        rebalance_log=pd.DataFrame({"turnover": [1.0, 0.5, 0.25, 0.2]}),
    )
    return strategy_equity, benchmark_equity, returns, regimes, weights, summary
