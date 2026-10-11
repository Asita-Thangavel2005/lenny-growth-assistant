from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.api import session_routes, chat_routes


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"]
    assert body["provider"] in {"local", "cloud"}


def test_create_session(monkeypatch):
    session_id = uuid4()
    now = datetime.now(timezone.utc)

    class FakeSession:
        id = session_id
        title = "Product growth"
        user_metadata = {"provider": "local"}
        created_at = now
        updated_at = now

    async def fake_create_session(**kwargs):
        assert kwargs["title"] == "Product growth"
        assert kwargs["user_metadata"] == {"provider": "local"}
        return FakeSession()

    async def fake_get_db():
        yield object()

    monkeypatch.setattr(session_routes, "create_session", fake_create_session)
    app.dependency_overrides[get_db] = fake_get_db

    try:
        response = client.post(
            "/sessions",
            json={
                "title": "Product growth",
                "user_metadata": {"provider": "local"},
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["title"] == "Product growth"
    assert response.json()["user_metadata"] == {"provider": "local"}
    assert response.json()["id"] == str(session_id)


def test_get_missing_session_returns_404(monkeypatch):
    async def fake_get_session(db, session_id):
        return None

    async def fake_get_db():
        yield object()

    monkeypatch.setattr(session_routes, "get_session", fake_get_session)
    app.dependency_overrides[get_db] = fake_get_db

    try:
        response = client.get(f"/sessions/{uuid4()}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Chat session not found."


def test_get_messages_for_missing_session_returns_404(monkeypatch):
    async def fake_get_session(db, session_id):
        return None

    async def fake_get_db():
        yield object()

    monkeypatch.setattr(session_routes, "get_session", fake_get_session)
    app.dependency_overrides[get_db] = fake_get_db

    try:
        response = client.get(f"/sessions/{uuid4()}/messages")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Chat session not found."


def test_chat_rejects_invalid_provider():
    response = client.post(
        "/chat",
        json={
            "session_id": str(uuid4()),
            "question": "How do I improve retention?",
            "provider": "unknown",
        },
    )

    assert response.status_code == 422


def test_chat_rejects_empty_question():
    response = client.post(
        "/chat",
        json={
            "session_id": str(uuid4()),
            "question": "",
            "provider": "local",
        },
    )

    assert response.status_code == 422


def test_chat_returns_404_for_missing_session(monkeypatch):
    async def fake_chat(**kwargs):
        raise ValueError("Chat session not found.")

    async def fake_get_db():
        yield object()

    monkeypatch.setattr(chat_routes, "chat", fake_chat)
    app.dependency_overrides[get_db] = fake_get_db

    try:
        response = client.post(
            "/chat",
            json={
                "session_id": str(uuid4()),
                "question": "How do I improve retention?",
                "provider": "local",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Chat session not found."

from backend.app.services.llm_service import LLMServiceError


def test_chat_returns_successful_response(monkeypatch):
    session_id = uuid4()

    async def fake_chat(**kwargs):
        assert kwargs["session_id"] == session_id
        assert kwargs["question"] == "How do I improve retention?"
        assert kwargs["provider"] == "local"

        return {
            "session_id": str(session_id),
            "answer": "Improve onboarding and measure activation.",
            "sources": [
                {
                    "episode_title": "Growth Strategies",
                    "episode_url": "https://example.com/episode",
                    "chunk_index": 2,
                    "content": "Focus on activation and retention.",
                }
            ],
        }

    async def fake_get_db():
        yield object()

    monkeypatch.setattr(chat_routes, "chat", fake_chat)
    app.dependency_overrides[get_db] = fake_get_db

    try:
        response = client.post(
            "/chat",
            json={
                "session_id": str(session_id),
                "question": "How do I improve retention?",
                "provider": "local",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == str(session_id)
    assert body["answer"] == "Improve onboarding and measure activation."
    assert body["sources"][0]["episode_title"] == "Growth Strategies"
    assert body["sources"][0]["chunk_index"] == 2


def test_chat_returns_502_when_llm_fails(monkeypatch):
    async def fake_chat(**kwargs):
        raise LLMServiceError("Internal provider failure details")

    async def fake_get_db():
        yield object()

    monkeypatch.setattr(chat_routes, "chat", fake_chat)
    app.dependency_overrides[get_db] = fake_get_db

    try:
        response = client.post(
            "/chat",
            json={
                "session_id": str(uuid4()),
                "question": "How do I improve retention?",
                "provider": "local",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "The language model could not generate a response."
    )
    assert "Internal provider failure details" not in response.text
