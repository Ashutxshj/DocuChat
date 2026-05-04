import { Route, Routes, useLocation, useNavigate } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ChatPage from "./pages/ChatPage";

export default function App() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI SaaS</p>
          <h1>DocuChat Copilot</h1>
        </div>
        <nav className="nav-tabs">
          <button
            type="button"
            className={location.pathname === "/" ? "active" : ""}
            onClick={() => navigate("/")}
          >
            Upload
          </button>
          <button
            type="button"
            className={location.pathname === "/chat" ? "active" : ""}
            onClick={() => navigate("/chat")}
          >
            Chat
          </button>
        </nav>
      </header>

      <main className="page-shell">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
      </main>
    </div>
  );
}
