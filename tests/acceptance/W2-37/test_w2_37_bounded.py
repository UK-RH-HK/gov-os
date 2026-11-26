"""The fix "``gov impact`` bounded" (DAEO-6n5k, K-lines IM-1 and IM-2): a record-only change never starts or waits on
the code index, and a change that needs code ends, naming the code index, when the index is stopped.

**The stopped index** is a stand-in executable named ``codebase-memory-mcp``, first on the case's ``PATH``: it writes
one line (its process id and arguments) to a marker file and then sleeps ``HANG_S`` seconds without an answer. So a
case can say whether the tool was ever started. A built index folder (``.gov-runtime/codeintel/files/``) is planted,
so that the command does not stop at "no index was built". No case needs the real tool and none is ``local_only``.

**Bounds.** Every ``gov impact`` run must end within ``BOUND_S`` seconds (the K-lines' 30 s). A run still going after
``CUT_S`` seconds is killed with its process group, and every stand-in still running is killed at the case's end.
"""

from __future__ import annotations

import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

import w2_37_support as support

BOUND_S = 30.0                 # IM-1 and IM-2: the command ends within this
CUT_S = 60.0                   # the harness gives up and kills the run
HANG_S = 87                    # how long the stand-in sleeps; it ends by itself if nothing kills it
UNKNOWN_CODE = "IMPACT_CHANGE_UNKNOWN"
NOT_LOADED = "not loaded"
UNAVAILABLE = "unavailable"
INDEX_NAMES = ("code index", support.TOOL)
ID_SHAPED = ("CHARTER-v5", "DEC-1204", "DAEO-6n5k")        # the K-line's own examples; no record holds them
NAMES_NO_RECORD = "DEC-500"

STOPPED, MARKER = "stopped-index", "starts.log"        # under the case's tmp_path
ROOTS = set()


@pytest.fixture(scope="module", autouse=True)
def remove_daemons(box):
    yield
    support.remove_daemon_dirs(box, ROOTS)


class StoppedIndex:
    """The stand-in code tool: ``path`` is the ``PATH`` that finds it; ``starts()`` is what it recorded."""

    def __init__(self, folder, box):
        folder.mkdir(parents=True, exist_ok=True)
        self.sleep = shutil.which("sleep")
        self.marker = folder / MARKER
        tool = folder / support.TOOL
        tool.write_text(f"#!/bin/sh\necho \"$$ $*\" >> {shlex.quote(str(self.marker))}\n"
                        f"exec {shlex.quote(self.sleep)} {HANG_S}\n", encoding="utf-8")
        tool.chmod(0o755)
        self.path = f"{folder}{os.pathsep}{box.bare}"

    def starts(self):
        return self.marker.read_text(encoding="utf-8").splitlines() if self.marker.exists() else []

    def stop(self):
        """Kill every stand-in still sleeping: only a process whose command line is exactly this sleep."""
        wanted = [self.sleep.encode(), str(HANG_S).encode()]
        for line in self.starts():
            pid = int(line.split()[0])
            try:
                if Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")[:-1] == wanted:
                    os.kill(pid, signal.SIGKILL)
            except OSError:
                pass


@pytest.fixture()
def stopped(box, tmp_path):
    made = StoppedIndex(tmp_path / STOPPED, box)
    yield made
    made.stop()


def a_project(source, box, destination, records=None):
    """A clone of a fixture repository (``records``: more files, committed), its store loaded at HEAD and a built
    code index folder planted."""
    root = support.clone(source, destination)
    if records:
        project = support.Project.__new__(support.Project)
        project.root, project.minute = root, 100
        for rel, text in records.items():
            project.write(rel, text)
        project.commit("more records")
    support.load_store(root, box)
    (root / ".gov-runtime" / "codeintel" / "files").mkdir(parents=True, exist_ok=True)
    ROOTS.add(str(root))
    return root


