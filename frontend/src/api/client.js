import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export async function uploadPdf(file, chunkSize = 1000, chunkOverlap = 200) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("chunk_size", chunkSize);
  formData.append("chunk_overlap", chunkOverlap);

  const response = await api.post("/documents/upload-pdf", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}

export async function askQuestion(payload) {
  const response = await api.post("/chat/ask", payload);
  return response.data;
}

export async function getSources() {
  const response = await api.get("/documents/sources");
  return response.data;
}

export async function ingestWebsite(url, chunkSize = 1000, chunkOverlap = 200) {
  const response = await api.post("/documents/ingest-website", {
    url,
    chunk_size: chunkSize,
    chunk_overlap: chunkOverlap,
  });

  return response.data;
}

export async function ingestYoutube(url, chunkSize = 1000, chunkOverlap = 200) {
  const response = await api.post("/documents/ingest-youtube", {
    url,
    chunk_size: chunkSize,
    chunk_overlap: chunkOverlap,
  });

  return response.data;
}