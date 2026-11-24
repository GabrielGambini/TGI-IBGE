import json
import urllib.parse

import certifi
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.mysql import DOUBLE, LONGTEXT, VARCHAR
from urllib3.util.retry import Retry

# --- CONFIGURAÇÃO DE ACESSO AO BANCO DE DADOS ---
USAR_NUVEM = True  # True = TiDB Cloud | False = MySQL local

if USAR_NUVEM:
    usuario = 'QQPXk1HfakbEwks.root'
    senha = urllib.parse.quote_plus('mwKVSJ3CFX6Zp9Q8')
    host = 'gateway01.sa-east-1.prod.aws.tidbcloud.com'
    porta = '4000'
else:
    usuario = 'root'
    senha = urllib.parse.quote_plus('91574455Ab@2026')
    host = 'localhost'
    porta = '3306'

banco = 'tgi_ibge'

# Bancos na nuvem exigem conexão com SSL
connect_args = {"ssl": {"ca": certifi.where()}} if USAR_NUVEM else {}

# Cria o banco se ainda não existir (o TiDB Cloud vem só com o banco 'sys' e outros de sistema)
_engine_admin = create_engine(
    f'mysql+pymysql://{usuario}:{senha}@{host}:{porta}/',
    connect_args=connect_args,
)
with _engine_admin.begin() as _conn:
    _conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {banco}"))
_engine_admin.dispose()

engine = create_engine(
    f'mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{banco}',
    connect_args=connect_args,
    pool_pre_ping=True,
)

# --- CONFIGURAÇÃO DA API ---
API = "https://servicodados.ibge.gov.br/api"
AGREGADO_IPCA15 = 7062  # IPCA-15 detalhado: mensal, acumulados e grupos
# Brasil (N1), regiões metropolitanas (N7) e municípios (N6) disponíveis no agregado
LOCALIDADES = "N1[all]|N7[all]|N6[all]"
CLASSIFICACAO = "315[all]"  # índice geral, grupos, subgrupos, itens e subitens
PERIODO_INICIO = "202002"  # primeiro período disponível no agregado 7062
MESES_POR_REQUISICAO = 3  # evita estourar o limite de valores por requisição do SIDRA

http = requests.Session()
http.mount(
    "https://",
    HTTPAdapter(max_retries=Retry(total=3, backoff_factor=2, status_forcelist=[429, 502, 503, 504])),
)


def buscar_json(url, timeout=120):
    resp = http.get(url, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} em {url} -> {resp.text[:200]}")
    return resp.json()


def registrar_log(tabela, status, lines=0, erro=None):
    try:
        log_df = pd.DataFrame([{
            "tabela_destino": tabela,
            "status": status,
            "total_linhas": lines,
            "mensagem_erro": str(erro) if erro else None,
        }])
        log_df.to_sql("logs_pipeline", con=engine, if_exists="append", index=False)
    except Exception as e:
        print(f"⚠️ Erro ao gravar log: {e}")


def carregar_dados_gerais(url, table_name, force_longtext=None):
    try:
        print(f"Buscando dados para: {table_name}...")
        data = buscar_json(url, timeout=60)

        # Aviso se a API paginar (ex.: calendário) e estivermos pegando só a primeira página
        if isinstance(data, dict) and data.get("totalPages", 1) > 1:
            aviso = f"Resposta paginada ({data.get('totalPages')} páginas); só a 1ª foi carregada."
            print(f"⚠️ {table_name}: {aviso}")
            registrar_log(table_name, "Aviso", 0, aviso)

        df = pd.json_normalize(data)
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                df[col] = df[col].apply(lambda x: json.dumps(x) if x is not None else None)

        dtype_dict = {}
        for col in force_longtext or []:
            if col in df.columns:
                dtype_dict[col] = LONGTEXT

        if df.empty:
            print(f"⚠️ '{table_name}' veio vazia, tabela não alterada.")
            registrar_log(table_name, "Vazio", 0)
            return

        df.to_sql(table_name, con=engine, if_exists="replace", index=False, dtype=dtype_dict)
        print(f"✅ Tabela '{table_name}' carregada com sucesso! ({len(df)} linhas)")
        registrar_log(table_name, "Sucesso", len(df))
    except Exception as e:
        print(f"⚠️ Falha em '{table_name}': {e}")
        registrar_log(table_name, "Erro Técnico", 0, str(e))


