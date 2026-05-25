import pandas as pd

# Dicionario de primeiros nomes e seus sexos
NOMES_MASCULINOS = [
    "Adenilso", "Adenilton", "Adiel", "Ajalmar", "Aldri", "Alneu",
    "Altigran", "Aluizio", "Amauri", "Anisio", "Aristofanes", "Baldoino",
    "Breno", "Carlile", "Celio", "Cleber", "Clodoveu", "Cristiano",
    "Dalcimar", "Danielo", "Davi", "Divanilson", "Dorgival", "Edelberto",
    "Edleno", "Ermeson", "Estevao", "Fabio", "Fabricio", "Fabrizzio",
    "Genaina", "Gilson", "Gladston", "Gleison", "Heder", "Jaelson",
    "Jamilson", "Javam", "Jeferson", "Joao", "Jomi", "Jurandir",
    "Jurandy", "Kleinner", "Lehilton", "Leobino", "Lisandro", "Luerbio",
    "Luidi", "Luiz", "Magnos", "Maycon", "Moacir", "Nabor", "Nalvo",
    "Nivan", "Nivio", "Odemir", "Pericles", "Rodrygo", "Rohit",
    "Rudini", "Thiago", "Tsang", "Ueverton", "Uira", "Vander",
    "Weverton", "Windson", "Zanoni", "Zhao"
]

NOMES_FEMININOS = [
    "Agma", "Aleteia", "Cristiane", "Fabricia", "Genaina", "Gisele",
    "Gracaliz", "Jussara", "Monalessa", "Soraia", "Sulamita", "Tatiane",
    "Tayana", "Thais", "Yandre"
]

def corrigir_sexo():
    df = pd.read_csv("data/dataset.csv")
    
    corrigidos = 0
    for i, row in df.iterrows():
        if row["sexo"] == "Indefinido":
            primeiro_nome = str(row["nome"]).strip().split()[0]
            primeiro_nome_clean = primeiro_nome.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ã","a").replace("â","a").replace("ê","e").replace("ô","o").replace("ç","c")
            
            if primeiro_nome_clean.capitalize() in NOMES_MASCULINOS:
                df.at[i, "sexo"] = "Masculino"
                corrigidos += 1
                print(f"M: {row['nome']}")
            elif primeiro_nome_clean.capitalize() in NOMES_FEMININOS:
                df.at[i, "sexo"] = "Feminino"
                corrigidos += 1
                print(f"F: {row['nome']}")

    df.to_csv("data/dataset.csv", index=False, encoding="utf-8-sig")
    print(f"\nCorrigidos: {corrigidos}")
    print(f"Ainda indefinidos: {(df['sexo'] == 'Indefinido').sum()}")

if __name__ == "__main__":
    corrigir_sexo()