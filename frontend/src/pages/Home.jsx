import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { useToast } from "../context/ToastContext";
import {
  Upload,
  Send,
  FileText,
  Link,
  PlayCircle,
  Loader2,
  Copy,
  Check,
} from "lucide-react";

import UrlIngestCard from "../components/UrlIngestCard";
import {
  askQuestion,
  getSources,
  uploadPdf,
  deleteSource,
  resetVectorDb,
  streamQuestion,
} from "../api/client";

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
  const { showToast } = useToast();

  const [conversations, setConversations] = useState(() => {
    return JSON.parse(localStorage.getItem("rag_conversations") || "[]");
  });

  const [activeConversationId, setActiveConversationId] = useState(() => {
    return localStorage.getItem("rag_active_conversation") || crypto.randomUUID();
  });

  const messagesEndRef = useRef(null);
  const [copiedMessageIndex, setCopiedMessageIndex] = useState(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

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

  async function handleCopyMessage(content, index) {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageIndex(index);
      showToast("Answer copied to clipboard.", "success");

      setTimeout(() => {
        setCopiedMessageIndex(null);
      }, 2000);
    } catch {
      showToast("Could not copy the answer.", "error");
    }
  }

  async function handleUpload() {
    if (!file) return;

    setUploading(true);

    try {
      await uploadPdf(file);
      setFile(null);
      await loadSources();
      showToast("PDF uploaded successfully.", "success");
    } catch (error) {
      showToast(error?.response?.data?.detail || "Upload failed.", "error");
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(e) {
    e.preventDefault();

    if (!question.trim()) return;

    const userQuestion = question;
    setQuestion("");

    const userMessage = { role: "user", content: userQuestion };
    const nextMessages = [...messages, userMessage];

    setMessages(nextMessages);
    saveConversation(nextMessages);

    setLoading(true);

    try {

      let assistantAnswer = "";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "" },
      ]);

      await streamQuestion(
        {
          question: userQuestion,
          session_id: "frontend-session",
          source_type: selectedSourceType || null,
          model: "gpt-4o-mini",
          temperature: 0,
          k: 5,
        },
        (event) => {
          if (event.type === "token") {
            assistantAnswer += event.content;

            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                role: "assistant",
                content: assistantAnswer,
              };
              return updated;
            });
          }

          if (event.type === "citations") {
            setCitations(event.citations || []);
          }
        }
      );
      saveConversation([
        ...nextMessages,
        { role: "assistant", content: assistantAnswer },
      ]);
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

  async function handleDeleteSource(source) {
        const confirmed = confirm(`Delete this source?\n\n${source}`);
        if (!confirmed) return;

        try {
            await deleteSource(source);
            await loadSources();
            showToast("Source deleted successfully.", "success");
        } catch (error) {
            showToast(error?.response?.data?.detail || "Delete failed.", "error");
        }
    }

    async function handleResetDb() {
        const confirmed = confirm("Reset entire vector database? This will delete all indexed sources.");
        if (!confirmed) return;

        try {
            await resetVectorDb();
            await loadSources();
            setCitations([]);
            showToast("Vector DB reset successfully.", "success");
        } catch (error) {
            showToast(error?.response?.data?.detail || "Reset failed.", "error");
        }
    }

    function handleDrop(e) {
      e.preventDefault();

      const droppedFile = e.dataTransfer.files?.[0];

      if (!droppedFile) return;

      if (droppedFile.type !== "application/pdf") {
        showToast("Only PDF files are allowed.", "error");
        return;
      }

      setFile(droppedFile);
    }

    function handleDragOver(e) {
      e.preventDefault();
    }

    function saveConversation(updatedMessages) {
      const title =
        updatedMessages.find((msg) => msg.role === "user")?.content?.slice(0, 45) ||
        "New Chat";

      const updated = [
        {
          id: activeConversationId,
          title,
          messages: updatedMessages,
          updatedAt: new Date().toISOString(),
        },
        ...conversations.filter((chat) => chat.id !== activeConversationId),
      ];

      setConversations(updated);
      localStorage.setItem("rag_conversations", JSON.stringify(updated));
      localStorage.setItem("rag_active_conversation", activeConversationId);
    }

    function startNewChat() {
      const newId = crypto.randomUUID();
      setActiveConversationId(newId);
      setMessages([]);
      setCitations([]);
      localStorage.setItem("rag_active_conversation", newId);
    }

    function loadConversation(chat) {
      setActiveConversationId(chat.id);
      setMessages(chat.messages || []);
      setCitations([]);
      localStorage.setItem("rag_active_conversation", chat.id);
    }

    function deleteConversation(chatId) {
      const updated = conversations.filter((chat) => chat.id !== chatId);
      setConversations(updated);
      localStorage.setItem("rag_conversations", JSON.stringify(updated));

      if (chatId === activeConversationId) {
        startNewChat();
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
          <button onClick={startNewChat}>+ New Chat</button>

          <div className="history-list">
            {conversations.length === 0 ? (
              <p className="muted">No chat history yet.</p>
            ) : (
              conversations.map((chat) => (
                <div
                  className={`history-item ${
                    chat.id === activeConversationId ? "active" : ""
                  }`}
                  key={chat.id}
                >
                  <button onClick={() => loadConversation(chat)}>
                    {chat.title}
                  </button>

                  <button
                    className="danger-icon"
                    onClick={() => deleteConversation(chat.id)}
                  >
                    ×
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card">
          <h2>Upload PDF</h2>

          <label
            className={`upload-box ${file ? "has-file" : ""}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}>
            <Upload size={26} />
            <span>
              {file ? file.name : "Drop PDF here or click to upload"}
            </span>

            {file && <small>{(file.size / 1024 / 1024).toFixed(2)} MB selected</small>}

            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => {
                const selected = e.target.files?.[0];

                if (!selected) return;

                if (selected.type !== "application/pdf") {
                  showToast("Only PDF files are allowed.", "error");
                  return;
                }

                setFile(selected);
              }}
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

          <button className="secondary-btn" onClick={loadSources}>
            Refresh Sources
          </button>

          <button className="danger-btn" onClick={handleResetDb}>
            Reset Vector DB
          </button>

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
                  <button
                    className="danger-btn small-btn"
                    onClick={() => handleDeleteSource(source.source)}
                    >
                    Delete
                   </button>
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
                <div className="message-content">
                  <div className="bubble">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>

                  {message.role === "assistant" && message.content && (
                    <button
                      className="copy-message-btn"
                      onClick={() => handleCopyMessage(message.content, index)}
                      title="Copy answer"
                    >
                      {copiedMessageIndex === index ? (
                        <>
                          <Check size={14} />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy size={14} />
                          Copy
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))
          )}

          {loading && messages[messages.length - 1]?.content === "" && (
            <div className="message assistant">
              <div className="bubble typing-bubble">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
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