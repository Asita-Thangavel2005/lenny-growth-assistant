import asyncio
from pathlib import Path

from backend.app.core.database import AsyncSessionLocal, engine
from backend.app.services.ingestion_service import ingest_transcript_file


TRANSCRIPT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "lennys-podcast-transcripts"
    / "episodes"
)


async def main():
    if not TRANSCRIPT_ROOT.exists():
        raise FileNotFoundError(f"Transcript directory not found: {TRANSCRIPT_ROOT}")

    files = sorted(TRANSCRIPT_ROOT.rglob("transcript.md"))

    if not files:
        print(f"No transcript files found under: {TRANSCRIPT_ROOT}")
        return

    total = len(files)
    ingested = 0
    skipped = 0
    failed = 0
    chunk_total = 0

    print(f"Found {total} transcript files.")

    try:
        async with AsyncSessionLocal() as db:
            for index, file_path in enumerate(files, start=1):
                try:
                    count = await ingest_transcript_file(db, file_path)

                    if count:
                        ingested += 1
                        chunk_total += count
                        print(
                            f"[{index}/{total}] Ingested "
                            f"{file_path.parent.name}: {count} chunks"
                        )
                    else:
                        skipped += 1
                        print(
                            f"[{index}/{total}] Skipped "
                            f"{file_path.parent.name}: already ingested"
                        )

                except Exception as exc:
                    failed += 1
                    await db.rollback()
                    print(
                        f"[{index}/{total}] FAILED "
                        f"{file_path.parent.name}: {type(exc).__name__}: {exc}"
                    )

    finally:
        await engine.dispose()

    print("\nIngestion summary")
    print(f"Transcript files found: {total}")
    print(f"Episodes ingested: {ingested}")
    print(f"Episodes skipped: {skipped}")
    print(f"Episodes failed: {failed}")
    print(f"New chunks stored: {chunk_total}")


if __name__ == "__main__":
    asyncio.run(main())
