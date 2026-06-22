from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings


def get_vectorstore():
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=settings.OPENAI_API_KEY,
    )

    return Chroma(
        collection_name="multi_doc_rag",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_DIR,
    )