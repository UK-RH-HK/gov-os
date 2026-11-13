"""S4, S5, F1 and F2: how the scoped close judges a red, and what it does with one it did not cause.

S4: every failing test is run again alone; a red is judged against the head without the change, one run each way:
it is not the change's only if the head without it has it red with the same failure type; the nightly's recorded
result is read first; no nightly-baseline clone is built; only the load-sensitive cases get 3 rounds; an unknown
failure (a timeout, no record) never matches.
S5: a red the change did not cause is named in the close record and opened as a repair ticket for the orchestrator;
no accepted-reds or load-sensitive list is read or written.
F1: an unowned red does not refuse the scoped close; a caused red does not close.
F2 (the lists half): the lists in the path map are neither changed nor written (bytes and file time unchanged).

Red on today's code: today's close refuses every red (``CHECK_FAILED``), re-runs nothing on the base, and writes no
``reds`` or ``nightly`` in a close record.
"""

import json
import os
from pathlib import Path

import pytest

import w2_115_support as support

BB_WIDGET = support.node_of("W2-bb", "bb_widget", "test_bb_reads_the_widget")
BB_FLIP = support.node_of("W2-bb", "bb_flip", "test_bb_flip")
BB_SLEEP = support.node_of("W2-bb", "bb_sleep", "test_bb_sleep")
ADDED = f"{support.ADDED_TEST}::test_w2_115_added"


# --------------------------------------------------------------------------
# The unowned reds (the session's ``unowned`` close, conftest.py)
# --------------------------------------------------------------------------

def test_an_unowned_red_does_not_refuse_the_scoped_close(unowned):
    """F1, S4: a red the head without the change also has, with the same failure type, is not the change's: the
    scoped close passes and the ticket closes."""
    support.passed(unowned.run)
    assert unowned.project.ticket_status() == "closed", f"the ticket did not close\n{unowned.run.describe()}"


def test_an_unowned_red_is_named_in_the_record_and_opened_as_a_repair_ticket_for_the_orchestrator(unowned):
    """S5: the close record names the unowned red (not caused, its reason) and the repair ticket it opened in
    ``.tickets/``: assigned to the orchestrator, naming the red's node id and failure type."""
    support.passed(unowned.run)
    front = unowned.project.record()
    entry = support.red_entry(front, unowned.known)
    assert entry.get("caused") is False, f"the unowned red is recorded as caused: {entry}"
    assert str(entry.get("reason") or "").strip(), f"the unowned red has no reason: {entry}"
    assert entry.get("failure_type") == "AssertionError", f"the red's failure type is not recorded: {entry}"
    repair = entry.get("repair_ticket")
    assert repair, f"the unowned red names no repair ticket: {entry}"
    new = [p for p in (unowned.project.root / ".tickets").glob("*.md") if p.stem not in unowned.known_tickets]
    found = [p for p in new if support.close_support.frontmatter_of(p).get("id") == repair or p.stem == repair]
    assert len(found) == 1, f"no ticket {repair} was opened in .tickets/: {[p.name for p in new]}"
    text = found[0].read_text(encoding="utf-8")
    assert support.close_support.frontmatter_of(found[0]).get("assignee") == "orchestrator", \
        f"the repair ticket is not for the orchestrator:\n{text}"
    assert unowned.known in text and "AssertionError" in text, \
        f"the repair ticket does not name the red's node id and failure type:\n{text}"


def test_every_failing_test_is_run_again_alone_and_once_on_the_head_without_the_change(unowned):
    """S4: the known red (not load-sensitive) ran in the selection, once more alone, and once on the head without
    the change: one run each way."""
    support.passed(unowned.run)
    runs = unowned.project.told_runs("test_bb_known")
    head, base = support.head_side(runs), support.base_side(runs)
    assert len(head) == 2, f"the red did not run in the selection and once again alone (head side): {len(head)} runs"
    assert len(base) == 1, f"the red did not run once on the head without the change: {len(base)} runs"


def test_only_the_load_sensitive_case_gets_three_rounds(unowned):
    """S4: the load-sensitive case (a ``latency`` entry of the serial-only list) gets 3 rounds each way."""
    support.passed(unowned.run)
    runs = unowned.project.told_runs("test_bb_timing")
    head, base = support.head_side(runs), support.base_side(runs)
    assert len(head) >= 4, f"the load-sensitive red did not get 3 rounds alone after its run: {len(head)} head runs"
    assert len(base) >= 3, f"the load-sensitive red did not get 3 rounds on the head without the change: {len(base)}"


