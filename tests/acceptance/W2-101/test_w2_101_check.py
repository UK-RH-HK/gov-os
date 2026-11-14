"""W2-101: each skill's own check, ``check_domain_skill.py`` (I1): success-1, failure-1, failure-2 (the section half).

Run as ``python3 <skill folder>/check_domain_skill.py <SKILL.md>``: ``REFUSED <skill>: missing <name>`` or
``REFUSED <skill>: permission line <n>: <text>`` (exit 1), else ``PASS`` (exit 0). The planted copies are made from the
real SKILL.md in ``tmp_path`` and keep its ``name`` (the area is chosen from the name, so a planted copy may sit in any
folder). The real files are never edited.
"""
from __future__ import annotations

import shutil

import pytest

import w2_101_support as s

SKILLS = pytest.mark.parametrize("skill", s.SKILLS)
PART_CASES = [(skill, part) for skill in s.SKILLS for part in s.PARTS]
POINT_CASES = [(skill, point) for skill in s.SKILLS for point in s.POINTS[skill]]
SECTION_CASES = [(skill, name, pattern) for skill in s.SKILLS for name, pattern in s.SECTION_PATTERNS]


# the real skills pass their own check ---------------------------------------------------------------------------------

@SKILLS
def test_the_real_skill_passes_its_own_check(skill, tmp_path):
    code, output = s.run_check(skill, s.skill_dir(skill) / "SKILL.md", cwd=tmp_path)
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"


def test_the_three_check_scripts_are_byte_equal():
    scripts = [s.check_script(skill).read_bytes() for skill in s.SKILLS]
    assert scripts[0] == scripts[1] == scripts[2], "the three check_domain_skill.py files are not byte-equal"


@SKILLS
def test_the_check_stands_alone_in_a_copied_folder_with_the_standard_library_only(skill, tmp_path):
    """Each folder is copied with its script: the script alone, run with no site packages and no PYTHONPATH, passes."""
    folder = tmp_path / "copied" / skill
    folder.mkdir(parents=True)
    shutil.copyfile(s.check_script(skill), folder / s.CHECK_NAME)
    shutil.copyfile(s.skill_dir(skill) / "SKILL.md", folder / "SKILL.md")
    code, output = s.run_check(skill, folder / "SKILL.md", cwd=tmp_path, script=folder / s.CHECK_NAME,
                               flags=("-I", "-S"))
    assert code == 0 and s.passes(output), f"exit {code}: {output!r}"


# success-1: the five parts and the area's points ------------------------------------------------------------------------

@pytest.mark.parametrize("skill,part", PART_CASES)
def test_a_copy_missing_one_of_the_five_parts_is_named(skill, part, tmp_path):
    text = s.read_skill(skill)
    assert s.has_line(text, s.part_line(part)), f"the real {skill} skill has no heading or labelled line for {part}"
    planted_text = s.remove_lines(text, s.part_line(part))
    assert not s.has_line(planted_text, s.part_line(part))
    code, output = s.run_check(skill, s.planted(tmp_path, planted_text), cwd=tmp_path)
    assert code == 1, f"expected exit 1 for a copy without {part}, got {code}: {output!r}"
    assert s.names_missing(output, skill, part), f"the refusal does not say 'missing {part}': {output!r}"
    assert not s.passes(output), f"PASS is printed beside a refusal: {output!r}"


@pytest.mark.parametrize("skill,point", POINT_CASES)
def test_a_copy_missing_one_of_the_areas_points_is_named(skill, point, tmp_path):
    text = s.read_skill(skill)
    assert s.has_line(text, s.labelled_line(point)), f"the real {skill} skill has no labelled line for {point}"
    planted_text = s.remove_lines(text, s.labelled_line(point))
    assert not s.has_line(planted_text, s.labelled_line(point))
    code, output = s.run_check(skill, s.planted(tmp_path, planted_text), cwd=tmp_path)
    assert code == 1, f"expected exit 1 for a copy without {point}, got {code}: {output!r}"
    assert s.names_missing(output, skill, point), f"the refusal does not say 'missing {point}': {output!r}"


@pytest.mark.parametrize("source,renamed", [("frontend", "ui-ux"), ("ui-ux", "devops"), ("devops", "frontend")])
def test_the_area_is_chosen_from_the_name_in_the_front_matter(source, renamed, tmp_path):
    """A skill's text under another area's name lacks that area's points: each is named, under the new name."""
    text = s.with_name(s.read_skill(source), renamed)
    wanted = [p for p in s.POINTS[renamed] if not s.has_line(text, s.labelled_line(p))]
    assert wanted, f"the {source} text already holds every point of {renamed}: the plant does not bite"
    code, output = s.run_check(source, s.planted(tmp_path, text, folder="anywhere"), cwd=tmp_path)
    assert code == 1, f"expected exit 1, got {code}: {output!r}"
    for point in wanted:
        assert s.names_missing(output, renamed, point), f"'missing {point}' is not said for {renamed}: {output!r}"
    assert not s.refused(output, source), f"the refusal uses the old name {source}: {output!r}"


# failure-2 (the section half): a section missing, out of order, or after Sources --------------------------------------

@pytest.mark.parametrize("skill,name,pattern", SECTION_CASES)
def test_a_copy_with_a_section_removed_is_refused_naming_the_section(skill, name, pattern, tmp_path):
    text = s.read_skill(skill)
    assert s.section_problems(text) == [], f"the real {skill} skill breaks the section structure"
    planted_text = s.remove_section(text, pattern)
    assert planted_text != text, f"the real {skill} skill has no '## {name}' heading to remove"
    code, output = s.run_check(skill, s.planted(tmp_path, planted_text), cwd=tmp_path)
    assert code == 1, f"expected exit 1 with {name} removed, got {code}: {output!r}"
    assert s.names_missing(output, skill, name), f"the refusal does not say 'missing {name}': {output!r}"
    assert not s.passes(output)


