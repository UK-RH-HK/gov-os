"""Helpers of S12 and F7 only (the weekly secret scan and push; Interface I13): they move with S12 if it is split off.

Planted under pytest's ``tmp_path``: a small repository with a bare remote (the remote holds the first commit of ``main``, the
repository its second), a fake ``gitleaks`` (a script that logs its argv, writes a planted JSON report to ``--report-path`` and
exits with a planted code; it never runs the real one; with ``land`` in its plan it commits, while it runs, a file holding the
planted key on the repository's branch and writes the new commit to ``landed.txt``: review round 1's F-B), and the runs folder
whose ``indep/memaudit/<key>/`` is the key folder.
``python3 -m gov.memaudit push`` runs in a child process with this tree's ``src/`` first on ``PYTHONPATH``.
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import site
import subprocess
import sys
from pathlib import Path

import w2_187_world as W
from w2_187_world import W171, W172

SECRET = "AKIAqz9planted4secret7vk2x"             # the planted finding: it must appear in no line, log, digest or file
NOISE = "FAKEGL-NOISE-77"                         # what the fake prints on its own stdout and stderr
HOOK = "HOOKWORD-pre-receive-88"                  # what the remote's pre-receive hook prints
WEEK_DIGEST = ["STANDING memory-standing-20261101 week 2026-W46 commit 0123456789ab", "P1 none", "REPAIR none"]
OLD_DIGEST = ["STANDING memory-standing-20261101 week 2026-W45 commit 0123456789ab", "P1 none"]
CRON_KEYS = {"at", "due", "mode", "reason", "started", "exit"}
GITLEAKS_ARGV = ("--no-banner", "--redact")

FAKE = '''\
import json, os, sys, time
HERE = os.path.dirname(os.path.realpath(__file__))
plan = json.load(open(os.path.join(HERE, "gitleaks_plan.json")))
argv = sys.argv[1:]
path = argv[argv.index("--report-path") + 1] if "--report-path" in argv and argv.index("--report-path") + 1 < len(argv) else None
rec = {"name": plan.get("name"), "argv": argv, "cwd": os.getcwd()}
if path:
    rec["path"] = path
    rec["pre_exists"] = os.path.exists(path)
    rec["pre_mode"] = (os.stat(path).st_mode & 0o777) if os.path.exists(path) else None
    parent = os.path.dirname(path) or "."
    rec["parent_mode"] = (os.stat(parent).st_mode & 0o777) if os.path.isdir(parent) else None
with open(os.path.join(HERE, "gitleaks_calls.jsonl"), "a") as f:
    f.write(json.dumps(rec) + "\\n")
if plan.get("probe"):
    import subprocess
    seen = subprocess.run(["git", "--git-dir=" + plan["probe"], "rev-parse", "refs/heads/main"], capture_output=True, text=True)
    open(os.path.join(HERE, "seen.txt"), "w").write(seen.stdout)
secret = plan.get("secret", "")
if plan.get("land"):
    import subprocess
    land = plan["land"]
    with open(os.path.join(land["repo"], land["file"]), "w") as f:
        f.write("key=" + secret + "\\n")
    genv = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
                GIT_COMMITTER_EMAIL="t@example.invalid", HOME=land["home"], GIT_CONFIG_NOSYSTEM="1")
    for args in (["add", "-A"], ["commit", "-q", "-m", "landed during the scan"]):
        subprocess.run([land["git"], "-C", land["repo"], *args], env=genv, check=True, capture_output=True)
    done = subprocess.run([land["git"], "-C", land["repo"], "rev-parse", "HEAD"], env=genv, check=True, capture_output=True,
                          text=True)
    open(os.path.join(HERE, "landed.txt"), "w").write(done.stdout.strip())
if plan.get("noise"):
    print(plan["noise"] + " " + secret)
    print(plan["noise"] + " " + secret, file=sys.stderr)
entries = [{"RuleID": "planted-rule", "Description": "planted", "Secret": secret, "Match": "key=" + secret,
            "File": "notes.txt", "StartLine": i + 1} for i in range(plan.get("entries", 0))]
if path and plan.get("write_report", True):
    with open(path, "w") as f:
        f.write(json.dumps(entries))
time.sleep(plan.get("sleep", 0))
sys.exit(plan.get("exit", 0))
'''


class Fake:
    """A planted gitleaks in its own folder: ``exe``, its plan and its call log."""

    def __init__(self, folder: Path, name: str = "gitleaks", label: str = "fake"):
        self.folder, self.label = folder, label
        folder.mkdir(parents=True, exist_ok=True)
        self.exe = folder / name
        self.exe.write_text(f"#!{sys.executable} -S\n" + FAKE, encoding="utf-8")
        self.exe.chmod(0o755)
        self.plan(entries=0, exit=0)

    def plan(self, **kw) -> None:
        doc = {"name": self.label, "secret": SECRET, "noise": NOISE, **kw}
        (self.folder / "gitleaks_plan.json").write_text(json.dumps(doc), encoding="utf-8")

    def calls(self) -> list[dict]:
        path = self.folder / "gitleaks_calls.jsonl"
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []


def git_env(home: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_", "W171_", "W172_"))}
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    return env


def git(cwd: Path, home: Path, *args: str, check: bool = True) -> str:
    done = subprocess.run(["git", *args], cwd=str(cwd), env=git_env(home), capture_output=True, text=True, timeout=60)
    assert not check or done.returncode == 0, (args, done.stderr)
    return done.stdout.strip()


def make_remote(path: Path, home: Path) -> Path:
    path.mkdir(parents=True)
    git(path, home, "init", "-q", "--bare")
    return path


def remote_head(remote: Path, home: Path, branch: str = "main") -> str | None:
    out = git(remote, home, "rev-parse", "-q", "--verify", f"refs/heads/{branch}", check=False)
    return out or None


def reject_pushes(remote: Path) -> None:
    hook = remote / "hooks" / "pre-receive"
    hook.parent.mkdir(exist_ok=True)
    hook.write_text(f"#!/bin/sh\necho {HOOK} >&2\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)


def secret_hits(*roots: Path) -> list[str]:
    """Every file under the roots that holds the planted secret."""
    found = []
    for root in roots:
        for path in sorted(Path(root).rglob("*")) if Path(root).exists() else []:
            if path.is_file() and SECRET.encode() in path.read_bytes():
                found.append(str(path))
    return found


class PushWorld:
    """A repository (two commits on ``main``), a bare remote at its first, a sets root, a runs folder, a key folder."""

    def __init__(self, base: Path):
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True)
        self.repo = base / "repo-p"
        self.remote = base / "remote.git"
        self.sets = base / "sets"
        self.runs = base / "runs"
        self.tmp = base / "tmp"
        self.nogl = base / "nogl"                  # a PATH holding git and nothing else
        for folder in (self.sets, self.runs, self.tmp, self.nogl):
            folder.mkdir()
        (self.nogl / "git").symlink_to(shutil.which("git"))
        self.repo.mkdir()
        git(self.repo, self.home, "init", "-q", "-b", "main")
        (self.repo / "notes.txt").write_text("notes one\n", encoding="utf-8")
        git(self.repo, self.home, "add", "-A")
        git(self.repo, self.home, "commit", "-q", "-m", "one")
        self.first = git(self.repo, self.home, "rev-parse", "HEAD")
        make_remote(self.remote, self.home)
        git(self.repo, self.home, "push", "-q", str(self.remote), "main")
        (self.repo / "notes.txt").write_text("notes one\nnotes two\n", encoding="utf-8")
        git(self.repo, self.home, "commit", "-q", "-am", "two")
        self.head = git(self.repo, self.home, "rev-parse", "HEAD")
        self.key = W172.state_key(self.repo)
        self.folder = self.runs / "indep" / "memaudit" / self.key
        self.fake = Fake(base / "gl" / "fake")
        self.plant_digests()
        self.plant_cron_log()

    # -- the key folder
    def plant_digests(self) -> None:
        old = self.folder / "standing" / W.STD / "2026-W45"
        new = self.folder / "standing" / W.STD / "2026-W46"
        for folder, lines, stamp in ((old, OLD_DIGEST, 1_700_000_000), (new, WEEK_DIGEST, 1_700_600_000)):
            folder.mkdir(parents=True)
            (folder / "DIGEST.txt").write_text("".join(x + "\n" for x in lines), encoding="utf-8")
            os.utime(folder / "DIGEST.txt", (stamp, stamp))

    def plant_cron_log(self) -> None:
        line = {"at": "2026-11-16T21:00:00Z", "due": True, "mode": "weekly", "reason": "start", "started": True, "exit": 0}
        (self.folder / "cron.log").write_text(json.dumps(line) + "\n", encoding="utf-8")

    def digest_lines(self, week: str = "2026-W46") -> list[str]:
        return (self.folder / "standing" / W.STD / week / "DIGEST.txt").read_text(encoding="utf-8").splitlines()

    def cron_lines(self) -> list[dict]:
        path = self.folder / "cron.log"
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

    def key_files(self) -> set[str]:
        return {str(p) for p in self.folder.rglob("*") if p.is_file()}

    # -- running
    def declare(self, remote: Path | str | None = None, branch: str = "main") -> str:
        return f"{remote or self.remote} {branch}"

    def env(self, *, push: str | None = None, extra: dict | None = None, path: Path | str | None = None) -> dict:
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_", "W171_", "W172_"))}
        rest = [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p and Path(p).resolve() != W.SRC]
        env.update(HOME=str(self.home), GIT_CONFIG_NOSYSTEM="1", PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(self.tmp),
                   PYTHONPATH=os.pathsep.join([str(W.SRC), *rest]), GOV_INDEP_RUNS_DIR=str(self.runs),
                   GOV_MEMAUDIT_NOW="2026-11-16T21:00:00Z", PATH=str(path or self.nogl),
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@example.invalid")
        env.setdefault("PYTHONUSERBASE", site.getuserbase())
        if push is not None:
            env["GOV_MEMAUDIT_PUSH"] = push
        env.update(extra or {})
        return env

    def push(self, *, declared: str | None = None, gitleaks: Path | str | None = "env", flag: Path | str | None = None,
             extra: dict | None = None, path: Path | str | None = None, timeout: int = 180) -> W171.Run:
        """``python3 -m gov.memaudit push --sets-root R --repo D``. ``gitleaks="env"`` names the fake by
        ``$GOV_MEMAUDIT_GITLEAKS``; ``flag`` names one by ``--gitleaks``; ``None`` names none."""
        env = dict(extra or {})
        if gitleaks == "env":
            env["GOV_MEMAUDIT_GITLEAKS"] = str(self.fake.exe)
        elif gitleaks is not None:
            env["GOV_MEMAUDIT_GITLEAKS"] = str(gitleaks)
        argv = [sys.executable, "-m", "gov.memaudit", "push", "--sets-root", str(self.sets), "--repo", str(self.repo)]
        if flag is not None:
            argv += ["--gitleaks", str(flag)]
        done = subprocess.run(argv, cwd=str(self.base), env=self.env(push=declared, extra=env, path=path),
                              capture_output=True, text=True, timeout=timeout)
        return W171.Run(argv, done)

    def remote_head(self) -> str | None:
        return remote_head(self.remote, self.home)


def check_scan_argv(call: dict, repo: Path) -> None:
    """I13's scan: ``detect --source <repo> --no-banner --redact --report-format json --report-path <p>``."""
    argv = call["argv"]
    assert argv[0] == "detect", argv
    assert argv[argv.index("--source") + 1] in (str(repo), os.path.realpath(repo)), argv
    assert all(flag in argv for flag in GITLEAKS_ARGV), argv
    assert argv[argv.index("--report-format") + 1] == "json", argv
    assert "--report-path" in argv, argv


