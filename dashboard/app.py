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
st.caption("Faca perguntas sobre os dados em portugues. Ex: Quantos pesquisadores sao da USP?")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    log_info("CONSULTA LINGUAGEM NATURAL", f"Pergunta: {pergunta}")
    with st.spinner("Analisando..."):
        try:
            total       = str(len(df_filtrado))
            inst_top    = df_filtrado["instituicao"].value_counts().head(5).to_string()
            niveis      = df_filtrado["nivel_bolsa"].value_counts().to_string()
            situacoes   = df_filtrado["situacao"].value_counts().to_string()
            ufs         = df_filtrado["uf"].value_counts().to_string()
            sexos       = df_filtrado["sexo"].value_counts().to_string()
            exemplos = df_filtrado[["nome", "sexo", "uf", "instituicao", "nivel_bolsa"]].head(10).to_string()

            sexo_uf = df_filtrado.groupby(["uf","sexo"]).size().unstack(fill_value=0)
            sexo_uf.columns = [str(c) for c in sexo_uf.columns]
            if "Feminino" not in sexo_uf.columns:
                sexo_uf["Feminino"] = 0
            if "Masculino" not in sexo_uf.columns:
                sexo_uf["Masculino"] = 0
            sexo_uf["Total"] = sexo_uf["Feminino"] + sexo_uf["Masculino"]
            sexo_uf = sexo_uf.sort_values("Feminino", ascending=False)

            uf_mais_feminino = sexo_uf.index[0]
            qtd_mais_feminino = int(sexo_uf["Feminino"].iloc[0])
            uf_mais_masculino = sexo_uf.sort_values("Masculino", ascending=False).index[0]
            qtd_mais_masculino = int(sexo_uf.sort_values("Masculino", ascending=False)["Masculino"].iloc[0])
            ufs_sem_feminino = sexo_uf[sexo_uf["Feminino"] == 0].index.tolist()

            sexo_por_uf = (
                "Tabela completa (UF | Feminino | Masculino | Total):\n" +
                sexo_uf[["Feminino","Masculino","Total"]].to_string() +
                f"\n\nRESUMO PRE-CALCULADO (use estes valores nas respostas):\n"
                f"- UF com MAIS pesquisadoras femininas: {uf_mais_feminino} com {qtd_mais_feminino} mulheres\n"
                f"- UF com MAIS pesquisadores masculinos: {uf_mais_masculino} com {qtd_mais_masculino} homens\n"
                f"- UFs SEM pesquisadoras femininas: {ufs_sem_feminino}\n"
                f"- Top 3 UFs com mais mulheres: {sexo_uf['Feminino'].head(3).to_dict()}\n"
            )

            sistema = (
                "Voce e um assistente especializado em analise de dados de pesquisadores bolsistas do CNPq. "
                "Seu papel e responder perguntas EXCLUSIVAMENTE com base nos dados fornecidos abaixo. "
                "REGRAS OBRIGATORIAS:\n"
                "1. Responda APENAS com base nos dados fornecidos neste prompt. NUNCA invente ou assuma informacoes.\n"
                "2. Se a pergunta nao puder ser respondida pelos dados disponiveis, responda EXATAMENTE: Nao tenho essa informacao nos dados disponiveis.\n"
                "3. Sempre cite numeros EXATOS dos dados fornecidos. NUNCA arredonde ou estime.\n"
                "4. Responda SEMPRE em portugues, independente do idioma da pergunta.\n"
                "5. Nao responda perguntas que nao sejam relacionadas aos pesquisadores do CNPq.\n"
                "6. Se a pergunta for ambigua, explique o que foi interpretado antes de responder.\n"
                "7. NUNCA faca suposicoes ou interpretacoes sobre os dados. Use apenas os numeros exatos.\n"
                "8. Quando citar pesquisadores especificos, use o nome exatamente como consta nos dados.\n"
                "9. Se perguntado sobre Google Scholar, informe que esse dado nao esta disponivel no dataset.\n"
                "10. Seja DIRETO e CONCISO. Responda em no maximo 5 linhas.\n"
                "11. Para perguntas sobre rankings (maior, menor, mais, menos), cite apenas o top 3 com numeros exatos.\n"
                "12. NUNCA use linguagem de incerteza como 'pode ser', 'talvez', 'provavelmente', 'parece que'.\n"
                "13. Se os dados mostrarem um numero exato, cite esse numero. Ex: SP tem 18 pesquisadoras.\n"
                "14. Para perguntas sobre sexo por UF, use APENAS os numeros da tabela Distribuicao de sexo por UF.\n"
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
                "Distribuicao de sexo por UF:\n" + sexo_por_uf + "\n\n"
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