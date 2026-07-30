import re
import pytest
import app as app_module

MAIN_CSS = (app_module.STATIC_DIR / "css" / "main.css").read_text(encoding="utf-8")

ELEMENTOS_ESTRUTURAIS = ["header", "footer", "section", "main", "article", "nav"]


@pytest.mark.parametrize("elemento", ELEMENTOS_ESTRUTURAIS)
def test_seletor_de_elemento_estrutural_e_escopado_em_body(elemento):
    sem_escopo = re.findall(r"^[ \t]*%s\s*\{" % elemento, MAIN_CSS, re.MULTILINE)

    assert sem_escopo == [], (
        "`%s {` sem escopo no main.css vaza para os elementos aninhados do blog; "
        "use `body > %s {`" % (elemento, elemento)
    )