def check_report_path(call: dict, repo: Path) -> None:
    """The report lies outside the repository; a file already there is mode 0600, else its folder is mode 0700."""
    path = os.path.realpath(call["path"])
    assert not (path + os.sep).startswith(os.path.realpath(repo) + os.sep), f"the report is inside the repository: {path}"
    assert os.path.realpath(repo) not in path
    if call["pre_exists"]:
        assert call["pre_mode"] == 0o600, oct(call["pre_mode"])
    else:
        assert call["parent_mode"] == 0o700, call


def no_stray_files(root: Path) -> list[str]:
    return [str(p) for p in Path(root).rglob("*") if p.is_file()]


# -- the wrapper's shim: W2-187's interpreter shim that also answers ``push`` -----------------------------------------------------
def install_push_shim(world) -> Path:
    """``py_shim187.py`` with ``push`` among the keys it answers (the other cases keep their own shim, which sends ``push`` to
    the real interpreter)."""
    source = (W.HERE / "py_shim187.py").read_text(encoding="utf-8")
    patched = source.replace('("maintain", "run")', '("maintain", "run", "push")')
    assert patched != source, "py_shim187.py no longer has the key list this helper patches"
    dest = world.base / "bin" / "py_shim_push"
    dest.write_text(f"#!{sys.executable} -S\n" + patched.replace("@REAL@", sys.executable), encoding="utf-8")
    dest.chmod(0o755)
    return dest


