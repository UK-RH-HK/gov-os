"""W2-172's planted world: the sets root, the repository, the store link, the runs folder and the planted programs.

Built on W2-171's world (imported, never changed): the repository of three commits, the set of 40, the control set, the
pool, the pinned fake ``gov``, the fake ``claude``. Added here: the three approved briefs in the repository (their bytes at
the audit commit differ from the working tree's, so ``git show <C>`` is what the driver hashes), the writer's delivery
folder, the planted launch script, gate, interpreter shim, ``crontab`` and file-access spy, the runs folder
(``GOV_INDEP_RUNS_DIR``) and the integration store's link (a git worktree of the planted repository, detached at the audit
commit, holding a planted ``.gov-runtime/store.db``).

Everything is under pytest's ``tmp_path``. The driver (``python3 -m gov.memaudit run|due|baseline|status``) and the cron
wrapper are only ever run as child processes, with this tree's ``src/`` first on ``PYTHONPATH`` (``W172_SRC`` may name
another tree's ``src/``: used to show the suite sound against a prototype outside the repository, unset otherwise).

**Path hygiene (S1, F1):** a path that can appear on a printed command line holds none of ``fixtures/``, ``runs/``,
``indep-walls/`` or ``hidden`` (the last is ``say``'s own refusal word). The planted runs folder is ``launch-log``.
The rule judges the paths this world builds (``conftest.clean_paths``), never where the repository itself or the
interpreter lives: a clone under ``gov-os-runs/`` is legal. A grep over printed lines or child argv (``forbidden_in_text``,
``forbidden_in_argv``) lets the exact ``sys.executable`` token pass and nothing else.
Rewrite-Reason: the merge queue's clone path (21:19 ejection)
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import shlex
import shutil
import site
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ACCEPT = HERE.parent
sys.path.insert(0, str(ACCEPT / "W2-171"))  # W2-171's helpers: imported, never changed

import w2_171_scenario as S171  # noqa: E402
import w2_171_world as W171  # noqa: E402

TREE = HERE.parents[2]
SRC = Path(os.environ.get("W172_SRC") or (TREE / "src")).resolve()
WRAPPER = Path(os.environ.get("W172_WRAPPER") or (TREE / "governance" / "project" / "orchestration" / "tools"
                                                   / "memaudit_cron.sh"))  # the env names: only to show the suite sound
UTC = timezone.utc
NOW = "2026-11-10T12:00:00Z"           # 12 hours after the audit commit's committer time
AUDIT_TIME = datetime(2026, 11, 10, tzinfo=UTC)
AUDIT = "memory-audit-20261110"
BRIEF_DIR = "governance/project/indep-briefs/memory-audit"
BRIEFS = ("writer", "checker", "auditor")
STEPS = ["writer-1", "preflight", "checker-1", "writer-2", "checker-2", "void", "measure", "judge", "auditor",
         "classes", "pool", "figures"]
GLOBS = ["src/gov/retrieval/**", "src/gov/retrieve/**", "src/gov/store/**", "src/gov/codeintel/**",
         "governance/project/retrieval.yaml", "governance/project/path-map.yaml"]
FORBIDDEN = ("fixtures/", "runs/", "indep-walls/", "hidden")


def forbidden_in_text(text: str) -> list[str]:
    """The sets-root words (``FORBIDDEN``) held by printed ``text``, the interpreter's own token aside.

    Rewrite-Reason: the merge queue's clone path (21:19 ejection). Item 2 of the ticket's Interface fixes the first word
    of a step line as ``<py>`` (``sys.executable``), and where that interpreter lives is not the test's to choose (a
    venv or a clone under ``gov-os-runs/`` holds ``runs/``). So exactly that token is removed before the grep: a
    whitespace-delimited token equal to ``sys.executable`` (bare or ``shlex.quote``d), nothing looser; a word in any
    other token, or in a path that merely begins with the interpreter's path, still counts.
    """
    for spelling in {sys.executable, shlex.quote(sys.executable)}:
        text = re.sub(r"(?<!\S)" + re.escape(spelling) + r"(?!\S)", " ", text)
    return [w for w in FORBIDDEN if w in text]


def forbidden_in_argv(argv: list[str]) -> list[str]:
    """The ``FORBIDDEN`` words held by a child's argv, an element equal to ``sys.executable`` aside (its first element).

    Rewrite-Reason: the merge queue's clone path (21:19 ejection). Whole-element comparison, as ``forbidden_in_text``.
    """
    return [w for arg in argv if arg != sys.executable for w in FORBIDDEN if w in arg]


CLASSES = ("gold_wrong", "question_ambiguous", "out_of_scope", "retrieval_miss", "answer_wrong")
STDERR_WORD = "stubstderrmarker"


def parse_iso(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)


def iso(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def audit_name(now: str) -> str:
    return "memory-audit-" + parse_iso(now).strftime("%Y%m%d")


def brief_text(name: str, version: int) -> str:
    return f"# The {name} brief, version {version}\n\nPlanted text of version {version} of the {name} brief.\n"


def sha(data: bytes) -> str:
    return W171.sha_bytes(data)


# -- the template -----------------------------------------------------------------------------------------------------
def build_template(base: Path) -> None:
    original = W171.repo_files

    def with_briefs():
        files = original()
        for name in BRIEFS:
            files[f"{BRIEF_DIR}/{name}.md"] = brief_text(name, 1)
        return files

    W171.repo_files = with_briefs
    try:
        W171.build(base)
    finally:
        W171.repo_files = original
    repo, home = base / "repo", base / "home"
    for name in BRIEFS:  # the working tree's briefs differ from those at the audit commit
        W171._write(repo, f"{BRIEF_DIR}/{name}.md", brief_text(name, 2))
    W171.git(repo, "add", "-A", home=home)
    W171.git(repo, "commit", "-q", "-m", "briefs edited after the audit", home=home, date="2026-11-11T01:00:00+00:00")
    w = W171.World(base)
    w.write_set(W171.clean_specs())
    shutil.move(str(w.set_dir), str(base / "delivery"))  # the writer's product, copied in by the planted launch script
    shutil.rmtree(base / "launch-log", ignore_errors=False)
    (base / "launch-log" / "indep").mkdir(parents=True)  # the planted runs folder (GOV_INDEP_RUNS_DIR)
    meta = json.loads((base / "world.json").read_text())
    (base / "launch-log" / "indep" / "AUDITS.log").write_text(json.dumps(
        {"time": "2026-11-02T00:00:00Z", "commit": meta["base_commit"], "run": "auditor-1",
         "audit": W171.EARLIER}) + "\n", encoding="utf-8")
    for source, dest in (("launch_stub.py", "bin/launch_stub.py"), ("gate_stub.py", "bin/gate_stub.py"),
                         ("fake_crontab.py", "fakebin/crontab")):
        W171.install_script(HERE / source, base / dest)
    shim = (HERE / "py_shim.py").read_text().replace("@REAL@", sys.executable)
    (base / "bin" / "py_shim").write_text(f"#!{sys.executable} -S\n" + shim)
    (base / "bin" / "py_shim").chmod(0o755)
    shutil.copytree(HERE / "spy", base / "spy")


# -- the driver's side: what both the full world and the light git worlds share ------------------------------------------
class Driver:
    """Runs ``python3 -m gov.memaudit`` and the cron wrapper as child processes and reads what they leave.

    The host class sets: ``base home work state sets repo link runs mem audits_log spy_dir now audit_commit``."""

    def plant_plan(self, name: str, doc: dict) -> None:
        self.state.mkdir(exist_ok=True)
        (self.state / name).write_text(json.dumps(doc), encoding="utf-8")

    def plan_launch(self, steps: dict) -> None:
        """``plan_launch({"writer-1": [{"exit": 10}]})``."""
        self.plant_plan("launch_plan.json", steps)

    def plan_gate(self, *codes: int) -> None:
        self.plant_plan("gate_plan.json", {"codes": list(codes)})

    def plant_starts(self, *lines: dict) -> None:
        self.mem.mkdir(parents=True, exist_ok=True)
        (self.mem / "STARTS.log").write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")

    def plant_history(self, *lines: dict) -> None:
        self.mem.mkdir(parents=True, exist_ok=True)
        (self.mem / "HISTORY.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")

    def plant_audits(self, *lines: dict) -> None:
        self.audits_log.parent.mkdir(parents=True, exist_ok=True)
        self.audits_log.write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")

    def start_line(self, at: str, *, audit: str = "memory-audit-20261101", commit: str | None = None,
                   force: bool = False) -> dict:
        return {"audit": audit, "commit": commit or self.audit_commit, "at": at, "force": force}

    # -- running
    def child_env(self, *, now="default", extra: dict | None = None, spy: bool = True, path: bool = True) -> dict:
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_", "W171_", "W172_"))}
        rest = [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p and Path(p).resolve() != SRC]
        env.update(HOME=str(self.home), GIT_CONFIG_NOSYSTEM="1", PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=os.pathsep.join([str(SRC), *([str(self.spy_dir)] if spy else []), *rest]),
                   GOV_INDEP_RUNS_DIR=str(self.runs), W171_STATE=str(self.state), W172_STATE=str(self.state))
        env.setdefault("PYTHONUSERBASE", site.getuserbase())
        if path:
            env["PATH"] = f"{self.base / 'fakebin'}{os.pathsep}{os.environ.get('PATH', '')}"
        if spy:
            env.update(W172_SPY=str(self.state / "spy.jsonl"), W172_SPY_ROOT=str(self.sets))
        when = self.now if now == "default" else now
        if when:
            env["GOV_MEMAUDIT_NOW"] = when
        env.update(extra or {})
        return env

    def drive(self, *args, now="default", env=None, cwd=None, timeout=900, spy=True) -> W171.Run:
        argv = [sys.executable, "-m", "gov.memaudit", *map(str, args)]
        done = subprocess.run(argv, cwd=str(cwd or self.work), env=self.child_env(now=now, extra=env, spy=spy),
                              capture_output=True, text=True, timeout=timeout)
        return W171.Run(argv, done)

    def popen(self, *args, now="default", env=None, spy=True) -> subprocess.Popen:
        argv = [sys.executable, "-m", "gov.memaudit", *map(str, args)]
        return subprocess.Popen(argv, cwd=str(self.work), env=self.child_env(now=now, extra=env, spy=spy),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def common_flags(self) -> list[str]:
        return ["--sets-root", str(self.sets), "--repo", str(self.repo)]

    def due(self, *, link: bool = True, **kw) -> W171.Run:
        args = ["due", *self.common_flags()]
        if link:
            args += ["--store-link", str(self.link)]
        return self.drive(*args, **kw)

    def baseline(self, commit: str, **kw) -> W171.Run:
        return self.drive("baseline", "--sets-root", str(self.sets), "--repo", str(self.repo), "--commit", commit, **kw)

    def status(self, since: str, **kw) -> W171.Run:
        return self.drive("status", *self.common_flags(), "--since", since, **kw)

    def wrapper(self, *, env: dict | None = None, cwd=None, timeout=300) -> subprocess.CompletedProcess:
        script = WRAPPER
        e = self.child_env(spy=False, extra=env)
        return subprocess.run(["bash", str(script)], cwd=str(cwd or self.repo), env=e, capture_output=True, text=True,
                              timeout=timeout)

    # -- reading
    def jsonl_file(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

    def jsonl(self, name: str) -> list[dict]:
        return self.jsonl_file(self.state / name)

    def stub_calls(self) -> list[dict]:
        return self.jsonl("launch_calls.jsonl")

    def gate_calls(self) -> list[dict]:
        return self.jsonl("gate_calls.jsonl")

    def shim_calls(self) -> list[dict]:
        return self.jsonl("shim_calls.jsonl")

    def spy(self) -> list[dict]:
        return self.jsonl("spy.jsonl")

    def counts(self, audit_dir: Path | None = None) -> dict:
        return json.loads(((audit_dir or self.audit_dir) / "COUNTS.json").read_text(encoding="utf-8"))

    def digest(self, audit_dir: Path | None = None) -> list[str]:
        return ((audit_dir or self.audit_dir) / "DIGEST.txt").read_text(encoding="utf-8").splitlines()

    def history(self) -> list[dict]:
        return self.jsonl_file(self.mem / "HISTORY.jsonl")

    def starts(self) -> list[dict]:
        return self.jsonl_file(self.mem / "STARTS.log")

    def audits(self) -> list[dict]:
        return self.jsonl_file(self.audits_log)

    def crontab_calls(self) -> str:
        path = self.state / "crontab_calls.log"
        return path.read_text() if path.exists() else ""

    def git_out(self, *args: str) -> str:
        done = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True,
                              env=W171.git_env(self.home), timeout=60)
        assert done.returncode == 0, done.stderr
        return done.stdout


class World(Driver, W171.World):
    """One test's copy of the template: ``go`` runs the driver's ``run``, ``wrapper`` the cron wrapper."""

    def __init__(self, base: Path, now: str = NOW):
        super().__init__(base)
        self.runs = self.base / "launch-log"
        self.mem = self.runs / "indep" / "memaudit"
        self.audits_log = self.runs / "indep" / "AUDITS.log"
        self.link = self.base / "link"
        self.delivery = self.base / "delivery"
        self.stub = self.base / "bin" / "launch_stub.py"
        self.gate_stub = self.base / "bin" / "gate_stub.py"
        self.shim = self.base / "bin" / "py_shim"
        self.spy_dir = self.base / "spy"
        self.set_now(now)
        self.write_world_json()

    def set_now(self, now: str | None) -> None:
        self.now = now
        self.audit = audit_name(now) if now else None
        if self.audit:
            self.set_dir = self.sets / "fixtures" / "evaluation" / self.audit
            self.hidden = self.set_dir / "hidden"
            self.run_dir = self.sets / "runs" / self.audit
            self.audit_dir = self.mem / self.audit

    def write_world_json(self) -> None:
        self.state.mkdir(exist_ok=True)
        (self.state / "world.json").write_text(json.dumps(
            {"delivery": str(self.delivery), "audit_commit": self.audit_commit, "sets": str(self.sets)}))

    def docs(self) -> dict:
        """The planted questions as the writer delivers them (the delivery folder's files, read back)."""
        import yaml
        return {p.stem: yaml.safe_load(p.read_text(encoding="utf-8"))
                for p in sorted((self.delivery / "hidden").glob("q*.yaml"))}

    # -- the store link
    def make_link(self, commit: str | None = None, head: str | None = None) -> str:
        """The link: a detached worktree of the planted repository at ``commit`` (default the audit commit), holding
        the planted store (whose fingerprints head is ``head``, default the audit commit). Returns the commit."""
        import sqlite3
        if self.link.exists():
            shutil.rmtree(self.link)
        shutil.rmtree(self.repo / ".git" / "worktrees", ignore_errors=True)  # the only worktree is this link
        W171.git(self.repo, "worktree", "prune", home=self.home)
        commit = commit or self.audit_commit
        W171.git(self.repo, "worktree", "add", "--detach", str(self.link), commit, home=self.home)
        (self.link / ".gov-runtime").mkdir(exist_ok=True)
        shutil.copy(self.store, self.link / ".gov-runtime" / "store.db")
        if head is not None:
            con = sqlite3.connect(self.link / ".gov-runtime" / "store.db")
            con.execute("UPDATE fingerprints SET head = ?", (head,))
            con.commit()
            con.close()
        return commit

    def link_git(self, *args: str, date: str | None = None) -> str:
        return W171.git(self.link, *args, home=self.home, date=date or "2026-11-10T00:00:00+00:00")

    def commit_in_link(self, *, branch: str | None = None, date: str, message: str = "side") -> str:
        """A new empty commit in the link (on a new branch ``branch``, else detached), dated ``date``."""
        if branch:
            self.link_git("checkout", "-q", "-b", branch)
        self.link_git("commit", "-q", "--allow-empty", "-m", message, date=date)
        return self.link_git("rev-parse", "HEAD").strip()

    def repo_git(self, *args: str, date: str = "2026-11-01T00:00:00+00:00") -> str:
        return W171.git(self.repo, *args, home=self.home, date=date)

    # -- running
    def run_args(self, *, gate: str | None = None, force: bool = False, extra=()) -> list[str]:
        args = ["run", *self.common_flags(), "--store-link", str(self.link), "--launch", str(self.stub),
                "--gov", str(self.gov), "--claude", str(self.claude)]
        if gate:
            args += ["--gate-cmd", str(gate)]
        if force:
            args.append("--force")
        return [*args, *extra]

    def go(self, *, gate=None, force=False, extra=(), **kw) -> W171.Run:
        """``python3 -m gov.memaudit run`` with the planted seams."""
        return self.drive(*self.run_args(gate=gate, force=force, extra=extra), **kw)

    def figures(self) -> dict:
        return json.loads((self.run_dir / "FIGURES.json").read_text(encoding="utf-8"))

    def guarded_files(self) -> dict:
        """The path map, the guard, ``.claude/`` and the walls' template of the repository: the bytes' sha256."""
        found = {}
        for rel in ("governance/project/path-map.yaml", ".claude/settings.json", ".claude/hooks/pretooluse.py",
                    "governance/project/indep-walls/tree-exclude.txt", "governance/project/retrieval.yaml"):
            found[rel] = sha((self.repo / rel).read_bytes())
        return found


# -- what a STEP line says ------------------------------------------------------------------------------------------
def step_lines(run: W171.Run) -> list[tuple[str, str]]:
    """``(name, command line)`` of each ``STEP <name> <command line>`` printed, in order."""
    found = []
    for line in run.out.splitlines():
        m = re.fullmatch(r"STEP (\S+) (.*)", line)
        if m:
            found.append((m[1], m[2]))
    return found


def step_names(run: W171.Run) -> list[str]:
    return [name for name, _ in step_lines(run)]


def flag_map(tokens: list[str]) -> dict:
    """The ``--flag value`` pairs of a command line (a flag with no value maps to True)."""
    out, i = {}, 0
    while i < len(tokens):
        t = tokens[i]
        if t.startswith("--"):
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                out[t], i = tokens[i + 1], i + 2
                continue
            out[t] = True
        i += 1
    return out


@contextmanager
def held_flock(path: Path):
    """The test holds an exclusive ``flock`` on ``path`` (made when absent) while the block runs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def flock_free(path: Path) -> bool:
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False
    finally:
        os.close(fd)


def tree_names(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in Path(root).rglob("*")}
