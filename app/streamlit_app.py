"""Premium Streamlit dashboard for the Aurora Regime AI project."""

from __future__ import annotations

from math import isnan

import pandas as pd
import streamlit as st

from app.components import (
    build_allocation_table,
    build_callout,
    build_flow_card,
    build_hero,
    build_info_card,
    build_metric_card,
    build_section_header,
    build_sidebar_brand,
    build_sidebar_nav,
    build_sidebar_status,
)
from app.styles import DASHBOARD_CSS
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
SLOGAN = "Não prevê o futuro. Reconhece o regime."
MODE_OFFLINE = "Offline com exemplo ou dados sintéticos"
MODE_ONLINE = "Online com cache e fallback offline"
REGIME_LABELS = {
    MarketRegime.TENDENCIA_POSITIVA: "Tendência positiva",
    MarketRegime.ESTRESSE: "Estresse",
    MarketRegime.LATERALIZACAO: "Lateralização",
    MarketRegime.RECUPERACAO: "Recuperação",
}
REGIME_SUMMARIES = {
    MarketRegime.TENDENCIA_POSITIVA: (
        "Momentum de médio e longo prazo acima de zero com volatilidade controlada."
    ),
    MarketRegime.ESTRESSE: (
        "Drawdown relevante ou volatilidade acima do limite metodológico do modelo."
    ),
    MarketRegime.LATERALIZACAO: (
        "Ambiente sem direcionalidade dominante, com sinais mistos e alocação equilibrada."
    ),
    MarketRegime.RECUPERACAO: (
        "Drawdown ainda negativo, mas com retomada de momentum curto e melhora de z-score."
    ),
}
CARD_TONES = ["tone-blue", "tone-teal", "tone-orange", "tone-violet", "tone-rose", "tone-green"]


