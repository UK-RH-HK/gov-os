"""W2-190 S1, S3 and F1: A3 and a DELETE_FROM_ACTIVE_TREE of a file another tracked file names by its path.

The fixture (``w2_190_support.documents``): ``docs/plans/0003-storage-migration.md`` is named, by its repository-relative
path, in the text of ``docs/plans/0007-storage-migration.md`` ("This plan supersedes plan 0003 (`docs/plans/0003-...`)")
and of ``docs/specs/storage-overview.md``. It carries no front matter, so no record graph class makes it superseded.
"""

from __future__ import annotations

import w2_190_support as support
from w2_190_support import base

OLD, NEW, OVERVIEW = support.OLD_PLAN, support.NEW_PLAN, support.OVERVIEW


def entry(path, action, **more):
    return base.entry(path, action, **more)


# --- S1 ---------------------------------------------------------------------------------------------------------------

def test_s1_deleting_a_file_another_file_names_is_refused_with_delete_referenced_and_the_referencer(adoption):
    before = base.head(adoption.root)
    done = support.propose(adoption, [entry(OLD, support.DELETE, batch=1)])
    problem = support.problem_for(done, OLD)  # the proposal is refused as a whole, with a problem for this path
    assert support.REFERENCED_CODE in problem, f"the problem for {OLD} does not carry {support.REFERENCED_CODE}: {problem}"
    assert NEW in problem, f"the problem for {OLD} does not name its referencing file {NEW}: {problem}"
    support.assert_no_a3_record(adoption.root, before, done)


def test_s1_every_referencing_file_is_named_and_the_whole_proposal_is_refused(adoption):
    before = base.head(adoption.root)
    done = support.propose(adoption, [entry(OLD, support.DELETE, batch=1),
                                      entry(support.UNREFERENCED, support.DELETE, batch=2)])
    problems = support.problems_of(done)
    assert {item.get("path") for item in problems} == {OLD}, \
        f"one problem per refused path: expected only {OLD} among {problems}"
    problem = support.problem_for(done, OLD)
    assert support.REFERENCED_CODE in problem, problem
    assert NEW in problem and OVERVIEW in problem, f"both referencing files ({NEW}, {OVERVIEW}) are named: {problem}"
    support.assert_no_a3_record(adoption.root, before, done)  # the unreferenced delete beside it is not recorded either


# --- S3: guards (green on the code before the change, required to stay green) -----------------------------------------

def test_s3_retiring_the_referenced_file_is_accepted_and_recorded(adoption):
    done = support.propose(adoption, [entry(OLD, "RETIRE", kind="rule-file")])
    support.accepted(done)
    assert support.recorded(adoption.root, OLD)["action"] == "RETIRE"


def test_s3_keeping_the_referenced_file_is_accepted_and_recorded(adoption):
    done = support.propose(adoption, [entry(OLD, "KEEP")])
    support.accepted(done)
    assert support.recorded(adoption.root, OLD)["action"] == "KEEP"


def test_s3_deleting_an_unreferenced_unsuperseded_file_is_accepted_with_its_batch(adoption):
    done = support.propose(adoption, [entry(support.UNREFERENCED, support.DELETE, batch=3)])
    support.accepted(done)
    held = support.recorded(adoption.root, support.UNREFERENCED)
    assert held["action"] == support.DELETE and held["batch"] == 3, held


# --- F1 ---------------------------------------------------------------------------------------------------------------

def test_f1_after_the_refusal_a4_and_a6_refuse_for_want_of_the_a3_record_and_the_file_stays(adoption):
    before = base.head(adoption.root)
    refused = support.propose(adoption, [entry(OLD, support.DELETE, batch=1)])
    support.problems_of(refused)  # the case stops here on code that records the delete: A3 must be the refusal
    support.assert_no_a3_record(adoption.root, before, refused)
    for stage in ("A4", "A6"):
        done = adoption.run(stage)
        error = base.refusal(done)
        assert error.get("code") == "ADOPT_STAGE_MISSING", \
            f"{stage} should refuse for want of the A3 record (ADOPT_STAGE_MISSING), got {error.get('code')}\n{done.describe()}"
        assert "A3" in (error.get("message") or ""), f"{stage}'s refusal does not name A3\n{done.describe()}"
    assert base.head(adoption.root) == before, "a stage after the refusal committed something"
    assert OLD in base.git(adoption.root, "ls-tree", "-r", "--name-only", "HEAD").splitlines(), f"{OLD} left HEAD"
    assert (adoption.root / OLD).is_file(), f"{OLD} is gone from the working tree"
    assert base.commits_deleting(adoption.root, OLD) == [], f"a commit deletes {OLD}"
