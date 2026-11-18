"""Fixtures for W2-202's acceptance tests: the planted runs, each built once per test session (as W2-115b's are).

A planted run is built by the first process that asks for it, under a lock in the session's shared temp folder, and
read by every other case from there; a build that fails is kept as failed, and every case that reads it fails with
the build's error. Before ``gov queue`` runs, each build checks its own planted project (plain pytest at the commits
the case depends on; the freeze flag; the close's own gates on the planted records), so a red case is never a broken
fixture: a broken fixture fails as ``fixture: ...``.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import sys
import traceback
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_202_support as support  # noqa: E402
from w2_202_support import A, B, BROKEN, C, CHANGED, N, O, R, S, U, X, kit, module_rel  # noqa: E402,E741

KNOWN_RED, KNOWN_RED_NODE = kit.KNOWN_RED, kit.KNOWN_RED_NODE


def _shared(factory, name, build):
    base = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        base = base.parent
    folder = base / f"w2-202-{name}"
    with open(base / f"w2-202-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "landing.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"the planted run {name} could not be built:\n{broken.read_text()}")
        if done.is_file():
            return kit.Landing(json.loads(done.read_text(encoding="utf-8")))
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        try:
            data = build(folder)
        except BaseException:
            broken.write_text(traceback.format_exc(), encoding="utf-8")
            raise
        done.write_text(json.dumps(data), encoding="utf-8")
        return kit.Landing(data)


def _run(project, onto, *args, **extra):
    """The project's state and the integration head, then ``gov queue <args>``: the run's data."""
    before = project.state()
    old_head = kit.rev(project.root, onto) if onto else kit.rev(project.root, "HEAD")
    run = kit.run_queue(project, *args)
    return kit.landing_data(project, run, onto, old_head, before, **extra)


def _again(project, *args):
    """One more ``gov queue`` in the same project: the state before it, the run, the state after it."""
    before = project.state()
    run = kit.run_queue(project, *args)
    return {"before": before, "run": run, "after": project.state()}


def _widget(project):
    return project.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED}, "engineer", True)])


def _clone_status(project):
    clone = project.root / kit.CLONE_REL
    return kit.git(clone, "status", "--porcelain") if (clone / ".git").exists() else None


# --------------------------------------------------------------------------
# A1: base reds
# --------------------------------------------------------------------------

def build_base_red(folder):
    """One clean candidate, A (the widget), and ``tests/unit/test_known_red.py``, red on the base (it is in the
    planted project's first commit) and reached by A's change (it imports the widget)."""
    told = folder / "told"
    p = kit.Planted(folder / "project", told,
                    extra={KNOWN_RED: kit.telling(KNOWN_RED, told, ["widget"], kit.RED_ALWAYS)})
    _widget(p)
    kit.self_check(p, {p.base: {KNOWN_RED_NODE: "failed", A.node: "passed", kit.USES_WIDGET_NODE: "passed"},
                       p.tips[A.id]: {KNOWN_RED_NODE: "failed", A.node: "passed", kit.USES_WIDGET_NODE: "passed"}})
    tickets_before = sorted(path.name for path in (p.root / ".tickets").iterdir())
    data = _run(p, "main", f"{A.id}=topic/aa", tickets_before=tickets_before)
    data["extra"]["clone_status"] = _clone_status(p)
    return data


def build_untrailered(folder):
    """As ``base_red``, where the test went red by a commit on ``main`` that carries no trailer at all (no ``Task:``,
    no ``Role:``): it breaks the gizmo, which the test guards; the test imports the widget, which A changes."""
    told = folder / "told"
    p = kit.Planted(folder / "project", told,
                    extra={KNOWN_RED: kit.telling(KNOWN_RED, told, ["widget"], support.GIZMO_NOT_BROKEN,
                                                  also_watch=["gizmo"])})
    first = p.base
    maker = p.commit("a quick change to the gizmo", kit.ENGINEER, [], {module_rel("gizmo"): BROKEN})
    assert kit.trailers(p.root, maker) == [], "fixture: the red-making commit carries a trailer"
    p.base = maker
    _widget(p)
    kit.self_check(p, {first: {KNOWN_RED_NODE: "passed"}, maker: {KNOWN_RED_NODE: "failed", A.node: "passed"},
                       p.tips[A.id]: {KNOWN_RED_NODE: "failed", A.node: "passed"}})
    return _run(p, "main", f"{A.id}=topic/aa", first=first, maker=maker)


def build_each_breaks(folder):
    """Two candidates and one test, ``tests/unit/test_both.py``, green on the base and red when the widget or the
    gadget says CHANGED: A changes the widget, B the gadget. With either left out the test is still red, so no
    single candidate explains it; each candidate's own suite is green."""
    told = folder / "told"
    p = kit.Planted(folder / "project", told,
                    extra={support.BOTH: kit.telling(support.BOTH, told, ["widget", "gadget"],
                                                     support.NEITHER_CHANGED)})
    _widget(p)
    p.plant_branch(B, "topic/bb", [({module_rel("gadget"): CHANGED}, "engineer", True)])
    kit.self_check(p, {p.base: {support.BOTH_NODE: "passed"},
                       p.tips[A.id]: {support.BOTH_NODE: "failed", A.node: "passed"},
                       p.tips[B.id]: {support.BOTH_NODE: "failed", B.node: "passed"}})
    return _run(p, "main", f"{A.id}=topic/aa", f"{B.id}=topic/bb")


def build_another_way(folder):
    """A test red on the base with a bare assert, which A's change makes fail another way (a ``ValueError``): red
    at the base, but not with the same failure type."""
    told = folder / "told"
    p = kit.Planted(folder / "project", told,
                    extra={KNOWN_RED: kit.telling(KNOWN_RED, told, ["widget"], support.RED_ANOTHER_WAY)})
    _widget(p)
    kit.self_check(p, {p.base: {KNOWN_RED_NODE: "failed", A.node: "passed"},
                       p.tips[A.id]: {KNOWN_RED_NODE: "failed", A.node: "passed"}})
    return _run(p, "main", f"{A.id}=topic/aa")


def build_mixed(folder):
    """A base red and a culprit in one batch: ``test_known_red`` is red on the base and reached by A (clean, the
    widget); B breaks the gadget, which ``tests/unit/test_uses_gadget.py`` (green on the base) and its own suite
    guard."""
    told = folder / "told"
    p = kit.Planted(folder / "project", told, unit=(*kit.UNIT_TESTS, support.USES_GADGET),
                    extra={KNOWN_RED: kit.telling(KNOWN_RED, told, ["widget"], kit.RED_ALWAYS)})
    _widget(p)
    p.plant_branch(B, "topic/bb", [({module_rel("gadget"): BROKEN}, "engineer", True)])
    kit.self_check(p, {p.base: {KNOWN_RED_NODE: "failed", support.USES_GADGET_NODE: "passed", B.node: "passed"},
                       p.tips[A.id]: {KNOWN_RED_NODE: "failed", A.node: "passed", kit.USES_WIDGET_NODE: "passed"},
                       p.tips[B.id]: {support.USES_GADGET_NODE: "failed"}})
    return _run(p, "main", f"{A.id}=topic/aa", f"{B.id}=topic/bb")


# --------------------------------------------------------------------------
# A3: acceptance at the landing
# --------------------------------------------------------------------------

def _no_tests_branch(project):
    return project.plant_branch(N, "topic/nn", [({module_rel("mod_nn"): CHANGED}, "engineer", True)])


def build_no_tests(folder):
    """N, a feature ticket whose acceptance folder holds a README and no test (its change is reached by a unit
    test), queued alone; then N and A (green) in one batch."""
    p = support.records_project(folder)
    _no_tests_branch(p)
    _widget(p)
    held = sorted(path.name for path in (p.root / N.acceptance).iterdir())
    assert held == ["README.md"], f"fixture: N's acceptance folder holds {held}"
    kit.self_check(p, {p.tips[N.id]: {kit.node(support.USES_MOD_NN[0]): "passed"}, p.tips[A.id]: {A.node: "passed"}})
    data = _run(p, "main", f"{N.id}=topic/nn")
    data["extra"]["alone_after"] = p.state()
    data["extra"]["batch"] = _again(p, f"{N.id}=topic/nn", f"{A.id}=topic/aa")
    return data


def build_classes(folder):
    """One batch of five: a research, an audit, a coordination and a specification ticket, each with no acceptance
    folder and a record the close's own gate accepts, and N (a feature ticket with no test). Then X alone: a research
    ticket whose record is no research record (the gate refuses it)."""
    p = support.records_project(folder)
    roles = {R.id: "research", U.id: "independent-auditor", O.id: "orchestrator", S.id: "product-spec"}
    for ticket in support.RECORD_TICKETS:
        p.plant_branch(ticket, f"topic/{ticket.wbs}", [(support.record_files(ticket, p.base), roles[ticket.id], True)])
    p.plant_branch(X, f"topic/{X.wbs}", [({X.evidence[0]: "# A note\n\nNo record of a kind.\n"}, "research", True)])
    _no_tests_branch(p)
    support.check_gates(p, accepted=support.RECORD_TICKETS, refused=[X])
    for ticket in (*support.RECORD_TICKETS, X):
        assert not (p.root / "tests" / "acceptance" / ticket.wbs).exists(), f"fixture: {ticket.id} has a test folder"
    kit.self_check(p, {p.base: {support.RECORDS_NODE: "passed"},
                       p.tips[N.id]: {kit.node(support.USES_MOD_NN[0]): "passed"}})
    order = (R, U, O, S, N)
    data = _run(p, "main", *[f"{t.id}={p.branches[t.id]}" for t in order])
    data["extra"]["bad"] = _again(p, f"{X.id}={p.branches[X.id]}")
    return data


def build_accepted(folder):
    """One green ticket, A, whose acceptance folder's README maps its two KPI lines; after the landing, ``gov
    accept`` on a scratch clone at the tested merge (its own answer, for the record to be read against)."""
    p = kit.Planted(folder / "project", folder / "told")
    _widget(p)
    kit.self_check(p, {p.tips[A.id]: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}})
    own = support.accept_at(p, p.tips[A.id], A.id)
    try:
        lines = json.loads(own["stdout"])["result"]["lines"]
    except (ValueError, KeyError, TypeError):
        lines = None
    assert own["code"] == 0 and lines and [line.get("kpi") for line in lines] == ["success-1", "failure-1"], \
        f"fixture: gov accept does not pass A's two lines at its branch tip\n{support.said(own)}"
    data = _run(p, "main", f"{A.id}=topic/aa")
    try:
        tested = json.loads(data["run"]["stdout"])["result"]["tested"]
    except (ValueError, KeyError, TypeError):
        tested = None
    data["extra"]["accept"] = support.accept_at(p, tested, A.id) if tested and kit.rev(p.root, tested) else None
    return data


