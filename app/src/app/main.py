from fastapi import FastAPI
import uvicorn

app = FastAPI(title="app")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "hello world"}


def main() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
