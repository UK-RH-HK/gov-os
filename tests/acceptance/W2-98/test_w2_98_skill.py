"""W2-98: the skill's own text: success-1's Steps half, success-3's Done when, success-4's template, failure-3.

Reading rules (stated in the README): a *section* is a level-2 heading; its text runs to the next level-1 or level-2
heading. The body is what follows the front matter; its size limit is 150 lines with a 10 per cent tolerance (165).
The skill validator is the shared one (``gov.check.skill_validator``), run as a subprocess on a SKILL.md.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest

import w2_98_support as s

BODY_LINES_AT_MOST = 165  # "about 150": the template's number with a 10 per cent tolerance


def _validator(path, cwd):
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(s.REPO_ROOT / "src"), os.environ.get("PYTHONPATH", "")])}
    done = subprocess.run([sys.executable, "-m", "gov.check.skill_validator", str(path)], capture_output=True,
                          text=True, cwd=str(cwd), env=env, timeout=60, stdin=subprocess.DEVNULL)
    try:
        findings = json.loads(done.stdout.strip().splitlines()[-1]).get("findings", [])
    except (ValueError, IndexError, AttributeError):
        findings = [{"code": "UNREADABLE", "message": (done.stdout + done.stderr)[-300:]}]
    return done.returncode, findings


# success-4: the template's form -----------------------------------------------------------------------------------

def test_the_skill_validator_exits_0_on_the_skill(tmp_path):
    path = s.need(s.SKILL_DIR / "SKILL.md")
    code, findings = _validator(path, tmp_path)
    assert code == 0 and findings == [], f"the validator exit {code}, findings {findings}"


def test_the_front_matter_has_name_version_and_a_third_person_description():
    front, _ = s.split_frontmatter(s.read_skill())
    assert front is not None, "SKILL.md has no front matter"
    assert front.get("name") == s.SKILL_NAME, f"name is {front.get('name')!r}, expected {s.SKILL_NAME!r}"
    version = front.get("version")
    assert isinstance(version, str) and version, f"version is {version!r}: the validator wants a string at the top"
    meta = front.get("metadata") if isinstance(front.get("metadata"), dict) else {}
    assert str(meta.get("version", version)) == version, "metadata.version differs from version"
    description = front.get("description")
    assert isinstance(description, str) and description.strip(), "no description"
    words = re.findall(r"[A-Za-z']+", description)
    assert not {w.lower() for w in words} & {"i", "you", "your", "we", "our", "my", "me", "us"}, (
        f"the description speaks in the first or second person: {description!r}")
    first = words[0].lower() if words else ""
    assert first not in {"use", "write", "run", "check", "make", "create", "build", "apply", "follow", "read", "ask",
                         "help", "always", "never"}, f"the description opens with a command, not the third person: {description!r}"
    assert re.search(r"\b(when|use[sd]?|for)\b", description, re.I), (
        f"the description does not say when to use the skill: {description!r}")


def test_the_sections_stand_in_the_templates_order_with_sources_last():
    assert s.section_problems(s.read_skill()) == []


def test_steps_are_a_checklist():
    steps = s.section(s.read_skill(), r"steps")
    assert steps is not None, "no Steps section"
    assert len(re.findall(r"^\s*[-*] \[[ xX]\]", steps, re.M)) >= 3, "Steps has fewer than three checklist items"


def test_the_output_section_gives_the_twelve_fields():
    out = s.section(s.read_skill(), r"output and handover")
    assert out is not None, "no Output and handover section"
    plain = " ".join(out.replace("`", "").split()).lower()
    names_all = all(field in plain for field in s.TWELVE)
    assert names_all or "twelve fields" in plain, "the section neither names the twelve fields nor says 'twelve fields'"


def test_the_escalation_section_maps_to_p3_p2_p1_and_emergency():
    esc = s.section(s.read_skill(), r"escalation")
    assert esc is not None, "no Escalation section"
    for rank in ("P3", "P2", "P1", "Emergency"):
        assert re.search(rf"\b{rank}\b", esc, re.I), f"Escalation does not mention {rank}"


@pytest.mark.parametrize("title,pattern", [("Never", r"never\b"), ("Sources", r"sources\b")], ids=["Never", "Sources"])
def test_never_and_sources_have_content(title, pattern):
    block = s.section(s.read_skill(), pattern)
    assert block is not None, f"no {title} section"
    assert block.strip(), f"the {title} section is empty"
    if title == "Never":
        assert s.list_items(block), "the Never section lists nothing"


def test_the_body_is_about_150_lines():
    body = s.split_frontmatter(s.read_skill())[1]
    count = len(body.rstrip("\n").splitlines())
    assert count <= BODY_LINES_AT_MOST, f"the body is {count} lines (limit 150 with a tolerance of 10 per cent)"


def test_every_other_file_is_one_level_below_the_skill_folder_and_nothing_deeper():
    files = s.skill_files(s.need(s.SKILL_DIR / "SKILL.md").parent)
    deeper = [str(f) for f in files if len(f.parts) > 2]
    assert not deeper, f"files more than one folder level below the skill folder: {deeper}"
    here = {f.name for f in files if len(f.parts) == 1}
    for expected in ("SKILL.md", "spec-form.md", "check_spec.py", "imports.yaml"):
        assert expected in here, f"{expected} is not in the skill folder itself (I1, I2, I4)"


def test_skill_md_links_its_reference_file_and_names_the_check():
    text = s.read_skill()
    assert "spec-form.md" in text, "SKILL.md does not name spec-form.md"
    assert "check_spec.py" in text, "SKILL.md does not name check_spec.py"


def test_the_form_reference_states_the_nine_headings_the_columns_and_the_failure_line():
    form = " ".join(s.need(s.SKILL_DIR / "spec-form.md").read_text(encoding="utf-8").replace("`", "").split())
    missing = [h for h in s.HEADINGS if h.lower() not in form.lower()]
    assert not missing, f"spec-form.md does not name the headings {missing}"
    cols = [c for c in s.COLUMNS if c not in form.lower()]
    assert not cols, f"spec-form.md does not name the Test data columns {cols}"
    assert "Fails if:" in form, "spec-form.md does not state the 'Fails if:' line"


# success-1: the Steps name each part --------------------------------------------------------------------------------

STEP_IDEAS = {
    "the problem": r"problem",
    "users": r"\busers?\b",
    "scenarios": r"scenarios?",
    "goals": r"(?<!non-)(?<!non )\bgoals?\b",
    "non-goals": r"non-?\s?goals?",
    "KPIs": r"\bKPIs?\b",
    "each KPI's failure line": r"fail(ure)? (line|if)|fails if",
    "test data": r"test data",
    "what is out of scope": r"out of scope",
    "open questions": r"open questions?",
    "who accepts it": r"accept",
}


@pytest.mark.parametrize("part", sorted(STEP_IDEAS))
def test_the_steps_name_the_part(part):
    steps = s.section(s.read_skill(), r"steps")
    assert steps is not None, "no Steps section"
    assert re.search(STEP_IDEAS[part], steps, re.I), f"the Steps do not name {part}"


# success-3: the Done when ------------------------------------------------------------------------------------------

def _done_items():
    block = s.section(s.read_skill(), r"done when")
    assert block is not None, "no Done when section"
    return block, s.list_items(block)


def test_every_done_when_item_is_a_yes_no_check():
    """Strictness (README): the section lists at least two items (list lines; a closing or introducing sentence
    outside the list is allowed), and no item is a bare instruction to do work: each is a checklist box, a
    question, or a statement that can be read as true or false (it holds a verb of state: is/are/has/have/holds/
    passes/prints/exits/refused..., or no/every/each)."""
    _block, items = _done_items()
    assert len(items) >= 2, f"Done when has {len(items)} list items"
    state = re.compile(r"^\[[ xX]\]|\?|\b(is|are|has|have|holds?|passes|pass|prints?|exits?|refused|names?|states?|"
                       r"finds?|shows?|lists?|carries|carry|reads?|stands?|stand|no|every|each)\b", re.I)
    vague = [i for i in items if not state.search(i)]
    assert not vague, f"Done when items that are not yes/no checks: {vague}"


def test_done_when_has_the_kpi_without_code_item():
    _, items = _done_items()
    hits = [i for i in items if re.search(r"\bKPIs?\b", i) and re.search(r"\bcode\b", i, re.I)]
    assert hits, f"no Done when item says every KPI is testable without naming code: {items}"


def test_done_when_has_the_data_source_owner_and_licence_or_recipe_item():
    _, items = _done_items()
    hits = [i for i in items if re.search(r"\bowner\b", i, re.I) and re.search(r"licen[cs]e", i, re.I)
            and re.search(r"recipe", i, re.I)]
    assert hits, f"no Done when item says each data source has its owner and its licence or synthetic recipe: {items}"


# failure-3 (re-worded, DEC-1156 (5)) --------------------------------------------------------------------------------

def test_the_section_check_names_never_on_a_copy_with_the_never_section_removed(tmp_path):
    text = s.read_skill()
    planted = s.remove_section(text, r"never\b")
    assert planted != text, "the real skill has no '## Never' heading to remove"
    path = tmp_path / s.SKILL_NAME / "SKILL.md"
    path.parent.mkdir()
    path.write_text(planted, encoding="utf-8")
    problems = s.section_problems(path.read_text(encoding="utf-8"))
    assert any("Never" in p for p in problems), f"the section check does not name Never: {problems}"


@pytest.mark.parametrize("title,pattern", [(n, p) for n, p in s.SECTION_PATTERNS if n != "Never"],
                         ids=[n for n, _p in s.SECTION_PATTERNS if n != "Never"])
def test_the_section_check_passes_the_real_skill_and_names_each_section_removed(title, pattern):
    text = s.read_skill()
    assert s.section_problems(text) == []
    planted = s.remove_section(text, pattern)
    assert planted != text, f"the real skill has no '## {title}' heading"
    problems = s.section_problems(planted)
    assert any(f"section {title} is missing" in p for p in problems), f"removing {title} is not named: {problems}"


def test_the_validator_reports_a_400_line_body_with_no_reference_files(tmp_path):
    front_text = s.read_skill()
    front_block = front_text[:front_text.find("\n---", 3) + 4] + "\n"
    folder = tmp_path / s.SKILL_NAME
    folder.mkdir()
    long_body = "\n".join(f"Line {n}: the method says to write the spec before any code and to check it first."
                          for n in range(400))
    (folder / "SKILL.md").write_text(front_block + "\n# Spec writing\n\n" + long_body + "\n", encoding="utf-8")
    code, findings = _validator(folder / "SKILL.md", tmp_path)
    assert code == 1 and "SKILL_BODY_TOO_LONG" in [f["code"] for f in findings], f"{code}: {findings}"
    assert [p.name for p in folder.iterdir()] == ["SKILL.md"], "the planted copy has reference files"


def test_the_same_front_matter_with_a_short_body_does_not_draw_the_size_finding(tmp_path):
    front_text = s.read_skill()
    front_block = front_text[:front_text.find("\n---", 3) + 4] + "\n"
    folder = tmp_path / s.SKILL_NAME
    folder.mkdir()
    (folder / "SKILL.md").write_text(front_block + "\n# Spec writing\n\nA short body.\n", encoding="utf-8")
    code, findings = _validator(folder / "SKILL.md", tmp_path)
    assert "SKILL_BODY_TOO_LONG" not in [f["code"] for f in findings], findings
