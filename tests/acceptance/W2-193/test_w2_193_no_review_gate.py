"""S7: ``gov close`` does not require a review record (EMERGENCY-2 3.6: no ticket gets a reviewer; audit 1).

A FULL ticket with no probe record under ``docs/probes/<ticket>/`` closes, in the scoped close and in the batch run
(``python3 -m gov.close.batch run <ticket> ...``, as W2-115's batch cases drive it), as a STANDARD ticket does: the
close record's ``review`` holds the verdict READY and no record (``record: null``). Where a probe record with a
committed reviewer verdict block exists, READY is still computed by code from the block: a block that fails a KPI
line with a finding in scope, ordinary and fails-open refuses ``FINDING_BLOCKS`` (the scoped close and the batch).
The malformed and not-the-reviewer's blocks keep refusing in ``tests/acceptance/W2-115/test_w2_115_verdict.py``
(unchanged).

Red on the base: a FULL ticket with no probe record is refused ``VERDICT_MALFORMED``, in the scoped close and the
batch. Two cases are green on the base by design, as guards: a blocking verdict block still refuses
``FINDING_BLOCKS`` (scoped close and batch).
"""

import w2_193_support as support

smart = support.smart
cs = support.close_support
PROBE_REL = f"docs/probes/{support.TICKET}/PR-{support.TICKET}.md"
REVIEWER_TRAILERS = ("Role: independent-auditor",)
BLOCKING = smart.verdict([("S1", "fail", [("F1", "in", "yes", "fails open")]), ("F1", "pass", [])])
BOLT = "src/gov/bolt/b.py"
B = "PROJ-b1b1"


def _full_ticket(ticket=support.TICKET, wbs=support.WBS, allowed=smart.TICKET_PATHS):
    return {cs.ticket_path(ticket): cs.ticket_text(ticket, wbs, profile="FULL", allowed_paths=allowed,
                                                   status="in_progress")}


def _scoped(tmp_path, sandbox, probe=None):
    """A FULL ticket's scoped close: its work, the reviewer's probe record with the verdict ``probe`` (none when
    ``probe`` is None), the checkpoint, the close."""
    made = support.project(tmp_path, files=_full_ticket(), nightly="green")
    probed = support.work(made)
    if probe is not None:
        made.write(PROBE_REL, smart.probe_text(support.TICKET, probe, probed))
        made._commit("the probe record", cs.REVIEWER, REVIEWER_TRAILERS)
    made.ready(sandbox)
    return made, support.close(made, sandbox)


def test_a_full_ticket_with_no_probe_record_closes_with_review_ready_and_no_record(tmp_path, sandbox):
    """S7: no ``docs/probes/<ticket>/``: ``gov close --json`` exits 0, the ticket closes and the record's ``review``
    is READY with ``record`` null (the key is present), and the output holds no ``VERDICT_MALFORMED``."""
    made, run = _scoped(tmp_path, sandbox)

    assert not (made.root / "docs" / "probes" / support.TICKET).exists(), "the planted project holds a probe record"
    assert run.returncode == 0, f"gov close did not exit 0\n{run.describe()}"
    assert "VERDICT_MALFORMED" not in run.stdout + run.stderr, f"the close names VERDICT_MALFORMED\n{run.describe()}"
    support.assert_closed(made, run)
    review = support.record(made).get("review")
    assert isinstance(review, dict) and review.get("verdict") == smart.READY, f"review: {review!r}"
    assert "record" in review and review["record"] is None, f"the review names a record: {review!r}"


def test_a_verdict_block_that_fails_a_kpi_line_still_refuses_finding_blocks(tmp_path, sandbox):
    """S7: the same FULL ticket with the reviewer's probe record whose committed verdict block fails S1 (a finding in
    scope, in ordinary work, that fails open): refused with FINDING_BLOCKS, the ticket stays open. Green on the base
    by design (a guard: READY stays computed by code where a review happened)."""
    made, run = _scoped(tmp_path, sandbox, probe=BLOCKING)

    smart.assert_refused(run, smart.FINDING_BLOCKS)
    assert made.ticket_status() == "in_progress", "the ticket closed on a blocking verdict"


