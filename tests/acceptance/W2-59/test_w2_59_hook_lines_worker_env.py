"""W2-59 KPI success 2 in a launched worker's environment: a hook line runs the pin's governance package whatever
import path the session's environment names (DEC-822 item 3 and step 2; the CIT-P review's finding, DEC-136).

``gov launch`` passes its own environment on to the session it starts, and the committed launch form sets
``PYTHONPATH=<worktree>/src`` on that command, so every worker session carries it; Claude Code runs a hook's line
with the session's environment. That variable chooses only the code under test, never the judge (DEC-822 item 3);
the guard and the other hook programs are the judge.

Each line of this repository's ``.rulesync/hooks.jsonc`` is run as the other hook-line cases run it (``sh -c``,
``CLAUDE_PROJECT_DIR`` a temporary project, ``HOME`` a temporary folder holding the link ``.local/bin/gov`` to the
stand-in pin, that folder first on ``PATH``, a decoy ``python3`` next), with the worker's ``PYTHONPATH`` added. The
folder it names holds a ``gov`` package standing for an edit of the code under test: its guard allows every call,
importing it leaves ``tree-gov-<pid>``, and a ``sitecustomize`` beside it leaves ``tree-site-<pid>``.

Never fail open: an inherited variable never turns the pin's refusal into an allow, and with no pin the guard line
still blocks.
"""

from __future__ import annotations

import pytest

import w2_59_support as support

ENTRIES = support.hook_entries()
IDS = [f"{event}[{index}]" for event, index, _ in ENTRIES]


def _entries(events):
    picked = [(i, e) for i, e in zip(IDS, ENTRIES) if e[0] in events]
    return [e for _, e in picked], [i for i, _ in picked]


GUARD, GUARD_IDS = _entries({"preToolUse"})
# The other lines. preCompact's and sessionStart's programs add the project's own ``src`` to their import path
# when that folder exists (row W2-M389, deferred to W2-10): for them the worker's path names a folder outside the
# project, so only what the line controls is measured. subagentStop's program imports no governance package: its
# case reads the import path itself (the ``sitecustomize`` marker) and the pin's interpreter.
OTHERS, OTHER_IDS = _entries({"postToolUse", "postToolUseFailure", "stop", "subagentStop", "preCompact",
                              "sessionStart"})
PROGRAM_ADDS_SRC = {"preCompact", "sessionStart"}
IMPORTS_NO_GOV = {"subagentStop"}


def _worker(src):
    """The environment a launched worker's session inherited: its ``PYTHONPATH`` names ``src``."""
    return {"PYTHONPATH": str(src)}


# ---------------------------------------------------------------------------------------------------------------
# 1. The guard line
# ---------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("inherits", ["worker-pythonpath", "no-pythonpath"])
@pytest.mark.parametrize("event,index,entry", GUARD, ids=GUARD_IDS)
def test_the_guard_line_refuses_what_the_pin_s_guard_refuses_whatever_the_session_s_import_path(
        event, index, entry, inherits, pin_markers, tmp_path):
    """An engineer's write outside the ticket's paths, which the pin's guard refuses, is refused (exit 2 or a deny
    decision), and the pin's package decided it, not the project's edited guard (which allows everything)."""
    box = support.make_box(tmp_path / "box", pin_markers)
    project, src = support.worker_project(tmp_path, box.markers, src_in_project=True)
    inherited = _worker(src) if inherits == "worker-pythonpath" else {}
    done = support.run_hook_line(entry["command"], event, project, box, inherited=inherited,
                                 payload=support.refused_write(project))
    assert not box.marks("tree-gov-"), (
        f"with the session's environment {inherited}, {event}[{index}] imported the project's own {src}/gov: "
        f"the code under test, not the pin, decided the call\n{done.describe()}")
    assert support.denies(done), (
        f"with the session's environment {inherited}, {event}[{index}] let through a write the pin's guard refuses "
        f"(exit {done.returncode}; only exit 2 or a deny decision blocks)\n{done.describe()}")
    assert pin_markers.marks("pin-gov-"), (
        f"{event}[{index}]'s decision did not come from the pin's installed package ({pin_markers.site / 'gov'})\n"
        f"{done.describe()}")


@pytest.mark.parametrize("event,index,entry", GUARD, ids=GUARD_IDS)
def test_with_a_worker_s_pythonpath_and_no_pin_the_guard_line_still_blocks(event, index, entry, tmp_path):
    """No ``gov`` link and no ``gov`` on ``PATH``, the worker's ``PYTHONPATH`` naming the project's edited guard:
    the call is still blocked, and neither the project's ``src`` nor the ``python3`` first on ``PATH`` stands in
    for the pin."""
    box = support.make_box(tmp_path / "box", None)
    path = f"{box.local_bin}:{box.decoy_bin}:{support.SYSTEM_PATH}"
    project, src = support.worker_project(tmp_path, box.markers, src_in_project=True)
    done = support.run_hook_line(entry["command"], event, project, box, path=path, inherited=_worker(src),
                                 payload=support.refused_write(project))
    assert support.denies(done), (
        f"with no pin and PYTHONPATH={src}, {event}[{index}] lets the call through (exit {done.returncode})\n"
        f"{done.describe()}")
    assert not box.marks("tree-gov-"), (
        f"with no pin, {event}[{index}] fell back to the package the inherited PYTHONPATH names ({src}/gov)\n"
        f"{done.describe()}")
    assert not box.marks("path-python3-"), (
        f"with no pin, {event}[{index}] fell back to the python3 first on PATH\n{done.describe()}")


