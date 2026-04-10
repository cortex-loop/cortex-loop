"""Policy drift checks for correspondence acceptance discipline."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
CORRESPONDENCE_PATH = REPO_ROOT / "docs/archive/internal/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md"
IMPLEMENTATION_PLAN_PATH = REPO_ROOT / "docs/archive/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_correspondence_doc_keeps_landing_and_update_law_explicit() -> None:
    text = _read(CORRESPONDENCE_PATH)

    assert "Rule: **no load-bearing implementation seam may land without a correspondence row in this document.**" in text
    assert "require updates whenever a seam adds or moves a load-bearing implementation home" in text
    assert (
        "refuse to mark a seam fully landed if the seam creates a new load-bearing "
        "surface without either updating this document or explicitly justifying why "
        "no update is needed"
    ) in text
    assert (
        "Every seam completion must include: `Correspondence rows touched:` listing "
        "the rows added, updated, or confirmed."
    ) in text


def test_implementation_plan_keeps_verification_spine_rejection_rule_explicit() -> None:
    text = _read(IMPLEMENTATION_PLAN_PATH)

    assert "`Correspondence rows touched:` listing rows added, updated, or confirmed" in text
    assert (
        "No load-bearing seam may be marked `landed` if it introduces new mathematical "
        "objects or implementation homes without updating the correspondence ledger."
    ) in text


def test_agents_contract_no_longer_acts_as_correspondence_ledger() -> None:
    text = _read(AGENTS_PATH)

    assert "internal/truth/cortex_status.json" in text
    assert "docs/CORTEX_STATUS.md" in text
    assert "CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE" not in text
    assert "CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2" not in text
    assert "Correspondence impact:" not in text
    assert "Correspondence rows touched:" not in text
