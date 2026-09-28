from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import chat, keys, models, prompts, proxy, spend, teams, users

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="GSA LiteLLM Manager", version="0.1.0")

app.include_router(models.router)
app.include_router(chat.router)
app.include_router(keys.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(spend.router)
app.include_router(prompts.router)
app.include_router(proxy.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
