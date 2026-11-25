"""F1: a verdict record the stage did not produce is refused [CAP-44.h].

``gov.adopt.verdict.check_record(root)`` accepts the record the stage committed and refuses, naming the cause by its
code (README, "Interface"), a record that lacks ``produced_by``, whose digest does not match its body, that stands on
another A10 record than the one now committed, that was not committed by a commit whose subject is the stage's
touching that record alone, or whose verdict does not agree with its conditions. Each plant changes one thing: the
others are made right (the stage's subject, the digest recomputed where the plant is not the digest).
"""

from __future__ import annotations

import pytest

import w2_210_support as d1

support = d1.support

NOT_PRODUCED, STALE, NOT_THE_STAGES, DISAGREES = ("ADOPT_VERDICT_NOT_PRODUCED", "ADOPT_VERDICT_STALE",
                                                  "ADOPT_VERDICT_NOT_THE_STAGES", "ADOPT_VERDICT_DISAGREES")


def refused_with(project):
    """The code ``check_record`` refuses with; an assertion error where it accepts."""
    from gov.cli.errors import GovError

    try:
        d1.check_record(project)
    except GovError as exc:
        assert exc.code.startswith("ADOPT_"), exc.code
        assert exc.message, "a refusal names its cause"
        return exc.code
    raise AssertionError("check_record accepted the record")


def produced_project(cli_plain, copy_of, tmp_path):
    """A copy of the project with the record the stage produced, committed by the stage."""
    d1.taken(cli_plain)
    return copy_of(cli_plain, tmp_path).project


def edited(text, mutate):
    """``text`` with its frontmatter changed and the ``produced_by`` it had kept (now stale)."""
    front = support.frontmatter(text, d1.VERDICT_REL)
    mutate(front)
    return support.with_frontmatter(text, front)


def test_the_record_the_stage_produced_is_accepted(cli_plain, cli_owner):
    """F1: the produced record (the first run's, NOT_ADOPTED_HEALTHY, and the owner's re-run's) is accepted."""
    for outcome in (cli_plain, cli_owner):
        d1.taken(outcome)
        d1.check_record(outcome.project)


def test_a_copy_with_the_verdict_changed_is_refused_as_not_produced(cli_plain, copy_of, tmp_path):
    produced = produced_project(cli_plain, copy_of, tmp_path)
    _, text = d1.record_at_head(produced)
    d1.commit_record(produced, edited(text, lambda front: front.__setitem__("verdict", "ADOPTED_HEALTHY")))
    assert refused_with(produced) == NOT_PRODUCED


def test_a_copy_with_a_conditions_state_changed_is_refused_as_not_produced(cli_plain, copy_of, tmp_path):
    produced = produced_project(cli_plain, copy_of, tmp_path)
    _, text = d1.record_at_head(produced)
    d1.commit_record(produced, edited(text, lambda front: front["conditions"][0].__setitem__("state", "not met")))
    assert refused_with(produced) == NOT_PRODUCED


def test_a_copy_with_the_digest_removed_is_refused_as_not_produced(cli_plain, copy_of, tmp_path):
    produced = produced_project(cli_plain, copy_of, tmp_path)
    _, text = d1.record_at_head(produced)
    d1.commit_record(produced, d1.without_digest(text))
    assert refused_with(produced) == NOT_PRODUCED


def test_a_hand_written_record_is_refused_as_not_produced(cli_plain, copy_of, tmp_path):
    """F1: a record written by hand (no ``produced_by``) is no verdict, whatever its subject says."""
    produced = produced_project(cli_plain, copy_of, tmp_path)
    _, text = d1.record_at_head(produced)
    hand = d1.changed_record(text, lambda front: front.__setitem__("verdict", "NOT_ADOPTED_HEALTHY"))
    d1.commit_record(produced, hand)
    assert refused_with(produced) == NOT_PRODUCED


def test_a_record_committed_by_an_ordinary_commit_is_refused_as_not_the_stages(cli_plain, copy_of, tmp_path):
    """F1: the record's bytes are the stage's own; the commit that brought it is an ordinary one."""
    produced = produced_project(cli_plain, copy_of, tmp_path)
    support.git(produced, "commit", "-q", "--amend", "-m", "an ordinary commit")
    assert refused_with(produced) == NOT_THE_STAGES


def test_a_record_committed_with_other_files_is_refused_as_not_the_stages(cli_plain, copy_of, tmp_path):
    """F1: the commit has the stage's subject but touches more than the record."""
    produced = produced_project(cli_plain, copy_of, tmp_path)
    support.git(produced, "reset", "-q", "--soft", "HEAD~1")
    support.write(produced, "notes/beside-the-record.md", "written with it\n")
    support.git(produced, "add", "-A")
    support.git(produced, "commit", "-q", "-m", d1.STAGE_SUBJECT)
    assert refused_with(produced) == NOT_THE_STAGES


def test_a_record_written_before_an_a10_record_that_has_since_changed_is_refused_as_stale(cli_plain, copy_of, tmp_path):
    """F1: the verdict stands on the A10 record it saw; that record has changed since."""
    produced = produced_project(cli_plain, copy_of, tmp_path)
    d1.append_to(produced, d1.RECORD["A10"])
    assert refused_with(produced) == STALE


@pytest.mark.parametrize("state", ["not met", "accepted"])
def test_a_verdict_that_does_not_agree_with_its_conditions_is_refused(cli_plain, copy_of, tmp_path, state):
    """F1: the digest and the commit right, the verdict a lie: ADOPTED_HEALTHY over a condition ``not met``."""
    produced = produced_project(cli_plain, copy_of, tmp_path)
    _, text = d1.record_at_head(produced)

    def lie(front):
        front["verdict"] = "ADOPTED_HEALTHY"
        for item in front["conditions"]:
            item["state"] = "met"
        front["conditions"][-1]["state"] = state
        if state == "accepted":
            front["conditions"][-1]["owner_entry"] = "DEC-9001"
    d1.commit_record(produced, d1.with_digest(d1.changed_record(text, lie)))
    assert refused_with(produced) == DISAGREES  # ADOPTED_HEALTHY over an accepted one disagrees too


def test_the_stage_replacing_a_record_it_did_not_produce_refuses_and_writes_nothing(cli_plain, copy_of, tmp_path):
    """F1: "and the stage when it replaces a record": the earlier record's digest is stale (the stage's subject, so
    only the digest is wrong); the stage run again refuses with the cause and writes nothing."""
    d1.taken(cli_plain)
    ad = copy_of(cli_plain, tmp_path)
    _, text = d1.record_at_head(ad.project)
    d1.commit_record(ad.project, edited(text, lambda front: front.__setitem__("verdict", "ADOPTED_HEALTHY")))
    outcome = d1.taken(d1.run_stage(ad))
    d1.assert_refused(outcome, NOT_PRODUCED)
    d1.assert_nothing_written(outcome)
