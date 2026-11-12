"""S1: one command runs one audit in this order and no other (Interface items 1, 2; S1's Verify: a planted sets root,
repository and stub launch: the call ledger shows the steps in that order for a set with revisions, and without the two
second-round steps for a clean set; the printed command lines hold no ``fixtures/``, ``runs/`` or ``indep-walls/``).

The order is read three ways: the ``STEP <name> <command line>`` lines the driver prints (item 2), the planted launch
script's own call ledger, and the file-access spy's ``subprocess.Popen`` lines of the driver's own process (what it really
started, whatever it printed). W2-170's and W2-171's subcommands run for real, fed by the fake ``gov`` and ``claude``.

Readings the Interface leaves open: the auditor's line carries ``--commit`` and ``--brief-sha256`` like the other launches
(the table names ``--set <A> --audit <A>`` as what the auditor adds) and carries no ``--round``; the second round is
decided by the first checker's counts (``out.revise + out.rejected > 0``, item 2a), whatever the notes say.
"""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

import pytest

import w2_172_checks as C
import w2_172_world as W
from w2_172_world import S171

SECOND_ROUND = ("writer-2", "checker-2")
LAUNCH_ORDER_REV = ["writer-1", "checker-1", "writer-2", "checker-2", "auditor"]


def test_s1_a_set_with_revisions_runs_the_twelve_steps_in_this_order(ran):
    world, run = ran("words")
    C.assert_ok(run)
    assert W.step_names(run) == W.STEPS, run.out
    assert [c["step"] for c in world.stub_calls()] == LAUNCH_ORDER_REV, world.stub_calls()
    assert C.spawned_steps(world) == W.STEPS, "what the driver really started, in order (file-access spy)"


def test_s1_a_clean_set_goes_straight_from_the_first_checker_to_the_measure(ran):
    world, run = ran("clean")
    C.assert_ok(run)
    expected = [s for s in W.STEPS if s not in SECOND_ROUND]
    assert W.step_names(run) == expected, run.out
    assert [c["step"] for c in world.stub_calls()] == ["writer-1", "checker-1", "auditor"], world.stub_calls()
    assert C.spawned_steps(world) == expected


def test_s1_every_launch_line_names_only_the_sets_root_the_brief_and_its_hash_at_the_audit_commit(ran):
    world, run = ran("words")
    C.assert_ok(run)
    launches = [(n, c) for n, c in W.step_lines(run) if n in LAUNCH_ORDER_REV]
    assert [n for n, _ in launches] == LAUNCH_ORDER_REV
    calls = world.stub_calls()
    for (name, line), call in zip(launches, calls):
        kind = "auditor" if name == "auditor" else name.split("-")[0]
        tokens, flags = C.launch_flags(line)
        assert tokens[0] == sys.executable, "<py> is sys.executable"
        assert Path(tokens[1]).resolve() == world.stub.resolve(), "the launch script of --launch"
        want = {"--sets-root", "--kind", "--brief", "--brief-sha256", "--commit", "--set",
                "--audit" if kind == "auditor" else "--round"}
        assert set(flags) == want, (name, sorted(flags))
        assert Path(flags["--sets-root"]).resolve() == world.sets.resolve()
        assert flags["--kind"] == kind
        assert flags["--brief"] == f"{W.BRIEF_DIR}/{kind}.md"
        assert flags["--brief-sha256"] == C.brief_hash_at(world, world.audit_commit, kind), \
            "the hash of `git show <audit commit>:<brief>`"
        working = W.sha((world.repo / W.BRIEF_DIR / f"{kind}.md").read_bytes())
        assert flags["--brief-sha256"] != working, "the working tree's brief differs: the commit's bytes are hashed"
        assert flags["--commit"] == world.audit_commit
        assert flags["--set"] == W.AUDIT
        if kind == "auditor":
            assert flags["--audit"] == W.AUDIT
        else:
            assert flags["--round"] == name.rsplit("-", 1)[1]
        assert tokens[2:] == call["argv"], "the printed line is the line the launch script was called with"