# --------------------------------------------------------------------------
# The batch run
# --------------------------------------------------------------------------

def _batch_project(base, full_b=True):
    """The project of W2-115's batch cases for two candidates: A (the ticket, its widget) and B (a bolt); both FULL
    tickets (``full_b``) with no probe record."""
    told = base / "told"
    files = {**_full_ticket(),
             **smart.candidate_ticket(B, "W2-b1", ["src/gov/bolt/**"], told),
             "src/gov/bolt/__init__.py": "", BOLT: "# a bolt\n"}
    if full_b:
        files.update(_full_ticket(B, "W2-b1", ["src/gov/bolt/**"]))
    return smart.Smart(base / "project", told, files=files)


def test_a_batch_of_full_tickets_with_no_probe_record_lands_with_review_ready_and_no_record(tmp_path):
    """S7: two FULL candidates, neither with a probe record, nothing red: the batch run lands both (each merged into
    ``main`` and closed) and each close record's ``review`` is READY with ``record`` null."""
    sandbox = support.sandbox_at(tmp_path)
    project = _batch_project(tmp_path)
    commits = smart.plant_candidates(project, sandbox, [
        (support.TICKET, support.WBS, {support.WIDGET: "# the widget, CHANGED\n"}, None),
        (B, "W2-b1", {BOLT: "# a bolt, CHANGED\n"}, None)])
    run = smart.run_module(project, sandbox, smart.BATCH_MODULE, "run", support.TICKET, B)

    assert "VERDICT_MALFORMED" not in run.stdout + run.stderr, f"the batch names VERDICT_MALFORMED\n{run.describe()}"
    assert smart.envelope(run).get("ok") is True and run.returncode == 0, f"the batch did not pass\n{run.describe()}"
    for ticket in (support.TICKET, B):
        assert project.ticket_status(ticket) == "closed", f"{ticket} did not close\n{run.describe()}"
        assert smart.is_ancestor(project, commits[ticket]), f"{ticket}'s work is not on main"
        review = project.record(ticket).get("review")
        assert isinstance(review, dict) and review.get("verdict") == smart.READY, f"{ticket} review: {review!r}"
        assert "record" in review and review["record"] is None, f"{ticket}'s review names a record: {review!r}"


def test_a_batch_whose_full_candidate_has_a_blocking_verdict_block_is_refused_and_nothing_lands(tmp_path):
    """S7: A is FULL with the reviewer's probe record (committed on its branch) whose verdict block fails S1; B
    is FULL with none. The batch run is refused with FINDING_BLOCKS and nothing lands: ``main`` does not move and
    neither ticket closes. Green on the base by design (a guard, as the scoped close's)."""
    sandbox = support.sandbox_at(tmp_path)
    project = _batch_project(tmp_path)
    old_head = project.head()
    project.git("checkout", "-q", "-b", f"w2/{support.WBS}", old_head)
    probed = project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.write(PROBE_REL, smart.probe_text(support.TICKET, BLOCKING, probed))
    project._commit("the probe record", cs.REVIEWER, REVIEWER_TRAILERS)
    project.ready(sandbox)
    project.git("checkout", "-q", "main")
    smart.plant_candidates(project, sandbox, [(B, "W2-b1", {BOLT: "# a bolt, CHANGED\n"}, None)])
    run = smart.run_module(project, sandbox, smart.BATCH_MODULE, "run", support.TICKET, B)

    smart.assert_refused(run, smart.FINDING_BLOCKS)
    assert project.head() == old_head, f"main moved: something landed\n{run.describe()}"
    for ticket in (support.TICKET, B):
        assert project.ticket_status(ticket) != "closed", f"{ticket} closed"
