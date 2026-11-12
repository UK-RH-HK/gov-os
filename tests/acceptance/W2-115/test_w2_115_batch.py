"""S6 and F3: a batch's culprit is found before anything lands, by building the merged result without each candidate.

The batch is ``python3 -m gov.close.batch run <ticket> [<ticket> ...] --root <project> --json`` (W2-68's command;
README, "Interface", the reading this suite takes). Each candidate is a ticket whose work waits on its own branch
``w2/<WBS>``, made from ``main``; landing is the candidate's work merged into ``main`` and its ticket closed.

- One culprit: A (the widget), B (a bolt) and C (the gadget, BROKEN, which W2-cc's test reads). The build without C
  is green; only C goes back; A and B land on the same run.
- Unexplained: A and B each break the same test (W2-bb's test reads both the widget and the gadget); no single
  candidate explains the red: ``BATCH_UNEXPLAINED``, nothing lands.
- Not isolated: A causes the red and B's branch is made from A's: the build without A cannot be made:
  ``CANDIDATE_NOT_ISOLATED``, nothing lands.

Red on today's code: today's batch takes tickets already merged and closes nothing on a red run; it lands no
candidate's branch and names no culprit, ``BATCH_UNEXPLAINED`` or ``CANDIDATE_NOT_ISOLATED``.
"""

import pytest

import w2_115_support as support

A, B, C = support.TICKET, "PROJ-b1b1", "PROJ-c1c1"
BOLT = "src/gov/bolt/b.py"
CC_GADGET = support.node_of("W2-cc", "cc_gadget", "test_cc_reads_the_gadget")
BB_BOTH = support.node_of("W2-bb", "bb_both", "test_bb_reads_both")
BB_WIDGET = support.node_of("W2-bb", "bb_widget", "test_bb_reads_the_widget")
BOTH_NOT_BROKEN = (f"    ok = 'BROKEN' not in (seen[{support.WIDGET!r}] or '') + (seen[{support.GADGET!r}] or '')\n"
                   "    _tell(ok)\n    assert ok, 'the widget or the gadget is broken'\n")


def _project(base, reds, bb_paths=None, test_map=support.DEFAULT_TEST_MAP):
    told = base / "told"
    files = {**support.candidate_ticket(B, "W2-b1", ["src/gov/bolt/**"], told),
             **support.candidate_ticket(C, "W2-c1", ["src/gov/gadget/**"], told),
             "src/gov/bolt/__init__.py": "", BOLT: "# a bolt\n"}
    if bb_paths:
        files[support.close_support.ticket_path("PROJ-bbbb")] = support.close_support.ticket_text(
            "PROJ-bbbb", "W2-bb", allowed_paths=bb_paths, status="closed")
    files.update({node.split("::")[0]: support.telling(node.split("::")[1], told, body)
                  for node, body in reds.items()})
    return support.Smart(base / "project", told, files=files, test_map=test_map)


class Batch:
    def __init__(self, base, reds, candidates, bb_paths=None, test_map=support.DEFAULT_TEST_MAP):
        self.sandbox = support.cli_support.make_sandbox(base / "sandbox")
        self.project = _project(base, reds, bb_paths, test_map)
        self.base = self.project.head()
        self.commits = support.plant_candidates(self.project, self.sandbox, candidates)
        self.run = support.run_module(self.project, self.sandbox, support.BATCH_MODULE, "run", A, B, C)

    def landed(self, ticket):
        return self.project.ticket_status(ticket) == "closed" and support.is_ancestor(self.project,
                                                                                      self.commits[ticket])

    def nothing_landed(self):
        assert self.project.head() == self.base, "main moved: something landed"
        for ticket in (A, B, C):
            assert not self.landed(ticket), f"{ticket} landed"
            assert self.project.ticket_status(ticket) != "closed", f"{ticket} closed"


@pytest.fixture(scope="module")
def culprit(tmp_path_factory):
    return Batch(tmp_path_factory.mktemp("w2_115_batch_culprit"), {CC_GADGET: support.GADGET_NOT_BROKEN}, [
        (A, "W2-aa", {support.WIDGET: "# the widget, CHANGED\n"}, None),
        (B, "W2-b1", {BOLT: "# a bolt, CHANGED\n"}, None),
        (C, "W2-c1", {support.GADGET: "# the gadget, BROKEN\n"}, None)])


def test_only_the_culprit_goes_back(culprit):
    """S6, F3: the culprit C is not closed and its work is not on ``main``; it alone goes back (A and B do not)."""
    assert culprit.project.ticket_status(C) != "closed", f"the culprit closed\n{culprit.run.describe()}"
    assert not support.is_ancestor(culprit.project, culprit.commits[C]), "the culprit's work landed on main"
    back = [t for t in (A, B) if not culprit.landed(t)]
    assert not back, f"candidates that are not the culprit went back too: {back}\n{culprit.run.describe()}"


