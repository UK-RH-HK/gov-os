"""W2-88 run 7, S24 (P-1): A9 works from an installed release.

Regression evidence only (DEC-136). One resolver, ``fabric.shipped(rel, root)``: (1) the Gov OS source tree gov runs
from, found by markers; (2) for a ``rel`` under ``template/``, the adopted project's copy that ``copier copy`` installed;
(3) else ``SHIPPED_FILE_MISSING``. Every read of a shipped file goes through it, at run time, never at import. The
release form (a wheel built from an export, installed into a fresh venv) is built inside a test's own tmp folder.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from gov.adopt import fabric, memory_sets, safety
from gov.cli.errors import GovError

from .test_w2_88_fabric import SHIPPED, git, planted, run_a9, stand_ins  # noqa: F401  (stand_ins is a fixture)

REPO = Path(__file__).resolve().parents[3]
SKILLS = "template/governance/kernel/skills"
KIT = ("template/governance/kernel/templates/brief.md", "template/governance/kernel/templates/role-cto.md",
       f"{SKILLS}/retrieval", f"{SKILLS}/discovery")
SHIPPED_FILES = (*KIT, "template/.gitleaks.toml", fabric.RETRIEVAL, memory_sets.WALLS, memory_sets.BRIEFS)
MARK = "\nSHIPPED-MARK\n"


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
    else:
        shutil.copyfile(src, dst)


def fake_tree(tmp_path: Path, leave_out: tuple = ()) -> Path:
    """A Gov OS source tree of its own (the markers, and the shipped files with a mark in four of them, a pool of 61)."""
    tree = tmp_path / "shipped-tree"
    (tree / "src/gov").mkdir(parents=True)
    (tree / "copier.yml").write_text("_subdirectory: template\n")
    for rel in SHIPPED_FILES:
        if rel not in leave_out:
            copy(REPO / rel, tree / rel)
    for rel in (f"{SKILLS}/retrieval/SKILL.md", f"{memory_sets.WALLS}/README.md", f"{memory_sets.BRIEFS}/auditor.md"):
        if rel not in leave_out and rel.rsplit("/", 1)[0] not in leave_out:
            with open(tree / rel, "a", encoding="utf-8") as handle:
                handle.write(MARK)
    if fabric.RETRIEVAL not in leave_out:
        place = tree / fabric.RETRIEVAL
        place.write_text(place.read_text().replace("route_depth: 60", "route_depth: 61"))
    return tree


def no_tree(monkeypatch, tree: Path | None = None) -> None:
    monkeypatch.setattr(fabric, "_source_tree", lambda start=None: tree)


def with_kit(root: Path) -> None:
    """What ``copier copy`` leaves in a project: each ``template/X`` as ``X`` (committed)."""
    for rel in KIT:
        copy(REPO / rel, root / rel.removeprefix("template/"))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "kit")


# ---- the resolver

def test_the_source_tree_is_found_by_its_markers_whatever_the_depth(tmp_path):
    tree = tmp_path / "gov-os"
    (tree / "template").mkdir(parents=True)
    (tree / "copier.yml").write_text("x: 1\n")
    for place in ("src/gov/adopt/fabric.py", "a/b/c/d/e/gov/adopt/fabric.py", ".venv/lib/python3.12/site-packages/gov/adopt/fabric.py"):
        (tree / place).parent.mkdir(parents=True, exist_ok=True)
        (tree / place).write_text("")
    (tree / "src/gov").mkdir(exist_ok=True)
    for place in ("src/gov/adopt/fabric.py", "a/b/c/d/e/gov/adopt/fabric.py", ".venv/lib/python3.12/site-packages/gov/adopt/fabric.py"):
        assert fabric._source_tree(tree / place) == tree.resolve()
    wheel = tmp_path / "pin/lib/python3.12/site-packages/gov/adopt/fabric.py"
    wheel.parent.mkdir(parents=True)
    wheel.write_text("")
    assert fabric._source_tree(wheel) is None  # parents[3] of this file is pin/lib/python3.12: no markers
    half = tmp_path / "half"
    (half / "src/gov/adopt").mkdir(parents=True)
    (half / "copier.yml").write_text("x: 1\n")  # a copier.yml and src/gov, but no template/: not the tree
    assert fabric._source_tree(half / "src/gov/adopt/fabric.py") is None


def test_gov_run_from_this_tree_finds_this_tree_first(tmp_path):
    root = tmp_path / "project"
    (root / ".gitleaks.toml").parent.mkdir()
    (root / ".gitleaks.toml").write_text("the project's copy\n")
    assert fabric.shipped("template/.gitleaks.toml", root) == REPO / "template/.gitleaks.toml"
    assert fabric.shipped(fabric.RETRIEVAL, root) == REPO / fabric.RETRIEVAL
    assert fabric.shipped(f"{SKILLS}/retrieval", root) == REPO / SKILLS / "retrieval"


def test_without_a_tree_a_template_file_is_the_projects_copy_template_x_read_as_x(tmp_path, monkeypatch):
    no_tree(monkeypatch)
    root = tmp_path / "project"
    copy(REPO / f"{SKILLS}/retrieval", root / "governance/kernel/skills/retrieval")
    assert fabric.shipped(f"{SKILLS}/retrieval", root) == root / "governance/kernel/skills/retrieval"
    assert fabric.shipped(f"{SKILLS}/retrieval/SKILL.md", root) == root / "governance/kernel/skills/retrieval/SKILL.md"


def test_the_tree_comes_before_the_projects_copy_and_a_file_it_lacks_falls_through_to_it(tmp_path, monkeypatch):
    tree = fake_tree(tmp_path, leave_out=("template/.gitleaks.toml",))
    no_tree(monkeypatch, tree)
    root = tmp_path / "project"
    root.mkdir()
    (root / ".gitleaks.toml").write_text("the project's copy\n")
    (root / "governance/kernel/templates").mkdir(parents=True)
    (root / "governance/kernel/templates/brief.md").write_text("the project's brief\n")
    assert fabric.shipped("template/governance/kernel/templates/brief.md", root) == \
        tree / "template/governance/kernel/templates/brief.md"  # both hold it: the tree's
    assert fabric.shipped("template/.gitleaks.toml", root) == root / ".gitleaks.toml"  # the tree lacks it


def test_a_file_found_nowhere_is_refused_by_name_with_each_place_looked(tmp_path, monkeypatch):
    tree = tmp_path / "gov-os"
    (tree / "src/gov").mkdir(parents=True)
    (tree / "template").mkdir()
    (tree / "copier.yml").write_text("x: 1\n")
    no_tree(monkeypatch, tree)
    root = tmp_path / "project"
    root.mkdir()
    with pytest.raises(GovError) as raised:
        fabric.shipped("template/.gitleaks.toml", root)
    err = raised.value
    assert err.code == "SHIPPED_FILE_MISSING" and err.details["file"] == "template/.gitleaks.toml"
    assert err.details["looked"] == [str(tree / "template/.gitleaks.toml"), str(root / ".gitleaks.toml")]
    assert "template/.gitleaks.toml" in err.message and all(place in err.message for place in err.details["looked"])
    with pytest.raises(GovError) as raised:  # not under template/: only the tree is looked at
        fabric.shipped(fabric.RETRIEVAL, root)
    assert raised.value.details == {"file": fabric.RETRIEVAL, "looked": [str(tree / fabric.RETRIEVAL)]}
    no_tree(monkeypatch)
    package = str(Path(fabric.__file__).resolve().parents[1])
    with pytest.raises(GovError) as raised:  # no tree, not under template/: the search for the tree is the one place
        fabric.shipped(fabric.RETRIEVAL, root)
    err = raised.value
    assert err.code == "SHIPPED_FILE_MISSING" and err.details["file"] == fabric.RETRIEVAL
    assert len(err.details["looked"]) == 1 and package in err.details["looked"][0], err.details
    assert "no Gov OS source tree" in err.details["looked"][0] and "copier.yml" in err.details["looked"][0]
    assert str(root / fabric.RETRIEVAL) not in err.details["looked"] and str(root / fabric.RETRIEVAL) not in err.message
    assert fabric.RETRIEVAL in err.message and all(place in err.message for place in err.details["looked"])
    with pytest.raises(GovError) as raised:  # no tree, under template/, the project's copy missing: both places
        fabric.shipped("template/.gitleaks.toml", root)
    err = raised.value
    assert len(err.details["looked"]) == 2 and package in err.details["looked"][0], err.details
    assert "no Gov OS source tree" in err.details["looked"][0] and err.details["looked"][1] == str(root / ".gitleaks.toml")
    assert all(place in err.message for place in err.details["looked"])


def test_no_read_of_a_shipped_file_uses_a_fixed_level_above_the_package():
    folder = REPO / "src/gov/adopt"
    for source in sorted(folder.glob("*.py")):
        text = source.read_text(encoding="utf-8")
        assert "parents[3]" not in text, source.name
        assert "GOV_OS" not in text, source.name


def test_nothing_shipped_is_read_when_the_modules_are_imported():
    for module in (fabric, memory_sets, safety):
        assert not any(name in vars(module) for name in ("STANDARD", "TEMPLATE_GITLEAKS", "GOV_OS")), module.__name__


# ---- the reads, through it

def test_a9_copies_reads_the_pool_the_walls_and_the_briefs_from_the_shipped_bytes(tmp_path, monkeypatch, stand_ins):
    tree = fake_tree(tmp_path)
    no_tree(monkeypatch, tree)
    root = planted(tmp_path, retrieval=(tree / fabric.RETRIEVAL).read_text())  # the project keeps the tree's own pool
    with_kit(root)
    out = tmp_path / "out"
    result = run_a9(root, out)
    assert result["ok"] is True
    for source, target in ((f"{SKILLS}/retrieval/SKILL.md", ".claude/skills/retrieval/SKILL.md"),
                           (f"{SKILLS}/discovery/SKILL.md", ".claude/skills/discovery/SKILL.md"),
                           ("template/governance/kernel/templates/brief.md", "governance/kernel/templates/brief.md"),
                           ("template/governance/kernel/templates/role-cto.md", "governance/kernel/templates/role-cto.md")):
        assert (root / target).read_bytes() == (tree / source).read_bytes(), target
    assert MARK in (root / ".claude/skills/retrieval/SKILL.md").read_text()
    head = yaml.safe_load((root / result["record"]).read_text().split("---\n")[1])
    assert head["standard"]["pool"]["route_depth"] == 61 and head["standard"]["departures"] == []  # the tree's pool
    walls = out / "memory-audit/ACT-WALLS/walls"
    assert (walls / "README.md").read_bytes() == (tree / memory_sets.WALLS / "README.md").read_bytes()
    assert MARK in (walls / "README.md").read_text()
    assert MARK in (out / "memory-audit/briefs/auditor.md").read_text()  # the variant is made of the shipped brief


def test_the_pool_is_the_shipped_files_not_one_written_in_code(tmp_path, monkeypatch, stand_ins):
    no_tree(monkeypatch, fake_tree(tmp_path))  # a pool of 61 ...
    root = planted(tmp_path)  # ... and a repository on the 60 of this repository's own file
    with_kit(root)
    with pytest.raises(GovError) as raised:
        run_a9(root, tmp_path / "out")
    assert raised.value.code == "STANDARD_DEPARTURE" and raised.value.details["settings"] == ["pool"]
    assert raised.value.details["standard"]["pool"]["route_depth"] == 61


def test_a9_refuses_a_missing_shipped_file_by_name_and_writes_nothing(tmp_path, monkeypatch, stand_ins):
    for missing in (fabric.RETRIEVAL, memory_sets.WALLS, memory_sets.BRIEFS, f"{SKILLS}/discovery",
                    "template/governance/kernel/templates/role-cto.md"):
        tmp = tmp_path / missing.replace("/", "_")
        tmp.mkdir()
        tree = fake_tree(tmp, leave_out=(missing,))
        no_tree(monkeypatch, tree)
        root = planted(tmp, retrieval=(tree / fabric.RETRIEVAL).read_text() if (tree / fabric.RETRIEVAL).exists() else SHIPPED)
        with pytest.raises(GovError) as raised:
            run_a9(root, tmp / "out")
        assert raised.value.code in ("SHIPPED_FILE_MISSING", "KERNEL_SOURCE_MISSING"), missing
        assert raised.value.details.get("file", raised.value.details.get("source")) == missing
        status = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
                                capture_output=True, text=True).stdout
        assert ".claude" not in status and "kernel" not in status and "governance/adoption" not in status, missing


def test_the_kernel_copies_come_from_the_projects_copy_when_gov_runs_from_no_tree(tmp_path, monkeypatch, stand_ins):
    no_tree(monkeypatch)
    root = planted(tmp_path)
    with_kit(root)
    with pytest.raises(GovError) as raised:  # the pool is not under template/: found nowhere, refused, no default
        run_a9(root, tmp_path / "out")
    assert raised.value.code == "SHIPPED_FILE_MISSING" and raised.value.details["file"] == fabric.RETRIEVAL
    sources = fabric._sources(root)  # the kit's own copies are found
    assert (f"{SKILLS}/retrieval/SKILL.md", ".claude/skills/retrieval/SKILL.md") in sources


def test_a0_takes_the_gitleaks_rules_from_the_trees_template_or_refuses_by_name(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    git(root, "init", "-q")
    assert safety.setup(root)[".gitleaks.toml"] == (REPO / "template/.gitleaks.toml").read_text()
    no_tree(monkeypatch)
    with pytest.raises(GovError) as raised:
        safety.setup(root)
    assert raised.value.code == "SHIPPED_FILE_MISSING" and raised.value.details["file"] == "template/.gitleaks.toml"
    (root / ".gitleaks.toml").write_text("the project's own\n")
    assert ".gitleaks.toml" not in safety.setup(root)  # its own is never touched, and nothing shipped is needed


# ---- the release form: a wheel built from an export, installed in a fresh venv, run with no source tree

PROBE = """
import json, sys
from pathlib import Path
import gov
from gov.adopt import fabric, memory_sets, safety
from gov.cli.errors import GovError
root = Path(sys.argv[1])
seen = {"gov": gov.__file__, "tree": fabric._source_tree(), "attrs": [n for n in ("STANDARD", "GOV_OS") if n in vars(fabric)]}
seen["copy"] = str(fabric.shipped("template/governance/kernel/skills/retrieval", root))
try:
    fabric.shipped("governance/project/retrieval.yaml", root)
