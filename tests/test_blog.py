import os
from datetime import datetime
import pytest
from scripts import blog

def test_le_metadados_do_proprio_template(env, posts_dir, escrever_post):
    escrever_post(
        "primeiro-commit",
        title="Primeiro commit",
        date="2026-07-29",
        summary="Um resumo curto.",
        tags=["python", "fastapi"],
    )

    post = blog.get_post(env, posts_dir, "primeiro-commit")

    assert post.slug == "primeiro-commit"
    assert post.title == "Primeiro commit"
    assert post.date == datetime(2026, 7, 29)
    assert post.summary == "Um resumo curto."
    assert post.tags == ("python", "fastapi")
    assert post.template == "blog/posts/primeiro-commit.html"


def test_summary_e_tags_sao_opcionais(env, posts_dir, escrever_post):
    escrever_post("sem-extras", title="Sem extras", date="2026-07-29")

    post = blog.get_post(env, posts_dir, "sem-extras")

    assert post.summary == ""
    assert post.tags == ()


def test_url_derivada_do_slug(env, posts_dir, escrever_post):
    escrever_post("meu-post", title="T", date="2026-01-02")

    assert blog.get_post(env, posts_dir, "meu-post").url == "/blog/meu-post"


# --- datas ------------------------------------------------------------------


def test_data_sem_hora_vira_meia_noite_e_iso_omite_a_hora(env, posts_dir, escrever_post):
    escrever_post("sem-hora", title="T", date="2026-07-29")

    post = blog.get_post(env, posts_dir, "sem-hora")

    assert post.date == datetime(2026, 7, 29, 0, 0)
    assert post.date_iso == "2026-07-29"
    assert post.date_display == "29.07.2026"


def test_hora_informada_aparece_no_iso(env, posts_dir, escrever_post):
    escrever_post("com-hora", title="T", date="2026-07-29 21:30")

    post = blog.get_post(env, posts_dir, "com-hora")

    assert post.date == datetime(2026, 7, 29, 21, 30)
    assert post.date_iso == "2026-07-29T21:30"
    assert post.date_display == "29.07.2026"



# --- ordenação

def test_ordena_do_mais_recente_para_o_mais_antigo(env, posts_dir, escrever_post):
    escrever_post("antigo", title="Antigo", date="2025-01-01")
    escrever_post("novo", title="Novo", date="2026-12-31")
    escrever_post("meio", title="Meio", date="2026-06-15")

    assert [p.slug for p in blog.all_posts(env, posts_dir)] == ["novo", "meio", "antigo"]


def test_hora_desempata_posts_do_mesmo_dia(env, posts_dir, escrever_post):
    escrever_post("manha", title="Manhã", date="2026-07-29 08:00")
    escrever_post("noite", title="Noite", date="2026-07-29 22:00")

    assert [p.slug for p in blog.all_posts(env, posts_dir)] == ["noite", "manha"]


def test_diretorio_de_posts_ausente_nao_quebra(env, tmp_path):
    assert blog.all_posts(env, tmp_path) == []


# --- tempo de leitura

def test_tempo_de_leitura_estimado_pelo_texto(env, posts_dir, escrever_post):
    # 600 palavras / 200 wpm = 3 min
    escrever_post("longo", title="T", date="2026-01-01", body="<p>" + "palavra " * 600 + "</p>")

    assert blog.get_post(env, posts_dir, "longo").reading_time == 3


def test_tempo_de_leitura_ignora_marcacao(env, posts_dir, escrever_post):
    """Tags Jinja e HTML não devem contar como texto lido."""
    ruido = "{% if true %}<div class='x'><span>{{ variavel }}</span></div>{% endif %}" * 200
    escrever_post("so-marcacao", title="T", date="2026-01-01", body=ruido)

    assert blog.get_post(env, posts_dir, "so-marcacao").reading_time == 1


def test_tempo_de_leitura_minimo_de_um_minuto(env, posts_dir, escrever_post):
    escrever_post("curtinho", title="T", date="2026-01-01", body="<p>oi</p>")

    assert blog.get_post(env, posts_dir, "curtinho").reading_time == 1


def test_tempo_de_leitura_explicito_vence_a_estimativa(env, posts_dir, escrever_post):
    escrever_post(
        "fixo",
        title="T",
        date="2026-01-01",
        reading_time=42,
        body="<p>" + "palavra " * 600 + "</p>",
    )

    assert blog.get_post(env, posts_dir, "fixo").reading_time == 42


# --- posts inválido

@pytest.mark.parametrize(
    "fonte, motivo",
    [
        ('{% extends "blog/post.html" %}\n<p>sem metadados</p>', "falta o bloco set"),
        ('{% set post = {"date": "2026-01-01"} %}', "sem title"),
        ('{% set post = {"title": "T"} %}', "sem date"),
        ('{% set post = "nao e um dicionario" %}', "nao e dict"),
        ('{% set post = {"title": alguma_variavel, "date": "2026-01-01"} %}', "nao literal"),
        ('{% set outra_coisa = {"title": "T"} %}', "nome errado da variavel"),
    ],
)
def test_post_malformado_e_ignorado_sem_derrubar_a_listagem(
    env, posts_dir, escrever_post, capsys, fonte, motivo
):
    escrever_post("valido", title="Válido", date="2026-01-01")
    (posts_dir / blog.POSTS_DIR / "quebrado.html").write_text(fonte, encoding="utf-8")

    posts = blog.all_posts(env, posts_dir)

    assert [p.slug for p in posts] == ["valido"], motivo
    assert "quebrado.html" in capsys.readouterr().err


