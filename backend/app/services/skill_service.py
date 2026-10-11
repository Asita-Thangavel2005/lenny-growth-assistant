from functools import lru_cache
from pathlib import Path

SKILL_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "ship_30_for_30"
    / "SKILL.md"
)


@lru_cache(maxsize=1)
def load_ship_30_for_30_skill() -> str:
    if not SKILL_PATH.is_file():
        raise FileNotFoundError(
            f"Ship 30 for 30 skill not found: {SKILL_PATH}"
        )

    content = SKILL_PATH.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError("Ship 30 for 30 skill is empty.")

    return content
