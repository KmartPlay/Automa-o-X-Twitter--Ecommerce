# Este arquivo junta os dois bot.py e PegarLinkAfiliado.py para finalizar o processo

from PegarLinkAfiliado import pegar_produtos
from bot import enviar_ofertas
from config import chamar_api_x

def main():
    produtos_para_enviar = pegar_produtos()

# Para testar antes de realmente chamar a API do X Deixe a função DRY_RUN=TRUE, para enviar deixe FALSE
    enviar_ofertas(produtos=produtos_para_enviar, dry_run=chamar_api_x )
    
if __name__ == "__main__":

    main()
