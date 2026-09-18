"""P2-AR-0009 (beta re-audit) probe helper. Independent evidence harness, NOT a product test.

Drives the release binary exactly the way the product's certification harness does
(`gov --json --root R --session S --role ROLE <args>`, GOV_CANONICAL_ROOT = the candidate checkout,
XDG_STATE_HOME = a per-project simulated machine), so every probe exercises the shipped CLI.

Environment:
  GOV_WT      candidate checkout (default: four levels above this file's evidence dir)
  PROBE_TMP   base for disposable projects (default: a fresh tempfile.mkdtemp())
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
WT = Path(os.environ.get("GOV_WT", HERE.parents[6])).resolve()
GOV = WT / "target" / "release" / "gov"
BASE = Path(os.environ.get("PROBE_TMP") or tempfile.mkdtemp(prefix="p2ar0009-"))
BASE.mkdir(parents=True, exist_ok=True)

_OUT: list[str] = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    _OUT.append(s)
    sys.stdout.flush()


def machine_home(root: Path) -> Path:
    key = hashlib.sha256(str(root).encode()).hexdigest()[:16]
    return BASE / "machines" / key


class Gov:
    def __init__(self, root: Path, session: str = "S-probe", role: str = "orchestrator", env: dict | None = None):
        self.root = Path(root)
        self.session = session
        self.role = role
        self.env = env or {}

    def as_role(self, role: str) -> "Gov":
        return Gov(self.root, self.session, role, dict(self.env))

    def as_session(self, s: str) -> "Gov":
        return Gov(self.root, s, self.role, dict(self.env))

    def run(self, *args: str, show: bool = True, check: bool = False) -> dict:
        cmd = [str(GOV), "--json", "--root", str(self.root), "--session", self.session, "--role", self.role, *args]
        env = dict(os.environ)
        env.pop("GOV_SESSION", None)
        env.pop("GOV_ROLE", None)
        env["GOV_CANONICAL_ROOT"] = str(WT)
        env["XDG_STATE_HOME"] = str(machine_home(self.root))
        env["PYTHONDONTWRITEBYTECODE"] = "1"   # auditor plugins must not leave .pyc files in the governed tree
        env.update(self.env)
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        try:
            envl = json.loads(p.stdout.strip())
        except Exception:
            envl = {"ok": False, "error": {"code": "NO_JSON", "message": p.stderr[-2000:], "stdout": p.stdout[-2000:]}}
        envl["_exit"] = p.returncode
        if show:
            shown = " ".join(a if " " not in a else repr(a) for a in args)
            log(f"$ gov --role {self.role} {shown}  -> exit {p.returncode} ok={envl.get('ok')}"
                + ("" if envl.get("ok") else f" error={json.dumps(envl.get('error', {}))[:600]}"))
        if check and not envl.get("ok"):
            raise SystemExit(f"required command failed: gov {' '.join(args)}: {envl.get('error')}")
        return envl

    def ok(self, *args: str, show: bool = True) -> dict:
        return self.run(*args, show=show, check=True).get("result")


def git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return p.stdout.strip()


def git_init_commit(root: Path, msg: str = "baseline"):
    git(root, "init", "-q")
    git(root, "config", "user.email", "probe@example.invalid")
    git(root, "config", "user.name", "probe")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)


def commit_all(root: Path, msg: str):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)


def new_project(name: str, fixture: str | None = None, files: dict | None = None) -> Path:
    root = BASE / name
    if root.exists():
        shutil.rmtree(root)
    if fixture:
        shutil.copytree(WT / "fixtures" / fixture / "project", root)
    else:
        root.mkdir(parents=True)
    for rel, text in (files or {}).items():
        write(root, rel, text)
    git_init_commit(root)
    return root


def write(root: Path, rel: str, text: str):
    f = Path(root) / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)


def init(root: Path, g: Gov, name="probe", alias="probe", intent="probe project") -> dict:
    return g.ok("init", "--name", name, "--alias", alias, "--intent", intent)


def db(root: Path) -> sqlite3.Connection:
    return sqlite3.connect(str(Path(root) / ".governance-runtime" / "state.db"))


def q(root: Path, sql: str, params=()):
    c = db(root)
    try:
        return c.execute(sql, params).fetchall()
    finally:
        c.close()


def jdump(v, limit: int = 4000) -> str:
    s = json.dumps(v, indent=1, sort_keys=True, default=str)
    return s if len(s) <= limit else s[:limit] + f"... <{len(s) - limit} more chars>"


RESULTS: list[tuple[str, bool, str]] = []


def check(bullet_id: str, cond: bool, what: str):
    RESULTS.append((bullet_id, bool(cond), what))
    log(f"[{'PASS' if cond else 'FAIL'}] {bullet_id}: {what}")


def summary():
    log("")
    log("=== SUMMARY ===")
    for b, okv, w in RESULTS:
        log(f"{'PASS' if okv else 'FAIL'}  {b}  {w}")
    log(f"probe tmp base: {BASE}")


# ---------------------------------------------------------------------------------------------- plugins & overrides
PLUGINS = HERE.parent / "plugins"


def install_plugin(root: Path, plugin_file: str, plugin_id: str, capability: str, version: str = "1", extra: dict | None = None):
    """Copy an auditor-authored plugin into the project and hand-declare it (governance/project/plugins/<id>.yaml)."""
    import yaml
    dst = Path(root) / "tools" / "probe-plugins" / plugin_file
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(PLUGINS / plugin_file, dst)
    dst.chmod(0o755)
    desc = {"plugin_id": plugin_id, "capability": capability, "version": version,
            "command": ["python3", f"tools/probe-plugins/{plugin_file}"], "languages": []}
    desc.update(extra or {})
    write(root, f"governance/project/plugins/{plugin_id}.yaml", yaml.safe_dump(desc, sort_keys=False))
    return desc


def set_overrides(root: Path, over: dict, merge: bool = True):
    import yaml
    p = Path(root) / "governance/project/PROJECT_POLICY.yaml"
    pp = yaml.safe_load(p.read_text())
    cur = pp.get("policy_overrides") or {}
    if merge:
        cur.update(over)
    else:
        cur = dict(over)
    pp["policy_overrides"] = cur
    p.write_text(yaml.safe_dump(pp, sort_keys=False))


def section(t):
    log("")
    log("=" * 100)
    log(t)
    log("=" * 100)


def body_of(env: dict) -> dict:
    return env.get("result") or (env.get("error") or {}).get("details") or {}
