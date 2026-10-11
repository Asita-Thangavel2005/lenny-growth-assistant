
import asyncio

from backend.app.core.database import Base, engine
from backend.app.models import ChatSession, ChatMessage, TranscriptChunk


async def main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    print("Database tables created successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
