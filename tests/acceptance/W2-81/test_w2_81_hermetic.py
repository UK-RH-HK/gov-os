"""Hermetic and bounded: no write in this repository, no skip, a missing tool fails naming it (DEC-898, DEC-899)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import w2_81_build as build
import w2_81_git as gitlib
from conftest import porcelain_here

SUITE = Path(__file__).resolve().parent
# Words the suite must not hold, written in parts so this file does not hold them either.
FORBIDDEN = ("pytest." + "skip", "skip" + "if", "importor" + "skip", "GOV_DEV" + "_TIERS", "gov-os-" + "workbench")
NETWORK = ("socket", "urllib", "http", "requests", "ftplib", "smtplib")


def _python_files():
    return sorted(p for p in SUITE.glob("*.py"))


def test_a_build_and_its_removal_write_nothing_in_this_repository(run_folder):
    before = porcelain_here()
    build.build_all(run_folder, 77)
    assert run_folder.is_dir()
    build.remove(run_folder)
    assert porcelain_here() == before, "a build changed this repository's working tree"
    assert not run_folder.exists()


def test_a_missing_tool_fails_naming_it(monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", str(tmp_path / "no-tools-here"))
    for tool in gitlib.TOOLS:
        try:
            gitlib.require(tool)
        except gitlib.MissingTool as missing:
            assert f"`{tool}`" in str(missing)
        else:
            raise AssertionError(f"{tool} was found on an empty PATH")
    try:
        build.build_python(tmp_path / "repo", 1, tmp_path / "run")
    except gitlib.MissingTool as missing:
        assert "`git`" in str(missing)
    else:
        raise AssertionError("a builder ran without git")


def test_no_case_is_skipped_and_nothing_names_the_workbench_or_the_dev_tiers():
    for path in _python_files():
        text = path.read_text(encoding="utf-8")
        for word in FORBIDDEN:
            assert word not in text, f"{path.name} holds {word!r}"


def test_the_suite_imports_no_network_module():
    for path in _python_files():
        imports = re.findall(r"^\s*(?:from|import)\s+([a-zA-Z_][\w.]*)", path.read_text(encoding="utf-8"), re.M)
        assert not {i.split(".")[0] for i in imports} & set(NETWORK), f"{path.name} imports {imports}"


def test_no_built_repository_or_large_file_is_tracked_in_this_repository():
    tracked = subprocess.run(["git", "-C", str(gitlib.REPO_ROOT), "ls-files", "-z", "--", str(SUITE)],
                             capture_output=True, text=True, env=gitlib.git_env(gitlib.REPO_ROOT.parent)).stdout
    for rel in filter(None, tracked.split("\0")):
        path = gitlib.REPO_ROOT / rel
        assert path.suffix in {".py", ".md", ".json", ".yaml"}, f"{rel} is tracked"
        assert path.stat().st_size < 100_000, f"{rel} is large"
    for path in SUITE.rglob("*"):
        assert path.name != ".git", f"a git repository inside the suite: {path}"
