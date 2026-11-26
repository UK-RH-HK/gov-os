"""W2-20 fix SP-1 and SP-2: ``gov.resources.toolpath``, the registry's pinned Node folder for a test run's ``PATH``."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from gov.resources import toolpath  # noqa: E402


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    return tmp_path / "home"


def _node(folder: Path) -> Path:
    folder.mkdir(parents=True)
    (folder / "node").write_text("#!/bin/sh\n", encoding="utf-8")
    return folder


def _registry(root: Path, text: str) -> Path:
    path = root / "governance" / "project" / "tool-registry.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return root


def _entry(version: str, install: str = "nvm install") -> str:
    return f'tools:\n  - name: node\n    version: "{version}"\n    install: "{install}"\n'


@pytest.mark.parametrize("written", ["v9.8.7", "9.8.7"])
def test_the_nvm_folder_of_the_pin_has_a_single_v(tmp_path, home, written):
    folder = _node(home / ".nvm/versions/node/v9.8.7/bin")
    found = toolpath.node_prefix(_registry(tmp_path / "project", _entry(written)))
    assert found == {"prefix": str(folder), "version": written, "reason": None}


@pytest.mark.parametrize("line", ["PATH=$HOME/own/bin:$PATH node -v", "PATH=~/own/bin:$PATH node -v"])
def test_the_install_lines_path_prefix_is_read_from_the_process_home(tmp_path, home, line):
    folder = _node(home / "own/bin")
    assert toolpath.node_prefix(_registry(tmp_path / "project", _entry("v9.8.7", line)))["prefix"] == str(folder)


@pytest.mark.parametrize("text", [None, "tools: [unclosed\n", "\x00", "- a list\n",
                                  "tools: 3\n", "tools:\n  - name: node\n"])
def test_a_registry_that_gives_no_node_is_named_and_leaves_the_environment(tmp_path, home, text):
    root = tmp_path / "project" if text is None else _registry(tmp_path / "project", text)
    found = toolpath.node_prefix(root)
    assert found["prefix"] is None and "node" in found["reason"]
    env = {"PATH": "/usr/bin", "A": "b"}
    assert toolpath.with_node(env, root) == env


def test_an_entry_whose_folder_holds_no_node_names_the_version_and_the_folder(tmp_path, home):
    found = toolpath.node_prefix(_registry(tmp_path / "project", _entry("v9.8.7")))
    assert found["prefix"] is None
    assert "9.8.7" in found["reason"] and str(home / ".nvm/versions/node/v9.8.7/bin") in found["reason"]


def test_the_prefix_is_first_once_in_a_copy(tmp_path, home):
    folder = str(_node(home / ".nvm/versions/node/v9.8.7/bin"))
    root = _registry(tmp_path / "project", _entry("v9.8.7"))
    env = {"PATH": "/usr/bin"}
    once = toolpath.with_node(env, root)
    assert once["PATH"] == folder + os.pathsep + "/usr/bin"
    assert toolpath.with_node(once, root)["PATH"] == once["PATH"]
    assert env == {"PATH": "/usr/bin"}
    assert toolpath.with_node({}, root)["PATH"] == folder + os.pathsep + os.defpath
