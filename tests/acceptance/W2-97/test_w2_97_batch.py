"""KPI 4 (DEC-959 item 1, DEC-979 item 3): a batch on one head gives one merged result and one run (the union of
its selections, no more); a red batch is searched by ticket: only the culprit is ejected and the rest advance on a
run of their own; a red no single ticket explains, or a ticket that cannot be isolated, ejects the whole batch (fail
closed). A ticket that does not merge cleanly is ejected and the rest go on."""

from __future__ import annotations

import w2_97_support as S


def test_a_batch_gives_one_merged_result_and_one_run_on_the_union(q):
    q.plant()
    t1 = q.ticket(901, {"app/c.txt": "ok\n", "tests/test_c.py": S.reads_ok("c")})
    t2 = q.ticket(902, {"app/d.txt": "ok\n", "tests/test_d.py": S.reads_ok("d")})
    h1 = q.code_moves_on()
    q.configure_select(targets={t1.name: ["tests/test_c.py"], t2.name: ["tests/test_d.py"]})
    q.submit(t1, t2)

    done = q.run()
    assert done.returncode == 0, S.said(done)
    head = q.head()
    first = q.parents(head)[0]
    assert q.parents(head) == [first, t2.commit] and q.parents(first) == [h1, t1.commit], \
        "the batch is not one merge commit per ticket, in approval order, on the old head"
    S.assert_landed_as(q, t1, first)
    S.assert_landed_as(q, t2, head)
    runs = q.runs()
    assert len(runs) == 1, f"a batch on one head was run {len(runs)} times, not once"
    assert runs[0]["head"] == head, "the batch's run was not on the merged result that landed"
    assert sorted(runs[0]["targets"]) == ["tests/test_c.py", "tests/test_d.py"], \
        f"the run is not the union of the batch's selections: {runs[0]['targets']}"
    assert q.names("records") == [head[:12]], f"not one record for one advance: {q.names('records')}"
    S.assert_main_unmoved(q)


def test_a_red_batch_ejects_only_its_culprit_and_lands_the_rest_tested(q):
    q.plant()
    good = q.ticket(901, {"app/c.txt": "ok\n", "tests/test_c.py": S.reads_ok("c")})
    culprit = q.ticket(902, {"app/a.txt": "broken\n"})  # turns tests/test_a.py red
    h1 = q.code_moves_on()
    q.submit(good, culprit)

    done = q.run()
    assert done.returncode == 3, f"a batch with one culprit: {S.said(done)}"
    S.assert_ejected(q, culprit, h1, test_name="test_a")
    head = q.head()
    assert q.parents(head) == [h1, good.commit], \
        f"the good ticket did not advance alone onto the old head: parents {q.parents(head)}"
    assert not q.is_ancestor(culprit.commit, head), "the causing ticket advanced"
    S.assert_landed_as(q, good, head)
    assert any(r["head"] == head for r in q.runs()), \
        "the rest of the batch, merged again without the culprit, landed without a run of its own"
    record = q.record(head)
    assert any(culprit.name in str(e) for e in record["ejected"]), f"the record does not name the culprit: {record}"
    S.assert_main_unmoved(q)


def test_a_red_no_single_ticket_explains_ejects_the_whole_batch(q):
    # Red while app/c.txt or app/d.txt exists: taking out any one ticket leaves it red.
    q.plant({"tests/test_pair.py": S.red_if_any("pair", ["app/c.txt", "app/d.txt"])})
    tickets = [q.ticket(901, {"app/e.txt": "ok\n"}), q.ticket(902, {"app/c.txt": "x\n"}),
               q.ticket(903, {"app/d.txt": "x\n"})]
    h1 = q.code_moves_on()
    q.submit(*tickets)

    done = q.run()
    assert done.returncode == 3, f"a red no single ticket explains: {S.said(done)}"
    assert q.head() == h1, "a batch with an unexplained red advanced"
    for t in tickets:
        S.assert_ejected(q, t, h1)
    assert q.names("landed") == [] and q.names("records") == [], "part of a fail-closed batch landed"
    S.assert_main_unmoved(q)


def test_a_ticket_bringing_another_ticket_s_commits_fails_the_batch_closed(q):
    q.plant()
    good = q.ticket(901, {"app/e.txt": "ok\n"})
    # W2-902's approved commit brings a commit of another ticket's (Task: DAEO-other), then its own red change.
    mixed = q.ticket(902, {"app/a.txt": "broken\n"}, before=[({"app/x.txt": "other\n"}, "DAEO-other")])
    h1 = q.code_moves_on()
    q.submit(good, mixed)

    done = q.run()
    assert done.returncode == 3, f"a red batch with a ticket that cannot be isolated: {S.said(done)}"
    assert q.head() == h1, "a batch with a ticket that cannot be isolated advanced"
    S.assert_ejected(q, good, h1)
    S.assert_ejected(q, mixed, h1)
    assert q.names("landed") == [] and q.names("records") == [], "part of a fail-closed batch landed"
    S.assert_main_unmoved(q)


def test_a_conflicting_ticket_is_ejected_and_the_rest_go_on(q):
    q.plant()
    good = q.ticket(901, {"app/e.txt": "ok\n"})
    clash = q.ticket(902, {"app/notes.txt": "ticket\n"})
    h1 = q.code_moves_on()  # changes app/notes.txt too: W2-902 does not merge cleanly
    q.submit(good, clash)

    done = q.run()
    assert done.returncode == 3, f"a batch with a conflicting ticket: {S.said(done)}"
    e = S.assert_ejected(q, clash, h1)
    assert "conflict" in str(e["reason"]).lower(), f"the ejection's reason is not the conflict: {e['reason']}"
    head = q.head()
    assert q.parents(head) == [h1, good.commit], f"the rest of the batch did not go on: parents {q.parents(head)}"
    S.assert_landed_as(q, good, head)
    assert any(r["head"] == head for r in q.runs()), "the rest of the batch landed without a run"
    S.assert_main_unmoved(q)