@pytest.mark.parametrize("skill", s.SKILLS)
def test_the_copy_with_the_never_section_removed_is_refused_naming_never(skill, tmp_path):
    """The ticket's own planted case for failure-2, with the exact words of the Interface's example."""
    planted_text = s.remove_section(s.read_skill(skill), r"never\b")
    code, output = s.run_check(skill, s.planted(tmp_path, planted_text), cwd=tmp_path)
    assert code == 1 and f"REFUSED {skill}: missing Never" in s.lines_of(output), f"{code}: {output!r}"


@pytest.mark.parametrize("skill", s.SKILLS)
@pytest.mark.parametrize("first,second,either", [
    (r"inputs?\b", r"steps\b", ("Inputs", "Steps")),
    (r"done when", r"output and handover", ("Done when", "Output and handover")),
    (r"never\b", r"sources\b", ("Never", "Sources")),
], ids=["inputs-steps", "done-output", "never-sources"])
def test_sections_out_of_order_are_refused_naming_one_of_the_two(skill, first, second, either, tmp_path):
    text = s.read_skill(skill)
    planted_text = s.swap_sections(text, first, second)
    assert planted_text != text
    code, output = s.run_check(skill, s.planted(tmp_path, planted_text), cwd=tmp_path)
    assert code == 1, f"expected exit 1 for sections out of order, got {code}: {output!r}"
    lines = s.refused(output, skill)
    assert any(name.lower() in line.lower() for line in lines for name in either), \
        f"no refusal names {either}: {output!r}"
    assert not s.passes(output)


@pytest.mark.parametrize("skill", s.SKILLS)
def test_a_heading_after_sources_is_refused(skill, tmp_path):
    text = s.read_skill(skill).rstrip("\n") + "\n\n## Appendix\n\nA late section.\n"
    code, output = s.run_check(skill, s.planted(tmp_path, text), cwd=tmp_path)
    assert code == 1, f"expected exit 1 with a section after Sources, got {code}: {output!r}"
    assert any(word in line.lower() for line in s.refused(output, skill) for word in ("sources", "appendix")), \
        f"no refusal names Sources or the late heading: {output!r}"


# failure-1: a permission-granting line ------------------------------------------------------------------------------------

FORMS = ["allowed-tools: Bash", "allowed_tools: [Read]", "permissions: all", "permission: write",
         "allow: Bash(git:*)", "deny: Read", "- allowed-tools: Bash", "`allowed-tools: Bash`", '"allow: Bash"',
         "ALLOWED-TOOLS: Bash", "  * Deny: Write"]


@SKILLS
@pytest.mark.parametrize("form", FORMS)
def test_a_permission_line_in_the_body_is_refused_naming_the_line(skill, form, tmp_path):
    text, number = s.insert_in_body(s.read_skill(skill), form)
    assert s.permission_lines(text) == [(number, form)], "the plant is not the one permission line"
    code, output = s.run_check(skill, s.planted(tmp_path, text), cwd=tmp_path)
    assert code == 1, f"expected exit 1 for the line {form!r}, got {code}: {output!r}"
    hits = [line for line in s.refused(output, skill) if f"permission line {number}:" in line]
    assert hits, f"no refusal says 'permission line {number}:' for {form!r}: {output!r}"
    key = form.strip(" -*`\"").split(":")[0].lower()
    assert key in hits[0].lower(), f"the refusal does not give the line's text ({form!r}): {hits[0]!r}"
    assert not s.passes(output)


@SKILLS
def test_a_permission_key_in_the_front_matter_is_refused_naming_its_line(skill, tmp_path):
    text = s.read_skill(skill)
    lines = text.split("\n")
    assert lines[0] == "---", "the real skill's front matter does not open on line 1"
    lines.insert(1, "allowed-tools: Bash")
    code, output = s.run_check(skill, s.planted(tmp_path, "\n".join(lines)), cwd=tmp_path)
    assert code == 1, f"expected exit 1, got {code}: {output!r}"
    assert any("permission line 2:" in line for line in s.refused(output, skill)), \
        f"no refusal says 'permission line 2:': {output!r}"


@SKILLS
@pytest.mark.parametrize("line", ["Never write allowed-tools: in a skill.", "Allowance: none of this grants anything.",
                                  "The allow list is the guard's, not this skill's."])
def test_a_line_that_only_mentions_a_permission_word_is_no_grant(skill, line, tmp_path):
    """Control: the rule is a line that *begins* with the key and a colon; a sentence that mentions one passes."""
    text, _ = s.insert_in_body(s.read_skill(skill), line)
    assert s.permission_lines(text) == [], "the plant is a permission line"
    code, output = s.run_check(skill, s.planted(tmp_path, text), cwd=tmp_path)
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"


@SKILLS
def test_two_defects_are_both_named_and_no_pass_stands_beside_them(skill, tmp_path):
    text = s.remove_section(s.read_skill(skill), r"never\b")
    text, number = s.insert_in_body(text, "allowed-tools: Bash")
    code, output = s.run_check(skill, s.planted(tmp_path, text), cwd=tmp_path)
    assert code == 1, f"{code}: {output!r}"
    assert s.names_missing(output, skill, "Never"), output
    assert any(f"permission line {number}:" in line for line in s.refused(output, skill)), output
    assert not s.passes(output), output
