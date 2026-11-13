"""S1, F1 and F2 for ``gov launch``: the role's template passed as the appended system prompt, the refusal without it,
and no other change to the built arguments.

Each case runs ``gov.launch.launcher.launch`` (the launcher's public entry) in a child process with a temporary home
whose ``.local/bin/claude`` is a stand-in that records its arguments (README, "How they run"). No session starts.
"""

from __future__ import annotations

import os

import pytest

import w2_153_support as support
from w2_153_support import ALL_ROLES, FLAG, REFUSAL, LaunchBed

CALLER = ["-p", "--model", "claude-opus-5-5", "--output-format", "json"]


@pytest.fixture
def bed(tmp_path):
    return LaunchBed(tmp_path / "bed")


def _started(run: dict) -> list[str]:
    result = run["result"]
    assert "error" not in result, f"the launch was refused: {result['error']}\nstderr: {run['stderr']}"
    assert result.get("exit") == 0, f"the launch ended with {result}\nstderr: {run['stderr']}"
    assert len(run["calls"]) == 1, f"the stand-in CLI was called {len(run['calls'])} times, not once: {run['calls']}"
    return run["calls"][0]["argv"]


@pytest.mark.parametrize("role", ALL_ROLES)
def test_s1_the_launch_passes_the_role_s_template_after_the_caller_s_arguments(bed, role):
    argv = _started(bed.launch(role, CALLER))
    expected = bed.expected_path(role)
    assert os.path.isabs(expected)
    assert support.flag_values(argv) == [expected], (
        f"{role}: {FLAG} must name {expected} once; the arguments were {support.shown(argv)}")
    assert argv[-2:] == [FLAG, expected], f"{role}: the flag must come after the caller's arguments: {support.shown(argv)}"
    assert argv[-2 - len(CALLER):-2] == CALLER, f"{role}: the caller's arguments must stay as given: {support.shown(argv)}"


@pytest.mark.parametrize("role", ["engineer", "lead"])
def test_s1_with_no_caller_arguments_the_flag_is_still_passed_last(bed, role):
    argv = _started(bed.launch(role, []))
    assert argv[-2:] == [FLAG, bed.expected_path(role)], support.shown(argv)
    assert support.flag_values(argv) == [bed.expected_path(role)], support.shown(argv)


@pytest.mark.parametrize("role", ALL_ROLES)
def test_f1_a_missing_template_refuses_with_launch_no_template_naming_the_path_and_starts_no_session(bed, role):
    """The role's own copy is missing; the other seven are there, so none of them stands in for it."""
    bed.template(support.ROLE_TEMPLATE[role]).unlink()
    run = bed.launch(role, CALLER)
    error = run["result"].get("error")
    assert error is not None, (f"{role}: the launch was not refused: {run['result']}; the stand-in CLI was called "
                               f"{len(run['calls'])} time(s)")
    assert error["code"] == REFUSAL, f"{role}: refused with {error['code']}, not {REFUSAL}: {error['message']}"
    assert bed.expected_path(role) in error["message"], f"{role}: the refusal does not name the path: {error}"
    assert run["calls"] == [], f"{role}: a session was started ({len(run['calls'])} call(s))"


def test_f1_guard_a_copy_no_launch_uses_missing_refuses_nothing(bed):
    """brief.md and role-cto.md are copies no launch passes: without them a worker and a lead still start."""
    for stem in ("brief", "role-cto"):
        bed.template(stem).unlink()
    for role in ("engineer", "lead"):
        _started(bed.launch(role, CALLER))


@pytest.mark.parametrize("role", ALL_ROLES)
def test_f2_the_built_arguments_are_integrate_s_but_for_the_one_flag(bed, baseline_src, role):
    """The same fixture, the same caller's arguments, integrate's launcher at the baseline commit beside this tree's:
    with the one flag and its value taken out, the arguments are equal (the session's temp folder and the home are
    replaced by fixed words, as they differ from run to run)."""
    ours = bed.launch(role, CALLER)
    theirs = bed.launch(role, CALLER, src=baseline_src)
    _started(ours)
    _started(theirs)
    assert theirs["result"]["module"].startswith(str(baseline_src)), theirs["result"]
    assert ours["result"]["module"].startswith(str(support.SRC)), ours["result"]
    mine = support.without_flag(bed.normalised(ours["calls"][0]))
    base = bed.normalised(theirs["calls"][0])
    assert mine == base, f"{role}: the launch changed beyond the one flag\nthis tree: {mine}\nintegrate: {base}"


@pytest.mark.parametrize("role", ["engineer", "lead"])
def test_f2_guard_integrate_s_launcher_starts_on_the_same_fixture_without_the_flag(bed, baseline_src, role):
    """The baseline is what F2 compares against: integrate's launcher starts the stand-in on this fixture, and its
    arguments carry no template flag."""
    argv = _started(bed.launch(role, CALLER, src=baseline_src))
    assert support.flag_values(argv) == [] and argv[-len(CALLER):] == CALLER, support.shown(argv)
