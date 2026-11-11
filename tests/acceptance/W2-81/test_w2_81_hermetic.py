"""Hermetic and bounded: no write in this repository, no skip, a missing tool fails naming it (DEC-898, DEC-899)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import w2_81_build as build
import w2_81_git as gitlib
import w2_81_manifest as manifest_form
import w2_81_standin as standin
from w2_81_git import porcelain_here, w2_81_artefacts

SUITE = Path(__file__).resolve().parent
# Words the suite must not hold, written in parts so this file does not hold them either.
FORBIDDEN = ("pytest." + "skip", "skip" + "if", "importor" + "skip", "GOV_DEV" + "_TIERS", "gov-os-" + "workbench")
NETWORK = ("socket", "urllib", "http", "requests", "ftplib", "smtplib")


def _python_files():
    return sorted(p for p in SUITE.glob("*.py"))


def test_a_build_and_its_removal_write_nothing_in_this_repository(run_folder):
    suite, artefacts = porcelain_here(str(SUITE)), w2_81_artefacts(porcelain_here())
    build.build_all(run_folder, 77)
    assert run_folder.is_dir() and not gitlib._inside(run_folder, gitlib.REPO_ROOT)
    build.remove(run_folder)
    assert porcelain_here(str(SUITE)) == suite, "a build changed the suite's folder"
    assert w2_81_artefacts(porcelain_here()) == artefacts, "a build left a W2-81 artefact in this repository"
    assert not run_folder.exists()


def test_every_write_aimed_inside_this_repository_is_refused_before_it_is_made(ground, tmp_path):
    inside = gitlib.REPO_ROOT / "tests" / "acceptance" / "W2-81" / "w2-81-run"
    attempts = {
        "a built repository": lambda: build.build_python(inside / "repos" / "python-app", 1, tmp_path),
        "a manifest": lambda: manifest_form.write(ground["python-app"].manifest, inside, tmp_path / "elsewhere"),
        "a removal": lambda: build.remove(gitlib.REPO_ROOT / "tests" / "acceptance" / "W2-81"),
        "a stand-in's outputs": lambda: standin.render(standin.perfect(ground["python-app"]), ground["python-app"],
                                                       inside / "adopted", tmp_path / "beside"),
        "the repository's root": lambda: gitlib.outside_this_repository(gitlib.REPO_ROOT),
        "a folder holding it": lambda: gitlib.outside_this_repository(gitlib.REPO_ROOT.parent),
    }
    for what, attempt in attempts.items():
        try:
            attempt()
        except gitlib.InsideThisRepository:
            pass
        else:
            raise AssertionError(f"{what} inside this repository was not refused")
    assert not inside.exists(), "a refused write left a folder behind"


def test_the_tripwire_names_only_w2_81_artefacts():
    assert set(build.SHAPES) | {build.CLEAN} <= set(gitlib.ARTEFACTS)
    status = "?? tests/acceptance/W2-81/w2-81-run/x\n?? some/other/suite/tmp.txt\n?? a/manifests/b.json\n"
    assert w2_81_artefacts(status) == {"tests/acceptance/W2-81/w2-81-run/x", "a/manifests/b.json"}


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
