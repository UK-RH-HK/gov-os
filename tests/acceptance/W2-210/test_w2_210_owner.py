"""F2: an exception accepted by anyone but the owner is refused before anything is computed, and ADOPTED_HEALTHY with a
condition not met is impossible [CAP-44.h; DEC-741 answer F].

The exceptions file is committed by each role the ticket names (and by none, and by ``owner`` with another role),
and left modified or never committed: the command line refuses with ``ADOPT_EXCEPTIONS_NOT_OWNERS``, names the file
and the commit, and leaves the tree and the refs as they were. Impossible records built by hand are refused by
``check_record`` and MALFORMED to W2-81's judge.
"""

from __future__ import annotations

import json

import pytest

import w2_210_support as d1
import w2_81_judge as judge

support = d1.support

NOT_OWNERS = "ADOPT_EXCEPTIONS_NOT_OWNERS"
BY = {"engineer": ("engineer",), "independent-auditor": ("independent-auditor",), "orchestrator": ("orchestrator",),
      "no-role": (), "owner-and-engineer": ("owner", "engineer"), "engineer-and-owner": ("engineer", "owner"),
      "owner-and-auditor": ("owner", "independent-auditor")}


@pytest.mark.parametrize("by", sorted(BY))
def test_an_exceptions_file_not_committed_by_the_owner_alone_is_refused_and_nothing_is_written(adopted, by):
    """F2: the file's last commit carries Role engineer, independent-auditor, orchestrator, none, or ``owner``
    together with another: refused before anything is computed; the file and the commit named; no record; HEAD, the
    refs and the tree as before."""
    commit = d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7, d1.DOCTOR), *BY[by])
    outcome = d1.taken(d1.run_stage(adopted))
    error = d1.assert_refused(outcome, NOT_OWNERS)
    said = json.dumps(error)
    assert d1.EXCEPTIONS_REL in said and commit[:7] in said, f"the refusal names the file and the commit: {error}"
    d1.assert_nothing_written(outcome)


def test_a_file_the_owner_committed_and_another_role_changed_since_is_refused(adopted):
    """F2: the last commit that touched it decides: the owner's file, then edited by an engineer's commit."""
    d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7), "owner")
    commit = d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7, d1.DOCTOR), "engineer", subject="a tweak")
    outcome = d1.taken(d1.run_stage(adopted))
    error = d1.assert_refused(outcome, NOT_OWNERS)
    assert d1.EXCEPTIONS_REL in json.dumps(error) and commit[:7] in json.dumps(error)
    d1.assert_nothing_written(outcome)


def test_a_file_the_owner_committed_and_that_is_modified_and_not_committed_is_refused(adopted):
    """F2: committed by the owner alone, then edited in the working tree: the commit does not hold what is read."""
    d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7), "owner")
    d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7, d1.DOCTOR), commit_it=False)
    outcome = d1.taken(d1.run_stage(adopted))
    error = d1.assert_refused(outcome, NOT_OWNERS)
    assert d1.EXCEPTIONS_REL in json.dumps(error)
    d1.assert_nothing_written(outcome)


def test_a_file_never_committed_is_refused(adopted):
    """F2: an exceptions file no commit touched is no owner's decision."""
    d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7), commit_it=False)
    outcome = d1.taken(d1.run_stage(adopted))
    error = d1.assert_refused(outcome, NOT_OWNERS)
    assert d1.EXCEPTIONS_REL in json.dumps(error)
    d1.assert_nothing_written(outcome)


def test_an_exceptions_file_committed_by_the_owner_alone_is_read(adopted):
    """F2 (the other side): ``Role: owner`` alone, committed: not refused as not the owner's (the stage goes on to its
    verdict)."""
    d1.write_exceptions(adopted.project, d1.accept(d1.LITE_A7), "owner")
    outcome = d1.taken(d1.run_stage(adopted))
    done = d1.envelope(outcome)
    assert (done.get("error") or {}).get("code") != NOT_OWNERS, outcome.run.describe()


def _impossible(project, mutate):
    """The record of ``cli_plain``-like shape, hand-built: the stage's commit subject, its own digest recomputed (the
    rest of what a record has), the verdict a lie. Only what the verdict says against its conditions is wrong."""
    front, text = d1.record_at_head(project)
    d1.commit_record(project, d1.with_digest(d1.changed_record(text, mutate)))


def _healthy_over_not_met(front):
    front["verdict"] = "ADOPTED_HEALTHY"


def _exceptions_over_not_accepted(front):
    front["verdict"] = "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"


IMPOSSIBLE = {"adopted-healthy-over-a-condition-not-met": _healthy_over_not_met,
              "accepted-exceptions-over-a-condition-not-accepted": _exceptions_over_not_accepted}


@pytest.mark.parametrize("which", sorted(IMPOSSIBLE))
def test_an_impossible_record_is_refused_by_check_record_and_malformed_to_the_judge(cli_plain, copy_of, tmp_path, which):
    """F2: ADOPTED_HEALTHY over a condition not met, or ADOPTED_WITH_ACCEPTED_EXCEPTIONS over one not accepted
    (committed under the stage's subject, with its digest right): ``check_record`` refuses, naming the cause; the judge
    reads the record as MALFORMED, never as a verdict."""
    d1.taken(cli_plain)
    ad = copy_of(cli_plain, tmp_path)
    _impossible(ad.project, IMPOSSIBLE[which])
    from gov.cli.errors import GovError

    with pytest.raises(GovError) as refused:
        d1.check_record(ad.project)
    assert refused.value.code == "ADOPT_VERDICT_DISAGREES", (refused.value.code, refused.value.message)
    read = judge.read_record(ad.project, d1.VERDICT_REL, "VERDICT")
    assert read.state == "MALFORMED", (read.state, read.why)


def test_the_stage_commits_no_impossible_record(cli_plain, cli_owner):
    """F2: what the stage itself committed (the two sessions' records) reads as a verdict for both ``check_record``
    and the judge: never an ADOPTED_HEALTHY over a condition not met."""
    for outcome in (cli_plain, cli_owner):
        d1.taken(outcome)
        d1.check_record(outcome.project)
        read = judge.read_record(outcome.project, d1.VERDICT_REL, "VERDICT")
        assert read.state == "PRESENT", (read.state, read.why)
