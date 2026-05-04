from __future__ import annotations

import asyncio
import logging

from fastapi import HTTPException
from google import genai
from google.genai import errors, types

from app.models.schemas import ChatRequest, ChatResponse, SourceReference
from app.services.chat_memory import chat_memory_service
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store_service
from app.utils.config import get_settings

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if not self.settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        if self.client is None:
            self.client = genai.Client(api_key=self.settings.gemini_api_key)
        return self.client

    async def answer_question(self, payload: ChatRequest, user_id: str) -> ChatResponse:
        client = self._get_client()
        history = await chat_memory_service.get_history(
            user_id=user_id,
            session_id=payload.session_id,
            limit=self.settings.chat_memory_window,
        )
        query_embedding = await embedding_service.embed_texts(
            [payload.question],
            task_type="RETRIEVAL_QUERY",
        )
        matches = await vector_store_service.query(
            query_embedding=query_embedding[0],
            user_id=user_id,
            doc_ids=payload.doc_ids,
            top_k=payload.top_k or self.settings.retrieval_top_k,
        )

        context_blocks: list[str] = []
        sources: list[SourceReference] = []
        for index, match in enumerate(matches, start=1):
            label = f"S{index}"
            metadata = match["metadata"]
            snippet = str(match["document"]).replace("\n", " ").strip()
            context_blocks.append(
                f"[{label}] document={metadata['filename']} doc_id={metadata['doc_id']} page={metadata['page_no']} chunk={metadata['chunk_index']}\n{snippet}"
            )
            sources.append(
                SourceReference(
                    source_id=label,
                    doc_id=str(metadata["doc_id"]),
                    filename=str(metadata["filename"]),
                    page_no=int(metadata["page_no"]),
                    chunk_index=int(metadata["chunk_index"]),
                    score=float(match["distance"]) if match["distance"] is not None else None,
                )
            )

        response = await self._generate_with_retry(
            client=client,
            contents=self._build_contents(history, payload.question, context_blocks),
        )
        answer = (response.text or "").strip()

        await chat_memory_service.append_message(user_id, payload.session_id, "user", payload.question)
        await chat_memory_service.append_message(user_id, payload.session_id, "assistant", answer)

        return ChatResponse(
            session_id=payload.session_id,
            answer=answer,
            sources=sources,
        )

    def _system_prompt(self) -> str:
        return (
            "You are DocuChat Copilot, a document QA assistant. Answer using only the provided context. "
            "If the answer is not supported by the retrieved chunks, say that the document context is insufficient. "
            "Format answers clearly using short paragraphs, bullet lists, and numbered steps when that improves readability. "
            "Use markdown-style plain text formatting only. Start with the direct answer, then organize supporting details. "
            "Be concise, accurate, and cite source labels like [S1] inline for factual claims. "
            "Do not invent citations or details beyond context."
        )

    def _build_user_prompt(self, question: str, context_blocks: list[str]) -> str:
        context = "\n\n".join(context_blocks) if context_blocks else "No relevant context was retrieved."
        return f"Question:\n{question}\n\nContext:\n{context}"

    def _build_contents(self, history: list, question: str, context_blocks: list[str]) -> list[types.Content]:
        contents: list[types.Content] = []
        for message in history:
            role = "model" if message.role == "assistant" else "user"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=message.content)],
                )
            )
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=self._build_user_prompt(question, context_blocks))],
            )
        )
        return contents

    async def _generate_with_retry(self, client: genai.Client, contents: list[types.Content]):
        delays = [1.0, 2.0, 4.0]

        for attempt, delay in enumerate(delays, start=1):
            try:
                return await asyncio.to_thread(
                    client.models.generate_content,
                    model=self.settings.gemini_chat_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=self._system_prompt(),
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                        temperature=0.2,
                        max_output_tokens=700,
                    ),
                )
            except errors.ServerError as exc:
                status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
                if status_code != 503 or attempt == len(delays):
                    logger.exception("Gemini generation failed after retries")
                    raise HTTPException(
                        status_code=503,
                        detail="The Gemini model is temporarily overloaded. Please retry in a few seconds.",
                    ) from exc
                logger.warning("Gemini overloaded on attempt %s, retrying in %ss", attempt, delay)
                await asyncio.sleep(delay)
            except Exception as exc:
                logger.exception("Unexpected Gemini generation failure")
                raise HTTPException(
                    status_code=502,
                    detail="The AI service returned an unexpected error.",
                ) from exc


chat_service = ChatService()
