"""Held-out probe library for Governance OS Phase-2 verification iteration 1, family epsilon (run P2-AR-0050).

Authored by the verifier from Contract v3 and the product's observable behaviour. Not derived from any builder test
or builder probe. Never enters the product tree.

Every probe drives the built `target/release/gov` against a disposable project created under a scratch root.
"""
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

WT = Path(__file__).resolve().parents[5]           # .../p2-verify1-epsilon
GOV = WT / "target" / "release" / "gov"
SCRATCH = Path(os.environ.get("EPS_SCRATCH", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/"
                              "1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/eps/heldout"))

_RESULTS = []


class Project:
    """A disposable governed project on its own simulated machine."""

    def __init__(self, name, fixture=None, provision_machine=True):
        self.name = name
        self.root = SCRATCH / f"{name}-{uuid.uuid4().hex[:8]}"
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_home = SCRATCH / "machines" / self.root.name
        self.state_home.mkdir(parents=True, exist_ok=True)
        if fixture:
            src = WT / "fixtures" / fixture / "project"
            shutil.copytree(src, self.root, dirs_exist_ok=True)
        self.git("init", "-q", ".")
        self.git("config", "user.email", "eps@example.invalid")
        self.git("config", "user.name", "eps")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "baseline", "--allow-empty")
        self.session = "eps-1"
        self.role = "orchestrator"

    # ---------------------------------------------------------------- plumbing
    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)

    def commit(self, msg="change"):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def env(self, extra=None):
        e = dict(os.environ)
        e["XDG_STATE_HOME"] = str(self.state_home)
        e["GOV_CANONICAL_ROOT"] = str(WT)
        e.pop("GOV_SESSION", None)
        e.pop("GOV_ROLE", None)
        if extra:
            e.update(extra)
        return e

    def run(self, *args, role=None, session=None, env=None, timeout=900):
        cmd = [str(GOV), "--json", "--root", str(self.root),
               "--session", session or self.session, "--role", role or self.role, *args]
        t0 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True, env=self.env(env), timeout=timeout)
        wall = time.time() - t0
        try:
            env_json = json.loads(p.stdout.strip() or "{}")
        except Exception:
            env_json = {"ok": False, "error": {"code": "NO_JSON", "message": p.stdout[-400:] + p.stderr[-400:]}}
        return Out(p.returncode, env_json, p.stdout, p.stderr, wall, cmd)

    def init(self, *extra):
        return self.run("init", *extra)

    # ---------------------------------------------------------------- files
    def write(self, rel, text):
        f = self.root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)

    def read(self, rel):
        return (self.root / rel).read_text()

    def exists(self, rel):
        return (self.root / rel).exists()


class Out:
    def __init__(self, code, envelope, stdout, stderr, wall, cmd):
        self.code, self.envelope, self.stdout, self.stderr, self.wall, self.cmd = \
            code, envelope, stdout, stderr, wall, cmd

    @property
    def ok(self):
        return bool(self.envelope.get("ok"))

    @property
    def result(self):
        return self.envelope.get("result") or {}

    @property
    def error(self):
        return self.envelope.get("error") or {}

    @property
    def error_code(self):
        return self.error.get("code", "")

    @property
    def details(self):
        return self.error.get("details") or {}

    def __repr__(self):
        return f"<Out ok={self.ok} code={self.code} err={self.error_code}>"


# ------------------------------------------------------------------ assertions
def check(test_id, condition, detail=""):
    _RESULTS.append((test_id, bool(condition), detail))
    print(f"{'PASS' if condition else 'FAIL'} {test_id}  {detail}", flush=True)
    return bool(condition)


def report(name):
    bad = [r for r in _RESULTS if not r[1]]
    print(f"\n--- {name}: {len(_RESULTS) - len(bad)}/{len(_RESULTS)} PASS ---", flush=True)
    return 1 if bad else 0


def main(fn, name):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        fn()
    except Exception as exc:  # a probe that cannot run is a failure, recorded as one
        import traceback
        traceback.print_exc()
        check(f"{name}-HARNESS", False, f"probe raised: {exc}")
    sys.exit(report(name))
