"""W2-129 S16 (DEC-1088 (6), standing): ticket changes.

A commit in the range that changes a closed ticket's file (its status closed before the commit) is
CLOSED_TICKET_EDITED; a commit that changes an open or in-progress ticket's title, kpis, allowed_paths, depends_on or
acceptance_tests with no decision id in the changed lines nor in its ``Implements:`` or ``Decided-by:`` trailers is
TICKET_CHANGE_UNMARKED; a change of status, assignee or links alone is no finding. Each names the ticket, the commit
and the field, the role orchestrator, and is listed only when its commit is in the range.

Each case works on its own copy of repository A. ``prepare`` first commits, outside the range, the fields the cases
change (DAEO-t005's ``assignee``, ``links``, ``depends_on``, ``allowed_paths`` and a KPI line with no bracket), marked
with ``Implements: DEC-100``; the range then starts at its head. The guards also plant one unmarked title change to
DAEO-t004 (the control), so a tool that reports nothing fails them too.
"""

from __future__ import annotations

import re

import pytest
import w2_129_support as support

S16 = ("CLOSED_TICKET_EDITED", "TICKET_CHANGE_UNMARKED")
T002 = ".tickets/DAEO-t002.md"  # closed since the records commit
T004 = ".tickets/DAEO-t004.md"  # open
T005 = ".tickets/DAEO-t005.md"  # in progress
UNMARKED = {"Task": "DAEO-t005", "Role": "orchestrator"}

# field -> (the line before, the line after unmarked, the line after with the mark in it)
FIELDS = {
    "kpis": ("  - 'The notes stay short.'\n",
             "  - 'The notes stay short and plain.'\n",
             "  - 'The notes stay short and plain [re-worded, DEC-113]'\n"),
    "allowed_paths": ("- src/app/**\n",
                      "- src/app/**\n- docs/notes.md\n",
                      "- src/app/**\n- docs/notes.md  # [added, DEC-113]\n"),
    "depends_on": ("depends_on: [DAEO-t002]\n",
                   "depends_on: [DAEO-t002, DAEO-t004]\n",
                   "depends_on: [DAEO-t002, DAEO-t004]  # [added, DEC-113]\n"),
    "title": ("title: 'The planted clean ticket'\n",
              "title: 'The planted clean ticket, re-titled'\n",
              "title: 'The planted clean ticket, re-titled [re-worded, DEC-113]'\n"),
    "acceptance_tests": ("  path: tests/acceptance/W2-905/\n",
                         "  path: tests/acceptance/W2-905/cases/\n",
                         "  path: tests/acceptance/W2-905/cases/  # [re-worded, DEC-113]\n"),
}

# field -> (the line before, the line after): the changes that are never a finding on their own
ALONE = {
    "status": ("status: in_progress\n", "status: blocked\n"),
    "assignee": ("assignee: engineer\n", "assignee: product-spec\n"),
    "links": ("links: []\n", "links: [DAEO-t004]\n"),
}


def edit(repo, rel: str, old: str, new: str) -> None:
    path = repo / rel
    text = path.read_text()
    assert old in text, (rel, old)
    path.write_text(text.replace(old, new, 1))


def prepare(shas: dict) -> str:
    """Commits DAEO-t005's extra fields (marked, outside the range); the range's base, the new head."""
    repo = shas["repo"]
    edit(repo, T005, "status: in_progress\n", "status: in_progress\nassignee: engineer\nlinks: []\n")
    edit(repo, T005, "sources:\n", "depends_on: [DAEO-t002]\nallowed_paths:\n- src/app/**\nsources:\n")
    edit(repo, T005, "  - 'The base rule holds [DEC-100]'\n",
         "  - 'The base rule holds [DEC-100]'\n  - 'The notes stay short.'\n")
    return support.commit(repo, "DAEO-t005's fields", {"Task": "DAEO-t005", "Implements": "DEC-100",
                                                       "Role": "orchestrator"}, 10, [T005])


def control(shas: dict, day: int) -> str:
    """An unmarked title change to the open DAEO-t004; its sha."""
    repo = shas["repo"]
    edit(repo, T004, "title: 'The planted open ticket'\n", "title: 'The planted open ticket, re-titled'\n")
    return support.commit(repo, "DAEO-t004's title", {"Task": "DAEO-t004", "Role": "orchestrator"}, day, [T004])


