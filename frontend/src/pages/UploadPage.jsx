import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import DocumentList from "../components/DocumentList";
import FileDropzone from "../components/FileDropzone";
import { useAppStore } from "../store/useAppStore";

async function pollDocument(docId, upsertDocument) {
  let attempts = 0;
  while (attempts < 30) {
    const status = await api.getDocumentStatus(docId);
    upsertDocument(status);
    if (status.status === "completed" || status.status === "failed") {
      return status;
    }
    attempts += 1;
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
  throw new Error("Document processing timed out");
}

export default function UploadPage() {
  const navigate = useNavigate();
  const { documents, activeDocIds, toggleDocumentSelection, upsertDocument, uploading, setUploading } = useAppStore();
  const [error, setError] = useState("");

  async function handleFileSelect(file) {
    setError("");
    setUploading(true);

    try {
      const upload = await api.initUpload({
        filename: file.name,
        content_type: file.type || "application/pdf",
      });

      upsertDocument({
        doc_id: upload.doc_id,
        filename: file.name,
        s3_key: upload.s3_key,
        status: upload.status,
      });

      await api.uploadFileToS3(upload.upload_url, file);
      const processResponse = await api.processDocument({
        doc_id: upload.doc_id,
        s3_key: upload.s3_key,
        filename: file.name,
        async_processing: true,
      });

      upsertDocument({ doc_id: upload.doc_id, status: processResponse.status, filename: file.name });
      await pollDocument(upload.doc_id, upsertDocument);
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="two-column-layout">
      <section className="panel hero-panel">
        <p className="eyebrow">Ingestion Pipeline</p>
        <h2>Upload PDFs and turn them into a searchable knowledge base</h2>
        <p className="lead">
          Files land in S3, get chunked and embedded in the background, then become available for grounded chat.
        </p>
        <FileDropzone disabled={uploading} onSelect={handleFileSelect} />
        {error ? <p className="error-text">{error}</p> : null}
        <button className="primary-action" onClick={() => navigate("/chat")} disabled={!activeDocIds.length}>
          Open chat workspace
        </button>
      </section>

      <section className="panel">
        <div className="section-heading">
          <h3>Document Queue</h3>
          <span>{documents.length} total</span>
        </div>
        <DocumentList
          documents={documents}
          activeDocIds={activeDocIds}
          onToggle={toggleDocumentSelection}
        />
      </section>
    </div>
  );
}
