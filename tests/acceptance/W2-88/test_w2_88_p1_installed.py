"""Run 7, S24 (P-1, DEC-1178 (3)(b)): A9 works from an installed release.

P-RELEASE-1's P-1: Gov OS is released as a wheel (built by ``python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w <dir>
<export>`` from an export of the commit) and the kit installed by ``copier copy --trust --defaults --vcs-ref <tag> <clone> <project>``; a ``gov``
run from that wheel has no Gov OS source tree beside it, and A9 read its shipped files through ``Path(__file__).resolve().parents[3]``. The
interface (the lead's statement, DEC-1052, DEC-136; the ticket's S24):

1. One resolver, ``gov.adopt.fabric.shipped(rel, root)`` (``rel``: the path in the Gov OS repository; ``root``: the adopted repository): (1) the Gov
   OS source tree when gov runs from one (the folder holding ``copier.yml``, ``template/`` and ``src/gov/``, found as an ancestor of the running
   ``gov`` package by those markers, never ``parents[3]`` taken as the root): ``<source tree>/<rel>``; (2) else, for a ``rel`` under
   ``template/``, the adopted project's copy that ``copier copy`` installed: ``template/X`` is read as ``<root>/X``; (3) else it refuses
   ``SHIPPED_FILE_MISSING``: the message names ``rel`` and each place looked, ``details`` hold ``file`` (= ``rel``) and ``looked``.
2. Every read of a shipped file goes through it (A9's kernel copies, the copy of ``governance/project/retrieval.yaml`` and the standard's
   ``pool:`` block, read when A9 runs and never at import; the walls template; the MEMORY-AUDIT-1 briefs; the ``.gitleaks.toml`` fallback). A grep
   of ``src/gov/adopt/`` finds no ``parents[3]``; importing the three modules from an installed wheel with no source tree reads no shipped file
   and does not fail.
3. The release form: the wheel built from a ``git archive`` export of HEAD and installed with ``--no-deps --no-index`` into a fresh venv
   (``--system-site-packages``, for PyYAML) in tmp, the kit by ``copier copy`` from a clone holding a planted tag (``--skip-tasks``: the planted
   tag has no release manifest for ``gov release --lock-from``). Run from that venv with no ``PYTHONPATH`` and a working folder outside the source
   tree, ``gov.__file__`` is in the venv.
4. Known before the work (the lead's reading, not a reason to change a line): the pool (``governance/project/retrieval.yaml``), the walls template
   and the MEMORY-AUDIT-1 briefs are not under ``template/`` and not in the wheel at ``a23678e27``, so from an installed release with the kit from
   copier (1) and (2) find them nowhere and A9 refuses ``SHIPPED_FILE_MISSING`` naming the first it meets. Shipping them is outside the ticket's
   paths (package data or ``template/``: a package for the CTO). **Case (a) below, the full line, stays red for that cause until the package is
   decided** (README: "red for the package"); every other case of this module is within the ticket's paths.

Everything is built in the case's tmp folders (the wheel, the venv, the clone, the projects); nothing is installed on the machine; no network.
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

import w2_88_support as W

TAG = "v0.0.0-s24"
CHILD = W.HERE / "shipped_child.py"
IMPORT_CHILD = W.HERE / "import_child.py"
POOL = "governance/project/retrieval.yaml"
IDENT = ["-c", "user.name=W2-88 acceptance", "-c", "user.email=w2-88@example.invalid", "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=/dev/null"]


WHEEL_PATHS = ["src", "pyproject.toml"]                                   # what the wheel build needs (setuptools: ``src`` and the project file)
KIT_PATHS = ["copier.yml", "template"]                                    # what ``copier copy`` reads
SOURCE_TREE_PATHS = ["copier.yml", "template", "src", "pyproject.toml",    # a relocated Gov OS source tree: the markers, the code, and the three
                     POOL, "governance/project/indep-walls", "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs"]   # not under ``template/``
GIT_FROM = W.REPO_ROOT / "src"                                            # a named folder of the worktree: git finds the repository above it


def archive(paths: list, dest: Path, rev: str = "HEAD") -> None:
    """Export each **named path** of ``rev`` (HEAD, never the working tree) of the tests worktree into ``dest``: a folder by ``git archive <rev>:<folder>``,
    a file by ``git show <rev>:<file>``; git runs in the named folder itself (``src`` for a file), where ``git archive`` takes that folder alone
    (DEC-385: never the whole tree, so never ``governance/project/held-out.yaml``)."""
    dest.mkdir(parents=True, exist_ok=True)
    for name in paths:
        kind = subprocess.run(["git", "-C", str(GIT_FROM), "cat-file", "-t", f"{rev}:{name}"], capture_output=True, text=True, check=True).stdout.strip()
        if kind == "tree":
            data = subprocess.run(["git", "-C", str(W.REPO_ROOT / name), "archive", "--format=tar", f"--prefix={name}/", rev], capture_output=True,
                                  check=True).stdout
            with tarfile.open(fileobj=io.BytesIO(data)) as handle:
                handle.extractall(dest, filter="data")
        else:
            (dest / name).parent.mkdir(parents=True, exist_ok=True)
            (dest / name).write_bytes(subprocess.run(["git", "-C", str(GIT_FROM), "show", f"{rev}:{name}"], capture_output=True, check=True).stdout)


def clean_env(base: Path, **extra) -> dict:
    values = {"PATH": "/usr/bin:/bin", "HOME": str(base), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TMPDIR": str(base),
              "PYTHONDONTWRITEBYTECODE": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    values.update(extra)
    return values


def run(argv, env, cwd, what, timeout=600):
    done = subprocess.run([str(a) for a in argv], env=env, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"{what} failed (exit {done.returncode}):\n{done.stdout[-1500:]}\n{done.stderr[-2500:]}"
    return done


@pytest.fixture(scope="module")
def release(tmp_path_factory):
    """The release form, built once in tmp: the wheel (from a ``git archive`` export of HEAD) installed into a fresh venv, a clone holding the planted
    tag, and decoys where the base's ``parents[3]`` would look. Nothing is installed outside the case's folders."""
    copier = shutil.which("copier") or str(Path.home() / ".local/bin/copier")
    if not Path(copier).is_file():
        pytest.skip("copier is not installed on this machine")
    base = tmp_path_factory.mktemp("p1-release")
    scratch = base / "tmp"
    scratch.mkdir()
    env = clean_env(scratch, PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
    export = base / "export"
    archive(WHEEL_PATHS, export)
    wheels = base / "wheelhouse"
    wheels.mkdir()
    run([sys.executable, "-m", "pip", "wheel", "-q", "--no-deps", "--no-build-isolation", "--no-index", "-w", wheels, export], env, base,
        "building the wheel")
    shutil.rmtree(export, ignore_errors=True)
    wheel = sorted(wheels.glob("gov-*.whl"))
    assert len(wheel) == 1, f"the wheel was not built: {list(wheels.iterdir())}"
    venv = base / "venv"
    run([sys.executable, "-m", "venv", "--system-site-packages", "--without-pip", venv], env, base, "making the venv")
    python = venv / "bin" / "python"
    run([sys.executable, "-m", "pip", "--python", python, "install", "-q", "--no-deps", "--no-index", wheel[0]], env, base, "installing the wheel")
    where = run([python, "-c", "import gov, yaml; print(gov.__file__)"], clean_env(scratch), scratch, "importing gov from the venv").stdout.strip()
    assert where.startswith(str(venv)), f"gov imported from {where}, not from the venv {venv}"
    # the kit: a clone holding the planted tag (a mini repository of copier.yml and template/ at HEAD)
    clone = base / "clone"
    archive(KIT_PATHS, clone)
    for step in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the kit"], ["tag", TAG]):
        run(["git", "-C", clone, *IDENT, *step], env, base, f"git {step[0]} in the clone")
    # decoys where the base's ``parents[3]`` of the installed fabric.py stands: the folder above site-packages
    site = Path(where).parent.parent
    decoy = site.parent
    (decoy / "template").mkdir(exist_ok=True)
    (decoy / "template" / ".gitleaks.toml").write_text("# a decoy: never Gov OS's\n", encoding="utf-8")
    (decoy / "template" / "governance" / "kernel" / "skills" / "retrieval").mkdir(parents=True, exist_ok=True)
    (decoy / "template" / "governance" / "kernel" / "skills" / "retrieval" / "SKILL.md").write_text("decoy\n", encoding="utf-8")
    (decoy / "copier.yml").write_text("# a decoy\n", encoding="utf-8")
    made = SimpleNamespace(base=base, venv=venv, python=python, clone=clone, copier=copier, scratch=scratch, decoy=decoy)
    try:
        yield made
    finally:
        shutil.rmtree(base, ignore_errors=True)


def install_kit(release, project: Path) -> None:
    """``copier copy --trust --defaults --skip-tasks --overwrite --vcs-ref <tag> <clone> <project>``: the kit as copier installs it."""
    env = clean_env(release.scratch, PATH=f"{Path(release.copier).parent}:/usr/bin:/bin")
    project.mkdir(parents=True, exist_ok=True)
    run([release.copier, "copy", "--trust", "--defaults", "--skip-tasks", "--overwrite", "--quiet", "--vcs-ref", TAG, release.clone, project],
        env, release.scratch, "copier copy of the kit")


@pytest.fixture(scope="module")
def kit_project(release, tmp_path_factory):
    """A project the kit was installed in by copier and nothing else (the resolver's ``root`` where gov runs from a wheel)."""
    project = tmp_path_factory.mktemp("p1-kit") / "project"
    install_kit(release, project)
    assert (project / "governance/kernel/skills/retrieval/SKILL.md").is_file(), "the plant: copier installed no retrieval skill"
    try:
        yield project
    finally:
        shutil.rmtree(project.parent, ignore_errors=True)


@pytest.fixture(scope="module")
def pool_tree(tmp_path_factory):
    """A relocated Gov OS source tree (``copier.yml``, ``template/``, ``src/``, ``pyproject.toml`` and the shipped governance files of HEAD) whose shipped pool differs
    from the one the planted repository tracks: ``pool.route_depth`` is 61 here, 60 in HEAD's file."""
    tree = tmp_path_factory.mktemp("p1-pool") / "gov-os"
    archive(SOURCE_TREE_PATHS, tree)
    path = tree / POOL
    text = path.read_text(encoding="utf-8")
    assert re.search(r"^  route_depth: 60\b", text, re.M), "the plant: the shipped pool has no `route_depth: 60` line"
    path.write_text(re.sub(r"^(  route_depth: )60\b", r"\g<1>61", text, flags=re.M), encoding="utf-8")
    try:
        yield tree
    finally:
        shutil.rmtree(tree.parent, ignore_errors=True)


def resolve(python, rel: str, root: Path, cwd: Path, *, pythonpath: str | None = None) -> dict:
    """``fabric.shipped(rel, root)`` in a child run by ``python`` from ``cwd`` (outside any source tree); the answer as ``shipped_child.py`` prints it."""
    env = clean_env(cwd, **({"PYTHONPATH": pythonpath} if pythonpath else {}))
    done = subprocess.run([str(python), str(CHILD), rel, str(root)], env=env, cwd=str(cwd), capture_output=True, text=True, timeout=300,
                          stdin=subprocess.DEVNULL)
    lines = [line for line in done.stdout.splitlines() if line.startswith("{")]
    assert lines, f"the child printed no answer (exit {done.returncode}):\n{done.stdout[-800:]}\n{done.stderr[-1500:]}"
    return json.loads(lines[-1])


def run_installed(adoption, release, stage: str, *extra, timeout: int = 900):
    """``gov adopt --lite --stage <stage> ...`` run by the venv's python (the wheel's gov) with the suite's hermetic environment and **no
    ``PYTHONPATH``**, from the project (outside the source tree)."""
    env = adoption.env()
    env.pop("PYTHONPATH", None)
    argv = [str(release.python), "-m", "gov.cli.main", "adopt", "--lite", "--stage", stage, *extra, "--json", "--session", W.SESSION]
    done = subprocess.run(argv, cwd=str(adoption.project), env=env, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    return W.S124.Run(("adopt", "--lite", "--stage", stage, *extra), done.returncode, done.stdout, done.stderr, 0.0)


def installed_a9(worlds, release, name: str, *, no_retrieval: bool = False, before=None):
    """A fork of the planted adoption at A8 (``no_retrieval``: the repository tracks none, so A9 installs Gov OS's), the kit installed in it by
    copier and committed, then ``before(project)`` if given (and committed), then A9 run by the wheel's gov. ``(adoption, run, out, start)``."""
    nine = worlds.a9("p1-a8-noret" if no_retrieval else "p1-a8", run_a9=False, plant_options={"no_retrieval": True} if no_retrieval else None)
    nine.need_chain()
    adoption = W.fork(nine, name)
    install_kit(release, adoption.project)
    W.commit_all(adoption.project, "the kit, installed by copier copy from the tag")
    if before is not None:
        before(adoption.project)
        W.commit_all(adoption.project, "the project's copy changes")
    out = Path(adoption.box.base) / f"{name}-out"
    start = W.head(adoption.project)
    return adoption, run_installed(adoption, release, "A9", "--out", str(out)), out, start


# ------------------------------------------------------------------------------------------------------------
# The resolver (item 1)
# ------------------------------------------------------------------------------------------------------------

RELS = ["template/governance/kernel/skills/retrieval", "template/.gitleaks.toml", POOL]


@pytest.mark.parametrize("rel", RELS)
@pytest.mark.parametrize("tree", ["the-worktree", "a-relocated-tree"])
def test_s24_from_a_source_tree_shipped_is_that_trees_file(kit_project, pool_tree, tmp_path, rel, tree):
    """success-S24 (item 1 (1)): gov run from a Gov OS source tree (this worktree's, or one relocated into tmp) answers ``<source tree>/<rel>`` for a
    folder under ``template/``, a file under ``template/`` and the pool; the source tree is found by its markers (``copier.yml``, ``template/``,
    ``src/gov/``). The project's own copy never wins: its ``.gitleaks.toml`` is changed, and the answer is still the tree's."""
    root = tmp_path / "project"
    shutil.copytree(kit_project, root)
    (root / ".gitleaks.toml").write_text("# the project's own copy, changed\n", encoding="utf-8")
    source = W.REPO_ROOT if tree == "the-worktree" else pool_tree
    answer = resolve(sys.executable, rel, root, tmp_path, pythonpath=str(source / "src"))
    assert answer.get("ok") is True, f"fabric.shipped({rel!r}, root) did not answer from the source tree: {answer}"
    assert Path(answer["path"]).resolve() == (source / rel).resolve(), f"it answered {answer['path']}, expected {source / rel}"
    assert answer["exists"] is True


@pytest.mark.parametrize("rel,placed", [
    pytest.param("template/governance/kernel/skills/retrieval", "governance/kernel/skills/retrieval", id="a-skill-folder"),
    pytest.param("template/.gitleaks.toml", ".gitleaks.toml", id="the-secrets-configuration"),
    pytest.param("template/governance/kernel/templates/brief.md", "governance/kernel/templates/brief.md", id="a-template"),
])
def test_s24_from_an_installed_wheel_a_template_file_is_the_projects_copy_that_copier_installed(release, kit_project, rel, placed):
    """success-S24 (item 1 (2), item 3): gov run from the wheel in the venv (no ``PYTHONPATH``, working folder in tmp; ``gov.__file__`` is in the venv)
    has no source tree, so ``template/X`` is read as ``<root>/X``: the copy ``copier copy`` installed. Decoys stand where ``parents[3]`` of the installed
    ``fabric.py`` points (a ``template/`` with another ``.gitleaks.toml`` and ``copier.yml``): they are never answered."""
    answer = resolve(release.python, rel, kit_project, release.scratch)
    assert answer.get("gov_file", "").startswith(str(release.venv)), f"gov ran from {answer.get('gov_file')}, not from the venv"
    assert answer.get("ok") is True, f"fabric.shipped({rel!r}, root) did not answer from the project's copy: {answer}"
    assert Path(answer["path"]).resolve() == (kit_project / placed).resolve(), f"it answered {answer['path']}, expected {kit_project / placed}"
    assert answer["exists"] is True


@pytest.mark.parametrize("rel", [
    pytest.param("template/governance/kernel/skills/discovery", id="under-template-copy-removed"),
    pytest.param("governance/project/not-shipped-anywhere.yaml", id="not-under-template"),
])
def test_s24_a_shipped_file_found_nowhere_is_refused_by_name_with_the_places_looked(release, kit_project, tmp_path, rel):
    """success-S24 (item 1 (3)): from the wheel, a ``template/`` folder whose copy the project does not hold (the project's discovery skill removed), and a
    path outside ``template/`` that nothing ships, are refused ``SHIPPED_FILE_MISSING``: the message names ``rel`` and each place looked; ``details.file``
    is ``rel`` and ``details.looked`` lists the places (the project's copy among them for the first); no default is answered in its place."""
    root = tmp_path / "project"
    shutil.copytree(kit_project, root)
    shutil.rmtree(root / "governance/kernel/skills/discovery")
    answer = resolve(release.python, rel, root, release.scratch)
    assert answer.get("ok") is False, f"fabric.shipped({rel!r}, root) answered for a file shipped nowhere: {answer}"
    assert answer.get("code") == "SHIPPED_FILE_MISSING", f"the refusal is {answer.get('code')!r} ({answer.get('type')}): {answer.get('message')!r}"
    details = answer.get("details") or {}
    assert details.get("file") == rel, f"details.file is {details.get('file')!r}, expected {rel!r}"
    looked = details.get("looked")
    assert isinstance(looked, list) and looked, f"details.looked names no place: {details!r}"
    message = str(answer.get("message", ""))
    assert rel in message, f"the message does not name {rel!r}: {message!r}"
    for place in looked:
        assert str(place) in message, f"the message does not name the place looked {place!r}: {message!r}"
    if rel.startswith("template/"):
        expected = str(root / "governance/kernel/skills/discovery")
        assert any(str(p) == expected or str(p).rstrip("/") == expected for p in looked), f"the project's copy {expected} is not among the places looked: {looked}"


# ------------------------------------------------------------------------------------------------------------
# Imports and the source (item 2)
# ------------------------------------------------------------------------------------------------------------

def test_s24_importing_the_adopt_modules_from_an_installed_wheel_reads_no_shipped_file_and_does_not_fail(release):
    """success-S24 (item 2): ``gov.adopt.fabric``, ``gov.adopt.memory_sets`` and ``gov.adopt.safety`` imported by the wheel's gov (no source tree, no
    ``PYTHONPATH``) fail with nothing, and no file Gov OS ships (the pool, the walls template, the audit briefs, a skill, a template,
    ``.gitleaks.toml``) is opened while they are imported: the shipped files are read when A9 runs, never at import."""
    done = subprocess.run([str(release.python), str(IMPORT_CHILD)], env=clean_env(release.scratch), cwd=str(release.scratch), capture_output=True,
                          text=True, timeout=300, stdin=subprocess.DEVNULL)
    lines = [line for line in done.stdout.splitlines() if line.startswith("{")]
    assert lines, f"the child printed no answer (exit {done.returncode}):\n{done.stdout[-500:]}\n{done.stderr[-1500:]}"
    seen = json.loads(lines[-1])
    assert not seen["failed"], f"importing from the wheel fails: {seen['failed']}"
    assert not seen["opened"], f"a shipped file is read at import: {seen['opened']}"


def test_s24_no_adopt_module_takes_the_gov_os_root_from_parents_3():
    """success-S24 (item 2, a string check of the source: a grep): ``src/gov/adopt/`` holds no ``parents[3]`` (``fabric.py``, ``memory_sets.py`` and
    ``safety.py`` among its files): the Gov OS root is found by markers (``shipped``), never by a fixed number of folders up from a module."""
    found = {}
    for name in ("fabric.py", "memory_sets.py", "safety.py"):
        assert (W.SRC / "gov/adopt" / name).is_file(), f"src/gov/adopt/{name} does not exist"
    for path in sorted((W.SRC / "gov/adopt").glob("*.py")):
        count = len(re.findall(r"parents\s*\[\s*3\s*\]", path.read_text(encoding="utf-8")))
        if count:
            found[path.name] = count
    assert not found, f"src/gov/adopt/ takes a root from parents[3] in: {found}"


# ------------------------------------------------------------------------------------------------------------
# A9 (items 2 and 3)
# ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("repository", ["tracks-the-old-pool", "tracks-the-shipped-pool"])
def test_s24_the_standards_pool_is_read_from_the_shipped_file_when_a9_runs(worlds, pool_tree, repository):
    """success-S24 (item 2: read when A9 runs, never at import, no hard-coded pool): A9 is run by gov from a relocated source tree whose shipped
    ``governance/project/retrieval.yaml`` has ``pool.route_depth: 61``. A repository whose own ``retrieval.yaml`` still says 60 departs from that
    standard (``STANDARD_DEPARTURE`` naming the pool); one whose own says 61 does not (A9 ok)."""
    nine = worlds.a9("p1-a8", run_a9=False)
    nine.need_chain()
    text = (pool_tree / POOL).read_text(encoding="utf-8") if repository == "tracks-the-shipped-pool" else None
    adoption = W.fork(nine, f"pool-{repository}", retrieval=text)
    adoption.extra_env["PYTHONPATH"] = str(pool_tree / "src")
    run = adoption.a9(Path(adoption.box.base) / "pool-out")
    W.assert_offered(run, "A9")
    if repository == "tracks-the-old-pool":
        W.assert_refused(run, "STANDARD_DEPARTURE", "A9 on a repository whose pool is not the shipped pool's")
        assert "pool" in W.error_text(run), f"the departure does not name the pool: {W.error_text(run)}"
    else:
        W.assert_ok(run, "A9 on a repository whose pool is the shipped pool's")
        assert not (W.a9_record(adoption.project, run).get("standard") or {}).get("departures"), "the record names a departure"


def test_s24_a9_from_an_installed_release_copies_reads_and_writes_from_shipped_bytes(worlds, release):
    """success-S24 (the full line; **red for the package while item 4 is open**, README): the kit installed by ``copier copy`` from the planted tag
    in the planted adoption at A8 (the repository tracks no ``retrieval.yaml``), A9 run by the wheel's gov (no ``PYTHONPATH``, working folder in
    tmp). A9 is ok; the kernel files it copies (the retrieval and discovery skills, T-0, T-8) are byte for byte the tag's; ``governance/project/
    retrieval.yaml`` is installed with Gov OS's bytes (read from the shipped pool); the walls copy (``memory-audit/ACT-WALLS/``) and the audit
    briefs (``memory-audit/briefs/``) are written from shipped bytes. Until the pool, the walls template and the audit briefs are shipped where
    the resolver looks (outside the ticket's paths: a package), A9 refuses ``SHIPPED_FILE_MISSING`` naming the first of them it meets."""
    adoption, run, out, _start = installed_a9(worlds, release, "p1-full", no_retrieval=True)
    W.assert_ok(run, "A9 run by a gov installed from a wheel, on a project whose kit copier installed")
    project = adoption.project
    for target, source in W.copy_plan():
        shipped = release.clone / source
        assert (project / target).is_file(), f"A9 did not write {target}"
        assert (project / target).read_bytes() == shipped.read_bytes(), f"{target} is not byte for byte the tag's {source}"
    assert (project / POOL).read_bytes() == W.RETRIEVAL_SRC.read_bytes(), "the installed retrieval.yaml is not Gov OS's, byte for byte"
    audit = out / "memory-audit"
    assert (audit / "AUDIT-RECORD.json").is_file(), "A9 wrote no audit record"
    for folder in ("ACT-WALLS", "briefs"):
        assert (audit / folder).is_dir() and any(p.is_file() for p in (audit / folder).rglob("*")), f"A9 wrote nothing under memory-audit/{folder}/"


def test_s24_a9_from_an_installed_release_with_a_shipped_folder_missing_is_refused_by_name_and_copies_nothing(worlds, release):
    """success-S24 (b): the same installed-release A9, the project's copy of ``governance/kernel/skills/discovery/`` removed (committed). A9 is refused
    ``SHIPPED_FILE_MISSING``, ``details.file`` a ``rel`` the message names (the first shipped file it could not find: the discovery skill, or, while
    item 4's package is open, the pool: either is a shipped file found nowhere), and nothing is copied in its place: no ``.claude/skills/discovery``
    and none of A9's copies in the tree or the index, HEAD unmoved, no A9 record, the tree clean."""
    def remove_discovery(project):
        shutil.rmtree(project / "governance/kernel/skills/discovery")

    adoption, run, _out, start = installed_a9(worlds, release, "p1-missing", before=remove_discovery)
    W.assert_refused(run, "SHIPPED_FILE_MISSING", "A9 run from a wheel where a shipped folder is found nowhere")
    error = run.error
    file = (error.get("details") or {}).get("file")
    assert isinstance(file, str) and file in str(error.get("message", "")), f"the refusal does not name the missing file: {error}"
    assert isinstance(error.get("details", {}).get("looked"), list) and error["details"]["looked"], f"details.looked: {error.get('details')}"
    project = adoption.project
    assert not (project / ".claude/skills/discovery").exists(), "a default copy of the discovery skill was written in its place"
    left = [t for t, _s in W.copy_plan() if (project / t).exists() and t.startswith(".claude/")]
    assert not left, f"A9 copied files though it was refused: {left}"
    assert W.head(project) == start, "A9 moved HEAD"
    assert not [n for n in W.git(project, "ls-files", "governance/adoption").splitlines() if "/A9" in n], "A9 committed a record though it was refused"
    assert W.git(project, "status", "--porcelain", "--untracked-files=all").strip() == "", "the tree is not clean after the refusal"
