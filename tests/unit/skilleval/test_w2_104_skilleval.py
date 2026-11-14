"""W2-104 (DAEO-drhj): builder tests of ``gov skilleval``, the skill evaluation harness (DEC-959 item 5).

Each test plants a skill in a temporary project and puts a stub ``claude`` on a PATH of its own (the stub's
folder, ``/usr/bin`` and ``/bin``): no real model, no network, no key.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml

from gov.cli.main import main
from gov.skilleval import harness

SECRET = "-".join(("PLANTED", "SECRET", "5b9e"))  # put in the environment and the stub's stderr: must never reach the caller

STUB = """#!/usr/bin/python3
import json, os, sys, time
prompt = sys.stdin.read()
judge = "VERDICT: PASS" in prompt
mode = os.environ.get("STUB_MODE", "ok")
skills = os.path.join(os.getcwd(), ".claude", "skills")
listing = sorted(os.listdir(skills)) if os.path.isdir(skills) else None
files = sorted(os.listdir(os.path.join(skills, listing[0]))) if listing else None
with open(os.environ["STUB_LOG"], "a") as log:
    log.write(json.dumps({"argv": sys.argv[1:], "cwd": os.getcwd(), "judge": judge, "prompt": prompt,
                          "skills": listing, "files": files}) + "\\n")
sys.stderr.write("stderr " + os.environ.get("FAKE_SECRET", "") + "\\n")
if mode == "exit1" or (mode == "judge_exit1" and judge):
    sys.exit(1)
if mode == "badjson":
    print("not json " + os.environ.get("FAKE_SECRET", ""))
    sys.exit(0)
if mode == "is_error":
    print(json.dumps({"result": "x", "is_error": True, "total_cost_usd": 0.1}))
    sys.exit(0)
if mode == "sleep":
    time.sleep(5)
if judge:
    text = "looks fine" if mode == "noverdict" else "reasons\\nVERDICT: FAIL" if "FAILME" in prompt else "ok\\nVERDICT: PASS"
else:
    text = "did it: " + prompt + " " + os.environ.get("FAKE_SECRET", "")
