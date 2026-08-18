import requests
import pandas as pd
import json
import urllib.parse

from sqlalchemy import (
    create_engine,
    Column,
    BigInteger,
    Float,
    Boolean,
    DateTime,
    Text,
    MetaData,
    Table
)

from sqlalchemy.dialects.mysql import LONGTEXT


# ============================================================
# CONFIGURAÇÃO DO AIVEN MYSQL
# ============================================================

usuario = 'avnadmin'

# COLOQUE AQUI A SENHA ATUAL DO AIVEN
senha = 'AVNS_6yHv-HjnCrIrlxEVRWP'

host = 'mysql-38a5aa36-tgiibge2026.g.aivencloud.com'
porta = 16051
banco = 'defaultdb'

senha_encoded = urllib.parse.quote_plus(senha)

engine = create_engine(
    f'mysql+pymysql://{usuario}:{senha_encoded}@{host}:{porta}/{banco}',
    connect_args={
        'ssl': {}
    },
    pool_pre_ping=True
)


# ============================================================
# TESTE DE CONEXÃO
# ============================================================

try:

    with engine.connect() as conn:

        print(
            "✅ Conexão com o Aiven realizada com sucesso!"
        )

except Exception as e:

    print(
        "❌ Erro na conexão com o Aiven:"
    )

    print(e)

    exit()


# ============================================================
# VIEWS UTILIZADAS PELO POWER BI
# ============================================================

VIEWS = [

    'v_dicionario_indicadores',

    'v_fat_ipp_tratada',

    'v_localidades_completas',

    'v_municipios_detalhado',

    'v_proximas_divulgacoes',

    'v_status_pipeline',

    'v_ultima_atualizacao_tabelas'

]


# ============================================================
# REMOVER VIEWS TEMPORARIAMENTE
#
# Isso é necessário porque algumas views dependem das tabelas
# que serão recriadas pelo pipeline.
# ============================================================

def remover_views():

    print(
        "\n================================================"
    )

    print(
        "🧹 PREPARANDO AS VIEWS"
    )

    print(
        "================================================"
    )

    try:

        with engine.begin() as conn:

            for view in VIEWS:

                try:

                    conn.exec_driver_sql(
                        f"DROP VIEW IF EXISTS `{view}`"
                    )

                    print(
                        f"   🗑️ View removida temporariamente: {view}"
                    )

                except Exception as e:

                    print(
                        f"   ⚠️ Não foi possível remover "
                        f"{view}: {e}"
                    )

        return True

    except Exception as e:

        print(
            f"❌ Erro ao preparar views: {e}"
        )

        return False


# ============================================================
# GARANTIR ESTRUTURA DO LOG
# ============================================================

