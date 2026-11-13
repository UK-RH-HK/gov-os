"""Support code for the W2-88 acceptance tests: memory for any repository (DAEO-2bdu; the assessment, the plan, A9 lite).

Everything here plants a repository in a temporary folder and runs the product as a child process (``python -m
gov.cli.main ...``, ``python -m gov.memaudit ...``) with **this worktree's** ``src/`` first on ``PYTHONPATH`` (DEC-732),
a ``HOME`` that is empty, no network (the embedder is a stand-in on a loopback port, W2-124's), and a rebuild lock of the
case's own. Nothing of this repository's store is read, no clone is made, and no real repository is touched.

Reused read-only from other suites (never edited): W2-124's ``Embedder``/``Box``/``environment``/planting helpers, W2-81's
planted-secret builder (``w2_81_secret``) and its builders (``w2_81_build``), W2-170's world (``w2_170_world``), W2-116's
``make_project``/``land_h2``/``integration_build``. The interface the cases hold is README.md's (I1-I7).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ACCEPT = HERE.parent
REPO_ROOT = HERE.parents[2]          # tests/acceptance/W2-88 -> the worktree this file sits in
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
for _name in ("W2-124", "W2-81", "W2-170", "W2-116"):
    if str(ACCEPT / _name) not in sys.path:
        sys.path.insert(0, str(ACCEPT / _name))

import w2_124_support as S124  # noqa: E402
import w2_81_secret as W81S  # noqa: E402

TICKET = "DAEO-2bdu"
SESSION = "adopter-w2-88"
FILE_LIMIT_FALLBACK = 1_048_576        # I1's proposal; the cases read assess.FILE_LIMIT_BYTES where the module exists
READ_CHARS_FALLBACK = 32768            # chunking.READ_CHARS
ASSESSMENT = "memory-assessment.json"
PLAN_DIR = "refactor-plan"
KINDS = ("vendored-no-folder", "generated-no-folder", "namespace-policy", "over-limit", "secret", "no-namespace",
         "two-namespaces")
STORES = ("record", "lexical", "vectors", "codegraph")
STORE_FIELDS = ("judged", "indexed", "refused", "chunks", "vectors", "nodes", "edges", "seconds", "peak_rss_bytes")
DIGESTS = ("record", "lexical", "vectors", "codegraph_bytes")
REFUSE_REASONS = ("secrets", "binary", "not-embedded", "unsupported-language", "over-limit")
CHAIN = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8")
RETRIEVAL_SRC = REPO_ROOT / "governance/project/retrieval.yaml"   # "as Gov OS ships it": a planted adoption holds a copy
EVIDENCE_REL = "docs/changes/W2-88-evidence.md"


# ------------------------------------------------------------------------------------------------------------
# What the module under test states (read, never restated)
# ------------------------------------------------------------------------------------------------------------

def limits() -> tuple[int, int]:
    """(``assess.FILE_LIMIT_BYTES``, ``chunking.READ_CHARS``); I1's proposed numbers where ``assess`` does not exist
    yet, so a case still plants and fails on what it checks (the module's absence is its own case)."""
    from gov.retrieval import chunking
    try:
        from gov.adopt import assess
        return int(assess.FILE_LIMIT_BYTES), int(chunking.READ_CHARS)
    except (ImportError, AttributeError):
        return FILE_LIMIT_FALLBACK, int(chunking.READ_CHARS)


def per_session_figure() -> int:
    """The resource gate's per-session figure: ``working_size_bytes`` as ``gov.resources.config`` reads it (the machine's
    ``gate.json`` under the real home, else under the current environment, else the template's value). Never restated."""
    import pwd
    from gov.resources import config
    real = {**os.environ, "HOME": pwd.getpwuid(os.getuid()).pw_dir}
    for environment in (real, None):
        try:
            values = config.load(environment).get("values") or {}
        except Exception:  # noqa: BLE001: a machine without the file reads as the template
            continue
        value = values.get("working_size_bytes")
        if isinstance(value, dict):
            value = value.get("value")
        if isinstance(value, int) and value > 0:
            return value
    return int(config.template()["working_size_bytes"]["value"])


# ------------------------------------------------------------------------------------------------------------
# Files, git, fingerprints
# ------------------------------------------------------------------------------------------------------------

def write(root: Path, rel: str, data) -> Path:
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")
    return path


def git(root, *args) -> str:
    return S124.git(root, *args)


def commit_all(root, message: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", message)


def head(root) -> str:
    return git(root, "rev-parse", "HEAD").strip()


def _tree_digest(root: Path, skip_git: bool) -> str:
    digest = hashlib.sha256()
    for folder, dirs, files in os.walk(root):
        dirs.sort()
        if skip_git and ".git" in dirs and Path(folder) == root:
            dirs.remove(".git")
        for name in sorted(files) + [d for d in dirs if os.path.islink(os.path.join(folder, d))]:
            path = Path(folder) / name
            rel = path.relative_to(root).as_posix()
            info = path.lstat()
            digest.update(f"{rel}\0{stat.S_IMODE(info.st_mode):o}\0".encode())
            digest.update(os.readlink(path).encode() if stat.S_ISLNK(info.st_mode) else path.read_bytes())
    return digest.hexdigest()


def settle(root) -> None:
    """Let git's racy-timestamp window pass and refresh the index once, so a read-only tool that runs ``git status``
    changes no byte of it (the case compares the index file itself)."""
    time.sleep(1.2)
    git(root, "status", "--porcelain")
    git(root, "update-index", "--refresh")


def repo_state(root) -> dict:
    """Tree (working files), index (file and ``ls-files -s``), history (``log --all`` and refs), ``.git`` as a whole,
    ``status --porcelain``: the five things the lines hold byte-identical."""
    root = Path(root)
    index = (root / ".git" / "index").read_bytes()
    return {
        "tree": _tree_digest(root, skip_git=True),
        "git": _tree_digest(root / ".git", skip_git=False),
        "index_file": hashlib.sha256(index).hexdigest(),
        "index_entries": git(root, "ls-files", "-s"),
        "history": git(root, "log", "--all", "--format=%H %T %P %an %ae %cd %s") + git(root, "for-each-ref"),
        "porcelain": git(root, "status", "--porcelain", "--untracked-files=all"),
    }


def assert_state_equal(before: dict, after: dict, what: str) -> None:
    changed = [key for key in before if before[key] != after[key]]
    assert not changed, f"{what}: the repository changed ({', '.join(changed)}); any difference is a failure"


# ------------------------------------------------------------------------------------------------------------
# The environment and the runs
# ------------------------------------------------------------------------------------------------------------

def make_box(base: Path):
    reason = S124.lacking()
    if reason:
        import pytest
        pytest.skip(reason)
    return S124.make_box(Path(base) / "box")


def env(box, host: str, *, tools=(), code_graph: bool = False, **extra) -> dict:
    """W2-124's hermetic environment (an empty HOME, real gitleaks, no ollama program, no secrets cache, a lock of the
    case's own), with this worktree's ``src/`` first on PYTHONPATH. ``tools`` are folders put first on PATH (a logging
    ``tk`` or ``crontab``); the real code-graph tool is on PATH only for ``code_graph=True`` (a ``local_only`` case)."""
    folders = [*(str(t) for t in tools), str(box.tools), str(Path(sys.executable).parent), "/usr/bin", "/bin"]
    values = {"PYTHONPATH": str(SRC)}
    standin = os.environ.get("W2_88_STANDIN")          # a bite check only (README, "Bite checks"): a stand-in folder first
    if standin:
        values["PYTHONPATH"] = standin + os.pathsep + str(SRC)
        values["W2_88_STANDIN_MODE"] = os.environ.get("W2_88_STANDIN_MODE", "good")
    if code_graph:
        tool = shutil.which("codebase-memory-mcp") or str(Path.home() / ".local/bin/codebase-memory-mcp")
        folders.append(str(Path(tool).parent))
        values["CODEINTEL_DAEMON_BASE"] = str(Path(box.base) / "cbm")
    values["PATH"] = os.pathsep.join(folders)
    values.update(extra)
    return S124.environment(box, host, **values)


def rebuild(project, box, host: str, *extra):
    """``gov rebuild <extra>`` in ``project`` with this suite's environment (a stand-in folder first on a bite check)."""
    return S124.gov(project, env(box, host), "rebuild", *extra)


def run_adopt(project, environment, stage: str, *extra, session: str = SESSION):
    return S124.gov(project, environment, "adopt", "--lite", "--stage", stage, *extra, "--json", "--session", session)


def stage_not_offered(run) -> bool:
    return run.returncode == 2 and "invalid choice" in (run.stderr or "")


def assert_offered(run, stage: str) -> None:
    assert not stage_not_offered(run), \
        f"gov adopt --lite does not take --stage {stage} on this head (argparse: invalid choice)\n{run.describe()}"


def assert_ok(run, what: str) -> dict:
    assert run.returncode == 0 and run.envelope().get("ok") is True, f"{what} did not succeed\n{run.describe()}"
    return run.result


def error_text(run) -> str:
    """The code and the message of the refusal, as the envelope states them."""
    err = run.error
    return f"{err.get('code', '')} {err.get('message', '')} {json.dumps(err.get('details', ''))}"


def assert_refused(run, code: str, what: str, stage: str = "A9") -> None:
    assert_offered(run, stage)
    assert run.returncode != 0 and run.envelope().get("ok") is False, f"{what}: expected a refusal\n{run.describe()}"
    assert run.returncode != 2, f"{what}: a usage error is no refusal\n{run.describe()}"
    assert code in error_text(run), f"{what}: the refusal does not name {code}\n{run.describe()}"


# ------------------------------------------------------------------------------------------------------------
# The planted repository of the assessment (S1, F1, F4, F5)
# ------------------------------------------------------------------------------------------------------------

PLANT = {
    "vendored": "vendor/acme/lib.py", "generated": "gen/tables.py", "minified": "static/app.min.js",
    "binary": "assets/logo.png", "over_limit": "data/big.txt", "wide_line": "data/wide.txt",
    "secret": "config/settings.env", "unsupported": "legacy/report.cob",
}
GENERATED_HEADER = "# Code generated by tablegen. DO NOT EDIT.\n"
VENDORED_HEADER = "# Vendored from github.com/acme/lib v1.2.0 (third-party code, kept as published).\n"
NORMAL = {
    "README.md": "# Orchard\n\nA planted repository of the W2-88 tests.\n",
    "docs/guide.md": "# Guide\n\nThe orchard's rows are numbered from the gate.\n",
    "src/app/main.py": "def main():\n    return 'orchard'\n",
    "src/app/util.py": "def rows(n):\n    return list(range(n))\n",
}


@dataclass
class Orchard:
    root: Path
    secret: object            # W2-81's Held: never printed
    file_limit: int
    read_chars: int
    commit: str

    def secret_in(self, text) -> bool:
        return self.secret.found_in(text)


def path_map_text(namespaces: dict | None = None) -> str:
    """A path map in the kernel schema's form (W2-124's ``adoption_path_map``) with the namespaces of the case."""
    document = S124.adoption_path_map()
    if namespaces is not None:
        template = next(iter(document["namespaces"].values()))
        document["namespaces"] = {name: {**template, **spec} for name, spec in namespaces.items()}
    return yaml.safe_dump(document, sort_keys=False)


ORCHARD_NAMESPACES = {"orchard": {"paths": ["**"], "embedding_policy": "embedded"}}


def plant_orchard(base: Path, name: str = "orchard", *, files: dict | None = None, big: bool = True) -> Orchard:
    """Every item S1 names, committed clean (two commits): a vendored folder, a generated file (by header), a minified
    file (by name), a binary, a file over the limit (by size) and one with a line over ``READ_CHARS``, a secret in a
    tracked file (a value the repository's gitleaks rules refuse: W2-81's ``cloud-access-key``), and a file in a
    language the code graph does not read."""
    file_limit, read_chars = limits()
    root = Path(base) / name
    root.mkdir(parents=True)
    write(root, ".gitignore", ".gov-runtime/\n__pycache__/\n")
    shutil.copy2(S124.GITLEAKS_TEMPLATE, root / ".gitleaks.toml")
    write(root, "governance/project/path-map.yaml", path_map_text(ORCHARD_NAMESPACES))
    for rel, text in NORMAL.items():
        write(root, rel, text)
    git(root, "init", "-q", "-b", "main")
    commit_all(root, "the orchard")
    secret = W81S.make_secret("cloud-access-key", seed=88, salt="orchard")
    write(root, PLANT["vendored"], "def vendored():\n    return 'acme'\n")
    write(root, "vendor/acme/README.md", "# acme\n\nCopied as published.\n")
    write(root, PLANT["generated"], GENERATED_HEADER + "ROWS = [1, 2, 3]\n")
    write(root, PLANT["minified"], "!function(){" + ";".join(f"a{n}=function(){{return {n}}}" for n in range(300)) + "}();")
    write(root, PLANT["binary"], b"\x89PNG\r\n\x1a\n" + bytes(range(256)) * 8 + b"\x00\x00\x00\x00")
    if big:
        write(root, PLANT["over_limit"], ("row of the long table\n" * ((file_limit // 22) + 400)))
    write(root, PLANT["wide_line"], "x" * (read_chars + 100) + "\n")
    write(root, PLANT["secret"], secret.line("AWS_ACCESS_KEY_ID={value}\nREGION=eu-west-1\n"))
    write(root, PLANT["unsupported"], "       IDENTIFICATION DIVISION.\n       PROGRAM-ID. ORCHARD.\n")
    for rel, data in (files or {}).items():
        write(root, rel, data)
    commit_all(root, "the orchard's problems")
    return Orchard(root, secret, file_limit, read_chars, head(root))


def listed(record: dict, key: str) -> list:
    value = record.get(key)
    assert isinstance(value, list), f"the record's {key!r} is no list: {value!r}"
    return value


def holds(items: list, rel: str, by: str | None = None, **more) -> bool:
    """Whether a category list names ``rel`` (the file, or a folder it lies in); with ``by`` its ``by`` too."""
    for item in items:
        path = item if isinstance(item, str) else (item or {}).get("path")
        if not isinstance(path, str):
            continue
        base = path.rstrip("/")
        if rel == base or rel.startswith(base + "/"):
            if by is not None and (not isinstance(item, dict) or item.get("by") != by):
                continue
            if all(isinstance(item, dict) and item.get(key) == value for key, value in more.items()):
                return True
    return False


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def all_text(*folders: Path, runs=()) -> dict:
    """Name -> text of every file under ``folders`` and every captured stream of ``runs`` (never the secret's value
    is looked for here: the caller searches)."""
    found = {}
    for folder in folders:
        folder = Path(folder)
        if not folder.exists():
            continue
        for path in sorted(p for p in folder.rglob("*") if p.is_file()):
            found[str(path)] = path.read_bytes()
    for number, run in enumerate(runs):
        found[f"run{number}.stdout"] = run.stdout.encode()
        found[f"run{number}.stderr"] = run.stderr.encode()
    return found


def assert_no_secret(held, texts: dict, what: str) -> None:
    for name, data in texts.items():
        assert not held.found_in(data), f"{what}: the planted secret's value appears whole in {Path(name).name}"


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------------------
# Logging stand-ins on PATH (tk, crontab)
# ------------------------------------------------------------------------------------------------------------

def logging_tool(folder: Path, name: str, log: Path, *, answer: str = "") -> Path:
    """A program ``name`` in ``folder`` that appends its argv to ``log`` and prints ``answer``: every call is seen."""
    folder.mkdir(parents=True, exist_ok=True)
    program = folder / name
    program.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> " + json.dumps(str(log)) + "\n"
                       + (f"printf '%s' {json.dumps(answer)}\n" if answer else "") + "exit 0\n", encoding="utf-8")
    program.chmod(0o755)
    return folder


# ------------------------------------------------------------------------------------------------------------
# A planted adoption through A8 (A9's start)
# ------------------------------------------------------------------------------------------------------------

DROP = S124.DROP
ADOPT_PATHS = (".gitignore", ".gitleaks.toml", "README.md", "governance/**", "docs/**", "lib/**", "audit/**",
               "assets/**", "config/**", "legacy/**")


def adoption_namespaces(not_embedded: bool = True) -> dict:
    spaces = {"harbour": {"paths": list(ADOPT_PATHS), "embedding_policy": "embedded"}}
    if not_embedded:
        spaces["archive"] = {"paths": ["archive/**"], "embedding_policy": "not embedded"}
    return spaces


def plant_adoption(box, name: str = "harbour", *, retrieval: str | None = None, code_intelligence: bool = False,
                   extra: dict | None = None) -> Path:
    """S124's legacy repository, with what A9's record judges: a tracked binary and a tracked secret (refused), a note in
    a namespace that is not embedded, the repository's ``retrieval.yaml`` as Gov OS ships it, and a path map with the
    namespaces of ``adoption_namespaces``."""
    project = Path(box.base) / name
    project.mkdir(parents=True)
    write(project, ".gitignore", ".gov-runtime/\n__pycache__/\n*.pyc\n")
    shutil.copy2(S124.GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    document = yaml.safe_load(path_map_text(adoption_namespaces()))
    if code_intelligence:
        document["capabilities"]["code_intelligence"] = {"enabled": True, "languages": ["python"]}
    write(project, S124.PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    write(project, "governance/project/retrieval.yaml",
          retrieval if retrieval is not None else RETRIEVAL_SRC.read_text(encoding="utf-8"))
    write(project, "README.md", "# Harbour\n\nA programme's own repository, planted by the W2-88 tests.\n")
    write(project, "docs/guide.md", "# Guide\n\nHow the harbour is run.\n")
    write(project, "docs/notes.txt", "Tide tables are kept by the harbour master.\n")
    write(project, "lib/__init__.py", '"""Loose helpers."""\n')
    write(project, "lib/util.py", "def helper():\n    return 41\n")
    write(project, DROP, "Removed from the active tree by batch 1.\n")
    write(project, "archive/old.md", "# Old note\n\nThe archived mooring plan of the harbour.\n")
    write(project, "assets/logo.bin", b"\x00\x01\x02\x03binary\x00" * 64)
    secret = W81S.make_secret("cloud-access-key", seed=88, salt="harbour")
    write(project, "config/settings.env", secret.line("AWS_ACCESS_KEY_ID={value}\n"))
    for rel, data in (extra or {}).items():
        write(project, rel, data)
    git(project, "init", "-q", "-b", "main")
    commit_all(project, "the programme's repository")
    return project


def harbour_secret():
    return W81S.make_secret("cloud-access-key", seed=88, salt="harbour")


class Adoption(S124.Adoption):
    """W2-124's adoption driver with this suite's environment; ``chain`` runs A0..A8 and, before A3, the memory
    assessment (MA) into ``out`` where the head offers the stage (else A3 runs as it does today, so a case still reaches
    what it checks and the missing stage is that case's own red reason)."""

    def __init__(self, project, box, host, *, tools=(), code_graph=False, extra_env=None):
        super().__init__(project, box, host)
        self.tools, self.code_graph, self.extra_env = tools, code_graph, dict(extra_env or {})
        self.out = Path(box.base) / "memory-out"
        self.ma_run = None

    def env(self):
        return env(self.box, self.host, tools=self.tools, code_graph=self.code_graph, **self.extra_env)

    def chain(self, last: str = "A8"):
        """Run A0..``last``; the first run that did not succeed (None when every one did)."""
        proposal = self.box.base / "proposal.yaml"
        proposal.write_text(yaml.safe_dump({"artefacts": [{"path": DROP, "action": "DELETE_FROM_ACTIVE_TREE",
                                                           "batch": 1}]}, sort_keys=False), encoding="utf-8")
        for stage in CHAIN[:CHAIN.index(last) + 1]:
            if stage == "A3":
                self.ma_run = self.run("MA", "--out", str(self.out))
                if stage_not_offered(self.ma_run):
                    run = self.run(stage, "--map", str(proposal))
                elif self.ma_run.returncode != 0:
                    return self.ma_run
                else:
                    run = self.run(stage, "--map", str(proposal), "--assessment", str(self.out))
            elif stage == "A5":
                self.write_verdict()
                run = self.run(stage, "--verdict", S124.VERDICT_REL)
            else:
                run = self.run(stage)
            if run.returncode != 0:
                return run
        return None

    def a9(self, out: Path, *extra):
        return self.run("A9", "--out", str(out), *extra)


def front_of(project, rel: str) -> dict:
    """The frontmatter of a committed record (at HEAD)."""
    text = git(project, "show", f"HEAD:{rel}")
    parts = text.split("---\n")
    assert len(parts) >= 3, f"{rel} has no frontmatter"
    return yaml.safe_load(parts[1])


def a9_record(project, run) -> dict:
    """The A9 record: its frontmatter, found by the stage's own answer, else under ``governance/adoption/``."""
    rel = run.result.get("record")
    if not rel:
        names = [n for n in git(project, "ls-files", "governance/adoption").splitlines() if "/A9" in n]
        assert names, f"A9 committed no record under governance/adoption/\n{run.describe()}"
        rel = names[0]
    return front_of(project, rel)


def ready_a9(box, host, name: str = "harbour", *, tools=(), plant_options=None):
    """A planted adoption through A8, ready for A9; returns (project, adoption). Fails by naming the stage that
    did not run."""
    project = plant_adoption(box, name, **(plant_options or {}))
    adoption = Adoption(project, box, host, tools=tools)
    failed = adoption.chain("A8")
    assert failed is None, f"the planted adoption did not reach A8: {failed.describe()}"
    return project, adoption


# ------------------------------------------------------------------------------------------------------------
# Forks of a planted adoption (the same commit, a copy of a temporary project the cases made, never of this repository)
# ------------------------------------------------------------------------------------------------------------

def fork(nine, name: str, retrieval: str | None = None) -> "Adoption":
    """A copy of the planted adoption at A8 (its ``.git`` with its refs, no ``.gov-runtime/``), optionally with another
    ``retrieval.yaml`` committed on top."""
    dest = Path(nine.box.base) / name
    shutil.copytree(nine.project, dest, symlinks=True, ignore=shutil.ignore_patterns(".gov-runtime"))
    if retrieval is not None:
        write(dest, "governance/project/retrieval.yaml", retrieval)
        commit_all(dest, "retrieval.yaml departs from the standard")
    return Adoption(dest, nine.box, nine.adoption.host, tools=nine.adoption.tools, code_graph=nine.adoption.code_graph,
                    extra_env=nine.adoption.extra_env)


def retrieval_variant(kind: str) -> str:
    """The repository's ``retrieval.yaml`` (as Gov OS ships it) with one setting changed: ``pool-off``,
    ``second-reranker`` or ``bundle-budget`` (the keys are ``fabric.STANDARD``'s names, I3)."""
    document = yaml.safe_load(RETRIEVAL_SRC.read_text(encoding="utf-8"))
    if kind == "pool-off":
        document.pop("pool", None)
    elif kind == "second-reranker":
        document["reranker"] = "bge-reranker-v2-m3"
    elif kind == "bundle-budget":
        document["bundle_tokens"] = 4000
    else:
        raise ValueError(kind)
    return yaml.safe_dump(document, sort_keys=False)


def child_gov(adoption, script: str, *args):
    """A suite program (``script``) run as a child in the adoption's project, with its environment."""
    import subprocess
    return subprocess.run([sys.executable, str(HERE / script), *map(str, args)], cwd=str(adoption.project),
                          env=adoption.env(), capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