def bounded(root, change, box, path, folder):
    """``gov impact --json --root <root> <change>...``, which must end within ``BOUND_S`` seconds."""
    argv = [support.COMMAND, "--json", "--root", str(root), *change]
    out, err = folder / "stdout.txt", folder / "stderr.txt"      # files: a surviving child cannot hold a pipe open
    started = time.monotonic()
    with out.open("wb") as stdout, err.open("wb") as stderr:
        process = subprocess.Popen([sys.executable, "-m", "gov.cli.main", *argv], cwd=str(box.elsewhere),
                                   env=support.child_env(box, path), stdin=subprocess.DEVNULL, stdout=stdout,
                                   stderr=stderr, start_new_session=True)
        try:
            process.wait(timeout=CUT_S)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            marker = folder / STOPPED / MARKER
            starts = marker.read_text(encoding="utf-8").splitlines() if marker.exists() else []
            raise AssertionError(f"gov {' '.join(argv)} was still running after {CUT_S:.0f} s (bound: "
                                 f"{BOUND_S:.0f} s) with the code index stopped; the code tool was started "
                                 f"{len(starts)} time(s): {starts[:3]}") from None
    taken = time.monotonic() - started
    run = support.Run(tuple(argv), process.returncode, out.read_text(encoding="utf-8", errors="replace"),
                      err.read_text(encoding="utf-8", errors="replace"))
    assert taken < BOUND_S, f"gov impact took {taken:.1f} s, more than {BOUND_S:.0f} s\n{run.describe()}"
    return run


def assert_code_graph_not_loaded(run, stopped):
    """Exit 0, the five groups, the code graph reported as not loaded, ``complete: false``, the tool never started."""
    found = support.assessment(run)
    show = run.describe()
    assert not stopped.starts(), f"the code tool was started for a record-only change: {stopped.starts()}\n{show}"
    assert found["graphs"]["code"].startswith(NOT_LOADED), \
        f"`graphs.code` does not begin with {NOT_LOADED!r}: {found['graphs']['code']!r}\n{show}"
    assert found["graphs"]["record"] == support.GRAPH_OK, f"`graphs.record`: {found['graphs']}\n{show}"
    assert found["complete"] is False, f"the report reads as complete although the code graph was not loaded\n{show}"
    return found


# --------------------------------------------------------------------------
# IM-1: a record-only change never starts, asks or waits on the code index
# --------------------------------------------------------------------------

# change -> what must still be listed from the record graph, as (kind, id). None of these reaches a symbol.
RECORD_ONLY = {
    "decision": ((support.WIDE,),
                 [("specifications", i) for i in support.WIDE_SPECS] + [("tickets", i) for i in support.WIDE_TICKETS]),
    "specification": ((support.UNRELATED[0],),
                      [("decisions", support.UNRELATED[1]), ("tests", support.UNRELATED[3])]),
    "ticket": ((support.UNRELATED[2],), []),
    "register-entry": ((support.ENTRY_DECISION,), [("tickets", support.ENTRY_TICKET)]),
}


@pytest.mark.parametrize("kind", list(RECORD_ONLY))
def test_a_record_only_change_is_answered_without_the_code_index(built, base, box, stopped, tmp_path, kind):
    change, listed = RECORD_ONLY[kind]
    root = a_project(base, box, tmp_path / "repo")
    run = bounded(root, change, box, stopped.path, tmp_path)
    found = assert_code_graph_not_loaded(run, stopped)
    assert [entry["id"] for entry in found["change"]] == list(change), f"`change`: {found['change']}"
    for group, record_id in listed:
        assert support.where(found, record_id) == [(group, "record")], \
            f"{record_id}: {support.where(found, record_id)}\n{run.describe()}"
    assert found["affected"]["code"] == [], f"`affected.code`: {found['affected']['code']}"


