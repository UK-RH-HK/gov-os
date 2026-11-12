"""S1 (eight families, each in a process of its own, all at once, within a bound), S2 (the lines) and F2 (a timed-out
family is a NOTICE "not measured", never ok).

Every case plants a git tree whose declarations (``template/governance/kernel/checks/<id>.yaml``) hold a stand-in
command (``checks/marker.py``), runs ``python3 -m gov.cli.main check --structural [--timeout <s>] --root <tree>`` in a
child process and judges the exit code, the standard output lines (L2, L5) and the records the stand-ins left.
"""

from __future__ import annotations

import json
import os
import re
import sys

import pytest

import w2_158_support as support
from w2_158_support import BOUND, FAMILIES, OUTPUT_ORDER, SLACK_S, assert_shape


# --- S1 ---------------------------------------------------------------------------------------------------------------

def test_s1_eight_families_each_in_a_process_of_its_own_all_at_once_one_line_each(tree):
    """Eight declarations (one per family, a marker each that sleeps 3 s then passes), plus a stray declaration of a
    check that is in no family: eight records with eight pids, each in its own session and process group; all eight
    started before any ended (they overlap), the whole run well under eight times 3 s; one line per family in L2's order
    reading ``<family>: ok``; the stray check never ran; the last line says all ran families are ok (S2)."""
    tree.declare_all("ok", delay=3)
    tree.declare("index-freshness", tree.marker_command("index-freshness"), family="index freshness")
    tree.commit()
    outcome = tree.structural(bound=30)
    lines = assert_shape(outcome, tree)
    expected = ["core-schema", "core-graph", "core-claims", "core-mutation", "core-authority", "core-pathmap",
                "audit-reproducibility", "skill-regression-a"]
    assert tree.started() == sorted(expected), f"started: {tree.started()}\n{outcome.text()}"
    assert not tree.ran("index-freshness"), "a declaration outside the eight families was run"
    for name in FAMILIES:
        assert lines[OUTPUT_ORDER.index(name)] == f"{name}: ok", lines
    records = [tree.record(name) for name in expected]
    ends = [tree.record(name, "end") for name in expected]
    assert all(ends), f"a check did not end on its own: {ends}"
    assert len({r["pid"] for r in records}) == 8, "the eight checks did not run in eight processes"
    assert all(r["pgid"] == r["pid"] and r["sid"] == r["pid"] for r in records), "each check is in a session of its own"
    assert max(r["start"] for r in records) < min(e["end"] for e in ends), (
        "the checks did not overlap in time: they were not all started at once")
    assert outcome.elapsed < 8 * 3 * 0.75, f"{outcome.elapsed:.1f} s: the checks ran in sequence, not all at once"
    assert lines[OUTPUT_ORDER.index("portability")] == "portability: skipped (no base given)"
    assert lines[OUTPUT_ORDER.index("links")] == "links: skipped (no base given)"


def test_s1_a_check_past_the_bound_is_killed_at_the_bound_with_what_it_started(tree):
    """``--timeout 2``: schema sleeps 120 s, graph starts a grandchild that sleeps 120 s and then sleeps itself, the
    rest pass at once. The run ends within bound + slack (not before the bound: the sleeper cannot end earlier on its
    own), and afterwards the sleeper, graph's process and its grandchild are all gone (the whole process group is
    killed); neither wrote an end record."""
    tree.declare_all("ok")
    tree.declare_family("schema", "sleep")
    tree.declare_family("graph", "grandchild")
    tree.commit()
    outcome = tree.structural(bound=BOUND)
    lines = assert_shape(outcome, tree, notices=("schema", "graph"))
    assert BOUND - 0.3 <= outcome.elapsed <= BOUND + SLACK_S, f"ran {outcome.elapsed:.1f} s for a bound of {BOUND} s"
    for name in ("core-schema", "core-graph"):
        record = tree.record(name)
        assert record is not None, f"{name} was never started\n{outcome.text()}"
        assert support.wait_gone(record["pid"]), f"{name} (pid {record['pid']}) is still running after the pass ended"
        assert tree.record(name, "end") is None, f"{name} ended on its own"
    grandchild = tree.record("core-graph", "grandchild")
    assert grandchild is not None, "the stand-in did not start its grandchild"
    assert support.wait_gone(grandchild["pid"]), f"the grandchild (pid {grandchild['pid']}) outlived the bound: only the child was killed"
    for name in ("claims", "mutation", "authority", "pathmap", "audit", "skills"):
        assert lines[OUTPUT_ORDER.index(name)] == f"{name}: ok", lines


