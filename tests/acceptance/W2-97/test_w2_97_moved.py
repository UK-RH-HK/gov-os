"""KPI 6 (DEC-959 item 1): when the integration head moves while a candidate is under test, the candidate is merged
again onto the new head and tested again, never advanced onto a head it was not tested on."""

from __future__ import annotations

import w2_97_support as S


def test_a_head_moved_under_test_is_re_merged_and_re_tested(q):
    q.plant()
    t = q.ticket(901, {"app/e.txt": "ok\n"})
    h1 = q.code_moves_on()
    q.configure_tests(move={"repo": str(q.repo), "path": "app/late.txt", "text": "late\n",
                            "subject": "lands while the candidate is under test"})
    q.submit(t)

    done = q.run()
    assert done.returncode == 0, S.said(done)
    head = q.head()
    h2 = q.parents(head)[0]
    assert q.parents(h2) == [h1] and q.git("log", "-1", "--format=%s", h2) == \
        "lands while the candidate is under test", "the new head is not merged onto the head that moved in"
    assert q.parents(head) == [h2, t.commit], f"parents of the new head: {q.parents(head)}"

    runs = q.runs()
    assert len(runs) >= 2, f"the candidate was not tested again on the moved head: {len(runs)} run(s)"
    assert runs[0]["head"] != head and not q.is_ancestor(runs[0]["head"], head), \
        "the merge tested on the old head was advanced"
    assert runs[-1]["head"] == head, "the commit landed is not the commit tested on the moved head"
    S.assert_landed_as(q, t, head)
    assert q.record(head)["base"] == h2, "the record's base is not the moved head"
    assert (q.repo / "app/late.txt").is_file() and (q.repo / "app/e.txt").is_file(), \
        "the checked-out integration worktree does not hold both the moved head and the ticket"
    S.assert_main_unmoved(q)
