"""Builder tests for W2-203: gov close's register reader finds an owner decision that only the archive holds (DEC-136)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.close import history  # noqa: E402

OWNER = "### {} — {}\n- **Status:** ACCEPTED (owner, 2026-11-01)\n- **Decision:** {}\n"


def _project(root: Path, path_map: str) -> Path:
    (root / "governance/project").mkdir(parents=True)
    (root / history.PATH_MAP_REL).write_text(path_map, encoding="utf-8")
    (root / "reg.md").write_text("# Register\n\n" + OWNER.format("DEC-200", "Kept", "the kept text"), encoding="utf-8")
    return root


def test_an_archive_only_entry_is_found_with_its_text_and_the_registers_own_entry_wins(tmp_path):
    root = _project(tmp_path, "decision_register: reg.md\ndecision_register_archive: old.md\n")
    (root / "old.md").write_text(OWNER.format("DEC-100", "Old", "the old text") + "\n"
                                 + OWNER.format("DEC-200", "Kept", "another text"), encoding="utf-8")
    entries = history.register_entries(root, "reg.md")
    assert sorted(entries) == ["DEC-100", "DEC-200"] and len(entries["DEC-200"]) == 1
    assert "the kept text" in entries["DEC-200"][0]
    why, text = history.owner_decision("DEC-100", entries)
    assert why is None and "the old text" in text


def test_no_archive_named_or_readable_adds_nothing(tmp_path):
    for at, path_map in enumerate(("decision_register: reg.md\n",
                                   "decision_register: reg.md\ndecision_register_archive: gone.md\n")):
        (tmp_path / str(at)).mkdir()
        assert sorted(history.register_entries(_project(tmp_path / str(at), path_map), "reg.md")) == ["DEC-200"]
    assert isinstance(history.register_entries(tmp_path / "0", None), str)