def run_wrapper(world, shim: Path, *, env: dict | None = None, cwd=None):
    """``memaudit_cron.sh --repo <the world's repository>`` with the planted interpreter."""
    extra = {"GOV_MEMAUDIT_PYTHON": str(shim), "GOV_MEMAUDIT_SETS_ROOT": str(world.sets), **(env or {})}
    return subprocess.run(["bash", str(W.WRAPPER), "--repo", str(world.repo)], cwd=str(cwd or world.repo),
                          env=world.child_env(spy=False, extra=extra), capture_output=True, text=True, timeout=300)


# -- A9's ACT text -----------------------------------------------------------------------------------------------------------------
STEP6_SENTENCE = ('The cycle runs the audit and measure, then one gitleaks scan, then git push only on a clean scan; declare the '
                  'push with GOV_MEMAUDIT_PUSH="<remote> <branch>" on this line; leave it out for no push.')


def squash(text: str) -> str:
    """Markdown code marks dropped and white space collapsed: a wrapped line or a code span is the same sentence."""
    return " ".join(text.replace("`", "").split())


def walls_act_text(world, *extra, out: Path | None = None) -> tuple[str, str]:
    out = out or world.base / "adoption-out"
    sets_root = str(world.base / "never-made-sets")
    env = world.child_env(spy=False, extra={"PYTHONPATH": str(W.SRC)})
    done = subprocess.run([sys.executable, str(W.HERE / "call_walls_act.py"), str(out), sets_root, "memory-audit-20261113", *extra],
                          cwd=str(world.work), env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stderr[-800:]
    return (out / "memory-audit" / "ACT-WALLS" / "ACT.md").read_text(encoding="utf-8"), sets_root


def step6_text(text: str) -> str:
    """Step 6 of ACT.md: its line and the lines after it up to the next numbered step."""
    lines = text.splitlines()
    starts = [i for i, x in enumerate(lines) if x.startswith("6.")]
    assert len(starts) == 1, f"ACT.md has one step 6: {text}"
    rest = []
    for x in lines[starts[0] + 1:]:
        if x[:1].isdigit():
            break
        rest.append(x)
    return " ".join([lines[starts[0]], *rest])


# -- the source scan of F7 -----------------------------------------------------------------------------------------------------------
ALLOWED = ("--gitleaks", "GOV_MEMAUDIT_GITLEAKS")
CALLERS = {"run", "Popen", "call", "check_call", "check_output", "execv", "execve", "execvp", "execvpe", "execl", "execlp",
           "spawnv", "spawnvp", "which", "system", "popen"}


def _strip(text: str) -> str:
    for token in ALLOWED:
        text = text.replace(token, "")
    return text.lower()


def module_calls_gitleaks(path: Path) -> bool:
    """True when the module runs or looks up the program: a call of ``subprocess.*``, ``os.exec*``, ``os.system`` or
    ``shutil.which`` with a string naming it among its arguments, or an argv list holding it. A flag or environment name that
    forwards the choice (``--gitleaks``, ``GOV_MEMAUDIT_GITLEAKS``) and a docstring or a comment are not a call."""
    tree = ast.parse(path.read_text(encoding="utf-8"))

    def names(node) -> bool:
        return any(isinstance(n, ast.Constant) and isinstance(n.value, str) and "gitleaks" in _strip(n.value) for n in ast.walk(node))

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if func in CALLERS and any(names(arg) for arg in [*node.args, *(k.value for k in node.keywords)]):
                return True
        if isinstance(node, (ast.List, ast.Tuple)) and any(
                isinstance(e, ast.Constant) and isinstance(e.value, str) and _strip(e.value).strip() == "gitleaks"
                for e in node.elts):
            return True
    return False


def wrapper_names_gitleaks(path: Path) -> bool:
    """A non-comment line of the shell wrapper that names it (the variable that forwards the choice aside)."""
    for line in path.read_text(encoding="utf-8").splitlines():
        code = line.strip()
        if code.startswith("#"):
            continue
        if "gitleaks" in _strip(code.split(" #")[0]):
            return True
    return False
