"""Builder tests, a fix at the land of W2-200 beside W2-203 (2026-11-19): a decision the register no longer holds
because it is in the archive (EMERGENCY-2 11.3) is history: the close lists it as no longer standing, marked archived,
and never applies it. An id in neither file is unresolved; nothing refuses (S6 as amended at the land).
"""
from __future__ import annotations

from gov.close import decisions

TICKET = "T-0001"
PATH_MAP = "governance/project/path-map.yaml"
REGISTER = "docs/REG.md"
ARCHIVE = "docs/archive/REG-old.md"


def _entry(number: int, status: str = "ACCEPTED") -> str:
    return f"### DEC-{number} — entry {number}\n- **Status:** {status}\n- **Decision:** text {number}\n\n"


def _project(repo, kept: str, archived: str | None):
    path_map = f"decision_register: {REGISTER}\n" + (f"decision_register_archive: {ARCHIVE}\n" if archived else "")
    files = {PATH_MAP: path_map, REGISTER: "# Register\n\n" + kept}
    if archived:
        files[ARCHIVE] = "> ARCHIVED, READ-ONLY.\n# Register\n\n" + archived
    repo.commit("register and archive", files=files)
    return repo.root


def test_an_archived_decision_of_sources_does_not_refuse_and_is_listed_archived_never_applied(repo):
    root = _project(repo, _entry(110), _entry(150) + _entry(151, "SUPERSEDED") + _entry(110))
    found = decisions.decisions_of(root, TICKET, {"sources": ["DEC-150", "DEC-110"], "decisions": ["DEC-151"],
                                                 "kpis": {"success": ["S1 as DEC-150 says"]}})
    assert found["applied"] == ["DEC-110"]  # the kept entry stands, though the archive holds its old text too
    assert found["not_standing"] == [{"id": "DEC-150", "status": "ARCHIVED"}, {"id": "DEC-151", "status": "ARCHIVED"}]
    assert found["unresolved"] == [] and [item["id"] for item in found["inputs"]] == ["DEC-110"]


def test_an_archived_decision_named_only_in_a_kpi_line_is_archived_not_unresolved(repo):
    root = _project(repo, _entry(110), _entry(150))
    found = decisions.decisions_of(root, TICKET, {"sources": ["DEC-110"], "kpis": {"success": ["S1 as DEC-150 says"]}})
    assert found["not_standing"] == [{"id": "DEC-150", "status": "ARCHIVED"}] and found["unresolved"] == []


def test_an_id_in_neither_the_register_nor_the_archive_is_unresolved_beside_an_archived_one(repo):
    root = _project(repo, _entry(110), _entry(150))
    found = decisions.decisions_of(root, TICKET, {"sources": ["DEC-150", "DEC-999", "DEC-110"]})
    assert found["unresolved"] == ["DEC-999"] and found["applied"] == ["DEC-110"]
    assert found["not_standing"] == [{"id": "DEC-150", "status": "ARCHIVED"}]


def test_without_an_archive_a_missing_decision_is_unresolved(repo):
    root = _project(repo, _entry(110), None)
    assert decisions.decisions_of(root, TICKET, {"sources": ["DEC-150"]})["unresolved"] == ["DEC-150"]
