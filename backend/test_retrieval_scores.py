import asyncio

from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal, engine
from backend.app.models.transcript import TranscriptChunk
from backend.app.services.embedding_service import embed_text


async def main():
    queries = [
        "How should a startup decide which product features to prioritize?",
        "What is the current weather on Mars right now, and what is the exact temperature at the landing site?",
    ]

    try:
        async with AsyncSessionLocal() as db:
            for query in queries:
                query_embedding = embed_text(query)
                distance = TranscriptChunk.embedding.cosine_distance(query_embedding)

                statement = (
                    select(TranscriptChunk, distance.label("distance"))
                    .where(TranscriptChunk.embedding.is_not(None))
                    .order_by(distance)
                    .limit(5)
                )

                result = await db.execute(statement)

                print(f"\nQUERY: {query}")

                for rank, (chunk, score) in enumerate(result.all(), start=1):
                    similarity = 1 - float(score)
                    print(f"\n{rank}. Similarity: {similarity:.4f}")
                    print(f"Episode: {chunk.episode_title}")
                    print(f"Passage: {chunk.content[:250]}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