def main() -> None:
    """Render the Aurora dashboard."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon="A",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _apply_theme()

    execution_mode, force_download = _render_sidebar_controls()

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

    _render_sidebar_context(result=result, execution_mode=execution_mode)
    _render_hero(result=result)
    _render_metric_overview(
        config=config,
        result=result,
        strategy_metrics=strategy_metrics,
        latest_regime=latest_regime,
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
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)


def _render_sidebar_controls() -> tuple[str, bool]:
    with st.sidebar:
        st.markdown(
            build_sidebar_brand(
                title="Aurora",
                subtitle="Pesquisa quantitativa adaptativa para regimes de mercado.",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("### Controles do pipeline")
        st.caption(
            "Escolha a fonte de dados e atualize a execução quando quiser revisar os artefatos."
        )
        execution_mode = st.radio(
            "Fonte de dados",
            options=[MODE_OFFLINE, MODE_ONLINE],
            index=0,
        )
        force_download = st.checkbox(
            "Forçar novo download online",
            value=False,
            disabled=execution_mode == MODE_OFFLINE,
            help="Ignora o cache local quando o modo online estiver ativo.",
        )
        if st.button("Atualizar pipeline", use_container_width=True):
            st.cache_resource.clear()

    return execution_mode, force_download


def _render_sidebar_context(
    *,
    result: PipelineResult,
    execution_mode: str,
) -> None:
    with st.sidebar:
        st.markdown(
            build_sidebar_status(
                execution_mode="Offline" if execution_mode == MODE_OFFLINE else "Online",
                data_source=_format_source(result.data_source),
                date_window=(
                    f"{result.prices.index.min().date()} → {result.prices.index.max().date()}"
                ),
                note=result.metadata.get("data_notes"),
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            build_sidebar_nav(
                [
                    "Hipótese de pesquisa",
                    "Universo de ativos",
                    "Indicadores usados",
                    "Regimes de mercado",
                    "Alocação por regime",
                    "Backtest",
                    "Métricas principais",
                    "Uso de GenAI",
                    "Limitações e vieses",
                    "Disclaimer",
                ]
            ),
            unsafe_allow_html=True,
        )


def _render_hero(*, result: PipelineResult) -> None:
    st.markdown(
        build_hero(
            title=PAGE_TITLE,
            slogan=SLOGAN,
            description=(
                "Robô quantitativo adaptativo para alocação por regime de mercado. "
                "O dashboard conecta narrativa metodológica, pipeline de pesquisa, "
                "backtest auditável e visualizações para auditoria do racional."
            ),
            badges=[
                "Python 3.11+",
                "Regime switching",
                "Backtest auditável",
                "Fallback offline",
                f"Fonte: {_format_source(result.data_source)}",
            ],
        ),
        unsafe_allow_html=True,
    )

    if result.metadata.get("data_notes"):
        st.markdown(
            build_callout(result.metadata["data_notes"], variant="warning"),
            unsafe_allow_html=True,
        )


def _render_metric_overview(
    *,
    config,
    result: PipelineResult,
    strategy_metrics: pd.Series,
    latest_regime: str,
) -> None:
    metric_specs = [
        (
            "Capital inicial",
            _format_currency(config.initial_capital),
            "Capital base configurado para o backtest.",
            "tone-blue",
        ),
        (
            "Retorno acumulado",
            _format_metric(strategy_metrics["cumulative_return"], pct=True),
            "Resultado total da estratégia no horizonte analisado.",
            "tone-teal",
        ),
        (
            "Retorno anualizado",
            _format_metric(strategy_metrics["annualized_return"], pct=True),
            "Taxa composta anual equivalente da série mensal.",
            "tone-teal",
        ),
        (
            "Volatilidade",
            _format_metric(strategy_metrics["annualized_volatility"], pct=True),
            "Volatilidade anualizada da estratégia.",
            "tone-orange",
        ),
        (
            "Max drawdown",
            _format_metric(strategy_metrics["max_drawdown"], pct=True),
            "Pior retração histórica acumulada.",
            "tone-rose",
        ),
        (
            "Regime atual",
            _format_regime_label(latest_regime),
            "Classificação mais recente segundo o classificador explicável.",
            "tone-violet",
        ),
    ]

    columns = st.columns(len(metric_specs))
    for column, (label, value, detail, tone) in zip(columns, metric_specs, strict=True):
        column.markdown(
            build_metric_card(label=label, value=value, detail=detail, tone=tone),
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="aurora-caption">Observações processadas: {len(result.prices):,}'.replace(
            ",", "."
        )
        + " • Rebalanceamentos: "
        + str(int(result.backtest.metadata["num_rebalances"]))
        + "</div>",
        unsafe_allow_html=True,
    )


def _render_project_hypothesis() -> None:
    st.markdown(
        build_section_header(
            "Hipótese de pesquisa",
            (
                "A hipótese central do Aurora é que uma carteira adaptativa, guiada por "
                "detecção de regime, pode melhorar a relação risco-retorno frente a "
                "alocações estáticas coerentes."
            ),
            eyebrow="Research Thesis",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        build_callout(
            (
                "O modelo vê o mercado como um ambiente dinâmico, observando momentum, "
                "volatilidade, drawdown, z-score e correlação para ajustar a exposição "
                "de forma explicável, sem antecipar informação futura."
            ),
            variant="disclaimer",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        build_flow_card(
            [
                ("Data Ingestion", "Cache, yfinance e CSV manual"),
                ("Feature Engineering", "Sinais defasados para decisão"),
                ("Regime Detection", "Regras fixas e explicáveis"),
                ("Weight Allocation", "Políticas long-only a priori"),
                ("Backtesting Engine", "Execução mensal auditável"),
            ]
        ),
        unsafe_allow_html=True,
    )


def _render_universe(config) -> None:
    st.markdown(
        build_section_header(
            "Universo de ativos",
            (
                "Ativos iniciais escolhidos para representar risco local, "
                "exposição global, proteção, inflação e caixa defensivo."
            ),
            eyebrow="Asset Universe",
        ),
        unsafe_allow_html=True,
    )

    columns = st.columns(3)
    for index, (ticker, description) in enumerate(config.assets.items()):
        columns[index % 3].markdown(
            build_info_card(
                title=ticker,
                body=description.replace("proxy", "proxy defensivo"),
                eyebrow="Ativo base",
                tone=CARD_TONES[index % len(CARD_TONES)],
                footer=f"Peso base: {_format_pct(config.asset_weights[ticker])}",
            ),
            unsafe_allow_html=True,
        )


def _render_indicators(config) -> None:
    st.markdown(
        build_section_header(
            "Indicadores usados",
            (
                "Os sinais abaixo estruturam a leitura de ambiente de mercado "
                "sem recorrer a otimização retroativa de thresholds."
            ),
            eyebrow="Signals",
        ),
        unsafe_allow_html=True,
    )
    indicators = [
        (
            "Momentum",
            (
                "Retorno acumulado nas janelas de 63, 126 e 252 períodos "
                "para detectar persistência de tendência."
            ),
        ),
        (
            "Volatilidade",
            (
                "Dispersão anualizada dos retornos em janela móvel de "
                f"{config.volatility_window} períodos."
            ),
        ),
        (
            "Drawdown",
            f"Queda relativa ao pico recente na janela de {config.drawdown_window} períodos.",
        ),
        (
            "Z-score",
            f"Padronização dos retornos em {config.zscore_window} períodos para medir anomalias.",
        ),
        (
            "Correlação",
            (
                f"Correlação móvel em {config.correlation_window} períodos "
                "para monitorar contágio e perda de diversificação."
            ),
        ),
    ]
    columns = st.columns(3)
    for index, (title, description) in enumerate(indicators):
        columns[index % 3].markdown(
            build_info_card(
                title=title,
                body=description,
                tone=CARD_TONES[index % len(CARD_TONES)],
            ),
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="aurora-caption">'
        "Todas as features de decisão são defasadas em 1 período para evitar look-ahead bias."
        "</div>",
        unsafe_allow_html=True,
    )


def _render_regimes(config) -> None:
    st.markdown(
        build_section_header(
            "Regimes de mercado",
            (
                "O classificador combina thresholds ex ante com sinais econômicos "
                "simples para diferenciar tendência, estresse, lateralização e recuperação."
            ),
            eyebrow="Market States",
        ),
        unsafe_allow_html=True,
    )
    signal_summary = (
        f"Stress se drawdown ≤ {config.stress_drawdown_threshold:.0%}, volatilidade > "
        f"{config.high_volatility_threshold:.0%}, momentum positivo acima de "
        f"{config.positive_momentum_threshold:.0%} e recuperação com melhora de z-score."
    )
    st.markdown(build_callout(signal_summary, variant="disclaimer"), unsafe_allow_html=True)

    columns = st.columns(4)
    for index, regime in enumerate(MarketRegime):
        columns[index].markdown(
            build_info_card(
                title=REGIME_LABELS[regime],
                body=REGIME_SUMMARIES[regime],
                tone=CARD_TONES[index % len(CARD_TONES)],
            ),
            unsafe_allow_html=True,
        )


def _render_allocations(config) -> None:
    st.markdown(
        build_section_header(
            "Alocação por regime",
            (
                "Os pesos são definidos a priori para reduzir overfitting "
                "e manter justificativa econômica transparente."
            ),
            eyebrow="Portfolio Policy",
        ),
        unsafe_allow_html=True,
    )

    allocation_rows: list[dict[str, str]] = []
    rationales = []
    for regime in MarketRegime:
        policy = get_weights_for_regime(regime, config)
        row = {"Regime": REGIME_LABELS[regime]}
        for asset, weight in policy.weights.items():
            row[asset] = _format_pct(weight)
        allocation_rows.append(row)
        rationales.append((REGIME_LABELS[regime], policy.rationale))

    allocation_frame = pd.DataFrame(allocation_rows)
    st.markdown(build_allocation_table(allocation_frame), unsafe_allow_html=True)

    columns = st.columns(2)
    for index, (title, rationale) in enumerate(rationales):
        columns[index % 2].markdown(
            build_info_card(
                title=title,
                body=rationale,
                tone=CARD_TONES[index % len(CARD_TONES)],
            ),
            unsafe_allow_html=True,
        )


def _render_backtest(result: PipelineResult) -> None:
    st.markdown(
        build_section_header(
            "Backtest",
            (
                "Comparação histórica entre a estratégia e benchmarks, "
                "preservando a barreira temporal entre sinal e execução."
            ),
            eyebrow="Execution Review",
        ),
        unsafe_allow_html=True,
    )
    returns_frame = pd.concat(
        [result.backtest.portfolio_returns.rename("strategy"), result.benchmark_returns],
        axis=1,
    )
    strategy_equity = result.backtest.equity_curve.rename("strategy")

    tab_overview, tab_allocation, tab_regimes = st.tabs(
        ["Curvas e risco", "Pesos e retornos", "Regimes e rebalanceamentos"]
    )

    with tab_overview:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                plot_equity_curves(strategy_equity, result.benchmark_equity_curves),
                use_container_width=True,
            )
        with col2:
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
    st.markdown(
        build_section_header(
            "Métricas principais",
            (
                "Leitura consolidada da performance da estratégia e de "
                "benchmarks coerentes, sem prometer retorno futuro."
            ),
            eyebrow="Performance Summary",
        ),
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.45, 0.85])
    with left:
        st.plotly_chart(
            plot_performance_table(result.performance_summary),
            use_container_width=True,
        )
    with right:
        st.markdown(
            build_metric_card(
                label="Sharpe ratio",
                value=_format_metric(strategy_metrics["sharpe_ratio"]),
                detail="Eficiência risco-retorno anualizada.",
                tone="tone-orange",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            build_metric_card(
                label="Hit rate",
                value=_format_metric(strategy_metrics["hit_rate"], pct=True),
                detail="Participação de meses positivos na estratégia.",
                tone="tone-green",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            build_metric_card(
                label="Rebalanceamentos",
                value=_format_int(strategy_metrics["num_rebalances"]),
                detail="Número de trocas registradas pelo motor mensal.",
                tone="tone-blue",
            ),
            unsafe_allow_html=True,
        )

    with st.expander("Tabela completa de métricas", expanded=False):
        st.dataframe(result.performance_summary.round(4), use_container_width=True)


def _render_genai() -> None:
    st.markdown(
        build_section_header(
            "Uso de GenAI",
            (
                "A camada generativa apoia comunicação técnica e revisão "
                "metodológica, sem decidir investimento ou substituir o motor quantitativo."
            ),
            eyebrow="Generative Layer",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        build_callout(
            (
                "GenAI auxilia na explicabilidade dos resultados, preparação de defesa "
                "técnica e identificação de pontos cegos. A decisão de regime, pesos e "
                "execução permanece determinística, auditável e testável fora do modelo generativo."
            ),
            variant="genai",
        ),
        unsafe_allow_html=True,
    )

    columns = st.columns(3)
    cards = [
        (
            "Resumo executivo",
            (
                "Transforma métricas e gráficos em narrativa acessível "
                "para banca, relatório e stakeholders."
            ),
        ),
        (
            "Revisão de vieses",
            (
                "Ajuda a organizar perguntas críticas sobre look-ahead bias, "
                "overfitting e robustez fora da amostra."
            ),
        ),
        (
            "Limite operacional",
            "Não escolhe ativos, não gera pesos e não substitui validação estatística do projeto.",
        ),
    ]
    for index, (title, body) in enumerate(cards):
        columns[index].markdown(
            build_info_card(title=title, body=body, tone=CARD_TONES[index % len(CARD_TONES)]),
            unsafe_allow_html=True,
        )


def _render_limitations() -> None:
    st.markdown(
        build_section_header(
            "Limitações e vieses",
            (
                "O projeto foi desenhado para ser honesto sobre simplificações, "
                "riscos metodológicos e fronteiras de uso."
            ),
            eyebrow="Risk Notes",
        ),
        unsafe_allow_html=True,
    )
    points = [
        (
            "Look-ahead bias é mitigado com shift das features "
            "e aplicação do peso apenas no período seguinte."
        ),
        (
            "As regras de regime ainda são simples, fixas e não "
            "incorporam slippage, impostos ou microestrutura."
        ),
        (
            "A robustez fora da amostra ainda depende de expansão "
            "do universo, mais benchmarks e testes adicionais."
        ),
        (
            "Mudanças estruturais de mercado podem degradar sinais "
            "historicamente úteis, inclusive em séries sintéticas."
        ),
    ]
    columns = st.columns(2)
    for index, point in enumerate(points):
        columns[index % 2].markdown(
            build_info_card(
                title=f"Ponto crítico {index + 1}",
                body=point,
                tone=CARD_TONES[index % len(CARD_TONES)],
            ),
            unsafe_allow_html=True,
        )


def _render_footer() -> None:
    st.markdown(
        build_section_header(
            "Disclaimer",
            (
                "Uso educacional e de pesquisa, sem constituir oferta, "
                "recomendação ou promessa de retorno."
            ),
            eyebrow="Legal Notice",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        build_callout(
            (
                "Este dashboard tem finalidade educacional e de pesquisa. Ele não constitui "
                "recomendação de investimento, oferta de ativos, promessa de retorno ou "
                "aconselhamento financeiro. Resultados históricos, inclusive em modo offline, "
                "não garantem desempenho futuro."
            ),
            variant="disclaimer",
        ),
        unsafe_allow_html=True,
    )


def _format_source(source: str) -> str:
    labels = {
        "cache": "Cache local",
        "example_csv": "CSV de exemplo",
        "manual_or_hybrid": "Manual/híbrido",
        "synthetic": "Sintético",
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


def _format_currency(value: float) -> str:
    integer_value = int(round(value))
    return f"${integer_value:,.0f}"


def _format_int(value: float) -> str:
    if pd.isna(value):
        return "-"
    return str(int(round(float(value))))


if __name__ == "__main__":
    main()
