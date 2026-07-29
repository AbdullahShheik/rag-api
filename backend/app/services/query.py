import os
from sqlalchemy.orm import Session
from sqlalchemy import String
from fastembed import TextEmbedding
from google.generativeai import GenerativeModel
import google.generativeai as genai

from app.models import Chunk, Document


_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
    return _embedder


def get_llm() -> GenerativeModel:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    return GenerativeModel("gemini-3.6-flash")


def retrieve_chunks(
    db: Session,
    question_vector: list,
    k: int = 3,
    category: str = None,
) -> list:
    try:
        query = db.query(Chunk)

        if category:
            query = (
                query.join(Document, Chunk.document_id == Document.source_id)
                .filter(Document.categories.cast(String).ilike(f"%{category}%"))
            )

        results = (
            query
            .order_by(Chunk.embedding.cosine_distance(question_vector))
            .limit(k)
            .all()
        )
        return results
    except Exception as e:
        raise RuntimeError(f"Vector search failed: {e}") from e


def generate_answer(question: str, chunks: list) -> str:
    context = "\n\n".join(chunk.content for chunk in chunks)
    prompt = f"""Answer the question using only the context below.
If the context doesn't contain the answer, say so.

Context:
{context}

Question: {question}
Answer:"""

    try:
        llm = get_llm()
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        raise RuntimeError(f"LLM generation failed: {e}") from e


def ask(db: Session, question: str, k: int = 3, category: str = None) -> dict:
    embedder = get_embedder()

    try:
        question_vector = list(embedder.embed([question]))[0].tolist()
    except Exception as e:
        raise RuntimeError(f"Embedding failed: {e}") from e

    chunks = retrieve_chunks(db, question_vector, k=k, category=category)

    if not chunks:
        return {
            "question": question,
            "answer": "No relevant chunks found in the database.",
            "sources": [],
        }

    answer = generate_answer(question, chunks)

    return {
        "question": question,
        "answer": answer,
        "sources": chunks,
    }