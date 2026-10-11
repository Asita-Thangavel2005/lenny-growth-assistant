
import re
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.transcript import TranscriptChunk
from backend.app.services.embedding_service import embed_texts


def split_transcript(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be between zero and chunk size.")

    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())

        if end == len(text):
            break

        start = end - overlap

    return chunks


def parse_transcript_file(file_path: Path) -> tuple[dict, str]:
    raw = file_path.read_text(encoding="utf-8-sig")

    if not raw.startswith("---"):
        raise ValueError(f"Missing YAML frontmatter: {file_path}")

    parts = raw.split("---", 2)

    if len(parts) != 3:
        raise ValueError(f"Invalid YAML frontmatter: {file_path}")

    metadata = yaml.safe_load(parts[1]) or {}
    content = parts[2].strip()

    if not isinstance(metadata, dict):
        raise ValueError(f"Frontmatter must be a mapping: {file_path}")

    return metadata, content


async def ingest_transcript_file(
    db: AsyncSession,
    file_path: Path,
) -> int:
    metadata, transcript = parse_transcript_file(file_path)

    title = str(metadata.get("title") or file_path.parent.name).strip()
    url = metadata.get("youtube_url")
    chunks = split_transcript(transcript)

    if not chunks:
        raise ValueError(f"No transcript text found: {file_path}")

    existing = await db.execute(
        select(TranscriptChunk.id)
        .where(TranscriptChunk.episode_title == title)
        .limit(1)
    )

    if existing.scalar_one_or_none() is not None:
        return 0

    embeddings = embed_texts(chunks)

    try:
        for index, (content, embedding) in enumerate(zip(chunks, embeddings)):
            db.add(
                TranscriptChunk(
                    episode_title=title,
                    episode_url=str(url) if url else None,
                    chunk_index=index,
                    content=content,
                    embedding=embedding,
                )
            )

        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return len(chunks)
