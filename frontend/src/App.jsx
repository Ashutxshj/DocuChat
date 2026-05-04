import { NavLink, Route, Routes } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ChatPage from "./pages/ChatPage";

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI SaaS</p>
          <h1>DocuChat Copilot</h1>
        </div>
        <nav className="nav-tabs">
          <NavLink to="/" end>
            Upload
          </NavLink>
          <NavLink to="/chat">Chat</NavLink>
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
