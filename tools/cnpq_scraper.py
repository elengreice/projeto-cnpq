import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

URL = (
    "http://plsql1.cnpq.br/divulg/RESULTADO_PQ_102003.prc_comp_cmt_links"
    "?V_COD_DEMANDA=200310&V_TPO_RESULT=CURSO"
    "&V_COD_AREA_CONHEC=10300007&V_COD_CMT_ASSESSOR=CC"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def scrape_cnpq():
    print("🔍 Acessando o site do CNPq...")
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.encoding = "latin-1"

    print(f"✅ Status da requisição: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Procura todas as tabelas na página
    tabelas = soup.find_all("table")
    print(f"📋 Total de tabelas encontradas: {len(tabelas)}")

    pesquisadores = []

    for i, tabela in enumerate(tabelas):
        linhas = tabela.find_all("tr")
        print(f"   Tabela {i+1}: {len(linhas)} linhas")
        
        for linha in linhas:
            colunas = linha.find_all("td")
            if len(colunas) >= 6:
                nome = colunas[0].text.strip()
                nivel = colunas[1].text.strip()
                
                # Filtra linhas que parecem cabeçalho ou vazias
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
    
    # Remove duplicatas caso existam
    df = df.drop_duplicates(subset=["nome"])
    
    print(f"\n✅ {len(df)} pesquisadores encontrados!")
    print(df.head(10))

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/dataset.csv", index=False, encoding="utf-8-sig")
    print("💾 Dataset salvo em data/dataset.csv")

    return df

if __name__ == "__main__":
    scrape_cnpq()