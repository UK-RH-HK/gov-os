"""S2: the draft is a spec in the spec-writing form, with its open questions as packages."""

from __future__ import annotations

import re

import w2_36_support as support
from w2_36_support import opened, spec_text


def assert_package_form(package):
    question, options, recommendation = package
    assert question, package
    assert options is not None, f"no - Options: line: {package}"
    assert len(re.findall(r"\(cost:\s*[^)]*\S[^)]*\)", options)) >= 2, f"fewer than two options with a cost: {package}"
    assert recommendation, f"no - Recommendation: line: {package}"


def row_packages(text):
    """(packages, {package index: the required rows it names})."""
    part = support.sections(text).get("Open questions")
    assert part is not None, "spec.md has no ## Open questions"
    found = support.packages(part)
    assert found, f"no package under ## Open questions:\n{part}"
    for package in found:
        assert_package_form(package)
    return found, [support.rows_named(question) for question, _, _ in found]


def test_draft_has_the_nine_parts_in_order_then_verify_and_sources_read(discovered):
    opened(discovered)
    assert support.headings(spec_text(discovered)) == list(support.HEADINGS)


def test_draft_problem_holds_the_idea_verbatim(discovered):
    opened(discovered)
    problem = support.sections(spec_text(discovered)).get("Problem") or ""
    assert support.WORDS in problem, problem


def test_lite_draft_asks_one_package_per_mandatory_row_and_one_on_profile_and_types(discovered):
    opened(discovered)
    found, named = row_packages(spec_text(discovered))
    required = set(support.MANDATORY)
    per_row = [names & required for names in named]
    profile = [found[i] for i, names in enumerate(per_row) if not names]
    assert len(found) == len(required) + 1, f"{len(found)} packages: {[q for q, _, _ in found]}"
    assert set().union(*per_row) == required, f"rows without a package: {required - set().union(*per_row)}"
    assert len(profile) == 1 and re.search(r"profile", profile[0][0], re.I), \
        f"expected one package on the profile and capability types: {profile}"


def test_standard_draft_records_profile_and_type_and_asks_its_rows_with_no_profile_package(researched):
    assert researched.run.returncode == 0, researched.run.describe()
    proposal, text = researched.extra["proposal.md"], researched.extra["spec.md"]
    assert proposal is not None and text is not None, "the STANDARD run wrote no proposal.md or spec.md"
    front = support.front_matter(researched.project / support.CHANGE_REL / "proposal.md")
    assert front.get("profile") == "STANDARD"
    assert front.get("capability_types") == ["performance-capacity"]
    found, named = row_packages(text)
    required = set(support.MANDATORY) | set(support.STANDARD_EXTRA)
    per_row = [names & required for names in named]
    assert len(found) == len(required), f"{len(found)} packages: {[q for q, _, _ in found]}"
    assert all(per_row), f"a package names no required row (a profile package?): {found}"
    assert set().union(*per_row) == required, f"rows without a package: {required - set().union(*per_row)}"


def test_check_refuses_the_unfilled_draft_by_name_but_not_problem_or_open_questions(discovered, tmp_path, home):
    opened(discovered)
    project = support.copy_project(discovered.project, tmp_path)
    check = support.discover(project, "--check", support.CHANGE, home=home)
    assert check.returncode == 1, check.describe()
    lines = check.lines()
    for part in support.DRAFT_REFUSED:
        assert any(f"REFUSED {part}:" in line for line in lines), f"{part} is not refused:\n{check.describe()}"
    for part in support.DRAFT_NOT_REFUSED:
        assert not any(f"REFUSED {part}:" in line for line in lines), f"{part} is refused:\n{check.describe()}"
    assert "PASS" not in lines
