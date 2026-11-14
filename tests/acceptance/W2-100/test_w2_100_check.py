"""W2-100, I1: the skill's own check ``check_domain_skill.py``, judged on planted SKILL.md files: success-1, failure-1,
failure-2 (the text half), failure-3 (the section half).

Each planted file is built by ``build_skill`` from the ticket's Interface (the skill's own text is never read here)
and judged by the real skill folder's ``check_domain_skill.py``, run as ``python3 <script> <SKILL.md>``. A good
planted copy of each area must print ``PASS`` (exit 0); each bad one must be refused with the line the Interface
fixes: ``REFUSED <skill>: missing <section|part|point>``, ``REFUSED <skill>: section order: ...``,
``REFUSED <skill>: permission line <n>: <text>`` and (security only) ``REFUSED security: finding below P1 line <n>:
<text>``.
"""
from __future__ import annotations

import pytest

import w2_100_support as s


def _run(tmp_path, skill, text, script_of=None):
    path = s.plant_file(tmp_path, text)
    code, output = s.run_check(script_of or skill, path, cwd=tmp_path)
    return code, output, path


def _assert_refused(code, output, expected_lines):
    assert code == 1, f"expected exit 1, got {code}: {output!r}"
    got = s.refused(output)
    for line in expected_lines:
        assert line in got, f"no line {line!r} in the refusals {got}"
    assert not s.passes(output), f"PASS printed beside a refusal: {output!r}"
    return got


# success-1: a good copy passes -------------------------------------------------------------------------------------

@pytest.mark.parametrize("skill", s.SKILLS)
def test_a_good_planted_copy_passes_its_own_check(tmp_path, skill):
    code, output, _ = _run(tmp_path, skill, s.build_skill(skill))
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"


@pytest.mark.parametrize("skill, style", [("backend", "heading"), ("api", "bold-colon-outside"), ("data", "heading"),
                                          ("security", "bold-colon-outside"), ("backend", "bold-colon-outside")])
def test_a_part_may_stand_as_a_heading_or_as_a_labelled_line(tmp_path, skill, style):
    code, output, _ = _run(tmp_path, skill, s.build_skill(skill, part_style=style))
    assert code == 0 and s.passes(output) and not s.refused(output), f"{style}: exit {code}: {output!r}"


def test_a_part_label_is_matched_without_regard_to_case(tmp_path):
    text = s.build_skill("api").replace("**Common mistakes:**", "**common MISTAKES:**")
    assert "common MISTAKES" in text
    code, output, _ = _run(tmp_path, "api", text)
    assert code == 0 and s.passes(output), f"exit {code}: {output!r}"


def test_the_area_comes_from_the_files_name_not_from_the_folder_the_script_sits_in(tmp_path):
    """The script of the security folder judges a planted ``data`` copy by data's points, not security's."""
    code, output, _ = _run(tmp_path, "data", s.build_skill("data"), script_of="security")
    assert code == 0 and s.passes(output), f"exit {code}: {output!r}"
    bad = s.build_skill("data", omit_point="rollback")
    code, output, _ = _run(tmp_path, "data", bad, script_of="security")
    _assert_refused(code, output, ["REFUSED data: missing rollback"])


# success-1 and failure-3: a missing section ------------------------------------------------------------------------

SECTION_CASES = [("backend", "When / not when"), ("api", "Inputs"), ("data", "Steps"), ("security", "Done when"),
                 ("backend", "Output and handover"), ("api", "Escalation"), ("data", "Never"), ("security", "Sources"),
                 ("backend", "Never"), ("api", "Never"), ("security", "Never")]


@pytest.mark.parametrize("skill, name", SECTION_CASES)
def test_a_copy_missing_a_section_is_refused_naming_it_and_nothing_else(tmp_path, skill, name):
    code, output, _ = _run(tmp_path, skill, s.build_skill(skill, omit_section=name))
    got = _assert_refused(code, output, [f"REFUSED {skill}: missing {name}"])
    assert got == [f"REFUSED {skill}: missing {name}"], f"more than the missing section is named: {got}"


@pytest.mark.parametrize("skill", ["backend", "security"])
def test_a_section_out_of_the_templates_order_is_refused(tmp_path, skill):
    order = ["When / not when", "Inputs", "Steps", "Never", "Done when", "Output and handover", "Escalation", "Sources"]
    code, output, _ = _run(tmp_path, skill, s.build_skill(skill, order=order))
    got = _assert_refused(code, output, [])
    assert any(line.startswith(f"REFUSED {skill}: section order: ") for line in got), f"no section order line: {got}"
    assert not any(": missing " in line for line in got), f"a section is called missing: {got}"


