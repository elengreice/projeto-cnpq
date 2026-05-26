import requests
import pandas as pd
from bs4 import BeautifulSoup

URL_GITHUB = "https://raw.githubusercontent.com/elengreice/projeto-cnpq/main/data/dataset.csv"
URL_CNPQ = (
    "http://plsql1.cnpq.br/divulg/RESULTADO_PQ_102003.prc_comp_cmt_links"
    "?V_COD_DEMANDA=200310&V_TPO_RESULT=CURSO"
    "&V_COD_AREA_CONHEC=10300007&V_COD_CMT_ASSESSOR=CC"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def carregar_dados():
    # Carrega o dataset completo do GitHub (com todos os campos)
    try:
        df_completo = pd.read_csv(URL_GITHUB)
    except:
        try:
            df_completo = pd.read_csv("data/dataset.csv")
        except:
            return None, "erro", 0, 0

    # Verifica se o CNPq esta disponivel e se ha novos pesquisadores
    try:
        response = requests.get(URL_CNPQ, headers=HEADERS, timeout=15)
        response.encoding = "latin-1"
        soup = BeautifulSoup(response.text, "html.parser")
        tabelas = soup.find_all("table")
        nomes_cnpq = []
        for tabela in tabelas:
            linhas = tabela.find_all("tr")
            for linha in linhas:
                colunas = linha.find_all("td")
                if len(colunas) >= 6:
                    nome = colunas[0].text.strip()
                    nivel = colunas[1].text.strip()
                    if nome and nivel and nome.upper() != "NOME":
                        nomes_cnpq.append(nome)

        if len(nomes_cnpq) > 10:
            novos = set(nomes_cnpq) - set(df_completo["nome"].tolist())
            removidos = set(df_completo["nome"].tolist()) - set(nomes_cnpq)
            if novos or removidos:
                return df_completo, "cnpq_atualizado", len(novos), len(removidos)
            return df_completo, "cnpq_ok", 0, 0
    except:
        return df_completo, "github", 0, 0