def preparar_logs():

    table_name = 'logs_pipeline'

    try:

        metadata = MetaData()

        # ----------------------------------------------------
        # Verifica se tabela existe
        # ----------------------------------------------------

        with engine.connect() as conn:

            resultado = conn.exec_driver_sql(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name = 'logs_pipeline'
                """
            )

            existe = resultado.scalar() > 0

        # ----------------------------------------------------
        # Cria tabela caso não exista
        # ----------------------------------------------------

        if not existe:

            tabela = Table(

                table_name,

                metadata,

                Column(
                    'pipeline_id',
                    BigInteger,
                    primary_key=True,
                    autoincrement=True
                ),

                Column(
                    'data_execucao',
                    DateTime,
                    nullable=False
                ),

                Column(
                    'tabela_destino',
                    Text
                ),

                Column(
                    'status',
                    Text
                ),

                Column(
                    'total_linhas',
                    BigInteger
                ),

                Column(
                    'mensagem_erro',
                    LONGTEXT
                )

            )

            metadata.create_all(engine)

            print(
                "✅ Tabela logs_pipeline criada."
            )

        else:

            # ------------------------------------------------
            # Verifica se data_execucao já existe
            # ------------------------------------------------

            with engine.connect() as conn:

                resultado = conn.exec_driver_sql(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.columns
                    WHERE table_schema = DATABASE()
                    AND table_name = 'logs_pipeline'
                    AND column_name = 'data_execucao'
                    """
                )

                coluna_existe = resultado.scalar() > 0

            # ------------------------------------------------
            # Adiciona coluna caso ainda não exista
            # ------------------------------------------------

            if not coluna_existe:

                with engine.begin() as conn:

                    conn.exec_driver_sql(
                        """
                        ALTER TABLE logs_pipeline
                        ADD COLUMN data_execucao
                        DATETIME
                        NULL
                        """
                    )

                print(
                    "✅ Coluna data_execucao adicionada ao logs_pipeline."
                )

                # ------------------------------------------------
                # Preenche logs antigos
                # ------------------------------------------------

                with engine.begin() as conn:

                    conn.exec_driver_sql(
                        """
                        UPDATE logs_pipeline
                        SET data_execucao = CURRENT_TIMESTAMP
                        WHERE data_execucao IS NULL
                        """
                    )

                # ------------------------------------------------
                # Depois torna obrigatória
                # ------------------------------------------------

                with engine.begin() as conn:

                    conn.exec_driver_sql(
                        """
                        ALTER TABLE logs_pipeline
                        MODIFY COLUMN data_execucao
                        DATETIME NOT NULL
                        """
                    )

            else:

                print(
                    "✅ logs_pipeline já possui data_execucao."
                )

        return True

    except Exception as e:

        print(
            f"❌ Erro ao preparar logs_pipeline: {e}"
        )

        return False


# ============================================================
# DEFINIR TIPO SQLALCHEMY
# ============================================================

def definir_tipo_sqlalchemy(
    serie,
    nome_coluna,
    force_longtext=None
):

    if force_longtext and nome_coluna in force_longtext:

        return LONGTEXT

    dtype = serie.dtype

    if pd.api.types.is_integer_dtype(dtype):

        return BigInteger

    if pd.api.types.is_float_dtype(dtype):

        return Float

    if pd.api.types.is_bool_dtype(dtype):

        return Boolean

    if pd.api.types.is_datetime64_any_dtype(dtype):

        return DateTime

    return Text


# ============================================================
# SALVAR DATAFRAME
# ============================================================

def salvar_dataframe(
    df,
    table_name,
    force_longtext=None
):

    if df.empty:

        print(
            f"⚠️ DataFrame vazio para '{table_name}'."
        )

        return False

    metadata = MetaData()

    try:

        # ----------------------------------------------------
        # Remove tabela antiga
        # ----------------------------------------------------

        with engine.begin() as conn:

            conn.exec_driver_sql(
                f"DROP TABLE IF EXISTS `{table_name}`"
            )

        # ----------------------------------------------------
        # Cria PRIMARY KEY do pipeline
        # ----------------------------------------------------

        colunas = [

            Column(
                'pipeline_id',
                BigInteger,
                primary_key=True,
                autoincrement=True
            )

        ]

        # ----------------------------------------------------
        # Cria colunas vindas do IBGE
        # ----------------------------------------------------

        for coluna_original in df.columns:

            coluna = coluna_original

            # Segurança para evitar conflito
            # com pipeline_id

            if coluna == 'pipeline_id':

                coluna = 'pipeline_id_ibge'

                df = df.rename(
                    columns={
                        coluna_original:
                        coluna
                    }
                )

            tipo = definir_tipo_sqlalchemy(

                df[coluna],

                coluna,

                force_longtext

            )

            colunas.append(

                Column(
                    coluna,
                    tipo,
                    nullable=True
                )

            )

        # ----------------------------------------------------
        # Cria tabela
        # ----------------------------------------------------

        tabela = Table(

            table_name,

            metadata,

            *colunas

        )

        metadata.create_all(engine)

        # ----------------------------------------------------
        # Insere dados
        # ----------------------------------------------------

        df.to_sql(

            table_name,

            con=engine,

            if_exists='append',

            index=False

        )

        print(

            f"✅ Tabela '{table_name}' criada e "
            f"carregada com sucesso! "
            f"Total: {len(df)} linhas."

        )

        return True

    except Exception as e:

        print(

            f"❌ Erro ao criar/carregar tabela "
            f"'{table_name}': {e}"

        )

        return False


