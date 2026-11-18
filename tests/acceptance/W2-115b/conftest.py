"""Fixtures for W2-115b's acceptance tests (``gov queue``): the planted runs, each built once per test session.

A planted run is built by the first process that asks for it, under a lock in the session's shared temp folder, and
read by every other case and xdist worker from there (the run's answer and the project's state are kept as JSON;
the project's git state is read in place, never changed by a case). A build that fails is kept as failed: every case
that reads it fails with the build's error, not with a second build. Before ``gov queue`` runs, each build checks its
own planted project with plain pytest (``support.self_check``), so a red case is never a broken fixture.
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

import w2_115b_support as support  # noqa: E402
from w2_115b_support import A, B, C, D, E, G, H, K, M, module_rel  # noqa: E402

CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
BROKEN = "# BROKEN by the ticket\nVALUE = 0\n"


def _shared(factory, name, build):
    base = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        base = base.parent
    folder = base / f"w2-115b-{name}"
    with open(base / f"w2-115b-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "landing.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"the planted run {name} could not be built:\n{broken.read_text()}")
        if done.is_file():
            return support.Landing(json.loads(done.read_text(encoding="utf-8")))
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        try:
            data = build(folder)
        except BaseException:
            broken.write_text(traceback.format_exc(), encoding="utf-8")
            raise
        done.write_text(json.dumps(data), encoding="utf-8")
        return support.Landing(data)


def _run(project, onto, *args, **extra):
    """The project's state and the integration head, then ``gov queue <args>``: the run's data."""
    before = project.state()
    old_head = support.rev(project.root, onto)
    run = support.run_queue(project, *args)
    return support.landing_data(project, run, onto, old_head, before, **extra)


# --------------------------------------------------------------------------
# The planted runs
# --------------------------------------------------------------------------

def build_green(folder):
    """One green ticket, A, on ``develop`` (checked out at the root, no ``queue.yaml``), its branch given on the
    command line. The branch holds A's trailered commit (the widget) and an honest slip without a ``Task:`` trailer
    (the helper): both are the branch's change."""
    p = support.Planted(folder / "project", folder / "told", branch="develop")
    p.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED}, "engineer", True),
                                   ({module_rel("helper"): CHANGED}, "engineer", False)])
    support.self_check(p, {
        p.base: {A.node: "passed", B.node: "passed", support.USES_WIDGET_NODE: "passed",
                 support.node(support.USES_HELPER[0]): "passed", support.node(support.GIZMO[0]): "passed"},
        p.tips[A.id]: {A.node: "passed", support.USES_WIDGET_NODE: "passed",
                       support.node(support.USES_HELPER[0]): "passed"}})
    return _run(p, "develop", f"{A.id}=topic/aa")


def build_red(folder):
    """One ticket, A, whose change breaks the widget: its own suite and the unit test that imports it go red."""
    p = support.Planted(folder / "project", folder / "told")
    p.plant_branch(A, "topic/aa", [({module_rel("widget"): BROKEN}, "engineer", True)])
    support.self_check(p, {p.base: {support.USES_WIDGET_NODE: "passed"},
                           p.tips[A.id]: {support.USES_WIDGET_NODE: "failed"}})
    return _run(p, "main", f"{A.id}=topic/aa")


def build_batch(folder):
    """Two tickets: A green (the widget), B red (it breaks the gadget, which its own suite guards). A's suite also
    watches the gadget (it does not guard it), so its runs tell whether B's change was in the tree."""
    told = folder / "told"
    p = support.Planted(folder / "project", told,
                        extra={A.suite_file: support.telling(A.suite_file, told, A.modules, also_watch=["gadget"])})
    p.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED}, "engineer", True)])
    p.plant_branch(B, "topic/bb", [({module_rel("gadget"): BROKEN}, "engineer", True)])
    support.self_check(p, {p.tips[A.id]: {A.node: "passed"}, p.tips[B.id]: {B.node: "failed"}})
    return _run(p, "main", f"{A.id}=topic/aa", f"{B.id}=topic/bb")