# --------------------------------------------------------------------------
# A4: a branch already merged
# --------------------------------------------------------------------------

def _merge_by_hand(project, branch):
    kit.git(project.root, "merge", "--no-ff", "-q", "-m", f"merge {branch} by hand", branch, who=kit.ORCHESTRATOR,
            date=project._date())
    return kit.rev(project.root, "HEAD")


def build_merged(folder):
    """A's work branch merged by hand into ``main`` (a merge commit, the ticket still open), then ``gov queue``;
    then ``gov queue`` once more for the same ticket, now closed."""
    p = kit.Planted(folder / "project", folder / "told")
    tip = _widget(p)
    merge = _merge_by_hand(p, "topic/aa")
    assert kit.is_ancestor(p.root, tip, "main") and kit.status_at(p.root, "main", A.id) == "open", \
        "fixture: the branch is not merged by hand with its ticket open"
    kit.self_check(p, {merge: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}})
    data = _run(p, "main", f"{A.id}=topic/aa", hand_merge=merge)
    data["extra"]["again"] = _again(p, f"{A.id}=topic/aa")
    return data


def build_merged_refused(folder):
    """C's work branch (its code commit and an engineer's commit to its acceptance suite) merged by hand into
    ``main``, then ``gov queue``: the checks still run for a branch already merged."""
    p = kit.Planted(folder / "project", folder / "told", tickets=(A, B, C))
    p.branch_from("topic/cc")
    p.work(C, {module_rel("mod_cc"): CHANGED})
    loosened = (p.root / C.suite_file).read_text(encoding="utf-8") + "# loosened by the engineer\n"
    offending = p.work(C, {C.suite_file: loosened})
    p.home()
    p.record_branch(C, "topic/cc")
    merge = _merge_by_hand(p, "topic/cc")
    kit.self_check(p, {merge: {C.node: "passed"}})
    return _run(p, "main", f"{C.id}=topic/cc", hand_merge=merge, offending=offending)


