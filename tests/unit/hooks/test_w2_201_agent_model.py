"""W2-201 (DAEO-k1us) builder tests for ``.claude/hooks/agent_model.py`` (S5, S6, S9, F1): the hook run as a
subprocess (``python3 -I``) on planted events in a planted project. Regression evidence only."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from gov.launch import criticality as crit, model_exceptions

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / ".claude" / "hooks" / "agent_model.py"
OPUS, SONNET, FABLE = "claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-2"
RUBRIC = {"version": 1, "default": "C2", "opus": OPUS, "rules": [
    {"class": "C3", "paths": ["src/gov/close/**"]}, {"class": "C1", "paths": ["docs/*"]},
    {"class": "C2", "profile": "FULL"}]}
K1 = [{"subagent_type": role, "model": "opus", "class": "C3", "decided": "DEC-1214 K1"}
      for role in ("independent-test-designer", "engineer", "independent-auditor", "qa-engineer")]


@pytest.fixture
def bed(tmp_path):
    root = tmp_path / "project"
    (root / "governance/project").mkdir(parents=True)
    (root / ".tickets").mkdir()
    plant(root, "criticality", RUBRIC)
    plant(root, "model-exceptions", {"exceptions": K1})
    ticket(root, "DAEO-c3aa", ["src/gov/close/x.py  # the close"])
    ticket(root, "DAEO-c2aa", ["src/gov/health/x.py"])
    return root


def plant(root, name, data):
    (root / f"governance/project/{name}.yaml").write_text(data if isinstance(data, str) else yaml.safe_dump(data),
                                                          encoding="utf-8")


def ticket(root, tid, allowed, profile="STANDARD", **more):
    front = {"id": tid, "status": "in_progress", "profile": profile, "allowed_paths": allowed, **more}
    (root / ".tickets" / f"{tid}.md").write_text("---\n" + yaml.safe_dump(front) + "---\n# t\n", encoding="utf-8")


def substitution(root, **change):
    plant(root, "model-substitution", {"active": True, "from": OPUS, "to": FABLE, "effort": "high",
                                       "until": "2999-01-01T00:00:00+00:00", **change})


def run(root, kind=None, model=None, prompt="Do it.", tool="Agent", raw=None):
    args = {"prompt": prompt, **({"subagent_type": kind} if kind else {}), **({"model": model} if model else {})}
    event = raw if raw is not None else json.dumps({"tool_name": tool, "tool_input": args})
    return subprocess.run([sys.executable, "-I", str(HOOK)], input=event, capture_output=True, text=True,
                          env={"CLAUDE_PROJECT_DIR": str(root), "PATH": "/usr/bin:/bin"}, timeout=30)


def passes(done):
    assert (done.returncode, done.stdout, done.stderr) == (0, "", ""), done


def refuses(done, *needles):
    assert done.returncode == 2 and done.stdout == "", done
    for needle in needles:
        assert needle in done.stderr, (needle, done.stderr)


# --- S5 -------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("model", ("opus", OPUS))
@pytest.mark.parametrize("kind", [entry["subagent_type"] for entry in K1])
def test_opus_passes_for_a_c3_ticket(bed, kind, model):
    passes(run(bed, kind, model, "Brief.\nTask: DAEO-c3aa\nGo."))


def test_opus_is_refused_for_a_c2_ticket_naming_the_ticket_and_its_class(bed):
    refuses(run(bed, "engineer", "opus", "Task: DAEO-c2aa\n"), "DAEO-c2aa", "C2", "Opus is for C3 work only")


def test_the_ticket_s_class_key_is_never_read_and_full_is_at_least_c2(bed):
    ticket(bed, "DAEO-kind", ["docs/x.md"], **{"class": "C3"})
    refuses(run(bed, "engineer", "opus", "Task: DAEO-kind"), "DAEO-kind", "C1")
    ticket(bed, "DAEO-full", ["docs/x.md"], profile="FULL")
    refuses(run(bed, "engineer", "opus", "Task: DAEO-full"), "DAEO-full", "C2")


@pytest.mark.parametrize("prompt", ("No line here.", "the Task: DAEO-c3aa inside a line", "Task: DAEO-c3aa extra"))
def test_no_task_line_is_refused_naming_the_line(bed, prompt):
    refuses(run(bed, "engineer", "opus", prompt), "Task:")


def test_two_task_lines_of_different_ids_are_refused_and_of_the_same_id_pass(bed):
    refuses(run(bed, "engineer", "opus", "Task: DAEO-c3aa\nTask: DAEO-c2aa\n"), "Task:")
    passes(run(bed, "engineer", "opus", "Task: DAEO-c3aa\nx\nTask: DAEO-c3aa  \n"))


def test_a_missing_ticket_file_is_refused_naming_it(bed):
    refuses(run(bed, "engineer", "opus", "Task: DAEO-none"), "DAEO-none")


def test_an_unlisted_type_is_refused_naming_the_exceptions_file(bed):
    refuses(run(bed, "general-purpose", "opus", "Task: DAEO-c3aa"), "general-purpose", "model-exceptions.yaml")
    refuses(run(bed, None, "opus", "Task: DAEO-c3aa"), "general-purpose")


@pytest.mark.parametrize("model", ("sonnet", SONNET, None))
def test_sonnet_or_no_model_passes_whatever_the_ticket(bed, model):
    passes(run(bed, "engineer", model, "Task: DAEO-c2aa"))
    passes(run(bed, "engineer", model))


def test_an_entry_with_no_class_needs_no_task_line(bed):
    plant(bed, "model-exceptions", {"exceptions": [{"subagent_type": "*", "model": "claude-haiku-5-5"}]})
    passes(run(bed, "anything", "claude-haiku-5-5"))


# --- S6 -------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("tool", ("Agent", "Task"))
@pytest.mark.parametrize("model", (None, "sonnet", "opus"))
def test_a_fork_is_refused(bed, tool, model):
    refuses(run(bed, "fork", model, tool=tool), "a fresh helper from a written brief", "DEC-1212 (4)")


def test_only_a_fork_entry_lifts_the_fork_refusal(bed):
    plant(bed, "model-exceptions", {"exceptions": [{"subagent_type": "*", "model": "sonnet"}]})
    refuses(run(bed, "fork"), "a fresh helper from a written brief")
    plant(bed, "model-exceptions", {"exceptions": [{"subagent_type": "fork", "model": "sonnet"}]})
    passes(run(bed, "fork"))


def test_a_general_purpose_spawn_with_no_model_passes(bed):
    passes(run(bed, "general-purpose"))


# --- S9 -------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("model", ("fable", FABLE))
def test_while_the_substitution_is_active_fable_is_judged_as_opus(bed, model):
    substitution(bed)
    passes(run(bed, "engineer", model, "Task: DAEO-c3aa"))
    refuses(run(bed, "engineer", model, "Task: DAEO-c2aa"), "DAEO-c2aa", "C2", "C3 work only")
    refuses(run(bed, "engineer", model), "Task:")
    refuses(run(bed, "general-purpose", model, "Task: DAEO-c3aa"), "model-exceptions.yaml")


def test_while_the_substitution_is_active_opus_is_refused_with_the_fable_hint_and_a_fork_stays_refused(bed):
    substitution(bed)
    refuses(run(bed, "engineer", "opus", "Task: DAEO-c3aa"), "DEC-1215", "Claude Fable 5.2", "'fable'")
    refuses(run(bed, "fork", "fable"), "a fresh helper from a written brief")


@pytest.mark.parametrize("change", ({"active": False}, {"until": "2000-01-01T00:00:00+00:00"}, None))
def test_with_the_substitution_inactive_past_or_absent_fable_is_refused_and_opus_is_judged_as_before(bed, change):
    if change is not None:
        substitution(bed, **change)
    refuses(run(bed, "engineer", FABLE, "Task: DAEO-c3aa"), "model-exceptions.yaml")
    passes(run(bed, "engineer", "opus", "Task: DAEO-c3aa"))


# --- F1 -------------------------------------------------------------------------------------------------------------

def _break(root, fault):
    if fault == "exceptions":
        plant(root, "model-exceptions", "exceptions: [\n")
    elif fault == "exceptions-form":
        plant(root, "model-exceptions", "- a\n")
    elif fault == "rubric":
        plant(root, "criticality", "rules: [\n")
    elif fault == "no-rubric":
        (root / "governance/project/criticality.yaml").unlink()
    elif fault == "front":
        (root / ".tickets/DAEO-c3aa.md").write_text("---\nallowed_paths: [\n---\n", encoding="utf-8")
    elif fault == "no-front":
        (root / ".tickets/DAEO-c3aa.md").write_text("# no front matter\n", encoding="utf-8")
    else:
        for path in (root / ".tickets").iterdir():
            path.unlink()
        (root / ".tickets").rmdir()


@pytest.mark.parametrize("fault", ("exceptions", "exceptions-form", "rubric", "no-rubric", "front", "no-front",
                                   "no-tickets"))
def test_unreadable_means_sonnet(bed, fault):
    _break(bed, fault)
    done = run(bed, "engineer", "opus", "Task: DAEO-c3aa")
    refuses(done)
    assert done.stderr.strip() and "Traceback" not in done.stderr
    passes(run(bed, "engineer", "sonnet", "Task: DAEO-c3aa"))
    passes(run(bed, "engineer", None, "Task: DAEO-c3aa"))


def test_an_event_that_is_not_json_or_is_for_another_tool_exits_0(bed):
    passes(run(bed, raw="not json"))
    passes(run(bed, raw="[1, 2]"))
    passes(run(bed, raw=json.dumps({"tool_name": "Agent", "tool_input": "text"})))
    passes(run(bed, "fork", "opus", tool="Bash"))


# --- one rule for the launcher and the hook -------------------------------------------------------------------------

def _hook():
    spec = importlib.util.spec_from_file_location("agent_model_hook", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("allowed, profile", (
    (["src/gov/close/x.py"], None), (["src/gov/close/**"], None), (["src/**"], None), (["src/gov/health/x.py"], None),
    (["docs/x.md"], None), (["docs/x.md"], "FULL"), ([".claude/hooks/agent_model.py"], None), ([], None),
    (["template/governance/kernel/roles/*.md  # kernel"], "LITE"), (["fixtures/evaluation/a/hidden/b"], None),
    (["governance/project/path-map.yaml", "docs/x.md"], None), (["tests/unit/x.py"], "STANDARD")))
def test_the_hook_and_ticket_criticality_give_the_same_class_on_the_real_rubric(allowed, profile):
    front = {"allowed_paths": allowed, **({"profile": profile} if profile else {})}
    assert _hook().ticket_class(str(REPO), front) == crit.ticket_criticality(REPO, front)


@pytest.mark.parametrize("entry, model, active", (
    ("opus", "opus", False), ("opus", OPUS, False), (OPUS, "opus", False), ("opus", SONNET, False),
    ("opus", FABLE, True), ("opus", "fable", True), ("opus", FABLE, False), ("claude-haiku-5-5", FABLE, True),
    ("claude-haiku-5-5", "claude-haiku-5-5", False), ("opus", "claude-opusx", False)))
def test_the_hook_and_the_launcher_match_a_model_by_one_rule(entry, model, active):
    assert _hook().model_matches(entry, model, active) is model_exceptions.model_matches(entry, model, active)


def test_the_real_exceptions_file_lists_the_four_c3_roles():
    data = yaml.safe_load((REPO / "governance/project/model-exceptions.yaml").read_text(encoding="utf-8"))
    assert [(e["subagent_type"], e["model"], e["class"]) for e in data["exceptions"]] == [
        (role, "opus", "C3") for role in ("independent-test-designer", "engineer", "independent-auditor",
                                          "qa-engineer")]
    assert all("DEC-1214 K1" in e["decided"] for e in data["exceptions"])
