import logging
import uuid
from backend.app.services.skill_service import load_ship_30_for_30_skill
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.llm_service import generate_response
from backend.app.services.message_service import (
    get_session_messages,
    save_message,
)
from backend.app.services.prompt_service import build_rag_prompt
from backend.app.services.retrieval_service import retrieve_relevant_chunks
from backend.app.services.session_service import get_session

logger = logging.getLogger(__name__)

def is_ship_30_for_30_request(question: str) -> bool:
    normalized = question.casefold()
    return any(
        phrase in normalized
        for phrase in (
            "ship 30 for 30",
            "ship 30/30",
            "ship30for30",
        )
    )

async def chat(
    db: AsyncSession,
    session_id: uuid.UUID,
    question: str,
    provider: str | None = None,
) -> dict:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    session = await get_session(db, session_id)

    if session is None:
        raise ValueError("Chat session not found.")

    history = await get_session_messages(db, session_id)

    conversation_history = [
        {"role": message.role, "content": message.content}
        for message in history[-10:]
    ]

    await save_message(
        db=db,
        session_id=session_id,
        role="user",
        content=question,
    )


    chunks = await retrieve_relevant_chunks(db, question)

    if not chunks:
        answer = (
            "I couldn't find relevant evidence in Lenny's Podcast transcripts "
            "to answer this question. The available sources don't establish "
            "the requested information."
        )
    else:
        essay_skill = (
            load_ship_30_for_30_skill()
            if is_ship_30_for_30_request(question)
            else None
        )

        prompt = build_rag_prompt(
            question=question,
            retrieved_chunks=chunks,
            conversation_history=conversation_history,
            essay_skill=essay_skill,
        )

        answer = await generate_response(prompt, provider=provider)


    await save_message(
        db=db,
        session_id=session_id,
        role="assistant",
        content=answer,
        message_metadata={
            "sources": [
                {
                    "episode_title": chunk.episode_title,
                    "episode_url": chunk.episode_url,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                }
                for chunk in chunks
            ]
        },
    )

    logger.info(
        "Chat response generated for session %s using %s sources",
        session_id,
        len(chunks),
    )

    return {
        "session_id": str(session_id),
        "answer": answer,
        "sources": [
            {
                "episode_title": chunk.episode_title,
                "episode_url": chunk.episode_url,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
            }
            for chunk in chunks
        ],
    }
