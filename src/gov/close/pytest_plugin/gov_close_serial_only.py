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
"""

from __future__ import annotations

import os
from pathlib import Path

LIST_REL = "tests/acceptance/serial-only.txt"
PLUGIN = "gov_close_serial_only"
# Names the project's root to the plugin, in the parallel run of a project that declares something.
ROOT_VARIABLE = "GOV_CLOSE_SERIAL_ONLY_OF"


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


def pytest_collection_modifyitems(config, items) -> None:
    root = os.environ.get(ROOT_VARIABLE)
    declared = entries(Path(root)) if root else []
    if not declared:
        return
    kept, apart = [], []
    for item in items:
        # The id as the list gives it, relative to the project's root: pytest's own is relative to its rootdir.
        path = os.path.relpath(str(getattr(item, "path", None) or item.fspath), root).replace(os.sep, "/")
        node = path + "".join(item.nodeid.partition("::")[1:])
        (apart if any(declares(entry, node) for entry in declared) else kept).append(item)
    if apart:
        config.hook.pytest_deselected(items=apart)
        items[:] = kept
