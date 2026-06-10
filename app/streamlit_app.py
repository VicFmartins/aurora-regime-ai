"""Streamlit dashboard for the Aurora Regime AI project."""

from __future__ import annotations

from math import isnan

import pandas as pd
import streamlit as st

from aurora import load_config, run_full_pipeline, run_offline_pipeline
from aurora.pipeline import PipelineResult
from aurora.portfolio import get_weights_for_regime
from aurora.regime import MarketRegime
from aurora.visualization import (
    plot_drawdown,
    plot_equity_curves,
    plot_performance_table,
    plot_period_returns,
    plot_regimes,
    plot_weights,
)

PAGE_TITLE = "Aurora Regime AI"
SLOGAN = "Nao preve o futuro. Reconhece o regime."
MODE_OFFLINE = "Offline com exemplo ou dados sinteticos"
MODE_ONLINE = "Online com cache e fallback offline"
REGIME_LABELS = {
    MarketRegime.TENDENCIA_POSITIVA: "Tendencia positiva",
    MarketRegime.ESTRESSE: "Estresse",
    MarketRegime.LATERALIZACAO: "Lateralizacao",
    MarketRegime.RECUPERACAO: "Recuperacao",
}
REGIME_SUMMARIES = {
    MarketRegime.TENDENCIA_POSITIVA: (
        "Momentum de medio e longo prazo acima de zero com volatilidade controlada."
    ),
    MarketRegime.ESTRESSE: (
        "Drawdown relevante ou volatilidade acima do limite metodologico do modelo."
    ),
    MarketRegime.LATERALIZACAO: (
        "Ambiente sem direcionalidade dominante, com sinais mistos e alocacao equilibrada."
    ),
    MarketRegime.RECUPERACAO: (
        "Drawdown ainda negativo, mas com retomada de momentum curto e melhora de z-score."
    ),
}


