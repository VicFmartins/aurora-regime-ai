# Relatorio Tecnico

## Projeto

**Aurora Regime AI**

Slogan: `Nao preve o futuro. Reconhece o regime.`

## 1. Resumo Executivo

O Aurora Regime AI e um projeto de pesquisa quantitativa para alocacao adaptativa de portfolio com base em regimes de mercado. A proposta central e identificar mudancas de contexto por meio de sinais objetivos, como momentum, volatilidade, drawdown, z-score e correlacao, e converter esses sinais em politicas de alocacao previamente definidas.

Nesta versao, o projeto entrega:

- arquitetura reprodutivel de dados, features, regime, portfolio, backtest, benchmarks, analise, visualizacao e dashboard;
- regras explicaveis de classificacao de regime;
- motor de backtest com barreira temporal para evitar look-ahead bias;
- camada GenAI para apoio a documentacao e comunicacao, sem delegar decisoes de investimento.

Resultado executivo atual:

- retorno acumulado da estrategia: `[INSERIR_METRICA_REAL_DO_ULTIMO_BACKTEST]`
- retorno anualizado da estrategia: `[INSERIR_METRICA_REAL_DO_ULTIMO_BACKTEST]`
- volatilidade anualizada da estrategia: `[INSERIR_METRICA_REAL_DO_ULTIMO_BACKTEST]`
- sharpe ratio da estrategia: `[INSERIR_METRICA_REAL_DO_ULTIMO_BACKTEST]`
- maximo drawdown da estrategia: `[INSERIR_METRICA_REAL_DO_ULTIMO_BACKTEST]`
- benchmark principal comparado: `[INSERIR_BENCHMARK_REAL_COMPARADO]`

Observacao importante:

- preencher esta secao somente com dados provenientes do pipeline validado, preferencialmente a partir de `reports/tables/performance_summary.csv`;
- nao utilizar resultados demonstrativos de modo offline como conclusao de investimento.

## 2. Problema

Modelos estaticos de alocacao assumem, implicitamente, que o mercado opera sob uma dinamica relativamente estavel. Na pratica, o ambiente financeiro alterna entre contextos de expansao, estresse, lateralizacao e recuperacao. Uma carteira unica e fixa pode se mostrar inadequada quando:

- a volatilidade sobe abruptamente;
- a correlacao entre ativos aumenta e reduz a diversificacao efetiva;
- o risco direcional se torna assimetrico;
- sinais de retomada aparecem antes de uma reversao estrutural completa.

O problema de pesquisa do Aurora e verificar se uma camada de regime explicavel pode melhorar a adaptacao de portfolio frente a essas mudancas de contexto, mantendo controle metodologico e auditabilidade.

## 3. Hipotese

A hipotese central do projeto e:

> Uma politica de alocacao adaptativa por regime, baseada em regras simples e definidas ex ante, pode melhorar a relacao risco-retorno em comparacao com referencias estaticas coerentes, sem depender de previsao pontual de mercado.

Essa hipotese nao implica promessa de retorno. Ela apenas orienta a investigacao quantitativa e a comparacao entre estrategia e benchmarks.

## 4. Dados Utilizados

### 4.1 Universo inicial

- `BOVA11.SA`: renda variavel Brasil
- `IVVB11.SA`: exposicao internacional
- `IMAB11.SA`: renda fixa inflacao
- `USDBRL=X`: protecao cambial
- `CDI`: caixa defensivo ou proxy de liquidez

### 4.2 Fonte de dados

Fonte principal prevista:

- `yfinance`, com prioridade para `Adj Close` e fallback para `Close` quando necessario.

Rotas auxiliares:

- cache local em `data/cache/prices.parquet`;
- CSV manual em `data/raw/prices.csv`;
- CSV de exemplo ou dados sinteticos para execucao offline do pipeline e do dashboard.

### 4.3 Janela da analise

- inicio padrao: `2015-01-01`
- fim padrao: `2024-12-31`
- frequencia de decisao: mensal

Janela efetivamente usada no resultado final:

- `[INSERIR_INTERVALO_REAL_UTILIZADO_NO_BACKTEST_FINAL]`

### 4.4 Cuidados metodologicos com dados

- validacao de `DatetimeIndex`;
- ordenacao temporal obrigatoria;
- controle de duplicatas;
- minimo de observacoes por ativo;
- controle de percentual de nulos por serie.

## 5. Indicadores

O Aurora transforma precos em sinais quantitativos usados para classificacao de regime.

### 5.1 Momentum

