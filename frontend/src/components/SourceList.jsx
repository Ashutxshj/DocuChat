export default function SourceList({ sources }) {
  if (!sources?.length) {
    return null;
  }

  return (
    <section className="source-panel">
      <div className="section-heading">
        <h3>Sources</h3>
        <span>{sources.length} retrieved chunks</span>
      </div>
      <div className="source-grid">
        {sources.map((source) => (
          <article key={`${source.doc_id}-${source.source_id}`} className="source-card">
            <p className="source-label">
              {source.source_id} · page {source.page_no}
            </p>
            <p>{source.snippet}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