def main() -> None:
    """Render the Aurora dashboard."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="A",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _apply_theme()

    st.sidebar.markdown("## Aurora Console")
    st.sidebar.caption("Escolha o modo de execucao do pipeline e atualize os resultados.")
    execution_mode = st.sidebar.radio(
        "Fonte de dados",
        options=[MODE_OFFLINE, MODE_ONLINE],
        index=0,
    )
    force_download = st.sidebar.checkbox(
        "Forcar novo download online",
        value=False,
        disabled=execution_mode == MODE_OFFLINE,
        help="Ignora o cache local quando o modo online estiver ativo.",
    )
    if st.sidebar.button("Atualizar pipeline", use_container_width=True):
        st.cache_resource.clear()

    try:
        result = _load_dashboard_result(
            execution_mode=execution_mode,
            force_download=force_download,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        st.error(f"Erro ao carregar o dashboard: {exc}")
        st.stop()

    config = result.config
    strategy_metrics = result.performance_summary.loc["strategy"]
    latest_regime = result.regimes["regime"].dropna().iloc[-1]

    _render_hero(
        result=result,
        latest_regime=latest_regime,
        execution_mode=execution_mode,
    )
    _render_project_hypothesis()
    _render_universe(config)
    _render_indicators(config)
    _render_regimes(config)
    _render_allocations(config)
    _render_backtest(result)
    _render_metrics(result, strategy_metrics)
    _render_genai()
    _render_limitations()
    _render_footer()


@st.cache_resource(show_spinner="Executando pipeline do Aurora...")
def _load_dashboard_result(
    *,
    execution_mode: str,
    force_download: bool,
) -> PipelineResult:
    config = load_config()
    if execution_mode == MODE_OFFLINE:
        return run_offline_pipeline(config)
    return run_full_pipeline(config, force_download=force_download)


def _apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --aurora-ink: #132a36;
            --aurora-deep: #0b3c49;
            --aurora-teal: #1f7a8c;
            --aurora-sand: #f2e8cf;
            --aurora-cream: #f8f5ee;
            --aurora-copper: #d17b49;
            --aurora-red: #b94e48;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(31, 122, 140, 0.18), transparent 30%),
                radial-gradient(circle at top right, rgba(209, 123, 73, 0.16), transparent 35%),
                linear-gradient(180deg, #f6f2e8 0%, #fbfaf7 32%, #ffffff 100%);
            color: var(--aurora-ink);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #102a43 0%, #163d4f 100%);
        }

        [data-testid="stSidebar"] * {
            color: #f9f7f2;
        }

        .hero-panel {
            padding: 1.8rem 1.8rem 1.4rem;
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(11, 60, 73, 0.95), rgba(31, 122, 140, 0.88));
            color: #fdfcf9;
            box-shadow: 0 20px 45px rgba(16, 42, 67, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: 3rem;
            line-height: 1.05;
            margin: 0 0 0.35rem;
            font-family: Georgia, "Avenir Next", serif;
            letter-spacing: -0.03em;
        }

        .hero-slogan {
            font-size: 1.1rem;
            margin: 0 0 1rem;
            color: rgba(255, 248, 240, 0.92);
        }

        .hero-body {
            font-size: 1rem;
            max-width: 58rem;
            color: rgba(255, 248, 240, 0.92);
        }

        .section-card {
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid rgba(19, 42, 54, 0.08);
            box-shadow: 0 12px 24px rgba(19, 42, 54, 0.06);
            margin-bottom: 0.9rem;
        }

        .mini-card {
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: rgba(248, 245, 238, 0.95);
            border-left: 4px solid var(--aurora-copper);
            min-height: 10.5rem;
        }

        .mini-card h4 {
            margin: 0 0 0.45rem;
            font-size: 1rem;
            color: var(--aurora-deep);
        }

        .mini-card p {
            margin: 0;
            color: #314c57;
            font-size: 0.95rem;
        }

        .signal-chip {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(242, 232, 207, 0.85);
            color: var(--aurora-deep);
            font-size: 0.88rem;
            margin-right: 0.45rem;
            margin-bottom: 0.45rem;
            border: 1px solid rgba(19, 42, 54, 0.08);
        }

        .footer-note {
            padding: 1.2rem 1.4rem;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(185, 78, 72, 0.12), rgba(209, 123, 73, 0.10));
            border: 1px solid rgba(185, 78, 72, 0.18);
            color: #5b2a27;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_hero(
    *,
    result: PipelineResult,
    latest_regime: str,
    execution_mode: str,
) -> None:
    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-title">{PAGE_TITLE}</div>
            <div class="hero-slogan">{SLOGAN}</div>
            <div class="hero-body">
                Robo quantitativo adaptativo para alocacao por regime de mercado.
                O dashboard conecta narrativa metodologica, pipeline de pesquisa,
                backtest reproduzivel e visualizacoes para auditoria do racional.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fonte usada", _format_source(result.data_source))
    col2.metric("Ultimo regime", _format_regime_label(latest_regime))
    col3.metric("Observacoes", f"{len(result.prices):,}".replace(",", "."))
    col4.metric("Modo escolhido", "Offline" if execution_mode == MODE_OFFLINE else "Online")

    if result.metadata.get("data_notes"):
        st.info(result.metadata["data_notes"])


def _render_project_hypothesis() -> None:
    st.markdown("## Hipotese de pesquisa")
    st.markdown(
        """
        <div class="section-card">
        A hipotese central do Aurora e que uma carteira adaptativa, guiada por sinais
        de regime, pode melhorar a relacao risco-retorno frente a alocacoes estaticas.
        Em vez de tratar o mercado como um unico ambiente, o modelo observa mudancas
        de momentum, volatilidade, drawdown, z-score e correlacao para ajustar a
        exposicao de forma explicavel.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_universe(config) -> None:
    st.markdown("## Universo de ativos")
    assets_frame = pd.DataFrame(
        {
            "Ticker": list(config.assets.keys()),
            "Papel no portfolio": list(config.assets.values()),
            "Peso base": [config.asset_weights[ticker] for ticker in config.assets],
        }
    )
    assets_frame["Peso base"] = assets_frame["Peso base"].map(_format_pct)
    st.dataframe(assets_frame, use_container_width=True, hide_index=True)


