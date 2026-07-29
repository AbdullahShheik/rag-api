import uuid
import json
import pandas as pd
from sqlalchemy.orm import Session

from app.models import Document, Chunk


DATA_DIR = "/app/data" 
DOCUMENTS_PARQUET = f"{DATA_DIR}/documents.parquet"
CHUNKS_PARQUET = f"{DATA_DIR}/chunks.parquet"


def _parse_json_col(value):
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return value


def ingest_from_parquet(
    db: Session,
    docs_path: str = DOCUMENTS_PARQUET,
    chunks_path: str = CHUNKS_PARQUET,
) -> dict:
    try:
        df_docs = pd.read_parquet(docs_path)
        df_chunks = pd.read_parquet(chunks_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Parquet file not found: {e.filename}") from e

    docs_inserted = 0
    docs_skipped = 0
    chunks_inserted = 0
    chunks_skipped = 0

    try:
        for _, row in df_docs.iterrows():
            existing = db.query(Document).filter(
                Document.source_id == row["source_id"]
            ).first()

            if existing:
                docs_skipped += 1
                continue

            db.add(Document(
                source_id=row["source_id"],
                title=row["title"],
                abstract=row.get("abstract"),
                authors=_parse_json_col(row.get("authors")),
                categories=_parse_json_col(row.get("categories")),
                published=row.get("published"),
                updated=row.get("updated"),
            ))
            docs_inserted += 1

        db.commit()
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to insert documents: {e}") from e

    try:
        rows = df_chunks.to_dict(orient="records")
        for i in range(0, len(rows), 500):
            batch = rows[i : i + 500]
            for row in batch:
                embedding = row.get("embedding")
                if embedding is None:
                    chunks_skipped += 1
                    continue

                db.add(Chunk(
                    id=uuid.uuid4(),
                    document_id=row["source_id"],
                    section_id=str(row.get("section_id", "")),
                    content=row["content"],
                    embedding=embedding if isinstance(embedding, list) else embedding.tolist(),
                ))
                chunks_inserted += 1

            db.commit()

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to insert chunks at batch ~{i}: {e}") from e

    return {
        "documents_inserted": docs_inserted,
        "documents_skipped": docs_skipped,
        "chunks_inserted": chunks_inserted,
        "chunks_skipped": chunks_skipped,
    }