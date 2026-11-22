"""F18 (fixes-015a): pytest plugins are Python packages, read by importlib.metadata, not binaries."""

from importlib import metadata
from pathlib import Path

from gov.doctor.command import _check_no_binary_tool


def test_an_installed_package_at_its_pin_is_ok(monkeypatch):
    monkeypatch.setattr(metadata, "version", lambda name: "3.1.0")
    result = _check_no_binary_tool("pytest-xdist", "3.1.0", "", Path("/nonexistent"))
    assert result["ok"] and result["found_version"] == "3.1.0"


def test_a_package_at_another_version_is_the_drift(monkeypatch):
    monkeypatch.setattr(metadata, "version", lambda name: "3.2.0")
    result = _check_no_binary_tool("pytest-timeout", "3.1.0", "", Path("/nonexistent"))
    assert not result["ok"] and "3.2.0" in result["reason"] and "3.1.0" in result["reason"]


def test_a_missing_package_is_not_ok(monkeypatch):
    def missing(name):
        raise metadata.PackageNotFoundError(name)
    monkeypatch.setattr(metadata, "version", missing)
    result = _check_no_binary_tool("pytest-testmon", "2.0", "", Path("/nonexistent"))
    assert not result["ok"] and result["found_version"] is None