def _render_indicators(config) -> None:
    st.markdown("## Indicadores usados")
    indicators = [
        (
            "Momentum",
            "Retorno acumulado em janelas de 63, 126 e 252 periodos para detectar "
            "persistencia de tendencia.",
        ),
        (
            "Volatilidade",
            "Dispersion anualizada dos retornos em janela movel de "
            f"{config.volatility_window} periodos.",
        ),
        (
            "Drawdown",
            f"Queda relativa ao pico recente na janela de {config.drawdown_window} periodos.",
        ),
        (
            "Z-score",
            f"Padronizacao dos retornos em {config.zscore_window} periodos para medir anomalias.",
        ),
        (
            "Correlacao",
            f"Correlacao movel em {config.correlation_window} periodos para enxergar "
            "contagio e perda de diversificacao.",
        ),
    ]

    columns = st.columns(len(indicators))
    for column, (title, description) in zip(columns, indicators, strict=True):
        column.markdown(
            f"""
            <div class="mini-card">
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "Todas as features de decisao sao defasadas em 1 periodo para evitar look-ahead bias."
    )


def _render_regimes(config) -> None:
    st.markdown("## Regimes de mercado")
    signal_chips = [
        f"drawdown <= {config.stress_drawdown_threshold:.0%}",
        f"volatilidade > {config.high_volatility_threshold:.0%}",
        f"momentum positivo acima de {config.positive_momentum_threshold:.0%}",
        "z-score em melhora",
    ]
    st.markdown(
        "".join(f'<span class="signal-chip">{chip}</span>' for chip in signal_chips),
        unsafe_allow_html=True,
    )

    regime_columns = st.columns(4)
    for column, regime in zip(regime_columns, MarketRegime, strict=True):
        column.markdown(
            f"""
            <div class="mini-card">
                <h4>{REGIME_LABELS[regime]}</h4>
                <p>{REGIME_SUMMARIES[regime]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_allocations(config) -> None:
    st.markdown("## Alocacao por regime")
    allocation_rows: list[dict[str, str]] = []
    rationales = []

    for regime in MarketRegime:
        policy = get_weights_for_regime(regime, config)
        row = {"Regime": REGIME_LABELS[regime]}
        for asset, weight in policy.weights.items():
            row[asset] = _format_pct(weight)
        allocation_rows.append(row)
        rationales.append((REGIME_LABELS[regime], policy.rationale))

    st.dataframe(pd.DataFrame(allocation_rows), use_container_width=True, hide_index=True)

    for title, rationale in rationales:
        st.markdown(
            f"""
            <div class="section-card">
                <strong>{title}.</strong> {rationale}
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_backtest(result: PipelineResult) -> None:
    st.markdown("## Backtest")
    returns_frame = pd.concat(
        [result.backtest.portfolio_returns.rename("strategy"), result.benchmark_returns],
        axis=1,
    )
    strategy_equity = result.backtest.equity_curve.rename("strategy")

    tab_overview, tab_allocation, tab_regimes = st.tabs(
        ["Panorama", "Pesos e retornos", "Regimes e detalhes"]
    )

    with tab_overview:
        st.plotly_chart(
            plot_equity_curves(strategy_equity, result.benchmark_equity_curves),
            use_container_width=True,
        )
        st.plotly_chart(plot_drawdown(returns_frame), use_container_width=True)

    with tab_allocation:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(plot_weights(result.backtest.weights_history), use_container_width=True)
        with col2:
            st.plotly_chart(
                plot_period_returns(returns_frame, frequency="M"),
                use_container_width=True,
            )

    with tab_regimes:
        st.plotly_chart(plot_regimes(result.regimes), use_container_width=True)
        st.dataframe(
            result.backtest.rebalance_log[["signal_date", "rebalance_date", "turnover"]],
            use_container_width=True,
            hide_index=True,
        )


def _render_metrics(result: PipelineResult, strategy_metrics: pd.Series) -> None:
    st.markdown("## Metricas principais")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(
        "Retorno anualizado",
        _format_metric(strategy_metrics["annualized_return"], pct=True),
    )
    col2.metric(
        "Volatilidade anualizada",
        _format_metric(strategy_metrics["annualized_volatility"], pct=True),
    )
    col3.metric("Sharpe", _format_metric(strategy_metrics["sharpe_ratio"]))
    col4.metric("Max drawdown", _format_metric(strategy_metrics["max_drawdown"], pct=True))
    col5.metric("Turnover medio", _format_metric(strategy_metrics["average_turnover"], pct=True))

    left, right = st.columns([1.2, 1.0])
    with left:
        st.plotly_chart(
            plot_performance_table(result.performance_summary),
            use_container_width=True,
        )
    with right:
        display_summary = result.performance_summary.copy()
        st.dataframe(display_summary, use_container_width=True)


def _render_genai() -> None:
    st.markdown("## Uso de GenAI")
    st.markdown(
        """
        <div class="section-card">
        No Aurora, GenAI tem papel complementar. Ela pode apoiar sumarizacao de pesquisas,
        explicacao de resultados, organizacao de hipoteses e redacao de documentacao.
        O motor de decisao quantitativa, porem, permanece auditavel, parametrizado e
        testavel fora do modelo generativo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    genai_points = st.columns(3)
    genai_points[0].markdown(
        """
        <div class="mini-card">
            <h4>Pesquisa assistida</h4>
            <p>
                Consolidacao de referencias, hipoteses e perguntas metodologicas
                para aprofundar o estudo.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    genai_points[1].markdown(
        """
        <div class="mini-card">
            <h4>Explicacao executiva</h4>
            <p>
                Traducao de tabelas e graficos para narrativa acessivel sem mexer
                nas regras do modelo.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    genai_points[2].markdown(
        """
        <div class="mini-card">
            <h4>Limite operacional</h4>
            <p>
                Nenhuma resposta generativa substitui validacao estatistica,
                controle de vieses ou auditoria de codigo.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_limitations() -> None:
    st.markdown("## Limitacoes e vieses")
    points = [
        "Look-ahead bias e mitigado com shift das features e aplicacao do peso "
        "apenas no periodo seguinte.",
        "Regras de regime ainda sao simples e fixas, sem slippage, impostos ou "
        "restricoes de liquidez.",
        "A robustez fora da amostra ainda depende de expansao de dados, "
        "benchmarks e testes adicionais.",
        "Mudancas estruturais de mercado podem degradar sinais historicamente uteis.",
    ]
    columns = st.columns(2)
    for index, point in enumerate(points):
        columns[index % 2].markdown(
            f"""
            <div class="section-card">
                {point}
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_footer() -> None:
    st.markdown("## Disclaimer")
    st.markdown(
        """
        <div class="footer-note">
        Este dashboard tem finalidade educacional e de pesquisa. Ele nao constitui
        recomendacao de investimento, oferta de ativos, promessa de retorno ou
        aconselhamento financeiro. Resultados historicos, inclusive em modo offline,
        nao garantem desempenho futuro.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_source(source: str) -> str:
    labels = {
        "cache": "Cache local",
        "example_csv": "CSV exemplo",
        "manual_or_hybrid": "Manual/hibrido",
        "synthetic": "Sintetico",
        "yfinance": "Online",
    }
    return labels.get(source, source)


def _format_regime_label(regime: str) -> str:
    try:
        return REGIME_LABELS[MarketRegime(regime)]
    except ValueError:
        return regime


def _format_pct(value: float) -> str:
    return f"{value:.0%}"


def _format_metric(value: float, *, pct: bool = False) -> str:
    if pd.isna(value):
        return "-"

    numeric_value = float(value)
    if isnan(numeric_value):
        return "-"
    if pct:
        return f"{numeric_value:.2%}"
    return f"{numeric_value:.2f}"


if __name__ == "__main__":
    main()
