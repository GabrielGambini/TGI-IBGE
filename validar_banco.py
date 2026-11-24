import pandas as pd
from sqlalchemy import text

# Reaproveita a conexão do seu script do pipeline (mesma pasta, arquivo Banco_de_Dados.py).
# Importar não roda o pipeline, só a configuração e a conexão.
# Se o seu arquivo tiver outro nome, troque "Banco_de_Dados" pelo nome dele (sem o .py).
from Banco_de_Dados import engine

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
pd.set_option("display.max_colwidth", 70)

consultas = {
    "1) Cobertura da fato do IPCA-15 por nível territorial": """
        SELECT nivel_territorial,
               COUNT(DISTINCT localidade_id) AS locais,
               COUNT(*) AS linhas,
               MIN(periodo_id) AS de,
               MAX(periodo_id) AS ate
        FROM fat_ipca_brasil
        GROUP BY nivel_territorial
    """,
    "2) Logs do pipeline (procure por Aviso ou Erro)": """
        SELECT * FROM logs_pipeline
    """,
    "3) IPCA-15 Brasil, índice geral, últimos períodos (compare com o divulgado pelo IBGE)": """
        SELECT indicador_id, indicador_nome, periodo_id, valor_indice
        FROM fat_ipca_brasil
        WHERE localidade_id = '1'
          AND categoria_id = '7169'
          AND indicador_id IN ('355', '356', '1120')
        ORDER BY periodo_id DESC, indicador_id
        LIMIT 6
    """,
    "4) Categorias do agregado IPCA-15": """
        SELECT DISTINCT categoria_id, categoria_nome
        FROM fat_ipca_brasil
        ORDER BY categoria_id
        LIMIT 15
    """,
}

with engine.connect() as conn:
    for titulo, sql in consultas.items():
        print(f"\n=== {titulo} ===")
        try:
            print(pd.read_sql(text(sql), conn).to_string(index=False))
        except Exception as e:
            print(f"Erro nesta consulta: {e}")