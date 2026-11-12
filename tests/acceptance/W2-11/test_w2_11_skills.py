"""W2-11: the test-design skill, the skill template, orchestration's reference files, the qa-review skill and a
version in every skill copy (KPI lines 8, 9, 10, 14 of the README)."""
from __future__ import annotations

import re

import pytest

import w2_11_support as s


def _skill(name):
    return s.read(f"{s.SKILLS}/{name}/SKILL.md")


# KPI 8: the test-design skill -------------------------------------------------------------------------------------

TEST_DESIGN = {
    "proportion: the minimum that shows each KPI line and failure line [DEC-951 item 5]":
        ("DEC-951", [r"proportion", r"minimum", r"KPI line", r"failure line"]),
    "W2-60a's 2,980 test lines for 713 code lines are out of proportion":
        ("DEC-951", [r"2,?980", r"\b713\b", r"out of proportion"]),
    "the test kinds [DEC-889 item 11 c]":
        ("DEC-889", [r"\bunit\b", r"acceptance", r"live|harness", r"dev-tier", r"load-sensitive",
                     r"repository-state"]),
    "the run-time cost a test may take and how it is measured":
        ("DEC-889", [r"run[- ]time|seconds|minutes", r"cost|take|budget|limit", r"measur"]),
    "no copy of the whole working tree where a minimal fixture will do":
        ("DEC-889", [r"cop(y|ies)", r"whole|entire", r"tree", r"fixture"]),
    "a test of the live repository's own state is declared as such":
        ("DEC-889", [r"live repositor|repository's own state", r"declar"]),
    "the work order in parallel, never reading the engineer's work [DEC-959 item 7]":
        ("DEC-959", [r"parallel|same time|beside", r"engineer|implement", r"never read|not read|does not read"]),
    "red against the ticket's base": ("DEC-959", [r"\bred\b", r"\bbase\b"]),
    "ISTQB's black-box techniques":
        ("DEC-959", [r"ISTQB|black-box", r"equivalence partition", r"boundary value", r"decision table",
                     r"state transition"]),
    "the README map of KPI lines to tests that gov accept reads": ("DEC-959", [r"README", r"KPI", r"gov accept"]),
}


@pytest.mark.parametrize("rule", sorted(TEST_DESIGN))
def test_the_test_design_skill_states(rule):
    decision, ideas = TEST_DESIGN[rule]
    text = _skill("test-design")
    assert s.cites(text, decision), f"test-design does not cite {decision}"
    assert s.stated(text, ideas), f"test-design does not state: {rule}"


# KPI 9: one skill template [DEC-959 item 5, ROLES-RESEARCH-1 §2] -------------------------------------------------

SECTIONS = (r"when.*not when", r"^inputs?\b", r"^steps\b", r"^done when", r"output and handover",
            r"^escalation", r"^never\b", r"^sources\b")


def test_the_skill_template_has_the_front_matter_and_the_sections_in_order():
    text = s.read(s.SKILL_TEMPLATE_REL)
    front, body = s.split_frontmatter(text)
    assert front is not None and {"name", "version", "description"} <= set(front), (
        "skill.md has no front matter with name, version and description")
    assert s.stated(text, [r"third[- ]person", r"what|when"]), "skill.md does not ask for a third-person description"
    headings = [h.strip().lower() for h in re.findall(r"^#{2,3}\s+(.*)$", body, re.M)]
    at = [next((i for i, h in enumerate(headings) if re.search(p, h)), None) for p in SECTIONS]
    assert None not in at, f"skill.md lacks sections {[p for p, i in zip(SECTIONS, at) if i is None]}: {headings}"
    assert at == sorted(at) and at[-1] == len(headings) - 1, f"the sections are out of order or Sources is not last"
    steps = re.search(r"^#{2,3}\s+steps.*?$(.*?)(?=^#{1,3}\s|\Z)", body, re.M | re.I | re.S).group(1)
    assert re.search(r"^\s*[-*] \[ \]", steps, re.M), "the Steps section is not a checklist"


def test_the_skill_template_states_its_rules():
    text = s.read(s.SKILL_TEMPLATE_REL)
    assert s.cites(text, "DEC-959")
    for what, ideas in {"escalation P3/P2/P1/Emergency": [r"\bP3\b", r"\bP2\b", r"\bP1\b", r"emergency"],
                        "the body under about 150 lines": [r"\b150\b", r"lines"],
                        "reference files one level deep": [r"reference", r"one level"],
                        "three test scenarios before the text": [r"three", r"scenario", r"before|first"],
                        "imports licence-checked, passing three scenarios": [r"import", r"licen[cs]e", r"scenario"],
                        }.items():
        assert s.stated(text, ideas), f"skill.md does not state {what}"
    assert len(s.split_frontmatter(text)[1].splitlines()) <= 150, "skill.md's own body passes 150 lines"