def s16(out: support.Output) -> list[support.Finding]:
    """The listed S16 lines (``support.CODES`` holds S1 to S15's codes only)."""
    return [support.Finding(line) for line in out.lines[1:] if line.split(" ", 1)[0] in S16]


def names_commit(finding: support.Finding, sha: str) -> bool:
    """Whether the first field names the commit by its sha or a prefix of 7 or more."""
    return any(sha.startswith(token)
               for token in re.findall(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])", finding.head))


def names_field(finding: support.Finding, field: str) -> bool:
    return bool(re.search(rf"(?<![\w-]){re.escape(field)}(?![\w-])", finding.head))


def of(out: support.Output, code: str, ticket: str, sha: str) -> list[support.Finding]:
    return [f for f in s16(out) if f.code == code and f.names(ticket) and names_commit(f, sha)]


def check(found: list, out: support.Output, repo, rel: str, field: str) -> None:
    """One finding at least, each at the ticket's file and a line of it, naming the field, the role orchestrator."""
    assert found, out.text()
    lines = len(support.head_text(repo, rel).split("\n"))
    for finding in found:
        assert finding.path == rel and finding.line is not None and 1 <= finding.line <= lines, finding
        assert "orchestrator" in finding.role and finding.fix, finding
    assert any(names_field(f, field) for f in found), found


@pytest.mark.parametrize("field", list(FIELDS))
def test_s16_an_unmarked_change_to_an_in_progress_ticket_is_ticket_change_unmarked(fresh, field):
    repo = fresh["repo"]
    base = prepare(fresh)
    before, after, _ = FIELDS[field]
    edit(repo, T005, before, after)
    sha = support.commit(repo, f"DAEO-t005's {field}", UNMARKED, 11, [T005])
    out = support.links(repo, "--since", base)
    check(of(out, "TICKET_CHANGE_UNMARKED", "DAEO-t005", sha), out, repo, T005, field)
    assert out.code == 1, out.text()


def test_s16_an_unmarked_change_to_an_open_ticket_is_ticket_change_unmarked(fresh):
    repo = fresh["repo"]
    base = prepare(fresh)
    sha = control(fresh, 11)
    out = support.links(repo, "--since", base)
    check(of(out, "TICKET_CHANGE_UNMARKED", "DAEO-t004", sha), out, repo, T004, "title")


def test_s16_the_role_is_orchestrator_whatever_the_commit_s_role(fresh):
    repo = fresh["repo"]
    base = prepare(fresh)
    before, after, _ = FIELDS["kpis"]
    edit(repo, T005, before, after)
    sha = support.commit(repo, "DAEO-t005's kpis", {"Task": "DAEO-t005", "Role": "engineer"}, 11, [T005])
    out = support.links(repo, "--since", base)
    check(of(out, "TICKET_CHANGE_UNMARKED", "DAEO-t005", sha), out, repo, T005, "kpis")


def test_s16_two_fields_in_one_commit_are_each_named(fresh):
    repo = fresh["repo"]
    base = prepare(fresh)
    for field in ("title", "depends_on"):
        edit(repo, T005, *FIELDS[field][:2])
    sha = support.commit(repo, "DAEO-t005's title and dependencies", UNMARKED, 11, [T005])
    out = support.links(repo, "--since", base)
    found = of(out, "TICKET_CHANGE_UNMARKED", "DAEO-t005", sha)
    check(found, out, repo, T005, "title")
    assert any(names_field(f, "depends_on") for f in found), found


@pytest.mark.parametrize("mark", ["in-the-line", "implements", "decided-by"])
@pytest.mark.parametrize("field", list(FIELDS))
def test_s16_guard_a_change_marked_with_its_decision_gives_no_finding(fresh, field, mark):
    repo = fresh["repo"]
    base = prepare(fresh)
    before, after, marked = FIELDS[field]
    trailers = dict(UNMARKED)
    if mark == "in-the-line":
        edit(repo, T005, before, marked)
    else:
        edit(repo, T005, before, after)
        trailers["Implements" if mark == "implements" else "Decided-by"] = "DEC-113"
    sha = support.commit(repo, f"DAEO-t005's {field}", trailers, 11, [T005])
    seen = control(fresh, 12)
    out = support.links(repo, "--since", base)
    assert of(out, "TICKET_CHANGE_UNMARKED", "DAEO-t004", seen), out.text()
    assert not [f for f in s16(out) if f.names("DAEO-t005") or names_commit(f, sha)], out.text()


