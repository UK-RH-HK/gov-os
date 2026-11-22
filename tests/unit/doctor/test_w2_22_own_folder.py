"""Unit tests for W2-22 fix F2 (audit 3, M-04): where doctor looks for a tool installed in its own folder."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.parametrize("name,binary", [
    ("node", "node"), ("node-22.23.5", "node"), ("node-v22.23.5", "node"), ("rea-agents", "rea"),
    ("check-jsonschema", "check-jsonschema"), ("ticket", "tk"), ("unknown-tool", "unknown-tool"),
])
def test_binary_name_of_a_registry_name(name, binary):
    from gov.doctor.command import _binary_name
    assert _binary_name(name) == binary


def test_install_line_prefix_reads_the_process_home(monkeypatch, tmp_path):
    from gov.doctor.command import _extract_path_prefix
    monkeypatch.setenv("HOME", str(tmp_path))
    assert _extract_path_prefix("PATH=$HOME/.nvm/versions/node/v22.23.5/bin:$PATH npm i") == \
        str(tmp_path / ".nvm/versions/node/v22.23.5/bin")
    assert _extract_path_prefix("PATH=~/x/bin:$PATH npm i") == str(tmp_path / "x/bin")


def test_install_folder_is_the_cd_of_a_local_install(monkeypatch, tmp_path):
    from gov.doctor.command import _install_folder
    monkeypatch.setenv("HOME", str(tmp_path))
    line = "cd ~/runs/tool && PATH=$HOME/n/bin:$PATH npm install --save-exact rea-agents@6.10.1"
    assert _install_folder(line) == tmp_path / "runs/tool"
    assert _install_folder(f"cd $HOME/runs/tool && npm install rea-agents@1") == tmp_path / "runs/tool"
    assert _install_folder("npm install -g ccusage@1") is None
    assert _install_folder("cd ~/x && npm install -g ccusage@1") is None


def test_own_places_of_a_node_is_its_nvm_folder(monkeypatch, tmp_path):
    from gov.doctor.command import _own_dirs
    monkeypatch.setenv("HOME", str(tmp_path))
    entry = {"install": "bash -c '. ~/.nvm/nvm.sh && nvm install 22.23.5'"}
    assert _own_dirs("node-22.23.5", entry, "v22.23.5") == [tmp_path / ".nvm/versions/node/v22.23.5/bin"]


def test_own_places_of_a_local_install_is_node_modules_bin(monkeypatch, tmp_path):
    from gov.doctor.command import _own_dirs
    monkeypatch.setenv("HOME", str(tmp_path))
    entry = {"install": "cd ~/runs/tool && PATH=$HOME/n/bin:$PATH npm install rea-agents@6.10.1"}
    assert _own_dirs("rea-agents", entry, "6.10.1") == [tmp_path / "runs/tool/node_modules/.bin"]
