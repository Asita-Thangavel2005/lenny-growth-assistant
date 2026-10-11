
import asyncio

from backend.app.core.database import AsyncSessionLocal, engine
from backend.app.services.retrieval_service import retrieve_relevant_chunks


async def main():
    query = "How should a startup decide which product features to prioritize?"

    try:
        async with AsyncSessionLocal() as db:
            chunks = await retrieve_relevant_chunks(db, query, top_k=5)

            print(f"Query: {query}")
            print(f"Results: {len(chunks)}")

            for index, chunk in enumerate(chunks, start=1):
                print(f"\n--- Result {index} ---")
                print(f"Episode: {chunk.episode_title}")
                print(f"URL: {chunk.episode_url}")
                print(f"Chunk: {chunk.chunk_index}")
                print(f"Text: {chunk.content[:600]}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
