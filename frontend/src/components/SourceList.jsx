export default function SourceList({ sources }) {
  if (!sources?.length) {
    return null;
  }

  return (
    <section className="source-panel">
      <div className="section-heading">
        <h3>Sources</h3>
        <span>{sources.length} references</span>
      </div>
      <div className="source-grid">
        {sources.map((source) => (
          <article key={`${source.doc_id}-${source.source_id}`} className="source-card">
            <p className="source-label">{source.source_id}</p>
            <h4>{source.filename}</h4>
            <p className="source-meta">Page {source.page_no}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
