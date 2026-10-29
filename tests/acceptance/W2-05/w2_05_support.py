"""Support code for the W2-05 acceptance tests (DAEO-0z8c): the git environment of every check, hook and helper,
and lefthook's re-sort of ``.claude/settings.json``.

How the tests run (README, "How the tests run"):

- **The code under test is this worktree's ``src/``** (DEC-732). ``SRC`` is derived from this file's own place
  (``tests/acceptance/W2-05/`` -> ``../../../src``). Every process a case starts that imports or runs ``gov``
  gets it first on ``PYTHONPATH``: the ``gov`` on the box's ``PATH`` is a launcher that puts it first on
  ``sys.path``, and every environment of this module names it on ``PYTHONPATH``.
- **Every repository is temporary and built from scratch** under pytest's ``tmp_path``: a repository with a
  linked worktree, a decoy repository, a bare remote, a stand-in dev tier (W1-21's fixture, built by its public
  support). A case receives single named files of this repository (the hooks file, a check declaration, the
  gitleaks rules), never a folder of it.
- **No hook is installed in this repository.** ``lefthook`` runs only in a temporary repository, with its
  working directory there and an environment built from nothing (no ``GIT_*`` variable of the caller).
- **No model, no network.** The embeddings endpoint is W1-21's stand-in on a loopback port.
- **This repository's ``.claude/settings.json`` is never read**: the settings cases write a stand-in, or take
  what ``rulesync generate`` writes from the kernel template's sources (W1-38's public support).
"""

from __future__ import annotations

import hashlib
import json
import os
import pwd
import re
import shutil
import signal
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SRC = REPO_ROOT / "src"
ACCEPTANCE = HERE.parent

# Earlier suites whose public supports these cases reuse (each imported by name where it is needed).
for _suite in ("W1-02", "W1-03", "W1-16", "W1-21", "W1-38", "W1-40", "W2-01"):
    _folder = str(ACCEPTANCE / _suite)
    if _folder not in sys.path:
        sys.path.append(_folder)

# ---- the ticket's deliverables (its allowed_paths)
SWEEP_REL = "docs/research/AR-2-git-sweep.md"
HELPER_REL = "src/gov/util/gitenv.py"
HELPER_MODULE = "gov.util.gitenv"
LEFTHOOK_YML = REPO_ROOT / "lefthook.yml"
TEMPLATE_HOOKS = REPO_ROOT / "template" / "lefthook.yml.jinja"   # the template's hooks file as it is in the tree

# ---- what the cases read from this repository (single named files)
CHECKS_REL = "template/governance/kernel/checks"
RETRIEVAL_CHECK = REPO_ROOT / CHECKS_REL / "retrieval-regression.yaml"
GITLEAKS_RULES = REPO_ROOT / "template" / ".gitleaks.toml"
# The two Claude Code hooks sources adapter-portability compares (W2-M281; DEC-783 item 3, DEC-805).
REPO_HOOKS_SOURCE_REL = ".rulesync/hooks.jsonc"
TEMPLATE_HOOKS_SOURCE_REL = "template/.rulesync/hooks.jsonc"

SYSTEM_PATH = "/usr/bin:/bin"
CALL_TIMEOUT_S = 300.0
HOOKED_COMMIT_TIMEOUT_S = 90.0   # a hooked commit that runs the retrieval check ends in about 5 s on this machine
BRANCH = "main"
WORKTREE_BRANCH = "w2-05/feature"

# The identity of the person committing, as a machine's own git configuration gives it (not a GIT_* variable).
USER_NAME, USER_EMAIL = "W2-05 person", "w2-05@example.invalid"

TRACE_VARIABLES = ("GIT_TRACE", "GIT_TRACE2_EVENT", "GIT_TRACE2", "GIT_TRACE_PACKET", "GIT_TRACE_SETUP")

# The code index's external tool, as W1-16's README names it (it starts git in the project itself), and the
# package of the code index (W1-16's public interface, ``gov.codeintel``).
CODE_INDEX_TOOL = "codebase-memory-mcp"
CODE_INDEX_PACKAGE_REL = "src/gov/codeintel"

