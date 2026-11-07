"""W2-136 S9 unit tests: gov launch refuses a lead outside the approved batches or with an unmet wait."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml

from gov.cli.errors import GovError
from gov.launch import launcher, plan_check
from gov.launch.plan_check import check_lead

REPOSITORY_CHECK = launcher._check_repository_settings


def _plant(root: Path, *tickets: dict) -> Path:
    folder = root / ".tickets"
    folder.mkdir(parents=True, exist_ok=True)
    for front in tickets:
        base = {"status": "in_progress", "priority": 1, "role": "engineer", "allowed_paths": [], "depends_on": [],
                "deps": [], "needs": []}
        base.update(front)
        (folder / f"{base['id']}.md").write_text("---\n" + yaml.safe_dump(base) + "---\n", encoding="utf-8")
    return root


def _ready(root: Path, *lines: str) -> Path:
    path = root / "ready.txt"
    path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    return path


@pytest.fixture
def store(tmp_path):
    return _plant(tmp_path, {"id": "T-1", "wbs_id": "W9-1", "allowed_paths": ["src/a/**"]},
                  {"id": "T-2", "wbs_id": "W9-2", "depends_on": ["T-1"], "deps": ["T-1"]},
                  {"id": "T-3", "wbs_id": "W9-3", "needs": ["src/a/x.py"]},
                  {"id": "T-4", "wbs_id": "W9-4"},
                  {"id": "T-5", "wbs_id": "W9-5", "depends_on": ["T-1"], "deps": ["T-1"], "plan_override": "DEC-899"},
                  {"id": "T-6", "wbs_id": "W9-6", "waits_on": ["T-404 — gone"]},
                  {"id": "T-7", "wbs_id": "W9-7", "status": "closed"},
                  {"id": "T-8", "wbs_id": "W9-8", "depends_on": ["T-7"], "deps": ["T-7"]})


def test_a_ticket_not_in_the_approved_batches_is_refused(store):
    ready = _ready(store, "# batch 1", "W9-1 T-1 W9-1-A5-run1.md W9-1-A5-run1.json")
    verdict = check_lead(store, "T-4", ready=ready)
    assert not verdict.admitted and verdict.override is None
    assert "not in the approved ready list's batches" in verdict.reason


def test_a_ticket_in_the_batches_with_its_waits_met_is_admitted(store):
    ready = _ready(store, "# batch 1", "W9-4 T-4 a.md a.json", "W9-8 T-8 b.md b.json")
    assert check_lead(store, "T-4", ready=ready).admitted
    assert check_lead(store, "W9-8", ready=ready)["admitted"]  # a closed depends_on is met; a WBS id is the ticket


def test_an_unmet_depends_on_is_refused_naming_the_ticket(store):
    ready = _ready(store, "W9-2 T-2 a.md a.json")
    verdict = check_lead(store, "T-2", ready=ready)
    assert not verdict.admitted and "waits for T-1 (DEPENDS_ON T-1)" in verdict.reason


def test_an_unmet_need_is_refused_naming_the_ticket_and_the_path(store):
    verdict = check_lead(store, "T-3", ready={"T-3"})
    assert not verdict.admitted and "waits for T-1 (NEEDS_WHAT_WRITES src/a/x.py)" in verdict.reason


def test_a_wait_that_names_nothing_is_refused(store):
    verdict = check_lead(store, "T-6", ready={"T-6"})
    assert not verdict.admitted and "T-404 (UNKNOWN_WAIT" in verdict.reason


def test_the_waits_are_checked_against_the_current_tickets(store):
    ready = _ready(store, "W9-2 T-2 a.md a.json")
    assert not check_lead(store, "T-2", ready=ready).admitted
    _plant(store, {"id": "T-1", "wbs_id": "W9-1", "status": "closed", "allowed_paths": ["src/a/**"]})
    assert check_lead(store, "T-2", ready=ready).admitted


def test_an_override_admits_and_names_its_decision(store):
    verdict = check_lead(store, "T-5", ready=_ready(store, "# nothing approved"))
    assert verdict.admitted and verdict.override == "DEC-899"
    assert "plan_override DEC-899" in verdict.reason and "T-1 (DEPENDS_ON T-1)" in verdict.reason


def test_no_ready_list_refuses(store, monkeypatch):
    monkeypatch.delenv(plan_check.READY_ENV, raising=False)
    verdict = check_lead(store, "T-4")
    assert not verdict.admitted and "no approved ready list" in verdict.reason
    monkeypatch.setenv(plan_check.READY_ENV, "ready.txt")
    _ready(store, "W9-4 T-4 a.md a.json")
    assert check_lead(store, "T-4").admitted


def test_an_unknown_ticket_or_no_store_is_refused(store, tmp_path):
    assert not check_lead(store, "T-99", ready={"T-99"}).admitted
    assert not check_lead(tmp_path / "none", "T-1", ready={"T-1"}).admitted


# -- the launcher's one call ----------------------------------------------------------------------------------------

def _no_session(monkeypatch, *, caller=None, ticket=None):
    """No session can start; the caller's own identity is ``caller`` (GOV_ROLE) and ``ticket`` (GOV_TICKET)."""
    for name, value in (("GOV_ROLE", caller), ("GOV_TICKET", ticket)):
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    started = []
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda *a, **k: started.append(a) or pytest.fail("started"))
    return started


