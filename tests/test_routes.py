import re
import pytest
import app as app_module
from scripts import blog

LANG_JS = app_module.STATIC_DIR / "js" / "lang.js"

POSTS_REAIS = blog.all_posts(app_module.templates.env, app_module.TEMPLATES_DIR)


def test_health(client):
    resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "OK"}


@pytest.mark.parametrize("rota", ["/", "/pt/", "/pt", "/blog", "/blog/", "/linktree", "/linktree/"])
def test_paginas_respondem_html(client, rota):
    resposta = client.get(rota)

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    assert "<html" in resposta.text


def test_portfolio_em_ingles_declara_idioma_e_alternativa(client):
    html = client.get("/").text

    assert 'data-lang-page="en"' in html
    assert 'data-lang-alt="/pt/"' in html


def test_portfolio_em_portugues_declara_idioma_e_alternativa(client):
    html = client.get("/pt/").text

    assert 'data-lang-page="pt"' in html
    assert 'data-lang-alt="/"' in html


def test_blog_traduz_no_lugar_em_vez_de_redirecionar(client):
    html = client.get("/blog/").text

    assert "data-i18n-live" in html
    assert "data-lang-alt" not in html


@pytest.mark.parametrize("rota", ["/", "/pt/", "/blog/", "/linktree"])
def test_todas_as_paginas_carregam_o_lang_js(client, rota):
    assert "/static/js/lang.js" in client.get(rota).text


# --- listagem do blog

def test_listagem_mostra_os_posts_publicados(client, post_temporario):
    post_temporario("teste-listagem", "Post de listagem", "2026-05-05")

    html = client.get("/blog/").text

    assert "Post de listagem" in html
    assert "/blog/teste-listagem" in html


def test_listagem_ordena_do_mais_recente_para_o_mais_antigo(client, post_temporario):
    post_temporario("teste-antigo", "Antigo", "2020-01-01")
    post_temporario("teste-novo", "Novo", "2099-01-01")

    html = client.get("/blog/").text
    ordem = re.findall(r'href="/blog/(teste-antigo|teste-novo)"', html)

    assert ordem == ["teste-novo", "teste-antigo"]


def test_listagem_oferece_filtro_com_as_tags_existentes(client, post_temporario):
    post_temporario("teste-tag", "Com tag", "2026-05-05", tags=["pentest"])

    html = client.get("/blog/").text

    assert 'data-tag="*"' in html
    assert 'data-tag="pentest"' in html


def test_titulos_e_resumos_ficam_marcados_como_portugues(client, post_temporario):
    post_temporario("teste-lang", "Título", "2026-05-05")

    html = client.get("/blog/").text

    assert 'class="post-item__title" lang="pt-br"' in html
    assert 'class="post-item__summary" lang="pt-br"' in html


# --- post individual

@pytest.mark.parametrize("post", POSTS_REAIS, ids=lambda p: p.slug)
def test_cada_post_publicado_responde(client, post):
    resposta = client.get(post.url)

    assert resposta.status_code == 200
    assert post.title in resposta.text


def test_post_declara_o_corpo_como_portugues(client, post_temporario):
    post_temporario("teste-corpo", "Corpo", "2026-05-05")

    html = client.get("/blog/teste-corpo").text

    assert 'class="post-body" lang="pt-br"' in html


def test_post_aponta_para_os_vizinhos(client, post_temporario):
    post_temporario("teste-vizinho-antigo", "Vizinho antigo", "2098-01-01")
    post_temporario("teste-vizinho-novo", "Vizinho novo", "2099-01-01")

    html = client.get("/blog/teste-vizinho-antigo").text

    assert "/blog/teste-vizinho-novo" in html
    assert 'data-i18n="post.next"' in html


def test_post_mais_novo_nao_tem_proximo(client, post_temporario):
    post_temporario("teste-unico-novo", "Mais novo", "2099-12-31")

    html = client.get("/blog/teste-unico-novo").text

    assert 'data-i18n="post.next"' not in html


def test_slug_inexistente_retorna_404(client):
    resposta = client.get("/blog/post-que-nunca-existiu")

    assert resposta.status_code == 404


@pytest.mark.parametrize(
    "slug",
    [
        "../../../etc/passwd",
        "..%2f..%2f..%2fetc%2fpasswd",
        "%2e%2e%2f%2e%2e%2fapp",
        "....//....//app",
        "Maiusculo",
        "com espaco",
        "post.html",
        "hello-world.html",
    ],
)
def test_slug_malicioso_retorna_404_sem_vazar_arquivo(client, slug):
    """`..` puro não entra aqui de propósito: o cliente HTTP normaliza o caminho
    antes de enviar, então a requisição nem chega no handler."""
    resposta = client.get(f"/blog/{slug}")

    assert resposta.status_code == 404
    assert "root:" not in resposta.text
    assert "STATIC_DIR" not in resposta.text


# --- linktree


def test_linktree_traduz_no_lugar_em_vez_de_redirecionar(client):
    html = client.get("/linktree").text

    assert "data-i18n-live" in html
    assert "data-lang-alt" not in html


def test_linktree_nao_marca_o_blog_como_pagina_atual(client):
    html = client.get("/linktree").text

    assert "nav--active" not in html


@pytest.mark.parametrize(
    "destino",
    [
        '"/"',
        '"/blog"',
        "Curriculum 2026.pdf",
        "api.whatsapp.com",
        "mailto:contato@matheusdealencar.com",
        "linkedin.com/in/matheus-de-alencar",
        "github.com/titiomathias",
        "instagram.com/matheuz_alencar",
    ],
)
def test_linktree_lista_os_canais_principais(client, destino):
    assert destino in client.get("/linktree").text


def test_linktree_carrega_o_proprio_estilo(client):
    assert "/static/css/linktree.css" in client.get("/linktree").text


# --- avaliações

def test_reviews_devolve_a_lista_do_scraper(client, monkeypatch):
    esperado = [{"link": "https://exemplo.com/p/1", "title": "Projeto", "comment": "Ótimo!"}]
    monkeypatch.setattr(app_module.request_site, "get_feedbacks", lambda: esperado)

    resposta = client.get("/reviews")

    assert resposta.status_code == 200
    assert resposta.json() == esperado


def test_reviews_propaga_falha_do_scraper_como_500(client, monkeypatch):
    monkeypatch.setattr(
        app_module.request_site,
        "get_feedbacks",
        lambda: {"error": "fail to access site"},
    )

    resposta = client.get("/reviews")

    assert resposta.status_code == 500
    assert resposta.json()["detail"] == "fail to access site"


# --- consistência do dicionário de idiomas

def _chaves_usadas(client):
    paginas = [client.get(rota).text for rota in ("/", "/pt/", "/blog/", "/linktree")]
    paginas += [client.get(post.url).text for post in POSTS_REAIS]
    return {chave for html in paginas for chave in re.findall(r'data-i18n="([^"]+)"', html)}


def test_toda_chave_de_traducao_existe_nos_dois_dicionarios(client, post_temporario):
    post_temporario("teste-chaves-a", "A", "2098-01-01")
    post_temporario("teste-chaves-b", "B", "2099-01-01")

    fonte = LANG_JS.read_text(encoding="utf-8")
    usadas = _chaves_usadas(client)
    assert usadas, "nenhuma chave data-i18n encontrada — varredura provavelmente quebrou"

    faltando = {
        chave: fonte.count("'%s':" % chave)
        for chave in usadas
        if fonte.count("'%s':" % chave) != 2
    }

    assert faltando == {}, "chaves ausentes em pt ou en (esperado 2 ocorrências): %s" % faltando
