"""Builder tests for W2-203: gov links counts an archived decision id among the ids that exist (DEC-136)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gov.links import check  # noqa: E402
from test_links import PATH_MAP, _plant, _ticket  # noqa: E402

OLD = "old/reg.md"


def test_an_archived_id_is_known_without_a_status_and_an_id_in_neither_file_is_unknown(tmp_path):
    root = _plant(tmp_path, {
        "governance/project/path-map.yaml": PATH_MAP + f"decision_register_archive: {OLD}\n",
        OLD: "### DEC-050: An old rule\n**Status:** SUPERSEDED\n\nOld.\n",
        ".tickets/T-aaaa.md": _ticket("T-aaaa", "open", ["DEC-050", "DEC-999"])})
    repo = check._Repo(root)
    assert "DEC-050" in repo.known and "DEC-050" not in repo.status and "DEC-050" not in repo.entry
    assert "DEC-999" not in repo.known
