"""W2-100, the four real skills as they stand in the repository (repository-state cases): success-1, success-2 (the
grep half), success-3, failure-1, failure-2 (the text half), failure-3, plus the planted copies the validator is shown
on (the size and the permission key).

Reading rules (README): a *section* is a level-2 heading; the template's eight in order, Sources last; the five labelled
parts and the area's named points are found as the ticket's Interface states (heading of level 2-4, or a line starting
with the name and a colon; points case-insensitive, whitespace folded, a hyphen a space). The body is what follows the
front matter, at most 165 lines ("about 150" with 10 per cent). The skill validator is the shared one
(``gov.check.skill_validator``), run as a subprocess.
"""
from __future__ import annotations

import re

import pytest

import w2_100_support as s

COMMAND_VERBS = {"use", "write", "run", "check", "make", "create", "build", "apply", "follow", "read", "ask", "help",
                 "always", "never", "load", "keep"}
PERSON_WORDS = {"i", "you", "your", "we", "our", "my", "me", "us"}


def _front(skill):
    front, _ = s.split_frontmatter(s.real_skill(skill))
    assert front is not None, f"{skill}/SKILL.md has no front matter"
    return front


def _body(skill):
    return s.split_frontmatter(s.real_skill(skill))[1]


# the folder ---------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_skill_folder_holds_skill_md_scenarios_and_its_check(skill):
    for name in s.BASE_FILES:
        s.need(s.skill_dir(skill) / name)


@pytest.mark.parametrize("skill", s.SKILLS)
def test_no_file_lies_more_than_one_folder_level_below_the_skill_folder(skill):
    files = s.skill_files(s.need(s.skill_dir(skill) / "SKILL.md").parent)
    deeper = [str(f) for f in files if len(f.parts) > 2]
    assert not deeper, f"files more than one folder level below the skill folder: {deeper}"


def test_the_four_check_scripts_are_byte_equal():
    scripts = {skill: s.need(s.skill_dir(skill) / s.SCRIPT).read_bytes() for skill in s.SKILLS}
    assert len(set(scripts.values())) == 1, f"the four {s.SCRIPT} files differ: {sorted(scripts)}"


# success-3: the skill template --------------------------------------------------------------------------------------

@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_front_matter_is_the_templates_with_nothing_more(skill):
    front = _front(skill)
    assert set(front) == {"name", "version", "description", "output", "metadata"}, (
        f"front matter keys are {sorted(front)}; the template's are name, version, description, output, metadata")
    assert front["name"] == skill, f"name is {front['name']!r}, the folder's name is {skill!r}"
    assert front["version"] == "1.0.0", f"version is {front['version']!r}, expected the string 1.0.0"
    assert front["metadata"] == {"version": "1.0.0"}, f"metadata is {front['metadata']!r}, expected only version 1.0.0"
    assert str(front["output"]).strip().lower() == "none", f"output is {front['output']!r}: a domain skill's output is none"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_description_is_third_person_and_says_what_and_when(skill):
    description = _front(skill).get("description")
    assert isinstance(description, str) and description.strip(), "no description"
    words = re.findall(r"[A-Za-z']+", description)
    assert not {w.lower() for w in words} & PERSON_WORDS, f"first or second person in the description: {description!r}"
    assert words[0].lower() not in COMMAND_VERBS, f"the description opens with a command verb: {description!r}"
    assert re.search(r"\b(when|use[sd]?|for)\b", description, re.I), f"the description does not say when to use it: {description!r}"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_sections_stand_in_the_templates_order_with_sources_last(skill):
    text = s.real_skill(skill)
    assert s.section_problems(text) == []
    body = s.split_frontmatter(text)[1]
    assert re.match(r"\s*# \S", body), "the body does not open with a level-1 title"
    intro = body.split("\n## ", 1)[0].split("\n", 1)[1].strip()
    assert intro, "no paragraph between the title and the first section"
    assert "<!--" not in text, "the template's HTML comment is still in SKILL.md"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_steps_are_a_checklist_the_handover_has_twelve_fields_and_escalation_has_four_ranks(skill):
    text = s.real_skill(skill)
    steps = s.section(text, "Steps")
    assert steps is not None and len(re.findall(r"(?m)^\s*[-*] \[[ xX]\]", steps)) >= 3, "Steps has fewer than three checklist items"
    out = s.section(text, "Output and handover")
    assert out is not None, "no Output and handover section"
    plain = " ".join(out.replace("`", "").split()).lower()
    assert all(f in plain for f in s.TWELVE) or "twelve fields" in plain, "Output and handover neither names nor counts the twelve fields"
    esc = s.section(text, "Escalation")
    assert esc is not None, "no Escalation section"
    missing = [rank for rank in ("P3", "P2", "P1", "Emergency") if not re.search(rf"\b{rank}\b", esc, re.I)]
    assert not missing, f"Escalation does not name {missing}"
    for name in ("Never", "Sources"):
        assert (s.section(text, name) or "").strip(), f"the {name} section is empty"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_body_is_about_150_lines(skill):
    count = len(_body(skill).rstrip("\n").splitlines())
    assert count <= s.BODY_LINES_AT_MOST, f"{skill}: the body is {count} lines (about 150, at most 165 here)"