def test_the_rest_land_on_the_same_run(culprit):
    """S6: A and B land (merged into ``main``, closed) and both close records name the same commit closed."""
    for ticket in (A, B):
        assert culprit.landed(ticket), f"{ticket} did not land\n{culprit.run.describe()}"
    commits = {culprit.project.record(t).get("commit") for t in (A, B)}
    assert len(commits) == 1 and None not in commits, f"A and B did not land on the same run: {commits}"


def test_the_build_without_the_culprit_is_green(culprit):
    """S6: the red test passed on a build holding A's work and not C's: the merged result without the culprit."""
    runs = culprit.project.told_runs("test_cc_reads_the_gadget")
    without = [r for r in runs if "CHANGED" in (r["seen"][support.WIDGET] or "")
               and "BROKEN" not in (r["seen"][support.GADGET] or "")]
    assert without and all(r["ok"] for r in without), f"no green run of the build without the culprit: {runs}"


def test_the_culprit_is_named_and_nothing_landed_before_it_was_found(culprit):
    """S6: the close records name C among the culprits; no commit on ``main`` ever held C's change and no revert was
    made (the culprit was found before anything landed, never by taking merged code out)."""
    culprits = culprit.project.record(A).get("culprits")
    assert isinstance(culprits, list) and any(C in str(c) or "W2-c1" in str(c) for c in culprits), \
        f"the close record does not name the culprit: {culprits!r}"
    touched = culprit.project.git("log", "--format=%H %s", f"{culprit.base}..main", "--", support.GADGET).strip()
    assert not touched, f"main held the culprit's change at some point: {touched}"
    reverts = culprit.project.git("log", "--format=%s", f"{culprit.base}..main", "--grep=Revert").strip()
    assert not reverts, f"merged code was taken out: {reverts}"


def test_a_red_no_single_candidate_explains_refuses_the_batch(tmp_path_factory):
    """S6, F3: A and B each break the same test: no single candidate explains the red; the batch is refused with
    BATCH_UNEXPLAINED and closes nothing."""
    batch = Batch(tmp_path_factory.mktemp("w2_115_batch_unexplained"), {BB_BOTH: BOTH_NOT_BROKEN}, [
        (A, "W2-aa", {support.WIDGET: "# the widget, CHANGED BROKEN\n"}, None),
        (B, "W2-b1", {BOLT: "# a bolt, CHANGED\n"}, None),
        (C, "W2-c1", {support.GADGET: "# the gadget, BROKEN\n"}, None)],
        bb_paths=["src/gov/widget/**", "src/gov/gadget/**"])
    support.assert_refused(batch.run, support.BATCH_UNEXPLAINED)
    batch.nothing_landed()


ADDED = f"{support.ADDED_TEST}::test_w2_115_added"
_SEES_THE_BOLT = f"    WATCH.append({BOLT!r})\n"
# The culprit's own new test: red wherever it exists.
NEW_RED = _SEES_THE_BOLT + "    _tell(False)\n    assert False, 'a new red'\n"
# A new test red only beside another candidate's change (the bolt's or the gadget's), green with its own alone.
NEW_RED_BESIDE_OTHERS = _SEES_THE_BOLT + (
    f"    now = _seen()\n    ok = 'CHANGED' not in (now[{BOLT!r}] or '') + (now[{support.GADGET!r}] or '')\n"
    "    _tell(ok)\n    assert ok, 'the bolt or the gadget changed'\n")


class OwnNewTest(Batch):
    """A adds a new test (``tests/unit/widget/test_w2_115_added.py``) with ``body`` beside its widget change; B
    changes the bolt, C the gadget; no planted red. Built without A, the test does not exist."""

    def __init__(self, base, body, test_map=support.DEFAULT_TEST_MAP):
        added = support.telling("test_w2_115_added", base / "told", body)
        super().__init__(base, {}, [
            (A, "W2-aa", {support.WIDGET: "# the widget, CHANGED\n", support.ADDED_TEST: added}, None),
            (B, "W2-b1", {BOLT: "# a bolt, CHANGED\n"}, None),
            (C, "W2-c1", {support.GADGET: "# the gadget, CHANGED\n"}, None)], test_map=test_map)


@pytest.fixture(scope="module")
def own_new_test(tmp_path_factory):
    return OwnNewTest(tmp_path_factory.mktemp("w2_115_batch_own_new_test"), NEW_RED)


