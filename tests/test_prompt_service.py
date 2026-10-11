
import pytest

from backend.app.services.prompt_service import build_rag_prompt


class FakeChunk:
    def __init__(self, title, url, content):
        self.episode_title = title
        self.episode_url = url
        self.content = content


def test_prompt_includes_question_and_source():
    chunk = FakeChunk(
        "Product Prioritization",
        "https://example.com/episode",
        "Users ranked features as must-have or nice-to-have.",
    )

    prompt = build_rag_prompt(
        question="How should we prioritize features?",
        retrieved_chunks=[chunk],
    )

    assert "How should we prioritize features?" in prompt
    assert "[Source 1]" in prompt
    assert "Product Prioritization" in prompt
    assert "must-have or nice-to-have" in prompt
    assert "https://example.com/episode" in prompt


def test_prompt_includes_multiple_sources():
    chunks = [
        FakeChunk("Episode A", "https://example.com/a", "Evidence A."),
        FakeChunk("Episode B", "https://example.com/b", "Evidence B."),
    ]

    prompt = build_rag_prompt(
        question="What does the evidence suggest?",
        retrieved_chunks=chunks,
    )

    assert "[Source 1]" in prompt
    assert "[Source 2]" in prompt
    assert "Evidence A." in prompt
    assert "Evidence B." in prompt


def test_prompt_handles_no_sources():
    prompt = build_rag_prompt(
        question="What is the weather on Mars?",
        retrieved_chunks=[],
    )

    assert "No relevant transcript passages were retrieved." in prompt
    assert "insufficient" in prompt.lower()


def test_prompt_rejects_empty_question():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        build_rag_prompt(
            question="   ",
            retrieved_chunks=[],
        )
