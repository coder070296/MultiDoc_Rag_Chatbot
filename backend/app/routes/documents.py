import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.ingest.pdf_loader import load_and_chunk_pdf
from app.rag.vectorstore import get_vectorstore

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunks = load_and_chunk_pdf(file_path, file.filename)

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