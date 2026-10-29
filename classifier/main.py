import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

try:
    from .router import route
except ImportError:  # pragma: no cover - script execution fallback
    from router import route


class PromptRequest(BaseModel):
    prompt: str


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/prompt/classification")
def classify_prompt(payload: PromptRequest):
    return route(payload.prompt)

if __name__ == "__main__":
    # Set your custom port here
    uvicorn.run("main:app", host="127.0.0.1", port=8085, reload=True)