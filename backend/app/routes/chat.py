from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.memory.session_store import clear_session, clear_all_sessions
from app.rag.chains import ask_question, stream_question, preview_retrieval, get_vectorstore_stats, ask_question_hybrid

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str
    source_type: Optional[str] = None
    filename: Optional[str] = None
    session_id: Optional[str] = "default"


@router.post("/ask")
def ask(request: ChatRequest):
    try:
        result = ask_question(
            question=request.question,
            source_type=request.source_type,
            filename=request.filename,
            session_id=request.session_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
def reset_session(session_id: str):
    clear_session(session_id)
    return {
        "message": "Session memory cleared successfully.",
        "session_id": session_id,
    }


@router.delete("/sessions")
def reset_all_sessions():
    clear_all_sessions()
    return {
        "message": "All session memories cleared successfully.",
    }
    
@router.post("/stream")
def stream(request: ChatRequest):
    try:
        return StreamingResponse(
            stream_question(
                question=request.question,
                source_type=request.source_type,
                filename=request.filename,
                session_id=request.session_id,
            ),
            media_type="text/plain",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preview-retrieval")
def preview(request: ChatRequest):
    try:
        return preview_retrieval(
            question=request.question,
            source_type=request.source_type,
            filename=request.filename,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def stats():
    try:
        return get_vectorstore_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/ask-hybrid")
def ask_hybrid(request: ChatRequest):
    try:
        return ask_question_hybrid(
            question=request.question,
            source_type=request.source_type,
            filename=request.filename,
            session_id=request.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))