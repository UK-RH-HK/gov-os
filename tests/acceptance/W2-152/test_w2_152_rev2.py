"""W2-152 revision 2: four behaviours the round-1 review found uncaught (README, "Revision 2").

From the ticket's lines only: S5 (every role's template), S9 (the dependency check is never off silently), S8 (a ticket
with no readable KPI lines or no readable front matter is not READY). Each case builds its own repository (README).
"""

from __future__ import annotations

import copy
import json

import pytest
import yaml

import w2_152_support as s


def _error(done) -> dict:
    """The error of a ``--json`` run that must refuse: non-zero exit, an envelope with ``ok: false``."""
    assert done.returncode != 0, f"gov brief did not refuse: {s.describe(done)}"
    data = s.envelope(done)
    assert data.get("ok") is False, f"the envelope is not a refusal: {data}"
    error = data.get("error")
    assert isinstance(error, dict), f"the envelope carries no error: {data}"
    return error


def _finding_codes(error: dict) -> list[str]:
    findings = (error.get("details") or {}).get("findings") or []
    return [str(item.get("code")) for item in findings if isinstance(item, dict)]


def _plain_refused(done) -> None:
    assert done.returncode != 0, f"gov brief did not refuse: {s.describe(done)}"
    assert done.stdout == "", f"a refusal printed something on stdout: {s.describe(done)}"


# --- S5: "until <ticket>" in the role's own template ----------------------------------------------------------------
# W2-153 delivers the whole role template as the system prompt, so a stale line there reaches the session too.
# The closed planted ticket and the open one; the briefed ticket itself is not used.

def _closed_and_open(repo):
    repo.ticket(s.closed_ticket("DAEO-fx09", "W2-909", status="closed"))
    repo.ticket(s.closed_ticket("DAEO-fx08", "W2-908", status="in_progress"))


def _until_found(findings, w2: str, tk: str) -> bool:
    return s.has(findings, "UNTIL_CLOSED", w2) or s.has(findings, "UNTIL_CLOSED", tk)


def _lead_common_line(repo, line: str) -> None:
    """A line in role-lead.md's common part ("## Where things are"), outside the run section and its blocks."""
    path = repo.template("role-lead.md")
    text = path.read_text(encoding="utf-8")
    anchor = "## Where things are\n"
    assert anchor in text, "the planted role-lead.md has no '## Where things are' section"
    path.write_text(text.replace(anchor, anchor + line + "\n", 1), encoding="utf-8")


def test_s5_role_engineer_template_until_a_closed_ticket_is_refused(repo):
    _closed_and_open(repo)
    repo.append_template_line("role-engineer.md", "PLANTED-ROLE-ENGINEER keep the old parser until W2-909.")
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert _until_found(findings, "W2-909", "DAEO-fx09"), \
        f"UNTIL_CLOSED W2-909 in role-engineer.md is not named: {findings}"
    s.plain_refusal(repo.run("engineer", s.TICKET_ID), ("UNTIL_CLOSED", "909"))


def test_s5_role_lead_common_part_until_a_closed_ticket_is_refused(repo):
    _closed_and_open(repo)
    _lead_common_line(repo, "PLANTED-ROLE-LEAD keep the old parser until W2-909.")
    findings = s.refusal(repo.run("lead", s.TICKET_ID, "--run", "build", json_out=True))
    assert _until_found(findings, "W2-909", "DAEO-fx09"), \
        f"UNTIL_CLOSED W2-909 in role-lead.md's common part (outside the build block) is not named: {findings}"
    s.plain_refusal(repo.run("lead", s.TICKET_ID, "--run", "build"), ("UNTIL_CLOSED", "909"))


def test_s5_role_templates_until_an_open_ticket_are_not_refused(repo):
    _closed_and_open(repo)
    repo.append_template_line("role-engineer.md", "PLANTED-ROLE-ENGINEER keep the old parser until W2-908.")
    _lead_common_line(repo, "PLANTED-ROLE-LEAD keep the old parser until W2-908.")
    for args in (("engineer", s.TICKET_ID), ("lead", s.TICKET_ID, "--run", "build")):
        done = repo.run(*args)
        s.ok(done)
        assert "UNTIL_CLOSED" not in done.stderr, f"{args[0]}: an open ticket's until line was refused: {done.stderr}"


