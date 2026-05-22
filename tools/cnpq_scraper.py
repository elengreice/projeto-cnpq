import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import gender_guesser.detector as gender

URL = (
    "http://plsql1.cnpq.br/divulg/RESULTADO_PQ_102003.prc_comp_cmt_links"
    "?V_COD_DEMANDA=200310&V_TPO_RESULT=CURSO"
    "&V_COD_AREA_CONHEC=10300007&V_COD_CMT_ASSESSOR=CC"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Mapeamento de siglas de instituicoes para UF
INSTITUICAO_UF = {
    "UFAM": "AM", "UEA": "AM",
    "UFPA": "PA", "UEPA": "PA", "UNIFESSPA": "PA",
    "UFMA": "MA", "UEMA": "MA",
    "UFC": "CE", "UECE": "CE", "URCA": "CE", "IFCE": "CE",
    "UFPI": "PI", "UESPI": "PI",
    "UFPB": "PB", "UEPB": "PB",
    "UFPE": "PE", "UPE": "PE", "UFRPE": "PE",
    "UFRN": "RN", "UERN": "RN",
    "UFAL": "AL", "UNEAL": "AL",
    "UFS": "SE", "UNIT": "SE",
    "UFBA": "BA", "UEFS": "BA", "UESC": "BA", "UESB": "BA", "UNEB": "BA",
    "UFMG": "MG", "UFJF": "MG", "UFV": "MG", "UFTM": "MG", "UFLA": "MG",
    "UNIMONTES": "MG", "CEFET/MG": "MG", "CEFETMG": "MG", "PUC MINAS": "MG",
    "PUC/MG": "MG", "UFOP": "MG", "UFU": "MG", "UFSJ": "MG",
    "UFRJ": "RJ", "UFF": "RJ", "UERJ": "RJ", "PUC-RIO": "RJ",
    "UNIRIO": "RJ", "CEFET/RJ": "RJ", "LNCC": "RJ", "FGV": "RJ",
    "IME": "RJ", "IMPA": "RJ",
    "USP": "SP", "UNICAMP": "SP", "UNESP": "SP", "UNIFESP": "SP",
    "UFSCAR": "SP", "UFSCar": "SP", "ITA": "SP", "UFABC": "SP",
    "UFPR": "PR", "UEL": "PR", "UEM": "PR", "UTFPR": "PR",
    "PUC/PR": "PR", "PUCPR": "PR", "PUC-PR": "PR",
    "UFSC": "SC", "UDESC": "SC", "UNIVALI": "SC",
    "UFRGS": "RS", "PUCRS": "RS", "UNISINOS": "RS", "UCS": "RS",
    "UFG": "GO", "PUC-GO": "GO",
    "UFMT": "MT", "UNEMAT": "MT",
    "UFMS": "MS", "UEMS": "MS",
    "UnB": "DF", "UCB": "DF",
    "UFAC": "AC",
    "UFRR": "RR",
    "UNIFAP": "AP",
    "UFRO": "RO",
    "UFT": "TO",
    "UFES": "ES", "UFVJM": "MG",
    "UNIJUI": "RS", "FURG": "RS", "UNIPAMPA": "RS",
    "ITV": "PA",
    "INMETRO": "RJ",
    "UNIFOR": "CE",
    "IBU": "PR",
    "UFDPAR": "PI", "UFDPar": "PI",
    "MACKENZIE": "SP", "FEI": "SP",
}

def inferir_uf(instituicao):
    inst_upper = instituicao.upper()
    for sigla, uf in INSTITUICAO_UF.items():
        if sigla.upper() in inst_upper:
            return uf
    return "N/A"

def inferir_sexo(nome):
    d = gender.Detector()
    primeiro_nome = nome.strip().split()[0].capitalize()
    resultado = d.get_gender(primeiro_nome)
    mapa = {
        "male": "Masculino",
        "female": "Feminino",
        "mostly_male": "Masculino",
        "mostly_female": "Feminino",
        "andy": "Indefinido",
        "unknown": "Indefinido"
    }
    return mapa.get(resultado, "Indefinido")

def montar_url(nome):
    nome_formatado = nome.strip().replace(" ", "+")
    return f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&termo={nome_formatado}"

def scrape_cnpq():
    print("Acessando o site do CNPq...")
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.encoding = "latin-1"

    print(f"Status da requisicao: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    tabelas = soup.find_all("table")
    print(f"Total de tabelas encontradas: {len(tabelas)}")

    pesquisadores = []

    for tabela in tabelas:
        linhas = tabela.find_all("tr")
        for linha in linhas:
            colunas = linha.find_all("td")
            if len(colunas) >= 6:
                nome = colunas[0].text.strip()
                nivel = colunas[1].text.strip()
                if nome and nivel and nome.upper() != "NOME":
                    instituicao = colunas[4].text.strip()
                    pesquisadores.append({
                        "nome":                      nome,
                        "sexo":                      inferir_sexo(nome),
                        "instituicao":               instituicao,
                        "uf":                        inferir_uf(instituicao),
                        "nivel_bolsa":               nivel,
                        "area_atuacao":              "Ciencia da Computacao",
                        "ano_conclusao_doutorado":   "N/A",
                        "url":                       montar_url(nome),
                        "google_scholar":             "N/A",
                        "vigencia_inicio":            colunas[2].text.strip(),
                        "vigencia_termino":           colunas[3].text.strip(),
                        "situacao":                  colunas[5].text.strip(),
                    })

    df = pd.DataFrame(pesquisadores)
    df = df.drop_duplicates(subset=["nome"])

    print(f"{len(df)} pesquisadores encontrados!")
    print(df.head(5))

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/dataset.csv", index=False, encoding="utf-8-sig")
    print("Dataset salvo em data/dataset.csv")

    return df

if __name__ == "__main__":
    scrape_cnpq()