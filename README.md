# DocuChat Copilot

DocuChat Copilot is a document-grounded AI chat application for uploading PDFs, indexing them into a vector store, and asking questions against that content with session memory and source attribution.

## Overview

The app combines a FastAPI backend, a React frontend, Gemini for generation and embeddings, and ChromaDB for retrieval. Users upload PDFs, the system extracts and chunks text, stores embeddings locally, and answers questions using retrieved document context.

## Features

- PDF upload and local file storage
- Background document processing
- Chunking with overlap for retrieval quality
- Gemini embeddings and grounded chat answers
- ChromaDB vector search
- Session-based chat memory
- Source references tied to document name and page number
- Multi-document querying from the chat workspace

## Stack

### Backend
- FastAPI
- Gemini API via `google-genai`
- ChromaDB
- PyPDF
- Optional Redis for persistent memory

### Frontend
- React
- Vite
- Zustand

### Storage
- Local filesystem for uploaded PDFs
- Local Chroma persistence for vectors
- Local JSON metadata registry

## Architecture

### Upload Flow
- `POST /upload` accepts a PDF via multipart form upload
- The backend stores the file under `LOCAL_STORAGE_PATH`
- A document record is created with status metadata

### Processing Flow
- `POST /process` reads the saved file
- PDF text is extracted page by page
- Text is chunked into token windows with overlap
- Gemini embeddings are generated
- Chunks and metadata are stored in ChromaDB

### Chat Flow
- `POST /chat` embeds the user question
- Top matching chunks are retrieved from ChromaDB
- Gemini answers only from retrieved context
- The response includes source labels and source document metadata

### Memory
- `GET /history` returns recent chat history for a session
- If Redis is configured, memory survives backend restarts
- If Redis is omitted, memory falls back to an in-process Python store

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

## Environment

The backend reads `backend/.env`.

Minimal backend config:

```env
APP_ENV=development
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_CHAT_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
LOCAL_STORAGE_PATH=./app/data/uploads
CHROMA_PERSIST_DIRECTORY=./app/data/chroma
CHROMA_COLLECTION_NAME=docuchat_chunks
CHAT_MEMORY_WINDOW=10
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
CHUNK_SIZE_TOKENS=800
CHUNK_OVERLAP_TOKENS=100
CORS_ORIGINS=["http://localhost:5173"]
```

Optional Redis:

```env
REDIS_URL=redis://localhost:6379/0
```

If you do not want Redis yet, leave that line out.

Frontend config:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEFAULT_USER_ID=demo-user
```

## Data Storage

Current storage is intentionally simple:

- Uploaded PDFs are stored locally
- Chroma vectors are persisted locally
- Document metadata is stored in `documents.json`
- Chat memory uses Redis if configured, otherwise in-memory storage

You do not need Supabase or another hosted database to run the current version.

## UX Notes

- Assistant answers are formatted for readability with paragraphs and lists
- The source panel shows document names and page numbers instead of raw chunk text
- The chat workspace is styled as a modern AI assistant interface

## Run The Project

### 1. Prepare Backend Env

Create `backend/.env` from `backend/.env.example`.

If Redis is not running, do not include `REDIS_URL`.

### 2. Start Backend on Windows PowerShell

Open PowerShell in `backend` and run:

```powershell
cd backend
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

If your prompt already shows `(.venv)`, the environment is active and you do not need to activate it again.

If activation causes trouble, run without activation:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend URLs:

```text
http://localhost:8000
http://localhost:8000/health
```

### 3. Start Frontend

Open a second terminal and run:

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

### 4. Optional Redis

If you want persistent chat memory, start Redis with Docker:

```powershell
docker run -d --name docuchat-redis -p 6379:6379 redis:7-alpine
```

Then set:

```env
REDIS_URL=redis://localhost:6379/0
```

If you are not using Redis, skip this step.

### 5. Use The App

1. Start the backend
2. Start the frontend
3. Open `http://localhost:5173`
4. Upload a PDF
5. Wait until processing finishes
6. Open the chat page
7. Ask questions about the document

### 6. Common Issues

- `uvicorn` not found:
  `pip install` did not finish successfully, or you should run `python -m uvicorn app.main:app --reload`
- PowerShell activation fails:
  Use `.\.venv\Scripts\Activate.ps1`, not `.\venv\Scripts\activate`
- Redis connection errors:
  Remove `REDIS_URL` from `backend/.env` or start Redis locally
- Gemini auth errors:
  Your `GEMINI_API_KEY` is invalid, expired, or needs rotation
- Frontend cannot connect:
  Ensure backend is running on `http://localhost:8000`