Momentum em janelas de `63`, `126` e `252` periodos mede persistencia de retorno e ajuda a distinguir:

- tendencia positiva;
- perda de forca;
- recuperacao apos queda.

### 5.2 Volatilidade

Volatilidade movel em janela de `21` periodos, anualizada, ajuda a identificar:

- estresse de mercado;
- instabilidade de precos;
- aumento de incerteza.

### 5.3 Drawdown

Drawdown em janela de `252` periodos mede a distancia em relacao ao pico recente e ajuda a capturar:

- deterioracao acumulada;
- profundidade de perda;
- fragilidade estrutural de tendencia.

### 5.4 Z-Score

Z-score em janela de `252` periodos padroniza os retornos e ajuda a observar:

- desvios anormais;
- compressao ou esticamento de movimento;
- melhora ou piora relativa do sinal.

### 5.5 Correlacao

Correlacao movel em `60` periodos ajuda a avaliar:

- contagio entre ativos;
- perda de diversificacao;
- sincronizacao de estresse em mercado.

## 6. Classificacao De Regimes

O classificador inicial do Aurora usa quatro estados:

- `TENDENCIA_POSITIVA`
- `ESTRESSE`
- `LATERALIZACAO`
- `RECUPERACAO`

### 6.1 Arvore de decisao

1. `ESTRESSE`
   Se `drawdown <= -15%` ou se a volatilidade anualizada superar `30%`.
2. `TENDENCIA_POSITIVA`
   Se `momentum_126 > 0`, `momentum_252 > 0` e volatilidade permanecer controlada.
3. `RECUPERACAO`
   Se o drawdown ainda for negativo, mas `momentum_63 > 0` e o z-score estiver melhorando.
4. `LATERALIZACAO`
   Caso residual quando os demais gatilhos nao forem ativados.

### 6.2 Principio metodologico

Os thresholds sao definidos ex ante e nao ajustados olhando o desempenho final do backtest. Isso reduz risco de otimizacao retroativa e preserva interpretabilidade.

## 7. Politica De Alocacao

As politicas de peso sao long-only e foram definidas a priori para mitigar overfitting.

### 7.1 Tendencia positiva

Maior peso em `BOVA11.SA` e `IVVB11.SA`, mantendo camada defensiva residual.

### 7.2 Estresse

Maior peso em `CDI`, `IMAB11.SA` e `USDBRL=X`, com reducao relevante do risco direcional.

### 7.3 Lateralizacao

Pesos equilibrados entre ativos de risco e defesa.

### 7.4 Recuperacao

Reentrada gradual em risco, sem abandono completo da protecao.

### 7.5 Principio de governanca

- nenhum peso negativo;
- soma de pesos igual a `100%`;
- pesos definidos antes da avaliacao de performance final.

## 8. Backtest

### 8.1 Estrutura

O motor de backtest recebe:

- `prices`
- `target_weights`
- `config`

E calcula:

- retornos da carteira;
- curva de patrimonio;
- historico de pesos aplicados;
- log de rebalanceamento;
- turnover;
- custo de transacao em bps, quando configurado.

### 8.2 Rebalanceamento

O rebalanceamento padrao e mensal.

Justificativa inicial:

- reduz excesso de giro;
- combina com a natureza mais lenta dos sinais de regime;
- evita reagir a ruido diario em um sistema ainda explicavel e robusto.

### 8.3 Controle de look-ahead bias

O projeto evita look-ahead bias em camadas complementares:

- o pipeline de features aplica `shift(1)` nas variaveis de decisao;
- o classificador consome apenas features defasadas;
- o peso decidido em `t` so entra na primeira observacao de retorno estritamente posterior a `t`.

Na pratica, isso significa que o sistema nao usa o proprio fechamento da data de decisao para definir e aplicar peso no mesmo retorno.

## 9. Benchmarks

O projeto compara a estrategia com referencias simples, interpretaveis e reproduziveis:

1. `Buy and hold` de `BOVA11.SA`
2. `CDI` ou caixa defensivo
3. carteira estatica diversificada tipo `60/40`
4. carteira `equal weight`

Esses benchmarks respondem a perguntas diferentes:

- o modelo supera risco direcional puro?
- supera a alternativa defensiva?
- agrega valor contra uma alocacao estatica razoavel?
- agrega valor contra uma diversificacao simples?

## 10. Metricas

As metricas principais do projeto sao:

