import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from scripts import request_site
from dotenv import dotenv_values

config = dotenv_values(".env")

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Matheus de Alencar Costa Oliveira - Portfólio",
    description="Meu portfólio oficial",
    version="2.2.0"
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


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
    return FileResponse(html_path)


@app.get("/pt")
@app.get("/pt/")
def index_pt():
    html_path = STATIC_DIR / "pt/index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Ocorreu um erro inesperado. entre em contato com o responsável.")
    return FileResponse(html_path)


@app.get("/reviews", summary="Get Reviews", tags=["Reviews"])
def get_reviews():
    feedbacks = request_site.get_feedbacks()
    if "error" in feedbacks:
        raise HTTPException(status_code=500, detail=feedbacks["error"])
    return feedbacks


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(config["PORT"]), server_header=False)
