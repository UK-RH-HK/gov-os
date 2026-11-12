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


def _project(base, reds, bb_paths=None):
    told = base / "told"
    files = {**support.candidate_ticket(B, "W2-b1", ["src/gov/bolt/**"], told),
             **support.candidate_ticket(C, "W2-c1", ["src/gov/gadget/**"], told),
             "src/gov/bolt/__init__.py": "", BOLT: "# a bolt\n"}
    if bb_paths:
        files[support.close_support.ticket_path("PROJ-bbbb")] = support.close_support.ticket_text(
            "PROJ-bbbb", "W2-bb", allowed_paths=bb_paths, status="closed")
    files.update({node.split("::")[0]: support.telling(node.split("::")[1], told, body)
                  for node, body in reds.items()})
    return support.Smart(base / "project", told, files=files)


class Batch:
    def __init__(self, base, reds, candidates, bb_paths=None):
        self.sandbox = support.cli_support.make_sandbox(base / "sandbox")
        self.project = _project(base, reds, bb_paths)
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


def test_a_candidate_that_cannot_be_isolated_refuses_the_batch(tmp_path_factory):
    """S6: A causes the red and B's branch is made from A's, so the build without A cannot be made: the batch is
    refused with CANDIDATE_NOT_ISOLATED and nothing lands."""
    batch = Batch(tmp_path_factory.mktemp("w2_115_batch_isolation"), {BB_WIDGET: support.WIDGET_NOT_BROKEN}, [
        (A, "W2-aa", {support.WIDGET: "# the widget, CHANGED BROKEN\n"}, None),
        (B, "W2-b1", {BOLT: "# a bolt, CHANGED\n"}, "w2/W2-aa"),
        (C, "W2-c1", {"src/gov/gadget/__init__.py": "# the gadget's package\n"}, None)])
    support.assert_refused(batch.run, support.CANDIDATE_NOT_ISOLATED)
    batch.nothing_landed()
