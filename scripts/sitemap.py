import datetime
from pathlib import Path
from xml.sax.saxutils import escape

SITE = "https://matheusdealencar.com"

HOME_ALTERNATES = (
    ("en", f"{SITE}/"),
    ("pt-br", f"{SITE}/pt/"),
    ("x-default", f"{SITE}/"),
)

def _lastmod(path: Path) -> str | None:
    try:
        return datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()
    except OSError:
        return None


def _entry(loc, lastmod=None, changefreq=None, priority=None, alternates=()) -> str:
    lines = [f"        <loc>{escape(loc)}</loc>"]
    for hreflang, href in alternates:
        lines.append(
            f'        <xhtml:link rel="alternate" hreflang="{hreflang}" href="{escape(href)}"/>'
        )
    if lastmod:
        lines.append(f"        <lastmod>{lastmod}</lastmod>")
    if changefreq:
        lines.append(f"        <changefreq>{changefreq}</changefreq>")
    if priority:
        lines.append(f"        <priority>{priority}</priority>")
    body = "\n".join(lines)
    return f"    <url>\n{body}\n    </url>"


def build(posts, static_dir: Path, templates_dir: Path) -> str:
    """Monta o XML. ``posts`` vem de ``blog.all_posts`` (mais recente primeiro)."""
    newest = posts[0].date.date().isoformat() if posts else None

    entries = [
        _entry(
            f"{SITE}/",
            lastmod=_lastmod(static_dir / "index.html"),
            changefreq="monthly",
            priority="1.0",
            alternates=HOME_ALTERNATES,
        ),
        _entry(
            f"{SITE}/pt/",
            lastmod=_lastmod(static_dir / "pt" / "index.html"),
            changefreq="monthly",
            priority="1.0",
            alternates=HOME_ALTERNATES,
        ),
        _entry(
            f"{SITE}/blog/",
            lastmod=newest,
            changefreq="weekly",
            priority="0.8",
        ),
        _entry(
            f"{SITE}/linktree",
            lastmod=_lastmod(templates_dir / "linktree.html"),
            changefreq="monthly",
            priority="0.5",
        ),
    ]

    entries += [
        _entry(
            f"{SITE}{post.url}",
            lastmod=post.date.date().isoformat(),
            changefreq="yearly",
            priority="0.7",
        )
        for post in posts
    ]

    urls = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
