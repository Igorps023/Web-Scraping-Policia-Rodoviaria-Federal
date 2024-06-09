# %%
import requests
from bs4 import BeautifulSoup
from datetime import date
from time import sleep
from io import BytesIO
import os
import datetime
from pathlib import Path

import time
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


def get_content(url):
    cookies = {
    'Encrypted-Local-Storage-Key': 'BVB7Em6X724W9J+NPFU7dWyo7oTuQPj30Uq8JU0LkJY',
    'I18N_LANGUAGE': '"pt-br"',
    }
    
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos',
    'Connection': 'keep-alive',
    # 'Cookie': 'Encrypted-Local-Storage-Key=BVB7Em6X724W9J+NPFU7dWyo7oTuQPj30Uq8JU0LkJY; I18N_LANGUAGE="pt-br"',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    }
    
    resp = requests.get(url, verify=False) #header and cookies when necessary
    return resp

# %%
def get_objects(soup, selector):
    """
    soup = self_explainable,
    selector = the css object chosen
    """
    return soup.select(selector)
# %%  
#Inicio do Codigo  
url  = 'https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf'

resp = get_content(url)
# %%
#Tentativas de reconexao
if resp.status_code != 200:
    for i in range(10):
        sleep(0.5)
        resp = get_content(url)
        if resp.status_code == 200:
            break
        else:
            print(f'Erro! Codigo Response: {resp.status_code} | {datetime.datetime.now()}')

# %%
soup = BeautifulSoup(resp.text, 'html.parser')
# %%
obj_multas = get_objects(soup, 'table[class="plain"]')
# %%
#Tabela com cabecalho
tabela = obj_multas[3]
# %%
#Linhas tabelas
linhas = tabela.find_all('tr')
# %%
linhas_sem_strong = [linha for linha in linhas if not linha.find('strong')]
# %%
linhas_sem_strong
# %%
# Criando um dicionario
dict_multas = {}

for linha in linhas_sem_strong:
    celulas = linha.find_all('td')
    if celulas:
        link_celula = celulas[1].find('a')
        if link_celula:
            referencia = celulas[0].text.strip()
            link = link_celula.get('href')
            
            #Add to dict
            dict_multas[referencia] = link
            
# Agora você pode fazer o que quiser com os valores obtidos
# for referencia, link in dict_multas.items():
#     print("Referência:", referencia)
#     print("Link:", link)
# %%
#Links para download direto, serao acessados via Selenium Webdriver
direct_link = {}

for referencia, link in dict_multas.items():
    if 'drive.google.com/file/d/' in link:
        file_id = link.split('/')[-3]
        modified_link = f'https://drive.google.com/uc?export=download&id={file_id}'
        direct_link[referencia] = modified_link #Add to dict
    else:
        direct_link[referencia] = link
# %%
#SELENIUM WORKFLOW
#Download Preferences
download_path = str( Path('./Arquivos/Multas').resolve() )
options = Options()
options.set_preference("browser.download.useDownloadDir", True)
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", download_path)
# %%
for full_download_link in list(direct_link.values())[:-3]:
    try:
        start_time = time.time()
        timeout = time.time() + 20
        #Browser
        driver = webdriver.Firefox(options=options)
        #Run
        driver.get(full_download_link)
        try:
            div_download_button = \
                driver.find_element(By.XPATH, '//form[@id="download-form"]/input[@type="submit"]')
            
            if  div_download_button is not None:
                div_download_button.click()
                sleep(19)
                driver.quit()
        except:
            driver.quit()
    except:
        pass