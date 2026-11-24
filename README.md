# TGI-IBGE
Repositório para guardar os códigos usados no TGI.

# IPCA15 Analytics
npm install && npm run dev
Dados em src/data.ts (IBGE, IPCA-15 out/2026). Atualize a cada divulgação ou integre a API SIDRA.

## Atualização mensal do banco

O GitHub Actions executa `Banco_de_Dados.py` no dia 15 de cada mês, às 12:00 UTC, e também pode ser iniciado manualmente pela aba **Actions**.

Configure estes secrets do repositório em **Settings > Secrets and variables > Actions**:

- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST` (opcional; padrão TiDB Cloud)
- `DB_PORT` (opcional; padrão `4000`)
- `DB_NAME` (opcional; padrão `tgi_ibge`)

O workflow usa o TiDB Cloud por padrão. Para execução local, defina `USAR_NUVEM=false` e configure as variáveis `DB_USER` e `DB_PASSWORD`.
