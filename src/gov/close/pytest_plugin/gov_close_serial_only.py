"""The project's list of cases that cannot hold under parallel load, and the pytest plugin that keeps them
out of ``gov close``'s parallel test run (DEC-527).

The list is ``tests/acceptance/serial-only.txt`` of the project: one entry on a line, the beginning of a
pytest node id relative to the project's root, either a test file (every case of it) or ``file::function``
(every parameter set of that function, and no function whose name merely begins with it). Text from `` #`` to
the line's end, and a line that begins with ``#``, is a comment. A project without the list declares nothing.

``gov close`` gives this module to the test runner of its parallel run (``-p gov_close_serial_only``, with this
folder alone added to the run's import path, since the project under test need not have ``gov``). The module
imports nothing but the standard library. pytest's own ``--deselect`` cannot do this: it takes any id that
begins with its argument, so ``file::test_a`` would take ``file::test_a_too`` with it.

The serial run afterwards is given the module too, with the entries of that run: an entry that names no case
ends the run with an error, where pytest itself passes over a file without a case (DEC-549). One exception
(W2-154; DEC-1112 (3), DEC-1061): an entry whose every case another plugin of the run left out (the project's
opt-in lists, reported to ``pytest_deselected``) is "not in this run": the plugin says so, names the entry in the
file ``GOV_CLOSE_SERIAL_ONLY_OUT`` names, and the run does not stop. The plugin never reads an opt-in list itself.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

LIST_REL = "tests/acceptance/serial-only.txt"
PLUGIN = "gov_close_serial_only"
# Names the project's root to the plugin, in the parallel run of a project that declares something.
ROOT_VARIABLE = "GOV_CLOSE_SERIAL_ONLY_OF"
# Names to the plugin, in the serial run afterwards, the entries that run was given, one on a line.
GIVEN_VARIABLE = "GOV_CLOSE_SERIAL_ONLY_GIVEN"
# Names the file the serial run afterwards writes the entries that are "not in this run" to, one on a line.
OUT_VARIABLE = "GOV_CLOSE_SERIAL_ONLY_OUT"

# The node ids (relative to the project's root) that other plugins passed to ``pytest_deselected`` in this run.
_deselected: list[str] = []


def entries(root: Path) -> list[str]:
    """The entries of the project's list, in its order; none when the project has no list."""
    path = Path(root) / LIST_REL
    if not path.is_file():
        return []
    found = ((" " + line).partition(" #")[0].strip() for line in path.read_text(encoding="utf-8").splitlines())
    return list(dict.fromkeys(entry for entry in found if entry))


def declares(entry: str, node: str) -> bool:
    """Whether ``entry`` names the node id ``node``: it is the id, or the id goes on at a boundary of it."""
    return node == entry or (node.startswith(entry) and node[len(entry):].startswith(("::", "[", "/")))


def _node(item, root: str) -> str:
    """The id as the list gives it, relative to the project's root: pytest's own is relative to its rootdir."""
    path = os.path.relpath(str(getattr(item, "path", None) or item.fspath), root).replace(os.sep, "/")
    return path + "".join(item.nodeid.partition("::")[1:])


def pytest_configure(config) -> None:
    _deselected.clear()


def pytest_deselected(items) -> None:
    """Every case another plugin leaves out of the run, as the list gives ids; only the run afterwards uses them."""
    root = os.environ.get(ROOT_VARIABLE)
    if root and os.environ.get(GIVEN_VARIABLE):
        _deselected.extend(_node(item, root) for item in items)


def _say(config, line: str) -> None:
    """``line`` to the run's output: pytest's terminal reporter (the run's capture would swallow a print here)."""
    reporter = config.pluginmanager.get_plugin("terminalreporter")
    if reporter is not None:
        reporter.write_line(line)
    else:
        print(line, file=sys.__stdout__, flush=True)


def pytest_collection_modifyitems(config, items) -> None:
    root = os.environ.get(ROOT_VARIABLE)
    given = os.environ.get(GIVEN_VARIABLE)
    if root and given:  # the run afterwards: an entry that names an existing file without a case ends it
        import pytest

        nodes = [_node(item, root) for item in items]
        empty = [entry for entry in given.split("\n") if not any(declares(entry, node) for node in nodes)]
        # An entry with no collected case whose cases another plugin left out is not in this run (W2-154).
        out = [entry for entry in empty if any(declares(entry, node) for node in _deselected)]
        empty = [entry for entry in empty if entry not in out]
        target = os.environ.get(OUT_VARIABLE)
        if target:
            Path(target).write_text("".join(entry + "\n" for entry in out), encoding="utf-8")
        if empty:
            raise pytest.UsageError(f"no case is named by the entry of {LIST_REL}: {', '.join(empty)}")
        for entry in out:
            _say(config, f"{PLUGIN}: not in this run: {entry}")
        config._gov_close_serial_only_out = bool(out)
        return
    declared = entries(Path(root)) if root else []
    if not declared:
        return
    kept, apart = [], []
    for item in items:
        (apart if any(declares(entry, _node(item, root)) for entry in declared) else kept).append(item)
    if apart:
        config.hook.pytest_deselected(items=apart)
        items[:] = kept


# The hook runs after the project's own (its conftest's opt-in mechanism reports what it leaves out first), and the
# module stays standard-library only: pluggy's marks are set as ``pytest.hookimpl(trylast=True)`` sets them.
pytest_collection_modifyitems.pytest_impl = {"wrapper": False, "hookwrapper": False, "optionalhook": False,
                                             "tryfirst": False, "trylast": True, "specname": None}


def pytest_sessionfinish(session, exitstatus) -> None:
    """A run of which every entry given is out ends 0: pytest itself ends 5 when it runs no case (W2-154)."""
    if getattr(session.config, "_gov_close_serial_only_out", False) and session.exitstatus == 5:
        session.exitstatus = 0