@pytest.mark.parametrize("skill", ["api", "data"])
def test_a_level_2_heading_after_sources_is_refused(tmp_path, skill):
    text = s.build_skill(skill, after_sources="## Appendix\n\nExtra notes.")
    code, output, _ = _run(tmp_path, skill, text)
    got = _assert_refused(code, output, [])
    assert any(line.startswith(f"REFUSED {skill}: section order: ") for line in got), f"no section order line: {got}"


def test_a_heading_between_the_sections_is_no_refusal(tmp_path):
    """The area guide is itself an extra level-2 heading between the template's sections; so is this one."""
    text = s.build_skill("backend").replace("## Done when", "## Notes\n\nA short note.\n\n## Done when")
    code, output, _ = _run(tmp_path, "backend", text)
    assert code == 0 and s.passes(output), f"exit {code}: {output!r}"


# success-1: a missing labelled part --------------------------------------------------------------------------------

PART_CASES = [("backend", "Conventions"), ("api", "Pre-commit checklist"), ("data", "Unit-test focus"),
              ("security", "Common mistakes"), ("backend", "When to escalate"), ("security", "Conventions"),
              ("api", "When to escalate"), ("data", "Common mistakes")]


@pytest.mark.parametrize("skill, part", PART_CASES)
def test_a_copy_missing_a_labelled_part_is_refused_naming_it(tmp_path, skill, part):
    code, output, _ = _run(tmp_path, skill, s.build_skill(skill, omit_part=part))
    got = _assert_refused(code, output, [f"REFUSED {skill}: missing {part}"])
    assert got == [f"REFUSED {skill}: missing {part}"], f"more than the missing part is named: {got}"


@pytest.mark.parametrize("style", ["label", "heading"])
def test_a_part_named_only_in_running_text_is_still_missing(tmp_path, style):
    text = s.build_skill("data", omit_part="Common mistakes", part_style=style,
                         body_extra="Common mistakes are listed elsewhere; see the common mistakes of the team.")
    code, output, _ = _run(tmp_path, "data", text)
    _assert_refused(code, output, ["REFUSED data: missing Common mistakes"])


def test_a_level_5_heading_is_no_part(tmp_path):
    text = s.build_skill("api", omit_part="Unit-test focus", body_extra="##### Unit-test focus")
    code, output, _ = _run(tmp_path, "api", text)
    _assert_refused(code, output, ["REFUSED api: missing Unit-test focus"])


# success-1: a missing named point ----------------------------------------------------------------------------------

POINT_CASES = [(skill, point) for skill, points in s.POINTS.items() for point in points]


@pytest.mark.parametrize("skill, point", POINT_CASES, ids=[f"{k}-{p}" for k, p in POINT_CASES])
def test_a_copy_missing_a_named_point_is_refused_naming_it(tmp_path, skill, point):
    code, output, _ = _run(tmp_path, skill, s.build_skill(skill, omit_point=point))
    got = _assert_refused(code, output, [f"REFUSED {skill}: missing {point}"])
    assert got == [f"REFUSED {skill}: missing {point}"], f"more than the missing point is named: {got}"


LOOSE = [("backend", "error handling", "ERROR  HANDLING"), ("backend", "error handling", "error\nhandling"),
         ("backend", "migration", "Migrations"), ("api", "contract-first", "Contract first"),
         ("api", "contract-first", "CONTRACT-FIRST"), ("data", "schema change", "schema changes"),
         ("security", "Prepare the Organization", "Prepare the Organisation"),
         ("security", "Prepare the Organization", "prepare THE organization"), ("security", "input check", "Input Checks")]


@pytest.mark.parametrize("skill, point, written", LOOSE, ids=[f"{k}-{w!r}" for k, _p, w in LOOSE])
def test_a_point_is_found_whatever_its_case_spacing_hyphen_or_ending(tmp_path, skill, point, written):
    text = s.build_skill(skill, point_text={point: written})
    code, output, _ = _run(tmp_path, skill, text)
    assert code == 0 and s.passes(output) and not s.refused(output), f"{written!r}: exit {code}: {output!r}"


@pytest.mark.parametrize("skill, point, written", [("backend", "idempotence", "idempotent"),
                                                   ("api", "contract-first", "contract based")])
def test_a_near_miss_is_not_the_point(tmp_path, skill, point, written):
    text = s.build_skill(skill, point_text={point: written})
    code, output, _ = _run(tmp_path, skill, text)
    _assert_refused(code, output, [f"REFUSED {skill}: missing {point}"])


# failure-1: a permission-granting line -----------------------------------------------------------------------------

