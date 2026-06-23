from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.rag.vectorstore import get_vectorstore


def ask_question(question: str):
    vectorstore = get_vectorstore()

    docs = vectorstore.similarity_search(question, k=4)

    context = "\n\n".join(
        [
            f"Source: {doc.metadata.get('source')} | Page: {doc.metadata.get('page')}\n{doc.page_content}"
            for doc in docs
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=settings.OPENAI_API_KEY,
    )

    prompt = f"""
You are a helpful RAG assistant.

Answer the question using only the provided context.
If the answer is not in the context, say: "I don't know based on the uploaded documents."

Question:
{question}

Context:
{context}
"""

    response = llm.invoke(prompt)

    citations = [
        {
            "source": doc.metadata.get("source"),
            "filename": doc.metadata.get("filename"),
            "page": doc.metadata.get("page"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "source_type": doc.metadata.get("source_type"),
            "preview": doc.page_content[:250],
        }
        for doc in docs
    ]

    return {
        "answer": response.content,
        "citations": citations,
    }