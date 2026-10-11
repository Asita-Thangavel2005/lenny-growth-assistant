from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.transcript import TranscriptChunk


async def save_transcript_chunk(
    db: AsyncSession,
    episode_title: str,
    content: str,
    chunk_index: int,
    episode_url: str | None = None,
    embedding: list[float] | None = None,
) -> TranscriptChunk:
    if not episode_title.strip():
        raise ValueError("Episode title cannot be empty.")

    if not content.strip():
        raise ValueError("Transcript content cannot be empty.")

    if chunk_index < 0:
        raise ValueError("Chunk index cannot be negative.")

    if embedding is not None and len(embedding) != 384:
        raise ValueError("Embedding must contain exactly 384 dimensions.")

    chunk = TranscriptChunk(
        episode_title=episode_title,
        episode_url=episode_url,
        chunk_index=chunk_index,
        content=content,
        embedding=embedding,
    )

    db.add(chunk)
    await db.commit()
    await db.refresh(chunk)

    return chunk


async def get_transcript_chunk(
    db: AsyncSession,
    chunk_id,
) -> TranscriptChunk | None:
    result = await db.execute(
        select(TranscriptChunk).where(TranscriptChunk.id == chunk_id)
    )
    return result.scalar_one_or_none()


async def get_episode_chunks(
    db: AsyncSession,
    episode_title: str,
) -> list[TranscriptChunk]:
    result = await db.execute(
        select(TranscriptChunk)
        .where(TranscriptChunk.episode_title == episode_title)
        .order_by(TranscriptChunk.chunk_index)
    )
    return list(result.scalars().all())
