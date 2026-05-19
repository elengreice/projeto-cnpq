import requests

URL = (
    "http://plsql1.cnpq.br/divulg/RESULTADO_PQ_102003.prc_comp_cmt_links"
    "?V_COD_DEMANDA=200310&V_TPO_RESULT=CURSO"
    "&V_COD_AREA_CONHEC=10300007&V_COD_CMT_ASSESSOR=CC"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

response = requests.get(URL, headers=HEADERS, timeout=30)
response.encoding = "latin-1"

# Salva o HTML completo num arquivo para inspecionar
with open("pagina.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("✅ HTML salvo em pagina.html")
print(f"Tamanho do HTML: {len(response.text)} caracteres")