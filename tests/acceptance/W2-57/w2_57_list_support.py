"""Helpers for W2-57's batch B: the serial-only list, its two routes, and the close that reads it.

The list is ``tests/acceptance/serial-only.txt``: one entry on a line, the beginning of a pytest node id; what
follows `` #`` is a comment. Every reader takes the entry as the text before `` #`` (``gov close``'s plugin, the
orchestrator's nightly script, W1-30's r11). Since W2-57 every entry's comment is ``<route>: <kind>: <reason>``:
``serial`` keeps the entry in the close (alone, after the parallel phase); ``nightly`` routes it to the nightly
(collected by the close and left out of both its phases; run alone in the nightly). These helpers read that form
as a reader of the list does; nothing here imports the product.

The close is driven as W1-30's round-11 cases drive it: a temporary project of W1-30's suite (``Project``), small
tests of its own that tell how they ran (``telling_test``), and ``gov close`` from this worktree's ``src/``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _name in ("W1-30", "W1-02"):
    _folder = str(_HERE.parent / _name)
    if _folder not in sys.path:
        sys.path.insert(0, _folder)

import w1_30_support as close_support  # noqa: E402  (a project gov close runs in, and the telling tests)
import w1_02_support as guard_support  # noqa: E402  (the guard hook in a project, timed as the harness waits)

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
LIST_REL = "tests/acceptance/serial-only.txt"
LIST = REPO_ROOT / LIST_REL
SERIAL, NIGHTLY = "serial", "nightly"
ROUTES = (SERIAL, NIGHTLY)
# The kinds, and the route each kind takes (DEC-889 item 5: latency cases stay alone; daemon and race cases stay
# serial in this run; live and real-model cases move to the nightly).
KINDS = {"latency": SERIAL, "daemon": SERIAL, "race": SERIAL, "real-model": NIGHTLY, "live-session": NIGHTLY}
# The close's plugin folder, as ``gov close`` gives it to its parallel run (``-p gov_close_serial_only``).
PLUGIN_FOLDER = SRC / "gov" / "close" / "pytest_plugin"
PLUGIN = "gov_close_serial_only"
PLUGIN_ROOT_VARIABLE = "GOV_CLOSE_SERIAL_ONLY_OF"


# ---------------------------------------------------------------------------
# Reading the list as its readers do
# ---------------------------------------------------------------------------

def lines_of(path=LIST):
    return Path(path).read_text(encoding="utf-8").splitlines()


def entries(path=LIST):
    """``[(entry, comment)]``: the text before `` #`` of every line that holds one, and what follows it."""
    found = []
    for line in lines_of(path):
        entry, _, comment = (" " + line).partition(" #")
        if entry.strip():
            found.append((entry.strip(), comment.strip()))
    return found


def header(path=LIST):
    """The comment lines before the first entry, without their ``#``, as one text."""
    kept = []
    for line in lines_of(path):
        if (" " + line).partition(" #")[0].strip():
            break
        kept.append(line.lstrip("#").strip())
    return "\n".join(kept)


def parsed(comment):
    """``(route, kind, reason)`` of an entry's comment ``<route>: <kind>: <reason>``; None for another form."""
    parts = [part.strip() for part in comment.split(":", 2)]
    return tuple(parts) if len(parts) == 3 else None


def declares(entry, node):
    """Whether ``entry`` names ``node``: it is the id, or the id goes on at a boundary (``::``, ``[``, ``/``)."""
    return node == entry or (node.startswith(entry) and node[len(entry):].startswith(("::", "[", "/")))


def route_of(node, listed):
    """The route of the entry of ``listed`` (``[(entry, comment)]``) that names ``node``; None when none does."""
    for entry, comment in listed:
        if declares(entry, node):
            found = parsed(comment)
            return found[0] if found else comment
    return None


