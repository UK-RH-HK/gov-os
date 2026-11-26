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
from gov.launch import criticality as crit, launcher, role as roles

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


# --- S4: the exceptions route ---------------------------------------------------------------------------------------

def test_another_model_is_refused_naming_the_session_model_the_class_and_the_exceptions_file(project):
    project.ticket()
    exceptions(project, [])
    project.refused(OPUS, SONNET, "C2", REL, args=["--model", OPUS])


def test_an_entry_for_the_role_and_model_starts_the_launch_on_it_and_the_record_names_the_decision(project):
    project.ticket()
    # Rewrite-Reason: DEC-1225: the entry had no limiter; R3: an Opus entry carries one, here the launch's ticket
    exceptions(project, [{"subagent_type": "engineer", "model": "opus", "decided": "DEC-9 (the owner)",
                          "task": ["T-1"]}])
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


def test_another_model_is_refused_whatever_probe_records_say(project):
    # Rewrite-Reason: DEC-1246 (3)(b): MR-2: no promotion exists; probe records change nothing, and an entry for
    # another model not held by the file leaves the refusal as on any launch
    tid = project.ticket()
    project.probe(tid, "p1.md", "fail")
    project.probe(tid, "p2.md", "fail")
    exceptions(project, [{"subagent_type": "research", "model": HAIKU, "decided": "x"}])
    project.refused(HAIKU, SONNET, args=["--model", HAIKU])  # the table's Sonnet is the only model
    project.launch()
    assert project.last()["promotion"] is None


# --- S9 (DEC-1215's substitution) is gone (DEC-1225, R3) ------------------------------------------------------------
# Rewrite-Reason: DEC-1225: the cases of this section (an Opus entry is Fable's while the substitution is active; Fable
# refused when it is not; a caller's Opus refused naming DEC-1215 and Fable; the table's Opus run as Fable) and the
# table of ``model_matches`` with its ``active`` argument pinned the substitution, which R3 removes with its file and
# readers. Deleted, not replaced here: the acceptance cases ``test_w2_201_r3_limiters.py`` pin that Fable is refused
# by the launcher and by the hook with an entry naming it and that nothing of the substitution is left; the
# limiters (class, task, decision) are shown there on one table for both readers.

# --- the limiters of an entry (R3), the launcher alone -------------------------------------------------------------

def test_an_opus_entry_with_no_limiter_lifts_nothing(project):
    project.ticket()
    exceptions(project, [{"subagent_type": "engineer", "model": "opus", "decided": "x"}])
    project.refused(REL, args=["--model", OPUS])


@pytest.mark.parametrize("model", ("fable", FABLE))
def test_fable_is_refused_whatever_the_entries_name(project, model):
    project.ticket()
    exceptions(project, [{"subagent_type": "engineer", "model": name, "decided": "x"} for name in ("fable", FABLE, "opus")])
    project.refused(args=["--model", model])


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

# Rewrite-Reason: DEC-1225: this table gave Opus (C3), Haiku (C0) and a table line to four roles. R1: Opus, high only for
# the orchestrator and the senior engineer; Sonnet, high and no table line for every other role.
_S, _O = (SONNET, "high"), (OPUS, "high")
RUBRIC = {"orchestrator": (_O, None), "senior-engineer": (_O, None), "ticket-lead": ((SONNET, "medium"), None),
          "product-spec": (_S, None), "research": (_S, None), "engineer": (_S, None),
          "independent-test-designer": (_S, None), "independent-auditor": (_S, None), "qa-engineer": (_S, None)}


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
