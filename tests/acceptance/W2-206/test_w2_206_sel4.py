"""SEL-4 (plan item 1-0; ``.tickets/DAEO-l2b2.md`` "Fix: one selection for many branches"): ``gov queue <T1>=<b1>
<T2>=<b2> ... --select`` prints ONE object for the merged tree of all the branches: one ``suites`` list (the union of each
branch's own selection, never a sum of ranges), ``tickets`` naming each; branches that do not merge together are refused
as a whole (``CANDIDATE_NOT_ISOLATED``), nothing run; the same ticket may be given twice with two branches (a held batch
of fix branches under one closed ticket); a branch that is itself the merge of several gives one list.

Each planted project is built once per session (a file lock in pytest's shared folder, as ``conftest._shared``): a green
nightly record naming the first commit, direct commits of the base after it that no branch has (a moved module, two
unplaced paths), and the branches forked at the green head. ``gov queue ... --select`` is run as a program, without
``--json``. The kit is W2-115b's (``w2_206_support.kit``).
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import traceback

import pytest

import w2_206_support as support  # noqa: F401  (puts W2-115b's kit and its helpers on the path)
import w2_115b_sel_support as sel
from w2_206_support import A, B, kit, module_rel

CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
OTHER = "# CHANGED by another branch\nVALUE = 3\n"
NOISE = [{sel.GIZMO: "# the gizmo, moved on the base\nVALUE = 1\n"}, {"repin.sh": "#!/bin/sh\necho repin\n"},
         {"docs/emergency-2/briefs/LEAD-plan.md": "# a lead brief\n"}]
FIX = "Fix: SEL-4 a held fix of the closed ticket"
GIZMO_SUITE = kit.GIZMO[0]
WIDGET_SUITE, HELPER_SUITE = kit.USES_WIDGET[0], kit.USES_HELPER[0]


def _shared(factory, name, build):
    root = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        root = root.parent
    folder = root / f"w2-206-sel4-{name}"
    with open(root / f"w2-206-sel4-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "data.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"the planted run {name} could not be built:\n{broken.read_text()}")
        if done.is_file():
            return json.loads(done.read_text(encoding="utf-8"))
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        try:
            data = build(folder)
        except BaseException:
            broken.write_text(traceback.format_exc(), encoding="utf-8")
            raise
        done.write_text(json.dumps(data), encoding="utf-8")
        return data


def _project(folder, tickets=(A, B), extra=None):
    """The project with the green night and the base's commits after it; returns it (``base`` is the green head)."""
    p = kit.Planted(folder / "project", folder / "told", tickets=tickets, extra=extra)
    green = p.base
    p.commit("a green night", kit.ORCHESTRATOR, ["Role: orchestrator"],
             {f"docs/close/nightly/NR-20261101T010000Z-{green[:12]}.json":
              json.dumps({"verdict": "green", "head": green}) + "\n"})
    for files in NOISE:
        p.commit(f"a commit of the base: {', '.join(files)}", kit.ORCHESTRATOR, ["Role: orchestrator"], files)
    return p


def _fork(p, ticket, name, files, fix=False, start=None):
    """``name`` from the green head (or ``start``), one commit of ``ticket``'s (with a Fix line where ``fix``)."""
    p.branch_from(name, start)
    lines = [f"Task: {ticket.id}", "Role: engineer"] + ([FIX] if fix else [])
    tip = p.commit(f"work on {ticket.id}", kit.ENGINEER, lines, files)
    p.home()
    return tip


def _select(p, *given):
    return sel.program(p, "queue", *given, "--select")


def _kept(run):
    return {k: run[k] for k in ("args", "code", "stdout", "stderr")}


def _check_fork(p, *names):
    for name in names:
        fork = kit.git(p.root, "merge-base", "main", name).strip()
        assert fork == p.base, f"fixture: {name} forks at {fork[:12]}, not at the green head {p.base[:12]}"


def build_pair(folder):
    """A's branch changes the widget, B's the gadget; ``--select`` of both and of each alone."""
    p = _project(folder)
    _fork(p, A, "topic/aa", {module_rel("widget"): CHANGED})
    _fork(p, B, "topic/bb", {module_rel("gadget"): CHANGED})
    _check_fork(p, "topic/aa", "topic/bb")
    return {"both": _kept(_select(p, f"{A.id}=topic/aa", f"{B.id}=topic/bb")),
            "a": _kept(_select(p, f"{A.id}=topic/aa")), "b": _kept(_select(p, f"{B.id}=topic/bb"))}


def build_conflict(folder):
    """Both branches rewrite the widget: they do not merge together."""
    told = folder / "told"
    p = _project(folder)
    _fork(p, A, "topic/aa", {module_rel("widget"): CHANGED})
    _fork(p, B, "topic/bb", {module_rel("widget"): OTHER})
    _check_fork(p, "topic/aa", "topic/bb")
    clash = kit.git(p.root, "merge-tree", "--write-tree", "topic/aa", "topic/bb", check=False)
    assert "CONFLICT" in clash, f"fixture: the two branches merge cleanly\n{clash}"
    before = p.state()
    run = _select(p, f"{A.id}=topic/aa", f"{B.id}=topic/bb")
    return {"run": _kept(run), "same_state": p.state() == before, "told": sorted(os.listdir(told))}