def converter_valor(v):
    """Converte o valor do SIDRA. '-' é zero real; 'X', '..', '...' e vazio são dado ausente/sigiloso."""
    if v is None:
        return None
    v = str(v).strip()
    if v == "-":
        return 0.0
    if v in ("", "X", "..", "..."):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def lista_periodos(base):
    periodos_disponiveis = buscar_json(f"{base}/periodos")
    periodos = sorted(
        str(periodo["id"])
        for periodo in periodos_disponiveis
        if str(periodo["id"]) >= PERIODO_INICIO
    )
    if not periodos:
        raise RuntimeError(f"Nenhum período disponível a partir de {PERIODO_INICIO}.")
    return periodos


def carregar_fato_ipca15(table_name):
    """Fato do IPCA-15: áreas disponíveis, variáveis e categorias do agregado 7062."""
    try:
        print(f"Buscando e processando a FATO UNIFICADA: {table_name}...")
        base = f"{API}/v3/agregados/{AGREGADO_IPCA15}"

        meta = buscar_json(f"{base}/metadados")
        variaveis_ids = [v["id"] for v in meta["variaveis"]]
        print(f"   Variáveis encontradas: {variaveis_ids}")

        periodos = lista_periodos(base)
        blocos = [periodos[i:i + MESES_POR_REQUISICAO] for i in range(0, len(periodos), MESES_POR_REQUISICAO)]

        linhas_fato = []
        erros = []

        for var_id in variaveis_ids:
            for bloco in blocos:
                intervalo = f"{bloco[0]}-{bloco[-1]}" if len(bloco) > 1 else bloco[0]
                url = (
                    f"{base}/periodos/{intervalo}/variaveis/{var_id}"
                    f"?localidades={LOCALIDADES}&classificacao={CLASSIFICACAO}"
                )
                try:
                    data = buscar_json(url)
                except Exception as e:
                    erros.append(f"var {var_id} períodos {intervalo}: {e}")
                    continue

                for variavel in data:
                    for res in variavel.get("resultados", []):
                        categorias = {}
                        for classif in res.get("classificacoes", []):
                            categorias.update(classif.get("categoria", {}))
                        categoria_id, categoria_nome = next(iter(categorias.items()), (None, None))

                        for serie in res.get("series", []):
                            loc = serie.get("localidade", {})
                            for periodo, valor in serie.get("serie", {}).items():
                                valor_num = converter_valor(valor)
                                if valor_num is None:
                                    continue
                                linhas_fato.append({
                                    "indicador_id": variavel.get("id"),
                                    "indicador_nome": variavel.get("variavel"),
                                    "unidade_medida": variavel.get("unidade"),
                                    "nivel_territorial": loc.get("nivel", {}).get("id"),
                                    "localidade_id": loc.get("id"),
                                    "localidade_nome": loc.get("nome"),
                                    "categoria_id": categoria_id,
                                    "categoria_nome": categoria_nome,
                                    "periodo_id": periodo,
                                    "valor_indice": valor_num,
                                })
            print(f"   Variável {var_id} concluída. Linhas acumuladas: {len(linhas_fato)}")

        # Se algum bloco falhou, NÃO sobrescreve a tabela: uma fato parcial enganaria o dashboard.
        if erros:
            print(f"⚠️ {len(erros)} requisição(ões) falharam; tabela '{table_name}' NÃO foi alterada.")
            registrar_log(table_name, "Erro Parcial", 0, " | ".join(erros[:5]))
            return

        df_fato = pd.DataFrame(linhas_fato)
        if df_fato.empty:
            print(f"⚠️ Fato '{table_name}' veio vazia, tabela não alterada.")
            registrar_log(table_name, "Vazio", 0)
            return

        dtype_fato = {
            "indicador_id": VARCHAR(10),
            "indicador_nome": VARCHAR(255),
            "unidade_medida": VARCHAR(100),
            "nivel_territorial": VARCHAR(5),
            "localidade_id": VARCHAR(10),
            "localidade_nome": VARCHAR(100),
            "categoria_id": VARCHAR(15),
            "categoria_nome": VARCHAR(255),
            "periodo_id": VARCHAR(6),
            "valor_indice": DOUBLE,
        }
        # Grava em lotes: cada lote é uma transação separada. Gravar milhões de linhas numa
        # transação só funciona no MySQL local; bancos distribuídos (TiDB) rejeitam transações grandes.
        tamanho_lote = 20000
        for i in range(0, len(df_fato), tamanho_lote):
            df_fato.iloc[i:i + tamanho_lote].to_sql(
                table_name, con=engine,
                if_exists="replace" if i == 0 else "append",
                index=False, dtype=dtype_fato, chunksize=5000, method="multi",
            )
            print(f"   Gravadas {min(i + tamanho_lote, len(df_fato))}/{len(df_fato)} linhas...")

        # Índice para acelerar os joins/filtros do Power BI
        try:
            with engine.begin() as conn:
                conn.execute(text(
                    f"CREATE INDEX idx_{table_name}_busca "
                    f"ON {table_name} (periodo_id, localidade_id, categoria_id, indicador_id)"
                ))
        except Exception as e:
            print(f"⚠️ Não foi possível criar o índice: {e}")

        print(f"✅ FATO '{table_name}' carregada! Total: {len(df_fato)} linhas.")
        print(f"   Localidades distintas: {df_fato['localidade_id'].nunique()} | "
              f"Categorias distintas: {df_fato['categoria_id'].nunique()}")
        registrar_log(table_name, "Sucesso", len(df_fato))
    except Exception as e:
        print(f"⚠️ Falha técnica na FATO: {e}")
        registrar_log(table_name, "Erro Técnico", 0, str(e))


