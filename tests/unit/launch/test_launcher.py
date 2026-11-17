"""Builder tests for the worker session launcher (W1-46).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the arguments that replace the launcher's settings, and a
refusal that leaves no temp directory behind.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import launcher  # noqa: E402


@pytest.mark.parametrize("args", (["-p", "x", "--setting-sources", "user"], ["--setting-sources=project"],
                                  ["--settings", "{}"], ["--settings={}"]))
def test_an_argument_that_takes_the_settings_away_refuses(args):
    with pytest.raises(GovError):
        launcher._check_cli_args(args)


def test_a_prompt_that_names_an_argument_as_a_word_passes():
    launcher._check_cli_args(["-p", "Do not use --bare.", "--model", "haiku"])


def test_a_refused_launch_leaves_no_temp_directory(tmp_path, monkeypatch):
    made = []
    monkeypatch.setattr(launcher.tempfile, "mkdtemp", lambda **kw: made.append(kw) or str(tmp_path))
    with pytest.raises(GovError):
        launcher.launch(tmp_path, "engineer", "DAEO-none", [])
    assert made == []