except GovError as exc:
    seen["refused"] = [exc.code, exc.details]
try:
    fabric.read_standard(root, [])
except GovError as exc:
    seen["standard"] = [exc.code, exc.details["file"]]
print(json.dumps(seen))
"""


def test_a_wheel_in_the_release_form_runs_a9s_reads_with_no_source_tree(tmp_path):
    pytest.importorskip("setuptools")
    export = tmp_path / "export"
    copy(REPO / "src", export / "src")
    shutil.copyfile(REPO / "pyproject.toml", export / "pyproject.toml")
    wheels, venv, work = tmp_path / "wheels", tmp_path / "venv", tmp_path / "work"
    work.mkdir()
    env = {key: value for key, value in os.environ.items() if key not in ("PYTHONPATH", "PYTHONHOME")}
    built = subprocess.run([sys.executable, "-m", "pip", "wheel", "-q", "--no-deps", "--no-build-isolation", "--no-index",
                            "-w", str(wheels), str(export)], capture_output=True, text=True, env=env, cwd=work)
    if built.returncode != 0:
        pytest.skip("no wheel can be built here offline: " + built.stderr.strip()[-300:])
    made = subprocess.run([sys.executable, "-m", "venv", "--system-site-packages", str(venv)], capture_output=True,
                          text=True, env=env, cwd=work)
    if made.returncode != 0:
        pytest.skip("no venv can be made here: " + made.stderr.strip()[-300:])
    wheel = next(wheels.glob("gov-*.whl"))
    installed = subprocess.run([str(venv / "bin/python"), "-m", "pip", "install", "-q", "--no-deps", "--no-index", str(wheel)],
                               capture_output=True, text=True, env=env, cwd=work)
    assert installed.returncode == 0, installed.stderr
    project = tmp_path / "project"
    copy(REPO / f"{SKILLS}/retrieval", project / "governance/kernel/skills/retrieval")  # the kit copier installed
    done = subprocess.run([str(venv / "bin/python"), "-c", PROBE, str(project)], capture_output=True, text=True, env=env,
                          cwd=work)
    assert done.returncode == 0, done.stderr
    seen = json.loads(done.stdout)
    assert seen["gov"].startswith(str(venv)) and seen["tree"] is None and seen["attrs"] == []
    assert seen["copy"] == str(project / "governance/kernel/skills/retrieval")
    assert seen["refused"][0] == "SHIPPED_FILE_MISSING" and seen["refused"][1]["file"] == fabric.RETRIEVAL
    assert seen["standard"] == ["SHIPPED_FILE_MISSING", fabric.RETRIEVAL]  # the pool is in neither the wheel nor the kit