# --------------------------------------------------------------------------
# A5: the pause
# --------------------------------------------------------------------------

def _runtime(project):
    runtime = project.root / ".gov-runtime"
    return sorted(str(path.relative_to(runtime)) for path in runtime.rglob("*")) if runtime.is_dir() else []


def _paused_then_lifted(project, onto, *args):
    support.pause(project)
    runtime_before = _runtime(project)
    data = _run(project, onto, *args, runtime_before=runtime_before)
    data["extra"].update(paused_after=project.state(), runtime_after=_runtime(project),
                         frozen_after=support.freeze_state(project))
    support.lift(project)
    data["extra"]["lifted"] = _again(project, *args)
    return data


def build_paused(folder):
    """``main`` checked out at the root, neither ``queue.yaml`` nor ``close.yaml``; A green. ``gov pause``, ``gov
    queue``, the freeze lifted, ``gov queue`` again."""
    p = kit.Planted(folder / "project", folder / "told")
    _widget(p)
    for rel in (support.QUEUE_YAML_REL, support.CLOSE_YAML_REL):
        assert not (p.root / rel).exists(), f"fixture: the planted project holds {rel}"
    kit.self_check(p, {p.tips[A.id]: {A.node: "passed"}})
    return _paused_then_lifted(p, "main", f"{A.id}=topic/aa")


def build_paused_detached(folder):
    """As ``paused`` with the root detached (no branch checked out, no setting, no ``--onto``)."""
    p = kit.Planted(folder / "project", folder / "told")
    _widget(p)
    p.checkout("--detach")
    assert not kit.git(p.root, "symbolic-ref", "-q", "HEAD", check=False).strip(), "fixture: the root is on a branch"
    return _paused_then_lifted(p, None, f"{A.id}=topic/aa")


BUILDS = {name[len("build_"):]: f for name, f in globals().items() if name.startswith("build_")}


@pytest.fixture(scope="session")
def landing(tmp_path_factory):
    """``landing(name)``: the planted run ``name`` (one of ``BUILDS``), built once per session."""
    return lambda name: _shared(tmp_path_factory, name, BUILDS[name])