# KPI 10: orchestration's three reference files; the qa-review skill ----------------------------------------------

REFERENCES = {
    "integration-queue": [r"enqueue", r"\btest", r"advance", r"eject", r"record"],
    "nightly-sheriff": [r"re-?run", r"alone", r"bisect", r"\bsmall\b", r"\bP1\b"],
    "incident-response": [r"\bstop", r"contain", r"\bP1\b", r"handoff|handover", r"blameless"],
}


@pytest.mark.parametrize("stem", sorted(REFERENCES))
def test_orchestration_has_the_reference_file(stem):
    folder = s.REPO_ROOT / s.SKILLS / "orchestration"
    found = [p for p in folder.glob(f"**/*{stem}*.md") if len(p.relative_to(folder).parts) <= 2]
    assert found, f"no {stem} reference file in {s.SKILLS}/orchestration/ (one level deep)"
    assert found[0].name in _skill("orchestration"), f"SKILL.md does not name {found[0].name}"
    text = found[0].read_text(encoding="utf-8")
    missing = [idea for idea in REFERENCES[stem] if not re.search(idea, text, re.I)]
    assert not missing, f"{found[0].name} does not state {missing}"


QA_REVIEW = {
    "trace each KPI line to its tests and code": [r"trace", r"KPI", r"test", r"code"],
    "tests against the spec": [r"tests? against the spec"],
    "code against the spec": [r"code against the spec"],
    "probes in proportion to the profile": [r"probe", r"proportion|profile", r"LITE|STANDARD|FULL"],
    "findings in JUDGEMENT's two lines": [r"Ordinary work: yes\|no", r"Consequence: fails open"],
    "severity tied to P3/P2/P1": [r"severity", r"\bP3\b", r"\bP2\b", r"\bP1\b"],
    "re-runs nothing": [r"re-?runs? nothing|never re-?runs?|does not re-?run"],
}


@pytest.mark.parametrize("rule", sorted(QA_REVIEW))
def test_the_qa_review_skill_states(rule):
    assert s.stated(_skill("qa-review"), QA_REVIEW[rule]), f"qa-review does not state: {rule}"


def test_the_qa_review_skill_has_its_three_copies():
    missing = [c for c in s.COPY_ROOTS if not (s.REPO_ROOT / c / "qa-review" / "SKILL.md").is_file()]
    assert not missing, f"qa-review has no copy under {missing}"


@pytest.mark.parametrize("name", ["test-design", "orchestration", "audit", "qa-review"])
def test_every_copy_carries_the_kernel_skills_body(name):
    kernel = s.plain(s.split_frontmatter(_skill(name))[1])
    differ = [c for c in s.COPY_ROOTS
              if s.plain(s.split_frontmatter(s.read(f"{c}/{name}/SKILL.md"))[1]) != kernel]
    assert not differ, f"the {name} copies under {differ} differ from the kernel source"


# KPI 14, G13: one version in every skill's four copies (DEC-832 item 2, DEC-981) --------------------------------

def _version(front):
    meta = front.get("metadata") if isinstance(front.get("metadata"), dict) else {}
    return front.get("version") or meta.get("version")


@pytest.mark.parametrize("name", [n for n in s.kernel_skill_names() if n != "adopt"])
def test_the_skill_carries_one_version_in_all_four_places(name):
    versions = {}
    for base in (s.SKILLS, *s.COPY_ROOTS):
        front, _ = s.split_frontmatter(s.read(f"{base}/{name}/SKILL.md"))
        assert front is not None, f"{base}/{name}/SKILL.md has no front matter"
        versions[base] = _version(front) if base != ".claude/skills" else (front.get("metadata") or {}).get("version")
        if base == ".claude/skills":
            extra = set(front) - s.CLAUDE_SKILL_KEYS
            assert not extra, f".claude/skills/{name}: keys rulesync does not write: {sorted(extra)}"
    assert all(versions.values()), f"{name}: no version in {[b for b, v in versions.items() if not v]}"
    assert len({str(v) for v in versions.values()}) == 1, f"{name}: the versions differ: {versions}"
