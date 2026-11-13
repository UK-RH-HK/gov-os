"""What W2-182's conftest and its guard case share: the README's map of node ids.

The README holds two kinds of table rows: the mapped cases (a run of this folder runs them) and, under the heading
``UNRUN_HEADING``, the revised cases this ticket still guards against a lowering mark but a run of this folder does not
run (line E, moved to W2-185 by DEC-1167 (4)).
"""
import re
from pathlib import Path

README = Path(__file__).with_name("README.md")
ROOT = Path(__file__).resolve().parents[3]
NODE_ID = re.compile(r"`(tests/acceptance/[^`\s]+\.py::[^`\s]+)`")
UNRUN_HEADING = "## Revised, not run here"


def _table_ids(in_unrun_section: bool) -> list[str]:
    """The node ids of the README's table rows, inside or outside the ``UNRUN_HEADING`` section, each once."""
    ids = []
    inside = False
    for line in README.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.strip() == UNRUN_HEADING
        if inside == in_unrun_section and line.lstrip().startswith("|"):
            ids += NODE_ID.findall(line)
    return list(dict.fromkeys(ids))


def mapped_node_ids() -> list[str]:
    """The node ids a run of this folder runs, each once, in the order the README gives them."""
    return _table_ids(False)


def unrun_node_ids() -> list[str]:
    """The revised cases the README names under ``UNRUN_HEADING``: guarded here, not run here."""
    return _table_ids(True)


def guarded_node_ids() -> list[str]:
    """Every revised case the failure-line case scans: the mapped ones, then the unrun ones."""
    return list(dict.fromkeys(mapped_node_ids() + unrun_node_ids()))
