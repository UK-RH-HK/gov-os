"""Support for the trustworthy-selection cases (plan item 1-0, SEL-1 to SEL-3), beside ``w2_115b_support``.

A planted project (``Planted``: A and B on ``main``), a green nightly record naming its first commit, then direct commits
on ``main`` after it (by no ticket, or by A's ``Task:`` as an earlier landing of the ticket would), and A's work branch
``topic/aa`` forked at the green head: the base has moved on since the green record, the branch has not seen it.
``gov queue PROJ-aaaa=topic/aa --select`` is run as a program (one JSON object on stdout, or ``SELECTION_REFUSED`` on
stderr with exit 2).
"""

from __future__ import annotations

import json
import subprocess
import sys

import w2_115b_support as support
from w2_115b_support import A, ORCHESTRATOR, module_rel

EXIT_SELECT_REFUSED = 2
CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
WIDGET = {module_rel("widget"): CHANGED}        # A's own module: A's suite holds it, test_uses_widget imports it
HELPER = module_rel("helper")                   # A's other module: test_uses_helper imports it
GIZMO = module_rel("gizmo")                     # imported by test_gizmo alone (no ticket holds it)
GADGET = module_rel("gadget")                   # B's module: B's suite imports it
OWN_SUITES = sorted([A.acceptance, support.USES_WIDGET[0]])   # what a change to the widget alone selects


def plant(planted, base_commits=(), branch_files=None):
    """The project: a green night naming the first commit; one direct commit on ``main`` per ``base_commits`` item
    (``{rel: text}``, no ``Task:``; for an item given as ``(files, trailer lines)`` those trailers); A's branch
    ``topic/aa`` from the green head with one commit of A's (``branch_files``, the widget by default). The fixture
    checks its own shape: the branch forks at the green head and ``main`` has moved on."""
    p = planted()
    green = p.base
    p.commit("a green night", ORCHESTRATOR, ["Role: orchestrator"],
             {f"docs/close/nightly/NR-20261101T010000Z-{green[:12]}.json":
              json.dumps({"verdict": "green", "head": green}) + "\n"})
    for item in base_commits:
        files, lines = item if isinstance(item, tuple) else (item, ["Role: orchestrator"])
        p.commit(f"a commit of the base: {', '.join(files)}", ORCHESTRATOR, lines, files)
    p.plant_branch(A, "topic/aa", [(branch_files or WIDGET, "engineer", True)])
    main, tip = support.rev(p.root, "main"), p.tips[A.id]
    fork = support.git(p.root, "merge-base", "main", tip).strip()
    assert fork == green, f"fixture: the branch forks at {fork[:12]}, not at the green head {green[:12]}"
    moved = support.git(p.root, "rev-list", "--count", f"{green}..{main}").strip()
    assert int(moved) >= 1 + len(base_commits), f"fixture: main moved by {moved} commit(s) since the green head"
    return p


def program(project, *args):
    env = support.base_env(project.root.parent / f"{project.root.name}-env")
    cmd = [sys.executable, "-m", "gov.cli.main", *args, "--root", str(project.root)]
    done = subprocess.run(cmd, cwd=str(project.root), env=env, capture_output=True, text=True,
                          timeout=support.GOV_TIMEOUT_S, stdin=subprocess.DEVNULL)
    return {"args": list(args), "code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}


def select(project):
    return program(project, "queue", f"{A.id}=topic/aa", "--select")


def chosen_object(run):
    assert run["code"] == 0, f"exit {run['code']}, not 0\n{support.describe(run)}"
    try:
        chosen = json.loads(run["stdout"])
    except ValueError:
        raise AssertionError(f"stdout is not one JSON object\n{support.describe(run)}") from None
    assert isinstance(chosen, dict), support.describe(run)
    return chosen


def refused(run, *named, unnamed=()):
    assert run["code"] == EXIT_SELECT_REFUSED, f"exit {run['code']}, not 2\n{support.describe(run)}"
    assert "SELECTION_REFUSED" in run["stderr"], support.describe(run)
    for rel in named:
        assert rel in run["stderr"], f"the refusal does not name {rel}\n{support.describe(run)}"
    for rel in unnamed:
        assert rel not in run["stderr"], f"the refusal names {rel}\n{support.describe(run)}"
