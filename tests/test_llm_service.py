
import pytest

from backend.app.services import llm_service


@pytest.mark.anyio
async def test_local_provider_uses_ollama(monkeypatch):
    async def fake_local(prompt):
        return "Local response"

    async def fake_cloud(prompt):
        raise AssertionError("Cloud should not be called")

    monkeypatch.setattr(llm_service, "generate_local", fake_local)
    monkeypatch.setattr(llm_service, "generate_cloud", fake_cloud)

    result = await llm_service.generate_response(
        "Test prompt",
        provider="local",
    )

    assert result == "Local response"


@pytest.mark.anyio
async def test_cloud_provider_uses_claude(monkeypatch):
    async def fake_cloud(prompt):
        return "Cloud response"

    async def fake_local(prompt):
        raise AssertionError("Local should not be called")

    monkeypatch.setattr(llm_service, "generate_cloud", fake_cloud)
    monkeypatch.setattr(llm_service, "generate_local", fake_local)

    result = await llm_service.generate_response(
        "Test prompt",
        provider="cloud",
    )

    assert result == "Cloud response"


@pytest.mark.anyio
async def test_cloud_failure_falls_back_to_ollama(monkeypatch):
    async def fake_cloud(prompt):
        raise llm_service.LLMServiceError("Cloud unavailable")

    async def fake_local(prompt):
        return "Fallback response"

    monkeypatch.setattr(llm_service, "generate_cloud", fake_cloud)
    monkeypatch.setattr(llm_service, "generate_local", fake_local)

    result = await llm_service.generate_response(
        "Test prompt",
        provider="cloud",
    )

    assert result == "Fallback response"


@pytest.mark.anyio
async def test_missing_provider_uses_configured_default(monkeypatch):
    async def fake_local(prompt):
        return "Default local response"

    monkeypatch.setattr(llm_service.settings, "llm_provider", "local")
    monkeypatch.setattr(llm_service, "generate_local", fake_local)

    result = await llm_service.generate_response("Test prompt")

    assert result == "Default local response"
