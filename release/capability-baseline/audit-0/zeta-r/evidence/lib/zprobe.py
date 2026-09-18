"""P2-AR-0012 (family zeta, Gate W) probe harness.

Independent audit tooling, NOT product code. Drives the candidate's release binary `target/release/gov` against
disposable projects created from the product's own fixtures, mirroring the environment the product's certification
harness uses (tests/certification/common.rs: GOV_CANONICAL_ROOT = repository root; XDG_STATE_HOME = a per-project
simulated machine home; --json --root --session --role on every call).

Every `gov` invocation is logged verbatim ("$ gov ...") together with the product's JSON envelope (or the relevant
excerpt), and every observation line ("OBS <id>: PASS|FAIL ...") is computed from that product output, never echoed.

Re-run: python3 <probe>.py   (from any cwd). Env ZPROBE_SCRATCH overrides the scratch root (default: a fresh temp dir).
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
GOV = os.path.join(WT, "target", "release", "gov")
_SCRATCH = os.environ.get("ZPROBE_SCRATCH") or tempfile.mkdtemp(prefix="zprobe-")
RESULTS = []


def log(*a):
    print(*a, flush=True)


def jdump(v, limit=4000):
    s = json.dumps(v, indent=1, sort_keys=True)
    if len(s) > limit:
        s = s[:limit] + f"\n... [truncated {len(s) - limit} chars]"
    return s


def obs(oid, ok, detail):
    """Record an observation computed from product output."""
    RESULTS.append((oid, bool(ok), detail))
    log(f"OBS {oid}: {'PASS' if ok else 'FAIL'} -- {detail}")


def summary():
    log("\n==== SUMMARY ====")
    for oid, ok, d in RESULTS:
        log(f"{oid}: {'PASS' if ok else 'FAIL'}")
    log(f"total={len(RESULTS)} pass={sum(1 for r in RESULTS if r[1])} fail={sum(1 for r in RESULTS if not r[1])}")


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


class Gov:
    def __init__(self, root, session="S-zeta", role="orchestrator", machine=None, env=None):
        self.root = root
        self.session = session
        self.role = role
        self.machine = machine or os.path.join(_SCRATCH, "machine-" + os.path.basename(root))
        self.env = dict(env or {})

    def with_(self, session=None, role=None):
        g = Gov(self.root, session or self.session, role or self.role, self.machine, self.env)
        return g

    def run(self, *args, quiet=False, limit=4000):
        cmd = [GOV, "--json", "--root", self.root, "--session", self.session, "--role", self.role, *args]
        env = dict(os.environ)
        env["GOV_CANONICAL_ROOT"] = WT
        env["XDG_STATE_HOME"] = self.machine
        env.pop("GOV_SESSION", None)
        env.pop("GOV_ROLE", None)
        env.update(self.env)
        t0 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        dt = time.time() - t0
        try:
            envl = json.loads(p.stdout.strip())
        except Exception:
            envl = {"ok": False, "error": {"code": "NO_JSON", "message": p.stderr[-2000:], "stdout": p.stdout[-2000:]}}
        shown = " ".join(a if " " not in a and a else json.dumps(a) for a in ["gov", *args])
        log(f"$ {shown}    [session={self.session} role={self.role} exit={p.returncode} {dt:.1f}s]")
        if not quiet:
            if envl.get("ok"):
                log("  ok=true result=" + jdump(envl.get("result"), limit))
            else:
                log("  ok=false error=" + jdump(envl.get("error"), limit))
        return envl

    def ok(self, *args, **kw):
        e = self.run(*args, **kw)
        if not e.get("ok"):
            raise RuntimeError(f"gov {' '.join(args)} failed: {e.get('error')}")
        return e["result"]


def new_project(tag, fixture="greenfield", init=True, name=None):
    root = os.path.join(_SCRATCH, f"{tag}-{int(time.time()*1000) % 10**9}")
    shutil.copytree(os.path.join(WT, "fixtures", fixture, "project"), root)
    git(root, "init", "-q")
    git(root, "config", "user.email", "zeta@example.invalid")
    git(root, "config", "user.name", "zeta")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture baseline")
    g = Gov(root)
    log(f"# project {tag}: fixture={fixture} root={root}")
    if init:
        r = g.run("init", "--name", name or tag, "--alias", f"z-{tag}"[:24], quiet=True)
        if not r.get("ok"):
            log("  init FAILED: " + jdump(r.get("error")))
            raise RuntimeError("init failed")
        log(f"  init ok: version={r['result'].get('version')} conformance={r['result'].get('conformance', {}).get('verdict')}")
        commit(root, "after gov init")
    return root, g


def commit(root, msg):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)


def write_record(root, rel, data):
    """Write a governed record as YAML (JSON is valid YAML; serde_yaml reads it)."""
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(json.dumps(data, indent=1) + "\n")
    log(f"  [probe wrote record] {rel}: {json.dumps(data)[:600]}")


def read_json(root, rel):
    with open(os.path.join(root, rel)) as f:
        return json.load(f)


def read_text(root, rel):
    with open(os.path.join(root, rel)) as f:
        return f.read()


def write_text(root, rel, text):
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)
    log(f"  [probe wrote file] {rel} ({len(text)} chars)")


def readiness_all_present():
    import yaml
    dims = yaml.safe_load(open(os.path.join(WT, "framework", "taxonomy", "READINESS_DIMENSIONS.yaml")))["dimensions"]
    ids = [d["id"] for d in dims]
    assert len(ids) >= 20, ids
    return {i: "PRESENT" for i in ids}


def db(root):
    return sqlite3.connect(os.path.join(root, ".governance-runtime", "state.db"))


def write_report(root, name, work, files, tests_status="passed", extra=None):
    d = os.path.join(root, ".governance-runtime", "reports")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, f"{name}.json")
    v = {"work_completed": work, "files_changed": files, "tests": {"status": tests_status, "reason": "zeta probe"},
         "outcome": "success", "evidence": []}
    if extra:
        v.update(extra)
    with open(f, "w") as fh:
        json.dump(v, fh)
    log(f"  [probe wrote worker report] {f}: {json.dumps(v)[:600]}")
    return f


def base_spec(root, feature="F-0001", req_ids=("REQ-0001",), scn="SCN-0001", extra_feature=None):
    """A feature with complete readiness, its requirements and one scenario (mirrors the greenfield certification spec)."""
    fd = {"id": feature, "type": "feature", "title": "Order totals", "status": "ACTIVE", "capability_category": "backend",
          "requirements": list(req_ids), "scenarios": [scn], "acceptance_tests": ["TST-0001"],
          "readiness": readiness_all_present()}
    if extra_feature:
        fd.update(extra_feature)
    write_record(root, f"spec/features/{feature}.yaml", fd)
    write_record(root, f"spec/scenarios/{scn}.yaml",
                 {"id": scn, "type": "scenario", "title": "Append two orders and total", "status": "ACTIVE",
                  "feature": feature, "actor": "clerk", "given": ["an empty ledger"], "when": ["two orders are appended"],
                  "then": ["total_cents is 399"], "success_criteria": ["exact total"], "failure_criteria": ["duplicate ids accepted"]})
    write_record(root, "spec/tasks/TST-0001.yaml",
                 {"id": "TST-0001", "type": "test-obligation", "title": "Totals acceptance test", "status": "ACTIVE",
                  "feature": feature, "family": "unit", "scenario": scn})
