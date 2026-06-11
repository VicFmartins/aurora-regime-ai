"""Plotly chart builders for Aurora analysis outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative

REGIME_COLORS = {
    "TENDENCIA_POSITIVA": "#34d399",
    "ESTRESSE": "#fb7185",
    "LATERALIZACAO": "#fbbf24",
    "RECUPERACAO": "#a78bfa",
}
CHART_COLORS = ["#5eead4", "#60a5fa", "#f59e0b", "#c084fc", "#fb7185", "#94a3b8"]
GRID_COLOR = "rgba(148, 163, 184, 0.18)"
PLOT_BG = "rgba(9, 19, 35, 0.78)"
PAPER_BG = "rgba(0, 0, 0, 0)"
FONT_COLOR = "#e5eef9"


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
            line={"width": 3.5, "color": CHART_COLORS[0]},
        )
    )

    for index, column in enumerate(benchmark_frame.columns, start=1):
        figure.add_trace(
            go.Scatter(
                x=benchmark_frame.index,
                y=benchmark_frame[column],
                mode="lines",
                name=str(column),
                line={"width": 2.2, "color": CHART_COLORS[index % len(CHART_COLORS)]},
            )
        )

    _apply_dark_layout(
        figure,
        title="Equity Curve: Estrategia vs Benchmarks",
        xaxis_title="Data",
        yaxis_title="Patrimonio",
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
    for index, column in enumerate(drawdown_frame.columns):
        figure.add_trace(
            go.Scatter(
                x=drawdown_frame.index,
                y=drawdown_frame[column],
                mode="lines",
                name=str(column),
                fill="tozeroy",
                line={"width": 2.0, "color": CHART_COLORS[index % len(CHART_COLORS)]},
                fillcolor=_hex_to_rgba(CHART_COLORS[index % len(CHART_COLORS)], 0.18),
            )
        )

    _apply_dark_layout(
        figure,
        title="Drawdown Ao Longo Do Tempo",
        xaxis_title="Data",
        yaxis_title="Drawdown",
        legend_title="Serie",
    )
    figure.update_yaxes(tickformat=".0%")
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

    _apply_dark_layout(
        figure,
        title="Regimes Classificados No Tempo",
        xaxis_title="Data",
        yaxis_title="Regime",
        legend_title="Regime",
    )
    return figure


def plot_weights(
    weights_history: pd.DataFrame,
) -> go.Figure:
    """Plot portfolio weights over time as a stacked area chart."""
    figure = go.Figure()
    palette = CHART_COLORS + list(qualitative.Set2)

    for index, column in enumerate(weights_history.columns):
        figure.add_trace(
            go.Scatter(
                x=weights_history.index,
                y=weights_history[column],
                mode="lines",
                name=str(column),
                stackgroup="weights",
                line={"width": 1.6, "color": palette[index % len(palette)]},
                fillcolor=_hex_to_rgba(palette[index % len(palette)], 0.42),
            )
        )

    _apply_dark_layout(
        figure,
        title="Pesos Da Carteira Ao Longo Do Tempo",
        xaxis_title="Data",
        yaxis_title="Peso",
        legend_title="Ativo",
    )
    figure.update_yaxes(tickformat=".0%")
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
    for index, column in enumerate(compounded.columns):
        figure.add_trace(
            go.Bar(
                x=compounded.index,
                y=compounded[column],
                name=str(column),
                marker={"color": CHART_COLORS[index % len(CHART_COLORS)]},
            )
        )

    period_label = "Mensais" if frequency.upper().startswith("M") else "Por Periodo"
    _apply_dark_layout(
        figure,
        title=f"Retornos {period_label}",
        xaxis_title="Data",
        yaxis_title="Retorno",
        legend_title="Serie",
        barmode="group",
    )
    figure.update_yaxes(tickformat=".0%")
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
                    "fill_color": "rgba(17, 24, 39, 0.96)",
                    "font": {"color": FONT_COLOR, "size": 12},
                    "align": "left",
                    "line_color": "rgba(125, 211, 252, 0.12)",
                },
                cells={
                    "values": table_values,
                    "fill_color": [
                        ["rgba(9, 19, 35, 0.96)"] * len(formatted_summary.index),
                        *[["rgba(13, 28, 51, 0.90)"] * len(formatted_summary.index)]
                        * len(formatted_summary.columns),
                    ],
                    "align": "left",
                    "font": {"color": FONT_COLOR, "size": 11},
                    "line_color": "rgba(125, 211, 252, 0.08)",
                },
            )
        ]
    )
    figure.update_layout(
        title="Resumo De Metricas",
        paper_bgcolor=PAPER_BG,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        font={"color": FONT_COLOR},
    )
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


def _apply_dark_layout(
    figure: go.Figure,
    *,
    title: str,
    xaxis_title: str,
    yaxis_title: str,
    legend_title: str,
    barmode: str | None = None,
) -> None:
    layout_updates = {
        "title": {"text": title, "font": {"size": 20}},
        "xaxis_title": xaxis_title,
        "yaxis_title": yaxis_title,
        "legend_title": legend_title,
        "template": "plotly_dark",
        "paper_bgcolor": PAPER_BG,
        "plot_bgcolor": PLOT_BG,
        "font": {"color": FONT_COLOR},
        "hoverlabel": {
            "bgcolor": "rgba(9, 19, 35, 0.96)",
            "bordercolor": "rgba(125, 211, 252, 0.18)",
            "font": {"color": FONT_COLOR},
        },
        "legend": {
            "orientation": "h",
            "yanchor": "top",
            "y": -0.18,
            "x": 0,
            "bgcolor": "rgba(0, 0, 0, 0)",
        },
        "margin": {"l": 24, "r": 24, "t": 64, "b": 42},
    }
    if barmode:
        layout_updates["barmode"] = barmode

    figure.update_layout(**layout_updates)
    figure.update_xaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        linecolor="rgba(125, 211, 252, 0.14)",
    )
    figure.update_yaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        linecolor="rgba(125, 211, 252, 0.14)",
    )


def _hex_to_rgba(color: str, alpha: float) -> str:
    color = color.lstrip("#")
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red}, {green}, {blue}, {alpha})"