def test_s1_timeout_changes_the_bound(tree):
    """A schema check that takes 2.5 s: ``--timeout 1`` leaves it not measured, ``--timeout 8`` lets it end and read ok."""
    tree.declare_family("schema", "ok", delay=2.5)
    tree.commit()
    short = tree.structural(bound=1)
    line = short.family("schema")
    assert line.startswith("schema: NOTICE") and "not measured" in line, f"{line!r}\n{short.text()}"
    assert short.elapsed < 1 + SLACK_S, f"{short.elapsed:.1f} s"
    assert tree.record("core-schema", "end") is None
    for stale in tree.marks.glob("*.json"):
        stale.unlink()
    long = tree.structural(bound=8)
    assert long.family("schema") == "schema: ok", long.text()
    assert tree.record("core-schema", "end") is not None


def test_s1_a_fraction_of_a_second_is_a_valid_bound(tree):
    """``--timeout 0.5`` is accepted (exit 0) and bounds a sleeping check: ended within 0.5 s + slack, not measured."""
    tree.declare_family("schema", "sleep")
    tree.commit()
    outcome = tree.structural(bound=0.5)
    line = outcome.family("schema")
    assert line.startswith("schema: NOTICE") and "not measured" in line, f"{line!r}\n{outcome.text()}"
    assert outcome.elapsed < 0.5 + SLACK_S, f"{outcome.elapsed:.1f} s"


def test_s1_a_check_runs_in_the_tree_with_the_environment_l4_states(tree):
    """L4: the command runs in the tree (working folder), with ``PYTHONPATH=<tree>/src`` (not the caller's) and
    ``PYTHONDONTWRITEBYTECODE=1`` (the caller set neither), without any ``GIT_*`` variable (the caller has one), with
    standard input at its end (the caller's stays open), in a process group of its own, and ``python3`` is the
    interpreter running ``gov``."""
    tree.declare_family("schema", "ok")
    tree.commit()
    outcome = tree.structural(env=tree.env(GIT_W2158_PROBE="from the caller"))
    assert outcome.family("schema") == "schema: ok", outcome.text()
    record = tree.record("core-schema")
    assert record is not None, outcome.text()
    assert record["cwd"] == os.path.realpath(tree.tree), record
    assert record["pythonpath"] == str(tree.tree / "src"), f"PYTHONPATH was {record['pythonpath']!r}"
    assert record["dontwritebytecode"] == "1", record
    assert record["git_vars"] == [], f"GIT_* variables reached the check: {record['git_vars']}"
    assert record["stdin_empty"] is True, "the check's standard input is not at its end (not /dev/null)"
    assert record["pgid"] == record["pid"] and record["sid"] == record["pid"], record
    assert os.path.realpath(record["executable"]) == os.path.realpath(sys.executable), (
        f"python3 ran as {record['executable']}, not the interpreter running gov ({sys.executable})")


def test_s1_a_first_word_other_than_python3_is_looked_up_on_path(tree):
    """L4: a declared command whose first word is a program on ``PATH`` runs as it is (a stand-in program first on PATH)."""
    tree.plant_tool("w2158-tool")
    tree.declare("core-graph", f"w2158-tool {tree.marks} core-graph ok", family="graph")
    tree.commit()
    outcome = tree.structural()
    assert outcome.family("graph") == "graph: ok", outcome.text()
    assert tree.ran("core-graph")


def test_s1_the_tree_is_the_working_directory_when_root_is_not_given(tree):
    """L1: without ``--root`` the tree is the working directory, as for every gov command."""
    tree.declare_family("schema", "ok")
    tree.commit()
    outcome = tree.gov("check", "--structural", "--timeout", str(BOUND), cwd=tree.tree)
    lines = assert_shape(outcome, tree)
    assert lines[0] == "schema: ok", lines
    assert tree.ran("core-schema")


