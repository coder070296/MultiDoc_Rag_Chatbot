# 🚀 MultiDoc RAG Chatbot

An enterprise-grade **Multi-Document Retrieval-Augmented Generation (RAG)** chatbot built with **FastAPI, LangChain, ChromaDB, React, and OpenAI**.

The application can ingest **PDFs**, **Websites**, and **YouTube transcripts**, index them into a vector database, and answer questions with accurate **source citations**.

---

# ✨ Features

## Document Ingestion

- 📄 PDF Upload
- 🌐 Website URL Ingestion
- ▶️ YouTube Transcript Ingestion

---

## Retrieval

- Semantic Vector Search (ChromaDB)
- Hybrid Search (Vector + BM25)
- Metadata Filtering
- Configurable Chunk Size
- Configurable Chunk Overlap
- Configurable Retrieval Count (Top-K)

---

## AI

- GPT-4o Mini
- Streaming Responses
- Conversation Memory
- Prompt Templates
- Source Citations

---

## Frontend

- React + Vite
- Modern Chat UI
- Markdown Rendering
- Upload PDF
- Website Ingestion
- YouTube Ingestion
- Citation Panel
- Source Management
- Delete Sources
- Reset Vector Database
- Demo Authentication

---

# 🛠 Tech Stack

## Backend

- Python
- FastAPI
- LangChain
- OpenAI
- ChromaDB
- BM25
- Pydantic

---

## Frontend

- React
- Axios
- React Markdown
- Lucide Icons

---

# 📂 Project Structure

```
MultiDoc_Rag_Chatbot/

├── backend/
│
│   ├── app/
│   │
│   ├── chunking/
│   ├── ingest/
│   ├── memory/
│   ├── prompts/
│   ├── rag/
│   ├── routes/
│   ├── sources/
│   │
│   └── main.py
│
└── frontend/
    ├── api/
    ├── components/
    ├── pages/
    ├── App.jsx
    └── main.jsx
```

---

# 🧠 Supported Sources

| Source | Status |
|---------|--------|
| PDF | ✅ |
| Website | ✅ |
| YouTube Transcript | ✅ |

---

# 🔍 Supported Retrieval

- Vector Search
- Hybrid Search
- Source Filtering
- File Filtering

---

# 📌 API Endpoints

## Documents

```
POST   /documents/upload-pdf
POST   /documents/ingest-website
POST   /documents/ingest-youtube

GET    /documents
GET    /documents/sources

DELETE /documents/{filename}
DELETE /documents/sources/delete
DELETE /documents/admin/reset-db
```

---

## Chat

```
POST /chat/ask
POST /chat/ask-hybrid
POST /chat/stream

POST /chat/preview-retrieval

GET /chat/stats

DELETE /chat/sessions/{session_id}
DELETE /chat/sessions
```

---

# ⚙️ Installation

## Backend

```bash
cd backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python -m uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 🔑 Environment Variables

Backend

```
OPENAI_API_KEY=YOUR_KEY

CHROMA_DIR=./chroma_db

UPLOAD_DIR=./uploads
```

Frontend

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

# 🎯 Demo Workflow

## 1

Upload a PDF

↓

## 2

Ingest a Website

↓

## 3

Ingest a YouTube Video

↓

## 4

Ask Questions

↓

## 5

View Source Citations

↓

## 6

Delete Sources

↓

## 7

Reset Database

---

# 📸 Screenshots

Add screenshots here:

```
docs/screenshots/home.png

docs/screenshots/chat.png

docs/screenshots/upload.png

docs/screenshots/citations.png
```

---

# 🚀 Future Improvements

- User Authentication
- PostgreSQL
- Redis Cache
- Docker
- AWS Deployment
- Railway Deployment
- React Native App
- OCR
- Voice Input
- Whisper Integration
- Multi-user Support
- Role Based Access
- Usage Analytics
- RAG Evaluation
- Multi-language Support

---

# 👨‍💻 Author

Bhanu Pratap Singh

GitHub:
https://github.com/coder070296

LinkedIn:
(Add your LinkedIn)