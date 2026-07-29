from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ingest import ingest_from_parquet, DOCUMENTS_PARQUET, CHUNKS_PARQUET

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/")
def ingest(
    docs_path: str = Query(default=DOCUMENTS_PARQUET),
    chunks_path: str = Query(default=CHUNKS_PARQUET),
    db: Session = Depends(get_db),
):
    try:
        result = ingest_from_parquet(db, docs_path=docs_path, chunks_path=chunks_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok", **result}