# A token by the template's gitleaks rules (W1-40's ``PLAIN``, never written whole in this file).
SECRET = "sk_" + "7Qd2" + "Xk9Lm4Wp8Zr3Tb6V"


class Absent(AssertionError):
    """Something the ticket delivers is not there."""


# --------------------------------------------------------------------------
# tools of this machine
# --------------------------------------------------------------------------

def real_tool(name):
    """The path of a tool on this machine, or None: ``PATH``, then ``~/.local/bin``."""
    found = shutil.which(name)
    if found:
        return found
    local = Path(pwd.getpwuid(os.getuid()).pw_dir) / ".local" / "bin" / name
    return str(local) if local.is_file() and os.access(local, os.X_OK) else None


GIT = shutil.which("git", path=SYSTEM_PATH) or real_tool("git")


def _lacking():
    lacking = {}
    for name in ("lefthook", "gitleaks", "rulesync"):
        if real_tool(name) is None:
            lacking[name] = f"{name} is not installed on this machine (PATH, ~/.local/bin)"
    try:
        import importlib.util
        if importlib.util.find_spec("sqlite_vec") is None:
            lacking["sqlite_vec"] = f"sqlite_vec cannot be imported by {sys.executable}; no vector can be stored"
    except ImportError:
        lacking["sqlite_vec"] = "importlib cannot look for sqlite_vec"
    if GIT is None:
        lacking["git"] = "git is not installed on this machine"
    return lacking


LACKING = _lacking()


def lacking(*names):
    return [LACKING[name] for name in names if name in LACKING]


def skip_without(*names):
    """Skip the case, with the stated reason, when a tool it needs is not on this machine (README)."""
    import pytest
    reasons = lacking(*names)
    if reasons:
        pytest.skip("; ".join(reasons))


# --------------------------------------------------------------------------
# the setup's own git: a clean environment, never a hook's
# --------------------------------------------------------------------------

def clean_env():
    """The environment of the cases' own git calls: no ``GIT_*`` of the caller, no user configuration."""
    return {
        "PATH": SYSTEM_PATH, "HOME": "/nonexistent-w2-05-home", "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0",
        "GIT_AUTHOR_NAME": "W2-05 setup", "GIT_AUTHOR_EMAIL": "setup@example.invalid",
        "GIT_COMMITTER_NAME": "W2-05 setup", "GIT_COMMITTER_EMAIL": "setup@example.invalid",
    }


def git(cwd, *args, check=True, env=None):
    done = subprocess.run([GIT, "-C", str(cwd), *[str(a) for a in args]], capture_output=True, text=True,
                          env=env or clean_env(), timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
    if check and done.returncode != 0:
        raise AssertionError(f"git {' '.join(str(a) for a in args)} failed in {cwd}:\n{done.stdout}\n{done.stderr}")
    return done.stdout


def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def said(done):
    out = getattr(done, "stdout", "") or ""
    err = getattr(done, "stderr", "") or ""
    return f"exit {done.returncode}\n--- stdout\n{out[-3000:]}\n--- stderr\n{err[-3000:]}"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def folder_fingerprint(folder):
    """``relative path -> sha256 of the bytes`` of every file under ``folder``, ``.git`` included, and the
    symbolic links by their target. A folder no process may touch keeps it exactly."""
    folder = Path(folder)
    found = {}
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder).as_posix()
        if path.is_symlink():
            found[rel] = "link:" + os.readlink(path)
        elif path.is_file():
            found[rel] = sha256(path.read_bytes())
    return found


# --------------------------------------------------------------------------
# the box: the machine a hook, a check or a command runs on
# --------------------------------------------------------------------------

def _launcher(path):
    """The console script an install of this worktree's package generates, with this worktree's src first."""
    target = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]["gov"]
    module, _, attribute = target.partition(":")
    path.write_text(
        f"#!{sys.executable}\n"
        "import sys\n"
        f"sys.path.insert(0, {str(SRC)!r})\n"
        f"from {module} import {attribute} as _main\n"
        "sys.argv[0] = 'gov'\n"
        "sys.exit(_main())\n", encoding="utf-8")
    path.chmod(0o755)


