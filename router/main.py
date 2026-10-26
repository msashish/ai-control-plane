from fastapi import FastAPI
from pydantic import BaseModel

from router.app import route


class PromptRequest(BaseModel):
    prompt: str


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/prompt/classification")
def classify_prompt(payload: PromptRequest):
    return route(payload.prompt)
