"""W2-174 S4 and F1: the answers file is checked before anything is written; all or nothing (README)."""

from __future__ import annotations

import pytest

import w2_174_support as s

CLAUSE = s.CLAUSE


def _fixture(repo) -> dict:
    """Four tickets: two open or in progress with lines lacking a verify, a closed one with a line lacking, and one
    with every line verified. Returns the good answers (every missing line answered)."""
    repo.ticket("DAEO-ok01", "W2-911", "open",
                [s.lacking("The first has a first line [DEC-1]."), s.lacking("The first has a second line [DEC-1].")],
                [s.mapping("The first never crashes [DEC-1].", "a unit test of the first")])
    repo.ticket("DAEO-ok02", "W2-912", "in_progress",
                [s.lacking("The second has a line [DEC-1].")], [s.lacking("The second never crashes [DEC-1].")])
    repo.ticket("DAEO-cl01", "W2-913", "closed", [s.lacking("The closed one has a line [DEC-1].")],
                [s.verified("The closed one never crashes [DEC-1].")])
    repo.ticket("DAEO-vf01", "W2-914", "open", [s.verified("The verified one has a line [DEC-1].")],
                [s.verified("The verified one never crashes [DEC-1].")])
    return {"DAEO-ok01": {"S1": f"{CLAUSE} (first S1)", "S2": f"{CLAUSE} (first S2)"},
            "DAEO-ok02": {"S1": f"{CLAUSE} (second S1)", "F1": f"{CLAUSE} (second F1)"}}


def _refused(repo, answers: dict | None = None, text: str | None = None, name: str = "answers.yaml") -> str:
    """Runs the apply through the CLI and through the function; each must refuse with the same code and leave the
    whole tree (repository and answers folder) byte-identical. Returns the code."""
    from gov.cli.errors import GovError

    path = repo.answers_text(text, name) if text is not None else repo.answers(answers, name)
    before = s.snapshot(repo.tmp)
    done = repo.verify_apply(path)
    code = s.refused_code(done)
    assert s.snapshot(repo.tmp) == before, f"a refusal ({code}) through the CLI changed the tree: " \
        f"{s.changed_entries(before, s.snapshot(repo.tmp))}"
    with pytest.raises(GovError) as raised:
        s.verify_pass().apply(repo.root, path, s.SESSION, s.TODAY)
    assert raised.value.code == code, f"the function refuses {raised.value.code}, the CLI {code}"
    assert s.snapshot(repo.tmp) == before, f"a refusal ({code}) through the function changed the tree"
    s.marker_invariant(repo.root)
    return code


def test_s4_the_good_answers_are_applied_to_prove_the_fixture_is_not_the_cause(repo):
    answers = _fixture(repo)
    changed = s.result_of(repo.verify_apply(repo.answers(answers))).get("changed")
    assert changed == ["DAEO-ok01", "DAEO-ok02"], f"changed is {changed!r}"
    for ticket in ("DAEO-ok01", "DAEO-ok02"):
        assert s.lacking_labels(repo.ticket_text(ticket)) == []
    s.marker_invariant(repo.root)


def test_s4_an_answers_key_that_is_no_ticket_is_refused(repo):
    answers = _fixture(repo)
    answers["DAEO-nope"] = {"S1": CLAUSE}
    assert _refused(repo, answers) == "VERIFY_PASS_UNKNOWN_TICKET"


def test_s4_a_closed_ticket_is_refused_and_never_edited(repo):
    answers = _fixture(repo)
    answers["DAEO-cl01"] = {"S1": CLAUSE}
    assert _refused(repo, answers) == "VERIFY_PASS_CLOSED"


@pytest.mark.parametrize("label", ["S9", "F7", "S0"])
def test_s4_a_label_the_ticket_does_not_have_is_refused(repo, label):
    answers = _fixture(repo)
    answers["DAEO-ok01"][label] = CLAUSE
    assert _refused(repo, answers) == "VERIFY_PASS_UNKNOWN_LABEL"


def test_s4_a_label_whose_line_already_has_a_verify_is_refused(repo):
    answers = _fixture(repo)
    answers["DAEO-ok01"]["F1"] = CLAUSE  # F1 of DAEO-ok01 is a {line, verify} mapping
    assert _refused(repo, answers) == "VERIFY_PASS_UNKNOWN_LABEL"


