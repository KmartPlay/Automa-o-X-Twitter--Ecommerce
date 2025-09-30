# Esse Arquivo recebe a lista de PegarLinkAfiliado para gerar o tweet, com a quantidade de itens que você
# Rodou no PegarLinkAfiliado

import tweepy
import time
import os
import requests
import io
import google.generativeai as genai
#from EnviarProdutos import Tempo_de_envio
from PegarLinkAfiliado import pegar_produtos  # Importa a função que retorna a lista de produtos
from dotenv import load_dotenv # Importa a Autenticação/Login para API V2 do X (Antigo Twitter)
from config import tem_proximo
from config import chamar_api_x


# --- INÍCIO DA SEÇÃO DE DEPURAÇÃO ---
# 1. Pega o diretório do arquivo atual (bot.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"DEBUG: Diretório atual do script (bot.py): {current_dir}")

# 2. Define o caminho provável do config.env
# Se config.env estiver no MESMO diretório do bot.py:
dotenv_path = os.path.join(current_dir, '.env')

print(f"DEBUG: Caminho completo esperado para .env: {dotenv_path}")

# 3. Verifica se o arquivo existe ANTES de tentar carregar
if not os.path.exists(dotenv_path):
    print(f"ERRO CRÍTICO: Arquivo 'config.env' NÃO encontrado no caminho especificado: {dotenv_path}")
    print("Por favor, verifique se o arquivo existe e o caminho está correto.")
    # Saia do script se o arquivo não for encontrado para evitar erros maiores
    exit()

# 4. Tenta carregar o .env
print("DEBUG: Tentando carregar o arquivo .env...")
load_dotenv(dotenv_path=dotenv_path, override=True) # Use override=True para garantir que não há variáveis antigas
print("DEBUG: load_dotenv() executado.")

# 5. Verifica os valores das variáveis imediatamente após carregar
consumer_key_val = os.getenv("consumer_key")
consumer_secret_val = os.getenv("consumer_secret")
bearer_token_val = os.getenv("bearer_token")
access_token_val = os.getenv("access_token")
access_token_secret_val = os.getenv("access_token_secret")

#  Carrega a chave da API do Gemini ---
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    print("ERRO CRÍTICO: Chave 'GEMINI_API_KEY' não encontrada no arquivo .env")
    exit()


# Autenticação com a API V2 do Twitter
client = tweepy.Client(
    consumer_key=consumer_key_val,
    consumer_secret=consumer_secret_val,
    bearer_token=bearer_token_val,
    access_token=access_token_val,
    access_token_secret=access_token_secret_val
)

#  Autenticação V1.1 necessária para o upload de mídias ---
auth_v1 = tweepy.OAuth1UserHandler(
    consumer_key=consumer_key_val,
    consumer_secret=consumer_secret_val,
    access_token=access_token_val,
    access_token_secret=access_token_secret_val
)
api_v1 = tweepy.API(auth_v1)

#  Configuração do Gemini ---
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

#  Função que gera o texto com o Gemini ---
def gerar_texto_com_gemini(titulo_produto):
    prompt = f"""
Você é o bot Super Eco Brasil do X (Twitter), especialista em caçar achados insanos no Mercado Livre.
Sua missão é criar um texto curto, zoeiro e empolgante para anunciar o seguinte produto: "{titulo_produto}".

REGRAS:

No máximo 1 frases curtas.

Use linguagem informal, divertida e cheia de vibe geração Z (pode ter trocadilhos, gírias e tom de meme).

Inclua 2 emojis que faz sentido no texto: um logo no começo e outro no meio.

Jamais coloque preço, nome completo do produto, link, temporalidade, ou glow-up — apenas a chamada criativa.

Exemplos:

Para "Fone de Ouvido Bluetooth":
👉 "Cansado de nó de fio? Esse fone solta o som sem treta 🎧 perfeito pra academia ou rolê."

Para "Lâmpada Inteligente Wi-Fi RGB":
👉 "Quarto sem graça? Essa lâmpada dá upgrade no mood 🌈 muda de cor direto do cel, sem levantar da cama."
    """
    try:
        print("🤖 Pedindo uma ideia criativa para o Gemini...")
        response = model.generate_content(prompt)
        texto_criativo = response.text.strip().replace('"', '') # Remove aspas que a IA às vezes adiciona
        print(f"✨ Gemini sugeriu: '{texto_criativo}'")
        return texto_criativo
    except Exception as e:
        print(f"⚠️ Erro ao chamar a API do Gemini: {e}. Usando texto padrão.")
        return "Olha só esse preço!!!"

def enviar_ofertas(produtos=None, dry_run=True):
    if produtos is None:
        # Este fallback é útil, mas no seu fluxo principal você sempre passará os produtos.
        from PegarLinkAfiliado import pegar_produtos
        produtos = pegar_produtos()
        
    for produto in produtos:
        # --- LÓGICA DO TWEET MODIFICADA ---
        # 1. Gera o texto criativo primeiro
        texto_criativo = gerar_texto_com_gemini(produto['titulo'])
        
        # 2. Monta o tweet completo com o texto do Gemini
        tweet_completo = (
            f"{texto_criativo}\n\n"
            f"{produto['titulo']}\n\n"
            f"De: {produto['preco_antigo']} 😎 Por apenas: 👌 {produto['preco_atual']}!\n\n"
            f"👉 Compre aqui: {produto['link_afiliado']}"
        )
        
        print("\n" + "="*50)
        print("Tweet a ser enviado:\n", tweet_completo)
        
        # Lógica para tratar e fazer upload da imagem (EXISTENTE)
        media_id = None
        if produto.get("link_imagem"):
            try:
                print(f"🖼️ Baixando imagem de alta qualidade...")
                response = requests.get(produto['link_imagem'], stream=True, timeout=15)
                response.raise_for_status()
                
                image_data = io.BytesIO(response.content)
                
                print("📤 Fazendo upload da imagem para o X...")
                media = api_v1.media_upload(filename="oferta_meli.jpg", file=image_data)
                media_id = media.media_id_string
                print(f"✅ Upload da imagem concluído! Media ID: {media_id}")
            except Exception as e:
                print(f"⚠️ AVISO: Falha ao processar a imagem. Tweet será enviado sem ela. Erro: {e}")
        else:
            print("ℹ️ Produto sem link de imagem. Enviando tweet somente com texto.")
        
        # Lógica de envio (EXISTENTE)
        if  dry_run and chamar_api_x:
            try:
                kwargs = {'text': tweet_completo}
                if media_id:
                    kwargs['media_ids'] = [media_id]
                
                print("🚀 Enviando tweet...")
                response = client.create_tweet(**kwargs)
                print(f"✅ Tweet enviado com sucesso para: {produto['titulo']}")
                print("Resposta da API:", response)
            except Exception as e:
                print(f"❌ ERRO CRÍTICO ao enviar o tweet: {e}")
        else:
            print("🚫 Dry run: Tweet não foi enviado.")
            
        print(f"⏳ Aguardando alguns segundos antes da próxima oferta...")
        time.sleep(tem_proximo)

if __name__ == "__main__":
    enviar_ofertas()
