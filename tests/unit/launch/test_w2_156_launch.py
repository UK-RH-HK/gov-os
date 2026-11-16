"""W2-156 builder tests: ``gov launch`` and the runaway brake (S3, F3) and ``--projection-usd`` (the projection's source).

Regression evidence only (DEC-136). No CLI is started: a recording stand-in replaces ``subprocess.Popen`` under a
temporary HOME with an open resource gate, as the W2-184 launch tests do.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from gov.cli.errors import GovError
from gov.cli.main import main
from gov.launch import launcher, role as roles

SONNET = "claude-sonnet-5-5"
TICKET = "T-1"
STARTED: list[list[str]] = []  # the argv of every CLI the stand-in was asked to start


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


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    (root / launcher.TEMPLATES_REL).mkdir(parents=True)
    for stem in set(launcher.ROLE_TEMPLATES.values()):
        (root / launcher.TEMPLATES_REL / f"{stem}.md").write_text(f"# {stem}\n", encoding="utf-8")
    role = root / roles.ROLES_REL / "engineer.md"
    role.parent.mkdir(parents=True, exist_ok=True)
    role.write_text(f"# engineer\n\n- **Version:** 1.0.0\n- **Launch default:** model {SONNET}, effort high\n",
                    encoding="utf-8")
    criticality = root / "governance/project/criticality.yaml"
    criticality.parent.mkdir(parents=True, exist_ok=True)
    criticality.write_text(yaml.safe_dump({"version": 1, "default": "C2", "opus": "claude-opus-5-5", "rules": [
        {"class": "C2", "profile": "FULL"}]}), encoding="utf-8")
    front = {"id": TICKET, "wbs_id": "W9-1", "status": "in_progress", "priority": 1, "role": "engineer",
             "profile": "STANDARD", "allowed_paths": ["src/x/**"], "depends_on": [], "deps": [], "needs": []}
    (root / ".tickets").mkdir()
    (root / ".tickets" / f"{TICKET}.md").write_text("---\n" + yaml.safe_dump(front) + "---\n", encoding="utf-8")
    for name in ("GOV_ROLE", "GOV_TICKET"):
        monkeypatch.delenv(name, raising=False)
    home = tmp_path / "home"
    (home / ".local" / "bin").mkdir(parents=True)
    (home / launcher.CLI_REL).write_text("", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    _open_gate(home, monkeypatch)
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)
    STARTED.clear()

    class Session:
        def __init__(self, argv, cwd, env):
            STARTED.append(argv)

        def wait(self):
            return 0

        def poll(self):
            return 0

    monkeypatch.setattr(launcher.subprocess, "Popen", Session)
    return root


def put_marker(root: Path, ticket=TICKET, cost=6.03, projection=3.0) -> Path:
    path = root / ".gov-runtime" / "spend" / "braked" / f"{ticket}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"ticket": ticket, "cost_usd": cost, "projection_usd": projection,
                                "at": "2026-11-10T10:00:00Z"}), encoding="utf-8")
    return path


def launch_records(root: Path) -> list[dict]:
    folder = root / ".gov-runtime" / "launches"
    return [json.loads(p.read_text()) for p in sorted(folder.glob("*.json"))] if folder.is_dir() else []


def session_records(root: Path) -> list[Path]:
    folder = root / ".gov-runtime" / "sessions"
    return sorted(folder.glob("*.json")) if folder.is_dir() else []


# -- S3 / F3 -------------------------------------------------------------------------------------------------------

def test_s3_a_ticket_with_a_marker_is_refused_naming_the_marker_cost_and_projection_and_nothing_starts(project):
    marker = put_marker(project)
    with pytest.raises(GovError) as caught:
        launcher.launch(project, "engineer", TICKET, [])
    assert caught.value.code == "SPEND_BRAKED"
    message = caught.value.message
    assert str(marker) in message and "6.03" in message and "3.00" in message
    assert STARTED == [] and launch_records(project) == [] and session_records(project) == []


def test_s3_a_ticket_without_a_marker_launches_as_before(project):
    assert launcher.launch(project, "engineer", TICKET, []) == 0
    assert len(STARTED) == 1 and len(launch_records(project)) == 1


def test_s3_a_marker_of_another_ticket_does_not_hold_this_one(project):
    put_marker(project, ticket="T-2")
    assert launcher.launch(project, "engineer", TICKET, []) == 0


def test_s3_a_removed_marker_lets_the_ticket_launch(project):
    put_marker(project).unlink()
    assert launcher.launch(project, "engineer", TICKET, []) == 0


def test_s3_a_marker_that_cannot_be_read_still_refuses_naming_it(project):
    marker = put_marker(project)
    marker.write_text("{broken", encoding="utf-8")
    with pytest.raises(GovError) as caught:
        launcher.launch(project, "engineer", TICKET, [])
    assert caught.value.code == "SPEND_BRAKED" and str(marker) in caught.value.message
    assert STARTED == []


def test_s3_the_resource_gate_refuses_first_when_it_is_shut_and_a_marker_is_planted(project, monkeypatch):
    put_marker(project)
    monkeypatch.setenv("GOV_RESOURCES_BUSY_CORES", "20")  # the gate's reading: every core busy
    with pytest.raises(GovError) as caught:
        launcher.launch(project, "engineer", TICKET, [])
    assert caught.value.code == "LAUNCH_REFUSED" and "the resource gate is shut" in caught.value.message
    assert STARTED == []


# -- the projection's source ---------------------------------------------------------------------------------------

def test_the_projection_is_recorded_on_the_launch_record(project):
    assert launcher.launch(project, "engineer", TICKET, [], projection_usd=12.5) == 0
    (record,) = launch_records(project)
    assert record["projection_usd"] == 12.5


def test_without_a_projection_the_key_is_absent(project):
    assert launcher.launch(project, "engineer", TICKET, []) == 0
    (record,) = launch_records(project)
    assert "projection_usd" not in record


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), True, "3"])
def test_a_projection_that_is_not_a_number_above_zero_refuses_before_anything_starts(project, value):
    with pytest.raises(GovError) as caught:
        launcher.launch(project, "engineer", TICKET, [], projection_usd=value)
    assert caught.value.code == "LAUNCH_REFUSED" and "--projection-usd" in caught.value.message
    assert STARTED == [] and launch_records(project) == []


def test_a_lead_launch_takes_no_projection_as_it_takes_no_reason(project):
    with pytest.raises(GovError) as caught:
        launcher.launch(project, "orchestrator", TICKET, [], projection_usd=3.0)
    assert caught.value.code == "LAUNCH_REFUSED" and "--projection-usd" in caught.value.message
    assert STARTED == []


@pytest.mark.parametrize("value", ["0", "-2", "abc", "nan", "inf"])
def test_the_command_option_refuses_what_is_not_a_number_above_zero_with_a_usage_error(project, value, capsys):
    with pytest.raises(SystemExit) as stop:
        main(["launch", "engineer", TICKET, "--projection-usd", value, "--root", str(project)])
    assert stop.value.code == 2 and STARTED == []


def test_the_command_refuses_a_lead_launch_with_a_projection_as_a_usage_error(project, capsys):
    code = main(["launch", "orchestrator", TICKET, "--projection-usd", "3", "--root", str(project)])
    assert code == 2 and "--projection-usd" in capsys.readouterr().err and STARTED == []
