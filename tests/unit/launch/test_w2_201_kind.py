"""W2-201 fix X1 to X3 (DEC-1219 (5)) builder tests: ``gov launch <role> <ticket> --fix "<line>"`` and
``gov launch <role> --chore "<line>"`` in ``gov.launch.command`` and ``gov.launch.launcher``.

Regression evidence only. No CLI is started: W2-184's recording stand-in (``Project``) is reused.
"""

from __future__ import annotations

import argparse
import json

import pytest
import yaml

from gov.launch import command, launcher

from .test_w2_184_launch import OPUS, SONNET, Project, _flag

FIX, CHORE = "the count is off by one", "tidy the notes"


@pytest.fixture
def project(tmp_path, monkeypatch):
    return Project(tmp_path, monkeypatch)


def _status(project, tid, status):
    path = project.root / ".tickets" / f"{tid}.md"
    front = yaml.safe_load(path.read_text().split("---\n")[1])
    front["status"] = status
    path.write_text("---\n" + yaml.safe_dump(front) + "---\n", encoding="utf-8")


def _settings(argv):
    return json.loads(argv[argv.index("--settings") + 1])


# --- the command line ----------------------------------------------------------------------------------------------

def _parse(argv, passthrough=None):
    parser = argparse.ArgumentParser()
    command.add_arguments(parser)
    args = parser.parse_args(argv)
    args.passthrough = passthrough
    return args


@pytest.fixture
def seen(monkeypatch):
    calls = []
    monkeypatch.setattr(launcher, "launch", lambda root, role, ticket, cli_args, **kw: calls.append(
        ("launch", role, ticket, kw)) or 0)
    monkeypatch.setattr(launcher, "plan", lambda root, role, ticket, **kw: calls.append(
        ("plan", role, ticket, kw)) or 0)
    monkeypatch.setattr(launcher, "tests_worktree", lambda root, role, ticket, **kw: calls.append(
        ("tests_worktree", role, ticket, kw)) or 0)
    return calls


@pytest.mark.parametrize("argv", [
    ["engineer", "T-1", "--fix", FIX, "--chore", CHORE], ["engineer", "--fix", FIX],
    ["engineer", "T-1", "--chore", CHORE],
    ["engineer"], ["engineer", "T-1", "--fix", ""], ["engineer", "--chore", " \t "],
    ["orchestrator", "--fix", FIX], ["orchestrator", "T-1", "--chore", CHORE], ["orchestrator"],
    ["--plan", "engineer", "--fix", FIX], ["--tests-worktree", "independent-test-designer", "--chore", CHORE],
])
def test_a_usage_error_ends_2_and_calls_nothing(seen, tmp_path, capsys, argv):
    assert command.run(tmp_path, _parse(argv), {}) == command.EXIT_USAGE
    assert seen == []
    assert "gov launch: error:" in capsys.readouterr().err


def test_fix_and_chore_reach_the_launcher_as_keywords(seen, tmp_path):
    assert command.run(tmp_path, _parse(["engineer", "T-1", "--fix", FIX]), {}) == 0
    assert command.run(tmp_path, _parse(["engineer", "--chore", CHORE]), {}) == 0
    assert command.run(tmp_path, _parse(["orchestrator", "--chore", CHORE]), {}) == 0
    assert [(c[1], c[2], c[3].get("fix"), c[3].get("chore")) for c in seen] == [
        ("engineer", "T-1", FIX, None), ("engineer", None, None, CHORE), ("orchestrator", None, None, CHORE)]


def test_without_the_flags_no_new_keyword_reaches_the_launcher(seen, tmp_path):
    command.run(tmp_path, _parse(["engineer", "T-1"]), {})
    command.run(tmp_path, _parse(["--plan", "engineer", "T-1"]), {})
    assert seen == [("launch", "engineer", "T-1", {"gate_override": None, "gpu_need_mib": None}),
                    ("plan", "engineer", "T-1", {})]


def test_plan_takes_fix_and_chore_and_tests_worktree_takes_fix(seen, tmp_path):
    command.run(tmp_path, _parse(["--plan", "engineer", "T-1", "--fix", FIX]), {})
    command.run(tmp_path, _parse(["--plan", "engineer", "--chore", CHORE]), {})
    command.run(tmp_path, _parse(["--tests-worktree", "independent-test-designer", "T-1", "--fix", FIX]), {})
    assert seen == [("plan", "engineer", "T-1", {"fix": FIX}), ("plan", "engineer", None, {"chore": CHORE}),
                    ("tests_worktree", "independent-test-designer", "T-1", {"fix": FIX})]