def test_the_nightly_s_recorded_result_is_read_first(unowned):
    """S4: the close record says the nightly's recorded result was read, and names the planted record."""
    support.passed(unowned.run)
    nightly = unowned.project.record().get("nightly")
    assert isinstance(nightly, dict) and nightly.get("read") is True, f"the nightly's result was not read: {nightly!r}"
    assert nightly.get("record") == unowned.project.nightly_record, \
        f"the record names another nightly record: {nightly.get('record')!r} != {unowned.project.nightly_record!r}"


CLONE_REL = ".gov-runtime/close/clone"


def _repos_under(root):
    """Every folder under ``root`` that holds a ``.git`` (a folder or a worktree's file); none is walked into."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames or ".git" in filenames:
            found.append(Path(dirpath).resolve())
            dirnames[:] = []
    return found


def _worktrees(repo):
    """``(path, head)`` of every entry ``git worktree list`` names for ``repo``."""
    entries, path = [], None
    for line in support.close_support.git(repo, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            path = Path(line[len("worktree "):]).resolve()
        elif line.startswith("HEAD ") and path is not None:
            entries.append((path, line[len("HEAD "):].strip()))
    return entries


def test_no_clone_is_built_for_the_nightly_baseline(unowned):
    """S4: no clone is built for the nightly baseline. After the run: no checkout (the project's worktrees, the warm
    clone's, any repository left in ``.gov-runtime/`` or the close's temporary folder) stands at the commit the
    nightly record names; no clone or worktree exists other than the project and S10's warm clone
    (``.gov-runtime/close/clone/``); and no folder named for a baseline or a nightly exists in ``.gov-runtime/`` or
    the temporary folder, the warm clone's committed folders (its checkout's ``docs/close/nightly/``) aside.

    Rewrite-Reason: S10's warm clone is the Interface's (DEC-1001 (b), DEC-1112 (3)); S4 forbids only a
    nightly-baseline clone (DEC-1083). The td-1 check failed on the warm clone's committed ``docs/close/nightly/``.
    """
    support.passed(unowned.run)
    project = unowned.project
    root = project.root.resolve()
    clone = (project.root / CLONE_REL).resolve()
    night = json.loads((project.root / project.nightly_record).read_text(encoding="utf-8"))["head"]
    clone_is_repo = (clone / ".git").exists()

    checkouts = _worktrees(project.root)
    if clone_is_repo:
        checkouts += _worktrees(clone)
    at_night = sorted({str(p) for p, head in checkouts if head == night})
    assert not at_night, f"a checkout stands at the nightly's recorded commit {night[:12]}: {at_night}"

    others = sorted({str(p) for p, _ in checkouts if p not in (root, clone)})
    assert not others, f"a worktree other than the project and the warm clone was built: {others}"

    repos = (_repos_under(project.root / ".gov-runtime") + _repos_under(unowned.sandbox.tmpdir))
    for repo in repos:
        head = support.close_support.git(repo, "rev-parse", "HEAD", check=False).strip()
        assert head != night, f"a repository stands at the nightly's recorded commit {night[:12]}: {repo}"
    extra = sorted(str(r) for r in repos if r != clone)
    assert not extra, f"a clone other than the warm clone ({CLONE_REL}) was built: {extra}"

    tracked = set()
    if clone_is_repo:
        listed = support.close_support.git(clone, "ls-tree", "-r", "-d", "--name-only", "HEAD", check=False)
        tracked = {(clone / rel).resolve() for rel in listed.splitlines() if rel.strip()}
    words = ("baseline", "nightly")
    named = (support.paths_named(project.root / ".gov-runtime", words)
             + support.paths_named(unowned.sandbox.tmpdir, words))
    found = sorted(p for p in named if Path(p).resolve() not in tracked)
    assert not found, f"a nightly-baseline clone was built: {found}"


def test_no_accepted_reds_or_load_sensitive_list_is_written(unowned):
    """S5, F2: the path map that holds the lists is unchanged (bytes and file time), and no list file appeared."""
    support.passed(unowned.run)
    path_map = unowned.project.root / support.PATH_MAP_REL
    assert (path_map.read_bytes(), path_map.stat().st_mtime_ns) == unowned.path_map_before, \
        "the path map (accepted_reds, load_sensitive) was written by the scoped close"
    after = {p.relative_to(unowned.project.root).as_posix() for p in unowned.project.root.rglob("*")
             if ".git" not in p.parts}
    lists = [rel for rel in after - unowned.files_before
             if any(w in rel.lower() for w in ("accepted", "load_sensitive", "load-sensitive"))]
    assert not lists, f"the scoped close wrote a list: {lists}"


# --------------------------------------------------------------------------
# Caused reds: each refuses the scoped close
# --------------------------------------------------------------------------

def _caused(make_project, sandbox, reds, failures, work, test_map=None):
    keys = {"test_map": test_map} if test_map else {}
    project = make_project(reds={}, nightly="green", **keys)
    for rel, text in reds.items():
        project.merged({rel: text}, "a test planted before the base")
    project.plant_night(project.head(), failures)
    project.work(work)
    project.ready(sandbox)
    return project, project.close(sandbox)


def _assert_caused(project, run, node):
    """The close was refused naming ``node``, the ticket did not close, and the red was run again alone on the
    change (at least two runs on the head side: the selection's run and the run alone)."""
    said = support.assert_refused(run)
    assert node in said, f"the refusal does not name the caused red {node}\n{run.describe()}"
    assert project.ticket_status() == "in_progress", "the ticket closed with a red its change caused"
    head = support.head_side(project.told_runs(node.split("::")[1]))
    assert len(head) >= 2, f"the failing test {node} was not run again alone: {len(head)} run(s) on the change"
    return head


def test_a_red_the_head_without_the_change_does_not_have_refuses_the_close(make_project, sandbox, tmp_path):
    """F1, S4: a red the head without the change does not have is the change's: the close does not close; the red
    ran again alone and once on the head without the change, where it passed."""
    told = tmp_path / "project-told"
    reds = {BB_WIDGET.split("::")[0]: support.telling("test_bb_reads_the_widget", told, support.WIDGET_NOT_BROKEN)}
    project, run = _caused(make_project, sandbox, reds, [], {support.WIDGET: "# the widget, CHANGED BROKEN\n"})
    _assert_caused(project, run, BB_WIDGET)
    runs = project.told_runs("test_bb_reads_the_widget")
    head, base = support.head_side(runs), support.base_side(runs)
    assert len(head) == 2 and not any(r["ok"] for r in head), f"the red was not run again alone: {len(head)} runs"
    assert len(base) == 1 and base[0]["ok"], f"the red was not run once on the head without the change: {base}"


def test_a_red_with_another_failure_type_on_the_head_without_the_change_is_the_change_s(make_project, sandbox,
                                                                                       tmp_path):
    """S4: red on both sides but with another failure type (ZeroDivisionError on the change, AssertionError
    without it) does not match: the close does not close."""
    told = tmp_path / "project-told"
    reds = {BB_FLIP.split("::")[0]: support.telling("test_bb_flip", told, support.TYPE_FLIP)}
    failures = [{"test": BB_FLIP, "failure_type": "AssertionError", "text": "AssertionError: a known red"}]
    project, run = _caused(make_project, sandbox, reds, failures, {support.WIDGET: "# the widget, CHANGED\n"})
    _assert_caused(project, run, BB_FLIP)


def test_a_timeout_never_matches(make_project, sandbox, tmp_path):
    """S4: a red that is a timeout on both sides is an unknown failure: it never matches; the close does not close."""
    told = tmp_path / "project-told"
    reds = {BB_SLEEP.split("::")[0]: support.telling("test_bb_sleep", told, support.SLEEPS)}
    failures = [{"test": BB_SLEEP, "failure_type": "timeout", "text": "Timeout"}]
    test_map = dict(support.DEFAULT_TEST_MAP, per_test_timeout=3)
    project, run = _caused(make_project, sandbox, reds, failures, {support.WIDGET: "# the widget, CHANGED\n"},
                           test_map=test_map)
    _assert_caused(project, run, BB_SLEEP)


def test_a_failing_test_the_ticket_added_has_no_record_and_never_matches(make_project, sandbox, tmp_path):
    """S4: a failing test the ticket added has no record on the head without the change: it never matches; the
    close does not close."""
    told = tmp_path / "project-told"
    project, run = _caused(make_project, sandbox, {}, [], {
        support.WIDGET: "# the widget, CHANGED\n",
        support.ADDED_TEST: support.telling("test_w2_115_added", told, support.KNOWN_RED)})
    _assert_caused(project, run, ADDED)


# --------------------------------------------------------------------------
# The base a red is judged against: the green base, only when it is an ancestor of HEAD; with no green base on
# HEAD's line there is no head without the change and every red is the change's (review round 1's F-1, PK-3 (a);
# review round 2's R2-1, the owner's P1-K (a), DEC-1150 (2); DEC-988 item 3, DEC-989)
# --------------------------------------------------------------------------

RED_CAUSED = "RED_CAUSED"  # the brief's code for a caused red (td-4; review round 1's F-1)
BB_KNOWN = support.node_of("W2-bb", "bb_known", "test_bb_known")


def _widget_test(told):
    return {BB_WIDGET.split("::")[0]: support.telling("test_bb_reads_the_widget", told, support.WIDGET_NOT_BROKEN)}


def _green_base_then_slip(make_project, sandbox, tmp_path, slip, work):
    """W2-bb's widget test passes at the green base G (the initial commit, named by the only nightly record, green);
    then the engineer's commit without a ``Task:`` trailer (``slip``), then the ticket's trailered work."""
    told = tmp_path / "project-told"
    project = make_project(reds=_widget_test(told), nightly="green")
    green = json.loads((project.root / project.nightly_record).read_text(encoding="utf-8"))["head"]
    assert green == project.initial, "the planted green record does not name the initial commit"
    project.slip({support.WIDGET: slip})
    project.work({support.WIDGET: work})
    project.ready(sandbox)
    assert support.is_ancestor(project, green, "HEAD"), "the planted green base is not an ancestor of HEAD"
    before = project.tickets()
    return project, before, project.close(sandbox)


def _assert_red_caused(project, before, run, node, green_base=True):
    """Refused with RED_CAUSED naming ``node``; the ticket stays open; a close record, when the refused close writes
    one, marks ``node`` caused (today's refused close writes none; README, reading 7); no repair ticket names it.
    With a green base on HEAD's line (``green_base``): on it, the head without the change, ``node`` ran and passed.
    Without one there is no head without the change, and nothing is asserted about a run off the change.

    Rewrite-Reason: DEC-1150 (2), the owner's P1-K (a): with no green base every red is the change's (the
    ``green_base`` switch; before, every caller expected a run on a base)."""
    said = support.assert_refused(run, RED_CAUSED)
    assert node in said, f"the refusal does not name the caused red {node}\n{run.describe()}"
    assert project.ticket_status() == "in_progress", "the ticket closed with a red its change caused"
    if (project.root / "docs" / "close" / support.TICKET / f"CL-{support.TICKET}.md").is_file():
        entry = support.red_entry(project.record(), node)
        assert entry.get("caused") is True, f"the close record does not mark the red as the change's: {entry}"
    repairs = [p.name for p in (project.root / ".tickets").glob("*.md")
               if p.stem not in before and node in p.read_text(encoding="utf-8")]
    assert not repairs, f"a repair ticket was opened for a red the change caused: {repairs}"
    if green_base:
        base = support.base_side(project.told_runs(node.split("::")[1]))
        assert base and all(r["ok"] for r in base), \
            f"the red was not judged against a base where it passes (runs without the change: {base})"


def test_a_red_an_untrailered_commit_after_the_green_base_caused_is_never_excused(make_project, sandbox, tmp_path):
    """F-1 (S4, F1): the green base G is an ancestor of HEAD, so reds are judged against G. The engineer's commit
    without a ``Task:`` trailer breaks W2-bb's widget test after G; the ticket's trailered work follows. The red is
    the change's: refused with RED_CAUSED, marked caused in the close record, no repair ticket opened for it, and
    the test ran and passed on G (not on the untrailered commit, where it is already red)."""
    project, before, run = _green_base_then_slip(make_project, sandbox, tmp_path,
                                                 slip="# the widget, CHANGED BROKEN\n",
                                                 work="# the widget, CHANGED BROKEN, and more\n")
    _assert_red_caused(project, before, run, BB_WIDGET)


def test_a_red_a_trailered_commit_after_a_green_untrailered_one_caused_is_refused(make_project, sandbox, tmp_path):
    """F-1's control (S4, F1): the same history, but the untrailered commit is green and the ticket's trailered
    commit breaks the test: still refused with RED_CAUSED, marked caused, no repair ticket."""
    project, before, run = _green_base_then_slip(make_project, sandbox, tmp_path,
                                                 slip="# the widget, tidied\n",
                                                 work="# the widget, CHANGED BROKEN\n")
    _assert_red_caused(project, before, run, BB_WIDGET)


def _green_base_elsewhere(make_project, sandbox, tmp_path, elsewhere, reds_on_main):
    """No green record on ``main``'s line: the only nightly record (green) names a commit on another branch that
    HEAD does not contain. ``reds_on_main`` are planted on ``main`` after the fork, before the ticket's work."""
    project = make_project(nightly=None)
    green = project.elsewhere(elsewhere)
    project.merged(reds_on_main, "a test planted before the base")
    project.plant_night(green, [])
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.ready(sandbox)
    assert not support.is_ancestor(project, green, "HEAD"), "the planted green base is an ancestor of HEAD"
    before = project.tickets()
    return project, before, project.close(sandbox)


def test_with_the_green_base_not_an_ancestor_a_red_the_parent_also_has_is_still_the_change_s(make_project, sandbox,
                                                                                            tmp_path):
    """R2-1, DEC-1150 (2) (S4, F1): the only green record names a commit on another branch, not an ancestor of
    HEAD, so there is no green base on HEAD's line and no head without the change: every red is the change's. W2-bb's
    known red is already red, with the same failure type (AssertionError), on the parent of the ticket's oldest own
    commit; that no longer excuses it (the fallback to that parent is dropped, the owner's P1-K (a)). Refused with
    RED_CAUSED, marked caused when a record is written, no repair ticket, the ticket stays open. Nothing is asserted
    about a run on the parent.

    Rewrite-Reason: DEC-1150 (2), the owner's P1-K (a): with no green base every red is the change's. Was
    ``test_with_the_green_base_not_an_ancestor_a_red_the_parent_has_is_not_the_change_s`` (PK-3 (a)'s fallback:
    the close passed, the red not caused, a repair ticket opened)."""
    told = tmp_path / "project-told"
    project, before, run = _green_base_elsewhere(
        make_project, sandbox, tmp_path, {support.GIZMO: "# a gizmo, on another branch\n"},
        {BB_KNOWN.split("::")[0]: support.telling("test_bb_known", told, support.KNOWN_RED)})
    _assert_red_caused(project, before, run, BB_KNOWN, green_base=False)


def test_with_the_green_base_not_an_ancestor_a_red_the_parent_does_not_have_is_the_change_s(make_project, sandbox,
                                                                                            tmp_path):
    """F-1, R2-1 (S4, F1): the only green record names a commit on another branch, not an ancestor of HEAD, so
    there is no green base on HEAD's line and every red is the change's. W2-bb's widget test passes before the
    ticket's work, and the work breaks it (the other branch has the widget broken too, so a close judging against
    that branch would wrongly excuse it). Refused with RED_CAUSED, marked caused, no repair ticket.

    Rewrite-Reason: DEC-1150 (2), the owner's P1-K (a): with no green base every red is the change's. The run on
    the parent of the ticket's oldest own commit is no longer asserted (the fallback is dropped; there is no head
    without the change)."""
    told = tmp_path / "project-told"
    project = make_project(reds=_widget_test(told), nightly=None)
    green = project.elsewhere({support.WIDGET: "# the widget, BROKEN on another branch\n"})
    project.plant_night(green, [])
    project.work({support.WIDGET: "# the widget, CHANGED BROKEN\n"})
    project.ready(sandbox)
    assert not support.is_ancestor(project, green, "HEAD"), "the planted green base is an ancestor of HEAD"
    before = project.tickets()
    run = project.close(sandbox)
    _assert_red_caused(project, before, run, BB_WIDGET, green_base=False)


def test_with_no_green_record_a_red_an_untrailered_first_commit_caused_is_the_change_s(make_project, sandbox,
                                                                                       tmp_path):
    """R2-1 (the reviewer's P1), DEC-1150 (2) (S4, F1): no green record at all, so no head without the change.
    The engineer's first commit has no ``Task:`` trailer (an honest slip) and breaks W2-bb's widget test; the
    ticket's trailered work follows. Judged against the parent of the oldest trailered commit (the slip, where the
    test is already red with the same failure type) the red would be excused; with no green base it is the
    change's: refused with RED_CAUSED, marked caused when a record is written, no repair ticket, the ticket stays
    open. Nothing is asserted about a run off the change."""
    told = tmp_path / "project-told"
    project = make_project(reds=_widget_test(told), nightly=None)
    records = list((project.root / support.NIGHTLY_DIR_REL).glob("*.json")) \
        if (project.root / support.NIGHTLY_DIR_REL).is_dir() else []
    assert not records, f"the planted project holds a nightly record: {records}"
    project.slip({support.WIDGET: "# the widget, BROKEN by an untrailered commit\n"})
    project.work({support.WIDGET: "# the widget, CHANGED BROKEN\n"})
    project.ready(sandbox)
    before = project.tickets()
    run = project.close(sandbox)
    _assert_red_caused(project, before, run, BB_WIDGET, green_base=False)
