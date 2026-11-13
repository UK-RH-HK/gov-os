"""S16 (success-16), the ticket's "S15 Search again once in the adopted repository"; I7: adoption copies, unchanged, the
kernel's retrieval skill (W2-142), the discovery skill's line (W2-142) and T-0's and T-8's "Search again once" line
(W2-128). Nothing is re-worded per repository.

A string test for "search again once", "own, different words", "not found" and "two searches" on the sources adoption copies
and on the copies a planted adoption holds. The sources: the kernel's retrieval skill, its discovery skill, and the brief
template that carries T-0's line (``template/governance/kernel/templates/brief.md``) and the CTO role template (T-8's carrier,
``role-cto.md``): this head holds the lines in the retrieval skill, ``brief.md`` and ``role-cto.md`` (so the source cases are
green here and stay green; they go red for W2-142 and W2-128 (``waits_on``) if the lines leave). The cases on the planted
adoption are red on the base: no stage of the chain copies the skill (package P-6 names the stage).
"""

from __future__ import annotations

import re

import pytest

import w2_88_support as W

PHRASES = ("search again once", "own, different words", "not found", "two searches")
KERNEL = W.REPO_ROOT / "template/governance/kernel"
SOURCES = {"the retrieval skill": KERNEL / "skills/retrieval/SKILL.md", "T-0's brief template": KERNEL / "templates/brief.md",
           "T-8's role template (CTO)": KERNEL / "templates/role-cto.md"}
SKILL_COPIES = ("skills/retrieval/SKILL.md",)


def holds(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text.lower())
    return [p for p in PHRASES if p not in flat]


@pytest.mark.parametrize("name", sorted(SOURCES))
def test_s16_guard_the_source_adoption_copies_holds_the_four_phrases(name):
    missing = holds(SOURCES[name].read_text(encoding="utf-8"))
    assert not missing, f"{name} lacks {missing} (W2-142 / W2-128's line is not on this head)"


def adopted_copies(project) -> list:
    return [p for p in project.rglob("*") if p.is_file() and ".git" not in p.parts and
            any(p.as_posix().endswith(tail) for tail in SKILL_COPIES)]


def test_s16_a_planted_adoption_holds_the_retrieval_skill_unchanged(worlds):
    nine = worlds.a9("default")
    nine.need_chain()
    copies = adopted_copies(nine.project)
    assert copies, ("the planted adoption holds no retrieval skill: no stage of the chain copies the kernel's skill "
                    "into the adopted repository (package P-6)")
    source = SOURCES["the retrieval skill"].read_bytes()
    for path in copies:
        assert path.read_bytes() == source, f"{path.relative_to(nine.project)} is not the kernel's skill, byte for byte"
        assert not holds(path.read_text(encoding="utf-8")), f"{path.name} lacks one of {PHRASES}"
