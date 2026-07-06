import Home from "./pages/Home";
import AuthGate from "./components/AuthGate";
import "./App.css";

export default function App() {
  return (
    <AuthGate>
      <Home />
    </AuthGate>
  );
}