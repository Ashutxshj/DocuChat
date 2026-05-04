import RichTextMessage from "./RichTextMessage";

export default function ChatWindow({ messages, draft, setDraft, onSend, loading }) {
  return (
    <section className="chat-shell">
      <div className="chat-shell-header">
        <div>
          <p className="eyebrow">Document Agent</p>
          <h2>DocuChat Copilot</h2>
        </div>
        <div className="status-pill">{loading ? "Analyzing" : "Ready"}</div>
      </div>

      <div className="messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <h2>Ask your document stack anything</h2>
            <p>Answers are grounded in retrieved chunks, structured for readability, and linked back to source pages.</p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <article key={`${message.role}-${index}`} className={`message ${message.role}`}>
                <div className="message-meta">
                  <span className="message-avatar">{message.role === "user" ? "You" : "AI"}</span>
                  <p className="message-role">{message.role === "user" ? "You" : "DocuChat Copilot"}</p>
                </div>
                {message.role === "assistant" ? (
                  <RichTextMessage content={message.content} />
                ) : (
                  <div className="rich-text">
                    <p>{message.content}</p>
                  </div>
                )}
              </article>
            ))}
            {loading ? (
              <article className="message assistant thinking-message">
                <div className="message-meta">
                  <span className="message-avatar">AI</span>
                  <p className="message-role">DocuChat Copilot</p>
                </div>
                <div className="thinking-indicator" aria-label="Assistant is thinking">
                  <span className="thinking-ring" />
                  <span className="thinking-dot" />
                  <span className="thinking-dot" />
                  <span className="thinking-dot" />
                </div>
              </article>
            ) : null}
          </>
        )}
      </div>

      <form
        className="composer"
        onSubmit={(event) => {
          event.preventDefault();
          onSend();
        }}
      >
        <textarea
          value={draft}
          placeholder="Ask a question about your uploaded PDFs..."
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              if (!loading && draft.trim()) {
                onSend();
              }
            }
          }}
          rows={3}
        />
        <div className="composer-footer">
          <p>Grounded answers only. Select documents from the left before sending.</p>
          <button type="submit" disabled={loading || !draft.trim()}>
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>
      </form>
    </section>
  );
}
