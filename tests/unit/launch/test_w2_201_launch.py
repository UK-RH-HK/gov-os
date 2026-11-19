"""W2-201 (DAEO-k1us) builder tests: the exceptions route, the worker's 5-minute cache and the wake-hook refusal of
``launcher.launch`` (S4, S7, S8, S9), and the real role files' and criticality list's values (S1, S2).

Regression evidence only. No CLI is started: W2-184's recording stand-in (``Project``) is reused.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from gov.cli.errors import GovError
from gov.launch import criticality as crit, launcher, model_exceptions, role as roles

from .test_w2_184_launch import HAIKU, OPUS, SONNET, Project, _flag

REPO = Path(__file__).resolve().parents[3]
FABLE = "claude-fable-5-2"
REL = "governance/project/model-exceptions.yaml"
CHECK_SETTINGS = launcher._check_repository_settings  # the real one: ``Project`` puts a no-op in its place


@pytest.fixture
def project(tmp_path, monkeypatch):
    return Project(tmp_path, monkeypatch)


def exceptions(project, entries=None, text=None):
    path = project.root / REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text is not None else yaml.safe_dump({"exceptions": entries}), encoding="utf-8")


def substitution(project, **change):
    data = {"active": True, "from": OPUS, "to": FABLE, "effort": "high", "until": "2999-01-01T00:00:00+00:00"}
    data.update(change)
    (project.root / roles.SUBSTITUTION_REL).write_text(yaml.safe_dump(data), encoding="utf-8")


# --- S4: the exceptions route ---------------------------------------------------------------------------------------

def test_another_model_is_refused_naming_the_session_model_the_class_and_the_exceptions_file(project):
    project.ticket()
    exceptions(project, [])
    project.refused(OPUS, SONNET, "C2", REL, args=["--model", OPUS])


def test_an_entry_for_the_role_and_model_starts_the_launch_on_it_and_the_record_names_the_decision(project):
    project.ticket()
    exceptions(project, [{"subagent_type": "engineer", "model": "opus", "decided": "DEC-9 (the owner)"}])
    argv = project.launch(args=["--model", OPUS])
    assert argv.count("--model") == 1 and _flag(argv, "--model") == OPUS
    last = project.last()
    assert (last["model"], last["model_source"], last["exception"], last["tier"]) == (OPUS, "exception",
                                                                                     "DEC-9 (the owner)", "opus")
    assert last["subagent_model"] == OPUS


def test_every_other_record_holds_exception_null(project):
    project.ticket()
    project.launch()
    assert project.last()["exception"] is None
    project.launch(args=["--model", SONNET])
    assert project.last()["exception"] is None


@pytest.mark.parametrize("entry", ({"subagent_type": "independent-auditor", "model": "opus"},
                                   {"subagent_type": "*", "model": "opus"},
                                   {"subagent_type": "engineer", "model": HAIKU},
                                   {"subagent_type": "engineer", "model": "opus", "class": "C3"}))
def test_an_entry_of_another_role_another_model_or_class_c3_does_not_lift_a_c2_ticket_s_refusal(project, entry):
    project.ticket()
    exceptions(project, [{**entry, "decided": "x"}])
    project.refused(REL, args=["--model", OPUS])


def test_an_exact_model_id_matches_itself(project):
    project.ticket()
    exceptions(project, [{"subagent_type": "engineer", "model": HAIKU, "decided": "x"}])
    project.launch(args=["--model", HAIKU])
    assert project.last()["model_source"] == "exception"


def test_an_entry_with_class_c3_lifts_the_refusal_for_a_c3_ticket(project):
    # a C3 engineer is Opus by the table; a role whose table gives Sonnet on C3 shows the entry's class at work
    project.role_file("engineer", "model claude-sonnet-5-5, effort high")
    project.ticket(allowed=["src/guard/a.py"])
    exceptions(project, [{"subagent_type": "engineer", "model": "opus", "class": "C3", "decided": "K1"}])
    project.launch(args=["--model", OPUS])
    assert (project.last()["model_source"], project.last()["exception"]) == ("exception", "K1")


@pytest.mark.parametrize("text", (None, "exceptions: [\n", "- a\n", "exceptions: nothing\n", "other: []\n", ""))
def test_an_unusable_file_refuses_another_model_and_does_not_touch_a_launch_that_asks_none(project, text):
    project.ticket()
    if text is not None:
        exceptions(project, text=text)
    project.refused(REL, args=["--model", OPUS])
    project.launch()
    project.launch(args=["--model", SONNET])


def test_a_promotion_still_refuses_another_model_whatever_the_file_says(project):
    tid = project.ticket()
    project.probe(tid, "p1.md", "fail")
    project.probe(tid, "p2.md", "fail")
    exceptions(project, [{"subagent_type": "engineer", "model": HAIKU, "decided": "x"}])
    project.refused(HAIKU, OPUS, args=["--model", HAIKU])


# --- S9: under DEC-1215's substitution ------------------------------------------------------------------------------

def test_while_the_substitution_is_active_an_opus_entry_is_fable_s(project):
    project.ticket()
    substitution(project)
    exceptions(project, [{"subagent_type": "engineer", "model": "opus", "decided": "K1"}])
    project.launch(args=["--model", FABLE])
    assert (project.last()["model"], project.last()["model_source"]) == (FABLE, "exception")


@pytest.mark.parametrize("change", ({"active": False}, {"until": "2000-01-01T00:00:00+00:00"}, None))
def test_with_the_substitution_inactive_past_or_absent_fable_is_refused(project, change):
    project.ticket()
    if change is not None:
        substitution(project, **change)
    exceptions(project, [{"subagent_type": "engineer", "model": "opus", "decided": "K1"}])
    project.refused(FABLE, REL, args=["--model", FABLE])


@pytest.mark.parametrize("entries", (None, [], [{"subagent_type": "engineer", "model": "opus", "decided": "K1"}],
                                     [{"subagent_type": "engineer", "model": "opus", "class": "C3", "decided": "K1"}]))
@pytest.mark.parametrize("allowed", (["src/guard/a.py"], ["src/x/a.py"], ["docs/a.md"]))
@pytest.mark.parametrize("model", (OPUS, "claude-opus-9"))
def test_while_the_substitution_is_active_a_caller_s_opus_is_refused_naming_dec_1215_and_fable(project, entries,
                                                                                              allowed, model):
    project.ticket(allowed=allowed)
    substitution(project)
    if entries is not None:
        exceptions(project, entries)
    project.refused("DEC-1215", "fable", args=["--model", model])


@pytest.mark.parametrize("change", ({"active": False}, {"until": "2000-01-01T00:00:00+00:00"}, None))
def test_with_the_substitution_inactive_past_or_absent_a_caller_s_opus_follows_s4(project, change):
    project.ticket()
    if change is not None:
        substitution(project, **change)
    exceptions(project, [])
    project.refused(REL, args=["--model", OPUS])
    exceptions(project, [{"subagent_type": "engineer", "model": "opus", "decided": "K1"}])
    project.launch(args=["--model", OPUS])
    assert (project.last()["model"], project.last()["model_source"]) == (OPUS, "exception")


def test_the_table_s_opus_is_the_substituted_model_in_the_record(project):
    project.ticket(allowed=["src/guard/a.py"])
    substitution(project)
    argv = project.launch()
    assert _flag(argv, "--model") == FABLE and project.last()["model"] == FABLE


# --- the reader (one rule for the launcher and the hook) -------------------------------------------------------------

@pytest.mark.parametrize("entry, model, active, expected", (
    ("opus", "opus", False, True), ("opus", OPUS, False, True), ("opus", "claude-opus-9", False, True),
    (OPUS, "opus", False, True), ("opus", SONNET, False, False), (HAIKU, HAIKU, False, True),
    ("opus", FABLE, True, True), ("opus", "fable", True, True), ("opus", FABLE, False, False),
    (HAIKU, FABLE, True, False), ("opus", "claude-opusx", False, False)))
def test_model_matches(entry, model, active, expected):
    assert model_exceptions.model_matches(entry, model, active) is expected


# --- S7: the worker's 5-minute cache --------------------------------------------------------------------------------

def test_a_worker_launch_carries_the_cache_variable_in_its_settings_its_process_env_and_its_record(project):
    project.ticket()
    argv = project.launch()
    settings = json.loads(argv[argv.index("--settings") + 1])
    assert settings["env"]["CLAUDE_CODE_PROMPT_CACHE_TTL"] == "5m"
    assert project.envs[-1]["CLAUDE_CODE_PROMPT_CACHE_TTL"] == "5m"
    assert "FORCE_PROMPT_CACHING_5M" not in settings["env"] and "FORCE_PROMPT_CACHING_5M" not in project.envs[-1]
    assert project.last()["cache_ttl"] == "5m"


def test_a_lead_s_settings_carry_no_cache_variable(project):
    env = launcher.build_lead_settings(project.root, "T-1")["env"]
    assert "CLAUDE_CODE_PROMPT_CACHE_TTL" not in env and "FORCE_PROMPT_CACHING_5M" not in env


# --- S8: no wake-up hook --------------------------------------------------------------------------------------------

def _settings(root, command, event="Stop", rel=".claude/settings.json"):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"hooks": {event: [{"hooks": [{"type": "command", "command": command}]}]}}),
                    encoding="utf-8")


@pytest.mark.parametrize("name", ("stop_waiter_check", "stop_idle_check", "gov session-watch", "gov msg wait"))
@pytest.mark.parametrize("event", ("Stop", "SubagentStop", "UserPromptSubmit"))
def test_a_wake_hook_in_the_repository_settings_refuses_a_worker_launch(tmp_path, name, event):
    _settings(tmp_path, f"python3 x/{name} --now", event, ".claude/settings.local.json")
    with pytest.raises(GovError) as caught:
        CHECK_SETTINGS(tmp_path)
    assert caught.value.code == "LAUNCH_REFUSED"
    assert ".claude/settings.local.json" in caught.value.message and name in caught.value.message


def test_another_hook_or_another_event_or_a_lead_is_not_refused(tmp_path):
    _settings(tmp_path, "python3 hooks/stop.py")
    CHECK_SETTINGS(tmp_path)
    _settings(tmp_path, "gov msg wait", "PostToolUse")
    CHECK_SETTINGS(tmp_path)
    _settings(tmp_path, "gov msg wait")
    CHECK_SETTINGS(tmp_path, False)


# --- S1, S2: the real files -----------------------------------------------------------------------------------------

_S, _O, _H = (SONNET, "high"), (OPUS, "high"), (HAIKU, "low")
_TABLE = {"C3": _O, "C2": _S, "C1": _S, "C0": _H}
RUBRIC = {"orchestrator": (_O, None), "senior-engineer": (_O, None), "ticket-lead": (_S, None),
          "product-spec": (_S, None), "research": (_S, None), "engineer": (_S, _TABLE),
          "independent-test-designer": (_S, _TABLE), "independent-auditor": (_S, _TABLE), "qa-engineer": (_S, _TABLE)}


@pytest.mark.parametrize("role", sorted(RUBRIC))
def test_the_kernel_role_file_carries_the_rubric(role):
    lines = (REPO / roles.ROLES_REL / f"{role}.md").read_text(encoding="utf-8").splitlines()
    default = roles._one_line(lines, roles.DEFAULT_HEAD, roles.DEFAULT_LINE, role, roles.DEFAULT_FORM, True)
    table = roles._table(lines, role)
    want_default, want_table = RUBRIC[role]
    assert default.groups() == want_default
    assert table == (None if want_table is None else {c: {"full": p, "other": p} for c, p in want_table.items()})


@pytest.mark.parametrize("path, expected", (
    ("template/governance/kernel/roles/x.md", "C3"), ("governance/kernel/x", "C3"), ("docs/contract/x.md", "C3"),
    ("src/gov/close/x.py", "C3"), ("src/gov/accept/x.py", "C3"), ("src/gov/queue/x.py", "C3"),
    ("src/gov/dispatch/landing.py", "C3"), ("src/gov/tasks/queue.py", "C3"),
    ("governance/project/orchestration/tools/merge_queue.py", "C3"),
    ("governance/project/operator/landing_check.py", "C3"), ("src/gov/memaudit/x.py", "C3"),
    ("fixtures/evaluation/x/y", "C3"), ("src/gov/release/x.py", "C3"), ("src/gov/update/x.py", "C3"),
    ("src/gov/lock/x.py", "C3"), ("governance/project/path-map.yaml", "C3"),
    ("src/gov/guard/x.py", "C2"), (".claude/hooks/agent_model.py", "C2"), (".claude/settings.json", "C2"),
    ("src/gov/health/x.py", "C2"), ("docs/x.md", "C1")))
def test_the_real_criticality_list(path, expected):
    assert crit.ticket_criticality(REPO, {"allowed_paths": [path]}) == expected


def test_a_full_ticket_on_docs_is_c2():
    assert crit.ticket_criticality(REPO, {"allowed_paths": ["docs/x.md"], "profile": "FULL"}) == "C2"
