from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

def encontrar_ponto_paragrafo(conteudo):
    limite_caracteres = 2000

    if len(conteudo) <= limite_caracteres:
        return conteudo

    indice_ponto = conteudo.find('. ', limite_caracteres)

    if indice_ponto == -1:
        return conteudo[:limite_caracteres]

    return conteudo[:indice_ponto + 2]

def pesquisar_google(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        titles = soup.find_all('h3')
        melhor_definicao = None

        for title in titles:
            link = title.find_parent('a')
            if link and link.has_attr('href'):
                link_absoluto = urljoin(url, link['href'])
                if "wikipedia.org" not in link_absoluto:
                    pagina_response = requests.get(link_absoluto)
                    
                    if pagina_response.status_code == 200:
                        pagina_soup = BeautifulSoup(pagina_response.text, 'html.parser')

                        possiveis_conteudos = [pagina_soup.find('div', {'class': 'content'}),
                                               pagina_soup.find('div', {'id': 'content'}),
                                               pagina_soup.find('article')]
                        
                        for conteudo_pagina in possiveis_conteudos:
                            if conteudo_pagina:
                                definicao = conteudo_pagina.get_text()
                                if not melhor_definicao or len(definicao) > len(melhor_definicao):
                                    melhor_definicao = definicao

        parte_inicial = encontrar_ponto_paragrafo(melhor_definicao)
        return parte_inicial, melhor_definicao if melhor_definicao else "Nenhuma definição foi encontrada nas páginas pesquisadas."
    else:
        return None, "Não foi possível acessar o Google."

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = ""
    conteudo_completo = ""
    if request.method == "POST":
        query = request.form.get("query")
        parte_inicial, conteudo_completo = pesquisar_google(query)
        resultado = parte_inicial

    return render_template("index.html", resultado=resultado, conteudo_completo=conteudo_completo)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
