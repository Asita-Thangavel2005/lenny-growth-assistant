
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.transcript import TranscriptChunk
from backend.app.services.embedding_service import embed_text
from backend.app.core.config import settings


MIN_SIMILARITY = 0.40


async def retrieve_relevant_chunks(
    db: AsyncSession,
    query: str,
    top_k: int | None = None,
) -> list[TranscriptChunk]:
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    limit = settings.retrieval_top_k if top_k is None else top_k

    if limit < 1:
        raise ValueError("top_k must be at least 1.")

    query_embedding = embed_text(query)

    distance = TranscriptChunk.embedding.cosine_distance(query_embedding)

    statement = (
        select(TranscriptChunk, distance.label("distance"))
        .where(TranscriptChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(limit)
    )

    result = await db.execute(statement)

    relevant_chunks = []

    for chunk, distance_value in result.all():
        similarity = 1.0 - float(distance_value)

        if similarity >= MIN_SIMILARITY:
            relevant_chunks.append(chunk)

    return relevant_chunks
