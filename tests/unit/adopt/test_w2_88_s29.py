"""W2-88 S29 (DEC-1189 (1)): every file the shipped-file resolver (``fabric.shipped``) is asked for is in the wheel.

Regression evidence only (DEC-136). The source of ``src/gov`` is scanned: every call of ``shipped`` has its argument
resolved to its constant (a string, a module's constant, an attribute of an imported module, or a loop over a tuple of
those); a call whose argument this test cannot resolve fails the test, naming the file and the line, unless its
argument is one ``COMPUTED`` names (by file, function and argument, with the computation that gives its values). Each
``rel`` found must be listed (every file under it) in ``pyproject.toml``'s package data under ``"gov"`` and present
under ``src/gov/_shipped/``, byte-identical to its source in this tree, and covered by ``fabric.PACKAGED`` (the code's
one named list of what the wheel carries). A0 run by a gov installed from a wheel built in the release form (an export
of HEAD), on a planted repository with no kit and no ``.gitleaks.toml``, exits 0 and commits the template's copy.
"""
from __future__ import annotations

import ast
import glob
import importlib
import io
import os
import shutil
import subprocess
import sys
import tarfile
import tomllib
from pathlib import Path

import pytest

from gov.adopt import fabric, project, safety

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
PACKAGE_DIR = SRC / "gov"
SHIPPED_DIR = PACKAGE_DIR / "_shipped"
GITLEAKS = "template/.gitleaks.toml"

# The calls whose argument is computed at run time, not a constant nor a loop over constants: (file, function,
# argument) -> what gives its values. ``install`` copies each pair ``_sources`` lists (the files under KERNEL_FOLDERS
# and the KERNEL_FILES) and, where the project tracks none, ``retrieval.yaml``.
COMPUTED = {
    ("src/gov/adopt/fabric.py", "install", "source"):
        lambda: [source for source, _ in fabric._sources(None)] + [fabric.RETRIEVAL],
}


class Unresolved(Exception):
    pass


def _module_name(path: Path, src: Path = SRC) -> str:
    parts = list(path.relative_to(src).with_suffix("").parts)
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def _imports(tree: ast.Module, modname: str) -> dict[str, tuple[str, str | None]]:
    """Every name an import binds anywhere in the module (a function's own import too): name -> (module, attribute)."""
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:  # relative: from the module's package (an ``__init__``'s name is its package's already)
                base = ".".join([*modname.split(".")[:-node.level], *([base] if base else [])])
            for alias in node.names:
                found[alias.asname or alias.name] = (base, alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                found[alias.asname or alias.name.split(".")[0]] = (alias.asname and alias.name or alias.name.split(".")[0],
                                                                   None)
    return found


class _Scope:
    def __init__(self, module, imports, function, loops):
        self.module, self.imports, self.function, self.loops = module, imports, function, loops

    def outer(self, loop):
        return _Scope(self.module, self.imports, self.function, self.loops[:self.loops.index(loop)])

    def local(self, name: str) -> bool:
        """A parameter of the enclosing function, or a name it assigns (not through a loop this scope resolves)."""
        if self.function is None:
            return False
        args = self.function.args
        if name in {a.arg for a in [*args.posonlyargs, *args.args, *args.kwonlyargs, args.vararg, args.kwarg] if a}:
            return True
        return any(isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Store)
                   for node in ast.walk(self.function))

    def lookup(self, name: str):
        if name in self.imports:
            base, attr = self.imports[name]
            mod = importlib.import_module(base)
            if attr is None:
                return mod
            if hasattr(mod, attr):
                return getattr(mod, attr)
            return importlib.import_module(f"{base}.{attr}")
        if name in vars(self.module):
            return vars(self.module)[name]
        raise Unresolved(f"the name {name} is bound nowhere this test can see")


