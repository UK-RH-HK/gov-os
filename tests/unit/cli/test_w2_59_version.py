"""Builder tests for W2-59: ``gov --version`` names the code's version and commit (DEC-835).

Regression evidence only (DEC-136); the acceptance tests prove it from an installed wheel.
"""
from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli import main as cli  # noqa: E402

VERSION = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def test_from_the_source_tree_outside_any_project_it_names_the_version_and_the_tree_s_head(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert cli.main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == f"gov {VERSION} (commit {head})"


def test_an_installed_package_inside_another_repository_names_no_commit(tmp_path, monkeypatch, capsys):
    site = tmp_path / "venv" / "lib" / "site-packages"
    (site / "gov").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(tmp_path)], capture_output=True, check=True)
    monkeypatch.setattr(cli, "PACKAGE", site / "gov")
    assert cli.main(["--version"]) == 0
    out = capsys.readouterr().out.strip()
    assert out.startswith("gov ") and out.endswith("(commit unknown)")