@pytest.mark.parametrize("event,index,entry", GUARD, ids=GUARD_IDS)
def test_after_the_rollback_with_a_worker_s_pythonpath_the_guard_line_runs_the_editable_install(
        event, index, entry, tmp_path):
    """The owner's rollback (DEC-605: an editable install whose package is found through the user site folder)
    with the worker's ``PYTHONPATH``: the rollback's interpreter and package decide, not the inherited path's.
    A line that drops the inherited path by also dropping the user site folder (``python -I`` or ``-s``) loses
    the rollback's package."""
    box = support.make_box(tmp_path / "box", None)
    rollback = support.install_rollback(box)
    project, src = support.worker_project(tmp_path, box.markers, src_in_project=True)
    done = support.run_hook_line(entry["command"], event, project, box, inherited=_worker(src),
                                 payload=support.refused_write(project))
    assert not box.marks("tree-gov-"), (
        f"after the rollback, with PYTHONPATH={src}, {event}[{index}] imported the inherited path's gov\n"
        f"{done.describe()}")
    assert not box.marks("path-python3-"), (
        f"after the rollback, {event}[{index}] started the python3 first on PATH\n{done.describe()}")
    assert box.marks("rollback-python-"), (
        f"after the rollback, {event}[{index}] did not start the editable install's interpreter with its user site "
        f"folder ({support.REAL_PYTHON}, named by {rollback})\n{done.describe()}")
    assert support.denies(done), (
        f"after the rollback, {event}[{index}] let through a write the guard refuses (exit {done.returncode})\n"
        f"{done.describe()}")


# ---------------------------------------------------------------------------------------------------------------
# 2. The other lines that start a governance program
# ---------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("event,index,entry", OTHERS, ids=OTHER_IDS)
def test_with_a_worker_s_pythonpath_the_line_s_program_runs_the_pin_s_code(
        event, index, entry, pin_markers, tmp_path):
    """With the worker's ``PYTHONPATH``, the program imports the pin's installed package, not the package the
    inherited path names (subagentStop, which imports none: the pin's interpreter starts without the inherited
    folder on its import path)."""
    box = support.make_box(tmp_path / "box", pin_markers)
    project, src = support.worker_project(tmp_path, box.markers, src_in_project=event not in PROGRAM_ADDS_SRC)
    done = support.run_hook_line(entry["command"], event, project, box, inherited=_worker(src))
    assert not box.marks("tree-gov-"), (
        f"with PYTHONPATH={src}, {event}[{index}]'s program imported that folder's gov, not the pin's\n"
        f"{done.describe()}")
    if event in IMPORTS_NO_GOV:
        assert pin_markers.marks("pin-python-"), (
            f"{event}[{index}] did not start the pin's interpreter ({pin_markers.python})\n{done.describe()}")
        assert not box.marks("tree-site-"), (
            f"with PYTHONPATH={src}, {event}[{index}]'s interpreter started with that folder on its import path "
            f"(its sitecustomize ran)\n{done.describe()}")
    else:
        assert pin_markers.marks("pin-gov-"), (
            f"with PYTHONPATH={src}, {event}[{index}]'s program did not import the pin's installed package "
            f"({pin_markers.site / 'gov'})\n{done.describe()}")


# ---------------------------------------------------------------------------------------------------------------
# 3. The variable stays the code under test's (DEC-732)
# ---------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("event,index,entry", GUARD, ids=GUARD_IDS)
def test_a_command_that_sets_pythonpath_itself_is_let_through_and_runs_the_tree_s_code(
        event, index, entry, pin_markers, tmp_path):
    """DEC-732's form, an engineer's ``PYTHONPATH=<worktree>/src python3 ...``, in a worker's session: the pin's
    guard decides it and lets it through, and the command, run with the session's environment, imports the tree's
    package. Whatever the line does with the session's environment, the variable is not taken from the session
    nor refused to the command."""
    box = support.make_box(tmp_path / "box", pin_markers)
    project, src = support.worker_project(tmp_path, box.markers, src_in_project=True)
    command = f"PYTHONPATH={src} python3 -c 'import gov; print(gov.__file__)'"
    payload = {**support.hook_input("preToolUse", project),
               "tool_input": {"command": command, "description": "w259: the code under test"}}
    done = support.run_hook_line(entry["command"], event, project, box, inherited=_worker(src), payload=payload)
    assert not box.marks("tree-gov-"), (
        f"with PYTHONPATH={src}, {event}[{index}] imported the project's own gov to decide the call\n"
        f"{done.describe()}")
    assert pin_markers.marks("pin-gov-"), (
        f"{event}[{index}]'s decision did not come from the pin's installed package\n{done.describe()}")
    assert done.returncode == 0 and not support.denies(done), (
        f"{event}[{index}] refused a command that sets PYTHONPATH to the code under test (DEC-732)\n"
        f"{done.describe()}")
    env = support.session_env(project, box, inherited=_worker(src))
    ran = support.run(["sh", "-c", command], cwd=project, env=env)
    assert ran.returncode == 0 and ran.stdout.strip() == str(src / "gov" / "__init__.py"), (
        f"the command that sets PYTHONPATH={src} itself did not run the tree's code\n{ran.describe()}")
