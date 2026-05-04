import { useEffect, useState } from "react";
import { api } from "../api/client";
import ChatWindow from "../components/ChatWindow";
import DocumentList from "../components/DocumentList";
import SourceList from "../components/SourceList";
import { useAppStore } from "../store/useAppStore";

export default function ChatPage() {
  const {
    sessionId,
    messages,
    setMessages,
    appendMessage,
    documents,
    activeDocIds,
    toggleDocumentSelection,
    loadingChat,
    setLoadingChat,
  } = useAppStore();
  const [draft, setDraft] = useState("");
  const [sources, setSources] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    api
      .getHistory(sessionId)
      .then((response) => {
        if (!mounted) {
          return;
        }
        setMessages(response.messages || []);
      })
      .catch(() => {});

    return () => {
      mounted = false;
    };
  }, [sessionId, setMessages]);

  async function handleSend() {
    if (!draft.trim() || !activeDocIds.length) {
      return;
    }

    const question = draft.trim();
    setDraft("");
    setError("");
    appendMessage({ role: "user", content: question });
    setLoadingChat(true);

    try {
      const response = await api.sendMessage({
        session_id: sessionId,
        question,
        doc_ids: activeDocIds,
      });
      appendMessage({ role: "assistant", content: response.answer });
      setSources(response.sources || []);
    } catch (chatError) {
      setError(chatError.message);
    } finally {
      setLoadingChat(false);
    }
  }

  return (
    <div className="chat-layout">
      <aside className="panel sidebar-panel">
        <div className="section-heading">
          <h3>Active Documents</h3>
          <span>{activeDocIds.length} selected</span>
        </div>
        <DocumentList
          documents={documents}
          activeDocIds={activeDocIds}
          onToggle={toggleDocumentSelection}
        />
      </aside>

      <div className="chat-main">
        <section className="panel workspace-summary">
          <div>
            <p className="eyebrow">Workspace</p>
            <h2>{activeDocIds.length ? "Multi-document reasoning ready" : "Select documents to begin"}</h2>
            <p className="lead">
              Ask for summaries, comparisons, action items, timelines, or grounded answers from your uploaded PDFs.
            </p>
          </div>
        </section>
        <ChatWindow
          messages={messages}
          draft={draft}
          setDraft={setDraft}
          onSend={handleSend}
          loading={loadingChat}
        />
        {error ? <p className="error-text">{error}</p> : null}
        <SourceList sources={sources} />
      </div>
    </div>
  );
}
