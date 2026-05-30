import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from groq import Groq
from dotenv import load_dotenv
import os
import logging
import sys

sys.path.insert(0, ".")
from tools.data_loader import carregar_dados as carregar_dados_cnpq

load_dotenv()

# ── Configuracao do Log ─────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/operacoes.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

def log_info(operacao, detalhes=""):
    mensagem = f"{operacao}" + (f" | {detalhes}" if detalhes else "")
    logging.info(mensagem)

def log_erro(operacao, erro=""):
    mensagem = f"{operacao}" + (f" | ERRO: {erro}" if erro else "")
    logging.error(mensagem)

# ── Configuracao da pagina ──────────────────────────────────────────
st.set_page_config(page_title="Pesquisadores CNPq", layout="wide")
st.title("Dashboard - Pesquisadores CNPq")

# ── Carrega os dados ─────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def carregar_dados():
    return carregar_dados_cnpq()

df, status_dados, novos, removidos = carregar_dados()

# Filtra apenas pesquisadores ativos para o dashboard
df = df[df["ativo"] == "S"].copy()

# Gravando Log
if status_dados == "cnpq_ok":
    log_info("DASHBOARD INICIADO", f"CNPq disponivel. Dataset atualizado. Total: {len(df)} pesquisadores")

elif status_dados == "cnpq_atualizado":
    st.info(f"ℹ️ Ha {novos} novos pesquisadores e {removidos} removidos desde a ultima atualizacao.")
    log_info("DASHBOARD INICIADO", f"CNPq com mudancas. Novos: {novos}, Removidos: {removidos}")

elif status_dados == "github":
    st.warning("⚠️ Site do CNPq indisponivel. Exibindo dados da ultima atualizacao.")
    log_info("DASHBOARD INICIADO", f"CNPq indisponivel. Dados do GitHub. Total: {len(df)} pesquisadores")

elif status_dados == "erro":
    st.error("❌ Nao foi possivel carregar os dados. Verifique sua conexao.")
    log_erro("DASHBOARD INICIADO", "Falha total ao carregar dados")
    st.stop()

# ── Validacoes do dataset ───────────────────────────────────────────
alertas = []

if len(df) == 0:
    alertas.append("CRITICO: Dataset vazio!")
if len(df) < 100:
    alertas.append(f"ATENCAO: Apenas {len(df)} pesquisadores carregados. Esperado mais de 100.")

colunas_obrigatorias = ["nome", "sexo", "instituicao", "uf", "nivel_bolsa", "situacao"]
for col in colunas_obrigatorias:
    if col not in df.columns:
        alertas.append(f"CRITICO: Coluna '{col}' nao encontrada no dataset!")

if "uf" in df.columns:
    ufs_nulas = df["uf"].isna().sum()
    if ufs_nulas > 0:
        alertas.append(f"ATENCAO: {ufs_nulas} pesquisadores sem UF mapeada.")

if "sexo" in df.columns:
    sexo_indefinido = (df["sexo"] == "Indefinido").sum()
    if sexo_indefinido > 0:
        alertas.append(f"ATENCAO: {sexo_indefinido} pesquisadores com sexo indefinido.")

if alertas:
    for alerta in alertas:
        if "CRITICO" in alerta:
            st.error(alerta)
            log_erro("VALIDACAO DO DATASET", alerta)
        else:
            st.warning(alerta)
            log_info("VALIDACAO DO DATASET", alerta)
else:
    log_info("VALIDACAO DO DATASET", f"Dataset valido com {len(df)} pesquisadores")

if st.button("Atualizar dados"):
    log_info("ATUALIZACAO DE DADOS", "Cache limpo e dados recarregados")
    st.cache_data.clear()
    st.rerun()

st.caption("Total de pesquisadores carregados: " + str(len(df)))
st.divider()

# ── Filtros na barra lateral ────────────────────────────────────────
st.sidebar.header("Filtros")

nivel = st.sidebar.multiselect(
    "Nivel da Bolsa",
    options=sorted(df["nivel_bolsa"].dropna().unique()),
    default=[]
)

uf = st.sidebar.multiselect(
    "UF",
    options=sorted(df["uf"].dropna().unique()),
    default=[]
)

instituicao = st.sidebar.multiselect(
    "Instituicao",
    options=sorted(df["instituicao"].dropna().unique()),
    default=[]
)

sexo = st.sidebar.multiselect(
    "Sexo",
    options=sorted(df["sexo"].dropna().unique()),
    default=[]
)

situacao = st.sidebar.multiselect(
    "Situacao",
    options=sorted(df["situacao"].dropna().unique()),
    default=[]
)

# ── Aplica os filtros ───────────────────────────────────────────────
df_filtrado = df.copy()
if nivel:
    df_filtrado = df_filtrado[df_filtrado["nivel_bolsa"].isin(nivel)]
    log_info("FILTRO APLICADO", f"Nivel: {nivel}")
if uf:
    df_filtrado = df_filtrado[df_filtrado["uf"].isin(uf)]
    log_info("FILTRO APLICADO", f"UF: {uf}")
if instituicao:
    df_filtrado = df_filtrado[df_filtrado["instituicao"].isin(instituicao)]
    log_info("FILTRO APLICADO", f"Instituicao: {instituicao}")
if sexo:
    df_filtrado = df_filtrado[df_filtrado["sexo"].isin(sexo)]
    log_info("FILTRO APLICADO", f"Sexo: {sexo}")
if situacao:
    df_filtrado = df_filtrado[df_filtrado["situacao"].isin(situacao)]
    log_info("FILTRO APLICADO", f"Situacao: {situacao}")

