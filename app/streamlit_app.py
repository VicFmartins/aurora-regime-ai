"""Dashboard inicial do projeto Aurora Regime AI."""

from __future__ import annotations

import streamlit as st

from aurora.config import load_config


def main() -> None:
    """Render the initial Streamlit application shell."""
    config = load_config()

    st.set_page_config(page_title="Aurora Regime AI", layout="wide")
    st.title("Aurora Regime AI")
    st.caption("Dashboard inicial para pesquisa de regimes de mercado e alocacao adaptativa.")

    st.markdown(
        """
        Esta interface ainda esta em fase de estruturacao.
        Nesta etapa, o foco e organizar a base do projeto para:

        - ingestao e organizacao de dados;
        - engenharia de features por regime;
        - experimentos de portfolio e backtest;
        - visualizacao e analise de resultados.
        """
    )

    st.subheader("Configuracao carregada")
    st.json(config.to_dict())

    st.info(
        "A estrategia quantitativa ainda nao foi implementada. "
        "Use esta tela como ponto de partida para o dashboard."
    )


if __name__ == "__main__":
    main()
