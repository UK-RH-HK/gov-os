"""Builder tests for the worker session launcher (W1-46).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the strict check itself, the names the ``.gov-runtime`` rules
cover, the host form of the allowlist, and a refusal that leaves no temp
directory behind.
"""
from __future__ import annotations

import fnmatch
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import launcher  # noqa: E402

STRICT = {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
          "network": {"strictAllowlist": True, "allowedDomains": []}}


def test_a_strict_block_has_no_fault():
    assert launcher.sandbox_faults({"sandbox": STRICT}) == []


@pytest.mark.parametrize("change", (
    {"enabled": False}, {"failIfUnavailable": "true"}, {"allowUnsandboxedCommands": None},
    {"network": {"strictAllowlist": False}}, {"network": None}, {"excludedCommands": []},
))
def test_a_weaker_block_is_a_fault(change):
    assert len(launcher.sandbox_faults({"sandbox": {**STRICT, **change}})) == 1


def test_no_sandbox_block_is_every_fault():
    assert len(launcher.sandbox_faults({})) == 4


def _names(root):
    prefix = f"Edit(/{root}/.gov-runtime/"
    return [rule[len(prefix):-1] for rule in launcher._runtime_rules(root)]


@pytest.mark.parametrize("name, covered", (
    ("freeze", True), ("findings.jsonl", True), ("snapshots", True), ("s", True), ("scratc", True),
    ("scratchy", True), ("scratch.bak", True), ("Scratch", True), ("scratch", False),
))
def test_the_runtime_rules_cover_every_name_but_scratch(tmp_path, name, covered):
    assert any(fnmatch.fnmatchcase(name, pattern) for pattern in _names(tmp_path)) is covered


def test_the_runtime_rules_name_the_entries_that_exist_at_launch(tmp_path):
    for name in ("records.jsonl", "snapshots", "scratch"):
        (tmp_path / ".gov-runtime" / name).mkdir(parents=True)
    names = _names(tmp_path)
    assert {"records.jsonl", "snapshots", "freeze"} <= set(names) and "scratch" not in names


@pytest.mark.parametrize("entry, valid", (
    ("pypi.org", True), ("*.readthedocs.io", True), ("cdn-lfs.huggingface.co", True),
    ("*", False), ("*.org.*", False), ("localhost", False), ("https://pypi.org", False), ("pypi.org/simple", False),
    ("PyPI.org", False), ("pypi.org ", False), ("", False),
))
def test_an_allowlist_entry_is_a_host_name_or_its_subdomain_form(tmp_path, entry, valid):
    (tmp_path / "list.yaml").write_text(f"hosts:\n- '{entry}'\n", encoding="utf-8")
    if valid:
        assert launcher._hosts(tmp_path, "list.yaml") == [entry]
    else:
        with pytest.raises(GovError):
            launcher._hosts(tmp_path, "list.yaml")


def test_a_missing_kernel_default_refuses(tmp_path):
    with pytest.raises(GovError):
        launcher._research_allowlist(tmp_path)


def test_a_refused_launch_leaves_no_temp_directory(tmp_path, monkeypatch):
    made = []
    monkeypatch.setattr(launcher.tempfile, "mkdtemp", lambda **kw: made.append(kw) or str(tmp_path))
    with pytest.raises(GovError):
        launcher.launch(tmp_path, "engineer", "DAEO-none", [])
    assert made == []