# ============================================================
# REGISTRAR LOG
# ============================================================

def registrar_log(
    tabela,
    status,
    lines=0,
    erro=None
):

    try:

        log_df = pd.DataFrame([{

            'data_execucao':
                pd.Timestamp.now(),

            'tabela_destino':
                tabela,

            'status':
                status,

            'total_linhas':
                lines,

            'mensagem_erro':
                str(erro) if erro else None

        }])

        log_df.to_sql(

            'logs_pipeline',

            con=engine,

            if_exists='append',

            index=False

        )

    except Exception as e:

        print(
            f"⚠️ Erro ao gravar log: {e}"
        )


# ============================================================
# CARREGAR DADOS GERAIS
# ============================================================

def carregar_dados_gerais(
    url,
    table_name,
    force_longtext=None
):

    try:

        print(
            f"\nBuscando dados para: "
            f"{table_name}..."
        )

        response = requests.get(

            url,

            timeout=60

        )

        # ----------------------------------------------------
        # HTTP
        # ----------------------------------------------------

        if response.status_code != 200:

            erro = (

                f"HTTP {response.status_code} - "
                f"{response.text[:500]}"

            )

            print(
                f"❌ Erro na API: {erro}"
            )

            registrar_log(
                table_name,
                "Erro API",
                0,
                erro
            )

            return False

        # ----------------------------------------------------
        # JSON
        # ----------------------------------------------------

        data = response.json()

        df = pd.json_normalize(data)

        # ----------------------------------------------------
        # Converte listas e dicionários para JSON
        # ----------------------------------------------------

        for col in df.columns:

            if df[col].apply(

                lambda x:
                isinstance(x, (list, dict))

            ).any():

                df[col] = df[col].apply(

                    lambda x:

                    json.dumps(
                        x,
                        ensure_ascii=False
                    )

                    if x is not None
                    else None

                )

        # ----------------------------------------------------
        # DataFrame vazio
        # ----------------------------------------------------

        if df.empty:

            print(
                f"⚠️ Nenhum dado encontrado "
                f"para '{table_name}'."
            )

            registrar_log(
                table_name,
                "Sem dados",
                0
            )

            return False

        # ----------------------------------------------------
        # Salva
        # ----------------------------------------------------

        sucesso = salvar_dataframe(

            df,

            table_name,

            force_longtext

        )

        if sucesso:

            registrar_log(

                table_name,

                "Sucesso",

                len(df)

            )

            return True

        registrar_log(

            table_name,

            "Erro Técnico",

            0,

            "Falha ao salvar tabela."

        )

        return False

    except Exception as e:

        print(

            f"❌ Erro técnico em "
            f"'{table_name}': {e}"

        )

        registrar_log(

            table_name,

            "Erro Técnico",

            0,

            str(e)

        )

        return False


# ============================================================
# FATO IPCA REGIONAL
# ============================================================

