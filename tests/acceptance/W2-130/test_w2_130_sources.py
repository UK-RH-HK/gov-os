"""S4: tickets linked, open and in-progress tickets only; closed tickets listed in the record, never edited."""

from __future__ import annotations

import re

import pytest

import w2_130_support as s

LIVE = ("open", "in_progress")


def _ticket_at_head(head_tree, ticket: str) -> str | None:
    path = head_tree / ".tickets" / f"{ticket}.md"
    return path.read_text(encoding="utf-8") if path.is_file() else None


def _sources_commit_problems(commit: str, only_tickets: bool) -> list:
    """The ways ``commit`` is not a sources-only commit of open or in-progress tickets."""
    bad = []
    before = s.parent(commit)
    for path, flag in s.changed_files(commit).items():
        if not (path.startswith(".tickets/") and path.endswith(".md")):
            if only_tickets:
                bad.append((path, "a file that is not .tickets/*.md"))
            continue
        old, new = s.show(before, path), s.show(commit, path)
        if flag != "M" or old is None or new is None:
            bad.append((path, f"a ticket file {flag}, not modified"))
            continue
        if s.ticket_status(old) not in LIVE:
            bad.append((path, f"status {s.ticket_status(old)} at the parent: only open or in-progress tickets"))
        delta = s.ticket_delta(old, new)
        if not delta["same_keys"] or delta["fields"] - {"sources"} or delta["body"]:
            bad.append((path, f"changes {sorted(delta['fields'] - {'sources'})} or the body or the field order"))
        if not set(s.ticket_sources(old)) <= set(s.ticket_sources(new)):
            bad.append((path, "removes an id from sources:"))
    return bad


def _linked(record) -> dict:
    """``w2-130:dec-1123-linked`` as ``{ticket id: [{id, form, via}]}``, its shape checked."""
    data = record.data("dec-1123-linked")
    assert isinstance(data, dict), "w2-130:dec-1123-linked is not a mapping ticket id -> list of {id, form, via}"
    for ticket, items in data.items():
        assert isinstance(items, list) and items, f"{ticket}: not a non-empty list"
        for item in items:
            assert isinstance(item, dict) and all(isinstance(item.get(k), str) for k in ("id", "form", "via")), (
                f"{ticket}: {item!r} is not {{id, form, via}} with string values")
            assert item["form"] in s.LINK_FORMS, f"{ticket}: {item['id']} has form {item['form']!r}, not one of {s.LINK_FORMS}"
    return data


def _linked_pairs(linked: dict) -> set:
    return {(f".tickets/{ticket}.md", item["id"]) for ticket, items in linked.items() for item in items}


def _less(by_path: dict, linked: dict) -> dict:
    """``{path: sorted ids}`` of ``by_path`` without the (ticket, id) pairs ``linked`` lists and without empty entries."""
    pairs = _linked_pairs(linked)
    kept = {path: sorted(i for i in ids if (path, i) not in pairs) for path, ids in by_path.items()}
    return {path: ids for path, ids in kept.items() if ids}


def test_s4_every_unlinked_id_on_an_open_or_in_progress_ticket_at_head_is_listed_with_its_dec_1123_2_form(
        record, head_findings, head_tree):
    linked = _linked(record)
    listed = {(ticket, item["id"]) for ticket, items in linked.items() for item in items}
    unlinked = {(ticket, ident) for ticket, ids in s.unlinked_on_live(head_findings, head_tree).items() for ident in ids}
    left = sorted(unlinked - listed)
    assert not left, f"{len(left)} UNLINKED_ID on open or in-progress tickets that dec-1123-linked does not list: {left[:6]}"


def test_s4_each_dec_1123_linked_entry_is_of_its_form_at_head(record, head_findings, head_tree):
    linked = _linked(record)
    bad = [(ticket, item["id"], item["form"], problem) for ticket, items in linked.items() for item in items
           if (problem := s.linked_form_problem(head_tree, ticket, item, head_findings))]
    assert not bad, f"{len(bad)} entries are not of their form at HEAD: {bad[:4]}"


