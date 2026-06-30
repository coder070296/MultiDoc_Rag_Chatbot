import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from app.chunking.chunker import chunk_documents

def load_and_chunk_pdf(
    file_path: str,
    original_filename: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    chunks = chunk_documents(
    pages,
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
)

    for index, chunk in enumerate(chunks):
        page_number = chunk.metadata.get("page", 0) + 1

        chunk.metadata.update(
            {
                "source": original_filename,
                "filename": original_filename,
                "file_path": file_path,
                "page": page_number,
                "chunk_id": f"{original_filename}_page_{page_number}_chunk_{index}",
                "source_type": "pdf",
            }
        )

    return chunks