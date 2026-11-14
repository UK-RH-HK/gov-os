"""W2-174 S1: ``gov adopt --verify-list`` and ``verify_pass.missing`` (README)."""

from __future__ import annotations

import json

import pytest

import w2_174_support as s


def _three_tickets(repo) -> None:
    """The ticket's fixture: all lines verified (both forms); two plain lines lacking a verify; a closed ticket with one."""
    repo.ticket("DAEO-aa01", "W2-901", "in_progress",
                [s.mapping("The widget prints its name [DEC-1].", "a unit test reads its name"),
                 s.verified("The widget refuses an empty name [DEC-1].")],
                [s.mapping("The widget prints nothing.", "the unit test of S1 fails")])
    repo.ticket("DAEO-bb02", "W2-902", "in_progress",
                [s.verified("The widget has a first line [DEC-1]."), s.lacking("The widget has a second line [DEC-1].")],
                [s.lacking("The widget never crashes [DEC-1].")])
    repo.ticket("DAEO-cc03", "W2-903", "closed", [s.lacking("A closed ticket's line [DEC-1].")], [s.verified()])


def test_s1_cli_names_exactly_the_open_ticket_with_two_lines_lacking_a_verify(repo):
    _three_tickets(repo)
    before = s.snapshot(repo.root)
    result = s.result_of(repo.verify_list())
    assert result.get("missing") == [{"ticket": "DAEO-bb02", "labels": ["S2", "F1"]}], \
        f"missing is not exactly the second ticket's two labels: {result!r}"
    assert result.get("text") == "DAEO-bb02 S2 F1", f"text is not '<id> <label> <label>': {result.get('text')!r}"
    assert s.snapshot(repo.root) == before, "--verify-list changed the repository"


def test_s1_function_names_exactly_the_open_ticket_with_two_lines_lacking_a_verify(repo):
    _three_tickets(repo)
    found = s.verify_pass().missing(repo.root)
    assert found == [{"ticket": "DAEO-bb02", "labels": ["S2", "F1"]}], f"missing(root) gave {found!r}"


def test_s1_cli_without_json_prints_the_result_as_gov_does(repo):
    _three_tickets(repo)
    done = repo.adopt("--verify-list", json_out=False)
    assert done.returncode == 0, f"gov adopt --verify-list failed: {s.describe(done)}"
    printed = json.loads(done.stdout)
    assert printed == {"missing": [{"ticket": "DAEO-bb02", "labels": ["S2", "F1"]}], "text": "DAEO-bb02 S2 F1"}, \
        f"stdout is not gov's result dict: {done.stdout!r}"


def test_s1_all_verified_repository_prints_none_and_exits_0_cli(repo):
    repo.ticket("DAEO-aa01", "W2-901", "in_progress",
                [s.mapping("The widget prints its name [DEC-1].", "a unit test reads its name"),
                 s.verified("The widget refuses an empty name [DEC-1].")],
                [s.mapping("The widget prints nothing.", "the unit test of S1 fails")])
    repo.ticket("DAEO-ab02", "W2-902", "open", [s.verified()], [s.verified("It never crashes [DEC-1].")])
    done = repo.verify_list()
    result = s.result_of(done)
    assert result.get("missing") == [], f"missing is not []: {result!r}"
    assert result.get("text") == "none", f"text is not exactly 'none': {result.get('text')!r}"


def test_s1_all_verified_repository_prints_none_function(repo):
    repo.ticket("DAEO-aa01", "W2-901", "in_progress", [s.verified()], [s.verified("It never crashes [DEC-1].")])
    assert s.verify_pass().missing(repo.root) == []


@pytest.mark.parametrize("kind", ["no-tickets", "only-closed-with-a-missing-line"])
def test_s1_nothing_to_list_is_none_with_exit_0(repo, kind):
    if kind == "only-closed-with-a-missing-line":
        repo.ticket("DAEO-cc03", "W2-903", "closed", [s.lacking()], [s.lacking("It never crashes [DEC-1].")])
    result = s.result_of(repo.verify_list())
    assert result.get("missing") == [] and result.get("text") == "none", f"not an empty list and 'none': {result!r}"


def test_s1_open_and_in_progress_listed_sorted_by_id_labels_in_kpi_order(repo):
    repo.ticket("DAEO-zz09", "W2-909", "open", [s.lacking("Z one [DEC-1].")], [s.lacking("Z failure [DEC-1].")])
    repo.ticket("DAEO-aa01", "W2-901", "in_progress", [s.verified(), s.lacking("A two [DEC-1].")],
                [s.verified("A failure [DEC-1].")])
    repo.ticket("DAEO-mm05", "W2-905", "open",
                [s.lacking("M one [DEC-1]."), s.verified("M two [DEC-1]."), s.lacking("M three [DEC-1].")],
                [s.verified("M failure one [DEC-1]."), s.lacking("M failure two [DEC-1].")])
    repo.ticket("DAEO-cc03", "W2-903", "closed", [s.lacking()], [s.lacking("C failure [DEC-1].")])
    expected = [{"ticket": "DAEO-aa01", "labels": ["S2"]},
                {"ticket": "DAEO-mm05", "labels": ["S1", "S3", "F2"]},
                {"ticket": "DAEO-zz09", "labels": ["S1", "F1"]}]
    result = s.result_of(repo.verify_list())
    assert result.get("missing") == expected, \
        f"missing is not sorted by id with labels in kpi_rows order: {result.get('missing')!r}"
    assert str(result.get("text")).splitlines() == ["DAEO-aa01 S2", "DAEO-mm05 S1 S3 F2", "DAEO-zz09 S1 F1"], \
        f"text is not one '<id> <label>...' line per ticket, sorted: {result.get('text')!r}"
    assert s.verify_pass().missing(repo.root) == expected, "the function and the CLI disagree"


def test_s1_the_list_agrees_with_the_ready_check(repo):
    """The labels are the ones ``ready_check`` refuses as KPI_NO_VERIFY (the tool reads lines with ``kpi_rows``)."""
    from gov.brief.build import Tickets, ready_check

    repo.ticket("DAEO-bb02", "W2-902", "in_progress",
                [s.verified(), s.lacking("Second [DEC-1]."), s.single("Third, single quoted [DEC-1].")],
                [s.double("A double quoted failure line [DEC-1].")])
    listed = s.result_of(repo.verify_list()).get("missing")
    tickets = Tickets(repo.root)
    front = tickets.load(repo.tickets / "DAEO-bb02.md")[0]
    refused = [finding["detail"] for finding in ready_check(front, tickets, repo.root, s.NEW_SINCE)[0]
               if finding["code"] == "KPI_NO_VERIFY"]
    assert listed == [{"ticket": "DAEO-bb02", "labels": refused}] and refused == ["S2", "S3", "F1"], \
        f"the list {listed!r} and ready_check's KPI_NO_VERIFY {refused!r} disagree"
