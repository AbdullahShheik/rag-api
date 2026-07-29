import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ---------- Document schemas ----------
class DocumentOut(BaseModel):
    source_id: str
    title: str
    abstract: Optional[str]
    authors: Optional[list]
    categories: Optional[list]
    published: Optional[str]
    updated: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Chunk schemas ----------
class ChunkOut(BaseModel):
    id: uuid.UUID
    document_id: str
    section_id: Optional[str]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Query schemas ----------
class QuestionRequest(BaseModel):
    question: str
    k: int = 3
    category: Optional[str] = None


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[ChunkOut]