class Box:
    """A machine as a hook sees it: a ``bin`` folder (git, gitleaks, lefthook, python3, and ``gov`` running this
    worktree's src), an empty home whose git configuration names the person committing, a temporary folder,
    and a folder for marks outside every repository."""

    def __init__(self, base):
        self.base = Path(base)
        self.bin = self.base / "bin"
        self.home = self.base / "home"
        self.tmp = self.base / "tmp"
        self.marks = self.base / "marks"
        self.pycache = self.base / "pycache"
        for folder in (self.bin, self.home, self.tmp, self.marks, self.pycache):
            folder.mkdir(parents=True, exist_ok=True)
        for name in ("git", "gitleaks", "lefthook"):
            found = GIT if name == "git" else real_tool(name)
            if found:
                (self.bin / name).symlink_to(found)
        (self.bin / "python3").symlink_to(sys.executable)
        _launcher(self.bin / "gov")
        self.site = self._link_sqlite_vec()
        self.user_config(None)

    def _link_sqlite_vec(self):
        """A folder that links the one package ``sqlite_vec`` (as W1-21's ``Api`` does): the empty home has no
        user site folder, and no other installed package (a model library) is seen."""
        import importlib.util
        spec = importlib.util.find_spec("sqlite_vec")
        if spec is None or not spec.origin:
            return None
        origin = Path(spec.origin)
        source = origin.parent if spec.submodule_search_locations else origin
        folder = self.base / "site"
        folder.mkdir(exist_ok=True)
        (folder / source.name).symlink_to(source, target_is_directory=source.is_dir())
        return folder

    def user_config(self, extra):
        """The person's own git configuration (``~/.gitconfig``): their name, and ``extra`` lines when given."""
        text = f"[user]\n\tname = {USER_NAME}\n\temail = {USER_EMAIL}\n" + (extra or "")
        (self.home / ".gitconfig").write_text(text, encoding="utf-8")

    def env(self, **extra):
        env = {
            "PATH": f"{self.bin}:{SYSTEM_PATH}",
            "HOME": str(self.home),
            "TMPDIR": str(self.tmp),
            "LC_ALL": "C.UTF-8",
            "PYTHONPATH": str(SRC),
            "PYTHONPYCACHEPREFIX": str(self.pycache),
            "PYTHONDONTWRITEBYTECODE": "1",
            "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
        }
        if self.site is not None:
            env["PYTHONPATH"] = os.pathsep.join([str(SRC), str(self.site)])
        env.update({key: str(value) for key, value in extra.items()})
        return env

    def run(self, args, cwd, env=None, timeout=CALL_TIMEOUT_S, **extra):
        """Run ``args`` in a process group of its own. A run that does not end within ``timeout`` is stopped
        with everything it started (its group, and every process left under the case's folder), and the case
        fails with that: a hooked commit whose check starts the same hook again never ends (README)."""
        return run_bounded([str(a) for a in args], cwd, env or self.env(**extra), timeout, self.base.parent)


def run_bounded(args, cwd, env, timeout, folder):
    process = subprocess.Popen(args, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        stop_group(process.pid)
        reap(folder)
        try:
            out, err = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            out, err = "", ""
        raise AssertionError(
            f"`{' '.join(args)}` in {cwd} did not end within {timeout:.0f} s and was stopped with every process "
            f"it started.\n--- stdout\n{(out or '')[-2000:]}\n--- stderr\n{(err or '')[-2000:]}") from None
    return subprocess.CompletedProcess(args, process.returncode, out, err)


def stop_group(pid):
    try:
        os.killpg(pid, signal.SIGKILL)
    except OSError:
        pass


def _under(pid, marker):
    try:
        command = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return False
    try:
        cwd = os.readlink(f"/proc/{pid}/cwd")
    except OSError:
        cwd = ""
    return marker in command or cwd == marker or cwd.startswith(marker + "/")


def reap(folder, rounds=40):
    """Stop every process whose command line names ``folder`` or whose working folder lies under it (a case's
    own temporary folder: nothing else is touched). Returns how many were stopped."""
    marker = str(Path(folder).resolve())
    me, stopped = os.getpid(), 0
    for _ in range(rounds):
        found = [int(p) for p in os.listdir("/proc") if p.isdigit() and int(p) != me and _under(int(p), marker)]
        if not found:
            break
        for pid in found:
            try:
                os.kill(pid, signal.SIGKILL)
                stopped += 1
            except OSError:
                pass
        time.sleep(0.1)
    return stopped


# --------------------------------------------------------------------------
# repositories
# --------------------------------------------------------------------------

def new_repo(root, files=None, message="initial"):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", BRANCH)
    for rel, text in (files or {"README.md": "# A project\n"}).items():
        write(root, rel, text)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)
    return root


