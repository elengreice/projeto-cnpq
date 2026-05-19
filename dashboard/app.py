import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# ── Configuração da página ──────────────────────────────────────────
st.set_page_config(page_title="Pesquisadores CNPq", layout="wide")
st.title("Dashboard - Pesquisadores CNPq")

# ── Função que busca os dados direto do CNPq ────────────────────────
@st.cache_data(ttl=3600)
def carregar_dados():
    URL = (
        "http://plsql1.cnpq.br/divulg/RESULTADO_PQ_102003.prc_comp_cmt_links"
        "?V_COD_DEMANDA=200310&V_TPO_RESULT=CURSO"
        "&V_COD_AREA_CONHEC=10300007&V_COD_CMT_ASSESSOR=CC"
    )
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    with st.spinner("Buscando dados do CNPq..."):
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.encoding = "latin-1"
        soup = BeautifulSoup(response.text, "html.parser")

        tabelas = soup.find_all("table")
        pesquisadores = []

        for tabela in tabelas:
            linhas = tabela.find_all("tr")
            for linha in linhas:
                colunas = linha.find_all("td")
                if len(colunas) >= 6:
                    nome = colunas[0].text.strip()
                    nivel = colunas[1].text.strip()
                    if nome and nivel and nome.upper() != "NOME":
                        pesquisadores.append({
                            "nome":             nome,
                            "nivel":            nivel,
                            "vigencia_inicio":  colunas[2].text.strip(),
                            "vigencia_termino": colunas[3].text.strip(),
                            "instituicao":      colunas[4].text.strip(),
                            "situacao":         colunas[5].text.strip(),
                        })

        df = pd.DataFrame(pesquisadores)
        df = df.drop_duplicates(subset=["nome"])
        return df

# ── Carrega os dados ────────────────────────────────────────────────
df = carregar_dados()

if st.button("Atualizar dados do CNPq"):
    st.cache_data.clear()
    st.rerun()

st.caption("Total de pesquisadores carregados: " + str(len(df)))
st.divider()

# ── Filtros na barra lateral ────────────────────────────────────────
st.sidebar.header("Filtros")

nivel = st.sidebar.multiselect(
    "Nivel da Bolsa",
    options=sorted(df["nivel"].dropna().unique()),
    default=[]
)

instituicao = st.sidebar.multiselect(
    "Instituicao",
    options=sorted(df["instituicao"].dropna().unique()),
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
    df_filtrado = df_filtrado[df_filtrado["nivel"].isin(nivel)]
if instituicao:
    df_filtrado = df_filtrado[df_filtrado["instituicao"].isin(instituicao)]
if situacao:
    df_filtrado = df_filtrado[df_filtrado["situacao"].isin(situacao)]

# ── Metricas principais ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total de Pesquisadores", len(df_filtrado))
col2.metric("Instituicoes", df_filtrado["instituicao"].nunique())
col3.metric("Niveis de Bolsa", df_filtrado["nivel"].nunique())

st.divider()

# ── Graficos ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Pesquisadores por Nivel")
    fig1 = px.bar(
        df_filtrado["nivel"].value_counts().reset_index(),
        x="nivel", y="count",
        labels={"nivel": "Nivel", "count": "Quantidade"},
        color="nivel"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Pesquisadores por Situacao")
    fig2 = px.pie(
        df_filtrado,
        names="situacao",
        title="Distribuicao por Situacao"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Top 10 Instituicoes")
top_inst = df_filtrado["instituicao"].value_counts().head(10).reset_index()
fig3 = px.bar(
    top_inst,
    x="count", y="instituicao",
    orientation="h",
    labels={"instituicao": "Instituicao", "count": "Quantidade"}
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Tabela de dados ─────────────────────────────────────────────────
st.subheader("Dados dos Pesquisadores")
st.dataframe(df_filtrado, use_container_width=True)

# ── Exportacao ──────────────────────────────────────────────────────
st.subheader("Exportar Dados")

col1, col2 = st.columns(2)

with col1:
    csv = df_filtrado.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="pesquisadores_cnpq.csv",
        mime="text/csv"
    )

with col2:
    def gerar_pdf(df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Pesquisadores CNPq", ln=True, align="C")
        pdf.ln(5)
        colunas = ["nome", "nivel", "instituicao", "situacao"]
        for _, row in df.iterrows():
            linha = " | ".join(str(row[c]) for c in colunas)
            pdf.cell(200, 8, txt=linha[:100], ln=True)
        return bytes(pdf.output())

    pdf_bytes = gerar_pdf(df_filtrado)
    st.download_button(
        label="Baixar PDF",
        data=pdf_bytes,
        file_name="pesquisadores_cnpq.pdf",
        mime="application/pdf"
    )

# ── Interface de Linguagem Natural ──────────────────────────────────
st.divider()
st.subheader("Consulta em Linguagem Natural")
st.caption("Faca perguntas sobre os dados em portugues. Ex: Quantos pesquisadores sao da USP?")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    with st.spinner("Analisando..."):

        total = str(len(df_filtrado))
        inst_top = df_filtrado["instituicao"].value_counts().head(5).to_string()
        niveis = df_filtrado["nivel"].value_counts().to_string()
        situacoes = df_filtrado["situacao"].value_counts().to_string()
        exemplos = df_filtrado.head(20).to_string()

        sistema = (
            "Voce e um assistente que responde perguntas sobre pesquisadores do CNPq. "
            "Os dados tem " + total + " pesquisadores com as colunas: "
            "nome, nivel, vigencia_inicio, vigencia_termino, instituicao, situacao. "
            "Exemplos dos dados: " + exemplos + " "
            "Estatisticas: Instituicoes: " + inst_top + " Niveis: " + niveis + " Situacoes: " + situacoes + " "
            "Responda em portugues de forma clara e objetiva."
        )

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": pergunta}
            ]
        )

        resposta = response.choices[0].message.content
        st.write("**Resposta:** " + resposta)