"""K6: this repository's own CLAUDE.md and AGENTS.md gain the "Value first" line in their golden-rule section and
nothing else in them changes (DEC-1217 (7)). Kind: repository-state (it reads this repository's own files against the
ticket's base commit)."""

from __future__ import annotations

import difflib
import subprocess

import pytest

import w2_208_support as support

BASE = "8e72e0228"   # the ticket's base (the ticket commit; it adds the ticket file only)
VALUE_FIRST_LINE = ("- **Value first.** What matters is tests and code that match the KPIs and the spec and pass green. "
                    "Everything else, practicality and security work included, must justify itself against that.")
SECTION = "## Golden rule"
# Gov OS's own head may carry one more paragraph outside the golden-rule section: the pointer to the golden workflow, the
# spine the owner approved on 2026-11-24 (DEC-1244 WF (a)); it is optional here, never more than one, never in the section.
POINTER_PREFIX = "**The golden workflow** (`docs/emergency-2/GOLDEN-WORKFLOW.md`"


def _base_text(rel):
    done = subprocess.run(["git", "-C", str(support.REPO_ROOT), "show", f"{BASE}:{rel}"], capture_output=True,
                          text=True)
    assert done.returncode == 0, f"the base {BASE} cannot be read for {rel}: {done.stderr.strip()}"
    return done.stdout


def _section(text):
    start = text.find(SECTION)
    assert start >= 0, f"no {SECTION!r} section"
    end = text.find("\n## ", start + 1)
    return text[start:] if end < 0 else text[start:end]


@pytest.mark.parametrize("rel", support.TEXTS)
def test_k6_the_file_adds_the_value_first_line_in_its_golden_rule_section_and_removes_none(rel):
    base, now = _base_text(rel), (support.REPO_ROOT / rel).read_text(encoding="utf-8")
    diff = list(difflib.ndiff(base.splitlines(), now.splitlines()))
    removed = [line[2:] for line in diff if line.startswith("- ")]
    added = [line[2:] for line in diff if line.startswith("+ ") and line[2:].strip()]   # blank lines are no content
    pointer = [line for line in added if line.startswith(POINTER_PREFIX)]
    others = [line for line in added if not line.startswith(POINTER_PREFIX)]
    assert not removed, f"{rel} removes or changes lines of the base: {removed}"
    assert len(pointer) <= 1, f"{rel} adds the golden workflow pointer more than once: {pointer}"
    assert support.normalise(" ".join(others)) == support.normalise(VALUE_FIRST_LINE), (
        f"{rel} does not add exactly the Value first line (and at most the golden workflow pointer): added {added}")
    assert not pointer or 0 <= now.find(pointer[0]) < now.find(SECTION), (
        f"the golden workflow pointer of {rel} is not in the head, before its golden-rule section")
    assert support.normalise(VALUE_FIRST_LINE) in support.normalise(_section(now)), (
        f"the Value first line of {rel} is not in its golden-rule section")


def test_k6_the_two_files_golden_rule_sections_stay_equal():
    sections = {rel: _section((support.REPO_ROOT / rel).read_text(encoding="utf-8")) for rel in support.TEXTS}
    assert sections["CLAUDE.md"] == sections["AGENTS.md"], "the golden-rule sections of CLAUDE.md and AGENTS.md differ"
    assert support.normalise(VALUE_FIRST_LINE) in support.normalise(sections["CLAUDE.md"]), (
        "the golden-rule section does not hold the Value first line")
