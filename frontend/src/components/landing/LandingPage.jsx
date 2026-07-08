import { FileText, Globe, Youtube, Zap, Quote, Brain } from "lucide-react";
import ThemeToggle from "../ui/ThemeToggle";

export default function LandingPage({ onLaunch }) {
  const features = [
    { icon: <FileText size={22} />, title: "PDF Ingestion" },
    { icon: <Globe size={22} />, title: "Website RAG" },
    { icon: <Youtube size={22} />, title: "YouTube Transcripts" },
    { icon: <Zap size={22} />, title: "Streaming Answers" },
    { icon: <Quote size={22} />, title: "Source Citations" },
    { icon: <Brain size={22} />, title: "Hybrid Retrieval" },
  ];

  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <div className="brand">
          <div className="brand-icon">R</div>
          <div>
            <h1>MultiDoc RAG</h1>
            <p>Enterprise Knowledge Assistant</p>
          </div>
        </div>

        <ThemeToggle />
      </nav>

      <section className="hero">
        <div className="hero-badge">PDFs • Websites • YouTube • Citations</div>

        <h2>Ask questions across all your knowledge sources.</h2>

        <p>
          Upload documents, ingest websites, analyze YouTube transcripts, and get
          accurate AI answers with source-backed citations.
        </p>

        <button className="launch-btn" onClick={onLaunch}>
          Launch Workspace
        </button>
      </section>

      <section className="feature-grid">
        {features.map((feature) => (
          <div className="feature-card" key={feature.title}>
            {feature.icon}
            <h3>{feature.title}</h3>
          </div>
        ))}
      </section>
    </div>
  );
}