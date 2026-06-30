import os
import shutil
from pydantic import BaseModel
from app.ingest.web_loader import load_and_chunk_website
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.core.config import settings
from app.ingest.pdf_loader import load_and_chunk_pdf
from app.rag.vectorstore import get_vectorstore
from app.ingest.youtube_loader import load_and_chunk_youtube
from app.sources.registry import list_sources

router = APIRouter(prefix="/documents", tags=["Documents"])

class WebsiteIngestRequest(BaseModel):
    url: str
    chunk_size: int = 1000
    chunk_overlap: int = 200

class YouTubeIngestRequest(BaseModel):
    url: str
    chunk_size: int = 1000
    chunk_overlap: int = 200

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunks = load_and_chunk_pdf(
            file_path=file_path,
            original_filename=file.filename,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        
        if chunk_size <= 0:
            raise HTTPException(status_code=400, detail="chunk_size must be greater than 0.")

        if chunk_overlap < 0:
            raise HTTPException(status_code=400, detail="chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise HTTPException(status_code=400, detail="chunk_overlap must be smaller than chunk_size.")

        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)

        return {
            "message": "PDF uploaded and ingested successfully.",
            "filename": file.filename,
            "chunks_created": len(chunks),
            "citation_metadata_sample": chunks[0].metadata if chunks else {},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def list_documents():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    files = [
        {
            "filename": filename,
            "file_path": os.path.join(settings.UPLOAD_DIR, filename),
            "source_type": "pdf",
        }
        for filename in os.listdir(settings.UPLOAD_DIR)
        if filename.lower().endswith(".pdf")
    ]

    return {
        "count": len(files),
        "documents": files,
    }

@router.get("/sources")
def get_sources():
    try:
        return list_sources()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{filename}")
def delete_document(filename: str):
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found.")

    try:
        vectorstore = get_vectorstore()

        existing = vectorstore.get(
            where={
                "filename": filename
            }
        )

        ids = existing.get("ids", [])

        if ids:
            vectorstore.delete(ids=ids)

        os.remove(file_path)

        return {
            "message": "Document deleted successfully.",
            "filename": filename,
            "chunks_deleted": len(ids),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/reset-db")
def reset_vector_db():
    try:
        if os.path.exists(settings.CHROMA_DIR):
            shutil.rmtree(settings.CHROMA_DIR)

        os.makedirs(settings.CHROMA_DIR, exist_ok=True)

        return {
            "message": "ChromaDB reset successfully.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/ingest-website")
def ingest_website(request: WebsiteIngestRequest):
    try:
        chunks = load_and_chunk_website(
            url=request.url,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
        
        if request.chunk_size <= 0:
            raise HTTPException(status_code=400, detail="chunk_size must be greater than 0.")

        if request.chunk_overlap < 0:
            raise HTTPException(status_code=400, detail="chunk_overlap cannot be negative.")

        if request.chunk_overlap >= request.chunk_size:
            raise HTTPException(status_code=400, detail="chunk_overlap must be smaller than chunk_size.")

        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)

        return {
            "message": "Website ingested successfully.",
            "url": request.url,
            "chunks_created": len(chunks),
            "citation_metadata_sample": chunks[0].metadata if chunks else {},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/ingest-youtube")
def ingest_youtube(request: YouTubeIngestRequest):
    try:
        chunks = load_and_chunk_youtube(
            url=request.url,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )

        if request.chunk_size <= 0:
            raise HTTPException(status_code=400, detail="chunk_size must be greater than 0.")

        if request.chunk_overlap < 0:
            raise HTTPException(status_code=400, detail="chunk_overlap cannot be negative.")

        if request.chunk_overlap >= request.chunk_size:
            raise HTTPException(status_code=400, detail="chunk_overlap must be smaller than chunk_size.")

        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)

        return {
            "message": "YouTube transcript ingested successfully.",
            "url": request.url,
            "chunks_created": len(chunks),
            "citation_metadata_sample": chunks[0].metadata if chunks else {},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))