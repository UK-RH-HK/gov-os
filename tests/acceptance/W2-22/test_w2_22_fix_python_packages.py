"""W2-22 fix F18 (fixes-015a, release 0.1.5): ``gov doctor`` checks the pytest plugins of the registry (pytest-xdist,
pytest-timeout, pytest-testmon: Python packages with no binary) as packages, by their installed version, as pyyaml is.

Observable: ``gov doctor --json``'s ``tools`` part, each entry's ``ok``, ``found_version``, ``pinned_version``. The
installed package is planted as a ``<name>-<version>.dist-info`` folder on the ``PYTHONPATH`` ``gov`` runs with (HOME is the
case's own folder, so the machine's real user site is not seen).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import w2_22_support as base

w1_27 = base.w1_27
PACKAGES = ("pytest-xdist", "pytest-timeout", "pytest-testmon")


def plant_package(site: Path, name: str, version: str) -> None:
    folder = site / f"{name.replace('-', '_')}-{version}.dist-info"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "METADATA").write_text(f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n", encoding="utf-8")


def entries(pins: dict) -> str:
    return "\n".join(w1_27.tool_entry_yaml(name, version, "0" * 64, install="echo install", uninstall="echo uninstall",
                                          date="2026-11-22", approved_by="test") for name, version in pins.items())


def doctor_tools(tmp_path, sandbox, pins: dict, installed: dict) -> dict:
    site = tmp_path / "site"
    site.mkdir()
    for name, version in installed.items():
        plant_package(site, name, version)
    project = tmp_path / "repo"
    project.mkdir()
    w1_27.git(project, "init", "-q", "-b", "main")
    w1_27.write_path_map(project, w1_27.minimal_valid_path_map())
    w1_27.write_tool_registry(project, entries(pins))
    launcher = base.base.write_launcher(base.REPO_ROOT, sandbox)
    env = {"PATH": f"{sandbox.bin}{os.pathsep}/usr/bin:/bin", "HOME": str(sandbox.home), "TMPDIR": str(sandbox.tmpdir),
           "LC_ALL": "C.UTF-8", "PYTHONPATH": f"{base.REPO_ROOT / 'src'}{os.pathsep}{site}",
           "PYTHONPYCACHEPREFIX": str(sandbox.pycache)}
    for name in pins:  # the machine must not show the package through another door (a user site, a system folder)
        seen = subprocess.run([sys.executable, "-c", "import importlib.metadata as m, sys; m.version(sys.argv[1])", name],
                              env={**env, "PYTHONPATH": ""}, capture_output=True, text=True)
        if name not in installed and seen.returncode == 0:
            pytest.skip(f"{name} is visible to the interpreter outside the planted folder")
    done = subprocess.run([sys.executable, str(launcher), "doctor", "--json"], cwd=str(project), env=env,
                          capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    run = base.base.Run(("doctor", "--json"), done.returncode, done.stdout, done.stderr, 0.0)
    envelope = base.envelope(run)
    found = envelope.get("result") if envelope.get("ok") is True else (envelope.get("error") or {}).get("details")
    part = (found or {}).get("tools") if isinstance(found, dict) else None
    assert isinstance(part, dict), f"gov doctor reported no tools part\n{run.describe()}"
    return {item.get("name"): item for item in part.get("tools", []) if isinstance(item, dict)}


def test_a_package_at_the_installed_version_reads_ok_with_that_version(tmp_path, sandbox):
    pins = {name: "9.9.9" for name in PACKAGES}
    tools = doctor_tools(tmp_path, sandbox, pins, installed=pins)
    for name in PACKAGES:
        got = tools.get(name) or {}
        assert got.get("ok") is True, f"{name} installed at its pin reads not ok: {got}"
        assert got.get("found_version") == "9.9.9", f"{name}: found_version {got.get('found_version')!r}, not 9.9.9"
        assert got.get("pinned_version") == "9.9.9", got


def test_a_package_at_another_version_reads_the_drift(tmp_path, sandbox):
    pins = {name: "9.9.8" for name in PACKAGES}
    tools = doctor_tools(tmp_path, sandbox, pins, installed={name: "9.9.9" for name in PACKAGES})
    for name in PACKAGES:
        got = tools.get(name) or {}
        assert got.get("ok") is False, f"{name} at 9.9.9 passed for the pin 9.9.8: {got}"
        assert got.get("found_version") == "9.9.9", f"{name}: the installed version is not read: {got}"
        assert "9.9.9" in str(got.get("reason")) and "9.9.8" in str(got.get("reason")), \
            f"{name}: the reason names neither both versions: {got}"


def test_a_missing_package_reads_not_ok(tmp_path, sandbox):
    tools = doctor_tools(tmp_path, sandbox, {name: "9.9.9" for name in PACKAGES}, installed={})
    for name in PACKAGES:
        got = tools.get(name) or {}
        assert got.get("ok") is False, f"{name} is not installed and reads ok: {got}"
        assert got.get("found_version") is None, got