def test_data_invalida_e_ignorada(env, posts_dir, escrever_post):
    escrever_post("data-ruim", title="T", date="29/07/2026")

    assert blog.all_posts(env, posts_dir) == []


@pytest.mark.parametrize("slug", ["Maiusculo", "com espaco", "-comeca-com-hifen", "acentuação"])
def test_slug_invalido_e_ignorado_na_listagem(env, posts_dir, slug):
    fonte = '{% set post = {"title": "T", "date": "2026-01-01"} %}'
    (posts_dir / blog.POSTS_DIR / f"{slug}.html").write_text(fonte, encoding="utf-8")

    assert blog.all_posts(env, posts_dir) == []


# --- busca por slug

def test_get_post_retorna_none_quando_nao_existe(env, posts_dir):
    assert blog.get_post(env, posts_dir, "nunca-escrito") is None


@pytest.mark.parametrize(
    "slug",
    ["../../../etc/passwd", "..", ".", "../conftest", "posts/../../app", "/etc/passwd", ""],
)
def test_get_post_recusa_travessia_de_caminho(env, posts_dir, slug):
    assert blog.get_post(env, posts_dir, slug) is None


# --- vizinhos

def test_neighbours_aponta_para_mais_novo_e_mais_antigo(env, posts_dir, escrever_post):
    escrever_post("antigo", title="Antigo", date="2025-01-01")
    escrever_post("meio", title="Meio", date="2026-06-15")
    escrever_post("novo", title="Novo", date="2026-12-31")
    posts = blog.all_posts(env, posts_dir)

    newer, older = blog.neighbours(posts, "meio")

    assert newer.slug == "novo"
    assert older.slug == "antigo"


def test_neighbours_nos_extremos(env, posts_dir, escrever_post):
    escrever_post("antigo", title="Antigo", date="2025-01-01")
    escrever_post("novo", title="Novo", date="2026-12-31")
    posts = blog.all_posts(env, posts_dir)

    assert blog.neighbours(posts, "novo") == (None, posts[1])
    assert blog.neighbours(posts, "antigo") == (posts[0], None)


def test_neighbours_com_post_unico(env, posts_dir, escrever_post):
    escrever_post("sozinho", title="Sozinho", date="2026-01-01")
    posts = blog.all_posts(env, posts_dir)

    assert blog.neighbours(posts, "sozinho") == (None, None)


def test_neighbours_com_slug_desconhecido(env, posts_dir, escrever_post):
    escrever_post("existe", title="Existe", date="2026-01-01")
    posts = blog.all_posts(env, posts_dir)

    assert blog.neighbours(posts, "nao-existe") == (None, None)


# --- tags -------------------------------------------------------------------


def test_all_tags_deduplica_e_ordena(env, posts_dir, escrever_post):
    escrever_post("a", title="A", date="2026-01-01", tags=["python", "fastapi"])
    escrever_post("b", title="B", date="2026-01-02", tags=["python", "css"])
    escrever_post("c", title="C", date="2026-01-03")

    assert blog.all_tags(blog.all_posts(env, posts_dir)) == ["css", "fastapi", "python"]


# --- cache

def test_cache_reaproveita_o_post_enquanto_o_arquivo_nao_muda(env, posts_dir, escrever_post):
    escrever_post("cacheado", title="Original", date="2026-01-01")

    primeiro = blog.get_post(env, posts_dir, "cacheado")
    segundo = blog.get_post(env, posts_dir, "cacheado")

    assert primeiro is segundo


def test_cache_invalida_quando_o_arquivo_muda(env, posts_dir, escrever_post):
    path = escrever_post("editado", title="Original", date="2026-01-01")
    antes = blog.get_post(env, posts_dir, "editado")

    escrever_post("editado", title="Reescrito", date="2026-01-01")
    mtime = path.stat().st_mtime + 10
    os.utime(path, (mtime, mtime))

    depois = blog.get_post(env, posts_dir, "editado")

    assert antes.title == "Original"
    assert depois.title == "Reescrito"
    assert depois is not antes


def test_post_que_passa_a_ser_invalido_sai_do_cache(env, posts_dir, escrever_post):
    path = escrever_post("regride", title="Válido", date="2026-01-01")
    assert blog.get_post(env, posts_dir, "regride") is not None

    path.write_text("<p>sem metadados</p>", encoding="utf-8")
    mtime = path.stat().st_mtime + 10
    os.utime(path, (mtime, mtime))

    assert blog.get_post(env, posts_dir, "regride") is None
