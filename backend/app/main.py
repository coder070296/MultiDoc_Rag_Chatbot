from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import documents, chat

app = FastAPI(
    title="Multi-doc RAG Chatbot",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Multi-doc RAG Chatbot API is running."}


@app.get("/health")
def health():
    return {"status": "ok"}