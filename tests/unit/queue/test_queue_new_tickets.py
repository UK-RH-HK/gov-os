"""W2-201 fix X4 (DEC-1219 (5)): a new ticket file that is not a feature is named at the landing, never refused
(``gov.queue.checks.ticket_notices``), on planted branches."""
from __future__ import annotations

import yaml

from gov.queue import checks

from queue_support import TICKET, ticket_text

VERIFY = {"kpis": {"success": [{"id": "S1", "text": "it works", "verify": "a test"}]}}


def _notices(project, branch):
    return checks.ticket_notices(project.root, project.sha("main"), project.sha(branch))


def _codes(found):
    return [(n["id"], n["code"], n["notice"]) for n in found]


def test_a_new_ticket_with_no_kpi_verify_and_no_body_names_both(project):
    project.branch("a", {".tickets/T-new.md": "---\n" + yaml.safe_dump({"id": "T-new", "status": "open"}) + "---\n"})
    assert _codes(_notices(project, "a")) == [(
        "T-new", "NEW_TICKET_NOT_FEATURE",
        "NEW_TICKET_NOT_FEATURE T-new: no kpis.success line with a verify; no spec (the ticket's body is empty)")]


def test_a_new_feature_gives_none_in_either_kpi_form(project):
    project.branch("a", {".tickets/T-new.md": ticket_text("T-new", "W-9", **VERIFY)})
    project.branch("b", {".tickets/T-str.md": ticket_text("T-str", "W-8", kpis={"success": [
        "S1 it works. Verify: a test."]})})
    assert _notices(project, "a") == [] and _notices(project, "b") == []


def test_a_blank_verify_or_a_string_without_verify_is_no_kpi(project):
    project.branch("a", {".tickets/T-new.md": ticket_text("T-new", "W-9", kpis={"success": [
        {"id": "S1", "verify": "  "}, "S2 it works"]})})
    assert _codes(_notices(project, "a"))[0][2] == "NEW_TICKET_NOT_FEATURE T-new: no kpis.success line with a verify"


def test_a_body_of_white_space_is_no_spec(project):
    text = ticket_text("T-new", "W-9", **VERIFY).replace("# A ticket\n", "\n  \n")
    project.branch("a", {".tickets/T-new.md": text})
    assert _codes(_notices(project, "a"))[0][2] == "NEW_TICKET_NOT_FEATURE T-new: no spec (the ticket's body is empty)"


def test_an_unreadable_front_matter_is_named(project):
    project.branch("a", {".tickets/T-bad.md": "---\nid: [unclosed\n---\n# body\n"})
    project.branch("b", {".tickets/T-none.md": "no front matter here\n"})
    assert _codes(_notices(project, "a"))[0][2] == "NEW_TICKET_NOT_FEATURE T-bad: front matter unreadable"
    assert _codes(_notices(project, "b"))[0][2] == "NEW_TICKET_NOT_FEATURE T-none: front matter unreadable"


def test_an_edit_of_an_existing_ticket_and_other_files_give_none(project):
    project.branch("a", {f".tickets/{TICKET}.md": "---\nid: x\n---\n", ".tickets/notes/T-x.md": "",
                         ".tickets/README.txt": "", "docs/T-y.md": ""})
    assert _notices(project, "a") == []