# --- S2 ---------------------------------------------------------------------------------------------------------------

def test_s2_each_state_reads_as_stated(tree):
    """A passing, a finding, a failing-with-stderr, a timed-out, an undeclared, a not-applicable, a first-line and a
    partly failing (skills) family, in one run with ``--timeout 2``: each family's line as L2 and L5 state it, in L2's
    order; no portability or links line other than the two skips; the last line names the families with a NOTICE."""
    tree.declare_family("schema", "ok")
    tree.declare_family("graph", "find", messages=["graph finding one"])
    tree.declare_family("claims", "stderr")
    tree.declare_family("mutation", "sleep")
    # authority: no declaration
    tree.declare_family("pathmap", "na", messages=["no path map in this tree"])
    tree.declare_family("audit", "first")
    for decl_id in support.SKILL_IDS[:2]:
        tree.declare(decl_id, tree.marker_command(decl_id), family="skill regression")
    orchestration = support.SKILL_IDS[2]
    tree.declare(orchestration, tree.marker_command(orchestration, "findobj"), family="skill regression")
    tree.set_messages(orchestration, ["skill finding X"])
    tree.commit()
    outcome = tree.structural()
    lines = assert_shape(outcome, tree, notices=("graph", "claims", "mutation", "audit", "skills"))
    by = dict(zip(OUTPUT_ORDER, lines))
    assert by["schema"] == "schema: ok"
    assert by["graph"].startswith("graph: NOTICE ") and "graph finding one" in by["graph"], by["graph"]
    assert by["claims"].startswith("claims: NOTICE ") and "core-claims exit 7: stderr-first-line: it failed" in by["claims"], by["claims"]
    assert by["mutation"].startswith("mutation: NOTICE") and "not measured" in by["mutation"] and "core-mutation" in by["mutation"], by["mutation"]
    assert by["authority"] == "authority: skipped (no declaration)"
    assert by["pathmap"] == "pathmap: ok (not applicable: no path map in this tree)"
    assert by["audit"].startswith("audit: NOTICE ") and "audit-reproducibility exit 5: boom: something broke" in by["audit"], by["audit"]
    assert "second line must not be shown" not in outcome.out
    assert by["skills"].startswith("skills: NOTICE ") and "skill finding X" in by["skills"], by["skills"]
    assert by["portability"] == "portability: skipped (no base given)"
    assert by["links"] == "links: skipped (no base given)"
    assert not tree.ran("core-authority")
    assert all(tree.ran(name) for name in ("core-schema", "core-graph", "core-claims", "core-mutation", "core-pathmap",
                                           "audit-reproducibility", *support.SKILL_IDS))


def test_s2_more_than_three_findings_show_three_joined_with_a_bar_then_the_number_left(tree):
    """Five findings of a family (one message holds a line break): the NOTICE is one line, shows the first three joined by
    `` | `` in their order, then ``(+2 more)``; the fourth and fifth are not shown."""
    tree.declare_family("graph", "find", messages=["alpha finding", "beta\nfinding two", "gamma finding", "delta finding", "epsilon finding"])
    tree.commit()
    outcome = tree.structural()
    lines = assert_shape(outcome, tree, notices=("graph",))
    line = lines[OUTPUT_ORDER.index("graph")]
    assert line.startswith("graph: NOTICE "), line
    assert "alpha finding | beta" in line and "gamma finding" in line, line
    assert line.index("alpha finding") < line.index("beta") < line.index("gamma finding"), line
    assert "delta" not in line and "epsilon" not in line, line
    assert line.rstrip().endswith("(+2 more)"), line


def test_s2_a_very_long_finding_is_shortened_on_the_one_line(tree):
    """One finding of 3,000 characters: the line shows a shortened form of it (L2 "each shortened"), and the family still
    takes exactly one line. (The width is not fixed by the Interface: the case only needs far under 3,000.)"""
    tree.declare_family("graph", "find", messages=["x" * 3000])
    tree.commit()
    outcome = tree.structural()
    lines = assert_shape(outcome, tree, notices=("graph",))
    line = lines[OUTPUT_ORDER.index("graph")]
    assert line.startswith("graph: NOTICE ") and "x" * 20 in line, line
    assert "x" * 3000 not in line and len(line) < 1500, f"the finding is not shortened ({len(line)} characters)"