def carregar_fato_ipca_regional(
    url,
    table_name
):

    try:

        print(

            f"\nBuscando e processando a "
            f"FATO REGIONAL UNIFICADA: "
            f"{table_name}..."

        )

        response = requests.get(

            url,

            timeout=120

        )

        # ----------------------------------------------------
        # HTTP
        # ----------------------------------------------------

        if response.status_code != 200:

            erro = (

                f"HTTP {response.status_code} - "
                f"{response.text[:500]}"

            )

            print(

                f"❌ Erro na API da FATO: "
                f"{erro}"

            )

            registrar_log(

                table_name,

                "Erro API",

                0,

                erro

            )

            return False

        data = response.json()

        linhas_fato = []

        # ----------------------------------------------------
        # Processamento
        # ----------------------------------------------------

        for variavel in data:

            indicador_id = variavel.get(
                'id'
            )

            indicador_nome = variavel.get(
                'variavel'
            )

            unidade = variavel.get(
                'unidade'
            )

            for resultado in variavel.get(
                'resultados',
                []
            ):

                for bloco_serie in resultado.get(
                    'series',
                    []
                ):

                    localidade = bloco_serie.get(
                        'localidade',
                        {}
                    )

                    localidade_id = localidade.get(
                        'id'
                    )

                    localidade_nome = localidade.get(
                        'nome'
                    )

                    serie = bloco_serie.get(
                        'serie',
                        {}
                    )

                    for periodo, valor in serie.items():

                        if valor not in [
                            None,
                            "-",
                            "",
                            "..."
                        ]:

                            try:

                                linhas_fato.append({

                                    'indicador_id':
                                        indicador_id,

                                    'indicador_nome':
                                        indicador_nome,

                                    'unidade_medida':
                                        unidade,

                                    'localidade_id':
                                        localidade_id,

                                    'localidade_nome':
                                        localidade_nome,

                                    'periodo_id':
                                        periodo,

                                    'valor_indice':
                                        float(valor)

                                })

                            except (
                                ValueError,
                                TypeError
                            ):

                                print(
                                    f"⚠️ Valor ignorado: "
                                    f"{valor}"
                                )

        df_fato = pd.DataFrame(
            linhas_fato
        )

        # ----------------------------------------------------
        # Vazio
        # ----------------------------------------------------

        if df_fato.empty:

            print(
                f"⚠️ Nenhum dado encontrado "
                f"para '{table_name}'."
            )

            registrar_log(
                table_name,
                "Sem dados",
                0
            )

            return False

        # ----------------------------------------------------
        # Salvar
        # ----------------------------------------------------

        sucesso = salvar_dataframe(

            df_fato,

            table_name

        )

        if sucesso:

            registrar_log(

                table_name,

                "Sucesso",

                len(df_fato)

            )

            return True

        registrar_log(

            table_name,

            "Erro Técnico",

            0,

            "Falha ao salvar FATO."

        )

        return False

    except Exception as e:

        print(

            f"❌ Falha técnica na FATO: "
            f"{e}"

        )

        registrar_log(

            table_name,

            "Erro Técnico",

            0,

            str(e)

        )

        return False


# ============================================================
# CRIAR AS 7 VIEWS
# ============================================================

