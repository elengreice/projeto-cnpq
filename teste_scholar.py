from scholarly import scholarly
import time

pesquisadores = [
    "Adenilso Simao",
    "Adriana Vivacqua",
    "Adriano Veloso",
    "Agma Traina",
    "Alba Melo",
]

for nome in pesquisadores:
    try:
        print(f"\nBuscando: {nome}")
        resultado = scholarly.search_author(nome)
        autor = next(resultado)
        url = f"https://scholar.google.com/citations?user={autor['scholar_id']}"
        print(f"  Encontrado: {autor.get('name', 'N/A')}")
        print(f"  Afiliacao: {autor.get('affiliation', 'N/A')}")
        print(f"  URL: {url}")
        time.sleep(3)
    except StopIteration:
        print(f"  Nao encontrado")
    except Exception as e:
        print(f"  Erro: {str(e)[:100]}")