# Dados

Este documento deve registrar:

- fontes de dados utilizadas;
- licenciamento e restricoes de uso;
- frequencia e granularidade;
- pipeline de coleta, tratamento e atualizacao;
- qualidade, cobertura e lacunas conhecidas.

Diretriz atual:

- `data/raw/` para dados brutos;
- `data/processed/` para dados tratados;
- `data/cache/` para artefatos temporarios.

Dados reais nao devem ser versionados no Git. O repositorio mantem apenas a estrutura das pastas com `.gitkeep`.
