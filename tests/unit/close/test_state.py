"""The state of a ticket's refused closes (DEC-487, DEC-490): written whole or not at all, not reset by its
absence or by a value that is no count, and lifted only by a decision that qualifies."""
from __future__ import annotations

import json
import os

import pytest

from gov.cli.errors import GovError
from gov.close import state
from gov.close.command import EXIT_BLOCKED, _refuse, run
from gov.close.state import (count_path, decisions_used, escalation_path, lift_escalation, read_count,
                             read_escalation, write_count, write_whole)

TICKET = "T-0001"
COUNTER = f".gov-runtime/iterations/{TICKET}.json"
ESCALATION = f".gov-runtime/escalations/{TICKET}.json"


def _decision(dec_id, status="ACTIVE", kind="decision"):
    return f"---\nid: {dec_id}\ntype: {kind}\nstatus: {status}\ntitle: Continue\n---\n# {dec_id}\n"


def _escalated(project):
    """Three refusals: the escalation is in force and began at the commit they were refused at."""
    for _ in range(3):
        with pytest.raises(GovError):
            _refuse(project.root, TICKET, "CHECK_FAILED", "refused", ["a finding"])
    project.commit("what the refusals left", "Role: orchestrator")
    return read_count(project.root, TICKET)


def _owners(project, dec_id="DEC-100", role="Role: owner", **keys):
    return project.commit("the owner's decision", role, files={f"docs/adr/{dec_id}.md": _decision(dec_id, **keys)})


def _lifts_nothing(project, dec_id, counted=None):
    counted = counted or read_count(project.root, TICKET)
    with pytest.raises(GovError) as raised:
        lift_escalation(project.root, TICKET, dec_id, counted)
    assert (raised.value.code, raised.value.exit_code) == ("ESCALATION_BLOCKED", EXIT_BLOCKED)
    assert read_count(project.root, TICKET)["count"] == 3, "the refused decision changed the counter"
    assert not read_escalation(project.root, TICKET).get("lifted_by")
    return raised.value.message


# ---- written whole or not at all ----

def test_a_file_is_written_beside_and_renamed(tmp_path):
    path = tmp_path / "folder" / "state.json"
    write_whole(path, "one")
    write_whole(path, b"two")
    assert path.read_text(encoding="utf-8") == "two"
    assert [entry.name for entry in path.parent.iterdir()] == ["state.json"]


@pytest.mark.parametrize("failing", ["replace", "fsync"])
def test_a_write_that_fails_leaves_the_file_as_it_was_and_nothing_beside_it(tmp_path, monkeypatch, failing):
    path = tmp_path / "state.json"
    write_whole(path, "as it was")

    def fails(*args, **keys):
        raise OSError("planted")

    monkeypatch.setattr(os, failing, fails)
    with pytest.raises(OSError):
        write_whole(path, "half of the new conte")
    assert path.read_text(encoding="utf-8") == "as it was"
    assert [entry.name for entry in tmp_path.iterdir()] == ["state.json"]


def test_the_counter_the_escalation_the_repair_ticket_and_the_close_record_are_written_that_way(root, monkeypatch):
    from gov.close.command import _write_close_record

    written = []
    real = state.write_whole
    monkeypatch.setattr(state, "write_whole", lambda path, content: (written.append(path), real(path, content))[1])
    for _ in range(3):
        with pytest.raises(GovError) as raised:
            _refuse(root, TICKET, "CHECK_FAILED", "refused", ["a finding"])
    _write_close_record(root, TICKET, {}, [], "")
    repair = root / ".tickets" / f"{raised.value.details['repair_ticket']}.md"
    assert {count_path(root, TICKET), escalation_path(root, TICKET), repair,
            root / "docs" / "close" / TICKET / f"CL-{TICKET}.md"} <= set(written)
    for folder in (count_path(root, TICKET).parent, escalation_path(root, TICKET).parent, root / ".tickets"):
        assert not [entry.name for entry in folder.iterdir() if entry.name.endswith(".part")]


