from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


STATIC_FIXTURE_LEAK_TERMS = (
    "docs search dataset marker",
    "hidden verifier answer",
)


@dataclass(frozen=True, slots=True)
class ProductFixtureLeak:
    path: str
    term: str


def fixture_identity_terms(root: Path) -> tuple[str, ...]:
    """Return fixture identities that may not become product Cortex policy."""

    terms: set[str] = set(STATIC_FIXTURE_LEAK_TERMS)
    for fixture_root in (
        root / "tests" / "lab" / "fixtures" / "output_quality",
        root / "lab" / "fixtures" / "output_quality",
    ):
        if not fixture_root.is_dir():
            continue
        for child in fixture_root.iterdir():
            if child.is_dir() and child.name.strip():
                terms.add(child.name.strip())
    return tuple(sorted(terms))


def find_product_fixture_leaks(
    root: Path,
    *,
    product_root: str = "cortex",
) -> tuple[ProductFixtureLeak, ...]:
    """Find lab-fixture identities that leaked into product Cortex code."""

    terms = fixture_identity_terms(root)
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
            if term.lower() in lowered:
                leaks.append(
                    ProductFixtureLeak(
                        path=str(path.relative_to(root)),
                        term=term,
                    )
                )
    return tuple(leaks)
