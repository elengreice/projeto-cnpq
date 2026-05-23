import pandas as pd
import re

df = pd.read_csv("data/dataset.csv")

def extrair_ano_conclusao(formacao):
    try:
        # Busca padrão como "2006 - 2008" e pega o segundo ano
        match = re.search(r'\d{4}\s*-\s*(\d{4})', str(formacao))
        if match:
            return match.group(1)
        # Se não achar, busca qualquer ano de 4 digitos
        match = re.search(r'\d{4}', str(formacao))
        if match:
            return match.group(0)
        return "N/A"
    except:
        return "N/A"

df["ano_conclusao_doutorado"] = df["formacao_academica"].apply(extrair_ano_conclusao)

print(df[["nome", "formacao_academica", "ano_conclusao_doutorado"]].head(10).to_string())

df.to_csv("data/dataset.csv", index=False, encoding="utf-8-sig")
print("\nDataset atualizado com ano de conclusao do doutorado!")