def test_the_usage_line_names_fix_and_chore():
    parser = argparse.ArgumentParser()
    command.add_arguments(parser)
    usage = parser.format_usage()
    first, second = usage.splitlines()
    assert "--fix" in first and "--chore" in second and second.index("--chore") < second.index("[-- <CLI arguments>]")


# --- the launcher's second fence -------------------------------------------------------------------------------------

@pytest.mark.parametrize("role", ["engineer", "orchestrator"])
@pytest.mark.parametrize("tid, keywords", [("T-1", {"fix": FIX, "chore": CHORE}), (None, {"fix": FIX}),
                                           ("T-1", {"chore": CHORE}), (None, {}), ("T-1", {"fix": "  "}),
                                           (None, {"chore": ""})])
def test_the_launcher_refuses_the_same_forms(project, role, tid, keywords):
    project.ticket()
    project.refused(role=role, tid=tid, **keywords)


# --- X1: a worker's fix ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("status", ["closed", "open", "in_progress"])
def test_a_fix_starts_on_its_ticket_whatever_its_status(project, status):
    # Rewrite-Reason: DEC-1225 / DEC-1236 (2): F19, no launch takes a model the rubric does not give (the table's C3 was Opus)
    project.ticket(allowed=["src/guard/a.py"])
    _status(project, "T-1", status)
    argv = project.launch(fix=FIX)
    last = project.last()
    assert (last["kind"], last["kind_line"], last["ticket"]) == ("fix", FIX, "T-1")
    assert (last["model"], last["model_source"], last["criticality"]) == (SONNET, "by criticality", "C3")
    assert _flag(argv, "--model") == SONNET and _settings(argv)["env"]["GOV_TICKET"] == "T-1"


def test_without_fix_a_closed_ticket_is_refused_and_an_unknown_one_with_it(project):
    project.ticket()
    _status(project, "T-1", "closed")
    project.refused("is not in_progress")
    project.refused("unknown ticket", tid="T-9", fix=FIX)


def test_a_fix_keeps_the_role_to_its_own_ticket(project):
    project.ticket(role="research")
    _status(project, "T-1", "closed")
    project.refused("another role", fix=FIX)


def test_an_ordinary_launch_records_kind_feature(project):
    project.ticket()
    project.launch()
    assert (project.last()["kind"], project.last()["kind_line"]) == ("feature", None)


def test_plan_and_tests_worktree_take_a_fix_on_a_closed_ticket(project, capsys, monkeypatch):
    project.ticket()
    _status(project, "T-1", "closed")
    assert launcher.plan(project.root, "engineer", "T-1", fix=FIX) == 0
    assert capsys.readouterr().out.strip() == f"model {SONNET}, effort high"
    with pytest.raises(launcher.GovError, match="is not in_progress"):
        launcher.plan(project.root, "engineer", "T-1")
    with pytest.raises(launcher.GovError, match="is not in_progress"):
        launcher.tests_worktree(project.root, "independent-test-designer", "T-1")
    # with --fix the status is not judged: the next refusal is the tree's own (git says it is on no branch)
    monkeypatch.setattr(launcher.subprocess, "run", lambda argv, **kw: launcher.subprocess.CompletedProcess(argv, 1))
    with pytest.raises(launcher.GovError, match="no branch"):
        launcher.tests_worktree(project.root, "independent-test-designer", "T-1", fix=FIX)


# --- X2: a worker's chore --------------------------------------------------------------------------------------------

def test_a_chore_starts_with_no_ticket_on_the_role_default(project, monkeypatch):
    monkeypatch.setattr(launcher.spend_brake, "refusal", lambda *a: pytest.fail("a chore has no ticket brake"))
    argv = project.launch(tid=None, chore=CHORE)
    last = project.last()
    assert (last["kind"], last["kind_line"], last["ticket"], last["ticket_class"]) == ("chore", CHORE, None, None)
    assert (last["criticality"], last["rubric"], last["model_source"], last["effort_source"]) == (
        None, None, "role default", "role default")
    assert (_flag(argv, "--model"), _flag(argv, "--effort")) == (SONNET, "high")
    assert "GOV_TICKET" not in _settings(argv)["env"] and "GOV_TICKET" not in project.envs[-1]
    assert project.envs[-1]["GOV_MSG_ADDRESS"].startswith("engineer:chore-")


