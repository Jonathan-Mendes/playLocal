import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def iniciar_scanner_vivo():
    servico = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=servico)
    driver.get("https://youtube.com")

    print("Mantenha o navegador aberto e navegue normalmente.")

    links_ja_vistos = set()

    try:
        while True:
            elems = driver.find_elements(By.XPATH, "//a[contains(@href, '/watch?v=')]")
            novos = []

            for elem in elems:
                href = elem.get_attribute("href")
                if href:
                    link = href.split("&")[0]
                    if link not in links_ja_vistos:
                        novos.append(link)
                        links_ja_vistos.add(link)

            if novos:
                dados = []
                if os.path.exists("links.json"):
                    with open("links.json", "r") as f:
                        dados = json.load(f).get("urls", [])

                lista_final = list(set(dados + novos))

                with open("links.json", "w") as f:
                    json.dump({"urls": lista_final}, f, indent=4)

                print(f"[SCANNER] +{len(novos)} novos links enviados para fila.")

            time.sleep(10)

    except KeyboardInterrupt:
        driver.quit()
        print("\nScanner parado.")

if __name__ == "__main__":
    iniciar_scanner_vivo()
