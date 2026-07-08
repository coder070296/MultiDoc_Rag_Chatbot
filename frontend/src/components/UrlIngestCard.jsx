import { useState } from "react";
import { Link, Loader2, PlayCircle } from "lucide-react";
import { ingestWebsite, ingestYoutube } from "../api/client";
import { useToast } from "../context/ToastContext";

export default function UrlIngestCard({ onIngested }) {
  const [url, setUrl] = useState("");
  const [sourceType, setSourceType] = useState("website");
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

  async function handleIngest() {
    if (!url.trim()) return;

    setLoading(true);

    try {
      if (sourceType === "website") {
        await ingestWebsite(url);
      } else {
        await ingestYoutube(url);
      }

      setUrl("");
      await onIngested?.();
      showToast("Source ingested successfully.", "success");
    } catch (error) {
      showToast(error?.response?.data?.detail || "Ingestion failed.", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2>Ingest URL</h2>

      <select value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
        <option value="website">Website</option>
        <option value="youtube">YouTube</option>
      </select>

      <input
        className="url-input"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder={
          sourceType === "website"
            ? "https://example.com/article"
            : "https://youtube.com/watch?v=..."
        }
      />

      <button onClick={handleIngest} disabled={loading || !url.trim()}>
        {loading ? (
          <Loader2 className="spin" size={16} />
        ) : sourceType === "website" ? (
          <Link size={16} />
        ) : (
          <PlayCircle size={16} />
        )}

        {loading ? "Ingesting..." : "Ingest Source"}
      </button>
    </div>
  );
}