def test_a_counter_that_cannot_be_written_is_an_error(root):
    count_path(root, TICKET).parent.parent.mkdir(parents=True)
    count_path(root, TICKET).parent.write_text("a file where the folder goes\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        write_count(root, TICKET, {"count": 1})
    assert raised.value.code == "ITERATION_UNWRITABLE"


# ---- a value that is no count ----

@pytest.mark.parametrize("content", ['{"count": -5, "outcomes": []}', '{"count": 1.5, "outcomes": []}',
                                     '{"outcomes": []}', '{"count": null}', '{"count": "3"}', '{"count": true}',
                                     '{"count": 1, "decisions": "DEC-1"}', "not json {{{", "[]", ""])
def test_a_counter_that_is_no_count_is_named_and_is_no_finding(root, content):
    count_path(root, TICKET).parent.mkdir(parents=True)
    count_path(root, TICKET).write_text(content, encoding="utf-8")
    with pytest.raises(GovError) as raised:
        read_count(root, TICKET)
    assert (raised.value.code, raised.value.exit_code) == ("ITERATION_CORRUPT", 1)
    assert COUNTER in raised.value.message and raised.value.details["file"] == COUNTER
    with pytest.raises(GovError) as raised:   # the counted path does not count over it either
        _refuse(root, TICKET, "CHECK_FAILED", "refused", ["a finding"])
    assert raised.value.code == "ITERATION_CORRUPT"
    assert count_path(root, TICKET).read_text(encoding="utf-8") == content
    assert len(list((root / ".tickets").glob("*.md"))) == 1, "a repair ticket was opened"


def test_a_counter_that_is_a_folder_is_no_count_of_zero(root):
    count_path(root, TICKET).mkdir(parents=True)
    with pytest.raises(GovError) as raised:
        read_count(root, TICKET)
    assert raised.value.code == "ITERATION_CORRUPT"


def test_a_count_from_zero_up_is_read(root):
    write_count(root, TICKET, {"count": 0})
    assert read_count(root, TICKET) == {"count": 0, "outcomes": []}
    write_count(root, TICKET, {"count": 7, "outcomes": [{}]})
    assert read_count(root, TICKET)["count"] == 7


# ---- not reset by its absence ----

def test_an_escalation_in_force_whose_counter_is_missing_blocks_and_names_the_counter(project):
    _escalated(project)
    count_path(project.root, TICKET).unlink()
    with pytest.raises(GovError) as raised:
        read_count(project.root, TICKET)
    assert (raised.value.code, raised.value.exit_code) == ("ESCALATION_BLOCKED", EXIT_BLOCKED)
    assert COUNTER in raised.value.message and "missing" in raised.value.message
    assert not count_path(project.root, TICKET).exists()

    class Args:
        ticket, timeout, disposition, owner_decision = TICKET, None, None, "DEC-100"

    _owners(project)
    with pytest.raises(GovError) as raised:   # nor does a decision given with the counter missing
        run(project.root, Args(), {})
    assert raised.value.exit_code == EXIT_BLOCKED


def test_an_escalation_that_was_lifted_does_not_block_without_a_counter(project):
    _escalated(project)
    _owners(project)
    lift_escalation(project.root, TICKET, "DEC-100", read_count(project.root, TICKET))
    count_path(project.root, TICKET).unlink()
    assert read_count(project.root, TICKET)["count"] == 0


@pytest.mark.parametrize("content", ["not json", "[1]", '{"decisions_used": "DEC-1"}'])
def test_an_escalation_file_that_cannot_be_read_is_named(root, content):
    escalation_path(root, TICKET).parent.mkdir(parents=True)
    escalation_path(root, TICKET).write_text(content, encoding="utf-8")
    with pytest.raises(GovError) as raised:
        read_count(root, TICKET)
    assert (raised.value.code, raised.value.exit_code) == ("ESCALATION_CORRUPT", 1)
    assert ESCALATION in raised.value.message


def test_the_third_refusal_records_where_the_escalation_began(project):
    head = project.git("rev-parse", "HEAD").strip()
    counted = _escalated(project)
    assert counted["escalated_at"] == head
    package = read_escalation(project.root, TICKET)
    assert package["escalated_at"] == head and package["decisions_used"] == []


# ---- the owner's decision ----

def test_the_owners_decision_recorded_after_the_escalation_began_lifts_it(project):
    counted = _escalated(project)
    _owners(project)
    lifted = lift_escalation(project.root, TICKET, "DEC-100", counted)
    assert lifted == {"count": 0, "last_failures": [], "outcomes": [], "decision": "DEC-100",
                      "decisions": ["DEC-100"]}
    assert read_count(project.root, TICKET) == lifted
    package = read_escalation(project.root, TICKET)
    assert package["lifted_by"] == "DEC-100" and package["decisions_used"] == ["DEC-100"]


def test_a_decision_recorded_before_the_escalation_began_lifts_none(project):
    _owners(project)
    _escalated(project)
    assert "before the escalation began" in _lifts_nothing(project, "DEC-100")


def test_a_decision_that_lifted_one_escalation_lifts_no_second(project):
    counted = _escalated(project)
    _owners(project)
    lift_escalation(project.root, TICKET, "DEC-100", counted)
    counted = _escalated(project)
    assert counted["decisions"] == ["DEC-100"] and counted["count"] == 3
    assert read_escalation(project.root, TICKET)["decisions_used"] == ["DEC-100"]
    assert "before" in _lifts_nothing(project, "DEC-100")
    count_path(project.root, TICKET).write_text(   # nor when the counter has forgotten it: the escalation holds it
        json.dumps({key: value for key, value in counted.items() if key not in ("decision", "decisions")}))
    assert "lifted an escalation of this ticket before" in _lifts_nothing(project, "DEC-100")
    _owners(project, "DEC-101")
    assert lift_escalation(project.root, TICKET, "DEC-101", read_count(project.root, TICKET))["decisions"] \
        == ["DEC-100", "DEC-101"]


def test_the_decisions_used_are_those_of_the_counter_and_of_the_escalation():
    assert decisions_used({"decision": "DEC-3", "decisions": ["DEC-1"]}, {"decisions_used": ["DEC-2", "DEC-1"]}) \
        == ["DEC-1", "DEC-2", "DEC-3"]
    assert decisions_used({}, None) == []


def test_a_file_no_commit_holds_lifts_no_escalation(project):
    _escalated(project)
    (project.root / "docs" / "adr").mkdir(parents=True)
    (project.root / "docs" / "adr" / "DEC-100.md").write_text(_decision("DEC-100"), encoding="utf-8")
    assert "no committed record" in _lifts_nothing(project, "DEC-100")


@pytest.mark.parametrize("named", ["../outside/DEC-100", "docs/adr/DEC-100", "/etc/DEC-100", "DEC-100.md", ""])
def test_a_path_is_no_decision_id(project, tmp_path, named):
    _escalated(project)
    _owners(project)
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "DEC-100.md").write_text(_decision("DEC-100"), encoding="utf-8")
    _lifts_nothing(project, named)