def _bound(target: ast.expr, name: str):
    """Where ``name`` sits in a loop's target: None (the whole item), an index (in a tuple), or False (not bound)."""
    if isinstance(target, ast.Name):
        return None if target.id == name else False
    if isinstance(target, ast.Tuple):
        for index, part in enumerate(target.elts):
            if isinstance(part, ast.Name) and part.id == name:
                return index
    return False


def _values(node: ast.expr, scope: _Scope) -> list:
    """Every value ``node`` can take (one, or each item of the loop that binds it)."""
    if isinstance(node, ast.Constant):
        return [node.value]
    if isinstance(node, ast.Name):
        for loop in reversed(scope.loops):
            where = _bound(loop.target, node.id)
            if where is False:
                continue
            items = _values(loop.iter, scope.outer(loop))
            if len(items) != 1 or not isinstance(items[0], (tuple, list)):
                raise Unresolved(f"the loop over {ast.unparse(loop.iter)} is over no tuple of constants")
            return [item if where is None else item[where] for item in items[0]]
        if scope.local(node.id):
            raise Unresolved(f"{node.id} is a parameter or a local name of {scope.function.name}")
        return [scope.lookup(node.id)]
    if isinstance(node, ast.Attribute):
        return [getattr(base, node.attr) for base in _values(node.value, scope)]
    if isinstance(node, (ast.Tuple, ast.List)):
        parts = [_values(element, scope) for element in node.elts]
        if any(len(part) != 1 for part in parts):
            raise Unresolved(f"{ast.unparse(node)} holds a name with more than one value")
        return [tuple(part[0] for part in parts)]
    raise Unresolved(f"{ast.unparse(node)} is no constant, name or attribute")


def _is_resolver_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and (
        (isinstance(node.func, ast.Name) and node.func.id == "shipped")
        or (isinstance(node.func, ast.Attribute) and node.func.attr == "shipped"))


def scan(src: Path = SRC, computed: dict = COMPUTED) -> tuple[dict[str, list[str]], list[str]]:
    """``({rel: [file:line, ...]}, [unresolved call, ...])`` over every module under ``src/gov``."""
    found, unresolved = {}, []
    for path in sorted((src / "gov").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        name = _module_name(path, src)
        rel_file = path.relative_to(src.parent).as_posix()
        calls = []

        def visit(node, function, loops):
            for child in ast.iter_child_nodes(node):
                if _is_resolver_call(child):
                    calls.append((child, function, loops))
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    visit(child, child, [])
                elif isinstance(child, (ast.For, ast.AsyncFor)):
                    visit(child, function, [*loops, child])
                else:
                    visit(child, function, loops)

        visit(tree, None, [])
        if not calls:
            continue
        module, imports = importlib.import_module(name), _imports(tree, name)
        for call, function, loops in calls:
            where = f"{rel_file}:{call.lineno}"
            arg = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg == "rel"), None)
            try:
                if arg is None:
                    raise Unresolved("no argument")
                values = _values(arg, _Scope(module, imports, function, loops))
            except Unresolved as why:
                key = (rel_file, function.name if function else None, arg.id if isinstance(arg, ast.Name) else None)
                if key not in computed:
                    unresolved.append(f"{where}: the argument {ast.unparse(arg) if arg else '?'} of shipped() cannot be "
                                      f"resolved to a constant ({why})")
                    continue
                values = computed[key]()
            for value in values:
                if not isinstance(value, str):
                    unresolved.append(f"{where}: the argument resolves to {value!r}, not a path")
                    continue
                found.setdefault(value, []).append(where)
    return found, unresolved


def package_data(pyproject: Path = REPO / "pyproject.toml") -> list[str]:
    return tomllib.loads(pyproject.read_text(encoding="utf-8"))["tool"]["setuptools"]["package-data"]["gov"]


