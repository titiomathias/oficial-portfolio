import json
import pytest
from fastapi.testclient import TestClient
from jinja2 import Environment
import app as app_module
from scripts import blog

def fonte_de_post(meta, body="<p>corpo</p>"):
    """Monta o source de um post.

    json.dumps em vez de %-formatting ou .format(): o template é cheio de
    `{% %}` e `{{ }}`, que colidem com os dois.
    """
    return (
        '{% extends "blog/post.html" %}\n'
        "{% set post = " + json.dumps(meta, ensure_ascii=False) + " %}\n"
        "{% block post_body %}" + body + "{% endblock %}\n"
    )


@pytest.fixture(autouse=True)
def limpa_cache_do_blog():
    """O registro de posts tem cache global por arquivo; sem limpar, um teste
    contamina o próximo."""
    blog._cache.clear()
    yield
    blog._cache.clear()


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.fixture
def env():
    """Environment sem loader: a extração de metadados usa env.parse(), que
    trabalha sobre a string e não precisa resolver o {% extends %}."""
    return Environment()


@pytest.fixture
def posts_dir(tmp_path):
    (tmp_path / blog.POSTS_DIR).mkdir(parents=True)
    return tmp_path


@pytest.fixture
def escrever_post(posts_dir):
    """Cria um post no diretório temporário e devolve o caminho."""

    def _escrever(slug, body="<p>corpo</p>", **meta):
        path = posts_dir / blog.POSTS_DIR / f"{slug}.html"
        path.write_text(fonte_de_post(meta, body), encoding="utf-8")
        return path

    return _escrever


@pytest.fixture
def post_temporario():
    """Cria um post de verdade em templates/blog/posts/ e remove no teardown.

    Necessário nos testes de rota: renderizar exige que o loader do Jinja
    encontre o arquivo, então tmp_path não serve.
    """
    criados = []

    def _criar(slug, title, date, summary="resumo", tags=("teste",)):
        path = app_module.TEMPLATES_DIR / blog.POSTS_DIR / f"{slug}.html"
        meta = {"title": title, "date": date, "summary": summary, "tags": list(tags)}
        path.write_text(fonte_de_post(meta, "<p>corpo do post</p>"), encoding="utf-8")
        criados.append(path)
        return path

    yield _criar

    for path in criados:
        path.unlink(missing_ok=True)
