from fastapi import FastAPI
from app.routers import ingest

app = FastAPI(title="RAG API")


@app.get("/")
def health_check():
    return {"status": "ok"}

app.include_router(ingest.router)