def test_a_name_shaped_like_a_record_id_is_a_gap_and_never_looked_up_as_a_symbol(built, base, box, stopped, tmp_path):
    """A decision constrains three names shaped like record ids that no record holds."""
    records = {f"docs/adr/{NAMES_NO_RECORD}.md": support.decision(NAMES_NO_RECORD, constrains=list(ID_SHAPED))}
    root = a_project(base, box, tmp_path / "repo", records)
    run = bounded(root, (NAMES_NO_RECORD,), box, stopped.path, tmp_path)
    found = assert_code_graph_not_loaded(run, stopped)
    for name in ID_SHAPED:
        gaps = [gap for gap in found["gaps"] if isinstance(gap, dict) and gap.get("id") == name]
        assert gaps and any("UNRESOLVED" in support.text_of(gap) for gap in gaps), \
            f"{name}, which no record holds, is not an UNRESOLVED gap: {found['gaps']}\n{run.describe()}"


def test_an_unknown_id_shaped_change_is_refused_without_the_code_index(built, base, box, stopped, tmp_path):
    root = a_project(base, box, tmp_path / "repo")
    run = bounded(root, ("DEC-1204",), box, stopped.path, tmp_path)
    support.assert_refused(run, "DEC-1204")
    assert not stopped.starts(), \
        f"the code tool was started for a name shaped like a record id: {stopped.starts()}\n{run.describe()}"


def test_a_record_that_names_a_symbol_still_loads_the_code_graph_and_ends(built, base, box, stopped, tmp_path):
    """G-16: DEC-001 constrains the symbol w37_apply, so the code tool is asked; stopped, it never reads as read."""
    root = a_project(base, box, tmp_path / "repo")
    run = bounded(root, (support.CHANGED,), box, stopped.path, tmp_path)
    document = support.envelope(run)
    show = run.describe()
    assert stopped.starts(), f"{support.CHANGED} names {support.SYMBOL} and the code graph was not loaded\n{show}"
    if document["ok"] is True:
        found = support.assert_incomplete(run, "code")
        said = found["graphs"]["code"]
    else:
        support.assert_refused(run)
        said = support.text_of(document["error"])
    assert not said.startswith(NOT_LOADED), f"the code graph reads as not loaded: {said!r}\n{show}"
    assert any(name in said.lower() for name in INDEX_NAMES), f"the code index is not named: {said!r}\n{show}"


# --------------------------------------------------------------------------
# IM-2: a change that needs code, with the index stopped
# --------------------------------------------------------------------------

def assert_refused_naming_the_code_index(run):
    """Exit code not 0, ``IMPACT_CHANGE_UNKNOWN``, a message that names the code index. Returns the error."""
    support.assert_refused(run)
    error = support.envelope(run)["error"]
    show = run.describe()
    assert error["code"] == UNKNOWN_CODE, f"the refusal's code is {error['code']!r}, not {UNKNOWN_CODE}\n{show}"
    message = str(error.get("message", "")).lower()
    assert any(name in message for name in INDEX_NAMES), \
        f"the refusal's message does not name the code index: {error.get('message')!r}\n{show}"
    return error


@pytest.mark.parametrize("change", [support.CODE_REL, support.SYMBOL], ids=["source-path", "symbol-name"])
def test_a_change_that_needs_code_with_a_hung_index_is_refused_naming_it(built, code_base, box, stopped, tmp_path,
                                                                         change):
    root = a_project(code_base, box, tmp_path / "repo")
    run = bounded(root, (change,), box, stopped.path, tmp_path)
    show = run.describe()
    error = assert_refused_naming_the_code_index(run)
    assert stopped.starts(), f"{change} needs code and the code tool was never started\n{show}"
    graphs = (error.get("details") or {}).get("graphs") or {}
    state = str(graphs.get("code", ""))
    assert state.startswith(UNAVAILABLE + ":"), \
        f"`details.graphs.code` does not begin with '{UNAVAILABLE}:': {state!r}\n{show}"
    assert any(name in state.lower() for name in INDEX_NAMES), \
        f"`details.graphs.code` names neither the code index nor {support.TOOL}: {state!r}\n{show}"


def test_a_source_path_with_the_code_tool_absent_is_refused_naming_the_code_index(built, code_base, box, tmp_path):
    root = a_project(code_base, box, tmp_path / "repo")
    run = bounded(root, (support.CODE_REL,), box, box.bare, tmp_path)          # ``git`` alone on PATH
    assert_refused_naming_the_code_index(run)
