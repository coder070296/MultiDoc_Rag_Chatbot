import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  Upload,
  Send,
  FileText,
  Link,
  PlayCircle,
  Loader2,
} from "lucide-react";

import { askQuestion, getSources, uploadPdf } from "../api/client";
import UrlIngestCard from "../components/UrlIngestCard";

function SourceIcon({ type }) {
  if (type === "website") return <Link size={16} />;
  if (type === "youtube") return <PlayCircle size={16} />;
  return <FileText size={16} />;
}

export default function Home() {
  const [file, setFile] = useState(null);
  const [sources, setSources] = useState([]);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [citations, setCitations] = useState([]);
  const [selectedSourceType, setSelectedSourceType] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  async function loadSources() {
    try {
      const data = await getSources();
      setSources(data.sources || []);
    } catch (error) {
      console.error(error);
    }
  }

  useEffect(() => {
    loadSources();
  }, []);

  async function handleUpload() {
    if (!file) return;

    setUploading(true);

    try {
      await uploadPdf(file);
      setFile(null);
      await loadSources();
      alert("PDF uploaded successfully.");
    } catch (error) {
      alert(error?.response?.data?.detail || "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(e) {
    e.preventDefault();

    if (!question.trim()) return;

    const userQuestion = question;
    setQuestion("");

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userQuestion },
    ]);

    setLoading(true);

    try {
      const result = await askQuestion({
        question: userQuestion,
        session_id: "frontend-session",
        source_type: selectedSourceType || null,
        model: "gpt-4o-mini",
        temperature: 0,
        k: 5,
      });

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer },
      ]);

      setCitations(result.citations || []);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: error?.response?.data?.detail || "Something went wrong.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">R</div>
          <div>
            <h1>RAG Chatbot</h1>
            <p>Multi-source AI assistant</p>
          </div>
        </div>

        <div className="card">
          <h2>Upload PDF</h2>

          <label className="upload-box">
            <Upload size={24} />
            <span>{file ? file.name : "Choose a PDF file"}</span>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files?.[0])}
            />
          </label>

          <button onClick={handleUpload} disabled={!file || uploading}>
            {uploading ? (
              <Loader2 className="spin" size={16} />
            ) : (
              <Upload size={16} />
            )}
            {uploading ? "Uploading..." : "Upload & Ingest"}
          </button>
        </div>

        <UrlIngestCard onIngested={loadSources} />

        <div className="card">
          <h2>Filter Sources</h2>

          <select
            value={selectedSourceType}
            onChange={(e) => setSelectedSourceType(e.target.value)}
          >
            <option value="">All sources</option>
            <option value="pdf">PDFs</option>
            <option value="website">Websites</option>
            <option value="youtube">YouTube</option>
          </select>
        </div>

        <div className="card sources-card">
          <h2>Sources</h2>

          {sources.length === 0 ? (
            <p className="muted">No sources ingested yet.</p>
          ) : (
            <div className="source-list">
              {sources.map((source) => (
                <div className="source-item" key={source.source}>
                  <div className="source-title">
                    <SourceIcon type={source.source_type} />
                    <span>{source.source_type}</span>
                  </div>
                  <p>{source.filename || source.source}</p>
                  <small>{source.chunks} chunks</small>
                </div>
              ))}
            </div>
          )}
        </div>
      </aside>

      <main className="chat-area">
        <header className="chat-header">
          <div>
            <h2>Ask your documents</h2>
            <p>PDFs, websites, and YouTube transcripts with citations</p>
          </div>
        </header>

        <section className="messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <h3>Start asking questions</h3>
              <p>Upload a PDF or ingest a website/YouTube source.</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div className={`message ${message.role}`} key={index}>
                <div className="bubble">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="message assistant">
              <div className="bubble loading-bubble">
                <Loader2 className="spin" size={16} />
                Thinking...
              </div>
            </div>
          )}
        </section>

        <form className="ask-form" onSubmit={handleAsk}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask anything from your sources..."
          />
          <button disabled={loading || !question.trim()}>
            <Send size={18} />
          </button>
        </form>
      </main>

      <aside className="citation-panel">
        <h2>Citations</h2>

        {citations.length === 0 ? (
          <p className="muted">Citations will appear after an answer.</p>
        ) : (
          citations.map((citation) => (
            <div className="citation-card" key={citation.chunk_id}>
              <div className="citation-meta">
                <SourceIcon type={citation.source_type} />
                <strong>Source {citation.citation_id}</strong>
              </div>

              <p className="citation-source">
                {citation.filename || citation.source}
              </p>

              {citation.page && <small>Page {citation.page}</small>}

              <p className="preview">{citation.preview}</p>
            </div>
          ))
        )}
      </aside>
    </div>
  );
}