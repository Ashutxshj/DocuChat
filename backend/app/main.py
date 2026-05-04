from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import chat, documents, health, history, process, upload
from app.utils.config import get_settings
from app.utils.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


settings = get_settings()

app = FastAPI(
    title="DocuChat Copilot API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(process.router, prefix="/process", tags=["processing"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
