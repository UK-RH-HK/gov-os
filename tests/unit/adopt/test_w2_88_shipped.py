"""W2-88 run 8, package 1 (a) (the owner's answer to be recorded as DEC-1183): the three files A9 needs ship inside the
wheel, under ``src/gov/_shipped/`` at their paths in the Gov OS repository, and ``fabric.shipped`` looks there second.
Since S29 (DEC-1189 (1)) the set is every rel the resolver is asked for, the ``template/`` ones included (nine); since
W2-174, also the two ticket schemas its Verify pass reads (eleven).

Regression evidence only (DEC-136). Each shipped copy equals its source bytes in this tree (no drift, nothing missing
from either side, nothing extra in the copy); ``shipped`` finds a ``rel`` in the installed package's ``_shipped/`` when
gov runs from no source tree; found nowhere, the refusal names each of the three places looked.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from gov.adopt import fabric, memory_sets
from gov.cli.errors import GovError

REPO = Path(__file__).resolve().parents[3]
PACKAGE = REPO / "src/gov/_shipped"
SKILLS = "template/governance/kernel/skills"
TEMPLATES = "template/governance/kernel/templates"
SCHEMAS = "template/governance/kernel/schemas"
# Four since run 8b (item 21); nine since S29 (DEC-1189 (1)): every rel the resolver is asked for, template/ ones too;
# eleven since W2-174: the two ticket schemas its Verify pass reads (through its own lookup, DEC-1189 (1)).
# Twelve since W2-195 (DEC-1204 (5)): the judging-work skill folder, which A9 installs as it does the other two.
THE_SHIPPED = (fabric.RETRIEVAL, memory_sets.WALLS, memory_sets.BRIEFS, memory_sets.CRON, "template/.gitleaks.toml",
               f"{SKILLS}/retrieval", f"{SKILLS}/discovery", f"{SKILLS}/judging-work", f"{TEMPLATES}/brief.md",
               f"{TEMPLATES}/role-cto.md", f"{SCHEMAS}/ticket.schema.json", f"{SCHEMAS}/common.schema.json")


def _files(base: Path, rel: str) -> dict[str, bytes]:
    """Each file at or under ``base / rel``, by its path from ``base``, with its bytes (no ``__pycache__``)."""
    top = base / rel
    if top.is_file():
        return {rel: top.read_bytes()}
    return {path.relative_to(base).as_posix(): path.read_bytes() for path in sorted(top.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts}


def test_the_shipped_set_is_named_once_in_the_code():
    assert fabric.PACKAGED == THE_SHIPPED


def test_each_shipped_copy_equals_its_source_bytes():
    # one case for the set (no parametrised rows: an opt-in list's ``rep:`` would keep only the first in a run)
    for rel in THE_SHIPPED:
        source, copy = _files(REPO, rel), _files(PACKAGE, rel)
        assert source, f"{rel}: no source in the Gov OS tree"
        assert sorted(copy) == sorted(source), f"{rel}: a file missing from one side, or extra in the copy"
        for name in source:
            assert copy[name] == source[name], f"{name}: the shipped copy has drifted from its source"


def test_the_package_ships_nothing_but_the_shipped_set():
    shipped = {path.relative_to(PACKAGE).as_posix() for path in PACKAGE.rglob("*")
               if path.is_file() and "__pycache__" not in path.parts}
    wanted = {name for rel in THE_SHIPPED for name in _files(REPO, rel)}
    assert shipped == wanted


def test_the_walls_and_briefs_are_whole_in_the_copy():
    assert sorted(_files(PACKAGE, memory_sets.BRIEFS)) == [f"{memory_sets.BRIEFS}/{name}" for name in
                                                          ("auditor.md", "checker.md", "writer.md")]
    assert f"{memory_sets.WALLS}/README.md" in _files(PACKAGE, memory_sets.WALLS)
    for name in ("retrieval", "discovery", "judging-work"):  # S29: the kernel skill folders A9 copies, whole
        assert sorted(_files(PACKAGE, f"{SKILLS}/{name}")) == sorted(_files(REPO, f"{SKILLS}/{name}"))


def test_the_package_copy_is_the_gov_packages_own_shipped_folder():
    assert fabric._package_copy() == Path(fabric.__file__).resolve().parents[1] / "_shipped"


def test_with_no_source_tree_shipped_finds_a_rel_in_the_packages_copy(tmp_path, monkeypatch):
    monkeypatch.setattr(fabric, "_source_tree", lambda start=None: None)
    package = tmp_path / "site-packages/gov/_shipped"
    (package / "governance/project").mkdir(parents=True)
    (package / fabric.RETRIEVAL).write_text("pool: {}\n")
    (package / memory_sets.BRIEFS).mkdir(parents=True)
    monkeypatch.setattr(fabric, "_package_copy", lambda: package)
    root = tmp_path / "project"
    root.mkdir()
    (root / "governance/project").mkdir(parents=True)
    (root / fabric.RETRIEVAL).write_text("the project's own\n")  # never read as Gov OS's: not under template/
    assert fabric.shipped(fabric.RETRIEVAL, root) == package / fabric.RETRIEVAL
    assert fabric.shipped(memory_sets.BRIEFS, root) == package / memory_sets.BRIEFS


def test_the_tree_comes_before_the_package_and_the_package_before_the_projects_copy(tmp_path, monkeypatch):
    tree = tmp_path / "tree"
    (tree / "template").mkdir(parents=True)
    (tree / "template/a.txt").write_text("tree\n")
    package = tmp_path / "pkg/_shipped"
    (package / "template").mkdir(parents=True)
    (package / "template/a.txt").write_text("package\n")
    (package / "template/b.txt").write_text("package\n")
    root = tmp_path / "project"
    root.mkdir()
    for name in ("a.txt", "b.txt", "c.txt"):
        (root / name).write_text("project\n")
    monkeypatch.setattr(fabric, "_source_tree", lambda start=None: tree)
    monkeypatch.setattr(fabric, "_package_copy", lambda: package)
    assert fabric.shipped("template/a.txt", root) == tree / "template/a.txt"
    assert fabric.shipped("template/b.txt", root) == package / "template/b.txt"
    assert fabric.shipped("template/c.txt", root) == root / "c.txt"


def test_found_nowhere_the_refusal_names_every_place_looked(tmp_path, monkeypatch):
    monkeypatch.setattr(fabric, "_source_tree", lambda start=None: None)
    package = tmp_path / "pkg/_shipped"
    monkeypatch.setattr(fabric, "_package_copy", lambda: package)
    root = tmp_path / "project"
    root.mkdir()
    with pytest.raises(GovError) as raised:
        fabric.shipped("template/.gitleaks.toml", root)
    err = raised.value
    assert err.code == "SHIPPED_FILE_MISSING" and err.details["file"] == "template/.gitleaks.toml"
    looked = err.details["looked"]
    assert len(looked) == 3 and "no Gov OS source tree" in looked[0]
    assert looked[1:] == [str(package / "template/.gitleaks.toml"), str(root / ".gitleaks.toml")]
    assert all(place in err.message for place in looked)
    with pytest.raises(GovError) as raised:  # not under template/: the tree's search and the package's copy
        fabric.shipped(fabric.RETRIEVAL, root)
    assert raised.value.details["looked"][1:] == [str(package / fabric.RETRIEVAL)]
    assert len(raised.value.details["looked"]) == 2