def test_s4_a_label_answered_twice_over_an_earlier_apply_is_refused(repo):
    answers = _fixture(repo)
    s.result_of(repo.verify_apply(repo.answers(answers)))
    assert _refused(repo, {"DAEO-ok01": {"S1": CLAUSE}}, name="again.yaml") == "VERIFY_PASS_UNKNOWN_LABEL"


def test_s4_f1_a_line_still_lacking_a_verify_is_refused_and_the_ticket_unmarked(repo):
    answers = _fixture(repo)
    del answers["DAEO-ok01"]["S2"]  # S2 of DAEO-ok01 still lacks a verify
    assert _refused(repo, answers) == "VERIFY_PASS_UNANSWERED"
    assert s.marker_lines(repo.ticket_text("DAEO-ok01")) == [], "a ticket with a line unanswered was marked"
    assert s.lacking_labels(repo.ticket_text("DAEO-ok01")) == ["S1", "S2"]


def test_s4_f1_a_named_ticket_with_no_label_answered_is_refused(repo):
    answers = _fixture(repo)
    answers["DAEO-ok01"] = {}
    assert _refused(repo, answers) == "VERIFY_PASS_UNANSWERED"


@pytest.mark.parametrize("clause", ["", "   ", "\t", "TBD", "tbd", "Tbd", "TODO", "todo", "n/a", "N/A", "none", "None",
                                    "NONE", "  none  ", "TBD.", "none.", "n/a ..", " TODO. ", 42, None],
                         ids=["empty", "spaces", "tab", "TBD", "tbd", "Tbd", "TODO", "todo", "n-a", "N-A", "none",
                              "None", "NONE", "none-padded", "TBD-dot", "none-dot", "n-a-dots", "TODO-padded-dot",
                              "number", "null"])
def test_s4_an_empty_or_placeholder_clause_is_refused(repo, clause):
    answers = _fixture(repo)
    answers["DAEO-ok02"]["F1"] = clause
    assert _refused(repo, answers) == "VERIFY_PASS_EMPTY_CLAUSE"


def test_s4_a_clause_with_words_of_its_own_is_accepted_even_when_it_starts_with_a_placeholder_word(repo):
    answers = _fixture(repo)
    answers["DAEO-ok01"]["S1"] = "none of the other files change: a folder hash before and after is the same"
    answers["DAEO-ok01"]["S2"] = "TBD marks are not allowed: a test greps the file for them"
    changed = s.result_of(repo.verify_apply(repo.answers(answers))).get("changed")
    assert changed == ["DAEO-ok01", "DAEO-ok02"], f"a clause of its own was refused or the result is wrong: {changed!r}"


@pytest.mark.parametrize("kind", ["missing-file", "not-yaml", "a-list", "a-mapping-of-text", "empty-file"])
def test_s4_an_answers_file_that_cannot_be_read_as_a_mapping_of_mappings_is_refused(repo, kind):
    _fixture(repo)
    if kind == "missing-file":
        before = s.snapshot(repo.tmp)
        done = repo.verify_apply(repo.outside / "no-such-answers.yaml")
        assert s.refused_code(done) == "VERIFY_PASS_ANSWERS_UNREADABLE"
        assert s.snapshot(repo.tmp) == before
        return
    text = {"not-yaml": "DAEO-ok01: {S1: [unclosed\n", "a-list": "- DAEO-ok01\n- DAEO-ok02\n",
            "a-mapping-of-text": "DAEO-ok01: S1 is answered somewhere\n", "empty-file": ""}[kind]
    assert _refused(repo, text=text) == "VERIFY_PASS_ANSWERS_UNREADABLE"


# --- F1: all or nothing ---------------------------------------------------------------------------------------------

def _ten(repo) -> dict:
    """Ten open tickets, each with one line lacking a verify, and two closed ones (ids that sort first and last); the
    returned answers file answers the ten, in order."""
    answers = {}
    for n in range(1, 11):
        ticket = f"DAEO-t{n:03d}"
        repo.ticket(ticket, f"W2-{920 + n}", "open", [s.lacking(f"Ticket {n} has a line [DEC-1].")],
                    [s.verified(f"Ticket {n} never crashes [DEC-1].")])
        answers[ticket] = {"S1": f"{CLAUSE} (ticket {n})"}
    for ticket, w2 in (("DAEO-aa98", "W2-998"), ("DAEO-zz98", "W2-999")):
        repo.ticket(ticket, w2, "closed", [s.lacking("A closed ticket's line [DEC-1].")], [s.verified()])
    return answers


