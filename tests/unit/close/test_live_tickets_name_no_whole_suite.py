"""The live tickets name no whole suite as their acceptance folder (a fix under DAEO-gr7t).

Kind: repository-state (record-reading): it reads this repository's own ``.tickets/``, not a fixture.

A ticket whose acceptance folder is the whole ``tests/`` or ``tests/acceptance/`` tree (or ``tests/unit``, or the
project root) makes every path its ``allowed_paths`` hold select that whole tree, and ``gov close --select`` /
``gov queue --select`` refuse such a selection (``SELECTION_REFUSED: the selection would run the whole of ...``).
"""
from pathlib import Path

from gov.close import select
from gov.tasks.tickets import TICKETS_REL, frontmatter

ROOT = Path(__file__).resolve().parents[3]
WHOLE = {select.FULL_TARGET, select.ACCEPTANCE, "tests/unit", "", "."}


def _whole(folder) -> bool:
    """Whether ``folder`` names a whole suite tree (or the project root) rather than one ticket's folder."""
    text = str(folder).strip()
    while text.startswith("./"):
        text = text[2:]
    return select._norm(text) in WHOLE


def test_no_ticket_with_a_suite_selects_a_whole_tree():
    offenders = [f"{tid}: suite {folder!r}, allowed_paths {paths}"
                 for tid, _, paths, folder, held in select._tickets(ROOT) if held and _whole(folder)]
    assert not offenders, ("tickets whose acceptance folder is a whole tree, so every path they hold selects it "
                           "and the selection is refused:\n" + "\n".join(offenders))


def test_no_ticket_file_declares_a_whole_tree_as_its_acceptance_path():
    offenders = []
    for path in sorted((ROOT / TICKETS_REL).glob("*.md")):
        front = frontmatter(path) or {}
        declared = front.get("acceptance_tests")
        if isinstance(declared, dict) and declared.get("path") is not None and _whole(declared["path"]):
            offenders.append(f"{front.get('id') or path.stem}: acceptance_tests.path {declared['path']!r}, "
                             f"allowed_paths {front.get('allowed_paths') or []}")
    assert not offenders, "ticket files declaring a whole tree as acceptance_tests.path:\n" + "\n".join(offenders)