@pytest.mark.parametrize("role", ["orchestrator", "lead"])
def test_the_launcher_refuses_a_lead_naming_what_it_waits_for_and_starts_nothing(store, monkeypatch, role):
    started = _no_session(monkeypatch)
    monkeypatch.setenv(plan_check.READY_ENV, str(_ready(store, "W9-2 T-2 a.md a.json")))
    with pytest.raises(GovError) as raised:
        launcher.launch(store, role, "T-2", [])
    assert raised.value.code == "LAUNCH_REFUSED"
    assert "T-1 (DEPENDS_ON T-1)" in raised.value.message
    assert started == []


def _sessions(monkeypatch, tmp_path, *, caller=None, ticket=None):
    """A CLI stand-in under a temporary HOME and a recording ``Popen``; the repository's settings check passes.
    Returns the list of (argv, cwd, env) of the sessions started."""
    for name, value in (("GOV_ROLE", caller), ("GOV_TICKET", ticket)):
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    home = tmp_path / "home"
    (home / ".local" / "bin").mkdir(parents=True)
    (home / launcher.CLI_REL).write_text("", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    started = []

    class Session:
        def __init__(self, argv, cwd, env):
            started.append((argv, cwd, env))

        def wait(self):
            return 0

        def poll(self):
            return 0

    monkeypatch.setattr(launcher.subprocess, "Popen", Session)
    return started


def _settings(argv) -> dict:
    return json.loads(argv[argv.index("--settings") + 1])


@pytest.mark.parametrize("role", ["orchestrator", "lead"])
def test_an_admitted_lead_reaches_the_session_start_with_the_leads_env(store, monkeypatch, tmp_path, role):
    started = _sessions(monkeypatch, tmp_path)
    monkeypatch.setenv(plan_check.READY_ENV, str(_ready(store, "W9-4 T-4 a.md a.json")))
    made = []
    monkeypatch.setattr(launcher.tempfile, "mkdtemp", lambda **kw: made.append(kw) or pytest.fail("a temp folder"))
    args = ["-p", "go", "--permission-mode", "acceptEdits"]
    assert launcher.launch(store, role, "T-4", args) == 0
    [(argv, cwd, env)] = started
    settings = _settings(argv)
    assert settings == {"env": {"GOV_ROLE": "orchestrator", "GOV_TICKET": "T-4"}}  # no sandbox, no deny rules
    assert argv[-len(args):] == args and Path(cwd) == Path(os.path.realpath(store))
    assert (env["GOV_ROLE"], env["GOV_TICKET"]) == ("orchestrator", "T-4")
    assert made == []


def test_a_lead_admitted_by_an_override_starts_and_logs_the_override(store, monkeypatch, tmp_path, capsys):
    started = _sessions(monkeypatch, tmp_path)
    monkeypatch.setenv(plan_check.READY_ENV, str(_ready(store, "# none")))
    assert launcher.launch(store, "orchestrator", "T-5", []) == 0
    assert "gov launch: OVERRIDE DEC-899: plan_override DEC-899 admits ticket T-5" in capsys.readouterr().err
    assert _settings(started[0][0])["env"] == {"GOV_ROLE": "orchestrator", "GOV_TICKET": "T-5"}


@pytest.mark.parametrize("role", ["orchestrator", "lead"])
def test_a_refused_lead_starts_nothing_even_with_the_cli_in_place(store, monkeypatch, tmp_path, role):
    started = _sessions(monkeypatch, tmp_path)
    monkeypatch.setenv(plan_check.READY_ENV, str(_ready(store, "W9-2 T-2 a.md a.json")))
    with pytest.raises(GovError) as raised:
        launcher.launch(store, role, "T-2", [])
    assert "no lead for ticket 'T-2'" in raised.value.message and "T-1 (DEPENDS_ON T-1)" in raised.value.message
    assert started == []


@pytest.mark.parametrize("args", [["--dangerously-skip-permissions"], ["--settings", "{}"], ["--bare"]])
def test_an_admitted_lead_still_refuses_arguments_that_take_the_guard_away(store, monkeypatch, tmp_path, args):
    started = _sessions(monkeypatch, tmp_path)
    monkeypatch.setenv(plan_check.READY_ENV, str(_ready(store, "W9-4 T-4 a.md a.json")))
    with pytest.raises(GovError):
        launcher.launch(store, "lead", "T-4", args)
    assert started == []


def test_an_admitted_lead_is_refused_without_the_guard_wired(store, monkeypatch, tmp_path):
    """A lead has no sandbox: a project whose settings do not wire the guard starts no lead."""
    started = _sessions(monkeypatch, tmp_path)
    monkeypatch.setattr(launcher, "_check_repository_settings", REPOSITORY_CHECK)  # the planted project has none
    monkeypatch.setenv(plan_check.READY_ENV, str(_ready(store, "W9-4 T-4 a.md a.json")))
    with pytest.raises(GovError) as raised:
        launcher.launch(store, "orchestrator", "T-4", [])
    assert "does not register the guard" in raised.value.message
    assert started == []


@pytest.mark.parametrize("caller, ticket", [("orchestrator", "DAEO-sdxk"), ("orchestrator", "T-2"), ("lead", "T-2")])
def test_a_worker_launch_from_a_lead_or_the_cto_never_consults_the_plan(store, monkeypatch, tmp_path, caller, ticket):
    """The CTO's session (GOV_ROLE=orchestrator, GOV_TICKET=DAEO-sdxk) and a lead launch workers of tickets in no
    batch: the plan is never asked, and the worker starts with its own sandboxed settings."""
    started = _sessions(monkeypatch, tmp_path, caller=caller, ticket=ticket)
    monkeypatch.setattr(plan_check, "check_lead", lambda *a, **k: pytest.fail("a worker was checked against the plan"))
    monkeypatch.setattr(launcher, "check_lead", lambda *a, **k: pytest.fail("a worker was checked against the plan"))
    assert launcher.launch(store, "engineer", "T-2", []) == 0
    settings = _settings(started[0][0])
    assert settings["env"]["GOV_ROLE"] == "engineer" and settings["env"]["GOV_TICKET"] == "T-2"
    assert launcher.sandbox_faults(settings) == []


@pytest.mark.parametrize("where", [plan_check, launcher])
@pytest.mark.parametrize("verdict", [{"admitted": False, "reason": "waits for T-1", "override": None},
                                     (False, "waits for T-1", None)])
def test_the_launcher_reads_a_verdict_given_as_a_mapping_or_a_triple(store, monkeypatch, where, verdict):
    _no_session(monkeypatch)
    monkeypatch.setattr(where, "check_lead", lambda root, tid, **k: verdict)
    with pytest.raises(GovError) as raised:
        launcher.launch(store, "lead", "T-4", [])
    assert "waits for T-1" in raised.value.message


def test_a_verdict_reads_as_fields_as_a_mapping_and_as_a_triple(store):
    verdict = check_lead(store, "T-5", ready={"T-5"})
    admitted, reason, override = verdict
    assert (admitted, override) == (True, "DEC-899") == (verdict[0], verdict["override"])
    assert reason == verdict.reason == verdict.get("reason")


def test_the_ready_list_may_be_given_as_its_text_or_its_lines(store):
    assert check_lead(store, "T-4", ready="# batch 1\nW9-4 T-4 a.md a.json\n").admitted
    assert check_lead(store, "T-4", ready=["# batch 1", "W9-4 T-4 a.md a.json"]).admitted
    assert not check_lead(store, "T-4", ready="# batch 1\nW9-1 T-1 a.md a.json\n").admitted


def test_a_waits_on_decision_is_met_once_the_register_accepts_it(store):
    (store / "docs").mkdir()
    register = store / "docs" / "DECISION_REGISTER.md"
    _plant(store, {"id": "T-9", "wbs_id": "W9-9", "waits_on": ["DEC-5 — the owner's word"]})
    register.write_text("### DEC-5 — five\n\n- **Status:** PROPOSED\n", encoding="utf-8")
    verdict = check_lead(store, "T-9", ready={"T-9"})
    assert not verdict.admitted and "DEC-5 (WAITS_ON DEC-5)" in verdict.reason
    register.write_text("### DEC-5 — five\n\n- **Status:** ACCEPTED (owner)\n", encoding="utf-8")
    assert check_lead(store, "T-9", ready={"T-9"}).admitted


def test_a_refusal_names_the_waited_tickets_wbs_id(store):
    assert "T-1 (DEPENDS_ON T-1) [W9-1]" in check_lead(store, "T-2", ready={"T-2"}).reason


@pytest.mark.parametrize("caller, ticket", [(None, None), ("engineer", "T-4"), ("orchestrator", "")])
def test_a_worker_launch_not_from_a_lead_never_calls_the_plan(store, monkeypatch, caller, ticket):
    _no_session(monkeypatch, caller=caller, ticket=ticket)
    monkeypatch.setattr(plan_check, "check_lead", lambda *a, **k: pytest.fail("a worker was checked against the plan"))
    with pytest.raises(GovError):
        launcher.launch(store, "engineer", "T-404", [])