def test_a_culprit_whose_red_is_its_own_new_test_goes_back_and_the_rest_land(own_new_test):
    """F-3 (S6, F3): A's red is a test A itself adds; no build without one candidate turns it green (without A it
    is absent). Once confirmed with A alone, A is the culprit: named in the close records, not closed, its work not
    on ``main``; B and C land on the same run. Not refused as unexplained."""
    batch = own_new_test
    assert batch.project.ticket_status(A) != "closed", f"the culprit closed\n{batch.run.describe()}"
    assert not support.is_ancestor(batch.project, batch.commits[A]), "the culprit's work landed on main"
    for ticket in (B, C):
        assert batch.landed(ticket), f"{ticket} did not land\n{batch.run.describe()}"
    commits = {batch.project.record(t).get("commit") for t in (B, C)}
    assert len(commits) == 1 and None not in commits, f"B and C did not land on the same run: {commits}"
    culprits = batch.project.record(B).get("culprits")
    assert isinstance(culprits, list) and any(A in str(c) or "W2-aa" in str(c) for c in culprits), \
        f"the close record does not name the culprit A: {culprits!r}"


def test_a_culprit_s_own_new_test_is_confirmed_red_with_that_candidate_alone(own_new_test):
    """F-3 (S6): the new test ran red on the base plus A only (the widget changed; neither the bolt nor the gadget)."""
    runs = own_new_test.project.told_runs("test_w2_115_added")
    alone = [r for r in runs if "CHANGED" in (r["seen"].get(support.WIDGET) or "")
             and "CHANGED" not in (r["seen"].get(BOLT) or "") + (r["seen"].get(support.GADGET) or "")]
    assert alone and not any(r["ok"] for r in alone), \
        f"the red was not confirmed with the culprit alone: {len(alone)} run(s) of the base plus A only\n" \
        f"{own_new_test.run.describe()}"


def test_nothing_landed_before_the_culprit_with_its_own_new_test_was_found(own_new_test):
    """F-3 (S6, F3): no commit on ``main`` ever held A's new test, and no revert was made."""
    batch = own_new_test
    assert batch.project.head() != batch.base, f"nothing landed\n{batch.run.describe()}"
    touched = batch.project.git("log", "--format=%H %s", f"{batch.base}..main", "--", support.ADDED_TEST).strip()
    assert not touched, f"main held the culprit's new test at some point: {touched}"
    reverts = batch.project.git("log", "--format=%s", f"{batch.base}..main", "--grep=Revert").strip()
    assert not reverts, f"merged code was taken out: {reverts}"


def test_a_new_test_green_with_its_candidate_alone_is_not_blamed_and_the_batch_is_refused(tmp_path_factory):
    """F-3's control (S6, F3): A's new test fails in the batch but passes with A alone (it fails beside B's or C's
    change, and without B or without C it is still red): not confirmed alone, so no single candidate explains it;
    refused with BATCH_UNEXPLAINED and nothing lands."""
    batch = OwnNewTest(tmp_path_factory.mktemp("w2_115_batch_new_test_beside"), NEW_RED_BESIDE_OTHERS)
    support.assert_refused(batch.run, support.BATCH_UNEXPLAINED)
    batch.nothing_landed()


def test_a_candidate_that_cannot_be_isolated_refuses_the_batch(tmp_path_factory):
    """S6: A causes the red and B's branch is made from A's, so the build without A cannot be made: the batch is
    refused with CANDIDATE_NOT_ISOLATED and nothing lands."""
    batch = Batch(tmp_path_factory.mktemp("w2_115_batch_isolation"), {BB_WIDGET: support.WIDGET_NOT_BROKEN}, [
        (A, "W2-aa", {support.WIDGET: "# the widget, CHANGED BROKEN\n"}, None),
        (B, "W2-b1", {BOLT: "# a bolt, CHANGED\n"}, "w2/W2-aa"),
        (C, "W2-c1", {"src/gov/gadget/__init__.py": "# the gadget's package\n"}, None)])
    support.assert_refused(batch.run, support.CANDIDATE_NOT_ISOLATED)
    batch.nothing_landed()


# --------------------------------------------------------------------------
# Review round 2's R2-4: two guards of the culprit search (S6, F3). Today's code is right on both; each case guards
# against a mutant that would land work it must not.
# --------------------------------------------------------------------------

# A's new test: red at once beside the bolt's or the gadget's change; with A alone it runs past the per-test limit.
NEW_RED_BESIDE_OTHERS_TIMES_OUT_ALONE = _SEES_THE_BOLT + (
    f"    now = _seen()\n    beside = 'CHANGED' in (now[{BOLT!r}] or '') + (now[{support.GADGET!r}] or '')\n"
    "    _tell(False)\n    assert not beside, 'the bolt or the gadget changed'\n    time.sleep(120)\n")
SHORT_LIMIT = dict(support.DEFAULT_TEST_MAP, per_test_timeout=3)


