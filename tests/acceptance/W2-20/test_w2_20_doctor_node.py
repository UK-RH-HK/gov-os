"""W2-20 fix SP-2 (plan item 1-13, FINDINGS I-6): ``gov doctor --json``'s ``tools`` part names the Node folder the
test runs use (``node_prefix``: ``prefix``, ``version``, ``reason``), and says by name when the registry's Node is
missing. It never changes doctor's status by itself.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w2_20_tool_path_support as t

PATH_MAP = "namespaces: {}\n"


def _tools(tmp_path: Path, entries: list[dict]) -> tuple[dict, str]:
    """The ``tools`` part of ``gov doctor --json`` on a small committed project holding a registry of ``entries``."""
    home = t.plant_home(tmp_path / "home") if not (tmp_path / "home" / ".local").exists() else tmp_path / "home"
    env = t.caller_env(tmp_path, home)
    root = t.git_project(tmp_path / "project", env, {
        "governance/project/path-map.yaml": PATH_MAP,
        "governance/project/tool-registry.yaml": t.registry_text(entries)})
    _, envelope, said = t.gov(root, env, "doctor")
    tools = t.body(envelope).get("tools")
    assert isinstance(tools, dict), f"gov doctor reported no tools part\n{said}"
    return tools, said


def _prefix(tools: dict, said: str) -> dict:
    found = tools.get("node_prefix")
    assert isinstance(found, dict), f"the tools part carries no node_prefix: {sorted(tools)}\n{said}"
    assert {"prefix", "version", "reason"} <= set(found), found
    return found


@pytest.mark.parametrize("place", ["nvm folder", "path prefix"])
def test_doctor_names_the_node_prefix_the_test_runs_use(tmp_path, place):
    home = tmp_path / "home"
    if place == "nvm folder":
        folder, line = t.nvm_bin(home, t.OTHER_PIN), None
    else:
        folder, line = home / "own-node" / "bin", "PATH=$HOME/own-node/bin:$PATH node --version"
    t.plant_home(home)
    t.install_node(folder, t.OTHER_PIN)
    tools, said = _tools(tmp_path, [t.entry("node", t.OTHER_PIN, line)])
    found = _prefix(tools, said)
    assert found["prefix"] == str(folder), found
    assert str(found["version"]).lstrip("v") == t.OTHER_PIN.lstrip("v"), found


@pytest.mark.parametrize("case", ["no node entry", "only a second node entry"])
def test_doctor_says_node_when_the_registry_has_no_node_entry(tmp_path, case):
    home = t.plant_home(tmp_path / "home")
    t.install_node(t.nvm_bin(home, "v22.23.5"), "v22.23.5")
    entries = {"no node entry": [t.entry("uv", "0.12.21", "echo install")],
               "only a second node entry": [t.entry("node-22.23.5", "v22.23.5")]}[case]
    tools, said = _tools(tmp_path, entries)
    found = _prefix(tools, said)
    assert found["prefix"] is None, found
    assert "node" in str(found["reason"]).lower(), f"the reason does not name node: {found}"


@pytest.mark.parametrize("place", ["nvm folder", "path prefix"])
def test_doctor_names_node_its_version_and_the_folder_when_the_folder_holds_none(tmp_path, place):
    home = t.plant_home(tmp_path / "home")
    if place == "nvm folder":
        folder, line = t.nvm_bin(home), None
    else:  # the prefix's folder holds no node; the nvm folder does, and does not answer for it
        folder, line = home / "own-node" / "bin", "PATH=$HOME/own-node/bin:$PATH node --version"
        t.install_node(t.nvm_bin(home))
    t.stand_in(folder / t.TOOL, "1.13.2")
    tools, said = _tools(tmp_path, [t.entry("node", t.PIN, line)])
    found = _prefix(tools, said)
    assert found["prefix"] is None, found
    reason = str(found["reason"])
    assert "node" in reason.lower() and t.PIN.lstrip("v") in reason, f"node and its pin are not named: {reason}"
    assert str(folder) in reason, f"the folder looked in ({folder}) is not named: {reason}"


def test_a_missing_node_entry_does_not_change_the_tools_status(tmp_path):
    """One tool, installed at its pin, and no ``node`` entry: the tools part passes and still says why no prefix."""
    home = t.plant_home(tmp_path / "home")
    t.stand_in(home / "own" / "bin" / "w2-20-tool", "1.2.3")
    entries = [t.entry("w2-20-tool", "1.2.3", "PATH=$HOME/own/bin:$PATH echo install")]
    tools, said = _tools(tmp_path, entries)
    assert tools.get("status") == "pass", said
    assert _prefix(tools, said)["prefix"] is None
