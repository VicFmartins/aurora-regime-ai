# Prompts GenAI

## Papel Da GenAI No Aurora

A camada GenAI do Aurora Regime AI existe para apoiar comunicacao, organizacao de argumentos e revisao metodologica. Ela nao substitui o pipeline quantitativo, nao calcula a estrategia e nao decide alocacao.

Onde a GenAI foi usada:

- estruturar templates reproduziveis para relatorios;
- transformar metricas reais em prompts auditaveis;
- apoiar resumo executivo, leitura por regime, revisao de vieses e preparacao de defesa tecnica.

## O Que A GenAI Nao Faz

- nao baixa dados de mercado;
- nao roda o backtest;
- nao ajusta thresholds;
- nao escolhe pesos de carteira;
- nao gera metricas novas fora das metricas observadas;
- nao envia chamadas obrigatorias para APIs externas.

## Por Que A GenAI Nao Decide Alocacao

No Aurora, a decisao de investimento precisa permanecer:

- explicavel;
- testavel;
- reproduzivel;
- auditavel fora de um modelo generativo.

Por isso, classificacao de regime, politicas de alocacao e backtest ficam em codigo deterministico. A camada generativa so recebe os resultados para ajudar na interpretacao e na comunicacao.

## Arquivos Da Camada GenAI

- `src/aurora/genai/prompts.py`: templates fixos dos prompts.
- `src/aurora/genai/reporting.py`: funcoes puras que preenchem os templates com metricas reais ou placeholders explicitos.

## Prompts Disponiveis

1. Resumo executivo dos resultados
   Foco em comparacao com benchmarks, mensagem para publico executivo e aviso de nao recomendacao.
2. Analise por regime
   Foco em distribuicao dos regimes, sinais recentes e leitura narrativa sem alterar regras do modelo.
3. Analise de limitacoes
   Foco em fragilidades metodologicas, de dados e de implementacao.
4. Revisao de vieses
   Foco em look-ahead bias, data snooping, overfitting e riscos residuais.
5. Preparacao de defesa tecnica
   Foco em explicar o racional do projeto para banca, comite ou revisao interna.

## Placeholders Explicitos

Quando nao houver dados reais disponiveis, os prompts preservam placeholders como:

- `[INSERIR_VALOR_REAL_AQUI]`

Isso evita que a camada generativa invente numeros ou complete lacunas sem evidencia quantitativa.

## Exemplos De Uso

```python
from aurora.genai import (
    build_executive_summary_prompt,
    build_prompt_bundle,
    build_regime_analysis_prompt,
)
```

Com metricas reais:

```python
executive_prompt = build_executive_summary_prompt(
    performance_summary=performance_summary,
    metadata={
        "data_source": "synthetic",
        "start_date": "2020-01-01",
        "end_date": "2024-12-31",
        "num_assets": 5,
        "num_features": 19,
        "num_observations": 60,
    },
)
```

Com regime e sinais recentes:

```python
regime_prompt = build_regime_analysis_prompt(
    performance_summary=performance_summary,
    regimes=regimes,
    metadata={"data_source": "cache"},
)
```

Gerando todos os prompts de uma vez:

```python
prompt_bundle = build_prompt_bundle(
    performance_summary=performance_summary,
    regimes=regimes,
    metadata=metadata,
)
```

## Exemplo De Trecho Gerado

Exemplo de campos que aparecem no prompt executivo:

- retorno acumulado;
- retorno anualizado;
- volatilidade anualizada;
- sharpe ratio;
- max drawdown;
- calmar ratio;
- hit rate;
- comparacao com benchmarks.

Esses campos entram no prompt exatamente como foram observados no `performance_summary`, sem recalcule ou enriquecimento por modelo externo.

## Diretriz Metodologica

Sempre que a camada GenAI for usada no projeto, a leitura produzida deve ser tratada como apoio interpretativo. O resultado final valido para pesquisa continua sendo aquele produzido pelo pipeline quantitativo, pelas tabelas e pelos testes do repositorio.
