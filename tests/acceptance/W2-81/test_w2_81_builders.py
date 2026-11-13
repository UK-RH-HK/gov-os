"""The five builders and the clean variant: repositories of their own, built file by file and commit by commit."""

from __future__ import annotations

import re
from pathlib import Path

import w2_81_build as build
import w2_81_git as gitlib
from w2_81_words import AUTHORS

LANGUAGE = {"python-app": ".py", "rust-workspace": ".rs", "typescript-monorepo": ".ts", "legacy-docs": ".py",
            "secret-history": ".go", build.CLEAN: ".py"}


def test_the_five_shapes_and_the_clean_variant_are_built(ground):
    assert set(ground) == set(build.SHAPES) | {build.CLEAN}
    shapes = {ground[name].manifest["shape"] for name in build.SHAPES}
    assert len(shapes) == 5, f"the five repositories are of five shapes: {shapes}"
    assert ground[build.CLEAN].manifest["shape"] == ground["python-app"].manifest["shape"]


def test_each_repository_is_a_git_repository_of_its_own_in_a_temporary_folder(ground):
    roots = set()
    for name, built in ground.items():
        gitlib.assert_own_repository(built.root)
        assert not gitlib._inside(built.root, gitlib.REPO_ROOT), name
        assert (built.root / ".git").is_dir(), f"{name}: its .git is a folder of its own, not a worktree's file"
        roots.add(built.root.resolve())
    assert len(roots) == len(ground), "each repository has a folder of its own"


def test_each_repository_has_several_commits_written_file_by_file(ground):
    for name, built in ground.items():
        commits = gitlib.run_git(built.root, "rev-list", "--reverse", "HEAD").split()
        assert len(commits) >= 4, f"{name}: {len(commits)} commits"
        assert [c[:12] for c in commits] == built.manifest["commits"], name
        sizes = [len(gitlib.tree(built.root, c)) for c in commits]
        assert sizes[0] < max(sizes), f"{name}: the first commit holds the whole tree"
        trees = {gitlib.run_git(built.root, "rev-parse", f"{c}^{{tree}}").strip() for c in commits}
        assert len(trees) == len(commits), f"{name}: a commit changes no file"


def test_each_history_has_set_authors_and_increasing_dates(ground):
    names = {a for a, _ in AUTHORS}
    for name, built in ground.items():
        lines = gitlib.run_git(built.root, "log", "--reverse", "--format=%an|%ae|%at|%ct").splitlines()
        stamps = []
        for line in lines:
            author, email, authored, committed = line.split("|")
            assert author in names and email.endswith("@example.invalid"), f"{name}: author {author}"
            assert authored == committed, f"{name}: the builder sets both dates"
            stamps.append(int(authored))
        assert stamps == sorted(stamps) and len(set(stamps)) == len(stamps), f"{name}: dates not increasing"


def test_each_repository_looks_real(ground):
    for name, built in ground.items():
        head = gitlib.tree(built.root)
        assert "README.md" in head, name
        assert any(p.endswith(LANGUAGE[name]) for p in head), f"{name}: no {LANGUAGE[name]} source"
        assert any(re.search(r"(spec|design|rfc|adr|decision)", p) for p in head), f"{name}: no spec"
        assert any("test" in Path(p).name for p in head), f"{name}: no test"
        assert any("plan" in p for p in head), f"{name}: no plan"


def test_the_workspace_and_the_monorepo_have_several_members(ground):
    cargo = gitlib.blob(ground["rust-workspace"].root, "HEAD", "Cargo.toml")
    crates = re.findall(r'"crates/([a-z]+)"', cargo)
    assert len(crates) >= 3, crates
    for crate in crates:
        assert gitlib.blob(ground["rust-workspace"].root, "HEAD", f"crates/{crate}/Cargo.toml"), crate
    packages = {p.split("/")[1] for p in gitlib.tree(ground["typescript-monorepo"].root)
                if p.startswith("packages/") and p.endswith("/package.json")}
    assert len(packages) >= 3, packages


def test_the_layout_of_a_run_folder_and_its_removal(run_folder):
    built = build.build_all(run_folder, 31337)
    for name, b in built.items():
        assert b.root == run_folder / "repos" / name
        assert b.manifest_path == run_folder / "manifests" / f"{name}.json"
    build.remove(run_folder)
    assert not run_folder.exists(), "the built repositories are removed"


def test_a_repository_is_never_built_over_an_existing_folder(tmp_path):
    (tmp_path / "taken").mkdir()
    try:
        build.build_python(tmp_path / "taken", 1, tmp_path / "run")
    except AssertionError as refused:
        assert "new folder" in str(refused)
    else:
        raise AssertionError("a builder wrote into a folder that existed")
