from fastapi import FastAPI
from fastapi import FastAPI

app = FastAPI(title="Organizations Directory API")


@app.get("/health")
def health_check():
    return {"status": "ok"}

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
