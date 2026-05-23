import pandas as pd

df = pd.read_csv("data/dataset.csv")

nomes = [
    "Claudine",
    "Diego Raphael",
    "Eduardo Antonio Guimaraes",
    "Geraldo Pereira Rocha",
    "Gustavo Pessin",
    "Joao Batista Florindo",
    "Marcelo Caggiani",
    "Pedro Olmo",
    "Raphael Carlos Santos",
    "Ricardo dos Santos Ferreira"
]

for nome in nomes:
    idx = df[df["nome"].str.contains(nome, na=False)].index
    if len(idx) > 0:
        df.at[idx[0], "area_atuacao"] = "Grande area: Ciencias Exatas e da Terra / Area: Ciencia da Computacao"
        print(f"Atualizado: {df.at[idx[0], 'nome']}")
    else:
        print(f"Nao encontrado: {nome}")

df.to_csv("data/dataset.csv", index=False, encoding="utf-8-sig")
print("Dataset atualizado!")