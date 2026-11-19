"""Builder tests for W2-203: a commit citing a decision its tree's archive holds cites a recorded decision (DEC-136)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gov.check import citations  # noqa: E402
from test_citations import Project, project  # noqa: E402,F401

ENTRY = "### {} — A rule\n- **Status:** ACCEPTED\n"


def test_an_archived_id_is_recorded_and_an_id_in_neither_file_is_not(project):  # noqa: F811
    project.configure(decision_register="reg.md", decision_register_archive="old/reg.md")
    project.write("reg.md", ENTRY.format("DEC-200"))
    project.write("old/reg.md", ENTRY.format("DEC-100"))
    commit = project.commit("Under DEC-100, DEC-200 and DEC-999")
    assert citations._configured(project.root) == ("reg.md", None, "old/reg.md")
    assert project.flagged() == [("DECISION_UNRECORDED", commit, "DEC-999")]


def test_a_tree_without_the_archive_has_no_ids_of_it_and_no_finding_of_its_own(project):  # noqa: F811
    project.configure(decision_register="reg.md", decision_register_archive="old/reg.md")
    project.write("reg.md", ENTRY.format("DEC-200"))
    before = project.commit("Under DEC-200 and DEC-100")
    project.write("old/reg.md", ENTRY.format("DEC-100"))
    project.commit("The archive")
    assert project.flagged() == [("DECISION_UNRECORDED", before, "DEC-100")]


def test_an_archive_heading_without_a_status_line_is_recorded_too(project):  # noqa: F811
    project.configure(decision_register="reg.md", decision_register_archive="old/reg.md")
    project.write("reg.md", ENTRY.format("DEC-200"))
    project.write("old/reg.md", "### DEC-027 — An old rule\nA paragraph first.\n")
    project.write("reg2.md", "### DEC-028 — Not the register\nA paragraph.\n")
    project.commit("Under DEC-027")
    assert project.flagged() == []
