"""
Script de atualizacao do dataset de pesquisadores CNPq.
Execute este script quando houver novos pesquisadores detectados pelo dashboard.

Como usar:
  Windows: python atualizacoes/atualizar_dataset.py
  Mac/Linux: python3 atualizacoes/atualizar_dataset.py
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import subprocess
import sys

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

def inferir_uf(instituicao):
    inst_upper = instituicao.upper()
    for sigla, uf in INSTITUICAO_UF.items():
        if sigla.upper() in inst_upper:
            return uf
    return "N/A"

def montar_google_scholar(nome):
    return f"https://scholar.google.com/scholar?q={nome.strip().replace(' ', '+')}"

def montar_url_lattes(nome):
    return f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&termo={nome.strip().replace(' ', '+')}"

print("=" * 60)
print("ATUALIZACAO DO DATASET - PESQUISADORES CNPq")
print("=" * 60)

# Carrega o dataset atual
print("\n1. Carregando dataset atual...")
try:
    df = pd.read_csv("data/dataset.csv")
    print(f"   Dataset carregado: {len(df)} pesquisadores")
except:
    print("   ERRO: Nao foi possivel carregar o dataset!")
    sys.exit(1)

# Carrega os novos pesquisadores detectados
print("\n2. Carregando novos pesquisadores detectados...")
try:
    df_novos = pd.read_csv("atualizacoes/novos_pesquisadores.csv")
    print(f"   {len(df_novos)} novos pesquisadores encontrados")
    print(df_novos[["nome", "instituicao", "nivel_bolsa"]].to_string())
except:
    print("   ERRO: Arquivo novos_pesquisadores.csv nao encontrado!")
    print("   Gere o arquivo pelo dashboard primeiro.")
    sys.exit(1)

# Confirma com o usuario
print("\n3. Deseja adicionar esses pesquisadores ao dataset? (s/n): ", end="")
confirmacao = input().strip().lower()
if confirmacao != "s":
    print("   Operacao cancelada.")
    sys.exit(0)

# Enriquece os dados com Google Scholar e URL Lattes
print("\n4. Enriquecendo dados...")
df_novos["google_scholar"] = df_novos["nome"].apply(montar_google_scholar)
df_novos["url"] = df_novos["nome"].apply(montar_url_lattes)
df_novos["url_lattes"] = "N/A"
df_novos["formacao_academica"] = "N/A"
df_novos["pos_doutorado"] = "N/A"
df_novos["area_atuacao"] = "N/A"
df_novos["ano_conclusao_doutorado"] = "N/A"
df_novos["ativo"] = "S"

# Garante que as colunas estao na ordem certa
colunas = df.columns.tolist()
for col in colunas:
    if col not in df_novos.columns:
        df_novos[col] = "N/A"
df_novos = df_novos[colunas]

# Adiciona ao dataset
df_atualizado = pd.concat([df, df_novos], ignore_index=True)
df_atualizado = df_atualizado.drop_duplicates(subset=["nome"])

# Salva o dataset
print("\n5. Salvando dataset atualizado...")
df_atualizado.to_csv("data/dataset.csv", index=False, encoding="utf-8-sig")
print(f"   Dataset salvo: {len(df_atualizado)} pesquisadores")

# Faz push para o GitHub
print("\n6. Atualizando GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"adiciona {len(df_novos)} novos pesquisadores ao dataset"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("   GitHub atualizado com sucesso!")
except Exception as e:
    print(f"   ERRO ao atualizar GitHub: {e}")
    print("   Execute manualmente: git add . && git commit -m 'atualiza dataset' && git push")

print("\n" + "=" * 60)
print("ATUALIZACAO CONCLUIDA!")
print("O dashboard sera atualizado automaticamente em alguns minutos.")
print("=" * 60)