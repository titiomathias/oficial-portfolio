import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.templating import Jinja2Templates
from pathlib import Path
from scripts import request_site, sitemap
from dotenv import dotenv_values
import os

ROOT_DIR = Path(__file__).resolve().parent

config = dotenv_values(ROOT_DIR / ".env")

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
    return templates.TemplateResponse(request, "linktree.html", {})


@app.get("/reviews", summary="Get Reviews", tags=["Reviews"])
def get_reviews():
    feedbacks = request_site.get_feedbacks()
    if "error" in feedbacks:
        raise HTTPException(status_code=500, detail=feedbacks["error"])
    return feedbacks


# Probe client
#@app.get("/_probe")
#async def probe(request: Request):
#    return {
#        "client_host": request.client.host if request.client else None,
#        "headers": dict(request.headers),
#    }

@app.get("/robots.txt")
def robots():
    return FileResponse(STATIC_DIR/"robots.txt")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(STATIC_DIR/"favicon.ico")


@app.get("/sitemap.xml", include_in_schema=False)
def get_sitemap():
    xml = sitemap.build(STATIC_DIR, TEMPLATES_DIR)
    return Response(xml, media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(config.get("PORT") or os.getenv("PORT") or 8000), server_header=False)
