"""Stage A5: no move before the verdict of a fresh Independent Auditor on the path map [CAP-44.c].

Success line 2 and failure line 2 ("A move runs without an A5 verdict"). No case launches a model: the verdict is
a record the case writes and commits as the Independent Auditor commits its report (``Role: independent-auditor``,
the kernel role's handoff format, DEC-182). What makes it a verdict the tool accepts is in the README ("The A5
verdict"). In every refusing case no file moves: each origin holds what the baseline holds.
"""

from __future__ import annotations

import pytest

import w1_41_support as support

ORIGINS = [item["path"] for item in support.moves_proposal()]
TARGETS = [item["target"] for item in support.moves_proposal()]


def _planned(adoption):
    """A0 to A4 with the three move batches; the baseline the moves would start from."""
    adoption.through("A4", support.moves_proposal())
    return support.tree(adoption.project)


def _assert_no_move(adoption, baseline):
    problems = support.moved_nothing(adoption.project, baseline, ORIGINS)
    assert not problems, f"a file moved without an accepted A5 verdict: {problems}"
    arrived = [rel for rel in TARGETS if (adoption.project / rel).exists() or rel in support.tree(adoption.project)]
    assert not arrived, f"a target exists without an accepted A5 verdict: {arrived}"


def _a5_and_a6_refuse(adoption, interface, baseline, *names, a5_extra=("--verdict", support.VERDICT_REL)):
    run = adoption.run("A5", *a5_extra)
    support.assert_refused(run, interface, *names)
    _assert_no_move(adoption, baseline)
    run = adoption.run("A6")
    support.assert_refused(run, interface)
    _assert_no_move(adoption, baseline)


def test_a6_without_any_verdict_moves_nothing(adoption, interface):
    baseline = _planned(adoption)
    run = adoption.run("A6")
    support.assert_refused(run, interface, any_of=("A5", "verdict"))
    _assert_no_move(adoption, baseline)


def test_a5_names_a_verdict_file_that_does_not_exist(adoption, interface):
    baseline = _planned(adoption)
    _a5_and_a6_refuse(adoption, interface, baseline, support.VERDICT_REL)


@pytest.mark.parametrize("verdict", ["fail", "inconclusive", "pass_with_findings"])
def test_a_verdict_that_is_not_a_pass_moves_nothing(adoption, interface, verdict):
    """Only ``pass`` is a pass (as DEC-490 settled for the probe record: any other value refuses)."""
    baseline = _planned(adoption)
    support.write_verdict(adoption.project, adoption.stages["A3"].record, verdict=verdict)
    baseline = support.tree(adoption.project)
    _a5_and_a6_refuse(adoption, interface, baseline, verdict)


@pytest.mark.parametrize("role", ["engineer", "orchestrator", None], ids=["engineer", "orchestrator", "no-role"])
def test_a_verdict_not_committed_by_the_independent_auditor_moves_nothing(adoption, interface, role):
    """The verdict's word for itself is not what makes it the auditor's: the commit that brought it carries
    ``Role: independent-auditor`` (DEC-454 held the same for the probe record)."""
    _planned(adoption)
    support.write_verdict(adoption.project, adoption.stages["A3"].record, role=role)
    baseline = support.tree(adoption.project)
    _a5_and_a6_refuse(adoption, interface, baseline, support.AUDITOR_ROLE)


def test_a_verdict_written_and_not_committed_moves_nothing(adoption, interface):
    _planned(adoption)
    baseline = support.tree(adoption.project)
    support.write(adoption.project, support.VERDICT_REL,
                  support.verdict_text(adoption.project, adoption.stages["A3"].record))
    _a5_and_a6_refuse(adoption, interface, baseline, support.VERDICT_REL)


