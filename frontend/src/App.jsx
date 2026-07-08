import { useState } from "react";
import AuthGate from "./components/AuthGate";
import LandingPage from "./components/landing/LandingPage";
import Home from "./pages/Home";
import ToastContainer from "./components/ui/ToastContainer";
import { ThemeProvider } from "./context/ThemeContext";
import { ToastProvider } from "./context/ToastContext";
import "./App.css";

export default function App() {
  const [launched, setLaunched] = useState(
    localStorage.getItem("rag_launched") === "true"
  );

  function handleLaunch() {
    localStorage.setItem("rag_launched", "true");
    setLaunched(true);
  }

  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthGate>
          {launched ? <Home /> : <LandingPage onLaunch={handleLaunch} />}
          <ToastContainer />
        </AuthGate>
      </ToastProvider>
    </ThemeProvider>
  );
}