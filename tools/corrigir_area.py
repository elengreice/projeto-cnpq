from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

NOMES_CORRIGIR = [
    "Claudine Santos Baduê",
    "Diego Raphael Amancio",
    "Eduardo Antonio Guimaraes Tavares",
    "Geraldo Pereira Rocha Filho",
    "Gustavo Pessin",
    "Joao Batista Florindo",
    "Marcelo Caggiani Luizelli",
    "Pedro Olmo Stancioli Vaz De Melo",
    "Raphael Carlos Santos Machado",
    "Ricardo dos Santos Ferreira"
]

def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def extrair_area(driver, nome):
    driver.get("http://buscatextual.cnpq.br/buscatextual/busca.do")
    time.sleep(2)

    campo = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "textoBusca"))
    )
    campo.clear()
    campo.send_keys(nome)
    driver.find_element(By.ID, "botaoBuscaFiltros").click()
    time.sleep(3)

    try:
        resultado = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ol li a b"))
        )
        resultado.click()
        time.sleep(2)
    except:
        resultado = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ol li a"))
        )
        resultado.click()
        time.sleep(2)

    botao = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Abrir') or contains(@class,'btn-primary')]"))
    )
    botao.click()
    time.sleep(3)

    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)

    area = "N/A"
    try:
        ancora = driver.find_element(By.CSS_SELECTOR, "a[name='AreasAtuacao']")
        container = ancora.find_element(
            By.XPATH,
            "following-sibling::div[contains(@class,'data-cell')][1]"
        )
        itens = container.find_elements(By.CSS_SELECTOR, "div.layout-cell-pad-5")
        textos = []
        for item in itens:
            texto = item.text.strip()
            if texto and len(texto) > 5:
                textos.append(texto)
        area = " | ".join(textos[:3])
    except:
        area = "N/A"

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return area

def corrigir():
    df = pd.read_csv("data/dataset.csv")
    driver = iniciar_driver()
    driver.get("http://buscatextual.cnpq.br/buscatextual/busca.do")

    print("Pressione ENTER para continuar...")
    input()

    for nome in NOMES_CORRIGIR:
        print(f"Processando: {nome}")
        tentativas = 0
        area = "N/A"

        while tentativas < 3:
            try:
                area = extrair_area(driver, nome)
                print(f"  Area: {area[:80]}")
                break
            except Exception as e:
                tentativas += 1
                print(f"  Sessao perdida. Reiniciando driver ({tentativas}/3)...")
                try:
                    driver.quit()
                except:
                    pass
                time.sleep(3)
                driver = iniciar_driver()
                driver.get("http://buscatextual.cnpq.br/buscatextual/busca.do")
                print("  Pressione ENTER para continuar...")
                input()

        # Atualiza o dataset
        idx = df[df['nome'].str.contains(nome.split()[0], na=False)].index
        if len(idx) > 0:
            df.at[idx[0], 'area_atuacao'] = area
            df.to_csv("data/dataset.csv", index=False, encoding="utf-8-sig")
            print(f"  Salvo!")

    print("\nDataset corrigido e salvo!")
    try:
        driver.quit()
    except:
        pass

if __name__ == "__main__":
    corrigir()