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

            # ── Estatisticas pre-calculadas para o Query Agent ──────────────────
            total = str(len(df_filtrado))
            inst_top = df_filtrado["instituicao"].value_counts().head(5).to_string()
            niveis = df_filtrado["nivel_bolsa"].value_counts().to_string()
            situacoes = df_filtrado["situacao"].value_counts().to_string()
            exemplos = df_filtrado[["nome", "sexo", "uf", "instituicao", "nivel_bolsa"]].head(10).to_string()

            # Sexo por UF
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
                f"\n\nRESUMO PRE-CALCULADO:\n"
                f"- UF com MAIS pesquisadoras femininas: {uf_mais_feminino} com {qtd_mais_feminino} mulheres\n"
                f"- UF com MAIS pesquisadores masculinos: {uf_mais_masculino} com {qtd_mais_masculino} homens\n"
                f"- UFs SEM pesquisadoras femininas: {ufs_sem_feminino}\n"
                f"- Top 3 UFs com mais mulheres: {sexo_uf['Feminino'].head(3).to_dict()}\n"
            )

            # UF rankings
            uf_counts = df_filtrado["uf"].value_counts()
            ufs = uf_counts.to_string()
            uf_mais_pesquisadores = uf_counts.index[0]
            qtd_uf_mais = int(uf_counts.iloc[0])
            uf_menos_pesquisadores = uf_counts.index[-1]
            qtd_uf_menos = int(uf_counts.iloc[-1])
            resumo_ufs = (
                f"Distribuicao por UF (maior para menor):\n{ufs}\n\n"
                f"RESUMO PRE-CALCULADO:\n"
                f"- UF com MAIS pesquisadores: {uf_mais_pesquisadores} com {qtd_uf_mais}\n"
                f"- UF com MENOS pesquisadores: {uf_menos_pesquisadores} com {qtd_uf_menos}\n"
                f"- Top 3 com mais: {uf_counts.head(3).to_dict()}\n"
                f"- Top 3 com menos: {uf_counts.tail(3).to_dict()}\n"
            )

            # Situacao por UF
            sit_uf = df_filtrado.groupby(["uf","situacao"]).size().reset_index(name="total")
            sit_uf_resumo = sit_uf.sort_values("total", ascending=False)
            ufs_por_situacao = {}
            for sit in df_filtrado["situacao"].unique():
                ufs = sit_uf[sit_uf["situacao"] == sit].sort_values("total", ascending=False)
                if len(ufs) > 0:
                    ufs_por_situacao[sit] = ufs[["uf","total"]].head(5).to_string()
            situacao_por_uf_str = (
                "Distribuicao de situacao por UF:\n" +
                sit_uf_resumo.to_string() +
                "\n\nRESUMO PRE-CALCULADO por situacao:\n" +
                "\n".join([f"- {sit}:\n{dados}" for sit, dados in ufs_por_situacao.items()])
            )

            # Nivel por UF com resumo direto e UFs sem cada nivel
            nivel_uf = df_filtrado.groupby(["uf","nivel_bolsa"]).size().reset_index(name="total")
            todas_ufs = set(df_filtrado["uf"].unique())

            resumo_nivel_uf_linhas = []
            for nivel in sorted(df_filtrado["nivel_bolsa"].unique()):
                dados = nivel_uf[nivel_uf["nivel_bolsa"] == nivel].sort_values("total", ascending=False)
                ufs_com_nivel = set(dados["uf"].tolist())
                ufs_sem_nivel = sorted(todas_ufs - ufs_com_nivel)
                if len(dados) > 0:
                    top3 = ", ".join([f"{row['uf']}({int(row['total'])})" for _, row in dados.head(3).iterrows()])
                    resumo_nivel_uf_linhas.append(
                        f"- {nivel}: top 3 UFs = {top3} | UFs SEM esse nivel = {ufs_sem_nivel if ufs_sem_nivel else 'nenhuma'}"
                    )

            nivel_por_uf_str = (
                "RANKING DE UFs POR NIVEL DE BOLSA (formato: UF(quantidade)):\n" +
                "\n".join(resumo_nivel_uf_linhas)
            )

            # Sexo por nivel
            sexo_nivel = df_filtrado.groupby(["nivel_bolsa","sexo"]).size().unstack(fill_value=0)
            sexo_nivel.columns = [str(c) for c in sexo_nivel.columns]
            if "Feminino" not in sexo_nivel.columns:
                sexo_nivel["Feminino"] = 0
            if "Masculino" not in sexo_nivel.columns:
                sexo_nivel["Masculino"] = 0
            sexo_nivel["Total"] = sexo_nivel["Feminino"] + sexo_nivel["Masculino"]
            sexo_por_nivel_str = (
                "Distribuicao de sexo por nivel de bolsa:\n" +
                sexo_nivel[["Feminino","Masculino","Total"]].to_string()
            )

            # Instituicao rankings
            inst_counts = df_filtrado["instituicao"].value_counts()
            inst_mais = inst_counts.index[0]
            qtd_inst_mais = int(inst_counts.iloc[0])
            inst_menos = inst_counts.index[-1]
            qtd_inst_menos = int(inst_counts.iloc[-1])
            resumo_inst = (
                f"Top 10 instituicoes:\n{inst_counts.head(10).to_string()}\n\n"
                f"RESUMO PRE-CALCULADO:\n"
                f"- Instituicao com MAIS pesquisadores: {inst_mais} com {qtd_inst_mais}\n"
                f"- Instituicao com MENOS pesquisadores: {inst_menos} com {qtd_inst_menos}\n"
            )

            sistema = (
                "Voce e um assistente especializado em analise de dados de pesquisadores bolsistas do CNPq. "
                "Seu papel e responder perguntas EXCLUSIVAMENTE com base nos dados fornecidos abaixo. "
                "\n\nREGRAS OBRIGATORIAS:\n"
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
                "11. Para perguntas sobre rankings, cite apenas o top 3 com numeros exatos.\n"
                "12. NUNCA use linguagem de incerteza como 'pode ser', 'talvez', 'provavelmente'.\n"
                "13. Se os dados mostrarem um numero exato, cite esse numero.\n"
                "14. Para cruzamentos de dados, use APENAS as tabelas pre-calculadas fornecidas.\n"
                "15. Os niveis de bolsa no dataset usam o prefixo PQ-. Exemplos: PQ-1A, PQ-1B, PQ-1C, PQ-1D, PQ-2, PQ-A, PQ-B, PQ-C, PQ-SR. Quando o usuario perguntar sobre nivel '1A', interprete como 'PQ-1A'.\n"
                "\nDADOS DISPONIVEIS:\n"
                "Total de pesquisadores: " + total + "\n"
                "Colunas: nome, sexo, instituicao, uf, nivel_bolsa, area_atuacao, ano_conclusao_doutorado, url_lattes, situacao.\n"
                "ATENCAO: Google Scholar NAO esta disponivel.\n\n"
                "Top 5 instituicoes:\n" + inst_top + "\n\n" +
                resumo_inst + "\n\n" +
                "Distribuicao por nivel:\n" + niveis + "\n\n" +
                "Distribuicao por situacao:\n" + situacoes + "\n\n" +
                resumo_ufs + "\n\n" +
                sexo_por_uf + "\n\n" +
                situacao_por_uf_str + "\n\n" +
                nivel_por_uf_str + "\n\n" +
                sexo_por_nivel_str + "\n\n" +
                "Exemplos dos dados:\n" + exemplos
            )

            print(f"Tamanho do contexto: {len(sistema)} caracteres")
            print(f"Tokens aproximados: {len(sistema)//4}")

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