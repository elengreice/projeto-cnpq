import requests
import pandas as pd
from bs4 import BeautifulSoup
import gender_guesser.detector as gender

URL_GITHUB = "https://raw.githubusercontent.com/elengreice/projeto-cnpq/main/data/dataset.csv"
URL_CNPQ = (
    "http://plsql1.cnpq.br/divulg/RESULTADO_PQ_102003.prc_comp_cmt_links"
    "?V_COD_DEMANDA=200310&V_TPO_RESULT=CURSO"
    "&V_COD_AREA_CONHEC=10300007&V_COD_CMT_ASSESSOR=CC"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

INSTITUICAO_UF = {
    "UFAM": "AM", "UEA": "AM", "UFPA": "PA", "UEPA": "PA",
    "UFMA": "MA", "UEMA": "MA", "UFC": "CE", "UECE": "CE",
    "URCA": "CE", "IFCE": "CE", "UFPI": "PI", "UESPI": "PI",
    "UFPB": "PB", "UEPB": "PB", "UFPE": "PE", "UPE": "PE",
    "UFRPE": "PE", "UFRN": "RN", "UERN": "RN", "UFAL": "AL",
    "UFS": "SE", "UFBA": "BA", "UEFS": "BA", "UESC": "BA",
    "UESB": "BA", "UNEB": "BA", "UFMG": "MG", "UFJF": "MG",
    "UFV": "MG", "UFOP": "MG", "UFU": "MG", "CEFET/MG": "MG",
    "PUC MINAS": "MG", "UFRJ": "RJ", "UFF": "RJ", "UERJ": "RJ",
    "PUC-RIO": "RJ", "UNIRIO": "RJ", "CEFET/RJ": "RJ", "LNCC": "RJ",
    "FGV": "RJ", "USP": "SP", "UNICAMP": "SP", "UNESP": "SP",
    "UNIFESP": "SP", "UFSCar": "SP", "ITA": "SP", "UFABC": "SP",
    "MACKENZIE": "SP", "FEI": "SP", "UFPR": "PR", "UEL": "PR",
    "UEM": "PR", "UTFPR": "PR", "PUC/PR": "PR", "UFSC": "SC",
    "UDESC": "SC", "UFRGS": "RS", "PUCRS": "RS", "UNISINOS": "RS",
    "FURG": "RS", "UNIJUI": "RS", "UNIPAMPA": "RS", "UFG": "GO",
    "UFMT": "MT", "UFMS": "MS", "UnB": "DF", "UFES": "ES",
    "UFAC": "AC", "UFRR": "RR", "UNIFAP": "AP", "UFRO": "RO",
    "UFT": "TO", "ITV": "PA", "INMETRO": "RJ", "UNIFOR": "CE",
    "UFDPAR": "PI", "UFDPar": "PI",
}

NOMES_MASCULINOS = [
    "Adenilso", "Adenilton", "Adiel", "Ajalmar", "Aldri", "Alneu",
    "Altigran", "Aluizio", "Amauri", "Anisio", "Aristofanes", "Baldoino",
    "Breno", "Carlile", "Celio", "Cleber", "Clodoveu", "Dalcimar",
    "Danielo", "Davi", "Divanilson", "Dorgival", "Edelberto", "Edleno",
    "Erickson", "Ermeson", "Estevao", "Fabio", "Fabricio", "Fabrizzio",
    "Gilson", "Gladston", "Gleison", "Heder", "Jaelson", "Jamilson",
    "Javam", "Jeferson", "Joao", "Jomi", "Jurandir", "Jurandy",
    "Kleinner", "Lehilton", "Leobino", "Lisandro", "Luerbio", "Luidi",
    "Luiz", "Magnos", "Maycon", "Moacir", "Nabor", "Nalvo", "Nivan",
    "Nivio", "Odemir", "Pericles", "Rodrygo", "Rohit", "Rudini",
    "Thiago", "Tsang", "Ueverton", "Uira", "Vander", "Weverton",
    "Windson", "Zanoni", "Zhao"
]

NOMES_FEMININOS = [
    "Agma", "Aleteia", "Cristiane", "Fabricia", "Genaina", "Gisele",
    "Gracaliz", "Jussara", "Monalessa", "Soraia", "Sulamita", "Tatiane",
    "Tayana", "Thais", "Yandre"
]

def inferir_sexo(nome):
    d = gender.Detector()
    primeiro_nome = nome.strip().split()[0].capitalize()
    primeiro_nome_clean = primeiro_nome.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ã","a").replace("â","a").replace("ê","e").replace("ô","o").replace("ç","c")
    if primeiro_nome_clean in NOMES_MASCULINOS:
        return "Masculino"
    if primeiro_nome_clean in NOMES_FEMININOS:
        return "Feminino"
    resultado = d.get_gender(primeiro_nome)
    mapa = {
        "male": "Masculino", "female": "Feminino",
        "mostly_male": "Masculino", "mostly_female": "Feminino",
        "andy": "Indefinido", "unknown": "Indefinido"
    }
    return mapa.get(resultado, "Indefinido")

def inferir_uf(instituicao):
    inst_upper = instituicao.upper()
    for sigla, uf in INSTITUICAO_UF.items():
        if sigla.upper() in inst_upper:
            return uf
    return "N/A"

def montar_url(nome):
    nome_formatado = nome.strip().replace(" ", "+")
    return f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&termo={nome_formatado}"

def carregar_dados():
    # Carrega o dataset completo do GitHub
    try:
        df_completo = pd.read_csv(URL_GITHUB)
    except:
        try:
            df_completo = pd.read_csv("data/dataset.csv")
        except:
            return None, "erro", 0, 0, []

    # Garante que o campo ativo existe
    if "ativo" not in df_completo.columns:
        df_completo["ativo"] = "S"

    # Verifica se o CNPq esta disponivel
    try:
        response = requests.get(URL_CNPQ, headers=HEADERS, timeout=15)
        response.encoding = "latin-1"
        soup = BeautifulSoup(response.text, "html.parser")
        tabelas = soup.find_all("table")

        pesquisadores_cnpq = {}
        for tabela in tabelas:
            linhas = tabela.find_all("tr")
            for linha in linhas:
                colunas = linha.find_all("td")
                if len(colunas) >= 6:
                    nome = colunas[0].text.strip()
                    nivel = colunas[1].text.strip()
                    if nome and nivel and nome.upper() != "NOME":
                        pesquisadores_cnpq[nome] = {
                            "nivel_bolsa": nivel,
                            "vigencia_inicio": colunas[2].text.strip(),
                            "vigencia_termino": colunas[3].text.strip(),
                            "instituicao": colunas[4].text.strip(),
                            "situacao": colunas[5].text.strip(),
                        }

        if len(pesquisadores_cnpq) > 10:
            nomes_dataset = set(df_completo["nome"].tolist())
            nomes_cnpq = set(pesquisadores_cnpq.keys())

            novos = nomes_cnpq - nomes_dataset
            removidos = nomes_dataset - nomes_cnpq

            # Marca removidos como ativo=N
            if removidos:
                df_completo.loc[df_completo["nome"].isin(removidos), "ativo"] = "N"

            # Adiciona novos pesquisadores com campos basicos
            if novos:
                novos_registros = []
                for nome in novos:
                    dados = pesquisadores_cnpq[nome]
                    instituicao = dados["instituicao"]
                    novos_registros.append({
                        "nome": nome,
                        "sexo": inferir_sexo(nome),
                        "instituicao": instituicao,
                        "uf": inferir_uf(instituicao),
                        "nivel_bolsa": dados["nivel_bolsa"],
                        "area_atuacao": "N/A",
                        "ano_conclusao_doutorado": "N/A",
                        "url": montar_url(nome),
                        "google_scholar": "N/A",
                        "vigencia_inicio": dados["vigencia_inicio"],
                        "vigencia_termino": dados["vigencia_termino"],
                        "situacao": dados["situacao"],
                        "url_lattes": "N/A",
                        "formacao_academica": "N/A",
                        "pos_doutorado": "N/A",
                        "ativo": "S"
                    })
                df_novos = pd.DataFrame(novos_registros)
                df_completo = pd.concat([df_completo, df_novos], ignore_index=True)

            # Reativa pesquisadores que voltaram
            voltaram = nomes_cnpq & set(df_completo[df_completo["ativo"] == "N"]["nome"].tolist())
            if voltaram:
                df_completo.loc[df_completo["nome"].isin(voltaram), "ativo"] = "S"

            status = "cnpq_atualizado" if (novos or removidos) else "cnpq_ok"
            nomes_novos = list(novos)
            return df_completo, status, len(novos), len(removidos), nomes_novos

    except:
        return df_completo, "github", 0, 0, []

    return df_completo, "cnpq_ok", 0, 0, []