def test_s1_the_printed_command_lines_hold_no_folder_of_the_sets_root(ran):
    """Rewrite-Reason: the merge queue's clone path (21:19 ejection). The grep skips only the line's first word when it is
    exactly ``sys.executable`` (``<py>``, Interface item 2): ``W.forbidden_in_text`` removes that one token, so a word in
    any other token still fails, and an interpreter under ``gov-os-runs/`` does not."""
    world, run = ran("words")
    C.assert_ok(run)
    for path in (world.sets, world.repo, world.link, world.stub, world.gov, world.claude):
        assert not any(w in str(path) + "/" for w in W.FORBIDDEN), f"path hygiene: {path}"
    lines = W.step_lines(run)
    assert len(lines) == len(W.STEPS)
    for name, line in lines:
        assert W.forbidden_in_text(line) == [], (name, line)
        assert str(world.sets) + "/" not in line, (name, line)


def test_s1_the_auditor_runs_also_when_there_is_no_miss_with_an_empty_misses_file(ran):
    world, run = ran("clean")
    C.assert_ok(run)
    call = [c for c in world.stub_calls() if c["step"] == "auditor"]
    assert len(call) == 1
    assert call[0]["misses_exists"] is True and call[0]["misses_lines"] == 0, call[0]
    assert (world.run_dir / "misses.jsonl").read_text() == ""
    assert world.audits()[-1]["audit"] == W.AUDIT and world.audits()[-1]["commit"] == world.audit_commit, \
        "the auditor's delivery wrote the audits' log line the next audit starts from"
    assert W.step_names(run).index("auditor") > W.step_names(run).index("judge")


def test_s1_the_auditor_gets_the_judges_misses(ran):
    from w2_171_scenario import Expected
    world, run = ran("words")
    C.assert_ok(run)
    call = [c for c in world.stub_calls() if c["step"] == "auditor"][0]
    expected = Expected(S171.SCENARIOS["words"], world).misses()
    assert call["misses_lines"] == len(expected) > 0, call


def test_s1_the_children_are_kept_in_the_audits_folder_and_nothing_a_child_says_is_printed(ran):
    from launch_stub import NOISE, STDERR_WORD
    world, run = ran("words")
    C.assert_ok(run)
    for step in W.STEPS:
        for suffix in (".out", ".err"):
            assert (world.audit_dir / f"{step}{suffix}").is_file(), (step, suffix)
    for step in ("writer-1", "checker-1", "writer-2", "checker-2", "auditor"):
        counts = json.loads((world.audit_dir / f"{step}.counts.json").read_text())
        assert counts["kind"] == ("auditor" if step == "auditor" else step.split("-")[0]) and counts["code"] == 0
    assert NOISE in (world.audit_dir / "writer-1.out").read_text()
    assert STDERR_WORD in (world.audit_dir / "writer-1.err").read_text()
    assert NOISE not in run.out and NOISE not in run.err
    assert STDERR_WORD not in run.out and STDERR_WORD not in run.err


@pytest.mark.parametrize("revise,rejected,second_round", [(1, 0, True), (0, 1, True), (0, 0, False)])
def test_s1_the_second_round_runs_exactly_when_the_first_checkers_counts_say_revise_or_reject(
        make_world, revise, rejected, second_round):
    world = make_world()
    if second_round:  # stop at the writer's second round: it was reached
        world.plan_launch({"checker-1": [{"revise_n": revise, "rejected_n": rejected}], "writer-2": [{"exit": 10}]})
    else:  # counts of none, but notes that void the set: the cycle stops at `void`, never at a second round
        world.plan_launch({"checker-1": [{"reject": ["q01", "q02", "q03", "q04", "q05"], "revise_n": 0,
                                          "rejected_n": 0}]})
    run = world.go()
    assert run.code == 2, run
    if second_round:
        assert W.step_names(run) == ["writer-1", "preflight", "checker-1", "writer-2"], run.out
        assert "STOPPED writer-2 10" in run.lines
    else:
        assert W.step_names(run) == ["writer-1", "preflight", "checker-1", "void"], run.out
        assert not [c for c in world.stub_calls() if c["step"] in SECOND_ROUND]
