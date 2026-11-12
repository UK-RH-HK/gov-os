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
