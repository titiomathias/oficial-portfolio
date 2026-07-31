import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from scripts import blog, request_site
from dotenv import dotenv_values

config = dotenv_values(".env")

STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"

app = FastAPI(
    title="Matheus de Alencar Costa Oliveira - Portfólio",
    description="Meu portfólio oficial",
    version="2.2.0",
    docs_url=None
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/health")
def health():
    return {
        "status":"OK"
    }


@app.get("")
@app.get("/")
def index():
    html_path = STATIC_DIR / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="ocorreu um erro inesperado. entre em contato com o responsável.")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/pt")
@app.get("/pt/")
def index_pt():
    html_path = STATIC_DIR / "pt/index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Ocorreu um erro inesperado. entre em contato com o responsável.")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/linktree", include_in_schema=False)
@app.get("/linktree/")
def get_linktree(request: Request):
    return templates.TemplateResponse(request, "linktree.html", {
        "nav_active": "linktree",
    })


@app.get("/reviews", summary="Get Reviews", tags=["Reviews"])
def get_reviews():
    feedbacks = request_site.get_feedbacks()
    if "error" in feedbacks:
        raise HTTPException(status_code=500, detail=feedbacks["error"])
    return feedbacks


@app.get("/blog", include_in_schema=False)
@app.get("/blog/")
def get_blog(request: Request):
    posts = blog.all_posts(templates.env, TEMPLATES_DIR)
    return templates.TemplateResponse(request, "blog/index.html", {
        "posts": posts,
        "tags": blog.all_tags(posts),
        "nav_active": "blog",
    })


@app.get("/blog/{slug}")
def get_blog_post(request: Request, slug: str):
    post = blog.get_post(templates.env, TEMPLATES_DIR, slug)
    if post is None:
        raise HTTPException(status_code=404, detail="Post não encontrado.")

    newer, older = blog.neighbours(blog.all_posts(templates.env, TEMPLATES_DIR), slug)
    return templates.TemplateResponse(request, post.template, {
        "meta": post,
        "newer": newer,
        "older": older,
        "nav_active": "blog",
    })

# Probe client
#@app.get("/_probe")
#async def probe(request: Request):
#    return {
#        "client_host": request.client.host if request.client else None,
#        "headers": dict(request.headers),
#    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(config["PORT"]), server_header=False)
