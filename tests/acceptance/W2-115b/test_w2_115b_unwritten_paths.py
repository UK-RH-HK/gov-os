"""The queue's selection refuses only the landing's own unplaced paths (W2-115b's fix, L2-4; README, "Fix: the
base's unplaced paths").

Each case plants a project (``w2_115b_support.Planted``: A and B on ``main``), a green nightly record naming its
first commit, then direct commits on ``main`` by no ticket (a document outside ``record_only``, a shell script, or a
module a unit test imports), beside A's work branch ``topic/aa`` forked at the green head. ``gov queue PROJ-aaaa=topic/aa
--select`` (plain: one JSON object on stdout, or ``SELECTION_REFUSED`` on stderr with exit 2), the landing itself
(``--json``), and ``gov close --select`` (the selection without a branch's change) are run as programs.
"""

from __future__ import annotations

import json
import subprocess
import sys

import w2_115b_support as support
from w2_115b_support import A, ORCHESTRATOR, module_rel

EXIT_SELECT_REFUSED = 2
DOC = "docs/emergency-2/briefs/LEAD-plan.md"   # outside record_only (.tickets/**, docs/checkpoints/**, docs/close/**)
SCRIPT = "repin.sh"
STRAY = "tools/stray.sh"                        # an unplaced path A's own branch writes
CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
WIDGET = {module_rel("widget"): CHANGED}        # mapped code: A's own suite holds it, a unit test imports it


def _plant(planted, base_files, branch_files=None):
    """The project: a green night naming the first commit, one direct commit per ``base_files`` item on ``main``
    (no ``Task:``), and A's branch ``topic/aa`` from the green head with one commit of A's (``branch_files``)."""
    p = planted()
    green = p.base
    p.commit("a green night", ORCHESTRATOR, ["Role: orchestrator"],
             {f"docs/close/nightly/NR-20261101T010000Z-{green[:12]}.json":
              json.dumps({"verdict": "green", "head": green}) + "\n"})
    for rel, text in base_files.items():
        p.commit(f"a direct commit: {rel}", ORCHESTRATOR, ["Role: orchestrator"], {rel: text})
    p.plant_branch(A, "topic/aa", [(branch_files or WIDGET, "engineer", True)])
    return p


def _program(project, *args):
    env = support.base_env(project.root.parent / f"{project.root.name}-env")
    cmd = [sys.executable, "-m", "gov.cli.main", *args, "--root", str(project.root)]
    done = subprocess.run(cmd, cwd=str(project.root), env=env, capture_output=True, text=True,
                          timeout=support.GOV_TIMEOUT_S, stdin=subprocess.DEVNULL)
    return {"args": list(args), "code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}


def _select(project):
    return _program(project, "queue", f"{A.id}=topic/aa", "--select")


def _object(run):
    assert run["code"] == 0, f"exit {run['code']}, not 0\n{support.describe(run)}"
    try:
        chosen = json.loads(run["stdout"])
    except ValueError:
        raise AssertionError(f"stdout is not one JSON object\n{support.describe(run)}") from None
    assert isinstance(chosen, dict), support.describe(run)
    return chosen


BASE = {DOC: "# a lead brief\n", SCRIPT: "#!/bin/sh\necho repin\n"}


# -- the base's unplaced paths: listed, not refused -------------------------------------------------------------------

def test_select_lists_the_base_s_unplaced_paths_under_unplaced_base_and_exits_0(planted):
    p = _plant(planted, BASE)
    chosen = _object(_select(p))
    assert chosen.get("unplaced_base") == sorted([DOC, SCRIPT]), f"unplaced_base: {chosen.get('unplaced_base')!r}"
    assert A.acceptance in chosen.get("suites", []), f"A's own suite is not selected: {chosen.get('suites')}"
    assert support.USES_WIDGET[0] in chosen["suites"], f"the widget's importer is not selected: {chosen['suites']}"


def test_a_base_side_path_a_test_imports_still_selects_that_test(planted):
    gizmo = module_rel("gizmo")
    p = _plant(planted, {gizmo: "# the gizmo, moved on the base\nVALUE = 1\n", DOC: "# a lead brief\n"})
    chosen = _object(_select(p))
    assert support.GIZMO[0] in chosen.get("suites", []), f"the gizmo's importer is not selected: {chosen}"
    assert chosen.get("unplaced_base") == [DOC], f"unplaced_base: {chosen.get('unplaced_base')!r}"


def test_the_landing_beside_the_base_s_unplaced_paths_lands_and_closes(planted):
    p = _plant(planted, BASE)
    support.self_check(p, {p.tips[A.id]: {A.node: "passed", support.USES_WIDGET_NODE: "passed"}})
    old_head = support.rev(p.root, "main")
    result = support.answer(support.run_queue(p, f"{A.id}=topic/aa"), support.EXIT_LANDED)
    assert result.get("landed") == [A.id], f"landed: {result.get('landed')}"
    support.assert_landed_through_close_commits(p, result, "main", old_head)
    head = support.rev(p.root, "main")
    assert support.close_record(p, head, A.id).get("commit") == result["tested"]
    assert support.status_at(p.root, head, A.id) == "closed"


# -- the landing's own unplaced path: refused, naming only it ----------------------------------------------------------

def test_a_branch_that_writes_an_unplaced_path_is_refused_naming_it_and_not_the_base_s(planted):
    p = _plant(planted, BASE, {**WIDGET, STRAY: "#!/bin/sh\necho stray\n"})
    run = _select(p)
    assert run["code"] == EXIT_SELECT_REFUSED, f"exit {run['code']}, not 2\n{support.describe(run)}"
    assert "SELECTION_REFUSED" in run["stderr"], support.describe(run)
    assert STRAY in run["stderr"], f"the refusal does not name the branch's path\n{support.describe(run)}"
    named = [rel for rel in (DOC, SCRIPT) if rel in run["stderr"]]
    assert not named, f"the refusal names the base's path(s) {named}\n{support.describe(run)}"


# -- without the branch's change (gov close): nothing changes ---------------------------------------------------------

def test_gov_close_select_without_a_change_still_refuses_the_base_s_unplaced_paths(planted):
    p = _plant(planted, BASE)
    run = _program(p, "close", "--select", A.id)
    assert run["code"] == EXIT_SELECT_REFUSED, f"exit {run['code']}, not 2\n{support.describe(run)}"
    assert "SELECTION_REFUSED" in run["stderr"], support.describe(run)
    assert DOC in run["stderr"] and SCRIPT in run["stderr"], support.describe(run)
