from typing import List
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_youtube_video_id(url: str) -> str:
    parsed = urlparse(url)

    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        query = parse_qs(parsed.query)
        return query.get("v", [""])[0]

    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    return ""


def load_and_chunk_youtube(url: str) -> List[Document]:
    video_id = extract_youtube_video_id(url)

    if not video_id:
        raise ValueError("Invalid YouTube URL.")

    ytt_api = YouTubeTranscriptApi()
    fetched_transcript = ytt_api.fetch(video_id)

    full_text = " ".join([snippet.text for snippet in fetched_transcript.snippets])

    document = Document(
        page_content=full_text,
        metadata={
            "source": url,
            "filename": url,
            "source_type": "youtube",
            "video_id": video_id,
            "page": None,
            "url": url,
        },
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents([document])

    for index, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "chunk_id": f"youtube_{video_id}_chunk_{index}",
            }
        )

    return chunks