def test_a_record_outside_the_folders_of_decisions_lifts_none(project):
    _escalated(project)
    project.commit("elsewhere", "Role: owner", files={"notes/DEC-100.md": _decision("DEC-100")})
    assert "no committed record" in _lifts_nothing(project, "DEC-100")


@pytest.mark.parametrize("keys, said", [({"kind": "checkpoint"}, "not a decision record"),
                                        ({"status": "DRAFT"}, "not in force"),
                                        ({"status": "SUPERSEDED"}, "not in force")])
def test_a_record_that_is_no_decision_in_force_lifts_none(project, keys, said):
    _escalated(project)
    _owners(project, **keys)
    assert said in _lifts_nothing(project, "DEC-100")


def test_a_record_of_another_id_or_without_frontmatter_lifts_none(project):
    _escalated(project)
    project.commit("two records", "Role: owner", files={"docs/adr/DEC-100.md": _decision("DEC-999"),
                                                        "docs/adr/DEC-200.md": "no frontmatter\n"})
    assert "not a decision record of that id" in _lifts_nothing(project, "DEC-100")
    assert "frontmatter" in _lifts_nothing(project, "DEC-200")


def test_a_decision_held_by_two_files_lifts_none(project):
    _escalated(project)
    project.commit("twice", "Role: owner", files={"docs/adr/DEC-100.md": _decision("DEC-100"),
                                                  "docs/other/DEC-100.md": _decision("DEC-100")})
    assert "not one committed decision record" in _lifts_nothing(project, "DEC-100")


@pytest.mark.parametrize("role", ["Role: engineer", "Role: orchestrator"])
def test_a_decision_the_checker_does_not_confirm_as_the_owners_lifts_none(project, role):
    _escalated(project)
    _owners(project, role=role)
    assert "ACTIVE_UNAPPROVED" in _lifts_nothing(project, "DEC-100")


def test_any_finding_of_the_checker_about_the_decision_lifts_none(project, monkeypatch):
    _escalated(project)
    _owners(project)
    for finding in ({"code": "ACTIVE_SUPERSEDED", "ids": ["DEC-100"], "paths": []},
                    {"code": "FRONTMATTER_UNREADABLE", "ids": [], "paths": ["docs/adr/DEC-100.md"]}):
        monkeypatch.setattr("gov.decisions.check", lambda root, finding=finding: [finding])
        assert finding["code"] in _lifts_nothing(project, "DEC-100")
    monkeypatch.setattr("gov.decisions.check", lambda root: [{"code": "DUPLICATE_ID", "ids": ["DEC-7"], "paths": []}])
    lift_escalation(project.root, TICKET, "DEC-100", read_count(project.root, TICKET))


def test_a_checker_that_cannot_run_is_an_error_and_lifts_nothing(project, monkeypatch):
    counted = _escalated(project)
    _owners(project)

    def cannot_run(root):
        raise GovError("DECISIONS_GIT_FAILED", "planted")

    monkeypatch.setattr("gov.decisions.check", cannot_run)
    with pytest.raises(GovError) as raised:
        lift_escalation(project.root, TICKET, "DEC-100", counted)
    assert raised.value.code == "DECISIONS_GIT_FAILED"
    assert read_count(project.root, TICKET)["count"] == 3


def test_an_escalation_whose_beginning_is_not_known_is_lifted_by_nothing(project):
    counted = _escalated(project)
    _owners(project)
    package = read_escalation(project.root, TICKET)
    del counted["escalated_at"], package["escalated_at"]
    write_count(project.root, TICKET, counted)
    state.write_escalation(project.root, TICKET, package)
    assert "not recorded" in _lifts_nothing(project, "DEC-100", counted)


def test_a_beginning_outside_the_history_being_closed_shows_nothing(project):
    counted = _escalated(project)
    base = project.git("rev-parse", "HEAD").strip()
    project.git("checkout", "-q", "-b", "side")
    aside = project.commit("aside")
    project.git("checkout", "-q", "main")
    project.git("reset", "-q", "--hard", base)
    _owners(project)
    counted["escalated_at"] = aside
    write_count(project.root, TICKET, counted)
    assert "not in the history" in _lifts_nothing(project, "DEC-100", counted)