def test_s4_dec_1123_linked_lists_only_unlinked_ids_gov_links_reports_at_head_on_open_or_in_progress_tickets(
        record, head_findings, head_tree):
    linked = _linked(record)
    unlinked = s.unlinked_on_live(head_findings, head_tree)
    listed = [(ticket, item["id"]) for ticket, items in linked.items() for item in items]
    assert len(listed) == len(set(listed)), "dec-1123-linked lists an id twice for one ticket"
    extra = sorted(pair for pair in listed if pair[1] not in unlinked.get(pair[0], set()))
    assert not extra, (f"{len(extra)} entries are no UNLINKED_ID gov links reports at HEAD on an open or in-progress "
                       f"ticket: {extra[:6]}")


def test_s4_the_record_names_e12f8a30c_and_at_most_one_follow_up_as_the_sources_commits(record):
    commits = record.commit_list("sources")
    assert commits[0] == s.full(s.FIRST), "commits.sources must start with e12f8a30c"
    assert len(commits) <= 2, f"commits.sources holds {len(commits)} commits: e12f8a30c and at most one follow-up"
    assert len(set(commits)) == len(commits)


@pytest.mark.parametrize("commit", [s.FIRST])
def test_s4_e12f8a30c_changes_only_the_sources_field_of_tickets_open_or_in_progress_at_its_parent(commit):
    assert not _sources_commit_problems(commit, only_tickets=False)


def test_s4_the_follow_up_sources_commit_changes_only_sources_of_live_tickets_and_no_other_file(record):
    follow = record.commit_list("sources")[1:]
    bad = [(c[:12], _sources_commit_problems(c, only_tickets=True)) for c in follow]
    assert all(not problems for _, problems in bad), f"{bad}"


@pytest.mark.parametrize("commit", [s.FIRST])
def test_s4_the_ids_e12f8a30c_adds_equal_gov_links_propose_sources_at_its_parent(commit, propose_sources_at):
    added = {path: sorted(ids) for path, ids in s.sources_added(commit).items()}
    proposed = {path: sorted(ids) for path, ids in propose_sources_at(commit).items()}
    assert added == proposed, (f"differ on tickets: {sorted(set(added) ^ set(proposed))[:5]}; "
                               f"{sum(1 for p in added if added[p] != proposed.get(p))} with other ids")


def test_s4_the_b1_patch_in_the_record_equals_the_ids_e12f8a30c_added(record):
    patch = {path: sorted(ids) for path, ids in s.patch_source_ids(record.block("patch-b1", "diff")).items()}
    added = {path: sorted(ids) for path, ids in s.sources_added(s.FIRST).items()}
    assert patch == added


def test_s4_the_follow_up_ids_equal_patch_sources_2_and_gov_links_propose_sources_at_its_parent_less_the_forms(
        record, propose_sources_at):
    linked = _linked(record)
    patch = _less(s.patch_source_ids(record.block("patch-sources-2", "diff")), linked)
    follow = record.commit_list("sources")[1:]
    assert follow, "commits.sources names no follow-up commit, yet patch-sources-2 exists"
    added = {path: sorted(ids) for path, ids in s.sources_added(follow[0]).items() if ids}
    assert patch == added, "the ids the follow-up adds differ from patch-sources-2 less the dec-1123-linked pairs"
    assert added == _less(propose_sources_at(follow[0]), linked), (
        "the ids the follow-up adds differ from gov links --propose-sources at its parent less the dec-1123-linked pairs")