# --- S9: the dependency check is never off silently -----------------------------------------------------------------

def _no_ready(facts: dict) -> None:
    facts.pop("ready", None)


def _soon(facts: dict) -> None:
    facts["ready"] = {"new_since": "soon"}


@pytest.mark.parametrize("break_facts", [_no_ready, _soon], ids=["no-ready-key", "new-since-soon"])
def test_s9_facts_without_a_readable_new_since_is_refused_naming_it(repo, break_facts):
    """With no readable ``ready.new_since`` the dependency check cannot run: refused, never READY by default. The
    ticket is READY on every other count."""
    facts = repo.facts()
    break_facts(facts)
    repo.write_facts(facts)
    error = _error(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert "new_since" in json.dumps(error), f"the refusal does not name ready.new_since: {error}"
    plain = repo.run("engineer", s.TICKET_ID)
    _plain_refused(plain)
    assert "new_since" in plain.stderr, f"stderr does not name ready.new_since: {s.describe(plain)}"


def test_s9_schema_requires_ready():
    import jsonschema

    schema = json.loads(s.FACTS_SCHEMA.read_text(encoding="utf-8"))
    data = yaml.safe_load(s.FACTS.read_text(encoding="utf-8"))
    data = copy.deepcopy(data)
    data.pop("ready", None)
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = [error.message for error in validator.iter_errors(data)]
    assert any("ready" in message for message in errors), \
        f"facts.schema.json accepts a facts file with no 'ready' key (errors: {errors[:5]})"


# --- S8: a ticket with no readable KPI lines is not READY -----------------------------------------------------------

def _kpis_missing(front: dict) -> None:
    front.pop("kpis")


def _kpis_list(front: dict) -> None:
    front["kpis"] = list(front["kpis"]["success"])


def _success_empty(front: dict) -> None:
    front["kpis"]["success"] = []


@pytest.mark.parametrize("break_kpis", [_kpis_missing, _kpis_list, _success_empty],
                         ids=["kpis-missing", "kpis-a-list", "success-empty"])
def test_s8_no_readable_kpi_lines_is_refused_naming_kpis(repo, break_kpis):
    front = s.ready_front()
    break_kpis(front)
    repo.ticket(front)
    findings = s.refusal(repo.run("engineer", s.TICKET_ID, json_out=True))
    assert any("kpis" in detail.lower() or "kpis" in code.lower() for code, detail in findings), \
        f"no finding names kpis: {findings}"
    _plain_refused(repo.run("engineer", s.TICKET_ID))


# --- S8: unreadable front matter ------------------------------------------------------------------------------------

def _unclosed(text: str) -> str:
    """The closing ``---`` of the front matter removed."""
    head, sep, body = text.partition("\n---\n")
    assert sep, "the fixture ticket has no closing front-matter line"
    return head + "\n" + body


def _invalid_yaml(text: str) -> str:
    """A flow list left open inside the front matter."""
    return text.replace("\nallowed_paths:\n", "\nallowed_paths: [src/widget/**\n", 1)


@pytest.mark.parametrize("spoil", [_unclosed, _invalid_yaml], ids=["unclosed-block", "invalid-yaml"])
def test_s8_unreadable_front_matter_is_refused_as_ticket_unreadable(repo, spoil):
    path = repo.ticket(s.ready_front())
    spoiled = spoil(path.read_text(encoding="utf-8"))
    path.write_text(spoiled, encoding="utf-8")
    done = repo.run("engineer", s.TICKET_ID, json_out=True)
    error = _error(done)
    assert error.get("code") == "TICKET_UNREADABLE" or "TICKET_UNREADABLE" in _finding_codes(error), \
        f"the refusal is not TICKET_UNREADABLE: {error}"
    assert "ALLOWED_PATHS_EMPTY" not in done.stdout + done.stderr, \
        f"an unreadable ticket was read as an empty one (ALLOWED_PATHS_EMPTY): {error}"
    plain = repo.run("engineer", s.TICKET_ID)
    _plain_refused(plain)
    assert "TICKET_UNREADABLE" in plain.stderr, f"stderr does not name TICKET_UNREADABLE: {s.describe(plain)}"
