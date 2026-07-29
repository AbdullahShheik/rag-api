from fastapi import FastAPI

app = FastAPI(title="RAG API")


@app.get("/")
def health_check():
    return {"status": "ok"}