def test_a_chore_s_other_model_needs_an_exception_whose_limiter_it_meets(project):
    """DEC-1225 (R3): a chore has no ticket and no class, so a class or task limiter is unmet; an Opus entry with no
    limiter lifts nothing; one limited by ``decision`` lifts it when the launch is given ``--owner-named``."""
    path = project.root / "governance/project/model-exceptions.yaml"
    project.refused(args=["--model", OPUS], tid=None, chore=CHORE)
    path.write_text(yaml.safe_dump({"exceptions": [{"subagent_type": "engineer", "model": "opus", "class": "C3",
                                                    "decided": "K1"}]}), encoding="utf-8")
    project.refused("none (a chore has no ticket)", args=["--model", OPUS], tid=None, chore=CHORE)
    path.write_text(yaml.safe_dump({"exceptions": [{"subagent_type": "engineer", "model": "opus", "decided": "K2"}]}),
                    encoding="utf-8")
    project.refused("limiter", args=["--model", OPUS], tid=None, chore=CHORE)
    path.write_text(yaml.safe_dump({"exceptions": [{"subagent_type": "engineer", "model": "opus",
                                                    "decision": ["DEC-1230"], "decided": "K3"}]}), encoding="utf-8")
    project.launch(args=["--model", OPUS], tid=None, chore=CHORE, owner_named="DEC-1230")
    assert (project.last()["model_source"], project.last()["exception"]) == ("exception", "K3")


def test_a_chore_takes_no_trial(project):
    project.trial()
    project.refused("--trial", tid=None, chore=CHORE, trial="trial-1")


def test_plan_takes_a_chore(project, capsys):
    assert launcher.plan(project.root, "engineer", None, chore=CHORE) == 0
    assert capsys.readouterr().out.strip() == f"model {SONNET}, effort high"


# --- X3: a lead's fix and chore --------------------------------------------------------------------------------------

def _lead(project, monkeypatch, admitted=True):
    calls = []
    monkeypatch.setattr(launcher, "check_lead", lambda root, tid: calls.append(tid) or
                        {"admitted": admitted, "reason": "not in the ready list", "override": None})
    return calls


def test_a_lead_fix_skips_the_plan_and_carries_its_kind_in_its_env(project, monkeypatch):
    calls = _lead(project, monkeypatch, admitted=False)
    project.ticket()
    _status(project, "T-1", "closed")
    argv = project.launch(role="orchestrator", fix=FIX)
    env = _settings(argv)["env"]
    assert calls == []
    assert (env["GOV_TICKET"], env["GOV_LAUNCH_KIND"], env["GOV_LAUNCH_LINE"]) == ("T-1", "fix", FIX)
    assert (project.envs[-1]["GOV_LAUNCH_KIND"], project.envs[-1]["GOV_LAUNCH_LINE"]) == ("fix", FIX)
    project.refused("unknown ticket", role="orchestrator", tid="T-9", fix=FIX)
    project.refused("no lead for ticket", role="orchestrator")


def test_a_lead_chore_has_no_ticket_and_a_chore_label(project, monkeypatch):
    calls = _lead(project, monkeypatch, admitted=False)
    argv = project.launch(role="lead", tid=None, chore=CHORE)
    env = _settings(argv)["env"]
    assert calls == [] and "GOV_TICKET" not in env and "GOV_TICKET" not in project.envs[-1]
    assert (env["GOV_LAUNCH_KIND"], env["GOV_LAUNCH_LINE"]) == ("chore", CHORE)
    address = project.envs[-1]["GOV_MSG_ADDRESS"]
    assert address.startswith("orchestrator:chore-") and len(address.split(":chore-")[1]) == 8


def test_a_lead_without_the_flags_has_an_unchanged_env(project, monkeypatch):
    calls = _lead(project, monkeypatch)
    project.ticket()
    argv = project.launch(role="orchestrator")
    assert calls == ["T-1"]
    assert not {"GOV_LAUNCH_KIND", "GOV_LAUNCH_LINE"} & (set(_settings(argv)["env"]) | set(project.envs[-1]))
    assert _settings(argv)["env"]["GOV_TICKET"] == "T-1"
