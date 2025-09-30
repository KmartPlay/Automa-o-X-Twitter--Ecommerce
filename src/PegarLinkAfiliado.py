# PegarLinkAfiliado.py

# Aqui vamos entrar no site do MELI e realizar a busca de itens na pagina principal, a quantidade de item
# é editavel, podendo pegar mais de 10 itens do site, todo o fluxo foi baseado na pagina de afiliado,
# podendo gerar erros em outras paginas do mercado livre, já que é utilizado a biblioteca Selenium, e o site 
# pode e é sempre atualizado, perdendo assim, perder a referencia para busca.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import qtd_itens
from config import UrlLink
import time
import pyperclip # Importe a biblioteca pyperclip

chrome_options = Options()
# Adicione o argumento '--headless' para rodar em modo headless
chrome_options.add_argument("--headless")

def pegar_produtos():
    chrome_options = Options()
    chrome_options.add_argument(r"user-data-dir=C:\Users\"USER"\AppData\Local\Google\Chrome for Testing\User Data")
    chrome_options.add_argument("profile-directory=Default")  # ou outro nome, como "Profile 1"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Aqui fica o link - para buscar em outra aba, atualizar no arquivo config.py.
    driver.get(UrlLink)
    wait = WebDriverWait(driver, 15)

    #Localiza e clica em "Entendi" quando sobe pop-up do mercado livre.
    try:
        botao_entendi = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Entendi']"))
    )
        botao_entendi.click()
        print("✅ Pop-up fechado.")
    except (TimeoutException, NoSuchElementException):
        print("ℹ️ Pop-up não apareceu.")

    container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#root-app > div > section > div.items > div > div")))
    
    # Quantidade de produtos que ele vai pegar da pagina inicial, editavel no arquivo config.py
    produtos = container.find_elements(By.CSS_SELECTOR, "div.andes-card.poly-card")[:qtd_itens] # Numero de Itens para buscar

    produtos_lista = []

    for produto in produtos:

        #Localiza e clica em "Entendi" quando sobe pop-up do mercado livre.
        try:
            titulo_element = produto.find_element(By.CSS_SELECTOR, "h3 > a.poly-component__title")
            titulo = titulo_element.text
            titulo_original = titulo
            url = titulo_element.get_attribute('href')

            # --- Lógica para encurtar o título ---
            palavras = titulo_original.split() # Divide o título em uma lista de palavras
            
            # Definir quantas palavras você quer manter (ex: 8 palavras)
            num_palavras_desejadas = 8 
            titulo_curto = " ".join(palavras[:num_palavras_desejadas])

            # Adiciona reticências se o título original era mais longo
            if len(palavras) > num_palavras_desejadas:
                titulo_curto += "..."
            
            titulo = titulo_curto # Atribui o título curto à variável 'titulo' que será usada no resto do código

            print(f"Título encurtado: {titulo}") # Para debug
            # --- Fim da lógica para encurtar o título ---

        except Exception as e:
            titulo = "Título não encontrado"
            url = ""
            print("Erro ao pegar titulo/url:", e)

        try:
            preco_atual = produto.find_element(By.CSS_SELECTOR, "div.poly-price__current > span.andes-money-amount.andes-money-amount--cents-superscript").text
        except:
            preco_atual = "Preço não encontrado"

        try:
            preco_antigo = produto.find_element(By.CSS_SELECTOR, "div.poly-component__price > s").text
        except:
            preco_antigo = "Sem preço antigo"

        #Edita o preço
        preco_atual = preco_atual.replace('\n', '').strip()
        preco_antigo = preco_antigo.replace('\n', '').strip()

        # Abrir a página do produto para gerar link de afiliado
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(url)

                #   Verifica se tem POP-UP
        try:
            botao_entendi = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Entendi']"))
    )
            botao_entendi.click()
            print("✅ Pop-up fechado.")
        except (TimeoutException, NoSuchElementException):
            print("ℹ️ Pop-up não apareceu.")


                # --- TRECHO PARA CAPTURAR A IMAGEM ---
        link_imagem = "" # Garante que a variável sempre exista
        try:
            print("ℹ️ Aguardando e localizando a imagem principal do produto...")
            
            # Ele procura especificamente pela imagem DENTRO da <figure> principal.
            seletor_da_imagem = "figure.ui-pdp-gallery__figure > img.ui-pdp-image"
            
            imagem_principal_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, seletor_da_imagem))
            )
            
            # --- A lógica "detetive" para aplicar ao elemento CORRETO ---
            urls_candidatas = [
                imagem_principal_element.get_attribute("data-zoom"),
                imagem_principal_element.get_attribute("srcset"),
                imagem_principal_element.get_attribute("src")
            ]
            
            todas_as_urls = []
            for item in urls_candidatas:
                if item:
                    urls = item.split(',')
                    for url_part in urls:
                        todas_as_urls.append(url_part.strip().split(' ')[0])

            prioridade_qualidade = ['-X.webp', '-O.webp', '-F.webp']
            melhor_url_encontrada = None

            for qualidade in prioridade_qualidade:
                for url in todas_as_urls:
                    if qualidade in url:
                        melhor_url_encontrada = url
                        break
                if melhor_url_encontrada:
                    break

            if not melhor_url_encontrada and todas_as_urls:
                melhor_url_encontrada = todas_as_urls[0]

            link_imagem = melhor_url_encontrada
            
            if link_imagem:
                print(f"✅ SUCESSO! Melhor link de imagem encontrado: {link_imagem}")
            else:
                print("❌ FALHA! Nenhuma URL de imagem pôde ser extraída.")

        except Exception as e:
            print(f"❌ Falha crítica ao tentar pegar a imagem: {e}")
        # --- FIM DO CÓDIGO ---

        # Esperar campo com o link afiliado visível
        try:

            gerar_link_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Compartilhar')]"))
            )
            gerar_link_btn.click()
            print("✅ Botão 'Compartilhar / ID' clicado.")

            # Esperar o modal aparecer (o título do modal)
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "span.andes-typography--type-title"))
            )
            print("✅ Modal 'Compartilhar / ID de produto' apareceu.")

            link_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'Link do produto')]/following-sibling::div//button[./*[name()='svg' or contains(@class, 'icon-copy') or contains(@class, 'copy-icon')]]"))
            )
            
            link_input.click()


            time.sleep(5)

            link_afiliado = pyperclip.paste()
    
            # Verifica se é diferente do link original
            if link_afiliado == url:
                print("⚠️ Link afiliado não foi gerado, mesmo após clique.")
                link_afiliado = ""
            else:
                print(f"✅ Link afiliado: {link_afiliado}")

        except Exception as e:
            print("❌ Erro ao Compartilhar de afiliado:", e)
            link_afiliado = ""


        # Fecha aba do produto e volta para a de listagem
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        produtos_lista.append({
            "titulo": titulo,
            "url": url,
            "preco_atual": preco_atual,
            "preco_antigo": preco_antigo,
            "link_afiliado": link_afiliado,
            "link_imagem": link_imagem
        })

    driver.quit()
    return produtos_lista

if __name__ == "__main__":
    produtos = pegar_produtos()
    print("Produtos capturados:")
    for produto in produtos:
        print(f"Título: {produto['titulo']}")
        print(f"URL: {produto['url']}")
        print(f"Preço atual: {produto['preco_atual']}")
        print(f"Preço antigo: {produto['preco_antigo']}")
        print(f"Link afiliado: {produto['link_afiliado']}")
        print(f"Link Img: {produto['link_imagem']}")
        print("-" * 40)
