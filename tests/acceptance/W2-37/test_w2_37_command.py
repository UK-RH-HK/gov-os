"""The command itself: found by gov's command list; an unknown or malformed change is refused; a read command.

W2-M285: ``gov impact`` returns an impact assessment for a stated change. The failure lines of the brief: an unknown
or malformed stated change is refused with a clear error, not answered with an empty impact; ``gov impact`` writes
nothing outside its declared output.
"""

from __future__ import annotations

import re

import pytest

import w2_37_support as support


def test_gov_lists_an_impact_command(box):
    """``gov --help`` lists ``impact``, and ``gov impact --help`` names the options the README states."""
    listing = support.gov(box, "--help")
    assert re.search(r"^\s+impact\s", listing.stdout, re.MULTILINE), \
        f"`gov --help` lists no `impact` command\n{listing.describe()}"
    run = support.gov(box, support.COMMAND, "--help")
    assert run.returncode == 0, f"`gov impact --help` failed\n{run.describe()}"
    for option in ("--json", "--root", support.COMPARE, support.OUT):
        assert option in run.stdout, f"`gov impact --help` does not name {option}\n{run.describe()}"


def test_an_unknown_id_is_refused_not_answered_with_an_empty_impact(graph, box):
    run = support.impact(graph, "NOPE-0001", box)
    support.assert_refused(run, "NOPE-0001")


def test_a_known_id_beside_an_unknown_one_is_refused_and_the_unknown_one_named(graph, box):
    run = support.impact(graph, [support.CHANGED, "NOPE-0002"], box)
    support.assert_refused(run, "NOPE-0002")


@pytest.mark.parametrize("change", ["", "   ", "???"], ids=["empty", "blank", "no-id"])
def test_a_malformed_change_is_refused(graph, box, change):
    support.assert_refused(support.impact(graph, change, box))


def test_no_change_at_all_is_refused(built, graph, box):
    run = support.gov(box, support.COMMAND, "--json", "--root", str(graph))
    support.assert_refused(run)


def test_gov_impact_writes_nothing(repo, box):
    """A read command: the tree, the store, the records and git are as they were, after an assessment, a question
    and a refusal."""
    before = support.snapshot(repo)
    support.impact(repo, support.CHANGED, box)
    support.impact(repo, f"What's the impact of {support.CHANGED}?", box)
    support.impact(repo, "NOPE-0001", box)
    after = support.snapshot(repo)
    changed = sorted(k for k in set(before[0]) | set(after[0]) if before[0].get(k) != after[0].get(k))
    assert not changed, f"gov impact changed these paths: {changed}"
    assert before[1] == after[1], f"gov impact changed git's state:\nbefore {before[1]}\nafter {after[1]}"


def test_out_writes_the_named_file_and_nothing_else(repo, box):
    """The declared output is the one file ``--out`` names (reading R3)."""
    before = support.snapshot(repo)
    out = repo / "docs" / "changes" / "CITP-900.md"
    run = support.impact(repo, support.CHANGED, box, out=out)
    support.assessment(run)
    assert out.is_file(), f"--out wrote no file at {out}\n{run.describe()}"
    after = support.snapshot(repo)
    changed = sorted(k for k in set(before[0]) | set(after[0]) if before[0].get(k) != after[0].get(k))
    assert changed in (["docs/changes/", "docs/changes/CITP-900.md"], ["docs/changes/CITP-900.md"]), \
        f"gov impact --out changed more than the file it names: {changed}"
    for key in ("head", "refs", "stash"):
        assert before[1][key] == after[1][key], f"gov impact --out changed git's {key}"
