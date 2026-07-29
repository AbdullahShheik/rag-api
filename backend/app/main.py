from fastapi import FastAPI
from app.routers import ingest, query

app = FastAPI(title="RAG API")


@app.get("/")
def health_check():
    return {"status": "ok"}


app.include_router(ingest.router)
app.include_router(query.router)