import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
from groq import Groq
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

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

# ── Carrega os dados do CSV no GitHub ───────────────────────────────
@st.cache_data(ttl=3600)
def carregar_dados():
    url_csv = "https://raw.githubusercontent.com/elengreice/projeto-cnpq/main/data/dataset.csv"
    df = pd.read_csv(url_csv)
    return df

df = carregar_dados()
log_info("DASHBOARD INICIADO", f"Total de pesquisadores carregados: {len(df)}")

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
st.caption("Faca perguntas sobre os dados em portugues. Ex: Quantos pesquisadores sao da USP?")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    log_info("CONSULTA LINGUAGEM NATURAL", f"Pergunta: {pergunta}")
    with st.spinner("Analisando..."):
        try:
            total = str(len(df_filtrado))
            inst_top = df_filtrado["instituicao"].value_counts().head(5).to_string()
            niveis = df_filtrado["nivel_bolsa"].value_counts().to_string()
            situacoes = df_filtrado["situacao"].value_counts().to_string()
            ufs = df_filtrado["uf"].value_counts().to_string()
            sexos = df_filtrado["sexo"].value_counts().to_string()
            exemplos = df_filtrado[colunas_exibir].head(20).to_string()

            sistema = (
                "Voce e um assistente especializado em analise de dados de pesquisadores bolsistas do CNPq. "
                "Seu papel e responder perguntas EXCLUSIVAMENTE com base nos dados fornecidos abaixo. "
                "\n\nREGRAS OBRIGATORIAS:\n"
                "1. Responda APENAS com base nos dados fornecidos neste prompt. NUNCA invente ou assuma informacoes.\n"
                "2. Se a pergunta nao puder ser respondida pelos dados disponiveis, responda EXATAMENTE: Nao tenho essa informacao nos dados disponiveis.\n"
                "3. Sempre cite numeros e estatisticas concretas quando disponiveis.\n"
                "4. Responda SEMPRE em portugues, independente do idioma da pergunta.\n"
                "5. Nao responda perguntas que nao sejam relacionadas aos pesquisadores do CNPq.\n"
                "6. Se a pergunta for ambigua, explique o que foi interpretado antes de responder.\n"
                "7. Nao faca suposicoes sobre dados que nao estao presentes no dataset.\n"
                "8. Quando citar pesquisadores especificos, use o nome exatamente como consta nos dados.\n"
                "9. Se perguntado sobre Google Scholar, informe que esse dado nao esta disponivel no dataset.\n"
                "10. Seja objetivo e direto. Evite respostas longas e desnecessarias.\n"
                "\nDADOS DISPONIVEIS:\n"
                "Total de pesquisadores: " + total + "\n"
                "Colunas disponiveis: nome, sexo, instituicao, uf, nivel_bolsa, area_atuacao, "
                "ano_conclusao_doutorado, url_lattes, situacao, formacao_academica, pos_doutorado.\n"
                "ATENCAO: Google Scholar NAO esta disponivel no dataset.\n\n"
                "Top 5 instituicoes:\n" + inst_top + "\n\n"
                "Distribuicao por nivel de bolsa:\n" + niveis + "\n\n"
                "Distribuicao por situacao:\n" + situacoes + "\n\n"
                "Distribuicao por UF:\n" + ufs + "\n\n"
                "Distribuicao por sexo:\n" + sexos + "\n\n"
                "Exemplos dos dados (primeiros 20 registros):\n" + exemplos
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
            log_info("RESPOSTA GERADA", "Pergunta respondida com sucesso")

        except Exception as e:
            log_erro("ERRO NA CONSULTA", str(e))
            st.error("Ocorreu um erro ao processar sua pergunta. Tente novamente.")