@pytest.mark.parametrize("fields", [["status"], ["assignee"], ["links"], ["status", "assignee", "links"]],
                         ids=["status", "assignee", "links", "all-three"])
def test_s16_guard_status_assignee_or_links_alone_give_no_finding(fresh, fields):
    repo = fresh["repo"]
    base = prepare(fresh)
    for field in fields:
        edit(repo, T005, *ALONE[field])
    sha = support.commit(repo, f"DAEO-t005's {', '.join(fields)}", UNMARKED, 11, [T005])
    seen = control(fresh, 12)
    out = support.links(repo, "--since", base)
    assert of(out, "TICKET_CHANGE_UNMARKED", "DAEO-t004", seen), out.text()
    assert not [f for f in s16(out) if f.names("DAEO-t005") or names_commit(f, sha)], out.text()


CLOSED_EDITS = {
    "title-unmarked": ("title", "title: 'The planted closed ticket'\n",
                       "title: 'The planted closed ticket, re-titled'\n", UNMARKED),
    "kpis-with-implements": ("kpis", "  - 'The base rule holds [DEC-100]'\n",
                             "  - 'The base rule holds [DEC-100]'\n  - 'The notes stay short [added, DEC-113]'\n",
                             {**UNMARKED, "Implements": "DEC-113"}),
    "status-reopened": ("status", "status: closed\n", "status: in_progress\n", UNMARKED),
}


@pytest.mark.parametrize("case", list(CLOSED_EDITS))
def test_s16_a_commit_that_edits_a_closed_ticket_is_closed_ticket_edited(fresh, case):
    """A closed ticket is never edited: a decision mark does not excuse it, nor is a status change exempt."""
    repo = fresh["repo"]
    base = prepare(fresh)
    field, before, after, trailers = CLOSED_EDITS[case]
    edit(repo, T002, before, after)
    sha = support.commit(repo, f"DAEO-t002's {field}", {**trailers, "Task": "DAEO-t002"}, 11, [T002])
    out = support.links(repo, "--since", base)
    check(of(out, "CLOSED_TICKET_EDITED", "DAEO-t002", sha), out, repo, T002, field)
    assert out.code == 1, out.text()


def test_s16_a_ticket_closed_in_the_range_is_closed_ticket_edited_only_by_the_commits_after(fresh):
    """The status before each commit decides: the closing commit is no finding; the edit after it is."""
    repo = fresh["repo"]
    base = prepare(fresh)
    edit(repo, T005, "status: in_progress\n", "status: closed\n")
    closing = support.commit(repo, "close DAEO-t005", UNMARKED, 11, [T005])
    before, after, _ = FIELDS["title"]
    edit(repo, T005, before, after)
    sha = support.commit(repo, "DAEO-t005's title", {**UNMARKED, "Implements": "DEC-113"}, 12, [T005])
    out = support.links(repo, "--since", base)
    check(of(out, "CLOSED_TICKET_EDITED", "DAEO-t005", sha), out, repo, T005, "title")
    assert not [f for f in s16(out) if names_commit(f, closing)], out.text()


def test_s16_a_ticket_change_is_listed_only_when_its_commit_is_in_the_range(fresh):
    repo = fresh["repo"]
    prepare(fresh)
    before, after, _ = FIELDS["kpis"]
    edit(repo, T005, before, after)
    sha = support.commit(repo, "DAEO-t005's kpis", UNMARKED, 11, [T005])
    support.write(repo, "docs/notes.md", "Planted notes, longer.\n")
    support.commit(repo, "the notes again", {"Task": "DAEO-t005", "Implements": "DEC-100", "Role": "orchestrator"},
                   12, ["docs/notes.md"])
    outside = support.links(repo, "--since", sha)
    assert not s16(outside), outside.text()
    inside = support.links(repo, "--since", f"{sha}~1")
    check(of(inside, "TICKET_CHANGE_UNMARKED", "DAEO-t005", sha), inside, repo, T005, "kpis")