def _reference_files(skill):
    folder = s.need(s.skill_dir(skill) / "SKILL.md").parent
    return folder, [f for f in s.skill_files(folder) if f.name not in s.OWN_FILES or len(f.parts) > 1]


@pytest.mark.parametrize("skill", s.SKILLS)
def test_every_reference_file_is_linked_from_skill_md_and_links_to_no_other(skill):
    folder, refs = _reference_files(skill)
    text = (folder / "SKILL.md").read_text(encoding="utf-8")
    unlinked = [str(r) for r in refs if r.name not in text and str(r) not in text]
    assert not unlinked, f"reference files SKILL.md does not link: {unlinked}"
    chained = {str(r): [o.name for o in refs if o != r and o.name in (folder / r).read_text(encoding="utf-8", errors="replace")]
               for r in refs}
    chained = {k: v for k, v in chained.items() if v}
    assert not chained, f"a reference file links to a further reference file: {chained}"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_skill_validator_exits_0_on_the_skill_md(tmp_path, skill):
    code, findings = s.validator(s.need(s.skill_dir(skill) / "SKILL.md"), tmp_path)
    assert code == 0 and findings == [], f"the validator exit {code}, findings {findings}"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_skill_validator_exits_0_on_the_folder_and_the_copies_it_reads(skill):
    """Run from the repository root, the validator also reads the generated copies that exist."""
    s.need(s.skill_dir(skill) / "SKILL.md")
    code, findings = s.validator(f"{s.KERNEL_REL}/{skill}", s.REPO_ROOT)
    assert code == 0 and findings == [], f"the validator exit {code}, findings {findings}"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_skill_passes_its_own_check(tmp_path, skill):
    code, output = s.run_check(skill, s.need(s.skill_dir(skill) / "SKILL.md"), cwd=tmp_path)
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"


# success-1: the five parts and the area's points --------------------------------------------------------------------

@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_five_labelled_parts_stand_in_the_body(skill):
    body = _body(skill)
    missing = [part for part in s.PARTS if not s.has_part(body, part)]
    assert not missing, f"{skill}: no heading or labelled line for {missing}"


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_areas_named_points_stand_in_the_body(skill):
    body = _body(skill)
    missing = [point for point in s.POINTS[skill] if not s.has_point(body, point)]
    assert not missing, f"{skill}: the named points not found: {missing}"


# success-2 (grep half) and failure-1: nothing grants a permission --------------------------------------------------

@pytest.mark.parametrize("skill", s.SKILLS)
def test_no_file_of_the_skill_holds_a_permission_granting_line(skill):
    folder = s.need(s.skill_dir(skill) / "SKILL.md").parent
    found = {str(p.relative_to(folder)): s.permission_lines(p.read_text(encoding="utf-8", errors="replace"))
             for p in s.plain_text_files(folder)}
    found = {k: v for k, v in found.items() if v}
    assert not found, f"permission-granting lines: {found}"


# failure-2 (the text half): the security skill routes no finding below P1 --------------------------------------------

def test_the_security_skill_states_the_p1_rule_and_routes_no_finding_below_p1():
    text = s.real_skill("security")
    assert s.has_point(s.split_frontmatter(text)[1], "any security finding is a P1"), "the P1 rule is not stated"
    assert s.finding_below_p1(text) == [], f"a line routes a finding to P2 or P3: {s.finding_below_p1(text)}"


# the validator on planted copies (planted, so green on the base) ----------------------------------------------------

@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_planted_good_copy_passes_the_validator(tmp_path, skill):
    """A control: the planted copies the next cases are built from are clean."""
    path = s.plant_file(tmp_path, s.build_skill(skill), folder=skill)
    code, findings = s.validator(path, tmp_path)
    assert code == 0 and findings == [], f"{skill}: the validator exit {code}, findings {findings}"


@pytest.mark.parametrize("skill", ["backend", "security"])
def test_the_validator_names_a_400_line_body_with_no_reference_files(tmp_path, skill):
    good = s.build_skill(skill)
    long_body = "\n".join(f"- Line {n}: the method says to make the change small and to check it before the commit."
                          for n in range(400))
    path = s.plant_file(tmp_path, good + "\n" + long_body + "\n", folder=skill)
    code, findings = s.validator(path, tmp_path)
    assert code == 1 and "SKILL_BODY_TOO_LONG" in [f["code"] for f in findings], f"{code}: {findings}"
    assert [p.name for p in path.parent.iterdir()] == ["SKILL.md"], "the planted copy has reference files"


@pytest.mark.parametrize("key", ["allowed-tools", "permissions"])
def test_the_validator_refuses_a_permission_key_in_the_front_matter_naming_the_key(tmp_path, key):
    text = s.insert_line(s.build_skill("api"), f"{key}: [Read]", "front")
    path = s.plant_file(tmp_path, text, folder="api")
    code, findings = s.validator(path, tmp_path)
    assert code == 1 and key in [f.get("key") for f in findings], f"{code}: {findings}"
