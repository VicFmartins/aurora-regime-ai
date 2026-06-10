# Dados

## Fonte Primaria

A camada inicial de ingestao usa `yfinance` como fonte primaria para baixar historico de precos. O carregamento privilegia a coluna `Adj Close`; quando ela nao estiver disponivel, o sistema faz fallback para `Close` e emite um aviso claro.

## Universo Inicial De Tickers

- `BOVA11.SA`: renda variavel Brasil
- `IVVB11.SA`: exposicao internacional
- `IMAB11.SA`: renda fixa inflacao
- `USDBRL=X`: protecao cambial
- `CDI`: caixa defensivo/proxy

## Cache

O cache local de precos fica em `data/cache/prices.parquet`. A funcao de carga reutiliza esse arquivo por padrao e so faz novo download quando `force_download=True`.

## Validacoes

Os dados carregados sao validados para garantir:

- indice `DatetimeIndex`;
- datas ordenadas;
- ausencia de datas duplicadas;
- minimo de observacoes por ativo;
- limite de nulos por ativo.

## Limitacoes Atuais

- `yfinance` depende de disponibilidade externa e pode falhar temporariamente;
- nem todos os tickers possuem cobertura uniforme no Yahoo Finance;
- `CDI` pode exigir manutencao manual, pois nem sempre existe uma serie compativel na mesma fonte;
- o projeto ainda nao implementa ajuste metodologico adicional de calendario, feriados ou consolidacao de multiplas fontes.

## Substituicao Manual Por CSV

Quando o download falhar ou um ticker nao estiver disponivel, o projeto orienta o uso de `data/raw/prices.csv`. O formato esperado e:

- primeira coluna com datas;
- demais colunas com os tickers configurados;
- valores numericos de preco por data.

Essa rota manual permite substituir parcial ou totalmente o download via `yfinance` no futuro, sem alterar a interface principal da camada de dados.