- retorno acumulado;
- retorno anualizado;
- volatilidade anualizada;
- sharpe ratio;
- maximo drawdown;
- calmar ratio;
- hit rate;
- melhor mes;
- pior mes;
- numero de rebalanceamentos;
- turnover medio.

Todas devem ser preenchidas a partir da tabela exportada pelo pipeline.

## 11. Resultados

### 11.1 Metodologia x resultado

Esta secao deve registrar apenas observacoes efetivamente produzidas pelo pipeline final do estudo. Nao deve misturar regra metodologica com interpretacao de performance.

### 11.2 Tabela-resumo a preencher

| Item | Valor |
|---|---|
| Janela analisada | `[INSERIR_INTERVALO_REAL]` |
| Fonte de dados | `[INSERIR_FONTE_REAL_USADA]` |
| Retorno acumulado da estrategia | `[INSERIR_METRICA_REAL]` |
| Retorno anualizado da estrategia | `[INSERIR_METRICA_REAL]` |
| Volatilidade anualizada da estrategia | `[INSERIR_METRICA_REAL]` |
| Sharpe ratio da estrategia | `[INSERIR_METRICA_REAL]` |
| Maximo drawdown da estrategia | `[INSERIR_METRICA_REAL]` |
| Calmar ratio da estrategia | `[INSERIR_METRICA_REAL]` |
| Hit rate da estrategia | `[INSERIR_METRICA_REAL]` |
| Numero de rebalanceamentos | `[INSERIR_METRICA_REAL]` |
| Turnover medio | `[INSERIR_METRICA_REAL]` |
| Benchmark principal | `[INSERIR_BENCHMARK_REAL]` |
| Diferencial contra benchmark principal | `[INSERIR_COMPARACAO_REAL]` |

### 11.3 Leitura qualitativa a preencher

- principais periodos de acerto: `[DESCREVER_COM_BASE_EM_RESULTADO_REAL]`
- principais periodos de fragilidade: `[DESCREVER_COM_BASE_EM_RESULTADO_REAL]`
- comportamento em estresse: `[DESCREVER_COM_BASE_EM_RESULTADO_REAL]`
- comportamento em recuperacao: `[DESCREVER_COM_BASE_EM_RESULTADO_REAL]`

### 11.4 Regra de integridade

Nenhum resultado deve ser descrito como evidencia de superioridade estrutural sem:

- comparacao consistente com benchmarks;
- avaliacao fora do mero retorno bruto;
- reconhecimento explicito das limitacoes metodologicas.

## 12. Uso De GenAI

A camada GenAI do Aurora foi estruturada como apoio a:

- resumo executivo;
- analise narrativa por regime;
- revisao de limitacoes;
- revisao de vieses;
- preparacao de defesa tecnica.

Ela nao:

- baixa dados;
- calcula performance;
- escolhe regime;
- decide pesos;
- faz recomendacao de investimento.

Razao metodologica:

- decisao quantitativa precisa permanecer explicavel, reproduzivel e auditavel em codigo deterministico.

## 13. Limitacoes

### 13.1 Overfitting

O projeto procura reduzir risco de overfitting por meio de:

- thresholds definidos ex ante;
- pesos definidos a priori;
- ausencia de calibracao olhando retorno final;
- benchmarks simples e transparentes.

Ainda assim, risco residual permanece porque:

- a estrutura de regras foi desenhada por criterio humano;
- a robustez fora da amostra ainda precisa de validacao mais ampla;
- o universo de ativos ainda e enxuto.

### 13.2 Outras limitacoes relevantes

- regras de regime ainda sao simples;
- nao ha slippage, impostos ou impacto de mercado;
- o `CDI` pode exigir manutencao manual dependendo da fonte;
- nao ha, nesta etapa, validacao institucional de dados;
- resultados podem ser sensiveis a mudancas de janela, universo e fonte.

## 14. Proximos Passos

- consolidar uma base de dados mais institucional e verificavel;
- expandir testes fora da amostra e por subperiodos;
- introduzir estimativas mais realistas de custo e liquidez;
- evoluir a classificacao com maior profundidade, sem perder explicabilidade;
- criar relatorio automatizado a partir do pipeline final;
- incorporar monitoramento de estabilidade de regime;
- avaliar stress tests adicionais e cenarios adversos.

## 15. Disclaimer

Este documento tem finalidade tecnica, educacional e de pesquisa. Ele nao constitui recomendacao de investimento, oferta de ativos, promessa de retorno, consultoria financeira ou inducao a tomada de risco. Resultados historicos, simulados ou demonstrativos nao garantem desempenho futuro.
