from typing import Optional, List
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.rag.vectorstore import get_vectorstore
from app.prompts.rag_prompt import build_rag_prompt


def format_context(docs):
    formatted_chunks = []

    for index, doc in enumerate(docs, start=1):
        source_type = doc.metadata.get("source_type", "unknown")
        source = doc.metadata.get("source")
        page = doc.metadata.get("page")
        url = doc.metadata.get("url")

        citation_label = f"[Source {index}]"

        metadata_line = f"{citation_label} Type: {source_type} | Source: {source}"

        if page:
            metadata_line += f" | Page: {page}"

        if url:
            metadata_line += f" | URL: {url}"

        formatted_chunks.append(
            f"{metadata_line}\nContent:\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(formatted_chunks)


def build_citations(docs):
    citations = []

    for index, doc in enumerate(docs, start=1):
        citations.append(
            {
                "citation_id": index,
                "source_type": doc.metadata.get("source_type", "unknown"),
                "source": doc.metadata.get("source"),
                "filename": doc.metadata.get("filename"),
                "page": doc.metadata.get("page"),
                "url": doc.metadata.get("url"),
                "video_id": doc.metadata.get("video_id"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "preview": doc.page_content[:300],
            }
        )

    return citations


def ask_question(
    question: str,
    source_type: Optional[str] = None,
    filename: Optional[str] = None,
):
    vectorstore = get_vectorstore()

    search_filter = {}

    if source_type:
        search_filter["source_type"] = source_type

    if filename:
        search_filter["filename"] = filename

    if search_filter:
        docs = vectorstore.similarity_search(
            question,
            k=5,
            filter=search_filter,
        )
    else:
        docs = vectorstore.similarity_search(question, k=5)

    context = format_context(docs)

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=settings.OPENAI_API_KEY,
    )

    prompt = build_rag_prompt(question=question, context=context)

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources_used": len(docs),
        "filters": {
            "source_type": source_type,
            "filename": filename,
        },
        "citations": build_citations(docs),
    }