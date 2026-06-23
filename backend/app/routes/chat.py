from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.rag.chains import ask_question

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(request: ChatRequest):
    try:
        result = ask_question(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))