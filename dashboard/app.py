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

# ── Configuracao da pagina ──────────────────────────────────────────
st.set_page_config(page_title="Pesquisadores CNPq", layout="wide")
st.title("Dashboard - Pesquisadores CNPq")

# ── Carrega os dados do CSV no GitHub ───────────────────────────────
@st.cache_data(ttl=3600)
def carregar_dados():
    url_csv = "https://raw.githubusercontent.com/elengreice/projeto-cnpq/main/data/dataset.csv"
    df = pd.read_csv(url_csv)
    return df

df = carregar_dados()

if st.button("Atualizar dados"):
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
if uf:
    df_filtrado = df_filtrado[df_filtrado["uf"].isin(uf)]
if instituicao:
    df_filtrado = df_filtrado[df_filtrado["instituicao"].isin(instituicao)]
if sexo:
    df_filtrado = df_filtrado[df_filtrado["sexo"].isin(sexo)]
if situacao:
    df_filtrado = df_filtrado[df_filtrado["situacao"].isin(situacao)]

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
                  "area_atuacao", "ano_conclusao_doutorado", "url",
                  "google_scholar", "situacao"]
st.dataframe(df_filtrado[colunas_exibir], use_container_width=True)

st.divider()

# ── Exportacao ──────────────────────────────────────────────────────
st.subheader("Exportar Dados")

col1, col2 = st.columns(2)

with col1:
    csv = df_filtrado[colunas_exibir].to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
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
        colunas = ["nome", "sexo", "nivel_bolsa", "instituicao", "uf", "situacao"]
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
st.caption("Faca perguntas sobre os dados em portugues. Ex: Quantos pesquisadores sao da Bahia?")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    with st.spinner("Analisando..."):

        total = str(len(df_filtrado))
        inst_top = df_filtrado["instituicao"].value_counts().head(5).to_string()
        niveis = df_filtrado["nivel_bolsa"].value_counts().to_string()
        situacoes = df_filtrado["situacao"].value_counts().to_string()
        ufs = df_filtrado["uf"].value_counts().to_string()
        sexos = df_filtrado["sexo"].value_counts().to_string()
        exemplos = df_filtrado[colunas_exibir].head(20).to_string()

        sistema = (
            "Voce e um assistente que responde perguntas sobre pesquisadores do CNPq. "
            "Os dados tem " + total + " pesquisadores com as colunas: "
            "nome, sexo, instituicao, uf, nivel_bolsa, area_atuacao, ano_conclusao_doutorado, url, google_scholar, situacao. "
            "Exemplos dos dados: " + exemplos + " "
            "Estatisticas: Instituicoes: " + inst_top + " Niveis: " + niveis +
            " Situacoes: " + situacoes + " UFs: " + ufs + " Sexos: " + sexos + " "
            "Responda em portugues de forma clara e objetiva."
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": pergunta}
            ]
        )

        resposta = response.choices[0].message.content
        st.write("**Resposta:** " + resposta)