# ── Metricas principais ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Pesquisadores", len(df_filtrado))
col2.metric("Instituicoes", df_filtrado["instituicao"].nunique())
col3.metric("Estados (UF)", df_filtrado["uf"].nunique())
col4.metric("Niveis de Bolsa", df_filtrado["nivel_bolsa"].nunique())

st.divider()

# ── Graficos ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Pesquisadores por Nivel")
    fig1 = px.bar(
        df_filtrado["nivel_bolsa"].value_counts().reset_index(),
        x="nivel_bolsa", y="count",
        labels={"nivel_bolsa": "Nivel", "count": "Quantidade"},
        color="nivel_bolsa"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Pesquisadores por Sexo")
    fig2 = px.pie(
        df_filtrado,
        names="sexo",
        title="Distribuicao por Sexo"
    )
    st.plotly_chart(fig2, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pesquisadores por UF")
    fig3 = px.bar(
        df_filtrado["uf"].value_counts().reset_index(),
        x="uf", y="count",
        labels={"uf": "UF", "count": "Quantidade"},
        color="uf"
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("Pesquisadores por Situacao")
    fig4 = px.pie(
        df_filtrado,
        names="situacao",
        title="Distribuicao por Situacao"
    )
    st.plotly_chart(fig4, use_container_width=True)

st.subheader("Top 10 Instituicoes")
top_inst = df_filtrado["instituicao"].value_counts().head(10).reset_index()
fig5 = px.bar(
    top_inst,
    x="count", y="instituicao",
    orientation="h",
    labels={"instituicao": "Instituicao", "count": "Quantidade"}
)
st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ── Tabela de dados ─────────────────────────────────────────────────
st.subheader("Dados dos Pesquisadores")
colunas_exibir = ["nome", "sexo", "instituicao", "uf", "nivel_bolsa",
                  "area_atuacao", "ano_conclusao_doutorado", "url_lattes",
                  "google_scholar", "situacao"]
st.dataframe(df_filtrado[colunas_exibir], use_container_width=True)

st.divider()

# ── Exportacao ──────────────────────────────────────────────────────
st.subheader("Exportar Dados")

col1, col2 = st.columns(2)

with col1:
    csv = df_filtrado[colunas_exibir].to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    if st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="pesquisadores_cnpq.csv",
        mime="text/csv"
    ):
        log_info("EXPORTACAO CSV", f"Total de registros exportados: {len(df_filtrado)}")

with col2:
    def gerar_pdf(df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Pesquisadores CNPq", ln=True, align="C")
        pdf.ln(5)
        colunas = ["nome", "sexo", "nivel_bolsa", "instituicao", "uf", "situacao"]
        for _, row in df.iterrows():
            linha = " | ".join(str(row[c]) for c in colunas)
            pdf.cell(200, 8, txt=linha[:100], ln=True)
        return bytes(pdf.output())

    pdf_bytes = gerar_pdf(df_filtrado)
    if st.download_button(
        label="Baixar PDF",
        data=pdf_bytes,
        file_name="pesquisadores_cnpq.pdf",
        mime="application/pdf"
    ):
        log_info("EXPORTACAO PDF", f"Total de registros exportados: {len(df_filtrado)}")

# ── Interface de Linguagem Natural ──────────────────────────────────
st.divider()
st.subheader("Consulta em Linguagem Natural")
st.caption("Faca perguntas sobre os dados em portugues. Ex: Quantos pesquisadores do sexo feminino tem na Bahia com nivel PQ-2?")

pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    log_info("CONSULTA LINGUAGEM NATURAL", f"Pergunta: {pergunta}")
    with st.spinner("Analisando..."):
        try:
            from langchain_groq import ChatGroq
            from langchain_experimental.agents import create_pandas_dataframe_agent
            from langchain_core.agents import AgentType

            llm = ChatGroq(
                model="llama-3.1-8b-instant",
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0
            )

            agent = create_pandas_dataframe_agent(
                llm,
                df_filtrado,
                verbose=False,
                agent_type="zero-shot-react-description",
                allow_dangerous_code=True,
                prefix=(
                    "Voce e um assistente que responde perguntas sobre pesquisadores do CNPq. "
                    "Voce tem acesso a um DataFrame pandas chamado 'df' com as colunas: "
                    "nome, sexo, instituicao, uf, nivel_bolsa, area_atuacao, "
                    "ano_conclusao_doutorado, url_lattes, situacao. "
                    "REGRAS OBRIGATORIAS:\n"
                    "1. Responda SEMPRE em portugues.\n"
                    "2. Use o DataFrame para calcular respostas precisas.\n"
                    "3. Cite numeros exatos.\n"
                    "4. Se nao conseguir responder, diga: Nao tenho essa informacao nos dados disponiveis.\n"
                    "5. Seja direto e conciso.\n"
                    "6. Niveis de bolsa usam prefixo PQ-: PQ-1A, PQ-1B, PQ-1C, PQ-1D, PQ-2, PQ-A, PQ-B, PQ-C, PQ-SR.\n"
                    "7. Google Scholar nao esta disponivel no dataset.\n"
                )
            )

            resposta = agent.invoke({"input": pergunta})
            resultado = resposta.get("output", str(resposta))
            st.write("**Resposta:** " + resultado)
            log_info("RESPOSTA GERADA", "Pergunta respondida com sucesso")

        except Exception as e:
            log_erro("ERRO NA CONSULTA", str(e))
            st.error("Ocorreu um erro ao processar sua pergunta. Tente novamente.")

# ── Visualizacao do Log ─────────────────────────────────────────────
st.divider()
st.subheader("Log de Operacoes")

if st.button("Ver Log"):
    try:
        with open("logs/operacoes.log", "r", encoding="utf-8") as f:
            conteudo = f.read()
        if conteudo:
            st.code(conteudo)
        else:
            st.info("Log vazio.")
    except:
        st.warning("Arquivo de log nao encontrado.")