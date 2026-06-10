"""Plotly chart builders for Aurora analysis outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative

REGIME_COLORS = {
    "TENDENCIA_POSITIVA": "#0b8f55",
    "ESTRESSE": "#c0392b",
    "LATERALIZACAO": "#7f8c8d",
    "RECUPERACAO": "#f39c12",
}


def plot_equity_curves(
    strategy_equity_curve: pd.Series,
    benchmark_equity_curves: pd.Series | pd.DataFrame,
) -> go.Figure:
    """Plot strategy equity curve against one or more benchmark equity curves."""
    benchmark_frame = _coerce_frame(benchmark_equity_curves)
    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=strategy_equity_curve.index,
            y=strategy_equity_curve,
            mode="lines",
            name=strategy_equity_curve.name or "strategy",
            line={"width": 3},
        )
    )

    for column in benchmark_frame.columns:
        figure.add_trace(
            go.Scatter(
                x=benchmark_frame.index,
                y=benchmark_frame[column],
                mode="lines",
                name=str(column),
            )
        )

    figure.update_layout(
        title="Equity Curve: Estrategia vs Benchmarks",
        xaxis_title="Data",
        yaxis_title="Patrimonio",
        template="plotly_white",
        legend_title="Serie",
    )
    return figure


def plot_drawdown(
    returns: pd.Series | pd.DataFrame,
) -> go.Figure:
    """Plot drawdown over time for one or more return series."""
    returns_frame = _coerce_frame(returns)
    drawdown_frame = returns_frame.apply(_compute_drawdown_series)

    figure = go.Figure()
    for column in drawdown_frame.columns:
        figure.add_trace(
            go.Scatter(
                x=drawdown_frame.index,
                y=drawdown_frame[column],
                mode="lines",
                name=str(column),
                fill="tozeroy",
            )
        )

    figure.update_layout(
        title="Drawdown Ao Longo Do Tempo",
        xaxis_title="Data",
        yaxis_title="Drawdown",
        template="plotly_white",
        legend_title="Serie",
    )
    return figure


def plot_regimes(
    regime_data: pd.Series | pd.DataFrame,
) -> go.Figure:
    """Plot classified regimes over time."""
    regime_series = _extract_regime_series(regime_data)

    figure = go.Figure()
    for regime_name, color in REGIME_COLORS.items():
        mask = regime_series == regime_name
        if not mask.any():
            continue
        figure.add_trace(
            go.Scatter(
                x=regime_series.index[mask],
                y=[regime_name] * int(mask.sum()),
                mode="markers",
                marker={"size": 12, "color": color},
                name=regime_name,
            )
        )

    figure.update_layout(
        title="Regimes Classificados No Tempo",
        xaxis_title="Data",
        yaxis_title="Regime",
        template="plotly_white",
        legend_title="Regime",
    )
    return figure


def plot_weights(
    weights_history: pd.DataFrame,
) -> go.Figure:
    """Plot portfolio weights over time as a stacked area chart."""
    figure = go.Figure()
    palette = qualitative.Set2

    for index, column in enumerate(weights_history.columns):
        figure.add_trace(
            go.Scatter(
                x=weights_history.index,
                y=weights_history[column],
                mode="lines",
                name=str(column),
                stackgroup="weights",
                line={"width": 1.5, "color": palette[index % len(palette)]},
            )
        )

    figure.update_layout(
        title="Pesos Da Carteira Ao Longo Do Tempo",
        xaxis_title="Data",
        yaxis_title="Peso",
        template="plotly_white",
        legend_title="Ativo",
    )
    return figure


def plot_period_returns(
    returns: pd.Series | pd.DataFrame,
    frequency: str = "M",
) -> go.Figure:
    """Plot compounded period returns, monthly by default."""
    returns_frame = _coerce_frame(returns)
    compounded = returns_frame.groupby(returns_frame.index.to_period(frequency)).apply(
        lambda frame: (1.0 + frame).prod() - 1.0
    )
    compounded.index = compounded.index.to_timestamp()

    figure = go.Figure()
    for column in compounded.columns:
        figure.add_trace(
            go.Bar(
                x=compounded.index,
                y=compounded[column],
                name=str(column),
            )
        )

    period_label = "Mensais" if frequency.upper().startswith("M") else "Por Periodo"
    figure.update_layout(
        title=f"Retornos {period_label}",
        xaxis_title="Data",
        yaxis_title="Retorno",
        template="plotly_white",
        barmode="group",
        legend_title="Serie",
    )
    return figure


def plot_performance_table(
    performance_summary: pd.DataFrame,
) -> go.Figure:
    """Render the performance summary table as a Plotly table."""
    formatted_summary = performance_summary.copy()
    formatted_summary = formatted_summary.round(4)

    table_values = [
        formatted_summary.index.tolist(),
        *[formatted_summary[col] for col in formatted_summary.columns],
    ]

    figure = go.Figure(
        data=[
            go.Table(
                header={
                    "values": ["serie", *formatted_summary.columns.tolist()],
                    "fill_color": "#1f2937",
                    "font": {"color": "white", "size": 12},
                    "align": "left",
                },
                cells={
                    "values": table_values,
                    "fill_color": "#f8fafc",
                    "align": "left",
                },
            )
        ]
    )
    figure.update_layout(title="Resumo De Metricas")
    return figure


def save_figure(
    figure: go.Figure,
    path: str | Path,
) -> Path:
    """Save a Plotly figure as HTML or PNG when supported by the environment."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.suffix.lower() == ".html":
        figure.write_html(output_path)
        return output_path

    if output_path.suffix.lower() == ".png":
        try:
            figure.write_image(output_path)
        except (ImportError, OSError, ValueError) as exc:
            raise RuntimeError(
                "Nao foi possivel exportar PNG. Instale o suporte de imagem do Plotly, "
                "como kaleido, ou salve em HTML."
            ) from exc
        return output_path

    raise ValueError("Formato de saida invalido. Use .html ou .png.")


def _coerce_frame(data: pd.Series | pd.DataFrame) -> pd.DataFrame:
    if isinstance(data, pd.Series):
        name = data.name or "series"
        frame = data.to_frame(name=name)
    else:
        frame = data.copy()

    frame.index = pd.to_datetime(frame.index)
    frame = frame.sort_index()
    return frame


def _extract_regime_series(regime_data: pd.Series | pd.DataFrame) -> pd.Series:
    if isinstance(regime_data, pd.Series):
        regime_series = regime_data.copy()
    elif "regime" in regime_data.columns:
        regime_series = regime_data["regime"].copy()
    else:
        raise ValueError("regime_data precisa ser uma Series ou um DataFrame com coluna 'regime'.")

    regime_series.index = pd.to_datetime(regime_series.index)
    return regime_series.sort_index()


def _compute_drawdown_series(returns: pd.Series) -> pd.Series:
    clean_returns = pd.to_numeric(returns, errors="coerce")
    equity_curve = (1.0 + clean_returns).cumprod()
    running_peak = equity_curve.cummax()
    return equity_curve.div(running_peak).sub(1.0)
