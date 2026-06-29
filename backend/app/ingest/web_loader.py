import requests
from bs4 import BeautifulSoup
from typing import List
from langchain_core.documents import Document
from app.chunking.chunker import chunk_documents


def load_and_chunk_website(url: str) -> List[Document]:
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    clean_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    document = Document(
        page_content=clean_text,
        metadata={
            "source": url,
            "filename": url,
            "source_type": "website",
            "page": None,
            "url": url,
        },
    )

    chunks = chunk_documents(
        [document],
        chunk_size=1000,
        chunk_overlap=200
    )

    for index, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "chunk_id": f"website_{index}_{url}",
            }
        )

    return chunks