def test_a_culprit_s_own_new_test_that_times_out_alone_is_not_confirmed_and_nothing_lands(tmp_path_factory):
    """R2-4 part 1, the reviewer's B3 (S4, S6, F3): A's new test fails in the batch (beside B's or C's change) and,
    with A alone on the base, runs past the per-test limit instead of failing. A timeout is an unknown failure and
    never confirms (S4), so no single candidate explains the red: refused with BATCH_UNEXPLAINED, nothing lands (not
    B, not C; ``main`` does not move). The run with A alone is observed, so the timeout is what was judged."""
    batch = OwnNewTest(tmp_path_factory.mktemp("w2_115_batch_timeout_alone"), NEW_RED_BESIDE_OTHERS_TIMES_OUT_ALONE,
                       test_map=SHORT_LIMIT)
    support.assert_refused(batch.run, support.BATCH_UNEXPLAINED)
    batch.nothing_landed()
    runs = batch.project.told_runs("test_w2_115_added")
    alone = [r for r in runs if "CHANGED" in (r["seen"].get(support.WIDGET) or "")
             and "CHANGED" not in (r["seen"].get(BOLT) or "") + (r["seen"].get(support.GADGET) or "")]
    assert alone, f"the new test was never run with A alone (no timeout was judged)\n{batch.run.describe()}"


RUN_INCOMPLETE = "RUN_INCOMPLETE"  # the brief's code (R2-4, the reviewer's B1); the Interface's list does not name it
A7, B7, C7 = "PROJ-a7a7", "PROJ-b7b7", "PROJ-c7c7"
NOTES, MORE_NOTES = support.GOVERNANCE_FILE, "governance/project/more-notes.yaml"
A7_TEST = "tests/unit/a7/test_w2_115_a7.py"  # a folder no ticket's allowed paths cover (no suite reached by overlap)
# Records select the record-reading suites (S2), and each candidate's checkpoint is a record: none is named here,
# so the checkpoints select nothing.
NO_RECORD_READERS = dict(support.DEFAULT_TEST_MAP, record_reading=[])


class ZeroRest(Batch):
    """A7 adds only a new failing test (``tests/unit/a7/test_w2_115_a7.py``, a folder only A7's allowed paths
    cover); B7 and C7 each change only a governance file, which selects nothing by itself (S2). No candidate has an
    acceptance folder and the test map names no record-reading suite, so the batch's selection holds A7's new test
    file alone; without A7 the rest holds none of its targets."""

    def __init__(self, base):
        cs = support.close_support
        self.sandbox = support.cli_support.make_sandbox(base / "sandbox")
        told = base / "told"
        files = {cs.ticket_path(A7): cs.ticket_text(A7, "W2-a7", allowed_paths=["tests/unit/a7/**"],
                                                    status="in_progress"),
                 cs.ticket_path(B7): cs.ticket_text(B7, "W2-b7", allowed_paths=[NOTES], status="in_progress"),
                 cs.ticket_path(C7): cs.ticket_text(C7, "W2-c7", allowed_paths=[MORE_NOTES], status="in_progress"),
                 NOTES: "notes: none\n", MORE_NOTES: "notes: none\n"}
        self.project = support.Smart(base / "project", told, files=files, test_map=NO_RECORD_READERS)
        self.base = self.project.head()
        self.commits = support.plant_candidates(self.project, self.sandbox, [
            (A7, "W2-a7", {A7_TEST: support.telling("test_w2_115_a7", told, NEW_RED)}, None),
            (B7, "W2-b7", {NOTES: "notes: changed\n"}, None),
            (C7, "W2-c7", {MORE_NOTES: "notes: changed\n"}, None)])
        self.run = support.run_module(self.project, self.sandbox, support.BATCH_MODULE, "run", A7, B7, C7)

    def nothing_landed(self):
        assert self.project.head() == self.base, f"main moved: something landed\n{self.run.describe()}"
        for ticket in (A7, B7, C7):
            assert not self.landed(ticket), f"{ticket} landed"
            assert self.project.ticket_status(ticket) != "closed", f"{ticket} closed"


def test_the_rest_never_lands_on_a_run_of_zero_tests(tmp_path_factory):
    """R2-4 part 2, the reviewer's B1 (S6, F3): the batch's only target is A7's own new test file, red, and A7 is
    confirmed alone as the culprit. Without A7 the rest (B7, C7) holds none of the selection's targets, so its run
    would be a run of 0 tests: it must not land on that. Refused with RUN_INCOMPLETE; nothing lands."""
    batch = ZeroRest(tmp_path_factory.mktemp("w2_115_batch_zero_rest"))
    support.assert_refused(batch.run, RUN_INCOMPLETE)
    batch.nothing_landed()
    runs = batch.project.told_runs("test_w2_115_a7")
    assert len(runs) >= 2 and not any(r["ok"] for r in runs), \
        f"A7's new test did not run red in the batch and again alone: {len(runs)} run(s)\n{batch.run.describe()}"