def _files(base: Path, rel: str) -> dict[str, bytes]:
    top = base / rel
    if top.is_file():
        return {rel: top.read_bytes()}
    return {path.relative_to(base).as_posix(): path.read_bytes() for path in sorted(top.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts}


def problems(rels, repo: Path, shipped_dir: Path, patterns: list[str], package_dir: Path) -> list[str]:
    """What keeps each ``rel`` from being in the wheel byte for byte: no source, a file not in the package data, a copy
    missing or drifted, a file extra in the copy."""
    explicit = {p for p in patterns if not glob.has_magic(p)}
    globbed = {hit for p in patterns if glob.has_magic(p)
               for hit in glob.glob(p, root_dir=package_dir, recursive=True, include_hidden=True)}
    said = []
    for rel in sorted(set(rels)):
        source = _files(repo, rel)
        if not source:
            said.append(f"{rel}: no source in the Gov OS tree")
            continue
        for name, data in source.items():
            entry = f"{shipped_dir.relative_to(package_dir).as_posix()}/{name}"
            if entry not in explicit and entry not in globbed:
                said.append(f"{name}: not in pyproject.toml's package data under \"gov\" ({entry})")
            copy = shipped_dir / name
            if not copy.is_file():
                said.append(f"{name}: no copy at {copy}")
            elif copy.read_bytes() != data:
                said.append(f"{name}: the copy at {copy} differs from its source")
        extra = sorted(set(_files(shipped_dir, rel)) - set(source)) if (shipped_dir / rel).is_dir() else []
        said += [f"{name}: in the copy, not in the source" for name in extra]
    return said


# ---- the scan

def test_every_call_of_the_resolver_has_an_argument_this_test_resolves():
    found, unresolved = scan()
    assert unresolved == []
    for rel in (GITLEAKS, fabric.RETRIEVAL, *(source for source, _ in fabric.KERNEL_FOLDERS + fabric.KERNEL_FILES)):
        assert rel in found, rel  # the scan sees A0's and MA's read and A9's (a scan that finds nothing proves nothing)


def test_a_call_this_test_cannot_resolve_fails_it_naming_the_file_and_the_line(tmp_path):
    src = tmp_path / "src"
    (src / "gov").mkdir(parents=True)
    module = src / "gov" / "w2_88_s29_planted.py"
    module.write_text("from gov.adopt import fabric\n\n\ndef f(rel):\n    return fabric.shipped(rel, None)\n")
    sys.path.insert(0, str(src))
    try:
        sys.modules.pop("gov.w2_88_s29_planted", None)
        importlib.invalidate_caches()
        import gov
        gov.__path__.append(str(src / "gov"))
        try:
            _found, unresolved = scan(src, {})
        finally:
            gov.__path__.remove(str(src / "gov"))
            sys.modules.pop("gov.w2_88_s29_planted", None)
    finally:
        sys.path.remove(str(src))
    assert len(unresolved) == 1 and unresolved[0].startswith("src/gov/w2_88_s29_planted.py:5: the argument rel")


def test_every_rel_the_resolver_is_asked_for_is_in_the_package_data_and_shipped_byte_identical():
    found, _ = scan()
    assert problems(found, REPO, SHIPPED_DIR, package_data(), PACKAGE_DIR) == []


def test_every_rel_the_resolver_is_asked_for_is_in_the_named_list_of_what_the_wheel_carries():
    found, _ = scan()
    outside = [rel for rel in found if not any(rel == each or rel.startswith(each + "/") for each in fabric.PACKAGED)]
    assert outside == []
    assert safety.TEMPLATE_GITLEAKS_REL == GITLEAKS and GITLEAKS in fabric.PACKAGED


def test_the_check_names_a_missing_a_drifted_and_an_unlisted_copy(tmp_path):
    shipped_dir = tmp_path / "gov" / "_shipped"
    shutil.copytree(SHIPPED_DIR, shipped_dir, ignore=shutil.ignore_patterns("__pycache__"))
    found, _ = scan()
    patterns = package_data()
    assert problems(found, REPO, shipped_dir, patterns, tmp_path / "gov") == []
    (shipped_dir / GITLEAKS).unlink()
    retrieval = shipped_dir / fabric.RETRIEVAL
    retrieval.write_bytes(retrieval.read_bytes() + b"\n")
    brief = "template/governance/kernel/templates/brief.md"
    said = problems(found, REPO, shipped_dir, [p for p in patterns if not p.endswith(brief)], tmp_path / "gov")
    assert any(line.startswith(f"{GITLEAKS}: no copy") for line in said), said
    assert any(line.startswith(f"{fabric.RETRIEVAL}: the copy") for line in said), said
    assert any(line.startswith(f"{brief}: not in pyproject.toml's package data") for line in said), said


# ---- A0 from a wheel built in the release form (an export of HEAD: passes only once S29 is committed)

def _run(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def test_a0_from_a_wheel_of_head_commits_the_templates_gitleaks_rules_in_a_repository_with_no_kit(tmp_path):
    pytest.importorskip("setuptools")
    env = {key: value for key, value in os.environ.items() if key not in ("PYTHONPATH", "PYTHONHOME")}
    export, wheels, venv, work = (tmp_path / name for name in ("export", "wheels", "venv", "work"))
    export.mkdir()
    work.mkdir()
    archive = subprocess.run(["git", "-C", str(REPO), "archive", "--format=tar", "HEAD", "--", "pyproject.toml", "src"],
                             capture_output=True, env=env)
    assert archive.returncode == 0, archive.stderr.decode(errors="replace")
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        tar.extractall(export, filter="data")
    built = _run([sys.executable, "-m", "pip", "wheel", "-q", "--no-deps", "--no-build-isolation", "--no-index",
                  "-w", str(wheels), str(export)], env=env, cwd=work)
    if built.returncode != 0:
        pytest.skip("no wheel can be built here offline: " + built.stderr.strip()[-300:])
    made = _run([sys.executable, "-m", "venv", "--system-site-packages", str(venv)], env=env, cwd=work)
    if made.returncode != 0:
        pytest.skip("no venv can be made here: " + made.stderr.strip()[-300:])
    wheel = next(wheels.glob("gov-*.whl"))
    installed = _run([str(venv / "bin/python"), "-m", "pip", "install", "-q", "--no-deps", "--no-index", str(wheel)],
                     env=env, cwd=work)
    assert installed.returncode == 0, installed.stderr
    where = _run([str(venv / "bin/python"), "-c", "import gov; from gov.adopt import fabric; "
                  "print(gov.__file__); print(fabric._source_tree())"], env=env, cwd=work)
    assert where.returncode == 0, where.stderr
    lines = where.stdout.splitlines()
    assert lines[0].startswith(str(venv)) and lines[1] == "None"  # the installed gov, run from no source tree
    root = tmp_path / "planted"
    (root / "lib").mkdir(parents=True)
    (root / "README.md").write_text("a repository with no kit\n")
    (root / "lib/util.py").write_text("def f():\n    return 1\n")
    for args in (("init", "-q"), ("config", "user.name", "t"), ("config", "user.email", "t@example.invalid"),
                 ("add", "-A"), ("commit", "-q", "-m", "planted")):
        assert _run(["git", "-C", str(root), *args], env=env).returncode == 0
    assert not (root / ".gitleaks.toml").exists() and not (root / "governance").exists()
    done = _run([str(venv / "bin/gov"), "adopt", "--root", str(root), "--session", "s29", "--lite", "--stage", "A0"],
                env=env, cwd=work)
    assert done.returncode == 0, done.stdout + done.stderr
    record = project.record_path("A0")
    a0 = _run(["git", "-C", str(root), "log", "-1", "--format=%H", "--", record], env=env).stdout.strip()
    assert a0, "A0 committed no record"
    held = subprocess.run(["git", "-C", str(root), "show", f"{a0}:.gitleaks.toml"], capture_output=True, env=env)
    assert held.returncode == 0, held.stderr.decode(errors="replace")
    assert held.stdout == (REPO / GITLEAKS).read_bytes()