def criar_views():

    print(
        "\n================================================"
    )

    print(
        "👁️ CRIANDO VIEWS PARA O POWER BI"
    )

    print(
        "================================================\n"
    )

    views_sql = {

        # ----------------------------------------------------
        # 1
        # ----------------------------------------------------

        'v_dicionario_indicadores': """

        CREATE OR REPLACE VIEW v_dicionario_indicadores AS

        SELECT

            meta_ipp_descritivo.id AS id,

            meta_ipp_descritivo.nome
                AS nome_indicador,

            meta_ipp_descritivo.`periodicidade.frequencia`
                AS frequencia,

            JSON_UNQUOTE(
                JSON_EXTRACT(
                    meta_ipp_descritivo.variaveis,
                    '$[*].nome'
                )
            ) AS detalhes_variaveis

        FROM meta_ipp_descritivo

        """,

        # ----------------------------------------------------
        # 2
        # ----------------------------------------------------

        'v_fat_ipp_tratada': """

        CREATE OR REPLACE VIEW v_fat_ipp_tratada AS

        SELECT

            fat_ipca_brasil.indicador_id
                AS indicador_id,

            CASE

                WHEN fat_ipca_brasil.indicador_nome
                    LIKE '%%Variação mensal%%'

                    THEN 'Variação Mensal'

                WHEN fat_ipca_brasil.indicador_nome
                    LIKE '%%Variação acumulada no ano%%'

                    THEN 'Acumulado no Ano'

                WHEN fat_ipca_brasil.indicador_nome
                    LIKE '%%Variação acumulada em 12 meses%%'

                    THEN 'Acumulado em 12 Meses'

                WHEN fat_ipca_brasil.indicador_nome
                    LIKE '%%Peso mensal%%'

                    THEN 'Peso Mensal'

                ELSE
                    fat_ipca_brasil.indicador_nome

            END AS indicador_nome,

            fat_ipca_brasil.unidade_medida
                AS unidade_medida,

            fat_ipca_brasil.localidade_id
                AS localidade_id,

            fat_ipca_brasil.localidade_nome
                AS localidade_nome,

            fat_ipca_brasil.periodo_id
                AS periodo_id,

            fat_ipca_brasil.valor_indice
                AS valor_indice

        FROM fat_ipca_brasil

        """,

        # ----------------------------------------------------
        # 3
        # ----------------------------------------------------

        'v_localidades_completas': """

        CREATE OR REPLACE VIEW v_localidades_completas AS

        SELECT

            e.id AS estado_id,

            e.nome AS estado_nome,

            e.sigla AS estado_sigla,

            r.nome AS regiao_nome

        FROM dim_estados e

        JOIN dim_regioes r

            ON e.`regiao.id` = r.id

        """,

        # ----------------------------------------------------
        # 4
        # ----------------------------------------------------

        'v_municipios_detalhado': """

        CREATE OR REPLACE VIEW v_municipios_detalhado AS

        SELECT

            m.id AS municipio_id,

            m.nome AS municipio_nome,

            e.nome AS estado_nome,

            e.sigla AS estado_sigla

        FROM dim_municipios m

        JOIN dim_estados e

            ON m.`microrregiao.mesorregiao.UF.id`
                = e.id

        """,

        # ----------------------------------------------------
        # 5
        # ----------------------------------------------------

        'v_proximas_divulgacoes': """

        CREATE OR REPLACE VIEW v_proximas_divulgacoes AS

        SELECT

            JSON_UNQUOTE(
                JSON_EXTRACT(
                    meta_calendario_geral.items,
                    '$[0].titulo'
                )
            ) AS titulo_pesquisa,

            JSON_UNQUOTE(
                JSON_EXTRACT(
                    meta_calendario_geral.items,
                    '$[0].periodo'
                )
            ) AS periodo_referencia,

            JSON_UNQUOTE(
                JSON_EXTRACT(
                    meta_calendario_geral.items,
                    '$[0].divulgacao'
                )
            ) AS data_divulgacao

        FROM meta_calendario_geral

        """,

        # ----------------------------------------------------
        # 6
        # ----------------------------------------------------

        'v_status_pipeline': """

        CREATE OR REPLACE VIEW v_status_pipeline AS

        SELECT

            logs_pipeline.data_execucao
                AS data_execucao,

            logs_pipeline.tabela_destino
                AS tabela_destino,

            logs_pipeline.status
                AS status,

            logs_pipeline.total_linhas
                AS total_linhas,

            logs_pipeline.mensagem_erro
                AS mensagem_erro

        FROM logs_pipeline

        ORDER BY
            logs_pipeline.data_execucao DESC

        """,

        # ----------------------------------------------------
        # 7
        # ----------------------------------------------------

        'v_ultima_atualizacao_tabelas': """

        CREATE OR REPLACE VIEW v_ultima_atualizacao_tabelas AS

        SELECT

            l.tabela_destino
                AS tabela_destino,

            l.data_execucao
                AS ultima_carga,

            l.status
                AS status,

            l.total_linhas
                AS total_linhas

        FROM logs_pipeline l

        JOIN (

            SELECT

                tabela_destino,

                MAX(data_execucao)
                    AS max_data

            FROM logs_pipeline

            GROUP BY tabela_destino

        ) ultimo_log

        ON l.tabela_destino
            = ultimo_log.tabela_destino

        AND l.data_execucao
            = ultimo_log.max_data

        """

    }

    resultados_views = {}

    # --------------------------------------------------------
    # Criar cada view
    # --------------------------------------------------------

    for nome_view, sql in views_sql.items():

        try:

            with engine.begin() as conn:

                conn.exec_driver_sql(sql)

            print(
                f"✅ View '{nome_view}' criada com sucesso!"
            )

            resultados_views[nome_view] = True

        except Exception as e:

            print(
                f"❌ Erro ao criar view "
                f"'{nome_view}':"
            )

            print(e)

            resultados_views[nome_view] = False

    return resultados_views


