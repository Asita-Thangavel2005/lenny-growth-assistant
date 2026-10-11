
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.chat_routes import router as chat_router
from backend.app.api.session_routes import router as session_router
from backend.app.core.config import settings
from backend.app.core.database import close_database
from backend.app.core.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.app_name)
    yield
    await close_database()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.app_name,
    description="A transcript-grounded assistant for product and growth questions.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router)
app.include_router(chat_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "provider": settings.llm_provider,
    }
