from app.rag.vectorstore import get_vectorstore


def list_sources():
    vectorstore = get_vectorstore()
    data = vectorstore.get()

    metadatas = data.get("metadatas", [])

    sources = {}

    for metadata in metadatas:
        source = metadata.get("source") or metadata.get("filename") or "unknown"

        if source not in sources:
            sources[source] = {
                "source": source,
                "filename": metadata.get("filename"),
                "source_type": metadata.get("source_type", "unknown"),
                "url": metadata.get("url"),
                "video_id": metadata.get("video_id"),
                "pages": set(),
                "chunks": 0,
            }

        sources[source]["chunks"] += 1

        page = metadata.get("page")
        if page:
            sources[source]["pages"].add(page)

    result = []

    for source in sources.values():
        pages = sorted(list(source["pages"]))

        result.append(
            {
                **source,
                "pages": pages,
                "page_count": len(pages),
            }
        )

    return {
        "count": len(result),
        "sources": result,
    }