# ============================================================
# TESTAR AS VIEWS
# ============================================================

def testar_views():

    print(
        "\n================================================"
    )

    print(
        "🧪 TESTANDO VIEWS"
    )

    print(
        "================================================\n"
    )

    resultados = {}

    for view in VIEWS:

        try:

            with engine.connect() as conn:

                resultado = conn.exec_driver_sql(

                    f"""
                    SELECT *
                    FROM `{view}`
                    LIMIT 5
                    """

                )

                linhas = resultado.fetchall()

            print(
                f"✅ {view}: funcionando "
                f"({len(linhas)} linhas retornadas no teste)"
            )

            resultados[view] = True

        except Exception as e:

            print(
                f"❌ {view}: ERRO"
            )

            print(
                f"   {e}"
            )

            resultados[view] = False

    return resultados


# ============================================================
# EXECUÇÃO DO PIPELINE
# ============================================================

if __name__ == "__main__":

    print(
        "\n================================================"
    )

    print(
        "🚀 INICIANDO PIPELINE IBGE → AIVEN MYSQL"
    )

    print(
        "================================================\n"
    )

    # --------------------------------------------------------
    # PREPARAR LOGS
    # --------------------------------------------------------

    if not preparar_logs():

        print(
            "\n❌ Não foi possível preparar "
            "o logs_pipeline."
        )

        exit()

    # --------------------------------------------------------
    # REMOVER VIEWS ANTES DE ATUALIZAR TABELAS
    # --------------------------------------------------------

    if not remover_views():

        print(
            "\n❌ Não foi possível preparar as views."
        )

        exit()

    resultados = {}

    # --------------------------------------------------------
    # REGIÕES
    # --------------------------------------------------------

    resultados['dim_regioes'] = (

        carregar_dados_gerais(

            "https://servicodados.ibge.gov.br/"
            "api/v1/localidades/regioes"
            "?orderBy=nome",

            "dim_regioes"

        )

    )

    # --------------------------------------------------------
    # ESTADOS
    # --------------------------------------------------------

    resultados['dim_estados'] = (

        carregar_dados_gerais(

            "https://servicodados.ibge.gov.br/"
            "api/v1/localidades/estados"
            "?orderBy=nome",

            "dim_estados"

        )

    )

    # --------------------------------------------------------
    # MESORREGIÕES
    # --------------------------------------------------------

    resultados['dim_mesorregioes'] = (

        carregar_dados_gerais(

            "https://servicodados.ibge.gov.br/"
            "api/v1/localidades/mesorregioes"
            "?orderBy=nome",

            "dim_mesorregioes"

        )

    )

    # --------------------------------------------------------
    # MUNICÍPIOS
    # --------------------------------------------------------

    resultados['dim_municipios'] = (

        carregar_dados_gerais(

            "https://servicodados.ibge.gov.br/"
            "api/v1/localidades/municipios",

            "dim_municipios"

        )

    )

    # --------------------------------------------------------
    # PERÍODOS IPP
    # --------------------------------------------------------

    resultados['aux_ipp_periodos'] = (

        carregar_dados_gerais(

            "https://servicodados.ibge.gov.br/"
            "api/v3/agregados/7060/periodos",

            "aux_ipp_periodos"

        )

    )

    # --------------------------------------------------------
    # METADADOS IPP
    # --------------------------------------------------------

    resultados['meta_ipp_descritivo'] = (

        carregar_dados_gerais(

            "https://servicodados.ibge.gov.br/"
            "api/v3/agregados/7060/metadados",

            "meta_ipp_descritivo",

            force_longtext=[

                'variaveis',

                'classificacoes'

            ]

        )

    )

    # --------------------------------------------------------
    # FATO IPCA
    # --------------------------------------------------------

    url_regional = (

        "https://servicodados.ibge.gov.br/"
        "api/v3/agregados/7060/"
        "periodos/202001-202612/"
        "variaveis?localidades=N7"

    )

    resultados['fat_ipca_brasil'] = (

        carregar_fato_ipca_regional(

            url_regional,

            "fat_ipca_brasil"

        )

    )

    # --------------------------------------------------------
    # METADADOS PESQUISAS
    # --------------------------------------------------------

    resultados['meta_pesquisas'] = (

        carregar_dados_gerais(

            "https://servicodados.ibge.gov.br/"
            "api/v2/metadados/pesquisas",

            "meta_pesquisas"

        )

    )

    # --------------------------------------------------------
    # CALENDÁRIO
    # --------------------------------------------------------

    resultados['meta_calendario_geral'] = (

        carregar_dados_gerais(

            "https://servicodados.ibge.gov.br/"
            "api/v3/calendario/"
            "?de=2018-12-20",

            "meta_calendario_geral",

            force_longtext=[

                'items'

            ]

        )

    )

    # ========================================================
    # CRIAR VIEWS
    # ========================================================

    resultados_views = criar_views()

    # ========================================================
    # TESTAR VIEWS
    # ========================================================

    testes_views = testar_views()

    # ========================================================
    # RESUMO DAS TABELAS
    # ========================================================

    print(
        "\n================================================"
    )

    print(
        "📊 RESUMO DA EXECUÇÃO"
    )

    print(
        "================================================\n"
    )

    sucessos = 0
    erros = 0

    for tabela, sucesso in resultados.items():

        if sucesso:

            print(
                f"✅ {tabela}: OK"
            )

            sucessos += 1

        else:

            print(
                f"❌ {tabela}: ERRO"
            )

            erros += 1

    print(
        "\n================================================"
    )

    print(
        f"✅ Tabelas carregadas: {sucessos}"
    )

    print(
        f"❌ Tabelas com erro: {erros}"
    )

    print(
        "================================================"
    )

    # ========================================================
    # RESUMO DAS VIEWS
    # ========================================================

    print(
        "\n================================================"
    )

    print(
        "👁️ RESUMO DAS VIEWS"
    )

    print(
        "================================================\n"
    )

    views_ok = 0
    views_erro = 0

    for view, sucesso in testes_views.items():

        if sucesso:

            print(
                f"✅ {view}: OK"
            )

            views_ok += 1

        else:

            print(
                f"❌ {view}: ERRO"
            )

            views_erro += 1

    print(
        "\n================================================"
    )

    print(
        f"✅ Views funcionando: {views_ok}"
    )

    print(
        f"❌ Views com erro: {views_erro}"
    )

    print(
        "================================================"
    )

    # ========================================================
    # RESULTADO FINAL
    # ========================================================

    if (

        erros == 0

        and views_erro == 0

    ):

        print(
            "\n🎉 PIPELINE FINALIZADA COM SUCESSO!"
        )

        print(
            "✅ IBGE → Aiven → Views → Power BI"
        )

    else:

        print(
            "\n⚠️ PIPELINE FINALIZADA COM ALGUNS ERROS."
        )

        print(
            "Verifique as mensagens acima."
        )