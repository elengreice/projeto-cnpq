from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def extrair_secao(driver, nome_ancora):
    try:
        ancora = driver.find_element(By.CSS_SELECTOR, f"a[name='{nome_ancora}']")
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
        return " | ".join(textos[:3])
    except:
        return "N/A"

def extrair_dados_lattes(driver, nome):
    try:
        driver.get("http://buscatextual.cnpq.br/buscatextual/busca.do")
        time.sleep(2)

        campo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "textoBusca"))
        )
        campo.clear()
        campo.send_keys(nome)
        driver.find_element(By.ID, "botaoBuscaFiltros").click()
        time.sleep(3)

        # Clica no nome do pesquisador
        try:
            resultado = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ol li a b"))
            )
            resultado.click()
            time.sleep(2)
        except:
            try:
                resultado = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ol li a"))
                )
                resultado.click()
                time.sleep(2)
            except:
                return dados_vazios()

        # Clica em Abrir Curriculo
        try:
            botao = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Abrir') or contains(@class,'btn-primary')]"))
            )
            botao.click()
            time.sleep(3)
        except:
            return dados_vazios()

        # Muda para nova aba
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        url_lattes = driver.current_url
        formacao = extrair_secao(driver, "FormacaoAcademicaTitulacao")
        pos_doc = extrair_secao(driver, "FormacaoAcademicaPosDoutorado")
        area = extrair_secao(driver, "AreasAtuacao")
        atuacao = extrair_secao(driver, "AtuacaoProfissional")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return {
            "url_lattes": url_lattes,
            "formacao_academica": formacao,
            "pos_doutorado": pos_doc,
            "area_atuacao": area if area != "N/A" else atuacao
        }

    except Exception as e:
        print(f"  Erro: {str(e)[:80]}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        raise e  # Propaga o erro para reiniciar o driver

def dados_vazios():
    return {
        "url_lattes": "N/A",
        "formacao_academica": "N/A",
        "pos_doutorado": "N/A",
        "area_atuacao": "N/A"
    }

def enriquecer_dataset():
    df = pd.read_csv("data/dataset.csv")

    for col in ["url_lattes", "formacao_academica", "pos_doutorado", "area_atuacao"]:
        if col not in df.columns:
            df[col] = "N/A"
        else:
            df[col] = df[col].fillna("N/A").astype(str)

    print(f"Total de pesquisadores: {len(df)}")

    driver = iniciar_driver()
    driver.get("http://buscatextual.cnpq.br/buscatextual/busca.do")

    print("\n" + "="*50)
    print("Resolva o CAPTCHA se aparecer.")
    print("Pressione ENTER para continuar...")
    print("="*50)
    input()

    for i, row in df.iterrows():
        # Pula os ja processados
        val = str(df.at[i, "url_lattes"])
        if val not in ["N/A", "", "nan"]:
            print(f"[{i+1}/{len(df)}] {row['nome']} - ja processado, pulando...")
            continue

        print(f"[{i+1}/{len(df)}] Processando: {row['nome']}")

        tentativas = 0
        while tentativas < 3:
            try:
                dados = extrair_dados_lattes(driver, row["nome"])
                df.at[i, "url_lattes"] = dados["url_lattes"]
                df.at[i, "formacao_academica"] = dados["formacao_academica"]
                df.at[i, "pos_doutorado"] = dados["pos_doutorado"]
                df.at[i, "area_atuacao"] = dados["area_atuacao"]
                print(f"  Formacao: {dados['formacao_academica'][:60]}")
                print(f"  Area: {dados['area_atuacao'][:60]}")
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
                print("  Pressione ENTER para continuar apos o CAPTCHA...")
                input()

        # Salva a cada 5 pesquisadores
        if i % 1 == 0:
            df.to_csv("data/dataset.csv", index=False, encoding="utf-8-sig")
            print(f"  Progresso salvo!")

        time.sleep(2)

    df.to_csv("data/dataset.csv", index=False, encoding="utf-8-sig")
    print("\nDataset completo salvo!")
    try:
        driver.quit()
    except:
        pass
    return df

if __name__ == "__main__":
    enriquecer_dataset()