def add_worktree(repo, path, branch=WORKTREE_BRANCH):
    git(repo, "worktree", "add", "-q", str(path), "-b", branch)
    return Path(path)


def git_dir_of(tree):
    """The git directory of a working tree (the worktree's own for a linked worktree)."""
    return Path(git(tree, "rev-parse", "--absolute-git-dir").strip())


def common_dir_of(tree):
    out = git(tree, "rev-parse", "--git-common-dir").strip()
    path = Path(out)
    return path if path.is_absolute() else (Path(tree) / path).resolve()


def make_decoy(base, name="decoy"):
    """A decoy repository: one commit, a second branch, a staged change in its index. Nothing may touch it."""
    decoy = new_repo(Path(base) / name, {"DECOY.md": "# the decoy\n"}, "decoy commit")
    git(decoy, "branch", "decoy-branch")
    write(decoy, "staged.md", "staged in the decoy\n")
    git(decoy, "add", "staged.md")
    return decoy


def planted(decoy):
    """The two variables of the failure KPI, pointing at the decoy's repository and index."""
    git_dir = Path(decoy) / ".git"
    return {"GIT_DIR": str(git_dir), "GIT_INDEX_FILE": str(git_dir / "index")}


@dataclass
class RepoState:
    refs: dict          # ref -> commit, every ref of the repository
    reflogs: dict       # ref (and each worktree's HEAD) -> [commit, ...], newest first
    indexes: dict       # working tree -> ``git ls-files --stage`` output
    reachable: set      # every commit reachable from a ref or a reflog
    heads: dict         # working tree -> HEAD commit


def _reflog(tree, ref):
    done = subprocess.run([GIT, "-C", str(tree), "reflog", "show", "--format=%H", ref, "--"], capture_output=True,
                          text=True, env=clean_env(), timeout=CALL_TIMEOUT_S)
    return done.stdout.split() if done.returncode == 0 else []


def repo_state(main, trees):
    """What a hooked commit may change in a repository, read with the setup's clean git: refs, reflogs, the
    index of every working tree, the commits reachable from refs and reflogs, the head of every tree."""
    refs = {}
    for line in git(main, "for-each-ref", "--format=%(refname) %(objectname)").splitlines():
        name, _, value = line.partition(" ")
        refs[name] = value
    reflogs = {name: _reflog(main, name) for name in refs if name.startswith("refs/heads/")}
    indexes, heads = {}, {}
    for tree in trees:
        reflogs[f"HEAD of {Path(tree).name}"] = _reflog(tree, "HEAD")
        indexes[str(tree)] = git(tree, "ls-files", "--stage")
        heads[str(tree)] = git(tree, "rev-parse", "HEAD").strip()
    reachable = set(git(main, "rev-list", "--all", "--reflog").split())
    return RepoState(refs, reflogs, indexes, reachable, heads)


def staged_tree(tree):
    """The tree the index of ``tree`` holds (what a commit made now would record)."""
    return git(tree, "write-tree").strip()


