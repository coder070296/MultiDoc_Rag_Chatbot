import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def load_and_chunk_pdf(file_path: str, original_filename: str) -> List[Document]:
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(pages)

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