from __future__ import annotations

import io

import tiktoken
from pypdf import PdfReader

from app.utils.config import get_settings


class PDFService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def extract_pages(self, pdf_bytes: bytes) -> list[dict[str, int | str]]:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages: list[dict[str, int | str]] = []
        for index, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append({"page_no": index, "text": text})
        return pages

    def chunk_pages(self, pages: list[dict[str, int | str]]) -> list[dict[str, int | str]]:
        chunks: list[dict[str, int | str]] = []
        max_tokens = self.settings.chunk_size_tokens
        overlap = self.settings.chunk_overlap_tokens

        for page in pages:
            text = str(page["text"])
            tokens = self.encoding.encode(text)
            start = 0
            chunk_index = 0
            while start < len(tokens):
                end = min(start + max_tokens, len(tokens))
                chunk_tokens = tokens[start:end]
                chunk_text = self.encoding.decode(chunk_tokens).strip()
                if chunk_text:
                    chunks.append(
                        {
                            "page_no": int(page["page_no"]),
                            "chunk_index": chunk_index,
                            "content": chunk_text,
                            "token_count": len(chunk_tokens),
                        }
                    )
                    chunk_index += 1
                if end >= len(tokens):
                    break
                start = max(0, end - overlap)

        return chunks


pdf_service = PDFService()