def index_outside_the_git_directory(repo, path, files):
    """An index file at ``path``, outside the repository's git directory, as a person or a tool that commits
    with ``GIT_INDEX_FILE=<file>`` makes one: ``HEAD``'s tree, with ``files`` (``rel -> text``) staged in it
    only. The repository's own index and working tree are not touched."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    env = dict(clean_env(), GIT_INDEX_FILE=str(path))
    git(repo, "read-tree", "HEAD", env=env)
    for number, (rel, text) in enumerate(files.items()):
        content = path.parent / f"content-{number}"
        content.write_text(text, encoding="utf-8")
        blob = git(repo, "hash-object", "-w", content).strip()
        git(repo, "update-index", "--add", "--cacheinfo", f"100644,{blob},{rel}", env=env)
    return path


def staged_in(repo, index):
    """``git ls-files --stage`` of the index file ``index`` (read with the setup's clean git)."""
    return git(repo, "ls-files", "--stage", env=dict(clean_env(), GIT_INDEX_FILE=str(index)))


def missing_from_the_index(tree):
    """The entries of the index of ``tree`` (``git ls-files --stage``) whose object the repository does not hold,
    each as ``(path, object)``; read with the setup's clean git."""
    missing = []
    for line in git(tree, "ls-files", "--stage").splitlines():
        meta, _, path = line.partition("\t")
        fields = meta.split()
        if len(fields) < 2:
            continue
        held = subprocess.run([GIT, "-C", str(tree), "cat-file", "-e", fields[1]], env=clean_env(),
                              capture_output=True, timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
        if held.returncode != 0:
            missing.append((path, fields[1]))
    return missing


def names_path(output, path):
    """Whether ``output`` names ``path``, as given or resolved."""
    path = Path(path)
    return any(form in output for form in {str(path), str(path.resolve())})


# --------------------------------------------------------------------------
# the stand-in dev tier and the retrieval-regression check (W1-21's public support)
# --------------------------------------------------------------------------

def build_tiers(base):
    """A dev-tier folder as ``GOV_DEV_TIERS`` names it: W1-21's stand-in fixture repository as the a-dev tier,
    and a dev query set of one question its corpus answers (W1-21's ``test_w1_21_check_project.py``)."""
    import w1_21_support as w121
    tiers = Path(base) / "tiers"
    w121.build_fixture(tiers / w121.TIERS["A"])
    queries = [{"programme": "A", "class": "lookup", "query": "Who reads the tide tables at dawn?",
                "gold": {"must_cite": [w121.TIDES], "must_not_cite": []}}]
    write(tiers, "dev-queryset.yaml", yaml.safe_dump({"queries": queries}, sort_keys=False))
    return tiers


def retrieval_check_command():
    """The command the retrieval-regression check's declaration names (DEC-285: run by ``sh -c`` in the root)."""
    if not RETRIEVAL_CHECK.is_file():
        raise Absent(f"{RETRIEVAL_CHECK.relative_to(REPO_ROOT)} is absent: the check is not declared")
    return str(yaml.safe_load(RETRIEVAL_CHECK.read_text(encoding="utf-8"))["command"])


def measured(output):
    """Whether the retrieval check's output says it measured (W1-21: not "unmeasured", a hit@5 line)."""
    text = output.lower()
    return "unmeasured" not in text and "hit@5" in text and "traceback" not in text


def declare_check(root, check_id, family, tier, command, severity="hard-block"):
    write(root, f"{CHECKS_REL}/{check_id}.yaml", yaml.safe_dump(
        {"id": check_id, "family": family, "tier": tier, "severity": severity, "command": command},
        sort_keys=False))


def gov_project(root, hooks_file=None, retrieval=True):
    """A project the hook commands can run in: the template's gitleaks rules, the retrieval-regression check's
    declaration (one named file) as its G1 check and a G2 check that passes, and ``hooks_file`` as its
    ``lefthook.yml`` when given. Committed on ``main``."""
    files = {
        "README.md": "# A project\n",
        ".gitignore": ".gov-runtime/\n__pycache__/\n",
        ".gitleaks.toml": GITLEAKS_RULES.read_text(encoding="utf-8"),
        "notes.md": "the first line\n",
    }
    if hooks_file is not None:
        files["lefthook.yml"] = Path(hooks_file).read_text(encoding="utf-8")
    root = new_repo(root, files)
    if retrieval:
        write(root, f"{CHECKS_REL}/{RETRIEVAL_CHECK.name}", RETRIEVAL_CHECK.read_text(encoding="utf-8"))
    declare_check(root, "w2-05-g2", "graph integrity", "G2", "true")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "the project's checks")
    return root


# --------------------------------------------------------------------------
# a plain pre-commit hook (the hook environment git gives), for the cases that are not about lefthook
# --------------------------------------------------------------------------

def plain_hook(repo, marks, command, refuse=False, result=False):
    """A pre-commit hook in the repository's common hooks folder that runs ``command`` by ``sh -c`` in the
    working tree's root with the environment git gives a hook, leaves its output and exit code in ``marks``,
    and lets the commit through (or refuses it with ``refuse``; with ``result`` the command's exit code decides).

    A hook started again from inside its own run (the check's own ``git commit`` reached this repository and
    ran its hooks) leaves a line in ``marks/nested`` and refuses at once, so that the case ends instead of
    recursing (README, "The nested hook")."""
    hooks = common_dir_of(repo) / "hooks"
    hooks.mkdir(exist_ok=True)
    out, code = Path(marks) / "hook.out", Path(marks) / "hook.exit"
    script = (
        "#!/bin/sh\n"
        f"if [ -n \"${NESTED_ENV}\" ]; then echo \"nested in $(pwd)\" >> {sh_quote(str(Path(marks) / 'nested'))}; "
        "exit 1; fi\n"
        f"{NESTED_ENV}=1; export {NESTED_ENV}\n"
        f"sh -c {sh_quote(command)} > {sh_quote(str(out))} 2>&1\n"
        "status=$?\n"
        f"echo $status > {sh_quote(str(code))}\n"
        + ("exit $status\n" if result else f"exit {1 if refuse else 0}\n"))
    (hooks / "pre-commit").write_text(script, encoding="utf-8")
    (hooks / "pre-commit").chmod(0o755)
    return out, code


NESTED_ENV = "W2_05_IN_THE_HOOK"


def nested_runs(marks):
    """The runs of the hook that started from inside its own run."""
    path = Path(marks) / "nested"
    return path.read_text(encoding="utf-8").splitlines() if path.is_file() else []


def sh_quote(text):
    return "'" + str(text).replace("'", "'\\''") + "'"


def hook_result(marks):
    out, code = Path(marks) / "hook.out", Path(marks) / "hook.exit"
    if not code.is_file():
        return None, ""
    return int(code.read_text().strip() or "-1"), out.read_text(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------
# planted git configuration and trace variables
# --------------------------------------------------------------------------

def trace_plants(folder):
    """``GIT_TRACE``-style variables, each naming a file of its own under ``folder``; git writes to it when the
    variable reaches it."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    return {name: str(folder / name.lower()) for name in TRACE_VARIABLES}


def written_traces(folder):
    """The trace files under ``folder`` that a git process wrote to."""
    folder = Path(folder)
    return sorted(path.name for path in folder.glob("*") if path.is_file() and path.stat().st_size > 0) \
        if folder.is_dir() else []


# --------------------------------------------------------------------------
# the code index's tool, as a recording stand-in
# --------------------------------------------------------------------------

def code_index_project(root):
    """A project ``gov rebuild`` builds a code index for: a full path map (W1-16's public support, one
    namespace ``**``), the template's gitleaks rules, one source file. Committed on ``main``."""
    import w1_16_support as w116
    return new_repo(root, {
        "README.md": "# A project\n",
        ".gitignore": ".gov-runtime/\n__pycache__/\n",
        ".gitleaks.toml": GITLEAKS_RULES.read_text(encoding="utf-8"),
        w116.PATH_MAP_REL: w116.path_map_text(w116.EVERYTHING),
        "src/app.py": "def hello():\n    return 1\n\n\ndef caller():\n    return hello()\n",
    })


def recording_stand_in(folder, name, record):
    """A program ``name`` in ``folder`` that records each start (its arguments, its folder and the environment it
    was started with) as one JSON file in ``record``, prints nothing and exits 0. ``folder`` goes first on
    ``PATH``."""
    folder, record = Path(folder), Path(record)
    folder.mkdir(parents=True, exist_ok=True)
    record.mkdir(parents=True, exist_ok=True)
    program = folder / name
    program.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys, uuid\n"
        f"with open(os.path.join({str(record)!r}, uuid.uuid4().hex + '.json'), 'w', encoding='utf-8') as out:\n"
        "    json.dump({'argv': sys.argv, 'cwd': os.getcwd(), 'env': dict(os.environ)}, out)\n", encoding="utf-8")
    program.chmod(0o755)
    return folder


def recorded_starts(record):
    record = Path(record)
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(record.glob("*.json"))] \
        if record.is_dir() else []