def test_a_verdict_from_the_session_that_made_the_path_map_moves_nothing(adoption, interface):
    """A fresh session: the auditor's session is not the session that ran the stages (CAP-44.c "independent";
    the kernel role: "a fresh session that wrote none of the audited files")."""
    _planned(adoption)
    support.write_verdict(adoption.project, adoption.stages["A3"].record, session=support.ADOPTER_SESSION)
    baseline = support.tree(adoption.project)
    _a5_and_a6_refuse(adoption, interface, baseline, support.ADOPTER_SESSION)


def test_a_verdict_about_a_path_map_that_changed_afterwards_moves_nothing(adoption, interface):
    """The auditor passed one path map; A3 and A4 then ran again with another proposal. The verdict is about the
    old map (its content hash), so nothing moves."""
    _planned(adoption)
    support.write_verdict(adoption.project, adoption.stages["A3"].record)
    changed = support.moves_proposal() + [support.entry("README.md", "MOVE", "docs/README.md", batch=3)]
    adoption.ok("A3", *adoption.map_argument(changed))
    adoption.ok("A4")
    baseline = support.tree(adoption.project)
    _a5_and_a6_refuse(adoption, interface, baseline)
    assert (adoption.project / "README.md").is_file() and not (adoption.project / "docs/README.md").exists()


def test_a_path_map_that_changes_after_a5_passed_is_not_executed(adoption, interface):
    """A5 passed and left its record. Then the path map changed. A6 executes only the map the verdict is about."""
    adoption.through("A5", support.moves_proposal())
    changed = support.moves_proposal() + [support.entry("README.md", "MOVE", "docs/README.md", batch=3)]
    adoption.ok("A3", *adoption.map_argument(changed))
    adoption.ok("A4")
    baseline = support.tree(adoption.project)
    run = adoption.run("A6")
    support.assert_refused(run, interface)
    _assert_no_move(adoption, baseline)
    assert (adoption.project / "README.md").is_file() and not (adoption.project / "docs/README.md").exists()


def _broken_yaml(adoption):
    return "---\nid: AV-0001\nverdict: [pass\n  path_map: }\n---\n\nA verdict nobody can read.\n"


def _no_frontmatter(adoption):
    return "# Review of the path map\n\nverdict: pass\n"


def _no_hash(adoption):
    return support.verdict_text(adoption.project, adoption.stages["A3"].record, path_map_hash=None)


def _no_verdict_key(adoption):
    return support.verdict_text(adoption.project, adoption.stages["A3"].record, verdict=None)


@pytest.mark.parametrize("text", [_broken_yaml, _no_frontmatter, _no_hash, _no_verdict_key],
                         ids=["broken-yaml", "no-frontmatter", "no-path-map-hash", "no-verdict"])
def test_a_verdict_that_cannot_be_read_moves_nothing(adoption, interface, text):
    """DEC-449: a verdict that cannot be read, or that does not say which path map it is about or what it found,
    is not a pass."""
    _planned(adoption)
    support.write_verdict(adoption.project, adoption.stages["A3"].record, text=text(adoption))
    baseline = support.tree(adoption.project)
    _a5_and_a6_refuse(adoption, interface, baseline, support.VERDICT_REL)


def test_a_passing_verdict_of_the_independent_auditor_is_recorded_by_a5(adoption):
    """The accepted case: A5 leaves its evidence record, which names the verdict and the path map's hash. Nothing
    has moved yet: A5 reviews, A6 moves."""
    _planned(adoption)
    support.write_verdict(adoption.project, adoption.stages["A3"].record)
    baseline = support.tree(adoption.project)
    stage = adoption.ok("A5", "--verdict", support.VERDICT_REL)
    assert stage.front.get("verdict") == support.VERDICT_REL, \
        f"{stage.record}: the record does not name the verdict it accepted"
    assert stage.front.get("path_map_hash") == support.map_hash(adoption.project, adoption.stages["A3"].record), \
        f"{stage.record}: the record does not carry the hash of the path map the verdict is about"
    _assert_no_move(adoption, baseline)
