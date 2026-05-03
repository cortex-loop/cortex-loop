from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


STATIC_TASK_IDENTITY_EXAMPLES = (
    ("docs search dataset marker", "hidden_verifier_fact", "static example"),
    ("hidden verifier answer", "hidden_verifier_fact", "static example"),
)


@dataclass(frozen=True, slots=True)
class TaskIdentityTerm:
    """Example task-identity term that may witness but not define Cortex law."""

    term: str
    category: str
    source: str


@dataclass(frozen=True, slots=True)
class ProductFixtureLeak:
    path: str
    term: str
    category: str = "task_identity"
    source: str = "unknown"


def task_identity_terms(root: Path) -> tuple[TaskIdentityTerm, ...]:
    """Return example task identities that must not become product triggers.

    This is an enforcement aid, not a complete ontology. The doctrine is
    category-based: product Cortex may key on executive state, not task
    identity. The scanner collects known examples from fixture banks and
    hidden-verifier phrases so the repo catches the common drift mechanically.
    """

    terms: set[TaskIdentityTerm] = {
        TaskIdentityTerm(term=term, category=category, source=source)
        for term, category, source in STATIC_TASK_IDENTITY_EXAMPLES
    }
    for fixture_root in (
        root / "tests" / "lab" / "fixtures" / "output_quality",
        root / "lab" / "fixtures" / "output_quality",
    ):
        if not fixture_root.is_dir():
            continue
        for child in fixture_root.iterdir():
            if child.is_dir() and child.name.strip():
                terms.add(
                    TaskIdentityTerm(
                        term=child.name.strip(),
                        category="lab_fixture_identity",
                        source=str(child.relative_to(root)),
                    )
                )
    return tuple(sorted(terms, key=lambda item: (item.category, item.term, item.source)))


def fixture_identity_terms(root: Path) -> tuple[str, ...]:
    """Return known fixture identity examples for legacy callers."""

    return tuple(item.term for item in task_identity_terms(root))


def find_product_task_identity_leaks(
    root: Path,
    *,
    product_root: str = "cortex",
) -> tuple[ProductFixtureLeak, ...]:
    """Find task-identity examples that leaked into product Cortex code."""

    terms = task_identity_terms(root)
    product_dir = root / product_root
    if not product_dir.is_dir():
        return ()
    leaks: list[ProductFixtureLeak] = []
    for path in sorted(product_dir.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        lowered = text.lower()
        for term in terms:
            if term.term.lower() in lowered:
                leaks.append(
                    ProductFixtureLeak(
                        path=str(path.relative_to(root)),
                        term=term.term,
                        category=term.category,
                        source=term.source,
                    )
                )
    return tuple(leaks)


def find_product_fixture_leaks(
    root: Path,
    *,
    product_root: str = "cortex",
) -> tuple[ProductFixtureLeak, ...]:
    """Compatibility wrapper for the task-identity leak scanner."""

    return find_product_task_identity_leaks(root, product_root=product_root)
