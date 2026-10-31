"""KPI 3 (DEC-959 item 1, DEC-968): tests run no more than this. The run is skipped when the merged code is what the
lead tested (the same tree for the code paths, the governance records left out), with its recorded reason; any other
code difference gets one run (test_w2_97_entry.py's green case counts it). A step that cannot be done moves nothing
and ejects nothing (exit 4, the entries kept)."""

from __future__ import annotations

import json

import pytest

import w2_97_support as S


def test_code_identical_to_the_lead_s_is_skipped_with_its_reason(q):
    q.plant()
    t = q.ticket(901, {"app/e.txt": "ok\n"})
    # Only a governance record lands on the integration branch after the ticket was cut: the merged code is the lead's.
    h1 = q.integrate_commit({"governance/project/orchestration/notes.md": "a record\n"}, "a record commit")
    q.submit(t)

    done = q.run()
    assert done.returncode == 0, S.said(done)
    assert q.test_calls() == [], f"code identical to the lead's tested code was run again: {len(q.test_calls())} calls"
    head = q.head()
    assert q.parents(head) == [h1, t.commit], "the skipped batch did not advance to its merge commit"
    S.assert_landed_as(q, t, head)
    record = q.record(head)
    reason = json.dumps(record["skipped"])
    assert record["skipped"], "the run was skipped without its recorded reason"
    assert t.commit[:12] in reason, f"the skip's reason does not name the commit the lead tested: {reason}"
    assert "governance/" in reason, f"the skip's reason does not name the governance paths left out: {reason}"
    assert record["counts"] is None, f"a skipped run has counts: {record['counts']}"
    S.assert_main_unmoved(q)


CANNOT = {
    "selection-refused": dict(select={"refuse": True}),
    "run-did-not-complete": dict(tests={"incomplete": True}),
    "prepare-failed": dict(prepare="false"),
}


@pytest.mark.parametrize("case", sorted(CANNOT))
def test_a_step_that_cannot_be_done_moves_nothing_and_ejects_nothing(q, case):
    how = CANNOT[case]
    q.plant()
    t = q.ticket(901, {"app/e.txt": "ok\n"})
    h1 = q.code_moves_on()
    q.submit(t)
    if "select" in how:
        q.configure_select(**how["select"])
    if "tests" in how:
        q.configure_tests(**how["tests"])

    done = q.run(prepare=how.get("prepare", "true"))
    assert done.returncode == 4, f"{case}: {S.said(done)}"
    assert done.stderr.strip(), f"{case}: no reason on stderr"
    assert q.head() == h1, f"{case}: the integration branch moved"
    assert q.names("ejected") == [], f"{case}: a ticket was ejected for a step that could not be done"
    assert q.names("landed") == [] and q.names("records") == [], f"{case}: something landed"
    assert q.entry("approved", t.name) is not None, f"{case}: the approved entry was not kept"
    S.assert_main_unmoved(q)