def plugin_entries(root):
    """What ``gov close``'s own plugin takes from the list of ``root``, asked in a fresh interpreter with this
    worktree's code."""
    code = ("import json, sys; from gov.close.pytest_plugin import gov_close_serial_only as s; "
            "print(json.dumps(s.entries(__import__('pathlib').Path(sys.argv[1]))))")
    done = subprocess.run([sys.executable, "-c", code, str(root)], capture_output=True, text=True, timeout=60,
                          env={**os.environ, "PYTHONPATH": str(SRC)}, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"the close's plugin could not read the list: {done.stderr[-400:]}"
    import json
    return json.loads(done.stdout)


def collected(*args, cwd=REPO_ROOT):
    """The node ids pytest collects for ``args`` under ``cwd``, with this worktree's code."""
    done = subprocess.run([sys.executable, "-m", "pytest", *args, "--collect-only", "-q", "-p", "no:cacheprovider"],
                          cwd=str(cwd), env={**os.environ, "PYTHONPATH": str(SRC)}, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=600)
    assert done.returncode in (0, 5), f"pytest did not collect {args}:\n{done.stdout[-2000:]}\n{done.stderr[-1000:]}"
    return [line.strip() for line in done.stdout.splitlines() if "::" in line]


# ---------------------------------------------------------------------------
# A close on a temporary project (W1-30's round 11), with a list in the reworked form
# ---------------------------------------------------------------------------

TICKET = "PROJ-w257"
WBS = "W1-w257"
OTHER = "tests/acceptance/W1-w257other"
UNIT = "tests/unit"


def telling(name, told, decorator=""):
    return close_support.telling_test(name, told, decorator=decorator)


def second_function(text):
    """The function part of a telling test's text, to put a second one in the same file."""
    return text.split("import pytest\n\n\n", 1)[1]


def list_text(lines):
    """A list in the reworked form: one header line, then ``(entry, route, kind)`` lines."""
    return ("# planted cases that cannot hold under load: <entry>  # <route>: <kind>: <reason>\n"
            + "".join(f"{entry}  # {route}: {kind}: planted by W2-57's case\n" for entry, route, kind in lines))


def build_closable(project, told, regression, acceptance, listed=()):
    """W1-30's round-11 project: the regression tests (``{rel: text}``) and the list (the orchestrator's commit),
    the ticket with its acceptance tests (``{name: text}``) and the engineer's work."""
    for rel, text in regression.items():
        project.write(rel, text)
    if listed:
        project.write(LIST_REL, list_text(listed))
    project.commit("regression tests", who=close_support.ORCHESTRATOR)
    project.add_ticket(TICKET, WBS)
    for name, text in acceptance.items():
        project.write(f"tests/acceptance/{WBS}/{name}.py", text)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=close_support.IMPLEMENTER, trailers=close_support.trailers_of(TICKET))
    close_support.checkpointed(project, TICKET)


def close(project, sandbox):
    """``gov close`` of the ticket, with the store loaded first, as W1-30's round-11 cases run it."""
    close_support.load_store(project, sandbox)
    return project.gov(sandbox, close_support.COMMAND, TICKET, "--json")


# ---------------------------------------------------------------------------
# The nightly's form: the parallel run less the list, then every entry alone
# ---------------------------------------------------------------------------

def nightly_form(root, folder="tests", workers=2):
    """The nightly's form on the project ``root``: one parallel run of ``folder`` with the close's plugin (every
    entry of the list left out), then each entry of the list (the text before `` #``) alone, in its own run.
    Returns ``[(form, entry or None, completed process)]``."""
    # A run of its own: nothing of the run that started it (its worker's name, its options) reaches it.
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTEST_")}
    env.update({"PYTHONPATH": os.pathsep.join([str(SRC), str(PLUGIN_FOLDER)]), PLUGIN_ROOT_VARIABLE: str(root)})
    base = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed"]
    runs = [("parallel", None, subprocess.run(base + [folder, "-n", str(workers), "-p", PLUGIN], cwd=str(root),
                                              env=env, capture_output=True, text=True, timeout=600,
                                              stdin=subprocess.DEVNULL))]
    alone_env = {key: value for key, value in env.items() if key != PLUGIN_ROOT_VARIABLE}
    for entry, _ in entries(Path(root) / LIST_REL):
        runs.append(("alone", entry, subprocess.run(base + [entry], cwd=str(root), env=alone_env,
                                                    capture_output=True, text=True, timeout=600,
                                                    stdin=subprocess.DEVNULL)))
    return runs


# ---------------------------------------------------------------------------
# A test designer's read through the guard, on a ticket branch with changes (I1 F-10)
# ---------------------------------------------------------------------------

BASE_BRANCH = "w2/integrate"       # the base Policy 2 (c) reads the branch's changes against (DEC-826 Q2)
CHANGED_FILES = 120                # a ticket branch of ordinary size: real branches held 48 to 318 (I1 F-10)


def designer_world(base):
    """W1-02's fixture project with the guard installed, its first commit on ``w2/integrate``, then the ticket's
    own branch ``w2/<wbs>`` with ``CHANGED_FILES`` files of the ticket's code changed. Returns (project, sandbox)."""
    sandbox = guard_support.make_sandbox(Path(base) / "sandbox")
    project = guard_support.make_project(Path(base) / "project")
    guard_support.git(project, "branch", "-m", "main", BASE_BRANCH)
    guard_support.git(project, "checkout", "-q", "-b", f"w2/{guard_support.TICKET_WBS_ID}")
    for index in range(CHANGED_FILES):
        (project / "src/gov/guard" / f"change_{index:03d}.py").write_text(f"VALUE = {index}\n", encoding="utf-8")
    guard_support.git(project, "add", "-A")
    guard_support.git(project, "commit", "-q", "-m", "the ticket's own work")
    return project, sandbox


def designer_read(project, sandbox, rel):
    """One Read of ``rel`` by the ticket's test designer, through the installed guard, timed as the harness
    waits for it (W1-02's ``run_hook``: the hook process, start to exit)."""
    return guard_support.run_hook(project, "Read", {"file_path": str(project / rel)}, sandbox,
                                  role=guard_support.TEST_DESIGNER, ticket=guard_support.TICKET_ID)
