"""W2-184 builder tests: RUBRIC-2 at launch in ``launcher.launch`` (interface 3-9).

Regression evidence only (DEC-136). No CLI is started: a recording stand-in replaces ``subprocess.Popen`` under a
temporary HOME with an open resource gate; the records are read from the project's record folder.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

from gov.cli.errors import GovError
from gov.launch import launcher, role as roles

OPUS, SONNET, HAIKU = "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"
VERSION = "- **Version:** 1.0.0"


def table(c3, c2, c1, c0):
    return "- **Launch by criticality:** " + "; ".join(f"{c} {entry}" for c, entry in
                                                     zip(("C3", "C2", "C1", "C0"), (c3, c2, c1, c0)))


def pair(model, effort):
    return f"model {model}, effort {effort}"


# the kernel engineer's table
ENGINEER_TABLE = table(pair(OPUS, "high"), pair(SONNET, "high"), pair(SONNET, "high"), pair(HAIKU, "low"))
CRITICALITY = {"version": 1, "default": "C2", "opus": OPUS, "rules": [
    {"class": "C3", "paths": ["src/guard/*"]}, {"class": "C1", "paths": ["docs/*"]},
    {"class": "C0", "paths": ["notes/*"]}, {"class": "C2", "profile": "FULL"}]}


def _open_gate(home: Path, monkeypatch) -> None:
    from gov.resources import config as gate_config
    folder = home / ".gov-os" / "machine"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "gate.json").write_text(json.dumps(gate_config.template(cpus=list(range(20)))), encoding="utf-8")
    (folder / "meminfo").write_text("MemAvailable: 67108864 kB\n", encoding="utf-8")
    (folder / "loadavg").write_text("0.1 0.1 0.1 1/1 1\n", encoding="utf-8")
    for name, value in (("GOV_RESOURCES_MEMINFO", folder / "meminfo"), ("GOV_RESOURCES_LOADAVG", folder / "loadavg"),
                        ("GOV_RESOURCES_NPROC", 20), ("GOV_RESOURCES_BUSY_CORES", 0),
                        ("GOV_RESOURCES_EMBEDDING_CPU", '{"shared": 0, "query": 0}'),
                        ("GOV_RESOURCES_EMBEDDING_CPU_NOW", '{"shared": 0, "query": 0}'),
                        ("GOV_RESOURCES_DISK", '{"free_bytes": 1000000000000000, "free_inodes": 1000000000}')):
        monkeypatch.setenv(name, str(value))


class Project:
    """A project: role files (engineer with a table, auditor with a default line only), tickets, a CLI stand-in."""

    def __init__(self, tmp_path, monkeypatch):
        self.root = tmp_path / "project"
        self.started: list[list[str]] = []
        self.envs: list[dict] = []
        (self.root / launcher.TEMPLATES_REL).mkdir(parents=True)
        for stem in set(launcher.ROLE_TEMPLATES.values()):
            (self.root / launcher.TEMPLATES_REL / f"{stem}.md").write_text(f"# {stem}\n", encoding="utf-8")
        self.role_file("engineer", pair(SONNET, "high"), ENGINEER_TABLE)
        self.role_file("independent-auditor", pair(OPUS, "high"))
        self.role_file("independent-test-designer", pair(SONNET, "high"), ENGINEER_TABLE)
        self.criticality()
        for name in ("GOV_ROLE", "GOV_TICKET"):
            monkeypatch.delenv(name, raising=False)
        home = tmp_path / "home"
        (home / ".local" / "bin").mkdir(parents=True)
        (home / launcher.CLI_REL).write_text("", encoding="utf-8")
        monkeypatch.setenv("HOME", str(home))
        _open_gate(home, monkeypatch)
        monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
        project = self

        class Session:
            def __init__(self, argv, cwd, env):
                project.started.append(argv)
                project.envs.append(env)

            def wait(self):
                return 0

            def poll(self):
                return 0

        monkeypatch.setattr(launcher.subprocess, "Popen", Session)

    def role_file(self, role, default, line=None):
        path = self.root / roles.ROLES_REL / f"{role}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {role}\n\n{VERSION}\n- **Launch default:** {default}\n" + (f"{line}\n" if line else ""),
                        encoding="utf-8")

    def criticality(self, text=None):
        path = self.root / "governance/project/criticality.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if text is not None else yaml.safe_dump(CRITICALITY), encoding="utf-8")

    def ticket(self, tid="T-1", role="engineer", profile="STANDARD", allowed=("src/x/**",), wbs="W9-1"):
        front = {"id": tid, "wbs_id": wbs, "status": "in_progress", "priority": 1, "role": role, "profile": profile,
                 "allowed_paths": list(allowed), "depends_on": [], "deps": [], "needs": []}
        (self.root / ".tickets").mkdir(parents=True, exist_ok=True)
        (self.root / ".tickets" / f"{tid}.md").write_text("---\n" + yaml.safe_dump(front) + "---\n", encoding="utf-8")
        return tid

    def launch(self, role="engineer", tid="T-1", args=(), **keywords):
        before = len(self.started)
        assert launcher.launch(self.root, role, tid, list(args), **keywords) == 0
        assert len(self.started) == before + 1
        return self.started[-1]

    def records(self) -> list[dict]:
        folder = self.root / ".gov-runtime" / "launches"
        if not folder.is_dir():
            return []
        found = []
        for path in folder.glob("*.json"):
            try:
                found.append(json.loads(path.read_text()))
            except ValueError:
                pass
        return sorted(found, key=lambda r: r["started_at"] + r["session_id"])

    def last(self) -> dict:
        argv = self.started[-1]
        found = [r for r in self.records() if r["session_id"] == argv[argv.index("--session-id") + 1]]
        assert len(found) == 1
        return found[0]

    def refused(self, *needles, role="engineer", tid="T-1", args=(), **keywords) -> GovError:
        before, files = len(self.started), len(self.records())
        with pytest.raises(GovError) as caught:
            launcher.launch(self.root, role, tid, list(args), **keywords)
        assert caught.value.code == "LAUNCH_REFUSED", caught.value
        for needle in needles:
            assert needle in caught.value.message, (needle, caught.value.message)
        assert len(self.started) == before and len(self.records()) == files  # no session, no record
        return caught.value

    def probe(self, tid, name, judgement=None, verdict=None, front=None):
        path = self.root / "docs/probes" / tid / name
        path.parent.mkdir(parents=True, exist_ok=True)
        meta = {"type": "probe", "task": tid, "judgement": judgement} if front is None else front
        text = "---\n" + (meta if isinstance(meta, str) else yaml.safe_dump(meta)) + "---\n\nReport.\n"
        if verdict is not None:
            text += "\n```verdict\n" + (verdict if isinstance(verdict, str) else json.dumps(verdict)) + "\n```\n"
        path.write_text(text, encoding="utf-8")
        return path.relative_to(self.root).as_posix()

    def trial(self, tid="trial-1", **change):
        data = {"role": "engineer", "criticality": "C2", "model": HAIKU, "effort": "high",
                "tickets": ["T-1", "T-other"], "reviewer": {"model": OPUS}}
        data.update(change)
        path = self.root / launcher.TRIALS_REL / f"{tid}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump({k: v for k, v in data.items() if v is not ...}), encoding="utf-8")
        return tid


@pytest.fixture
def project(tmp_path, monkeypatch):
    return Project(tmp_path, monkeypatch)


def _flag(argv, name):
    values = [argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg == name]
    return values[0] if len(values) == 1 else None


# --- the table, a case per role and criticality (S1) ------------------------------------------------------------

@pytest.mark.parametrize("role", ("engineer", "independent-test-designer"))
@pytest.mark.parametrize("allowed, cls, model, effort", (
    (["src/guard/a.py"], "C3", OPUS, "high"), (["src/x/a.py"], "C2", SONNET, "high"),
    (["docs/a.md"], "C1", SONNET, "high"), (["notes/a.md"], "C0", HAIKU, "low"),
))
def test_the_session_takes_the_table_s_model_and_effort_for_its_role_and_class(project, role, allowed, cls, model, effort):
    project.ticket(role=role, allowed=allowed)
    argv = project.launch(role)
    assert (_flag(argv, "--model"), _flag(argv, "--effort")) == (model, effort)
    record = project.last()
    assert {k: record[k] for k in ("model", "effort", "model_source", "effort_source", "criticality", "tier")} == {
        "model": model, "effort": effort, "model_source": "by criticality", "effort_source": "by criticality",
        "criticality": cls, "tier": model.split("-")[1]}
    assert (record["trial"], record["promotion"], record["effort_reason"], record["owner_named"],
            record["review_round"]) == (None, None, None, None, None)
    assert record["subagent_model"] == model


def test_the_subagent_model_in_the_settings_env_is_the_session_s_final_model(project):
    project.ticket(allowed=["notes/a.md"])
    argv = project.launch()
    settings = json.loads(argv[argv.index("--settings") + 1])
    assert settings["env"]["CLAUDE_CODE_SUBAGENT_MODEL"] == HAIKU


def test_a_role_file_with_no_table_takes_its_default_for_every_class(project):
    project.role_file("research", pair(SONNET, "medium"))
    project.role_file("independent-auditor", pair(OPUS, "high"))
    project.ticket(role="independent-auditor", allowed=["notes/a.md"], tid="T-a")
    project.launch("independent-auditor", "T-a")
    assert (project.last()["model"], project.last()["effort"], project.last()["model_source"],
            project.last()["criticality"]) == (OPUS, "high", "role default", "C0")


def test_the_full_form_takes_its_first_pair_on_a_full_ticket_and_its_second_otherwise(project):
    line = table(pair(OPUS, "high"), f"{pair(OPUS, 'high')} on FULL, {pair(SONNET, 'high')} otherwise",
                 pair(SONNET, "high"), pair(HAIKU, "low"))
    project.role_file("engineer", pair(SONNET, "high"), line)
    project.ticket("T-f", profile="FULL")
    project.ticket("T-s", profile="STANDARD")
    project.launch(tid="T-f")
    assert (project.last()["model"], project.last()["criticality"]) == (OPUS, "C2")
    project.launch(tid="T-s")
    assert (project.last()["model"], project.last()["criticality"]) == (SONNET, "C2")


@pytest.mark.parametrize("line", ("- **Launch by criticality:** C3 nonsense",
                                  table(pair(OPUS, "high"), pair(SONNET, "high"), pair(SONNET, "high"), "model x, effort low")))
def test_a_malformed_line_refuses_the_launch(project, line):
    project.role_file("engineer", pair(SONNET, "high"), line)
    project.ticket()
    project.refused("Launch by criticality", "engineer.md")


def test_a_plain_launch_with_no_file_records_the_criticality_null(project):
    (project.root / "governance/project/criticality.yaml").unlink()
    project.role_file("engineer", pair(SONNET, "high"))
    project.ticket()
    project.launch()
    record = project.last()
    assert (record["criticality"], record["model"], record["model_source"], record["tier"]) == (None, SONNET, "role default", "sonnet")


def test_a_plain_launch_with_a_malformed_file_refuses_even_where_no_line_needs_it(project):
    project.role_file("engineer", pair(SONNET, "high"))
    project.criticality("version: 2\n")
    project.ticket()
    project.refused("governance/project/criticality.yaml")


def test_a_role_file_with_a_table_and_no_file_refuses(project):
    (project.root / "governance/project/criticality.yaml").unlink()
    project.ticket()
    project.refused("governance/project/criticality.yaml")


# --- the floor, max and --reason (S1) ---------------------------------------------------------------------------

@pytest.mark.parametrize("effort", ("low", "medium"))
def test_an_effort_below_high_after_the_double_dash_is_refused_where_the_table_is_high(project, effort):
    project.ticket()
    project.refused(effort, "high", args=["--effort", effort])


def test_no_floor_where_the_table_s_effort_is_low_or_medium(project):
    project.ticket(allowed=["notes/a.md"])  # C0: low
    project.launch(args=["--effort", "medium"])
    assert (project.last()["effort"], project.last()["effort_source"]) == ("medium", "after --")
    project.role_file("engineer", pair(SONNET, "medium"))
    project.launch(args=["--effort=low"])
    assert project.last()["effort"] == "low"


@pytest.mark.parametrize("effort", ("high", "xhigh"))
def test_an_effort_of_high_or_more_after_the_double_dash_is_the_launch_s_own(project, effort):
    project.ticket()
    argv = project.launch(args=["--effort", effort])
    assert (project.last()["effort"], project.last()["effort_source"]) == (effort, "after --")
    assert argv.count("--effort") == 1 and _flag(argv, "--model") == SONNET


def test_max_after_the_double_dash_needs_a_reason_and_records_it(project):
    project.ticket()
    project.refused("--reason", "max", args=["--effort", "max"])
    project.launch(args=["--effort", "max"], reason="the plan names it")
    record = project.last()
    assert (record["effort"], record["effort_source"], record["effort_reason"]) == ("max", "after --", "the plan names it")


@pytest.mark.parametrize("reason", ("", "   ", "\n"))
def test_an_empty_reason_is_refused(project, reason):
    project.ticket()
    project.refused("--reason", reason=reason)


def test_a_reason_is_recorded_whatever_the_effort(project):
    project.ticket()
    project.launch(reason="because")
    assert (project.last()["effort"], project.last()["effort_reason"]) == ("high", "because")


def test_a_max_the_table_names_needs_no_reason(project):
    project.role_file("engineer", pair(SONNET, "max"), table(pair(OPUS, "max"), pair(SONNET, "max"), pair(SONNET, "max"), pair(HAIKU, "max")))
    project.ticket()
    project.launch()
    assert (project.last()["effort"], project.last()["effort_reason"]) == ("max", None)
    project.role_file("engineer", pair(SONNET, "max"))
    project.launch()
    assert project.last()["effort"] == "max"


# --- the model after --, the tier ------------------------------------------------------------------------------

def test_a_model_after_the_double_dash_that_is_not_the_resolved_one_is_refused_naming_both(project):
    project.ticket()
    project.refused(HAIKU, SONNET, args=["--model", HAIKU])
    project.refused(OPUS, SONNET, args=[f"--model={OPUS}"])


def test_a_model_after_the_double_dash_equal_to_the_resolved_one_is_accepted_and_not_repeated(project):
    project.ticket()
    argv = project.launch(args=["--model", SONNET])
    assert argv.count("--model") == 1
    assert (project.last()["model"], project.last()["model_source"]) == (SONNET, "after --")


# --- trial (S2, S3) ---------------------------------------------------------------------------------------------

def test_a_planted_trial_admits_its_model_and_effort_and_is_recorded(project):
    project.ticket()
    argv = project.launch(args=["--model", HAIKU], trial=project.trial())
    assert argv.count("--model") == 1 and _flag(argv, "--effort") == "high"
    record = project.last()
    assert (record["model"], record["model_source"], record["tier"], record["trial"], record["subagent_model"]) == \
        (HAIKU, "trial", "haiku", "trial-1", HAIKU)
    assert (record["effort"], record["effort_source"]) == ("high", "trial")


def test_a_trial_with_no_model_after_the_double_dash_sets_the_line(project):
    project.ticket()
    argv = project.launch(trial=project.trial())
    assert (_flag(argv, "--model"), project.last()["model_source"]) == (HAIKU, "trial")


@pytest.mark.parametrize("args", (["--model", OPUS], ["--effort", "xhigh"]))
def test_a_model_or_effort_after_the_double_dash_that_differs_from_the_trial_s_is_refused(project, args):
    project.ticket()
    project.refused(args[1], "trial-1", args=args, trial=project.trial())


def test_a_trial_s_effort_below_the_floor_is_accepted(project):
    project.ticket()
    project.launch(trial=project.trial(effort="low"))
    assert (project.last()["effort"], project.last()["effort_source"]) == ("low", "trial")


def test_a_trial_s_max_needs_a_reason(project):
    project.ticket()
    trial = project.trial(effort="max")
    project.refused("--reason", trial=trial)
    project.launch(trial=trial, reason="measured")
    assert project.last()["effort_reason"] == "measured"


@pytest.mark.parametrize("change", (
    {"role": "research"}, {"criticality": "C3"}, {"criticality": "C9"}, {"model": "haiku"}, {"model": ...},
    {"effort": "extreme"}, {"effort": ...}, {"tickets": ["T-1"]}, {"tickets": ["T-1", "T-1"]},
    {"tickets": ["T-x", "T-y"]}, {"tickets": "T-1"}, {"tickets": ...}, {"reviewer": ...},
    {"reviewer": {"model": SONNET}}, {"reviewer": {"model": "opus"}}, {"reviewer": OPUS}, {"role": ...},
    {"criticality": ...}, {"extra": 1},
))
def test_a_trial_that_does_not_fit_refuses_naming_the_file_and_the_field(project, change):
    project.ticket()
    trial = project.trial(**change)
    error = project.refused(f"{launcher.TRIALS_REL}/{trial}.yaml", next(iter(change)), trial=trial)
    assert "its " + next(iter(change)) in error.message


def test_a_trial_names_this_launch_s_ticket_by_its_wbs_id_as_well(project):
    project.ticket()
    project.launch(trial=project.trial(tickets=["W9-1", "T-z"]))
    assert project.last()["trial"] == "trial-1"


@pytest.mark.parametrize("text", ("", "- a\n", "role: [\n", "role: engineer\nrole: engineer\n"))
def test_a_trial_file_that_is_not_a_map_or_not_yaml_refuses(project, text):
    project.ticket()
    path = project.root / launcher.TRIALS_REL / "t.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    project.refused("trials/t.yaml", trial="t")


def test_a_missing_trial_file_refuses_naming_it(project):
    project.ticket()
    project.refused("trials/nope.yaml", trial="nope")


@pytest.mark.parametrize("trial", ("../x", "-a", ".a", "a/b", "a b", ""))
def test_a_bad_trial_id_is_refused(project, trial):
    project.ticket()
    project.refused("--trial", trial=trial)


# --- promotion (S5) -------------------------------------------------------------------------------------------

FAIL_OPEN = {"kpis": [{"kpi": "S1", "verdict": "fail", "findings": [
    {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}]}
CLEAN = {"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [
    {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}]}]}


def test_a_fail_open_finding_promotes_the_next_round_to_opus_at_the_table_s_effort(project):
    project.ticket(allowed=["notes/a.md"])  # C0 on haiku, low: opus at low
    rel = project.probe("T-1", "r1.md", judgement="pass", verdict=FAIL_OPEN)
    argv = project.launch()
    assert (_flag(argv, "--model"), _flag(argv, "--effort")) == (OPUS, "low")
    record = project.last()
    assert (record["model"], record["model_source"], record["tier"], record["subagent_model"]) == (OPUS, "promotion", "opus", OPUS)
    assert (record["effort"], record["effort_source"]) == ("low", "by criticality")
    assert record["promotion"] == {"reason": "a fail-open finding", "record": rel}


def test_two_failed_reviews_promote_and_name_the_second_failed_record(project):
    project.ticket()
    project.probe("T-1", "a.md", judgement="failed")
    project.probe("T-1", "sub/b.md", judgement="fail")
    project.probe("T-1", "c.md", judgement="passed")
    project.launch()
    assert project.last()["promotion"] == {"reason": "two failed reviews", "record": "docs/probes/T-1/sub/b.md"}
    assert project.last()["model"] == OPUS


def test_a_fail_open_finding_is_checked_before_two_failed_reviews(project):
    project.ticket()
    project.probe("T-1", "a.md", judgement="failed")
    project.probe("T-1", "b.md", judgement="failed")
    rel = project.probe("T-1", "z.md", judgement="pass", verdict=FAIL_OPEN)
    project.launch()
    assert project.last()["promotion"] == {"reason": "a fail-open finding", "record": rel}


def test_one_failed_review_and_clean_records_do_not_promote(project):
    project.ticket()
    project.probe("T-1", "a.md", judgement="failed", verdict=CLEAN)
    project.probe("T-1", "b.md", judgement="passed", verdict=CLEAN)
    project.launch()
    record = project.last()
    assert (record["model"], record["model_source"], record["promotion"]) == (SONNET, "by criticality", None)


def test_the_promotion_applies_to_every_worker_role_on_the_ticket(project):
    project.ticket()
    project.probe("T-1", "a.md", judgement="pass", verdict=FAIL_OPEN)
    project.launch("independent-test-designer")
    assert project.last()["model"] == OPUS


def test_the_records_of_another_ticket_do_not_promote(project):
    project.ticket()
    project.probe("T-other", "a.md", judgement="pass", verdict=FAIL_OPEN)
    project.launch()
    assert project.last()["promotion"] is None


def test_a_record_that_is_not_a_probe_or_has_no_front_matter_is_skipped(project):
    project.ticket()
    project.probe("T-1", "a.md", front={"type": "note", "judgement": "failed"})
    project.probe("T-1", "b.md", front={"type": "note", "judgement": "failed"})
    (project.root / "docs/probes/T-1/c.md").write_text("no front matter\n```verdict\nnot json\n```\n")
    (project.root / "docs/probes/T-1/d.md").write_text("---\n- a list\n---\n")
    (project.root / "docs/probes/T-1/e.txt").write_text("---\ntype: probe\njudgement: failed\n---\n")
    project.launch()
    assert project.last()["promotion"] is None


@pytest.mark.parametrize("make", (
    lambda p: p.probe("T-1", "a.md", front="type: probe\n  bad: [\n"),
    lambda p: p.probe("T-1", "a.md", judgement="pass", verdict="not json"),
    lambda p: p.probe("T-1", "a.md", judgement="pass", verdict={"kpis": "x"}),
    lambda p: p.probe("T-1", "a.md", judgement="pass", verdict={"kpis": [{"kpi": "S1"}]}),
    lambda p: p.probe("T-1", "a.md", judgement="pass", verdict={"kpis": [{"findings": ["x"]}]}),
    lambda p: p.probe("T-1", "a.md", judgement="pass", verdict=[1]),
))
def test_an_unreadable_probe_record_refuses_naming_it(project, make):
    project.ticket()
    make(project)
    project.refused("docs/probes/T-1/a.md")


def test_a_promotion_refuses_a_model_after_the_double_dash_and_a_trial(project):
    project.ticket()
    project.probe("T-1", "a.md", judgement="pass", verdict=FAIL_OPEN)
    project.refused(HAIKU, OPUS, args=["--model", HAIKU])
    project.refused("promotion", trial=project.trial())
    project.launch(args=["--model", OPUS])
    assert (project.last()["model"], project.last()["model_source"]) == (OPUS, "promotion")


def test_a_promotion_with_no_criticality_file_refuses(project):
    project.role_file("engineer", pair(SONNET, "high"))
    (project.root / "governance/project/criticality.yaml").unlink()
    project.ticket()
    project.probe("T-1", "a.md", judgement="pass", verdict=FAIL_OPEN)
    project.refused("governance/project/criticality.yaml")


# --- a FULL ticket's two reviews (S4) -------------------------------------------------------------------------

def _review(project, **keywords):
    return project.launch("independent-auditor", "T-a", **keywords)


@pytest.fixture
def full(project):
    project.ticket("T-a", role="engineer", profile="FULL", allowed=["src/x/**"])
    return project


def test_round_one_takes_the_table_and_round_two_is_the_probe_at_max(full):
    _review(full)
    first = full.last()
    assert (first["model"], first["effort"], first["review_round"], first["criticality"]) == (OPUS, "high", 1, "C2")
    assert (first["model_source"], first["effort_source"]) == ("role default", "role default")
    argv = _review(full)
    second = full.last()
    assert (_flag(argv, "--model"), _flag(argv, "--effort")) == (OPUS, "max")
    assert (second["model"], second["effort"], second["review_round"]) == (OPUS, "max", 2)
    assert (second["effort_source"], second["effort_reason"]) == ("probe", None)
    assert second["model_source"] == "role default"  # the probe did not change the model


def test_the_probe_sets_the_model_when_the_table_s_is_lower(full):
    full.role_file("independent-auditor", pair(SONNET, "high"))
    _review(full)
    assert (full.last()["model"], full.last()["model_source"]) == (SONNET, "role default")
    _review(full)
    assert (full.last()["model"], full.last()["model_source"], full.last()["effort"]) == (OPUS, "probe", "max")


def test_the_same_setting_twice_is_refused_unless_the_owner_named_it(full):
    _review(full)
    _review(full)
    first, second = (next(r for r in full.records() if r["review_round"] == n) for n in (1, 2))
    error = full.refused(first["model"], "max", second["session_id"], role="independent-auditor", tid="T-a")
    assert "--owner-named" in error.message
    _review(full, owner_named="DEC-1010")
    third = full.last()
    assert (third["review_round"], third["owner_named"], third["effort"]) == (3, "DEC-1010", "max")


def test_an_effort_after_the_double_dash_on_round_two_is_accepted_if_not_below_the_floor(full):
    _review(full)
    full.refused("high", args=["--effort", "medium"], role="independent-auditor", tid="T-a")
    full.refused("--reason", args=["--effort", "max"], role="independent-auditor", tid="T-a")
    _review(full, args=["--effort", "xhigh"])
    assert (full.last()["effort"], full.last()["effort_source"], full.last()["review_round"]) == ("xhigh", "after --", 2)


def test_max_on_round_two_chosen_after_the_double_dash_needs_a_reason_not_the_probe(full):
    _review(full)
    _review(full, args=["--effort", "max"], reason="the probe, as the plan says")
    assert (full.last()["effort_source"], full.last()["effort_reason"]) == ("after --", "the probe, as the plan says")


@pytest.mark.parametrize("value", ("DEC", "dec-1", "DEC-", "DEC-1x", "1010", " DEC-1", ""))
def test_a_malformed_owner_named_is_refused(project, value):
    project.ticket()
    project.refused("--owner-named", owner_named=value)


def test_a_launch_that_is_not_an_auditor_on_a_full_ticket_has_no_round_and_no_probe(project):
    project.ticket("T-s", profile="STANDARD")
    project.ticket("T-f", profile="FULL")
    for tid in ("T-s", "T-s", "T-s"):
        project.launch("independent-auditor", tid)
        record = project.last()
        assert (record["review_round"], record["effort"], record["effort_source"]) == (None, "high", "role default")
    project.launch("independent-test-designer", "T-f")
    project.launch("independent-test-designer", "T-f")
    assert project.last()["review_round"] is None and project.last()["effort"] == "high"


def test_a_launch_record_of_another_ticket_role_or_a_resume_is_not_counted(full):
    full.ticket("T-b", profile="FULL")
    full.launch("independent-auditor", "T-b")
    full.launch("independent-test-designer", "T-a")
    full.launch("engineer", "T-a")
    _review(full)
    assert full.last()["review_round"] == 1
    planted = {"record": "gov-launch", "session_id": "11111111-1111-4111-8111-111111111111", "ticket": "T-a",
               "role": "independent-auditor", "resumes": "22222222-2222-4222-8222-222222222222",
               "model": OPUS, "effort": "max", "started_at": "2026-01-01T00:00:00Z"}
    folder = full.root / ".gov-runtime/launches"
    (folder / f"{planted['session_id']}.json").write_text(json.dumps(planted))
    _review(full)
    assert full.last()["review_round"] == 2 and full.last()["effort"] == "max"


def test_the_record_of_the_session_being_resumed_is_left_out_of_the_count(full):
    _review(full)
    original = full.last()
    assert (original["review_round"]) == 1
    # a resume needs the original's record to be of the record's form; resumed launches count as a round of their own
    argv = _review(full, args=["--resume", original["session_id"]])
    assert full.last()["review_round"] == 1 and "--fork-session" in argv


def test_a_launch_record_that_is_not_json_refuses_a_full_auditor_launch_naming_it(full):
    folder = full.root / ".gov-runtime/launches"
    folder.mkdir(parents=True)
    (folder / "bad.json").write_text("{", encoding="utf-8")
    full.refused("bad.json", role="independent-auditor", tid="T-a")
    full.ticket("T-s", profile="STANDARD")
    full.launch("independent-auditor", "T-s")  # not FULL: no count


# --- refusals leave nothing; the plan and the lead are untouched ---------------------------------------------------

def test_every_refusal_comes_before_the_gate_the_temp_folder_and_the_record(project, monkeypatch):
    made = []
    monkeypatch.setattr(launcher.tempfile, "mkdtemp", lambda **kw: made.append(kw) or "/nonexistent")
    monkeypatch.setattr(launcher, "_admit_start", lambda *a, **k: made.append("gate"))
    project.ticket()
    project.refused(args=["--effort", "low"])
    project.refused(args=["--model", HAIKU])
    project.refused(args=["--effort", "max"])
    project.refused(trial="nope")
    assert made == []


def test_the_plan_prints_the_default_line_alone(project, capsys):
    project.ticket(allowed=["notes/a.md"])
    assert launcher.plan(project.root, "engineer", "T-1") == 0
    assert capsys.readouterr().out == f"model {SONNET}, effort high\n"


def test_a_lead_launch_is_untouched(project, monkeypatch):
    monkeypatch.setattr(launcher, "check_lead", lambda root, tid: {"admitted": True, "reason": "", "override": None})
    project.ticket()
    assert launcher.launch(project.root, "orchestrator", "T-1", ["-p", "go"]) == 0
    assert project.records() == []


def test_tier_is_the_family_word_of_the_model_id():
    for model, tier in ((OPUS, "opus"), ("claude-haiku-4-5-20251001", "haiku"), (SONNET, "sonnet")):
        assert model.split("-")[1] == tier
