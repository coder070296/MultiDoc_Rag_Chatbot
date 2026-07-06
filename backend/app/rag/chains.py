from typing import Optional, List, Generator
from urllib import response
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.rag.vectorstore import get_vectorstore
from app.prompts.rag_prompt import build_rag_prompt
from app.memory.session_store import format_chat_history, add_message
from rank_bm25 import BM25Okapi
import json

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
    session_id: Optional[str] = "default",
    model: str = "gpt-4o-mini",
    temperature: float = 0,
    k: int = 5,
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
            k=k,
            filter=search_filter,
        )
    else:
        docs = vectorstore.similarity_search(question, k=k)

    context = format_context(docs)

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY,
    )
    
    chat_history = format_chat_history(session_id)

    prompt = build_rag_prompt(
        question=question,
        context=context,
        chat_history=chat_history,
    )

    response = llm.invoke(prompt)
    
    add_message(session_id, "user", question)
    add_message(session_id, "assistant", response.content)

    return {
        "answer": response.content,
        "sources_used": len(docs),
        "filters": {
            "source_type": source_type,
            "filename": filename,
        },
        "citations": build_citations(docs),
        "session_id": session_id,
        "rag_config": {
            "model": model,
            "temperature": temperature,
            "k": k,
            "retrieval_mode": "vector",
        },
    }
    
def stream_question(
    question: str,
    source_type: Optional[str] = None,
    filename: Optional[str] = None,
    session_id: Optional[str] = "default",
    model: str = "gpt-4o-mini",
    temperature: float = 0,
    k: int = 5,
) -> Generator[str, None, None]:
    vectorstore = get_vectorstore()

    search_filter = {}

    if source_type:
        search_filter["source_type"] = source_type

    if filename:
        search_filter["filename"] = filename

    if search_filter:
        docs = vectorstore.similarity_search(question, k=k, filter=search_filter)
    else:
        docs = vectorstore.similarity_search(question, k=k)

    context = format_context(docs)
    chat_history = format_chat_history(session_id)

    prompt = build_rag_prompt(
        question=question,
        context=context,
        chat_history=chat_history,
    )

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        streaming=True,
        api_key=settings.OPENAI_API_KEY,
    )

    final_answer = ""

    for chunk in llm.stream(prompt):
        token = chunk.content or ""
        final_answer += token

        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", final_answer)

    yield f"data: {json.dumps({'type': 'citations', 'citations': build_citations(docs)})}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

def preview_retrieval(
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
        docs = vectorstore.similarity_search_with_score(
            question,
            k=5,
            filter=search_filter,
        )
    else:
        docs = vectorstore.similarity_search_with_score(question, k=5)

    results = []

    for index, item in enumerate(docs, start=1):
        doc, score = item

        results.append(
            {
                "rank": index,
                "score": score,
                "source_type": doc.metadata.get("source_type"),
                "source": doc.metadata.get("source"),
                "filename": doc.metadata.get("filename"),
                "page": doc.metadata.get("page"),
                "url": doc.metadata.get("url"),
                "video_id": doc.metadata.get("video_id"),
                "chunk_id": doc.metadata.get("chunk_id"),
                "preview": doc.page_content[:500],
            }
        )

    return {
        "question": question,
        "filters": {
            "source_type": source_type,
            "filename": filename,
        },
        "results_count": len(results),
        "results": results,
    }


def get_vectorstore_stats():
    vectorstore = get_vectorstore()
    data = vectorstore.get()

    metadatas = data.get("metadatas", [])

    source_type_counts = {}
    filename_counts = {}

    for metadata in metadatas:
        source_type = metadata.get("source_type", "unknown")
        filename = metadata.get("filename", "unknown")

        source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1
        filename_counts[filename] = filename_counts.get(filename, 0) + 1

    return {
        "total_chunks": len(data.get("ids", [])),
        "source_type_counts": source_type_counts,
        "filename_counts": filename_counts,
    }
    
def hybrid_retrieval(
    question: str,
    source_type: Optional[str] = None,
    filename: Optional[str] = None,
    k: int = 5,
):
    vectorstore = get_vectorstore()

    search_filter = {}

    if source_type:
        search_filter["source_type"] = source_type

    if filename:
        search_filter["filename"] = filename

    all_data = vectorstore.get(where=search_filter if search_filter else None)

    documents = all_data.get("documents", [])
    metadatas = all_data.get("metadatas", [])
    ids = all_data.get("ids", [])

    if not documents:
        return []

    tokenized_docs = [doc.lower().split() for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)

    tokenized_question = question.lower().split()
    bm25_scores = bm25.get_scores(tokenized_question)

    if search_filter:
        vector_results = vectorstore.similarity_search_with_score(
            question,
            k=k,
            filter=search_filter,
        )
    else:
        vector_results = vectorstore.similarity_search_with_score(question, k=k)

    combined = {}

    for doc, score in vector_results:
        chunk_id = doc.metadata.get("chunk_id")

        combined[chunk_id] = {
            "doc": doc,
            "vector_score": float(score),
            "bm25_score": 0.0,
            "final_score": 1 / (1 + float(score)),
        }

    top_bm25_indexes = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True,
    )[:k]

    for index in top_bm25_indexes:
        metadata = metadatas[index]
        chunk_id = metadata.get("chunk_id")

        from langchain_core.documents import Document

        doc = Document(
            page_content=documents[index],
            metadata=metadata,
        )

        bm25_score = float(bm25_scores[index])

        if chunk_id in combined:
            combined[chunk_id]["bm25_score"] = bm25_score
            combined[chunk_id]["final_score"] += bm25_score
        else:
            combined[chunk_id] = {
                "doc": doc,
                "vector_score": None,
                "bm25_score": bm25_score,
                "final_score": bm25_score,
            }

    ranked = sorted(
        combined.values(),
        key=lambda item: item["final_score"],
        reverse=True,
    )

    return ranked[:k]

def ask_question_hybrid(
    question: str,
    source_type: Optional[str] = None,
    filename: Optional[str] = None,
    session_id: Optional[str] = "default",
    model: str = "gpt-4o-mini",
    temperature: float = 0,
    k: int = 5,
):
    results = hybrid_retrieval(
        question=question,
        source_type=source_type,
        filename=filename,
        k=k,
    )

    docs = [item["doc"] for item in results]

    context = format_context(docs)
    chat_history = format_chat_history(session_id)

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY,
    )

    prompt = build_rag_prompt(
        question=question,
        context=context,
        chat_history=chat_history,
    )

    response = llm.invoke(prompt)

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", response.content)

    citations = build_citations(docs)

    for index, citation in enumerate(citations):
        citation["retrieval"] = {
            "vector_score": results[index]["vector_score"],
            "bm25_score": results[index]["bm25_score"],
            "final_score": results[index]["final_score"],
        }

    return {
        "answer": response.content,
        "session_id": session_id,
        "retrieval_mode": "hybrid",
        "sources_used": len(docs),
        "filters": {
            "source_type": source_type,
            "filename": filename,
        },
        "citations": citations,
        "rag_config": {
            "model": model,
            "temperature": temperature,
            "k": k,
            "retrieval_mode": "hybrid",
        },
    }