if __name__ == "__main__":
    print("=== INICIANDO PIPELINE IBGE ===\n")

    # Dimensões geográficas
    carregar_dados_gerais(f"{API}/v1/localidades/regioes?orderBy=nome", "dim_regioes")
    carregar_dados_gerais(f"{API}/v1/localidades/estados?orderBy=nome", "dim_estados")
    carregar_dados_gerais(f"{API}/v1/localidades/mesorregioes?orderBy=nome", "dim_mesorregioes")
    carregar_dados_gerais(f"{API}/v1/localidades/municipios", "dim_municipios")

    # Nomes "ipp" mantidos para não quebrar o que já existe no banco/Power BI.
    carregar_dados_gerais(f"{API}/v3/agregados/{AGREGADO_IPCA15}/periodos", "aux_ipp_periodos")
    carregar_dados_gerais(
        f"{API}/v3/agregados/{AGREGADO_IPCA15}/metadados", "meta_ipp_descritivo",
        force_longtext=["variaveis", "classificacoes"],
    )

    # Nome da tabela mantido para preservar a conexão existente com o Power BI.
    carregar_fato_ipca15("fat_ipca_brasil")

    # Metadados gerais
    carregar_dados_gerais(f"{API}/v2/metadados/pesquisas", "meta_pesquisas")
    carregar_dados_gerais(f"{API}/v3/calendario/?de=2018-12-20", "meta_calendario_geral", force_longtext=["items"])

    print("\n--- PIPELINE FINALIZADA. Confira a tabela logs_pipeline para ver o status de cada carga. ---")