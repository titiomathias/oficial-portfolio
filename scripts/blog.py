import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from jinja2 import nodes

POSTS_DIR = "blog/posts"
POST_LAYOUT = "blog/post.html"

WORDS_PER_MINUTE = 200

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
_MARKUP_RE = re.compile(r"{%.*?%}|{{.*?}}|{#.*?#}|<[^>]+>", re.DOTALL)

_cache: dict[str, tuple[int, "Post"]] = {}


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    date: datetime
    summary: str
    tags: tuple[str, ...]
    reading_time: int
    template: str

    @property
    def url(self) -> str:
        return f"/blog/{self.slug}"

    @property
    def date_iso(self) -> str:
        if (self.date.hour, self.date.minute, self.date.second) == (0, 0, 0):
            return self.date.date().isoformat()
        return self.date.isoformat(timespec="minutes")

    @property
    def date_display(self) -> str:
        return self.date.strftime("%d.%m.%Y")


def _parse_date(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.fromisoformat(str(value).strip())


def _reading_time(source: str) -> int:
    words = len(_MARKUP_RE.sub(" ", source).split())
    return max(1, round(words / WORDS_PER_MINUTE))


def _extract_meta(env, source: str, name: str) -> dict | None:
    for node in env.parse(source, name=name).body:
        if (
            isinstance(node, nodes.Assign)
            and isinstance(node.target, nodes.Name)
            and node.target.name == "post"
        ):
            try:
                return node.node.as_const()
            except nodes.Impossible as exc:
                raise ValueError("os metadados precisam ser valores literais") from exc
    return None


def _build(env, path: Path) -> Post:
    slug = path.stem
    name = f"{POSTS_DIR}/{slug}.html"
    source = path.read_text(encoding="utf-8")
    meta = _extract_meta(env, source, name)

    if not isinstance(meta, dict):
        raise ValueError("falta o bloco {% set post = {...} %} no topo do arquivo")
    if not meta.get("title"):
        raise ValueError("metadado 'title' é obrigatório")
    if not meta.get("date"):
        raise ValueError("metadado 'date' é obrigatório (formato AAAA-MM-DD)")

    return Post(
        slug=slug,
        title=str(meta["title"]),
        date=_parse_date(meta["date"]),
        summary=str(meta.get("summary", "")),
        tags=tuple(str(tag) for tag in meta.get("tags", ())),
        reading_time=int(meta.get("reading_time") or _reading_time(source)),
        template=name,
    )


def _load(env, path: Path) -> Post | None:
    """Carrega um post do disco, reaproveitando o cache enquanto o arquivo não mudar."""
    key = str(path)
    mtime = path.stat().st_mtime_ns
    cached = _cache.get(key)
    if cached and cached[0] == mtime:
        return cached[1]

    try:
        post = _build(env, path)
    except Exception as exc:
        print(f"[blog] ignorando {path.name}: {exc}", file=sys.stderr)
        _cache.pop(key, None)
        return None

    _cache[key] = (mtime, post)
    return post


def all_posts(env, templates_dir: Path) -> list[Post]:
    """Todos os posts publicados, do mais recente para o mais antigo."""
    posts_dir = templates_dir / POSTS_DIR
    if not posts_dir.is_dir():
        return []

    posts = []
    for path in posts_dir.glob("*.html"):
        if not _SLUG_RE.match(path.stem):
            print(f"[blog] ignorando {path.name}: slug inválido", file=sys.stderr)
            continue
        post = _load(env, path)
        if post is not None:
            posts.append(post)

    posts.sort(key=lambda post: (post.date, post.slug), reverse=True)
    return posts


def get_post(env, templates_dir: Path, slug: str) -> Post | None:
    """Busca um post pelo slug. Retorna ``None`` se não existir."""
    if not _SLUG_RE.match(slug):
        return None
    path = templates_dir / POSTS_DIR / f"{slug}.html"
    if not path.is_file():
        return None
    return _load(env, path)


def neighbours(posts: list[Post], slug: str) -> tuple[Post | None, Post | None]:
    """Devolve (mais novo, mais antigo) em relação ao post do slug."""
    slugs = [post.slug for post in posts]
    if slug not in slugs:
        return None, None
    index = slugs.index(slug)
    newer = posts[index - 1] if index > 0 else None
    older = posts[index + 1] if index + 1 < len(posts) else None
    return newer, older


def all_tags(posts: list[Post]) -> list[str]:
    return sorted({tag for post in posts for tag in post.tags})
