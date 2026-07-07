import { useState } from "react";

const DEMO_PASSWORD = "ragdemo123";

export default function AuthGate({ children }) {
  const [password, setPassword] = useState("");
  const [isAuthed, setIsAuthed] = useState(
    localStorage.getItem("rag_authed") === "true"
  );

  function handleLogin(e) {
    e.preventDefault();

    if (password === DEMO_PASSWORD) {
      localStorage.setItem("rag_authed", "true");
      setIsAuthed(true);
    } else {
      alert("Wrong password");
    }
  }

    if (isAuthed) {
        return (
            <>
            <button
                className="logout-btn"
                onClick={() => {
                localStorage.removeItem("rag_authed");
                setIsAuthed(false);
                }}
            >
                Logout
            </button>
            {children}
            </>
        );
    }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleLogin}>
        <div className="brand-icon">R</div>
        <h1>RAG Chatbot</h1>
        <p>Enter demo password to continue</p>

        <input
          type="password"
          placeholder="Demo password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button>Login</button>

        <small>Demo password: ragdemo123</small>
      </form>
    </div>
  );
}