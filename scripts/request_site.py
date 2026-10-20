import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import cloudscraper
import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values

ROOT_DIR = Path(__file__).resolve().parent.parent

config = dotenv_values(ROOT_DIR / ".env")

FILE_PATH = Path(__file__).parent / "feedbacks.json"

CACHE_TTL = timedelta(days=1)
RETRY_DELAY = timedelta(hours=1)
TIMEOUT = 15

FETCH_ERROR = {"error": "fail to access site"}

_next_retry: datetime | None = None


def base_url() -> str:
    base = config.get("URL") or os.getenv("URL")
    if not base:
        raise RuntimeError("variável URL não configurada (.env ou ambiente)")
    return base.rstrip("/")


def mirror_url() -> str:
    return (config.get("FEEDBACKS_MIRROR") or os.getenv("FEEDBACKS_MIRROR") or "").strip()


def _failed(result) -> bool:
    return isinstance(result, dict) and "error" in result


def _parse(html, base: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    feedbacks = []

    for item in soup.find_all("li", class_="box-loader-item"):
        left_elements = item.find_all(class_="project-info-left")
        right_elements = item.find_all(class_="project-info-right")

        for p, x in zip(left_elements, right_elements):
            if "Cancelado" in x.get_text():
                continue
            feedbacks.append({
                "link": f"{base}{p.a.get('href')}",
                "title": p.a.get_text().strip(),
                "comment": p.find(class_="project-comment").get_text().strip(),
            })

    return feedbacks


def _read_cache() -> list | None:
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            cache = json.load(file)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as erro:
        print(f"cache {FILE_PATH} ilegível: {erro}", file=sys.stderr)
        return None

    return cache if isinstance(cache, list) else None


def _write_cache(feedbacks: list[dict]) -> None:
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(feedbacks, file, ensure_ascii=False, indent=4)


def _cache_is_fresh() -> bool:
    try:
        modified = datetime.fromtimestamp(os.path.getmtime(FILE_PATH))
    except OSError:
        return False
    return datetime.now() - modified < CACHE_TTL


def _retry_allowed() -> bool:
    return _next_retry is None or datetime.now() >= _next_retry


def _hold_retries() -> None:
    """Segura novas tentativas por RETRY_DELAY.

    Sem isso cada acesso a /reviews com o cache vencido dispara um request
    novo ao Cloudflare — todos bloqueados, todos pagos em latência.
    """
    global _next_retry
    _next_retry = datetime.now() + RETRY_DELAY


def request_site():
    base = base_url()
    scraper = cloudscraper.create_scraper()

    try:
        response = scraper.get(f"{base}/user/tio-mathias", timeout=TIMEOUT)
    except Exception as erro:
        print(f"falha ao acessar {base}: {erro}", file=sys.stderr)
        return dict(FETCH_ERROR)

    if response.status_code != 200:
        print(f"{base} respondeu {response.status_code}", file=sys.stderr)
        return dict(FETCH_ERROR)

    feedbacks = _parse(response.content, base)
    _write_cache(feedbacks)
    return feedbacks


def request_mirror():
    url = mirror_url()
    if not url:
        return dict(FETCH_ERROR)

    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        feedbacks = response.json()
    except (requests.RequestException, ValueError) as erro:
        print(f"falha ao ler o espelho {url}: {erro}", file=sys.stderr)
        return dict(FETCH_ERROR)

    if not isinstance(feedbacks, list):
        print(f"espelho {url} não devolveu uma lista", file=sys.stderr)
        return dict(FETCH_ERROR)

    _write_cache(feedbacks)
    return feedbacks


def get_feedbacks():
    cache = _read_cache()

    if cache is not None and _cache_is_fresh():
        return cache

    if not _retry_allowed():
        return cache if cache is not None else dict(FETCH_ERROR)

    feedbacks = request_site()

    if _failed(feedbacks):
        feedbacks = request_mirror()

    if _failed(feedbacks):
        _hold_retries()
        # cache vencido é melhor que /reviews devolvendo 500
        return cache if cache is not None else dict(FETCH_ERROR)

    return feedbacks


def main() -> int:
    """Coleta forçada, usada pela CI e por uma máquina local."""
    feedbacks = request_site()

    if _failed(feedbacks):
        print("não foi possível coletar as avaliações", file=sys.stderr)
        return 1

    print(f"{len(feedbacks)} avaliações gravadas em {FILE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