# --------------------------------------------------------------------------
# the sweep record
# --------------------------------------------------------------------------

_GIT_LITERAL = re.compile(r"""(?<![\w.\-/])["']git["']""")


def files_that_start_git():
    """Every file of the Gov OS source (``src/gov/**/*.py``) that names ``git`` as a program: a string literal
    that is exactly ``git``. A lower bound of the files whose calls the sweep lists (README)."""
    found = []
    for path in sorted((SRC / "gov").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if _GIT_LITERAL.search(path.read_text(encoding="utf-8", errors="replace")):
            found.append(path.relative_to(REPO_ROOT).as_posix())
    return found


def files_naming_program(name, under):
    """Every file of the source under ``under`` (``src/gov/...``) that names the program ``name``: a string
    literal that is exactly ``name``. A lower bound of the files that start it, as for git."""
    literal = re.compile(r"""(?<![\w.\-/])["']""" + re.escape(name) + r"""["']""")
    found = []
    for path in sorted((REPO_ROOT / under).rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if literal.search(path.read_text(encoding="utf-8", errors="replace")):
            found.append(path.relative_to(REPO_ROOT).as_posix())
    return found


def table_rows(text):
    """The body rows of every Markdown table of ``text`` (each as its line), header separators left out."""
    separator = re.compile(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?")
    return [line for line in text.splitlines()
            if line.strip().startswith("|") and not separator.fullmatch(line.strip())]


def names_file(text, rel):
    """Whether the sweep names ``rel`` (``src/gov/a/b.py``) as a path, as ``gov/a/b.py`` or as ``gov.a.b``."""
    short = rel[len("src/"):] if rel.startswith("src/") else rel
    dotted = short[:-3].replace("/", ".") if short.endswith(".py") else short
    if dotted.endswith(".__init__"):
        dotted = dotted[: -len(".__init__")]
    for form in (rel, short):
        if form in text:
            return True
    return re.search(r"(?<![\w.])" + re.escape(dotted) + r"(?![\w])", text) is not None


def table_headers(text):
    """The header cells of every Markdown table of ``text``, lower case."""
    lines = text.splitlines()
    headers = []
    for index, line in enumerate(lines[:-1]):
        below = lines[index + 1].strip()
        if line.strip().startswith("|") and re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?", below):
            headers.append([cell.strip().lower() for cell in line.strip().strip("|").split("|")])
    return headers


# --------------------------------------------------------------------------
# a Claude Code settings file, as a stand-in
# --------------------------------------------------------------------------

def stand_in_settings():
    """A ``.claude/settings.json`` in the shape of a Claude Code settings file with hooks, written the way a
    generator writes it: two-space JSON, a final newline, and keys in the generator's own order, which is not
    alphabetical (the events, each entry's ``matcher`` before ``hooks``, each hook's ``type``, ``command``,
    ``timeout``)."""
    def entry(command, matcher=None):
        hook = {"type": "command", "command": f"python3 \"$CLAUDE_PROJECT_DIR\"/governance/kernel/hooks/{command}",
                "timeout": 60}
        return ({"matcher": matcher} if matcher else {}) | {"hooks": [hook]}
    settings = {
        "permissions": {
            "deny": ["Read(./secrets/**)", "Edit(./.gov-runtime/**)", "Bash(git push --force:*)"],
            "allow": ["Bash(gov status:*)"],
        },
        "hooks": {
            "SessionStart": [entry("sessionstart.py")],
            "PreToolUse": [entry("pretooluse.py", "*")],
            "PostToolUse": [entry("posttooluse.py", "Bash")],
            "PostToolUseFailure": [entry("posttooluse.py", "Bash")],
            "PreCompact": [entry("precompact.py")],
            "Stop": [entry("stop.py")],
            "SubagentStop": [entry("subagentstop.py")],
        },
        "env": {"GOV_GUARD": "on", "DISABLE_TELEMETRY": "1"},
    }
    return json.dumps(settings, indent=2, ensure_ascii=False) + "\n"
