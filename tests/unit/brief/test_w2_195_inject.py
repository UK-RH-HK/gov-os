"""W2-195 (DAEO-d8df) S2 and F1: a judging brief carries sections 1 to 3 of the installed judging-work skill file,
byte for byte, and names its version; a brief that judges nothing carries neither (DEC-1204 (5)).

Regression evidence only (DEC-136), on a planted repository with stand-in templates; the skill's bytes are the
kernel file's in this tree (and a changed copy, so the brief is shown to follow the installed file).
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest

from gov.brief import judging
from gov.brief.build import build

REPO = Path(__file__).resolve().parents[3]
KERNEL_REL = "template/governance/kernel/skills/judging-work/SKILL.md"
ADOPTED_REL = "governance/kernel/skills/judging-work/SKILL.md"
PRELOADED_REL = ".claude/skills/judging-work/SKILL.md"
# The approved text's bytes (version 1.2.0, W2-208's text agreeing with the kit's head, approved by the CTO by naming
# it, DEC-1217 (7)) and its sections 1 to 3: the approval is on the committed bytes, so these two stay pinned; every
# version a test names is read from the file instead (version_in).
APPROVED_SHA = "8f05fbead54ba3f58af1358339bcec3dcfb282a60d777c14a6ff295c4b432762"
SECTIONS_SHA = "0e55e871d4027d71a80d9f35c6524d58caa05196abc660f6133ab6d334765e68"

T0 = """---
name: brief
version: 1.0.0
role: any
---
# Your assignment
You are a fresh {ROLE} session (template `{ROLE_TEMPLATE}`). Ticket {ID} ({W2}).
{KPI_TABLE: | id | line | verify |}
End of T-0.
"""
ROLES = {
    "role-engineer": "---\nname: role-engineer\nversion: 1.2.0\nrole: engineer\n---\n# You are the engineer\n",
    "role-test-designer": "---\nname: role-test-designer\nversion: 1.0.0\nrole: independent-test-designer\n---\n"
                          "# You are the test designer\n",
    "role-reviewer": "---\nname: role-reviewer\nversion: 1.0.1\nrole: independent-auditor\nskills: [audit, "
                     "judging-work]\n---\n# You are the reviewer\n",
    "role-lead": "---\nname: role-lead\nversion: 1.0.0\nrole: orchestrator\n---\n# Lead\n"
                 "## Your run: {RUN_KIND} (only this section)\n**build**: implement.\n1. Build it.\n\n"
                 "**review**: one review round.\n1. Brief the reviewer; then the probe.\n\n## Return\nReturn line.\n",
}
FACTS = "paths:\n  tree: '/w/{W2}'\n  tests_tree: '/w/{W2}-tests'\nbudgets: {brief: 4000}\n" \
        "ready: {new_since: \"2026-11-10\"}\n"
KEYS = "keys: [ID, W2, ROLE, ROLE_TEMPLATE, KPI_TABLE, RUN_KIND, TREE, TESTS_TREE]\n"
TICKET = {"id": "DAEO-aaaa", "external-ref": "W2-900", "status": "open", "created": "2026-11-01T10:00:00Z",
          "role": "engineer", "allowed_paths": ["src/x/**"], "non_goals": ["nothing else"], "est_loc": 100,
          "kpis": {"success": [{"line": "S1 it works", "verify": "a test"}]}}
JUDGING = [("independent-auditor", None), ("qa-engineer", None), ("lead", "review")]
NOT_JUDGING = [("engineer", None), ("independent-test-designer", None), ("lead", "build")]


def kernel_bytes() -> bytes:
    return (REPO / KERNEL_REL).read_bytes()


def version_in(data: bytes) -> str:
    """The version a skill file's front matter states on its top-level ``version:`` line, read by the test itself."""
    match = re.search(rb'^version: "([^"]+)"$', data.split(b"\n---\n", 1)[0], re.M)
    assert match, "the skill file states no top-level version"
    return match.group(1).decode("utf-8")


def bumped(version: str) -> str:
    """Another version than ``version``: its last number plus one (1.1.0 -> 1.1.1)."""
    head, _, last = version.rpartition(".")
    return f"{head}.{int(last) + 1}"


def with_version(data: bytes, new: str) -> bytes:
    """``data`` with every ``version: "<its version>"`` line (top-level and ``metadata``) stating ``new``."""
    old = version_in(data)
    out = data.replace(f'version: "{old}"'.encode(), f'version: "{new}"'.encode())
    assert out != data
    return out


VERSION = version_in(kernel_bytes())


def rulesync_form(data: bytes) -> bytes:
    """The generated copy's form: front matter name, description and metadata.version only, no top-level version,
    the blank line after the front matter dropped (as rulesync writes ``.claude/skills/``)."""
    text = data.decode("utf-8")
    end = text.index("\n---\n", 3)
    head, body = text[:end], text[end + 5:]
    front = [line for line in head.split("\n")[1:] if not line.startswith("version:")]
    return ("---\n" + "\n".join(front) + "\n---\n" + body.lstrip("\n")).encode("utf-8")


def changed_copy() -> bytes:
    """A copy of the next version with one word of section 2 changed: what a brief built from a constant would miss."""
    data = with_version(kernel_bytes(), bumped(VERSION))
    data = data.replace(b"Ask of every finding, word for word:", b"Ask of each finding, word for word:")
    assert data != kernel_bytes()
    return data