FAULTS = {
    "empty-clause": ("VERIFY_PASS_EMPTY_CLAUSE", None, {"S1": "TBD"}),
    "unknown-label": ("VERIFY_PASS_UNKNOWN_LABEL", None, "extra"),
    "unanswered": ("VERIFY_PASS_UNANSWERED", None, {}),
    "closed-ticket": ("VERIFY_PASS_CLOSED", "closed", {"S1": CLAUSE}),
    "unknown-ticket": ("VERIFY_PASS_UNKNOWN_TICKET", "unknown", {"S1": CLAUSE}),
}


@pytest.mark.parametrize("position", ["last", "first"])
@pytest.mark.parametrize("fault", list(FAULTS))
def test_f1_nine_good_entries_and_one_bad_one_leave_the_whole_tree_byte_identical(repo, fault, position):
    """Nine of the ten tickets are answered well; the tenth entry (first or last, by file order and by id) is bad."""
    from gov.cli.errors import GovError

    code, kind, value = FAULTS[fault]
    pairs = list(_ten(repo).items())
    slot = len(pairs) - 1 if position == "last" else 0
    key = pairs[slot][0]
    if kind == "closed":
        key = "DAEO-zz98" if position == "last" else "DAEO-aa98"
    elif kind == "unknown":
        key = "DAEO-zz00" if position == "last" else "DAEO-aa00"
    if value == "extra":
        value = {"S1": CLAUSE, "S5": CLAUSE}
    pairs[slot] = (key, value)
    path = repo.answers(dict(pairs))
    before = s.snapshot(repo.tmp)
    assert s.refused_code(repo.verify_apply(path)) == code
    assert s.snapshot(repo.tmp) == before, \
        f"the CLI refused but the tree changed: {s.changed_entries(before, s.snapshot(repo.tmp))}"
    with pytest.raises(GovError) as raised:
        s.verify_pass().apply(repo.root, path, s.SESSION, s.TODAY)
    assert raised.value.code == code
    assert s.snapshot(repo.tmp) == before, \
        f"the function refused but the tree changed: {s.changed_entries(before, s.snapshot(repo.tmp))}"
    s.marker_invariant(repo.root)


def test_f1_a_ticket_the_answers_file_does_not_name_is_never_edited(repo):
    answers = _ten(repo)
    repo.ticket("DAEO-un01", "W2-990", "open", [s.lacking("Unnamed one [DEC-1].")], [s.lacking("Unnamed failure [DEC-1].")])
    repo.ticket("DAEO-un02", "W2-991", "in_progress", [s.verified("Unnamed two [DEC-1].")], [s.verified()])
    unnamed = {t: repo.ticket_bytes(t) for t in ("DAEO-un01", "DAEO-un02", "DAEO-aa98", "DAEO-zz98")}
    changed = s.result_of(repo.verify_apply(repo.answers(answers))).get("changed")
    assert changed == sorted(answers), f"changed is {changed!r}"
    for ticket, content in unnamed.items():
        assert repo.ticket_bytes(ticket) == content, f"{ticket} is not named in the answers file but was edited"
    for ticket in answers:
        assert len(s.marker_lines(repo.ticket_text(ticket))) == 1 and s.lacking_labels(repo.ticket_text(ticket)) == []
    s.marker_invariant(repo.root)


def test_f1_the_function_never_edits_an_unnamed_ticket_either(repo):
    answers = _ten(repo)
    answers = {k: v for k, v in answers.items() if k in ("DAEO-t001", "DAEO-t002")}
    others = {p.name: p.read_bytes() for p in repo.tickets.glob("*.md") if p.stem not in answers}
    changed = s.verify_pass().apply(repo.root, repo.answers(answers), s.SESSION, s.TODAY)
    assert sorted(changed) == ["DAEO-t001", "DAEO-t002"]
    assert {p.name: p.read_bytes() for p in repo.tickets.glob("*.md") if p.stem not in answers} == others


def test_f1_no_ticket_is_marked_while_a_line_of_it_lacks_a_verify(repo):
    answers = _fixture(repo)
    repo.ticket("DAEO-ok03", "W2-915", "open", [s.lacking("Third has a line [DEC-1].")], [s.lacking("Third failure [DEC-1].")])
    answers["DAEO-ok03"] = {"S1": CLAUSE}  # F1 of DAEO-ok03 is not answered: the whole file is refused
    assert _refused(repo, answers) == "VERIFY_PASS_UNANSWERED"
    for path in repo.tickets.glob("*.md"):
        assert s.marker_lines(path.read_text(encoding="utf-8")) == [], f"{path.name} was marked"