def build_same(folder):
    """A, closed, with two fix branches (the widget; the helper), each with a ``Fix:`` line; the held batch."""
    p = _project(folder, tickets=(A,), extra={A.ticket_rel: kit.ticket_text(A, "closed")})
    _fork(p, A, "fix/one", {module_rel("widget"): CHANGED}, fix=True)
    _fork(p, A, "fix/two", {module_rel("helper"): CHANGED}, fix=True)
    _check_fork(p, "fix/one", "fix/two")
    return {"both": _kept(_select(p, f"{A.id}=fix/one", f"{A.id}=fix/two")),
            "one": _kept(_select(p, f"{A.id}=fix/one")), "two": _kept(_select(p, f"{A.id}=fix/two"))}


def build_merge(folder):
    """A's branch is the merge of two branches (the widget; the helper), each forked at the green head."""
    p = _project(folder, tickets=(A,))
    _fork(p, A, "part/one", {module_rel("widget"): CHANGED})
    _fork(p, A, "part/two", {module_rel("helper"): CHANGED})
    p.branch_from("topic/merged", "part/one")
    kit.git(p.root, "merge", "--no-ff", "--no-edit", "part/two")
    p.commit("merge the parts", kit.ENGINEER, [f"Task: {A.id}", "Role: engineer"])
    p.home()
    _check_fork(p, "topic/merged")
    return {"merged": _kept(_select(p, f"{A.id}=topic/merged")), "one": _kept(_select(p, f"{A.id}=part/one")),
            "two": _kept(_select(p, f"{A.id}=part/two"))}


BUILDS = {"pair": build_pair, "conflict": build_conflict, "same": build_same, "merge": build_merge}


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    return lambda name: _shared(tmp_path_factory, name, BUILDS[name])


def _object(run):
    return sel.chosen_object(run)


# -- the two branches of two tickets ------------------------------------------------------------------------------------

def test_sel4_two_branches_print_one_object_naming_both_tickets(built):
    chosen = _object(built("pair")["both"])
    assert chosen.get("tickets") == [A.id, B.id], f"tickets: {chosen.get('tickets')!r}"
    assert "ticket" not in chosen, f"a single `ticket` beside two: {chosen.get('ticket')!r}"
    assert isinstance(chosen.get("suites"), list), sorted(chosen)


def test_sel4_suites_are_the_union_of_each_branch_s_own_selection_and_none_of_the_base_s(built):
    data = built("pair")
    both = _object(data["both"])["suites"]
    union = sorted(set(_object(data["a"])["suites"]) | set(_object(data["b"])["suites"]))
    assert sorted(both) == union, f"suites {both} are not the union {union} of each branch's selection alone"
    assert len(both) == len(set(both)), f"a suite is named twice: {both}"
    want = sorted([A.acceptance, WIDGET_SUITE, B.acceptance])
    assert sorted(both) == want, f"the branches change the widget and the gadget alone; suites: {both}"
    assert GIZMO_SUITE not in both, f"a suite only the base's commits reach is selected: {both}"


# -- branches that do not merge together --------------------------------------------------------------------------------

def test_sel4_a_pair_that_conflicts_is_refused_as_a_whole(built):
    run = built("conflict")["run"]
    assert run["code"] != 0, f"exit {run['code']}\n{kit.describe(run)}"
    assert "CANDIDATE_NOT_ISOLATED" in run["stderr"], f"stderr does not say CANDIDATE_NOT_ISOLATED\n{kit.describe(run)}"
    printed = run["stdout"].strip()
    assert "suites" not in printed, f"a selection is printed for a refused pair\n{kit.describe(run)}"


def test_sel4_the_refused_pair_runs_nothing_and_moves_nothing(built):
    data = built("conflict")
    assert data["same_state"], "the refused pair changed the project (a ref, HEAD, the status or a tracked file)"
    assert not data["told"], f"a planted test ran: {data['told']}"


# -- the same ticket twice, and a branch that is a merge ------------------------------------------------------------------

def test_sel4_the_same_ticket_given_twice_with_two_branches_is_accepted_and_gives_one_list(built):
    data = built("same")
    for name in ("one", "two"):
        _object(data[name])    # fixture: each fix branch alone is a selection of its own
    chosen = _object(data["both"])
    assert A.id in chosen.get("tickets", []), f"tickets: {chosen.get('tickets')!r}"
    union = sorted(set(_object(data["one"])["suites"]) | set(_object(data["two"])["suites"]))
    assert sorted(chosen["suites"]) == union, f"suites {chosen['suites']} are not the union {union}"
    assert sorted(chosen["suites"]) == sorted([A.acceptance, WIDGET_SUITE, HELPER_SUITE]), chosen["suites"]
    assert GIZMO_SUITE not in chosen["suites"], f"a suite only the base's commits reach: {chosen['suites']}"


def test_sel4_a_branch_that_is_the_merge_of_several_gives_one_list(built):
    data = built("merge")
    chosen = _object(data["merged"])
    assert sorted(chosen["suites"]) == sorted([A.acceptance, WIDGET_SUITE, HELPER_SUITE]), chosen["suites"]
    union = sorted(set(_object(data["one"])["suites"]) | set(_object(data["two"])["suites"]))
    assert sorted(chosen["suites"]) == union, f"suites {chosen['suites']} are not the union {union}"
