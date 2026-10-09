"""Unit tests for the builder where every declared id is an external reference (W1-41; DEC-520, DEC-454)."""

from __future__ import annotations

import pytest

import gov.context as ctx
from gov.cli.errors import GovError
from gov.context import EXTERNAL_REFERENCES_REL

LISTED = ("references:\n"
          "  - id: S0a-G-12\n    location: the archive\n    reason: kept outside\n"
          "  - id: G-10\n    location: the library\n    reason: never a record\n")
CHARTER = {"id": "CH-1", "type": "charter", "status": "ACTIVE", "path": "charter.md"}


def _project(tmp_path, monkeypatch, declared, records=()):
    path = tmp_path / EXTERNAL_REFERENCES_REL
    path.parent.mkdir(parents=True)
    path.write_text(LISTED, encoding="utf-8")
    (tmp_path / "charter.md").write_text("the charter\n", encoding="utf-8")
    monkeypatch.setattr(ctx, "_ticket_mandatory_ids", lambda root, ticket: list(declared))
    monkeypatch.setattr(ctx, "_record_map", lambda root: {r["id"]: r for r in records})
    monkeypatch.setattr(ctx, "_supersedes_edges", lambda root: set())
    monkeypatch.setattr(ctx, "_try_supplementary", lambda root, ticket, remaining: ([], []))
    return tmp_path


@pytest.mark.parametrize("declared", [["S0a-G-12"], ["S0a-G-12", "G-10"]])
def test_a_ticket_whose_declared_ids_are_all_external_is_blocked(tmp_path, monkeypatch, declared):
    with pytest.raises(GovError) as raised:
        ctx.context(_project(tmp_path, monkeypatch, declared), "TK-1")
    assert raised.value.code == "BLOCKED"
    assert raised.value.details == {"ticket": "TK-1", "external": declared}
    message = raised.value.message
    assert "TK-1" in message and "external" in message and "none was read" in message
    assert all(rid in message for rid in declared)


def test_a_dependency_that_was_read_is_not_a_source_that_was_read(tmp_path, monkeypatch):
    project = _project(tmp_path, monkeypatch, ["S0a-G-12", "G-10", "CH-1"], [CHARTER])
    monkeypatch.setattr(ctx, "_ticket_source_ids", lambda root, ticket: ["S0a-G-12", "G-10"])
    with pytest.raises(GovError) as raised:
        ctx.context(project, "TK-1")
    assert (raised.value.code, raised.value.details) == ("BLOCKED", {"ticket": "TK-1", "external": ["S0a-G-12", "G-10"]})


def test_a_record_beside_the_external_ids_is_still_built(tmp_path, monkeypatch):
    project = _project(tmp_path, monkeypatch, ["S0a-G-12", "CH-1", "G-10"], [CHARTER])
    packet = ctx.context(project, "TK-1")
    assert [item["id"] for item in packet["mandatory"]] == ["CH-1"]
    assert [item["id"] for item in packet["external"]] == ["S0a-G-12", "G-10"]
