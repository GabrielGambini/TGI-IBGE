import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import LONGTEXT
import urllib.parse
import json

# --- CONFIGURAÇÃO DE ACESSO AO BANCO DE DADOS ---
usuario = 'root'
senha = urllib.parse.quote_plus('91574455Ab@2026')
host = 'localhost'
porta = '3306'
banco = 'tgi_ibge'

engine = create_engine(f'mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{banco}')


def registrar_log(tabela, status, lines=0, erro=None):
    try:
        log_df = pd.DataFrame([{
            'tabela_destino': tabela,
            'status': status,
            'total_linhas': lines,
            'mensagem_erro': str(erro) if erro else None
        }])
        log_df.to_sql('logs_pipeline', con=engine, if_exists='append', index=False)
    except Exception as e:
        print(f"⚠️ Erro ao gravar log: {e}")


def carregar_dados_gerais(url, table_name, force_longtext=None):
    try:
        print(f"Buscando dados para: {table_name}...")
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            df = pd.json_normalize(data)
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                    df[col] = df[col].apply(lambda x: json.dumps(x) if x is not None else None)
            dtype_dict = {}
            if force_longtext:
                for col in force_longtext:
                    if col in df.columns:
                        dtype_dict[col] = LONGTEXT
            if not df.empty:
                df.to_sql(table_name, con=engine, if_exists='replace', index=False, dtype=dtype_dict)
                print(f"✅ Tabela '{table_name}' carregada com sucesso!")
                registrar_log(table_name, "Sucesso", len(df))
    except Exception as e:
        registrar_log(table_name, "Erro Técnico", 0, str(e))


def carregar_fato_ipca_regional(url, table_name):
    try:
        print(f"Buscando e processando a FATO REGIONAL UNIFICADA: {table_name}...")
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            linhas_fato = []
            for variavel in data:
                indicador_id = variavel.get('id')
                indicador_nome = variavel.get('variavel')
                unidade = variavel.get('unidade')
                for res in variavel.get('resultados', []):
                    for boco_serie in res.get('series', []):
                        localidade_id = boco_serie.get('localidade', {}).get('id')
                        localidade_nome = boco_serie.get('localidade', {}).get('nome')
                        for periodo, valor in boco_serie.get('serie', {}).items():
                            if valor not in [None, "-", "", "..."]:
                                linhas_fato.append({
                                    'indicador_id': indicador_id,
                                    'indicador_nome': indicador_nome,
                                    'unidade_medida': unidade,
                                    'localidade_id': localidade_id,
                                    'localidade_nome': localidade_nome,
                                    'periodo_id': periodo,
                                    'valor_indice': float(valor)
                                })
            df_fato = pd.DataFrame(linhas_fato)
            if not df_fato.empty:
                df_fato.to_sql(table_name, con=engine, if_exists='replace', index=False)
                print(f"✅ Nova FATO Regional '{table_name}' carregada! Total: {len(df_fato)} linhas.")
                registrar_log(table_name, "Sucesso", len(df_fato))
    except Exception as e:
        print(f"⚠️ Falha técnica na FATO: {e}")
        registrar_log(table_name, "Erro Técnico", 0, str(e))


if __name__ == "__main__":
    print("=== INICIANDO PIPELINE DE VOLTA DOS ESTADOS COMPLETA ===\n")

    carregar_dados_gerais("https://servicodados.ibge.gov.br/api/v1/localidades/regioes?orderBy=nome", "dim_regioes")
    carregar_dados_gerais("https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome", "dim_estados")
    carregar_dados_gerais("https://servicodados.ibge.gov.br/api/v1/localidades/mesorregioes?orderBy=nome",
                          "dim_mesorregioes")
    carregar_dados_gerais("https://servicodados.ibge.gov.br/api/v1/localidades/municipios", "dim_municipios")

    carregar_dados_gerais("https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos", "aux_ipp_periodos")
    carregar_dados_gerais("https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados", "meta_ipp_descritivo",
                          force_longtext=['variaveis', 'classificacoes'])

    # MUDANÇA DA URL AQUI: Trocado localidades=BR para localidades=N7 (Regiões Metropolitanas de 2020 a 2026)
    url_regional = "https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/202001-202612/variaveis?localidades=N7"
    carregar_fato_ipca_regional(url_regional, "fat_ipca_brasil")

    carregar_dados_gerais("https://servicodados.ibge.gov.br/api/v2/metadados/pesquisas", "meta_pesquisas")
    carregar_dados_gerais("https://servicodados.ibge.gov.br/api/v3/calendario/?de=2018-12-20", "meta_calendario_geral",
                          force_longtext=['items'])

    print("\n--- PIPELINE ATUALIZADA FINALIZADA COM SUCESSO ---")