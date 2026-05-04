# DocuChat Copilot

DocuChat Copilot is a production-oriented AI SaaS starter for uploading PDFs, processing them into embeddings, and chatting against grounded document context with per-session memory.

## Architecture

### Backend
- `FastAPI` API with modular `routes`, `services`, `models`, and `utils`
- `AWS S3` presigned uploads for PDF storage
- `PyPDF` text extraction
- `tiktoken`-based chunking with overlap
- `OpenAI embeddings` for vectorization
- `ChromaDB` persistent local vector store
- `OpenAI responses API` for grounded RAG answers
- `Redis` chat memory with in-memory fallback

### Frontend
- `React + Vite`
- Functional components and hooks
- `Zustand` state store
- Drag-and-drop upload flow
- Chat workspace with source cards and multi-document selection

## Project Structure

```text
backend/
  app/
    main.py
    routes/
    services/
    models/
    utils/
frontend/
  src/
    api/
    components/
    pages/
    store/
```

## Backend Setup

1. Create an S3 bucket and ensure the configured IAM user or role can run `s3:PutObject` and `s3:GetObject`.
2. Copy [backend/.env.example](/C:/Users/Ashut/OneDrive/Desktop/Projects/DocuChat/backend/.env.example) to `backend/.env` and fill in:
   - `OPENAI_API_KEY`
   - `S3_BUCKET_NAME`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `REDIS_URL` if you want persistent memory
3. Install backend dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

4. Start the API:

```bash
uvicorn app.main:app --reload
```

## Frontend Setup

1. Copy [frontend/.env.example](/C:/Users/Ashut/OneDrive/Desktop/Projects/DocuChat/frontend/.env.example) to `frontend/.env`.
2. Install dependencies and run:

```bash
cd frontend
npm install
npm run dev
```

3. Open `http://localhost:5173`.

## API Endpoints

- `POST /upload`
  - Returns a presigned S3 upload URL, `doc_id`, and `s3_key`
- `POST /process`
  - Starts or performs PDF extraction, chunking, embeddings, and Chroma indexing
- `POST /chat`
  - Accepts `question`, `session_id`, and selected `doc_ids`
- `GET /history?session_id=...`
  - Returns recent session history
- `GET /documents/{doc_id}`
  - Returns processing status used by the frontend poller
- `GET /health`
  - Basic readiness check

## Local Docker

1. Copy env examples:

```bash
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
```

2. Start the stack:

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Redis: `localhost:6379`

## AWS Deployment Notes

### Backend on ECS or EC2
- Build the backend image from [backend/Dockerfile](/C:/Users/Ashut/OneDrive/Desktop/Projects/DocuChat/backend/Dockerfile)
- Inject secrets via AWS Secrets Manager or SSM Parameter Store
- Mount persistent storage for `backend/app/data` if you want Chroma persistence on a single instance
- For multi-instance production, move Chroma to a shared vector service or a stateful deployment strategy

### Frontend
- Build the React app from [frontend/Dockerfile](/C:/Users/Ashut/OneDrive/Desktop/Projects/DocuChat/frontend/Dockerfile)
- Serve through ECS, S3 + CloudFront, or an ALB-backed container
- Set `VITE_API_BASE_URL` to the deployed FastAPI endpoint

### S3 and CloudFront
- Keep the upload bucket private
- Use presigned URLs for direct browser uploads
- Optionally place CloudFront in front of a separate download bucket or generated previews

## Production Notes

- Current document status tracking is file-backed via `backend/app/data/documents.json`
- User isolation is handled through `X-User-Id` or optional JWT bearer parsing
- Chat responses are grounded against retrieved chunks and return source metadata for UI display
- Background processing is triggered with FastAPI `BackgroundTasks`

## Next Hardening Steps

- Replace file-backed document registry with PostgreSQL
- Add proper auth flows and user persistence
- Add rate limiting and structured request logging
- Add streaming chat over SSE or WebSockets
- Move Chroma to infrastructure that matches your scaling model
