"""W2-184, review round 2's F1 -- a test designer launched from the ticket's tests worktree sees the ticket's probe records.

KPI success-5 [DEC-1120 (3)] and failure-1 ("a promotion not applied"), as the owner decided round 2's F1:
P-W2-184-1 (a), DEC-1010. Interface 5.1a (amended after review round 2): the probe records are also read under each
worktree root that the ticket's launch records name: every file in the shared record folder with ``record: gov-launch``
and a ``ticket`` that is one of the ticket's names (the id given, its ``id``, its ``wbs_id``), any role, gives its
``root``. A named root that no longer exists (or is not a folder) is skipped. A record file there that cannot be read as
JSON refuses the launch naming it (as 6.1). The records found are one set by their root-relative path: a path present
under two roots counts once, the launch root's copy first, then the other roots in sorted order; 5.2's sorted path order
and its ``record`` path are over that set (root-relative). With no probe record under any root, the launch is as before.
Nothing that refuses today stops refusing. Interface 10.3 (R3, DEC-1180 (4), rv-f1 F3) revises the "launch root's copy
first": every root's copy of a path is read (identical bytes are one copy) and the path is one review, holding a
fail-open finding if any copy does and failed if any copy failed; section 5's two cases are revised to it.

The fixture is one repository with two real linked worktrees, the ticket's (branch ``w2/W2-f1aa``) and the tests'
(``w2/W2-f1aa-tests``), both from the main checkout's commit that holds the tickets, the role files and a
``criticality.yaml``; they share the main checkout's launch record folder. Probe records are committed on the branch the
case names. Every launch is ``gov launch`` run from the tree the case names. The test designer's C2 entry is Sonnet,
xhigh; promoted, Opus at xhigh.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pytest

import w2_184_support as s

b = s.b
ENG, TD, AUD = s.ENGINEER, s.TEST_DESIGNER, s.AUDITOR
TK = "DAEO-f1aa"
OTHER = "DAEO-f1ab"
WBS = f"W2-184-{TK}"  # the ticket's wbs_id, as w2_184_support.ticket writes it
TABLE = s.TABLES[TD]["C2"]
FAIL_OPEN, TWO_FAILED = "a fail-open finding", "two failed reviews"


@dataclass(frozen=True)
class Repo:
    sandbox: object
    project: Path  # the main checkout, on main
    ticket: Path   # the ticket's worktree
    tests: Path    # the tests' worktree

    def tree(self, name):
        """One more linked worktree of the repository, ``<home>/work/<name>`` on the branch ``w2/<name>``."""
        return s.add_worktree(self.project, self.sandbox.home / "work" / name, f"w2/{name}")


@pytest.fixture()
def make_repo(sandbox, project):
    def make(profile="STANDARD"):
        s.ticket(project, ENG, "C2", profile, tk=TK)
        s.ticket(project, ENG, "C2", "STANDARD", tk=OTHER)
        s.commit_all(project, "the fixture tickets")
        return Repo(sandbox, project, s.add_worktree(project, sandbox.home / "work" / "W2-f1aa", "w2/W2-f1aa"),
                    s.add_worktree(project, sandbox.home / "work" / "W2-f1aa-tests", "w2/W2-f1aa-tests"))

    return make


@pytest.fixture()
def repo(make_repo):
    return make_repo()


# Rewrite-Reason: DEC-1225: a promotion launched the test designer on Opus (a model after -- other than Opus refused,
# Opus accepted). R2: a promotion keeps its record and the table's effort and launches the table's model (the test
# designer's C2 entry: Sonnet); a model after -- other than it is refused, it is accepted; the model's source word is
# left open.
def _promoted(result, reason, record):
    return s.assert_session(result, TABLE[0], TABLE[1], criticality="C2", model_source=s.ANY,
                            effort_source="by criticality", promotion={"reason": reason, "record": record})


def _on_table(result):
    return s.assert_session(result, *TABLE, criticality="C2", model_source="by criticality",
                            effort_source="by criticality", promotion=None)


def _fail_open(tree, name, judgement="fail"):
    return s.plant_probe(tree, TK, name, judgement, verdict=s.verdict_block("other", "fails open"))


# --------------------------------------------------------------------------
# 1. The promotion reaches the tests worktree
# --------------------------------------------------------------------------

@pytest.mark.parametrize("profile", ["STANDARD", "FULL"])
def test_f1_a_fail_open_record_on_the_ticket_branch_promotes_the_test_designer_in_the_tests_worktree(
        make_repo, launch, profile):
    repo = make_repo(profile)
    s.plant_probe(repo.ticket, TK, "01-review.md", "pass")
    record = _fail_open(repo.ticket, "02-review.md")
    s.commit_all(repo.ticket, "the review records, on the ticket branch only")
    assert not (repo.tests / s.PROBES_REL).exists(), "the tests worktree holds probe records: the fixture is wrong"
    promotion = {"reason": FAIL_OPEN, "record": record}
    engineer = s.assert_session(launch(ENG, TK, cwd=repo.ticket), s.TABLES[ENG]["C2"][0],
                                s.TABLES[ENG]["C2"][1], criticality="C2", model_source=s.ANY,
                                effort_source="by criticality", promotion=promotion)
    assert engineer["root"] == os.path.realpath(repo.ticket), "the engineer's launch record does not name its worktree"
    _promoted(launch(TD, TK, cwd=repo.tests), FAIL_OPEN, record)
    _promoted(launch(TD, TK, "--model", TABLE[0], cwd=repo.tests), FAIL_OPEN, record)
    s.refused(launch(TD, TK, "--model", s.OPUS, cwd=repo.tests), s.OPUS, TABLE[0])


@pytest.mark.parametrize("profile", ["STANDARD", "FULL"])
def test_f1_two_failed_records_on_the_ticket_branch_promote_the_test_designer_in_the_tests_worktree(
        make_repo, launch, profile):
    repo = make_repo(profile)
    s.plant_probe(repo.ticket, TK, "01-review.md", "fail")
    record = s.plant_probe(repo.ticket, TK, "02-review.md", "fail")
    s.commit_all(repo.ticket, "two failed review records, on the ticket branch only")
    b.assert_launched(launch(ENG, TK, cwd=repo.ticket))
    _promoted(launch(TD, TK, cwd=repo.tests), TWO_FAILED, record)
    _promoted(launch(TD, TK, "--model", TABLE[0], cwd=repo.tests), TWO_FAILED, record)


@pytest.mark.parametrize("name,role", [("wbs_id", AUD), ("id", s.PRODUCT_SPEC)])
def test_f1_a_root_named_by_a_launch_record_of_any_role_under_a_name_of_the_ticket_is_read(
        repo, sandbox, launch, name, role):
    """Before any launch record names the ticket worktree it is not read; once one does (planted: another role, the
    ticket named by its ``wbs_id`` or its ``id``), the next launch from the tests worktree is promoted."""
    record = _fail_open(repo.ticket, "01-open.md")
    s.commit_all(repo.ticket, "a fail-open review record, on the ticket branch only")
    first = launch(TD, TK, cwd=repo.tests)
    _on_table(first)
    s.plant_launch_record(sandbox, first.record(), root=os.path.realpath(repo.ticket), role=role,
                          ticket={"wbs_id": WBS, "id": TK}[name])
    _promoted(launch(TD, TK, cwd=repo.tests), FAIL_OPEN, record)


# --------------------------------------------------------------------------
# 2. A named root that no longer exists is skipped
# --------------------------------------------------------------------------

@pytest.mark.parametrize("how", ["a-removed-worktree", "a-record-naming-a-missing-folder", "a-record-naming-a-file"])
def test_f1_a_named_root_that_no_longer_exists_is_skipped_and_the_other_roots_count(repo, sandbox, launch, how):
    record = _fail_open(repo.ticket, "01-open.md", "pass")
    s.commit_all(repo.ticket, "a fail-open review record, on the ticket branch only")
    engineer = launch(ENG, TK, cwd=repo.ticket)
    b.assert_launched(engineer)
    if how == "a-removed-worktree":
        review = repo.tree("W2-f1aa-review")
        b.assert_launched(launch(AUD, TK, cwd=review))
        s.remove_worktree(repo.project, review)
        assert not review.exists(), "the review worktree was not removed"
    elif how == "a-record-naming-a-missing-folder":
        s.plant_launch_record(sandbox, engineer.record(), root=str(sandbox.home / "work" / "W2-f1aa-gone"))
    else:
        path = b.write(sandbox.elsewhere / "W2-f1aa-not-a-folder", "a file, not a folder\n")
        s.plant_launch_record(sandbox, engineer.record(), root=str(path))
    _promoted(launch(TD, TK, cwd=repo.tests), FAIL_OPEN, record)


# --------------------------------------------------------------------------
# 3. No probe record of the ticket under any named root: as before
# --------------------------------------------------------------------------

@pytest.mark.parametrize("how", ["no-probe-folder", "only-another-ticket-s-probe-folder"])
def test_f1_with_no_probe_record_of_the_ticket_under_any_named_root_the_launch_is_as_before(repo, launch, how):
    if how == "only-another-ticket-s-probe-folder":
        s.plant_probe(repo.ticket, OTHER, "01-open.md", "fail", verdict=s.verdict_block("fails open"))
        s.plant_probe(repo.ticket, OTHER, "02-failed.md", "fail")
        s.commit_all(repo.ticket, "another ticket's review records")
    review = repo.tree("W2-f1aa-review")
    b.assert_launched(launch(ENG, TK, cwd=repo.ticket))
    b.assert_launched(launch(AUD, TK, cwd=review))
    for root in (repo.ticket, review, repo.tests, repo.project):
        assert not (root / s.PROBES_REL / TK).exists(), f"{root} holds the ticket's probe folder: the fixture is wrong"
    _on_table(launch(TD, TK, cwd=repo.tests))
    s.refused(launch(TD, TK, "--model", s.OPUS, cwd=repo.tests), s.OPUS, TABLE[0])


# --------------------------------------------------------------------------
# 4. Nothing that refuses today stops refusing
# --------------------------------------------------------------------------

UNREADABLE = {
    "a-front-matter-that-is-not-yaml": "---\ntype: probe\njudgement: [fail\n---\n\n# Probe\n",
    "a-verdict-block-that-is-not-json": "---\ntype: probe\njudgement: pass\n---\n\n```verdict\nnot json at all\n```\n",
}


@pytest.mark.parametrize("case", sorted(UNREADABLE))
def test_f1_an_unreadable_probe_record_only_under_another_named_root_refuses_naming_the_file(repo, launch, case):
    b.assert_launched(launch(ENG, TK, cwd=repo.ticket))
    s.plant_probe(repo.ticket, TK, "09-garbled.md", raw=UNREADABLE[case])
    s.commit_all(repo.ticket, "an unreadable review record, on the ticket branch only, after the engineer's launch")
    s.refused(launch(TD, TK, cwd=repo.tests), "09-garbled.md")


@pytest.mark.parametrize("probe", ["a-probe-record-under-the-ticket-worktree", "no-probe-record-anywhere"])
def test_f1_a_launch_record_that_is_not_json_refuses_a_launch_from_the_tests_worktree_naming_it(
        repo, sandbox, launch, probe):
    if probe == "a-probe-record-under-the-ticket-worktree":
        _fail_open(repo.ticket, "01-open.md")
        s.commit_all(repo.ticket, "a fail-open review record, on the ticket branch only")
    b.assert_launched(launch(ENG, TK, cwd=repo.ticket))
    b.write(sandbox.records / "garbled-record.json", "{ not json")
    s.refused(launch(TD, TK, cwd=repo.tests), "garbled-record.json")


def test_f1_a_launch_record_that_is_not_json_refuses_the_s4_setting_now_that_every_launch_reads_the_folder(
        project, sandbox, launch):
    """The setting of ``test_w2_184_s4_reviews.py::test_s4_a_launch_record_that_is_not_json_does_not_matter_where_nothing_is_counted``
    before td-5 (an auditor on a STANDARD ticket, launched in the main checkout, no probe record anywhere, a
    ``criticality.yaml``): 5.1a reads the record folder on this launch too, so the record that is not JSON refuses it,
    naming it. That S4 case now holds where nothing reads the folder: no ``criticality.yaml`` (interface 1.4)."""
    standard = s.ticket(project, ENG, "C2", "STANDARD", tk="DAEO-rv07")
    b.write(sandbox.records / "garbled-record.json", "{ not json")
    s.refused(launch(AUD, standard), "garbled-record.json")


# --------------------------------------------------------------------------
# 5. One set by root-relative path
# --------------------------------------------------------------------------

def test_f1_the_same_record_under_both_roots_counts_once(repo, launch):
    """The stop-gap (c) brings the ticket branch's record into the tests branch: one failed review in both trees is one
    failed review, not two. A second failed record on the ticket branch then promotes, naming it (the set's second
    failed record in sorted path order; counted twice, the first record would be named)."""
    s.plant_probe(repo.ticket, TK, "01-review.md", "fail")
    s.commit_all(repo.ticket, "the first review record")
    b.git(repo.tests, "merge", "-q", "--ff-only", "w2/W2-f1aa")
    assert (repo.tests / s.PROBES_REL / TK / "01-review.md").is_file(), "the record was not brought into the tests tree"
    b.assert_launched(launch(ENG, TK, cwd=repo.ticket))
    _on_table(launch(TD, TK, cwd=repo.tests))
    second = s.plant_probe(repo.ticket, TK, "02-review.md", "fail")
    s.commit_all(repo.ticket, "the second review record, on the ticket branch only")
    _promoted(launch(TD, TK, cwd=repo.tests), TWO_FAILED, second)


def test_f1_a_path_under_both_roots_is_promoted_by_the_other_root_s_copy_that_holds_a_fail_open_finding(repo, launch):
    """Revised to R3 (interface 10.3, DEC-1180 (4), rv-f1 F3; was ``..._is_read_from_the_launch_root_s_copy``, P-td5-2).
    ``01-review.md`` passes in the tests tree and holds a fail-open finding in the ticket tree: every root's copy is
    read and the path holds a fail-open finding if any copy does, which is checked first (5.2), so the promotion is
    ``a fail-open finding`` on ``01-review.md``, not the two failed records ``02`` and ``03``."""
    s.plant_probe(repo.tests, TK, "01-review.md", "pass")
    s.commit_all(repo.tests, "the tests branch's copy of the first review record")
    first = _fail_open(repo.ticket, "01-review.md")
    s.plant_probe(repo.ticket, TK, "02-review.md", "fail")
    s.plant_probe(repo.ticket, TK, "03-review.md", "fail")
    s.commit_all(repo.ticket, "the ticket branch's review records")
    b.assert_launched(launch(ENG, TK, cwd=repo.ticket))
    _promoted(launch(TD, TK, cwd=repo.tests), FAIL_OPEN, first)


def test_f1_a_path_under_two_other_roots_is_read_from_every_root(repo, launch):
    """Revised to R3 (interface 10.3, DEC-1180 (4), rv-f1 F3; was ``..._is_read_from_the_first_root_in_sorted_order``,
    P-td5-2). ``01-review.md`` fails in the first root and passes with a fail-open finding in the later one: both
    copies are read, so the path holds a fail-open finding (checked first): ``a fail-open finding`` on
    ``01-review.md``, not ``two failed reviews`` on ``02-review.md``."""
    first, last = repo.tree("W2-f1aa-a"), repo.tree("W2-f1aa-z")
    assert os.path.realpath(first) < os.path.realpath(last)
    for tree in (first, last):
        b.assert_launched(launch(ENG, TK, cwd=tree))
    record = s.plant_probe(first, TK, "01-review.md", "fail")
    s.commit_all(first, "the first review record")
    _fail_open(last, "01-review.md", "pass")
    s.plant_probe(last, TK, "02-review.md", "fail")
    s.commit_all(last, "another copy of the first review record and a second one")
    _promoted(launch(TD, TK, cwd=repo.tests), FAIL_OPEN, record)


# --------------------------------------------------------------------------
# 6. Only the roots this ticket's launch records name
# --------------------------------------------------------------------------

@pytest.mark.parametrize("where", ["another-ticket-s-worktree", "the-main-checkout"])
def test_f1_a_root_no_launch_record_of_this_ticket_names_is_not_read(repo, launch, where):
    """A tree named only by another ticket's launch record, or by none (the main checkout), holds a fail-open record in
    ``docs/probes/<this id>/``: it is not read; the promotion is the ticket worktree's two failed records."""
    b.assert_launched(launch(ENG, TK, cwd=repo.ticket))
    s.plant_probe(repo.ticket, TK, "01-review.md", "fail")
    second = s.plant_probe(repo.ticket, TK, "02-review.md", "fail")
    s.commit_all(repo.ticket, "two failed review records, on the ticket branch")
    if where == "another-ticket-s-worktree":
        foreign = repo.tree("W2-f1ab")
        b.assert_launched(launch(ENG, OTHER, cwd=foreign))
    else:
        foreign = repo.project
    _fail_open(foreign, "00-open.md")
    s.commit_all(foreign, "a fail-open record of this ticket in a tree it was never launched from")
    _promoted(launch(TD, TK, cwd=repo.tests), TWO_FAILED, second)
