"""W2-121c builder tests: the launcher's end message (RT-2) and the launch record's rubric (RT-8, a quiet launch).

A stand-in replaces ``subprocess.Popen`` (from W2-184's builder tests) and runs a real short process, so the session has
a pid and a registry entry; everything is under a temporary HOME.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from gov.dispatch import inbox
from gov.launch import launcher

from .test_w2_184_launch import Project

REAL_POPEN = subprocess.Popen


@pytest.fixture
def project(tmp_path, monkeypatch):
    found = Project(tmp_path, monkeypatch)
    monkeypatch.delenv("GOV_MSG_ADDRESS", raising=False)

    class Session(REAL_POPEN):
        def __init__(self, argv, cwd=None, env=None, **_):
            found.started.append(argv)
            found.envs.append(env)
            super().__init__([sys.executable, "-c", "import sys; sys.exit(3)"], start_new_session=True)

    monkeypatch.setattr(launcher.subprocess, "Popen", Session)
    return found


def test_the_end_is_one_wake_to_the_launching_address(project, monkeypatch):
    monkeypatch.setenv("GOV_MSG_ADDRESS", "lead:DAEO-x")
    project.ticket()
    assert launcher.launch(project.root, "engineer", "T-1", []) == 3
    [message] = inbox.read("lead:DAEO-x", peek=True)["messages"]
    assert message["kind"] == "wake" and message["id"].startswith("end:")
    assert "engineer" in message["text"] and "T-1" in message["text"] and "3" in message["text"]
    assert message["data"]["exit_code"] == 3
    assert project.envs[-1]["GOV_MSG_ADDRESS"] == "engineer:T-1"


def test_without_an_address_the_end_goes_to_cto(project):
    project.ticket()
    launcher.launch(project.root, "engineer", "T-1", [])
    assert len(inbox.read("cto", peek=True)["messages"]) == 1


def test_a_failed_send_keeps_the_exit_code(project, monkeypatch):
    project.ticket()

    def broken(*args, **kwargs):
        raise OSError("disk full")
    monkeypatch.setattr(inbox, "send", broken)
    assert launcher.launch(project.root, "engineer", "T-1", []) == 3


def test_the_record_names_model_effort_sources_class_and_rubric_and_the_launch_is_quiet(project, capfd):
    project.ticket()
    launcher.launch(project.root, "engineer", "T-1", [])
    out, err = capfd.readouterr()
    assert (out, err) == ("", "")
    record = project.records()[-1]
    assert (record["model"], record["model_source"], record["effort"], record["effort_source"]) == \
        ("claude-sonnet-5-5", "by criticality", "high", "by criticality")
    assert record["criticality"] == "C2" and record["rubric"] == "governance/project/criticality.yaml"


def test_no_rubric_is_null_and_the_role_default(project, capfd):
    (project.root / "governance/project/criticality.yaml").unlink()
    project.ticket()
    launcher.launch(project.root, "engineer", "T-1", [])
    assert capfd.readouterr() == ("", "")
    record = project.records()[-1]
    assert record["rubric"] is None and record["model_source"] == "role default"