def _appended(project, rel, line):
    return (project.root / rel).read_text(encoding="utf-8") + line


def _merge_designer(p, ticket, work, designer, edit=None):
    """``ticket``'s work branch ``work`` (the engineer's code commit) with the designer's branch ``designer`` (a new
    test) merged into it by the engineer; ``edit`` (a path) is changed in the merge's resolution. Returns the merge
    commit."""
    more = f"{ticket.acceptance}test_{ticket.slug}_more.py"
    p.branch_from(designer)
    p.work(ticket, {more: support.telling(more, p.told, ticket.modules)}, role="independent-test-designer",
           who=support.DESIGNER, message="the test designer's tests")
    p.home()
    p.branch_from(work)
    p.work(ticket, {module_rel(ticket.modules[0]): CHANGED})
    support.git(p.root, "merge", "--no-ff", "--no-commit", designer)
    if edit:
        p.write(edit, _appended(p, edit, "# the engineer's edit, made in the merge\n"))
    merge = p.commit(f"merge {designer}", support.ENGINEER, [f"Task: {ticket.id}", "Role: engineer"])
    p.home()
    p.record_branch(ticket, work)
    return merge


def build_authors(folder):
    """G-1 in one batch of six: C (an engineer's commit to its suite under ``tests/acceptance/``) and K (an engineer's
    commit to its ``acceptance_tests.path`` outside it) refused; D (the test designer's commit to its suite), E (the
    owner's) and G (a clean merge of the designer's branch) landing; H (a merge whose resolution edits the designer's
    new test) refused."""
    p = support.Planted(folder / "project", folder / "told", tickets=(A, B, C, D, E, G, H, K))
    offending = {}
    p.branch_from("topic/cc")
    p.work(C, {module_rel("mod_cc"): CHANGED})
    offending[C.id] = p.work(C, {C.suite_file: _appended(p, C.suite_file, "# loosened by the engineer\n")})
    p.home()
    p.record_branch(C, "topic/cc")
    p.plant_branch(D, "topic/dd", [({module_rel("mod_dd"): CHANGED}, "engineer", True)])
    p.checkout("topic/dd")
    p.work(D, {D.suite_file: _appended(p, D.suite_file, "# one more case by the test designer\n")},
           role="independent-test-designer", who=support.DESIGNER)
    p.home()
    p.record_branch(D, "topic/dd")
    p.plant_branch(E, "topic/ee", [({module_rel("mod_ee"): CHANGED}, "engineer", True)])
    p.checkout("topic/ee")
    p.work(E, {E.suite_file: _appended(p, E.suite_file, "# a case the owner wrote\n")}, role="owner",
           who=support.OWNER)
    p.home()
    p.record_branch(E, "topic/ee")
    clean = _merge_designer(p, G, "topic/gg", "designer/gg")
    offending[H.id] = _merge_designer(p, H, "topic/hh", "designer/hh", edit=f"{H.acceptance}test_hh_more.py")
    p.branch_from("topic/kk")
    p.work(K, {module_rel("mod_kk"): CHANGED})
    offending[K.id] = p.work(K, {K.suite_file: _appended(p, K.suite_file, "# loosened by the engineer\n")})
    p.home()
    p.record_branch(K, "topic/kk")
    support.self_check(p, {p.tips[D.id]: {D.node: "passed"}, p.tips[E.id]: {E.node: "passed"},
                           p.tips[G.id]: {G.node: "passed", support.node(f"{G.acceptance}test_gg_more.py"): "passed"}})
    order = (C, D, E, G, H, K)
    return _run(p, "main", *[f"{t.id}={p.branches[t.id]}" for t in order], offending=offending, clean_merge=clean)


def build_authors_alone(folder):
    """G-1 with one candidate: C's engineer commit to its acceptance suite; nothing else."""
    p = support.Planted(folder / "project", folder / "told", tickets=(A, B, C))
    p.branch_from("topic/cc")
    offending = p.work(C, {C.suite_file: _appended(p, C.suite_file, "# loosened by the engineer\n")})
    p.home()
    p.record_branch(C, "topic/cc")
    return _run(p, "main", f"{C.id}=topic/cc", offending={C.id: offending})


