from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.rag.chains import ask_question

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str
    source_type: Optional[str] = None
    filename: Optional[str] = None


@router.post("/ask")
def ask(request: ChatRequest):
    try:
        result = ask_question(
            question=request.question,
            source_type=request.source_type,
            filename=request.filename,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))