print(json.dumps({"result": text, "is_error": False, "total_cost_usd": 0.25 if judge else 0.5}))
"""


def scenarios_md(situations=("first", "second", "third")) -> str:
    parts = ["# demo: the three scenarios", "", "Intro text.", ""]
    for n, situation in enumerate(situations, 1):
        parts += [f"## {n}. Scenario {n}", "",
                  f"- **Situation:** {situation} situation",
                  "  that runs over two lines.",
                  f"- **Expected:** expected {n}.",
                  f"- **Pass line:** PASSLINE-{n} holds.", ""]
    return "\n".join(parts)


def plant_skill(root: Path, folder="skills/demo", name="demo", version='"1.2.0"', scenarios=None) -> Path:
    skill = root / folder
    skill.mkdir(parents=True)
    front = ["---", f"name: {name}"] + ([f"version: {version}"] if version else []) + ["---"]
    (skill / "SKILL.md").write_text("\n".join(front + ["# Demo", "Body."]), encoding="utf-8")
    (skill / "reference.md").write_text("detail\n", encoding="utf-8")
    if scenarios is not False:
        (skill / "scenarios.md").write_text(scenarios or scenarios_md(), encoding="utf-8")
    return skill


@pytest.fixture
def project(tmp_path, monkeypatch):
    root, bin_dir, temp = tmp_path / "proj", tmp_path / "bin", tmp_path / "tmp"
    for folder in (root, bin_dir, temp):
        folder.mkdir()
    stub = bin_dir / "claude"
    stub.write_text(STUB, encoding="utf-8")
    stub.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:/usr/bin:/bin")
    monkeypatch.setenv("STUB_LOG", str(tmp_path / "stub.log"))
    monkeypatch.setenv("FAKE_SECRET", SECRET)
    monkeypatch.setenv("TMPDIR", str(temp))
    monkeypatch.setattr(tempfile, "tempdir", str(temp))
    return root, tmp_path / "stub.log", stub


def skilleval(root: Path, capsys, *extra: str) -> tuple[int, dict, str]:
    code = main(["skilleval", "skills/demo", "--json", "--root", str(root), *extra])
    out, err = capsys.readouterr()
    return code, json.loads(out), out + err


def calls(log: Path) -> list[dict]:
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


def records(root: Path) -> list[dict]:
    return yaml.safe_load((root / "skills/demo/scenario-records.yaml").read_text())["records"]


# --- the scenarios' form -------------------------------------------------------------------------------------------

def test_w2_104_parses_three_scenarios_with_continued_bullets():
    parsed = harness.parse_scenarios(scenarios_md())
    assert [s["n"] for s in parsed] == [1, 2, 3]
    assert parsed[0]["situation"] == "first situation that runs over two lines."
    assert parsed[2]["pass_line"] == "PASSLINE-3 holds."


@pytest.mark.parametrize("break_it", [
    lambda root: plant_skill(root, version=None),
    lambda root: plant_skill(root, scenarios=False),
    lambda root: plant_skill(root, scenarios=scenarios_md(("a", "b"))),
    lambda root: plant_skill(root, scenarios=scenarios_md(("a", "b", "c", "d"))),
    lambda root: plant_skill(root, scenarios=scenarios_md().replace("- **Expected:** expected 2.", "")),
    lambda root: (root / "skills/demo").mkdir(parents=True),
])
def test_w2_104_unevaluable_skill_exits_5_runs_and_records_nothing(project, capsys, break_it):
    root, log, _ = project
    break_it(root)
    code, envelope, _ = skilleval(root, capsys)
    assert code == 5 and envelope["ok"] is False
    assert not calls(log)
    assert not (root / "skills/demo/scenario-records.yaml").exists()


# --- verdicts and the record ---------------------------------------------------------------------------------------

def test_w2_104_all_pass_records_beside_the_skill(project, capsys):
    root, log, _ = project
    plant_skill(root)
    code, envelope, _ = skilleval(root, capsys)
    assert code == 0 and envelope["ok"] is True
    result = envelope["result"]
    assert (result["skill"], result["skill_version"], result["adopted"]) == ("demo", "1.2.0", None)
    assert [s["verdict"] for s in result["scenarios"]] == ["pass"] * 3
    assert all(s["cost_usd"] == 0.75 and s["cause"] is None for s in result["scenarios"])
    assert Path(result["record"]) == (root / "skills/demo/scenario-records.yaml").resolve()
    entries = records(root)
    assert [e["scenario"] for e in entries] == [1, 2, 3]
    for entry in entries:
        assert entry["skill"] == "demo" and entry["skill_version"] == "1.2.0" and entry["verdict"] == "pass"
        assert entry["model"] == "claude-opus-5-5" and entry["effort"] == "high"
        assert isinstance(entry["seconds"], float) and entry["run_at"].endswith("+00:00")
    assert len(calls(log)) == 6


def test_w2_104_a_failing_scenario_fails_and_exits_3(project, capsys):
    root, _, _ = project
    plant_skill(root, scenarios=scenarios_md(("ok", "FAILME", "ok")))
    code, envelope, _ = skilleval(root, capsys)
    assert code == 3
    assert [s["verdict"] for s in envelope["result"]["scenarios"]] == ["pass", "fail", "pass"]
    assert envelope["result"]["scenarios"][1]["cause"]


def test_w2_104_no_verdict_line_is_a_fail(project, capsys, monkeypatch):
    root, _, _ = project
    plant_skill(root)
    monkeypatch.setenv("STUB_MODE", "noverdict")
    code, envelope, _ = skilleval(root, capsys)
    assert code == 3 and {s["verdict"] for s in envelope["result"]["scenarios"]} == {"fail"}


def test_w2_104_verdict_is_the_last_verdict_line():
    assert harness.judge_verdict("VERDICT: PASS\nVERDICT: FAIL")[0] == "fail"
    assert harness.judge_verdict("VERDICT: FAIL\n  VERDICT: PASS  ")[0] == "pass"
    assert harness.judge_verdict("verdict: pass\n**VERDICT: PASS**")[0] == "fail"


@pytest.mark.parametrize("mode, step", [("exit1", "session"), ("judge_exit1", "judgement"), ("badjson", "session"),
                                        ("is_error", "session")])
def test_w2_104_a_model_that_does_not_answer_is_not_run(project, capsys, monkeypatch, mode, step):
    root, _, _ = project
    plant_skill(root)
    monkeypatch.setenv("STUB_MODE", mode)
    code, envelope, text = skilleval(root, capsys)
    assert code == 4
    for scenario in envelope["result"]["scenarios"]:
        assert scenario["verdict"] == "not-run" and scenario["cost_usd"] is None
        assert scenario["cause"].startswith(step) and "\n" not in scenario["cause"]
    assert [e["verdict"] for e in records(root)] == ["not-run"] * 3
    assert SECRET not in text and SECRET not in (root / "skills/demo/scenario-records.yaml").read_text()


def test_w2_104_no_claude_on_the_path_is_not_run(project, capsys):
    root, _, stub = project
    plant_skill(root)
    stub.unlink()
    code, envelope, _ = skilleval(root, capsys)
    assert code == 4
    assert {s["cause"] for s in envelope["result"]["scenarios"]} == {"session: no claude on the PATH"}


def test_w2_104_a_timeout_is_not_run(project, capsys, monkeypatch):
    root, _, _ = project
    plant_skill(root)
    monkeypatch.setenv("STUB_MODE", "sleep")
    code, envelope, _ = skilleval(root, capsys, "--timeout", "0.5")
    assert code == 4 and "timed out" in envelope["result"]["scenarios"][0]["cause"]


def test_w2_104_records_are_appended(project, capsys):
    root, _, _ = project
    plant_skill(root)
    skilleval(root, capsys)
    skilleval(root, capsys)
    assert len(records(root)) == 6


def test_w2_104_invalid_record_refuses_before_running(project, capsys):
    root, log, _ = project
    plant_skill(root)
    (root / "skills/demo/scenario-records.yaml").write_text("- not a map\n")
    code, envelope, _ = skilleval(root, capsys)
    assert code == 1 and envelope["error"]["code"] == "RECORD_INVALID" and not calls(log)


# --- the sessions ----------------------------------------------------------------------------------------------------

def test_w2_104_fresh_sessions_with_only_the_skill(project, capsys):
    root, log, _ = project
    plant_skill(root)
    skilleval(root, capsys, "--model", "m-x", "--effort", "low")
    session, judgement = calls(log)[:2]
    for call in (session, judgement):
        argv = call["argv"]
        assert argv[:7] == ["-p", "--model", "m-x", "--effort", "low", "--output-format", "json"]
        assert "--resume" not in argv and "--continue" not in argv
        assert not Path(call["cwd"]).is_relative_to(root) and not Path(call["cwd"]).exists()
    assert session["cwd"] != judgement["cwd"]
    assert session["skills"] == ["demo"] and session["files"] == ["SKILL.md", "reference.md"]
    assert "first situation" in session["prompt"] and "PASSLINE-1" not in session["prompt"]
    assert judgement["skills"] is None
    assert "PASSLINE-1" in judgement["prompt"] and "expected 1." in judgement["prompt"]
    assert "did it:" in judgement["prompt"]
    assert records(root)[0]["model"] == "m-x" and records(root)[0]["effort"] == "low"


def test_w2_104_session_folder_leaves_out_scenarios_records_and_summaries(project, capsys):
    root, log, _ = project
    skill = plant_skill(root)
    (skill / "scenario-records.yaml").write_text("records: []\n", encoding="utf-8")
    (skill / "scenario-summaries.md").write_text("# Summaries\nhand-written\n", encoding="utf-8")
    code, _, _ = skilleval(root, capsys)
    assert code == 0
    files = calls(log)[0]["files"]
    assert "SKILL.md" in files
    for left_out in ("scenarios.md", "scenario-records.yaml", "scenario-summaries.md"):
        assert left_out not in files


def test_w2_104_no_secret_or_stderr_reaches_the_output(project, capsys):
    root, _, _ = project
    plant_skill(root)
    _, _, text = skilleval(root, capsys)
    assert SECRET not in text and "stderr" not in text
    assert SECRET not in (root / "skills/demo/scenario-records.yaml").read_text()


# --- imports ---------------------------------------------------------------------------------------------------------

def imports(root: Path, *entries: dict) -> Path:
    path = root / harness.IMPORTS
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# header kept\n" + yaml.safe_dump({"imports": list(entries)}, sort_keys=False))
    return path


GOOD = {"name": "demo", "source": "a collection", "version": "1.2.0", "licence": "Apache-2.0",
        "licence_verdict": "allowed", "adopted": False}
OTHER = {"name": "other", "source": "s", "version": "1", "licence": "MIT", "licence_verdict": "allowed",
         "adopted": True}


def entries(path: Path) -> list[dict]:
    return yaml.safe_load(path.read_text())["imports"]


def test_w2_104_adopts_with_a_licence_record_and_three_passes(project, capsys):
    root, _, _ = project
    plant_skill(root)
    path = imports(root, GOOD, OTHER)
    code, envelope, _ = skilleval(root, capsys, "--adopt")
    assert code == 0 and envelope["result"]["adopted"] is True
    adopted, other = entries(path)
    assert adopted["adopted"] is True and adopted["adopted_version"] == "1.2.0" and adopted["adopted_at"]
    assert other == OTHER
    assert path.read_text().startswith("# header kept\n")


@pytest.mark.parametrize("change", [
    {"licence": ""}, {"licence": None}, {"source": " "}, {"version": None}, {"licence_verdict": "denied"},
    {"licence_verdict": None},
])
def test_w2_104_refuses_adoption_without_a_licence_record(project, capsys, change):
    root, _, _ = project
    plant_skill(root)
    path = imports(root, dict(GOOD, adopted=True, **change), OTHER)
    code, envelope, _ = skilleval(root, capsys, "--adopt")
    assert code == 6 and envelope["result"]["adopted"] is False and envelope["result"]["reason"]
    assert entries(path)[0]["adopted"] is False and entries(path)[1] == OTHER


@pytest.mark.parametrize("mode, situations", [("ok", ("ok", "FAILME", "ok")), ("exit1", ("a", "b", "c"))])
def test_w2_104_refuses_adoption_unless_all_three_pass(project, capsys, monkeypatch, mode, situations):
    root, _, _ = project
    plant_skill(root, scenarios=scenarios_md(situations))
    monkeypatch.setenv("STUB_MODE", mode)
    path = imports(root, GOOD)
    code, envelope, _ = skilleval(root, capsys, "--adopt")
    assert code == 6 and envelope["result"]["adopted"] is False
    assert entries(path)[0]["adopted"] is False


def test_w2_104_refuses_adoption_with_no_entry_and_adds_none(project, capsys):
    root, _, _ = project
    plant_skill(root)
    path = imports(root, OTHER)
    before = path.read_text()
    code, _, _ = skilleval(root, capsys, "--adopt")
    assert code == 6 and path.read_text() == before
    (path).unlink()
    code, envelope, _ = skilleval(root, capsys, "--adopt")
    assert code == 6 and envelope["result"]["adopted"] is False and not path.exists()


def test_w2_104_without_adopt_adoption_is_untouched(project, capsys):
    root, _, _ = project
    plant_skill(root, scenarios=scenarios_md(("ok", "FAILME", "ok")))
    path = imports(root, dict(GOOD, adopted=True))
    before = path.read_text()
    code, envelope, _ = skilleval(root, capsys)
    assert code == 3 and envelope["result"]["adopted"] is None and path.read_text() == before


def test_w2_104_this_repository_records_no_adopted_import():
    path = Path(__file__).resolve().parents[3] / harness.IMPORTS
    assert yaml.safe_load(path.read_text()) == {"imports": []}


# --- the command line ------------------------------------------------------------------------------------------------

def test_w2_104_help_offers_skilleval(capsys):
    with pytest.raises(SystemExit) as done:
        main(["--help"])
    assert done.value.code == 0 and "skilleval" in capsys.readouterr().out
    with pytest.raises(SystemExit) as done:
        main(["skilleval", "--help"])
    assert done.value.code == 0 and "skilleval" in capsys.readouterr().out
