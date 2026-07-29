import json
import os
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path

import pytest

from scripts import request_site

RAIZ = Path(__file__).resolve().parent.parent


PAGINA = """
<html><body><ul>
  <li class="box-loader-item">
    <div class="project-info-left">
      <a href="/projeto/api-de-pagamentos">  API de pagamentos  </a>
      <p class="project-comment">  Entregou antes do prazo.  </p>
    </div>
    <div class="project-info-right">Finalizado</div>
  </li>
  <li class="box-loader-item">
    <div class="project-info-left">
      <a href="/projeto/site-institucional">Site institucional</a>
      <p class="project-comment">Cliente desistiu no meio.</p>
    </div>
    <div class="project-info-right">Cancelado pelo cliente</div>
  </li>
  <li class="box-loader-item">
    <div class="project-info-left">
      <a href="/projeto/scraper">Scraper de dados</a>
      <p class="project-comment">Recomendo demais.</p>
    </div>
    <div class="project-info-right">Finalizado</div>
  </li>
</ul></body></html>
"""


class RespostaFalsa:
    def __init__(self, status_code, content=""):
        self.status_code = status_code
        self.content = content.encode("utf-8")


class ScraperFalso:
    def __init__(self, resposta):
        self.resposta = resposta
        self.urls = []

    def get(self, url):
        self.urls.append(url)
        return self.resposta


@pytest.fixture
def cache_temporario(tmp_path, monkeypatch):
    """Redireciona o arquivo de cache para tmp_path.

    Sem isso os testes sobrescreveriam o scripts/feedbacks.json real.
    """
    caminho = tmp_path / "feedbacks.json"
    monkeypatch.setattr(request_site, "FILE_PATH", caminho)
    return caminho


@pytest.fixture
def scraper_falso(monkeypatch):
    def _instalar(status_code=200, content=PAGINA):
        dublê = ScraperFalso(RespostaFalsa(status_code, content))
        monkeypatch.setattr(request_site.cloudscraper, "create_scraper", lambda: dublê)
        return dublê

    return _instalar


@pytest.fixture(autouse=True)
def url_configurada(monkeypatch):
    monkeypatch.setattr(request_site, "config", {"URL": "https://exemplo.com.br"})


# --- base_url

def test_base_url_vem_do_env_file(monkeypatch):
    monkeypatch.setattr(request_site, "config", {"URL": "https://do-arquivo.com"})

    assert request_site.base_url() == "https://do-arquivo.com"


def test_base_url_cai_para_variavel_de_ambiente(monkeypatch):
    monkeypatch.setattr(request_site, "config", {})
    monkeypatch.setenv("URL", "https://do-ambiente.com")

    assert request_site.base_url() == "https://do-ambiente.com"


def test_base_url_remove_barra_final(monkeypatch):
    monkeypatch.setattr(request_site, "config", {"URL": "https://exemplo.com/"})

    assert request_site.base_url() == "https://exemplo.com"


def test_base_url_sem_configuracao_levanta_erro_claro(monkeypatch):
    monkeypatch.setattr(request_site, "config", {})
    monkeypatch.delenv("URL", raising=False)

    with pytest.raises(RuntimeError, match="URL"):
        request_site.base_url()


def test_importar_a_app_sem_env_e_sem_variaveis(tmp_path):
    """Regressão: a URL era montada no import, então `import app` estourava
    KeyError em qualquer ambiente sem .env — a CI inclusive.

    Roda em subprocesso com CWD vazio justamente para que o .env do repositório
    não esteja no caminho; um reload aqui dentro encontraria o arquivo real e o
    teste passaria mesmo com o bug de volta.
    """
    ambiente = {k: v for k, v in os.environ.items() if k != "URL"}
    ambiente["PYTHONPATH"] = str(RAIZ)

    resultado = subprocess.run(
        [sys.executable, "-c", "import app; print(app.app.title)"],
        cwd=tmp_path,
        env=ambiente,
        capture_output=True,
        text=True,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert "KeyError" not in resultado.stderr


# --- request_site

def test_extrai_avaliacoes_da_pagina(cache_temporario, scraper_falso):
    scraper_falso()

    feedbacks = request_site.request_site()

    assert feedbacks == [
        {
            "link": "https://exemplo.com.br/projeto/api-de-pagamentos",
            "title": "API de pagamentos",
            "comment": "Entregou antes do prazo.",
        },
        {
            "link": "https://exemplo.com.br/projeto/scraper",
            "title": "Scraper de dados",
            "comment": "Recomendo demais.",
        },
    ]


def test_ignora_projetos_cancelados(cache_temporario, scraper_falso):
    scraper_falso()

    feedbacks = request_site.request_site()

    assert all("Site institucional" != f["title"] for f in feedbacks)


def test_monta_a_url_do_perfil(cache_temporario, scraper_falso):
    dublê = scraper_falso()

    request_site.request_site()

    assert dublê.urls == ["https://exemplo.com.br/user/tio-mathias"]


def test_grava_o_cache_em_disco(cache_temporario, scraper_falso):
    scraper_falso()

    feedbacks = request_site.request_site()

    assert json.loads(cache_temporario.read_text(encoding="utf-8")) == feedbacks


def test_status_diferente_de_200_devolve_erro(cache_temporario, scraper_falso):
    scraper_falso(status_code=503, content="")

    assert request_site.request_site() == {"error": "fail to access site"}
    assert not cache_temporario.exists()


def test_pagina_sem_avaliacoes_devolve_lista_vazia(cache_temporario, scraper_falso):
    scraper_falso(content="<html><body><p>nada aqui</p></body></html>")

    assert request_site.request_site() == []


# --- get_feedbacks

def test_sem_cache_busca_no_site(cache_temporario, monkeypatch):
    chamou = []
    monkeypatch.setattr(request_site, "request_site", lambda: chamou.append(1) or ["novo"])

    assert request_site.get_feedbacks() == ["novo"]
    assert chamou == [1]


def test_cache_recente_e_lido_do_disco(cache_temporario, monkeypatch):
    cache_temporario.write_text('[{"title": "do cache"}]', encoding="utf-8")
    monkeypatch.setattr(
        request_site, "request_site", lambda: pytest.fail("não deveria acessar a rede")
    )

    assert request_site.get_feedbacks() == [{"title": "do cache"}]


def test_cache_vencido_dispara_nova_busca(cache_temporario, monkeypatch):
    cache_temporario.write_text('[{"title": "antigo"}]', encoding="utf-8")
    velho = time.time() - timedelta(days=1, hours=1).total_seconds()
    os.utime(cache_temporario, (velho, velho))
    monkeypatch.setattr(request_site, "request_site", lambda: ["recarregado"])

    assert request_site.get_feedbacks() == ["recarregado"]


def test_cache_na_fronteira_das_24h_ainda_vale(cache_temporario, monkeypatch):
    cache_temporario.write_text('[{"title": "quase vencido"}]', encoding="utf-8")
    quase = time.time() - timedelta(hours=23, minutes=50).total_seconds()
    os.utime(cache_temporario, (quase, quase))
    monkeypatch.setattr(
        request_site, "request_site", lambda: pytest.fail("não deveria acessar a rede")
    )

    assert request_site.get_feedbacks() == [{"title": "quase vencido"}]
