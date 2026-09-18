"""P2-AR-0011 (family delta re-audit) probe harness.

Independent evidence only: this file is NOT a product test and is never added to the product tree.

Every probe creates a disposable Governance OS project with `gov init` under a scratch directory, drives the
release binary `target/release/gov` of the audited worktree through its CLI JSON contract (API-0002), and prints
one line per observation:

    $ gov <args>                        -- the exact command line (role/session/env shown)
    CHECK <id> PASS|FAIL <statement>    -- an observation the audit record cites by <id>

Machine state is isolated per project with XDG_STATE_HOME (the same mechanism the builder certification suite uses),
so no probe reads or writes the operator's real protected machine state.

Environment:
    GOV_BIN        path to the gov binary (default: <worktree>/target/release/gov)
    PROBE_SCRATCH  directory for disposable projects (default: $TMPDIR/p2-ar-0011-probes)
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
GOV = os.environ.get("GOV_BIN", os.path.join(WT, "target", "release", "gov"))
SCRATCH = os.environ.get("PROBE_SCRATCH", os.path.join(tempfile.gettempdir(), "p2-ar-0011-probes"))

RESULTS = []


def check(cid, ok, statement, detail=None):
    RESULTS.append((cid, bool(ok)))
    line = f"CHECK {cid} {'PASS' if ok else 'FAIL'} {statement}"
    print(line, flush=True)
    if detail is not None:
        print("      detail: " + (detail if isinstance(detail, str) else json.dumps(detail, sort_keys=True)[:1500]), flush=True)


def observe(cid, statement, value=None):
    """A neutral observation (not a pass/fail judgement)."""
    print(f"OBSERVE {cid} {statement}" + ("" if value is None else ": " + (value if isinstance(value, str) else json.dumps(value, sort_keys=True)[:2000])), flush=True)


def summary():
    n = len(RESULTS)
    f = [c for c, ok in RESULTS if not ok]
    print(f"SUMMARY checks={n} pass={n - len(f)} fail={len(f)} failed={f}", flush=True)


class Proj:
    def __init__(self, name, init=True, init_args=None):
        os.makedirs(SCRATCH, exist_ok=True)
        base = os.path.join(SCRATCH, f"{name}-{int(time.time())}-{uuid.uuid4().hex[:6]}")
        self.root = os.path.join(base, "proj")
        self.state = os.path.join(base, "state")
        os.makedirs(self.root)
        os.makedirs(self.state)
        self.session = "probe-" + uuid.uuid4().hex[:8]
        self.git("init", "-q", ".")
        self.git("config", "user.email", "probe@example.invalid")
        self.git("config", "user.name", "probe")
        print(f"# project: {self.root}", flush=True)
        if init:
            r = self.run(["init", "--name", name] + (init_args or []), quiet=True)
            assert r["ok"], r
            print(f"# gov init ok: version {r['result']['version']} doctor {r['result'].get('doctor')}", flush=True)
            self.git("add", "-A")
            self.git("commit", "-q", "-m", "baseline after gov init")

    def env(self, extra=None):
        e = dict(os.environ)
        for k in ("GOV_ROLE", "GOV_SESSION", "GOV_MACHINE_STATE_DIR"):
            e.pop(k, None)
        e["XDG_STATE_HOME"] = self.state
        e["GOV_CANONICAL_ROOT"] = WT
        if extra:
            for k, v in extra.items():
                if v is None:
                    e.pop(k, None)
                else:
                    e[k] = v
        return e

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)

    def run(self, args, role=None, session=None, env=None, json_mode=True, quiet=False, show=True):
        cmd = [GOV]
        if json_mode:
            cmd.append("--json")
        cmd += ["--root", self.root]
        if session is not False:
            cmd += ["--session", session or self.session]
        if role:
            cmd += ["--role", role]
        cmd += list(args)
        shown = " ".join(("--role " + role + " ") if False else [])
        envdesc = " ".join(f"{k}={v}" for k, v in (env or {}).items())
        disp = " ".join(a if " " not in a else repr(a) for a in cmd[1:]).replace(f"--root {self.root} ", "")
        if show and not quiet:
            print(f"$ {envdesc + ' ' if envdesc else ''}gov {disp}", flush=True)
        p = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, env=self.env(env))
        if not json_mode:
            return {"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
        try:
            v = json.loads(p.stdout)
        except Exception:
            v = {"ok": False, "error": {"code": "NO_JSON", "message": p.stderr[-2000:], "stdout": p.stdout[-2000:]}}
        v["_exit"] = p.returncode
        if show and not quiet:
            if v.get("ok"):
                print("  -> ok", flush=True)
            else:
                err = v.get("error", {})
                print(f"  -> ERROR [{err.get('code')}] {str(err.get('message'))[:600]}", flush=True)
        return v

    def ok(self, args, **kw):
        v = self.run(args, **kw)
        if not v.get("ok"):
            raise SystemExit(f"unexpected failure: gov {' '.join(args)}: {v.get('error')}")
        return v["result"]

    def path(self, rel):
        return os.path.join(self.root, rel)

    def read(self, rel):
        with open(self.path(rel)) as f:
            return f.read()

    def write(self, rel, text):
        full = self.path(rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)

    def yaml(self, rel):
        # PyYAML may be absent; use the product-neutral route: python json from `gov task show`-like reads is not
        # generic, so parse the simple YAML the product writes through a minimal loader when PyYAML is missing.
        try:
            import yaml  # type: ignore
            with open(self.path(rel)) as f:
                return yaml.safe_load(f)
        except ImportError:
            return None

    def record(self, rid):
        """Read a governed record through the product itself (`gov cit show` works for any record id)."""
        v = self.run(["cit", "show", rid], show=False)
        return v.get("result") if v.get("ok") else None

    def find_record_file(self, rid):
        for d, _, fs in os.walk(self.path("spec")):
            for f in fs:
                if f.startswith(rid + ".") or f == rid + ".yaml":
                    return os.path.relpath(os.path.join(d, f), self.root)
        return None


# ---------------------------------------------------------------------------------------------------------------------
# Shared helpers for record edits and CIT manifests (used by the probes other than L3, which carries its own copy).
try:
    import yaml as _yaml

    class NoDatesLoader(_yaml.SafeLoader):
        """SafeLoader that keeps ISO timestamps as strings, so an edit never reformats a value it did not touch."""

    NoDatesLoader.yaml_implicit_resolvers = {
        k: [(t, r) for t, r in v if t != "tag:yaml.org,2002:timestamp"]
        for k, v in _yaml.SafeLoader.yaml_implicit_resolvers.items()
    }
except ImportError:  # pragma: no cover
    _yaml = None


def load_record_file(p, rid):
    rel = p.find_record_file(rid)
    with open(p.path(rel)) as f:
        return rel, _yaml.load(f, Loader=NoDatesLoader)


def edit_record(p, rid, fn, note="direct file write, no gov command"):
    rel, d = load_record_file(p, rid)
    fn(d)
    with open(p.path(rel), "w") as f:
        _yaml.safe_dump(d, f, sort_keys=False)
    print(f"# RECORD EDIT ({note}): {rel}", flush=True)
    return rel


def write_record(p, rel, data, note="direct file write, no gov command"):
    p.write(rel, _yaml.safe_dump(data, sort_keys=False))
    print(f"# RECORD WRITE ({note}): {rel}", flush=True)


def manifest_file(p, name, ops):
    """Write a CIT mutation manifest outside the project tree; `gov cit propose --manifest <path>` takes a plain path."""
    path = os.path.join(os.path.dirname(p.root), f"{name}.json")
    with open(path, "w") as f:
        json.dump(ops, f)
    return path


def json_file(p, name, obj):
    path = os.path.join(os.path.dirname(p.root), f"{name}.json")
    with open(path, "w") as f:
        json.dump(obj, f)
    return path


def cit_via_cli(p, tag, ops, trigger=None, targets=None, role=None, proposal=None):
    """Propose -> (auto-)simulate; returns (cit_id, gate_id_or_None, propose_result, simulation)."""
    args = ["cit", "propose", "--proposal", proposal or f"probe change {tag}", "--manifest", manifest_file(p, f"m-{tag}", ops)]
    if trigger:
        args += ["--trigger", trigger]
    if targets:
        args += ["--targets", ",".join(targets)]
    r = p.ok(args, role=role)
    cid = r["id"]
    sim = r.get("simulation")
    if sim is None:
        sim = p.ok(["cit", "simulate", cid], role=role)
    return cid, sim.get("human_gate"), r, sim


def cit_through(p, tag, ops, trigger=None, targets=None, answer="A"):
    """Full governed path: propose, simulate, present+decide (human relayed by the default orchestrator) if gated,
    approve, execute. Returns (cit_id, execute_envelope)."""
    cid, gid, _, sim = cit_via_cli(p, tag, ops, trigger=trigger, targets=targets)
    if gid:
        p.ok(["gate", "present", gid])
        p.ok(["decide", gid, "--option", answer, "--rationale", "probe relay"])
    a = p.run(["cit", "approve", cid])
    if not a.get("ok"):
        return cid, a
    return cid, p.run(["cit", "execute", cid])
