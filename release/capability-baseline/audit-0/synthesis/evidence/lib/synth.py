"""P2-AR-0007 synthesis probe harness (independent evidence; NOT a product test, never added to the product tree).

Every probe copies a fixture from the audited checkout into SYNTH_SCRATCH, drives `target/release/gov` through its
JSON CLI contract and prints:
    $ gov <args>   [role=.. session=.. exit=..]        the exact command
    X <id> PASS|FAIL <statement> -- <detail>          an observation cited by the synthesis report
    NOTE <text>                                        neutral context

Isolation: each project gets its own HOME and XDG_STATE_HOME (protected machine state) under the scratch area; every
GOV_* variable is stripped; GOV_CANONICAL_ROOT is NOT set, so `gov init` installs the kernel embedded in the binary
(the consumer default). Nothing outside the scratch area is written.

Environment: SYNTH_SCRATCH (default $TMPDIR/p2-ar-0007), GOV_BIN (default <worktree>/target/release/gov).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
GOV = os.environ.get("GOV_BIN", os.path.join(WT, "target", "release", "gov"))
SCRATCH = os.environ.get("SYNTH_SCRATCH", os.path.join(tempfile.gettempdir(), "p2-ar-0007"))
RESULTS = []


def log(*a):
    print(*a, flush=True)


def x(xid, ok, statement, detail=""):
    RESULTS.append((xid, bool(ok)))
    d = detail if isinstance(detail, str) else json.dumps(detail, sort_keys=True, default=str)
    log(f"X {xid} {'PASS' if ok else 'FAIL'} {statement} -- {d[:1800]}")


def note(t):
    log("NOTE " + t)


def summary():
    f = [i for i, ok in RESULTS if not ok]
    log(f"SUMMARY total={len(RESULTS)} pass={len(RESULTS) - len(f)} fail={len(f)} failed={f}")


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def commit(root, msg):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)


class Gov:
    def __init__(self, root, home, role="orchestrator", session="S-synth", extra_env=None, pass_role=True):
        self.root, self.home, self.role, self.session = root, home, role, session
        self.extra_env = dict(extra_env or {})
        self.pass_role = pass_role

    def as_(self, role=None, session=None, extra_env=None, pass_role=True):
        env = dict(self.extra_env)
        env.update(extra_env or {})
        return Gov(self.root, self.home, role or self.role, session or self.session, env, pass_role)

    def env(self):
        e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        e["HOME"] = self.home
        e["XDG_STATE_HOME"] = os.path.join(self.home, ".local", "state")
        e["XDG_CACHE_HOME"] = os.path.join(self.home, ".cache")
        e["GIT_CONFIG_GLOBAL"] = "/dev/null"
        e["GIT_AUTHOR_NAME"] = e["GIT_COMMITTER_NAME"] = "synth"
        e["GIT_AUTHOR_EMAIL"] = e["GIT_COMMITTER_EMAIL"] = "synth@example.invalid"
        e["PATH"] = os.path.expanduser("~/.cargo/bin") + ":" + os.environ.get("PATH", "")
        e.update(self.extra_env)
        return e

    def run(self, *args, quiet=False, limit=1500):
        cmd = [GOV, "--json", "--root", self.root]
        if self.session:
            cmd += ["--session", self.session]
        if self.pass_role and self.role:
            cmd += ["--role", self.role]
        cmd += list(args)
        p = subprocess.run(cmd, capture_output=True, text=True, env=self.env(), cwd=self.root)
        try:
            v = json.loads(p.stdout)
        except Exception:
            v = {"ok": False, "error": {"code": "NO_JSON", "message": (p.stderr or p.stdout)[-1500:]}}
        v["_exit"] = p.returncode
        envd = " ".join(f"{k}={v2}" for k, v2 in self.extra_env.items())
        shown = " ".join(a if (a and " " not in a) else json.dumps(a) for a in args)
        rl = f"role={self.role if self.pass_role else '(none: --role not passed)'}"
        log(f"$ {envd + ' ' if envd else ''}gov {shown}   [{rl} session={self.session} exit={p.returncode}]")
        if not quiet:
            if v.get("ok"):
                log("   ok " + json.dumps(v.get("result"), sort_keys=True, default=str)[:limit])
            else:
                log("   ERR " + json.dumps(v.get("error"), sort_keys=True, default=str)[:limit])
        return v

    def ok(self, *args, **kw):
        v = self.run(*args, **kw)
        if not v.get("ok"):
            raise RuntimeError(f"gov {' '.join(args)} failed: {v.get('error')}")
        return v["result"]


def new_project(tag, fixture="greenfield", init=True, name=None):
    os.makedirs(SCRATCH, exist_ok=True)
    base = os.path.join(SCRATCH, f"{tag}-{uuid.uuid4().hex[:6]}")
    root = os.path.join(base, "proj")
    home = os.path.join(base, "home")
    os.makedirs(home)
    shutil.copytree(os.path.join(WT, "fixtures", fixture, "project"), root)
    git(root, "init", "-q")
    git(root, "config", "user.email", "synth@example.invalid")
    git(root, "config", "user.name", "synth")
    commit(root, "fixture baseline")
    g = Gov(root, home)
    log(f"# project {tag}: fixture={fixture} root={root}")
    if init:
        r = g.run("init", "--name", name or tag, quiet=True)
        if not r.get("ok"):
            raise RuntimeError(f"init failed: {r.get('error')}")
        log(f"   init ok version={r['result'].get('version')}")
        commit(root, "after gov init")
    return root, g


def write_record(root, rel, data):
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(json.dumps(data, indent=1) + "\n")
    log(f"   [probe wrote] {rel}")


def read(root, rel):
    with open(os.path.join(root, rel)) as f:
        return f.read()


def write(root, rel, text):
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)
    log(f"   [probe wrote] {rel} ({len(text)} chars)")


def yload(root, rel):
    import yaml
    return yaml.safe_load(read(root, rel))


def readiness_all_present():
    import yaml
    dims = yaml.safe_load(open(os.path.join(WT, "framework", "taxonomy", "READINESS_DIMENSIONS.yaml")))["dimensions"]
    return {d["id"]: "PRESENT" for d in dims}


def report(root, name, work, files, tests="passed", extra=None):
    d = os.path.join(root, ".governance-runtime", "synth-reports")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, name + ".json")
    v = {"work_completed": work, "files_changed": files, "tests": {"status": tests, "reason": "synthesis probe"},
         "outcome": "success", "evidence": []}
    v.update(extra or {})
    json.dump(v, open(f, "w"))
    return f


def spec_base(root):
    """Feature F-0001 with complete readiness, REQ-0001, SCN-0001, TST-0001 (mirrors the greenfield certification spec)."""
    write_record(root, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Order totals", "status": "ACTIVE",
                 "capability_category": "backend", "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"],
                 "acceptance_tests": ["TST-0001"], "readiness": readiness_all_present()})
    write_record(root, "spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact integer cents",
                 "status": "ACTIVE", "feature": "F-0001", "kind": "functional", "acceptance_criteria": ["2 x 199 = 398"]})
    write_record(root, "spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Append two orders and total",
                 "status": "ACTIVE", "feature": "F-0001", "actor": "clerk", "given": ["an empty ledger"], "when": ["two orders are appended"],
                 "then": ["total_cents is 398"], "success_criteria": ["exact total"], "failure_criteria": ["rounding"]})
    write_record(root, "spec/tasks/TST-0001.yaml", {"id": "TST-0001", "type": "test-obligation", "title": "Totals acceptance test",
                 "status": "ACTIVE", "feature": "F-0001", "family": "unit", "scenario": "SCN-0001"})
