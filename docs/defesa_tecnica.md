# Defesa Tecnica

Este documento organiza respostas objetivas para perguntas mais dificeis sobre o Aurora Regime AI. O foco nao e vender resultado, e sim defender metodologia, escolhas de implementacao e limites do estudo.

## 1. Por Que Regime Switching?

Porque o mercado nao se comporta como um ambiente unico e estavel ao longo do tempo. Regime switching e uma forma de reconhecer mudancas estruturais de contexto, como estresse, tendencia e recuperacao, sem exigir previsao exata de preco. A proposta do Aurora nao e prever o proximo retorno diario, mas adaptar a exposicao conforme sinais coerentes com o ambiente observado.

## 2. Por Que Esses Indicadores?

Os indicadores foram escolhidos por complementaridade economica e simplicidade interpretavel:

- momentum ajuda a capturar persistencia de tendencia;
- volatilidade ajuda a medir instabilidade e estresse;
- drawdown captura perda acumulada em relacao ao pico;
- z-score ajuda a enxergar desvios e melhora relativa do comportamento recente;
- correlacao ajuda a detectar contagio e perda de diversificacao.

O objetivo nao foi maximizar complexidade, mas construir uma base defensavel, auditavel e testavel.

## 3. Por Que Esses Ativos?

O universo inicial foi montado para representar blocos economicos relevantes em uma carteira brasileira diversificada:

- `BOVA11.SA`: risco de renda variavel local;
- `IVVB11.SA`: exposicao internacional;
- `IMAB11.SA`: renda fixa ligada a inflacao;
- `USDBRL=X`: protecao cambial;
- `CDI`: caixa defensivo.

Nao se trata de um universo definitivo, mas de um conjunto enxuto e pedagogicamente forte para validar a arquitetura do projeto.

## 4. Como Evitaram Look-Ahead Bias?

O controle foi implementado em mais de uma camada:

- as features usadas para decisao sao defasadas em `1` periodo;
- o classificador consome apenas essas features defasadas;
- o backtest aplica o peso decidido em `t` somente no periodo seguinte.

Ou seja, o sistema nao usa a propria informacao do fechamento para decidir e executar no mesmo retorno. Esse ponto foi tratado como requisito de implementacao, nao como observacao opcional.

## 5. Como Evitaram Overfitting?

O Aurora reduz risco de overfitting por desenho metodologico:

- thresholds de regime definidos ex ante;
- pesos de alocacao definidos a priori;
- ausencia de otimizacao olhando retorno final;
- benchmarks simples e transparentes;
- separacao clara entre metodologia, simulacao e comunicacao.

Isso nao elimina completamente o risco de overfitting. Apenas reduz as fontes mais obvias de ajuste oportunista.

## 6. Por Que Rebalanceamento Mensal?

O rebalanceamento mensal foi escolhido como compromisso inicial entre responsividade e robustez:

- sinais de regime tendem a ser mais lentos do que sinais intradiarios;
- frequencia maior aumentaria giro e ruido;
- frequencia menor pode perder mudancas relevantes de contexto;
- mensal e um ponto de partida defensavel para uma estrategia de alocacao macro ou multiativo.

Essa escolha ainda pode ser revisitada no futuro, mas deve ser testada de forma controlada, e nao ajustada apenas para melhorar um backtest especifico.

## 7. Por Que A GenAI Nao Decide Investimento?

Porque decisao de investimento precisa permanecer:

- explicavel;
- reproduzivel;
- auditavel;
- verificavel sem depender de texto generativo.

A camada GenAI do Aurora serve para resumir resultados, estruturar defesa tecnica e apoiar documentacao. Ela nao calcula metricas, nao escolhe regime e nao define pesos.

## 8. O Que Acontece Se O Modelo Errar Regime?

O principal efeito e alocar pesos inadequados para o contexto observado. Isso pode:

- reduzir retorno potencial;
- elevar drawdown;
- aumentar custo de oportunidade;
- fazer a carteira reagir tarde ou cedo demais.

Esse risco e inerente a qualquer sistema de classificacao. Por isso, o projeto usa:

- benchmarks para comparacao;
- regras simples para facilitar auditoria;
- politicas defensivas em cenarios de estresse;
- documentacao explicita das limitacoes.

## 9. Quais Sao As Principais Limitacoes?

As principais limitacoes nesta fase sao:

- regras de regime ainda simples e fixas;
- ausencia de slippage, impostos e impacto de mercado;
- universo de ativos ainda reduzido;
- dependencia de fontes publicas e proxies;
- necessidade de testes adicionais fora da amostra;
- sensibilidade potencial a janelas de calculo e mudancas estruturais de mercado.

## 10. Como Evoluir Para Uma Versao Profissional?

Uma versao profissional exigiria, no minimo:

- base de dados mais robusta e auditavel;
- governanca formal de parametros e versoes;
- simulacao com custos, liquidez e restricoes operacionais realistas;
- monitoramento continuo de estabilidade de regime;
- testes por subperiodo, stress tests e validacao fora da amostra;
- instrumentacao para observabilidade, logs e trilha de auditoria;
- processo formal de revisao de risco e de aprovacao metodologica.

## 11. Pergunta Adicional: Se Os Resultados Finais Forem Fracos, O Projeto Continua Valido?

Sim, desde que a conclusao seja honesta. Em pesquisa quantitativa, arquitetura, controle de vieses e clareza metodologica sao entregas relevantes mesmo quando o desempenho final nao confirma a hipotese. Um resultado fraco ainda pode:

- invalidar uma tese de forma útil;
- revelar onde a classificacao falha;
- orientar a proxima iteracao do modelo;
- fortalecer a credibilidade do processo.

## 12. Pergunta Adicional: Por Que Nao Usar Um Modelo Mais Complexo Desde O Inicio?

Porque complexidade prematura dificulta interpretacao, auditoria e depuracao. O Aurora foi desenhado para crescer sobre uma base controlada. Antes de introduzir modelos mais sofisticados, era necessario garantir:

- estrutura profissional de projeto;
- pipeline reprodutivel;
- controle de look-ahead bias;
- benchmarks coerentes;
- documentacao defensavel.

## 13. Formula De Resposta Curta Para Banca

Se for preciso responder em poucos segundos:

> O Aurora Regime AI nao tenta prever o mercado ponto a ponto. Ele tenta reconhecer em que tipo de ambiente o mercado esta e adaptar a carteira com regras explicaveis, pesos definidos a priori e backtest com barreira temporal. A camada de GenAI so ajuda a comunicar e revisar o projeto; a decisao quantitativa continua toda em codigo auditavel.
