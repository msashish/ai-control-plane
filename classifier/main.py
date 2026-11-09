import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
import os

try:
    from .router import route, warm_up
except ImportError:  # pragma: no cover - script execution fallback
    from router import route, warm_up


class PromptRequest(BaseModel):
    prompt: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uvicorn binds port only after startup completes, so /health is unreachable until model is loaded
    warm_up()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/prompt/classification")
def classify_prompt(payload: PromptRequest):
    return route(payload.prompt)

if __name__ == "__main__":
    # Set your custom port here
    reload_enabled = os.getenv("CLASSIFIER_RELOAD", "false").lower() == "true"
    uvicorn.run("main:app", host="127.0.0.1", port=8085, reload=reload_enabled)