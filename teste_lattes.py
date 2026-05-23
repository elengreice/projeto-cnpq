from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

driver = iniciar_driver()

# Abre o Lattes
driver.get("http://buscatextual.cnpq.br/buscatextual/busca.do")
print("Pagina aberta!")

input("Digite o nome, clique em Buscar, clique no resultado, clique em Abrir Curriculo e pressione ENTER aqui...")

# Muda para a aba do curriculo
driver.switch_to.window(driver.window_handles[-1])
time.sleep(3)

print("URL atual:", driver.current_url)
print("\n--- Procurando secoes ---")

# Lista todas as ancoras da pagina
ancoras = driver.find_elements(By.CSS_SELECTOR, "a[name]")
print(f"Total de ancoras encontradas: {len(ancoras)}")
for a in ancoras:
    print(" -", a.get_attribute("name"))

print("\n--- Tentando extrair formacao ---")
try:
    blocos = driver.find_elements(By.CSS_SELECTOR, "div.layout-cell-pad-5")
    print(f"Total de blocos layout-cell-pad-5: {len(blocos)}")
    for i, b in enumerate(blocos[:5]):
        print(f"Bloco {i}: {b.text[:100]}")
except Exception as e:
    print("Erro:", e)

input("Pressione ENTER para fechar...")
driver.quit()