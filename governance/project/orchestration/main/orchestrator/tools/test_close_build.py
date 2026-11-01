"""The close tool's red attribution (DEC-968): close_build.trace_node, the same code main() runs, with fake runners.
Run: python3 -m pytest -q tools/test_close_build.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import close_build as cb  # noqa: E402


def trace(seq):
    """seq: per round (exit with the change, exit without it)."""
    w = iter(a for a, _ in seq)
    wo = iter(b for _, b in seq)
    verdict, c = cb.trace_node(lambda: next(w), lambda: next(wo))
    return verdict, c["rounds"]


def test_a_new_failing_test_is_the_changes():  # absent without the change (exit 4)
    assert trace([(1, 4)] * 6) == ("owned", 0)


def test_a_collection_error_without_the_change_is_the_changes():
    assert trace([(1, 2)] * 6)[0] == "owned"


def test_absent_without_even_if_green_with_is_the_changes():  # fails closed
    assert trace([(0, 5)] * 6)[0] == "owned"


def test_red_with_green_without_is_the_changes_after_3():
    assert trace([(1, 0)] * 6) == ("owned", 3)


def test_a_collection_error_with_the_change_counts_red():
    assert trace([(2, 0)] * 6) == ("owned", 3)


def test_red_both_ways_is_not_the_changes_after_3():
    assert trace([(1, 1)] * 6) == ("unowned", 3)


def test_load_sensitive_mixed_is_not_the_changes():  # 2026-10-31's latency cases
    assert trace([(1, 0), (0, 0), (0, 1), (1, 1), (0, 0), (0, 1)])[0] == "unowned"


def test_much_worse_with_the_change_is_the_changes():
    assert trace([(1, 0), (1, 1), (1, 0), (1, 0), (1, 0), (1, 0)]) == ("owned", 6)


def test_intermittent_only_with_the_change_is_the_changes():
    assert trace([(1, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]) == ("owned", 6)


def test_green_with_the_change_every_round_is_flaky():
    assert trace([(0, 0)] * 6) == ("flaky", 6)


def test_slightly_worse_with_is_not_the_changes():
    assert trace([(1, 1), (1, 0), (0, 0), (1, 1), (0, 0), (0, 0)])[0] == "unowned"


# ---- DEC-979 item 3: the culprit of a batch's red, the rest closed on the same run ----------------------------------
import subprocess  # noqa: E402
import tempfile  # noqa: E402


def rcs(*codes):
    it = iter(codes)
    return lambda: next(it)


def test_green_without_in_three_rounds_explains():
    assert cb.explained_without(rcs(0, 0, 0)) == "yes"


def test_one_red_round_without_does_not_explain():
    assert cb.explained_without(rcs(0, 1, 0)) == "no"


def test_a_collection_error_or_crash_without_does_not_explain():  # the first review's fail-open case
    assert cb.explained_without(rcs(2)) == "no"
    assert cb.explained_without(rcs(-9)) == "no"


def test_red_alone_needs_a_real_failure_every_round():
    assert cb.red_alone(rcs(1, 1, 1)) is True
    assert cb.red_alone(rcs(1, 0, 1)) is False
    assert cb.red_alone(rcs(4, 4, 4)) is False


def culprits(reds, candidates, verdicts, skip=(), confirmed=()):
    """verdicts: {(red, candidate): "yes"|"absent"} (else "no"); confirmed: {(red, candidate)} red with it alone."""
    state = {}

    def prepare(c):
        state["c"] = c
        return c not in skip

    return cb.assign_culprits(reds, candidates, prepare, lambda r: verdicts.get((r, state["c"]), "no"),
                              lambda r, c: (r, c) in confirmed)


def test_one_culprit_explains_its_reds_and_the_rest_close():
    got, left, skipped = culprits(["r1", "r2"], ["A", "B", "C"], {("r1", "B"): "yes", ("r2", "B"): "yes"})
    assert got == {"r1": ["B"], "r2": ["B"]} and left == [] and skipped == []


def test_two_culprits_each_own_their_red():
    got, left, _ = culprits(["r1", "r2"], ["A", "B"], {("r1", "A"): "yes", ("r2", "B"): "yes"})
    assert got == {"r1": ["A"], "r2": ["B"]} and left == []


def test_a_red_either_ticket_alone_explains_sends_both_back():
    got, left, _ = culprits(["r1"], ["A", "B", "C"], {("r1", "A"): "yes", ("r1", "B"): "yes"})
    assert got == {"r1": ["A", "B"]} and left == []


def test_a_red_no_single_ticket_explains_is_unexplained():
    got, left, _ = culprits(["r1"], ["A", "B"], {})
    assert got == {} and left == ["r1"]


def test_a_skipped_candidate_is_reported_so_the_batch_is_refused():  # the second review's case 2
    got, left, skipped = culprits(["r1"], ["A", "B"], {("r1", "A"): "yes"}, skip={"B"})
    assert skipped == ["B"]


def test_a_test_a_ticket_added_is_its_own_only_if_red_with_it_alone():
    got, left, _ = culprits(["r1"], ["A", "B"], {("r1", "A"): "absent"}, confirmed={("r1", "A")})
    assert got == {"r1": ["A"]} and left == []


def test_a_test_a_ticket_added_that_another_breaks_is_not_blamed_on_it():  # the second review's case 1
    got, left, _ = culprits(["r1"], ["A", "B"], {("r1", "A"): "absent", ("r1", "B"): "yes"}, confirmed=set())
    assert got == {"r1": ["B"]} and left == []


def test_an_unproven_absent_test_with_no_other_cause_refuses():
    got, left, _ = culprits(["r1"], ["A", "B"], {("r1", "A"): "absent"}, confirmed=set())
    assert got == {} and left == ["r1"]


def test_every_candidate_is_tried():
    seen = []

    def prepare(c):
        seen.append(c)
        return True

    cb.assign_culprits(["r1"], ["A", "B", "C"], prepare, lambda r: "yes" if seen[-1] == "A" else "no",
                       lambda r, c: False)
    assert seen == ["A", "B", "C"]


def _repo():
    d = tempfile.mkdtemp()
    g = lambda *a: subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", *a],  # noqa: E731
                                  capture_output=True, text=True, check=True).stdout.strip()
    g("init", "-q", "-b", "main")
    g("commit", "-q", "--allow-empty", "-m", "base")
    return d, g


def test_a_merge_of_the_tickets_own_commits_is_isolable():
    d, g = _repo()
    g("checkout", "-q", "-b", "a")
    g("commit", "-q", "--allow-empty", "-m", "a1", "--trailer", "Task: T-A")
    g("checkout", "-q", "main")
    g("merge", "-q", "--no-ff", "a", "-m", "merge a")
    assert cb.merge_is_own(g, g("rev-parse", "HEAD"), "T-A") is True


def test_a_merge_that_brings_another_tickets_commits_is_not():  # the review's case 2: a stacked branch
    d, g = _repo()
    g("checkout", "-q", "-b", "b")
    g("commit", "-q", "--allow-empty", "-m", "b1", "--trailer", "Task: T-B")
    g("checkout", "-q", "-b", "a")
    g("commit", "-q", "--allow-empty", "-m", "a1", "--trailer", "Task: T-A")
    g("checkout", "-q", "main")
    g("merge", "-q", "--no-ff", "a", "-m", "merge a")
    assert cb.merge_is_own(g, g("rev-parse", "HEAD"), "T-A") is False


def test_failure_types_reads_pytest_short_summary():
    out = ("FAILED tests/a.py::test_x - AssertionError: 1 != 2\n"
           "ERROR tests/a.py::test_y - FileNotFoundError: [Errno 2] no file\n"
           "FAILED tests/b.py::test_z - subprocess.TimeoutExpired(cmd, 5)\n")
    assert cb.failure_types(out, "tests/a.py::test_x") == ["AssertionError"]
    assert cb.failure_types(out, "tests/a.py::test_y") == ["FileNotFoundError"]
    assert cb.failure_types(out, "tests/b.py::test_z") == ["subprocess.TimeoutExpired"]
    assert cb.failure_types(out, "tests/c.py::test_none") == []


def test_a_different_failure_type_differs():  # the review's case: same test id, another failure
    a = cb.failure_types("FAILED t.py::x - AssertionError: no", "t.py::x")
    b = cb.failure_types("FAILED t.py::x - KeyError: 'k'", "t.py::x")
    assert a != b
