import re
import pytest
import app as app_module

LANG_JS = app_module.STATIC_DIR / "js" / "lang.js"


def test_health(client):
    resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "OK"}


@pytest.mark.parametrize("rota", ["/", "/pt/", "/pt", "/linktree", "/linktree/"])
def test_paginas_respondem_html(client, rota):
    resposta = client.get(rota)

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    assert "<html" in resposta.text


@pytest.mark.parametrize("rota", ["/blog", "/blog/", "/blog/hello-world"])
def test_blog_foi_removido_do_site(client, rota):
    assert client.get(rota).status_code == 404


def test_sitemap_lista_so_as_paginas_publicas(client):
    resposta = client.get("/sitemap.xml")

    assert resposta.status_code == 200
    assert "/blog" not in resposta.text
    for pagina in ("<loc>https://matheusdealencar.com/</loc>",
                   "<loc>https://matheusdealencar.com/pt/</loc>",
                   "<loc>https://matheusdealencar.com/linktree</loc>"):
        assert pagina in resposta.text


def test_portfolio_em_ingles_declara_idioma_e_alternativa(client):
    html = client.get("/").text

    assert 'data-lang-page="en"' in html
    assert 'data-lang-alt="/pt/"' in html


def test_portfolio_em_portugues_declara_idioma_e_alternativa(client):
    html = client.get("/pt/").text

    assert 'data-lang-page="pt"' in html
    assert 'data-lang-alt="/"' in html


@pytest.mark.parametrize("rota", ["/", "/pt/", "/linktree"])
def test_todas_as_paginas_carregam_o_lang_js(client, rota):
    assert "/static/js/lang.js" in client.get(rota).text


# --- linktree


def test_linktree_traduz_no_lugar_em_vez_de_redirecionar(client):
    html = client.get("/linktree").text

    assert "data-i18n-live" in html
    assert "data-lang-alt" not in html


@pytest.mark.parametrize(
    "destino",
    [
        '"/"',
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
    paginas = [client.get(rota).text for rota in ("/", "/pt/", "/linktree")]
    return {chave for html in paginas for chave in re.findall(r'data-i18n="([^"]+)"', html)}


def test_toda_chave_de_traducao_existe_nos_dois_dicionarios(client):
    fonte = LANG_JS.read_text(encoding="utf-8")
    usadas = _chaves_usadas(client)
    assert usadas, "nenhuma chave data-i18n encontrada — varredura provavelmente quebrou"

    faltando = {
        chave: fonte.count("'%s':" % chave)
        for chave in usadas
        if fonte.count("'%s':" % chave) != 2
    }

    assert faltando == {}, "chaves ausentes em pt ou en (esperado 2 ocorrências): %s" % faltando