def build_notices(folder):
    """A, green: one commit inside its allowed paths (the widget), one outside them (a governance file)."""
    p = support.Planted(folder / "project", folder / "told")
    p.branch_from("topic/aa")
    inside = p.work(A, {module_rel("widget"): CHANGED})
    outside = p.work(A, {support.NOTES_REL: "notes: [one more]\n"})
    p.home()
    p.record_branch(A, "topic/aa")
    support.self_check(p, {p.tips[A.id]: {A.node: "passed"}})
    return _run(p, "main", A.id + "=topic/aa", inside=inside, outside=outside)


def build_feature(folder):
    """A repository on ``main`` whose ``queue.yaml`` names the integration branch and the form ``feature/{wbs}``; the
    ticket named alone."""
    p = support.Planted(folder / "project", folder / "told",
                        queue_yaml='integration: main\nwork_branch: "feature/{wbs}"\n')
    p.plant_branch(A, "feature/F-aa", [({module_rel("widget"): CHANGED}, "engineer", True)])
    support.self_check(p, {p.tips[A.id]: {A.node: "passed"}})
    return _run(p, "main", A.id)


def build_onto(folder):
    """``queue.yaml`` names ``main`` and the form ``work/{ticket}``; ``--onto release`` names another integration
    branch, not checked out at the root (``main`` is)."""
    p = support.Planted(folder / "project", folder / "told",
                        queue_yaml='integration: main\nwork_branch: "work/{ticket}"\n')
    support.git(p.root, "branch", "release")
    p.plant_branch(A, f"work/{A.id}", [({module_rel("widget"): CHANGED}, "engineer", True)])
    support.self_check(p, {p.tips[A.id]: {A.node: "passed"}})
    return _run(p, "release", A.id, "--onto", "release", main=support.rev(p.root, "main"))


def build_unexplained(folder):
    """A's change reaches a test that is red on the base too."""
    told = folder / "told"
    p = support.Planted(folder / "project", told,
                        extra={support.KNOWN_RED: support.telling(support.KNOWN_RED, told, ["widget"],
                                                                  support.RED_ALWAYS)})
    p.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED}, "engineer", True)])
    support.self_check(p, {p.base: {support.KNOWN_RED_NODE: "failed", A.node: "passed"}})
    return _run(p, "main", f"{A.id}=topic/aa")


def build_moved(folder):
    """M's own suite holds a test that commits once to the root's integration branch (``main``, checked out there)
    while the queue's run runs, as another landing would."""
    told, root, marker = folder / "told", folder / "project", folder / "moved.txt"
    p = support.Planted(root, told, tickets=(A, B, M),
                        extra={M.suite_file: support.telling(M.suite_file, told, M.modules,
                                                             support.mover_body(root, marker))})
    p.plant_branch(M, "topic/mm", [({module_rel("mod_mm"): CHANGED}, "engineer", True)])
    support.self_check(p, {p.base: {M.node: "passed"}, p.tips[M.id]: {M.node: "passed"}})
    data = _run(p, "main", f"{M.id}=topic/mm")
    data["extra"]["moved_to"] = marker.read_text(encoding="utf-8").strip() if marker.is_file() else None
    return data


BUILDS = {name[len("build_"):]: f for name, f in globals().items() if name.startswith("build_")}


@pytest.fixture(scope="session")
def landing(tmp_path_factory):
    """``landing(name)``: the planted run ``name`` (one of ``BUILDS``), built once per session."""
    return lambda name: _shared(tmp_path_factory, name, BUILDS[name])


@pytest.fixture()
def planted(tmp_path):
    """A fresh planted project for a case of its own: ``planted(**Planted keys)``."""
    return lambda **keys: support.Planted(tmp_path / "project", tmp_path / "told", **keys)
