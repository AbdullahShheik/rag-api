import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2


class Document(Base):
    __tablename__ = "documents"

    source_id = Column(String, primary_key=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    authors = Column(JSONB)
    categories = Column(JSONB)
    published = Column(String)
    updated = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String, ForeignKey("documents.source_id"), nullable=False)
    section_id = Column(String)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM))
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")