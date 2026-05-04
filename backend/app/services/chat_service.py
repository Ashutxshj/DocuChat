from __future__ import annotations

from openai import AsyncOpenAI

from app.models.schemas import ChatRequest, ChatResponse, SourceReference
from app.services.chat_memory import chat_memory_service
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store_service
from app.utils.config import get_settings


class ChatService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        if self.client is None:
            self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        return self.client

    async def answer_question(self, payload: ChatRequest, user_id: str) -> ChatResponse:
        client = self._get_client()
        history = await chat_memory_service.get_history(
            user_id=user_id,
            session_id=payload.session_id,
            limit=self.settings.chat_memory_window,
        )
        query_embedding = await embedding_service.embed_texts([payload.question])
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
                f"[{label}] doc_id={metadata['doc_id']} page={metadata['page_no']} chunk={metadata['chunk_index']}\n{snippet}"
            )
            sources.append(
                SourceReference(
                    source_id=label,
                    doc_id=str(metadata["doc_id"]),
                    page_no=int(metadata["page_no"]),
                    chunk_index=int(metadata["chunk_index"]),
                    snippet=snippet[:280],
                    score=float(match["distance"]) if match["distance"] is not None else None,
                )
            )

        history_items = [
            {"role": message.role, "content": [{"type": "input_text", "text": message.content}]}
            for message in history
        ]
        history_items.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": self._build_user_prompt(payload.question, context_blocks),
                    }
                ],
            }
        )

        response = await client.responses.create(
            model=self.settings.openai_chat_model,
            instructions=self._system_prompt(),
            input=history_items,
            max_output_tokens=700,
        )
        answer = response.output_text.strip()

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
            "Be concise, accurate, and cite source labels like [S1] inline for factual claims."
        )

    def _build_user_prompt(self, question: str, context_blocks: list[str]) -> str:
        context = "\n\n".join(context_blocks) if context_blocks else "No relevant context was retrieved."
        return f"Question:\n{question}\n\nContext:\n{context}"


chat_service = ChatService()
