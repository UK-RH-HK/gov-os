"""KPI 2 (DEC-959 item 1, DEC-953, DEC-968): on red the integration branch does not move; the ticket is ejected with
the failing tests' names and the run's log folder. A red that passes alone is a flaky candidate, named, deciding
nothing on its own; a red that is red without the batch too is not the batch's, named, and does not stop the advance;
a red test the ticket added (it cannot run without it) is the ticket's."""

from __future__ import annotations

import json

import w2_97_support as S


def test_red_ejects_the_ticket_and_the_head_stays(q):
    q.plant()
    t = q.ticket(901, {"app/a.txt": "broken\n"})  # turns tests/test_a.py red
    h1 = q.code_moves_on()
    q.submit(t)

    done = q.run()
    assert done.returncode == 3, f"a red ticket: {S.said(done)}"
    assert q.head() == h1, "the integration branch moved after a red"
    S.assert_ejected(q, t, h1, test_name="test_a")
    assert q.names("landed") == [], "a red ticket landed"
    assert q.names("records") == [], "a record was written with no advance"
    S.assert_main_unmoved(q)


def test_a_red_that_passes_alone_is_a_flaky_candidate(q):
    q.plant({"tests/test_flaky.py": S.red_once("flaky", q.tmp / "flaky-marker")})
    t = q.ticket(901, {"app/e.txt": "ok\n"})
    h1 = q.code_moves_on()
    q.submit(t)

    done = q.run()
    assert done.returncode == 0, f"a batch whose only red passes alone: {S.said(done)}"
    head = q.head()
    assert q.parents(head) == [h1, t.commit], "the batch did not advance as green"
    S.assert_landed_as(q, t, head)
    assert q.names("ejected") == [], "a flaky candidate ejected its ticket"
    record = q.record(head)
    assert any("test_flaky" in json.dumps(f) for f in record["flaky"]), \
        f"the flaky candidate is not named in the record: {record['flaky']}"
    assert "test_flaky" in done.stdout + done.stderr, "the flaky candidate is not named in the run's output"
    S.assert_main_unmoved(q)


def test_a_red_not_the_batch_s_does_not_stop_the_advance(q):
    q.plant({"tests/test_known_red.py": S.always_red("known_red")})
    t = q.ticket(901, {"app/e.txt": "ok\n"})
    h1 = q.code_moves_on()
    q.submit(t)

    done = q.run()
    assert done.returncode == 0, f"a batch whose only red is red without it too: {S.said(done)}"
    head = q.head()
    assert q.parents(head) == [h1, t.commit], "a red that is not the batch's stopped the advance"
    S.assert_landed_as(q, t, head)
    assert q.names("ejected") == [], "a red that is not the batch's ejected its ticket"
    record = q.record(head)
    assert any("test_known_red" in json.dumps(u) for u in record["unowned"]), \
        f"the red that is not the batch's is not named in the record: {record['unowned']}"
    # It was checked without the batch: on the head before the merges (the same tree, checked out or reverted to).
    h1_tree = q.rev(f"{h1}^{{tree}}")
    assert any(c["tree"] == h1_tree for c in q.test_calls()), "the red was never re-run without the batch"
    S.assert_main_unmoved(q)


def test_a_failing_test_the_ticket_added_is_the_ticket_s(q):
    q.plant()
    t = q.ticket(901, {"tests/test_added.py": S.always_red("added")})
    h1 = q.code_moves_on()
    q.submit(t)

    done = q.run()
    assert done.returncode == 3, f"a ticket whose own new test is red: {S.said(done)}"
    assert q.head() == h1, "a ticket whose own new test is red advanced"
    S.assert_ejected(q, t, h1, test_name="test_added")
    assert q.names("landed") == [], "a ticket whose own new test is red landed"
    S.assert_main_unmoved(q)