def test_s4_outside_the_sources_commits_a_cleanup_commit_adds_to_sources_only_dec_1098_and_dec_1088_on_this_ticket(
        record):
    other = [c for c in record.commit_list("cleanup") if c not in record.commit_list("sources")]
    assert s.full(s.SECOND) in other, "commits.cleanup lacks c4420040f"
    for commit in other:
        added = {path: sorted(ids) for path, ids in s.sources_added(commit).items()}
        expected = {s.TICKET: ["DEC-1088", "DEC-1098"]} if commit == s.full(s.SECOND) else {}
        assert added == expected, f"{commit[:12]} adds {added} to sources:"


def test_s4_c4420040f_adds_to_sources_only_dec_1098_and_dec_1088_on_this_ticket():
    added = {path: sorted(ids) for path, ids in s.sources_added(s.SECOND).items()}
    assert added == {s.TICKET: ["DEC-1088", "DEC-1098"]}


@pytest.mark.parametrize("commit", [s.FIRST, s.SECOND])
def test_s4_no_closed_ticket_is_changed_by_e12f8a30c_or_c4420040f(commit):
    before = s.parent(commit)
    closed = [p for p in s.ticket_changes(commit) if s.ticket_status(s.show(before, p) or "") == "closed"]
    assert not closed, f"closed tickets changed: {closed}"


def test_s4_no_clean_up_commit_the_record_names_changes_a_ticket_closed_at_its_parent(record):
    bad = []
    for commit in record.commit_list("cleanup"):
        before = s.parent(commit)
        bad += [(commit[:12], p) for p in s.ticket_changes(commit)
                if s.ticket_status(s.show(before, p) or "") == "closed"]
    assert not bad, f"{bad[:5]}"


def test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack(record, head_findings, head_tree):
    data = record.data("closed-missing")
    assert isinstance(data, dict), "w2-130:closed-missing is not a mapping ticket -> ids"
    expected = {}
    for finding in head_findings:
        if finding["code"] == "UNLINKED_ID" and finding["path"].startswith(".tickets/"):
            ticket = finding["ids"][1]
            if s.ticket_status(_ticket_at_head(head_tree, ticket) or "") == "closed":
                expected.setdefault(ticket, set()).add(finding["ids"][0])
    for ticket, ids in data.items():
        assert isinstance(ids, list) and ids and all(isinstance(i, str) for i in ids), f"{ticket}: not a non-empty list"
        text = _ticket_at_head(head_tree, ticket)
        assert text is not None and s.ticket_status(text) == "closed", f"{ticket} is not a closed ticket"
        assert not set(ids) & set(s.ticket_sources(text)), f"{ticket}: lists an id its sources: already holds"
    assert {t: set(i) for t, i in data.items()} == expected, "closed-missing differs from gov links' UNLINKED_ID on closed tickets"


def test_s4_no_record_lists_per_ticket_ids_that_name_no_record(record, head_findings, head_tree):
    data = record.data("no-record")
    assert isinstance(data, dict), "w2-130:no-record is not a mapping ticket -> ids"
    headings = set(re.findall(r"(?m)^### (DEC-\d+)\b", (head_tree / s.REGISTER).read_text(encoding="utf-8")))
    stems = {p.stem for p in (head_tree / ".tickets").glob("*.md")}
    for ticket, ids in data.items():
        assert isinstance(ids, list) and ids and all(isinstance(i, str) for i in ids), f"{ticket}: not a non-empty list"
        text = _ticket_at_head(head_tree, ticket)
        assert text is not None, f"{ticket} is no ticket"
        for ident in ids:
            assert ident not in headings and ident not in stems, f"{ticket}: {ident} names a record"
            assert ident in text, f"{ticket}: {ident} is in neither its brackets nor its sources"
    named = {(f["ids"][1], f["ids"][0]) for f in head_findings if f["code"] == "UNKNOWN_ID"
             and f["path"].startswith(".tickets/") and not f["ids"][0].startswith("tests/")}
    left = [(t, i) for t, i in named if i not in data.get(t, [])]
    assert not left, f"gov links reports unknown ids the record does not list per ticket: {left[:5]}"
