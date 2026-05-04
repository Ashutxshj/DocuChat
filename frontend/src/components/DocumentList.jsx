export default function DocumentList({ documents, activeDocIds, onToggle }) {
  if (!documents.length) {
    return <p className="empty-state">No documents uploaded yet.</p>;
  }

  return (
    <div className="document-list">
      {documents.map((document) => {
        const isSelected = activeDocIds.includes(document.doc_id);
        const canSelect = document.status === "completed";
        return (
          <label key={document.doc_id} className={`document-card ${isSelected ? "selected" : ""}`}>
            <div className="document-card-row">
              <input
                type="checkbox"
                checked={isSelected}
                disabled={!canSelect}
                onChange={() => onToggle(document.doc_id)}
              />
              <div>
                <strong>{document.filename}</strong>
                <p>{document.status}</p>
              </div>
            </div>
            <small>
              {document.page_count ? `${document.page_count} pages` : "Processing metadata pending"}
            </small>
          </label>
        );
      })}
    </div>
  );
}