def sections_of(data: bytes) -> bytes:
    start = data.index(b"\n## 1. The threat model\n") + 1
    return data[start:data.index(b"\n## 4. Doing it\n") + 1]


def plant(tmp_path: Path, kernel: bytes | None = None, preloaded: bytes | None = None, adopted: bool = False) -> Path:
    """A repository with the brief's stand-in templates, a ready ticket and the skill installed (kernel and
    preloaded copy); ``adopted`` puts the kernel under ``governance/kernel/`` with no ``template/``."""
    root = tmp_path / "repo"
    base = root / ("governance/kernel" if adopted else "template/governance/kernel")
    (base / "templates").mkdir(parents=True)
    for stem, text in {"brief": T0, **ROLES}.items():
        (base / "templates" / f"{stem}.md").write_text(text, encoding="utf-8")
    (base / "templates/keys.yaml").write_text(KEYS, encoding="utf-8")
    (root / "governance/project").mkdir(parents=True, exist_ok=True)
    (root / "governance/project/facts.yaml").write_text(FACTS, encoding="utf-8")
    (root / ".tickets").mkdir()
    (root / ".tickets/DAEO-aaaa.md").write_text("---\n" + json.dumps(TICKET) + "\n---\n# W2-900 T\n\nSummary.\n",
                                               encoding="utf-8")
    kernel = kernel_bytes() if kernel is None else kernel
    skill = base / "skills/judging-work/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_bytes(kernel)
    copy = root / PRELOADED_REL
    copy.parent.mkdir(parents=True)
    copy.write_bytes(rulesync_form(kernel) if preloaded is None else preloaded)
    return root


def brief_of(root: Path, role: str, run: str | None) -> str:
    out = build(root, role, "W2-900", run=run)
    assert out["findings"] == [], out["findings"]
    return out["brief"]


def test_the_kernel_skill_in_this_tree_is_the_approved_text_quoted():
    assert hashlib.sha256(kernel_bytes()).hexdigest() == APPROVED_SHA
    assert hashlib.sha256(sections_of(kernel_bytes())).hexdigest() == SECTIONS_SHA


@pytest.mark.parametrize("role, run", JUDGING)
def test_a_judging_brief_holds_sections_1_to_3_byte_for_byte_and_its_version(tmp_path, role, run):
    brief = brief_of(plant(tmp_path), role, run)
    assert sections_of(kernel_bytes()).decode("utf-8") in brief
    named = [line for line in brief.split("\n") if "judging-work" in line and f"version {VERSION}" in line]
    assert named == [f"Judging work: the judging-work skill, version {VERSION} (sections 1 to 3 of {KERNEL_REL}, "
                     f"verbatim):"]


@pytest.mark.parametrize("role, run", JUDGING)
def test_f1_the_carried_sections_hash_as_the_installed_files_sections(tmp_path, role, run):
    for kernel, version in ((kernel_bytes(), VERSION), (changed_copy(), bumped(VERSION))):
        shutil.rmtree(tmp_path / "repo", ignore_errors=True)
        brief = brief_of(plant(tmp_path, kernel=kernel), role, run).encode("utf-8")
        start = brief.index(b"\n## 1. The threat model\n") + 1
        carried = brief[start:start + len(sections_of(kernel))]
        assert hashlib.sha256(carried).hexdigest() == hashlib.sha256(sections_of(kernel)).hexdigest()
        assert f"version {version} ".encode() in brief
    assert hashlib.sha256(sections_of(kernel_bytes())).hexdigest() != hashlib.sha256(
        sections_of(changed_copy())).hexdigest()


@pytest.mark.parametrize("role, run", NOT_JUDGING)
def test_a_brief_that_judges_nothing_holds_neither_the_sections_nor_the_version_line(tmp_path, role, run):
    brief = brief_of(plant(tmp_path), role, run)
    assert "## 1. The threat model" not in brief and "judging-work" not in brief


@pytest.mark.parametrize("role, run", NOT_JUDGING)
def test_a_brief_that_judges_nothing_needs_no_skill(tmp_path, role, run):
    root = plant(tmp_path)
    shutil.rmtree(root / "template/governance/kernel/skills")
    shutil.rmtree(root / ".claude")
    brief_of(root, role, run)


def test_in_an_adopted_tree_the_brief_reads_governance_kernel(tmp_path):
    brief = brief_of(plant(tmp_path, adopted=True), "independent-auditor", None)
    assert sections_of(kernel_bytes()).decode("utf-8") in brief
    assert f"sections 1 to 3 of {ADOPTED_REL}, verbatim" in brief


def test_a_preloaded_copy_with_a_top_level_version_passes_too(tmp_path):
    brief = brief_of(plant(tmp_path, preloaded=kernel_bytes()), "qa-engineer", None)
    assert f"version {VERSION} " in brief


def test_the_qa_engineer_is_a_brief_role_on_the_reviewer_template():
    from gov.brief import ROLE_TEMPLATES
    assert ROLE_TEMPLATES["qa-engineer"] == "role-reviewer"


def test_judging_names_the_judging_briefs():
    assert [judging.judges(role, run) for role, run in JUDGING] == [True, True, True]
    assert [judging.judges(role, run) for role, run in NOT_JUDGING] == [False, False, False]
