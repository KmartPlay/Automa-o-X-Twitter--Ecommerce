# Bot de Automação para X (Twitter) com E-commerce

Este projeto consiste em um bot que automatiza a criação de tweets para um perfil no X, divulgando promoções encontradas no e-commerce "Mercado Livre".

## Objetivo

O principal objetivo deste repositório é demonstrar a estrutura do código e minhas habilidades na utilização de:
- **Linguagem:** Python
- **Bibliotecas:** Selenium para Web Scraping
- **APIs:** Integração com as APIs do X (antigo Twitter) e do Gemini (Google AI).

## Como Funciona

1.  **Coleta de Dados:** O bot utiliza a biblioteca `Selenium` para navegar até o site do Mercado Livre e extrair informações dos produtos, como título, preço e imagem.
    -   ⚠️ **Ponto de Atenção:** A coleta de dados depende da estrutura front-end do site. Alterações no layout do Mercado Livre podem quebrar o scraper.

2.  **Criação de Conteúdo:** Com os dados do produto em mãos, a aplicação faz uma chamada à **API do Gemini** para gerar um texto de marketing criativo e dinâmico para o tweet. Isso evita que as postagens soem robóticas e repetitivas.

3.  **Publicação:** Por fim, o bot utiliza a **API do X** para postar o conteúdo gerado (texto + imagem) no perfil de destino.

## Perfil de Demonstração

O perfil utilizado para este projeto é o **[@SuperEcoBrasil](https://twitter.com/SuperEcoBrasil)**. Ele foi criado como um ambiente de testes e aprendizado para este estudo de caso.(e acabou me gerando receita rsrs)

