from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import QuestionRequest, QuestionResponse
from app.services.query import ask

router = APIRouter(prefix="/ask", tags=["query"])


@router.post("/", response_model=QuestionResponse)
def query(request: QuestionRequest, db: Session = Depends(get_db)):
    try:
        result = ask(
            db,
            question=request.question,
            k=request.k,
            category=request.category,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result