def test_s2_a_command_that_cannot_be_started_is_a_notice_naming_it(tree):
    """A declared command naming no program: that family reads NOTICE ``<id> could not run: ...``, the pass goes on
    (another family reads ok) and exits 0."""
    tree.declare("core-schema", "no-such-program-w2158 --flag", family="schema/invariants")
    tree.declare_family("graph", "ok")
    tree.commit()
    outcome = tree.structural()
    lines = assert_shape(outcome, tree, notices=("schema",))
    schema = lines[0]
    assert schema.startswith("schema: NOTICE ") and "core-schema could not run" in schema, schema
    assert lines[1] == "graph: ok", lines


def test_s2_skills_runs_every_declaration_whose_family_is_exactly_skill_regression(tree):
    """The skills family: every declaration with ``family: skill regression`` is run (the three of today and one more
    by another id), one with a family that merely contains or differs in case is not, and the line is ok only if all
    that ran are ok; a failing one makes it a NOTICE holding its finding."""
    tree.declare_family("skills")
    tree.declare("my-own-skill-check", tree.marker_command("my-own-skill-check"), family="skill regression")
    tree.declare("other-skill-thing", tree.marker_command("other-skill-thing"), family="skill regression extra")
    tree.declare("other-skill-case", tree.marker_command("other-skill-case"), family="Skill Regression")
    tree.commit()
    outcome = tree.structural()
    assert outcome.family("skills") == "skills: ok", outcome.text()
    assert tree.started() == sorted([*support.SKILL_IDS, "my-own-skill-check"]), f"started: {tree.started()}"
    for stale in tree.marks.glob("*.json"):
        stale.unlink()
    tree.declare("my-own-skill-check", tree.marker_command("my-own-skill-check", "find"), family="skill regression")
    tree.set_messages("my-own-skill-check", ["a skill problem"])
    tree.commit("one skill check now finds a problem")
    again = tree.structural()
    line = again.family("skills")
    assert line.startswith("skills: NOTICE ") and "a skill problem" in line, f"{line!r}\n{again.text()}"
    assert all(tree.ran(name) for name in (*support.SKILL_IDS, "my-own-skill-check")), tree.started()


def test_s2_json_changes_nothing_on_standard_output(tree):
    """``--json`` or not, the output is the plain lines (L2) and the exit code the pass's own (no envelope)."""
    tree.declare_all("ok")
    tree.commit()
    outcome = tree.gov("check", "--structural", "--timeout", str(BOUND), "--json", "--root", str(tree.tree))
    assert_shape(outcome, tree)
    with pytest.raises(ValueError):
        json.loads(outcome.out)


# --- F2 ---------------------------------------------------------------------------------------------------------------

def test_f2_a_timed_out_family_is_a_notice_never_ok_and_never_a_failure_exit(tree):
    """S1's sleeper as the schema check, the others pass: the schema line is NOTICE and holds "not measured", no schema
    line reads ok, the last line names schema and says a notice is not a refusal, and the exit code is 0."""
    tree.declare_all("ok")
    tree.declare_family("schema", "sleep")
    tree.commit()
    outcome = tree.structural()
    lines = assert_shape(outcome, tree, notices=("schema",))
    line = lines[0]
    assert line.startswith("schema: NOTICE") and "not measured" in line, line
    assert not any(l.startswith("schema: ok") for l in lines), lines
    assert outcome.code == 0


def test_f2_every_family_timing_out_together_ends_within_one_bound_and_exits_0(tree):
    """All eight checks sleep past the bound: all eight lines are NOTICE "not measured" (none ok), the run ends within one
    bound + slack (not eight bounds), exit 0."""
    tree.declare_all("sleep")
    tree.commit()
    outcome = tree.structural()
    lines = assert_shape(outcome, tree, notices=FAMILIES)
    for name in FAMILIES:
        line = lines[OUTPUT_ORDER.index(name)]
        assert line.startswith(f"{name}: NOTICE") and "not measured" in line, line
    assert outcome.elapsed < BOUND + SLACK_S, f"{outcome.elapsed:.1f} s: the checks were not bounded together"