PERMISSION_CASES = [("backend", "front", "allowed-tools: Bash, Read"), ("api", "front", "permissions: [write]"),
                    ("data", "body", "- allow: Bash(git push:*)"), ("security", "body", "**allowed_tools:** Write"),
                    ("backend", "body", "`allowedTools`: Edit"), ("api", "body", '- "permission": write anywhere'),
                    ("data", "front", "Allow: everything")]


@pytest.mark.parametrize("skill, where, line", PERMISSION_CASES, ids=[f"{k}-{w}-{l[:14]}" for k, w, l in PERMISSION_CASES])
def test_a_permission_granting_line_is_refused_naming_the_line_and_its_number(tmp_path, skill, where, line):
    text = s.insert_line(s.build_skill(skill), line, where)
    number = [n for n, text_line in enumerate(text.splitlines(), start=1) if text_line == line]
    assert len(number) == 1, "the planted line is not unique in the planted file"
    code, output, _ = _run(tmp_path, skill, text)
    got = _assert_refused(code, output, [f"REFUSED {skill}: permission line {number[0]}: {line.strip()}"])
    assert len(got) == 1, f"more than the permission line is named: {got}"


def test_every_permission_line_is_named_not_only_the_first(tmp_path):
    text = s.insert_line(s.insert_line(s.build_skill("backend"), "allowed-tools: Read", "front"),
                         "- permissions: write", "body")
    code, output, _ = _run(tmp_path, "backend", text)
    numbers = [n for n, l in s.permission_lines(text)]
    assert len(numbers) == 2
    _assert_refused(code, output, [f"REFUSED backend: permission line {n}: {l}" for n, l in s.permission_lines(text)])


@pytest.mark.parametrize("prose", ["- The skill grants no permission; allow rules and permissions belong to the guard.",
                                   "Permission to write is never given here.",
                                   "- Do not allow: anything the guard refuses.",
                                   "- Tools the role may use are named in its role file, never here (allowed-tools is the role's)."])
def test_prose_that_mentions_the_words_is_no_permission_line(tmp_path, prose):
    code, output, _ = _run(tmp_path, "backend", s.build_skill("backend", prose=prose))
    assert code == 0 and s.passes(output) and not s.refused(output), f"{prose!r}: exit {code}: {output!r}"


# failure-2 (the text half): a security finding below P1 ------------------------------------------------------------

FINDING_LINES = ["- A finding of low impact is a P2.", "- P3: a minor finding goes to the lead.",
                 "Findings of this kind are P3 unless the lead says otherwise."]


@pytest.mark.parametrize("line", FINDING_LINES, ids=["p2", "p3", "findings-plural"])
def test_a_security_copy_routing_a_finding_below_p1_is_refused_naming_the_line(tmp_path, line):
    text = s.insert_line(s.build_skill("security"), line, "body")
    number = [n for n, l in enumerate(text.splitlines(), start=1) if l == line]
    assert len(number) == 1
    code, output, _ = _run(tmp_path, "security", text)
    got = _assert_refused(code, output, [f"REFUSED security: finding below P1 line {number[0]}: {line.strip()}"])
    assert len(got) == 1, f"more than the finding line is named: {got}"


def test_the_good_security_copy_names_p3_and_p2_without_the_word_finding_and_states_the_p1_rule(tmp_path):
    text = s.build_skill("security")
    assert s.finding_below_p1(text) == [], "the planted good copy itself routes a finding below P1"
    assert "any security finding is a P1" in text
    code, output, _ = _run(tmp_path, "security", text)
    assert code == 0 and s.passes(output), f"exit {code}: {output!r}"


def test_the_finding_rule_is_for_the_security_skill_only(tmp_path):
    text = s.insert_line(s.build_skill("backend"), "- A finding of low impact is a P2.", "body")
    code, output, _ = _run(tmp_path, "backend", text)
    assert code == 0 and s.passes(output), f"exit {code}: {output!r}"


# every failure is reported, not only the first ----------------------------------------------------------------------

def test_every_failure_is_named_on_its_own_line(tmp_path):
    text = s.build_skill("security", omit_section="Never", omit_part="Common mistakes", omit_point="least privilege")
    text = s.insert_line(text, "allowed-tools: Bash", "front")
    text = s.insert_line(text, "- A finding is a P2 when small.", "body")
    n_perm = next(n for n, l in s.permission_lines(text))
    n_find = next(n for n, l in s.finding_below_p1(text))
    code, output, _ = _run(tmp_path, "security", text)
    _assert_refused(code, output, [
        "REFUSED security: missing Never", "REFUSED security: missing Common mistakes",
        "REFUSED security: missing least privilege", f"REFUSED security: permission line {n_perm}: allowed-tools: Bash",
        f"REFUSED security: finding below P1 line {n_find}: - A finding is a P2 when small."])
