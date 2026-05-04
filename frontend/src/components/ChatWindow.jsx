export default function ChatWindow({ messages, draft, setDraft, onSend, loading }) {
  return (
    <section className="chat-shell">
      <div className="messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <h2>Ask your document stack anything</h2>
            <p>Answers are grounded in retrieved chunks and linked back to source pages.</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <article key={`${message.role}-${index}`} className={`message ${message.role}`}>
              <p className="message-role">{message.role === "user" ? "You" : "Copilot"}</p>
              <p>{message.content}</p>
            </article>
          ))
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
          rows={4}
        />
        <button type="submit" disabled={loading || !draft.trim()}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>
    </section>
  );
}
