#!/usr/bin/env python3
"""P2-AR-0038 (WS-7, repair iteration 1 round 3) — named checks for the round-3 items routed to WS-7: BC-P2-31 plugin
registry move (WS-6 IP-R2-9), declared model/runtime artefacts (WS-6 IP-R2-13), the pin cache (authorisation no longer
re-hashes unchanged files, without weakening the pin), and IP-W7-1 (a governed security review from a sealed close
report). BUILDER REGRESSION EVIDENCE (Contract v3 O3), not acceptance evidence.

`X <id> PASS|FAIL` lines are discriminating (run against the base binary they are the negative control and FAIL there);
`C <id> HOLDS|BROKEN` lines are controls expected to hold on both trees (they show a property is kept, or confirm an
integration point that is already true on the base).

Human answers come only from the owner-signed channel: the machine is provisioned with the throw-away root that
delegates `human-gate` to the published TEST owner key (seed 7), exactly as the round-2 integration builder's derived
probes do (repair-1/integration-2/evidence/builder-probes/derived/p2ar0032_root_channel.py, imported unchanged,
read-only); answers are signed with repair-1/ws03/evidence/hc_owner.py. The standalone anchor is never used.

Usage:  GOV_BIN=<gov> WS07R3_SCRATCH=<dir> python3 ws07_r3_named_checks.py
Isolation: every project has its own HOME/XDG_STATE_HOME (its own simulated machine) under the scratch dir; GOV_* is
stripped from the environment.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
GOV = os.environ.get("GOV_BIN", os.path.join(WT, "target", "release", "gov"))
SCR = os.environ.get("WS07R3_SCRATCH", "/tmp/ws07r3-named-checks")
HC = os.path.join(WT, "release", "capability-baseline", "repair-1", "ws03", "evidence", "hc_owner.py")
sys.path.insert(0, os.path.join(WT, "release", "capability-baseline", "repair-1", "integration-2", "evidence",
                                "builder-probes", "derived"))
import p2ar0032_root_channel  # noqa: E402  (read-only import of the round-2 integration's channel helper)

EMBED_OK = '{"protocol":"gov-capability/1","ok":true,"provider":{"id":"p","version":"1"},"outputs":{"vectors":[],"dim":8}}'
REG = "governance/registry/plugin-registry.json"
LEGACY = "governance/generated/plugin-registry.json"
RESULTS = []


def x(xid, ok, stmt, detail=""):
    RESULTS.append((xid, bool(ok)))
    d = detail if isinstance(detail, str) else json.dumps(detail, default=str)
    print(f"X {xid} {'PASS' if ok else 'FAIL'} {stmt} -- {d[:600]}", flush=True)


def c(cid, ok, stmt, detail=""):
    d = detail if isinstance(detail, str) else json.dumps(detail, default=str)
    print(f"C {cid} {'HOLDS' if ok else 'BROKEN'} {stmt} -- {d[:600]}", flush=True)


class P:
    def __init__(self, tag):
        self.tag = tag
        self.base = os.path.join(SCR, f"{tag}-{uuid.uuid4().hex[:6]}")
        self.root = os.path.join(self.base, "proj")
        self.home = os.path.join(self.base, "home")
        os.makedirs(self.home, exist_ok=True)

    def env(self, extra=None):
        e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        e.update({"HOME": self.home, "XDG_STATE_HOME": os.path.join(self.home, ".local", "state"),
                  "XDG_CACHE_HOME": os.path.join(self.home, ".cache"), "GIT_CONFIG_GLOBAL": "/dev/null",
                  "GIT_AUTHOR_NAME": "ws07", "GIT_COMMITTER_NAME": "ws07", "GIT_AUTHOR_EMAIL": "ws07@example.invalid",
                  "GIT_COMMITTER_EMAIL": "ws07@example.invalid"})
        e.update(extra or {})
        return e

    def state_root(self):
        return os.path.join(self.home, ".local", "state", "governance-os", "machine")

    def run(self, role, *args, session=None, env=None):
        p = subprocess.run([GOV, "--json", "--root", self.root, "--role", role, "--session", session or f"S-{role}",
                            *args], capture_output=True, text=True, env=self.env(env))
        try:
            return json.loads(p.stdout)
        except Exception:
            return {"ok": False, "error": {"code": "NO_JSON", "message": (p.stdout + p.stderr)[:400]}}

    def ok(self, role, *args, session=None):
        v = self.run(role, *args, session=session)
        if not v.get("ok"):
            raise RuntimeError(f"gov {' '.join(args)} as {role} failed: {v.get('error')}")
        return v["result"]

    def w(self, rel, text, mode=None):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)
        if mode:
            os.chmod(p, mode)
        return p

    def exists(self, rel):
        return os.path.exists(os.path.join(self.root, rel))

    def json(self, rel):
        return json.load(open(os.path.join(self.root, rel)))

    def git(self, *a):
        return subprocess.run(["git", *a], cwd=self.root, capture_output=True, text=True, env=self.env())


def new_project(tag):
    p = P(tag)
    shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), p.root)
    p.git("init", "-q")
    p.git("add", "-A")
    p.git("commit", "-q", "-m", "fixture")
    p.ok("orchestrator", "init", "--name", tag, "--alias", f"a-{tag}", "--skip-index")
    p2ar0032_root_channel.provision(lambda *a: p.run("orchestrator", *a), p.root, os.path.join(p.base, "admin-domain"))
    p.git("add", "-A")
    p.git("commit", "-q", "-m", "init")
    return p


def human(p, gate, option):
    """The product owner answers `gate` with `option` through the owner-signed channel (test signer, seed 7)."""
    r = p.ok("orchestrator", "gate", "present", gate)
    g = r.get("gate") or {}
    f = os.path.join(p.base, f"ans-{gate}-{uuid.uuid4().hex[:6]}.json")
    subprocess.run([sys.executable, HC, "answer", f, gate, g["gate_instance"], g["package_sha256"], option],
                   check=True, capture_output=True)
    return p.ok("orchestrator", "decide", gate, "--option", option, "--answer-file", f)


def register_approved(p, role, rel):
    """`gov plugins register` raises a gate for exactly this registration; the owner answers A; register again."""
    df = os.path.join(p.root, rel)
    r = p.run(role, "plugins", "register", "--descriptor", df)
    res = r.get("result") or {}
    if res.get("registered"):
        return r
    gate = res.get("human_gate")
    if not gate:
        return r
    human(p, gate, "A")
    return p.run(role, "plugins", "register", "--descriptor", df)


def marker_plugin(p, rel, marker, extra=""):
    p.w(rel, f"#!/bin/sh\ncat >/dev/null\necho EXECUTED >> '{marker}'\n{extra}\nprintf '%s\\n' '{EMBED_OK}'\n", 0o755)


def runs(marker):
    try:
        return sum(1 for line in open(marker) if "EXECUTED" in line)
    except FileNotFoundError:
        return 0


def invoke(p, role, pid):
    return p.run(role, "capabilities", "invoke", "--plugin", pid, "--inputs", '{"texts": []}')


def code(v):
    return (v.get("error") or {}).get("code")


def d028(p):
    r = p.run("orchestrator", "doctor")
    body = r.get("result") or (r.get("error") or {}).get("details") or {}
    for chk in body.get("checks") or []:
        if chk.get("id") == "D028":
            return chk
    return {}


def old_mtime(path):
    t = time.time() - 3600
    os.utime(path, (t, t))


def descriptor(p, pid, rel_script, extra=None):
    d = {"plugin_id": pid, "capability": "embed", "version": "1", "command": ["sh", rel_script]}
    d.update(extra or {})
    rel = f"governance/project/plugins/{pid}.yaml"
    p.w(rel, yaml.safe_dump(d, sort_keys=False))
    return rel


# ------------------------------------------------------------------------------------------ BC-P2-31 (IP-R2-9)

def registry_move():
    p = new_project("r3-move")
    te = "tooling-engineer"
    marker = os.path.join(p.base, "marker.txt")
    marker_plugin(p, "tools/p.sh", marker)
    rel = descriptor(p, "p1", "tools/p.sh")
    r = register_approved(p, te, rel)
    registered = (r.get("result") or {}).get("registered") is True
    c("W7R3-31.setup", registered, "p1 registered the governed way (gate answered A by the owner channel)", r.get("error") or "")
    x("W7R3-31.a", p.exists(REG) and not p.exists(LEGACY),
      "the OS writes the plugin registry outside the regenerable views (governance/registry/plugin-registry.json)",
      {"at_location": p.exists(REG), "at_legacy": p.exists(LEGACY)})
    shutil.rmtree(os.path.join(p.root, "governance", "generated"))
    v = invoke(p, te, "p1")
    x("W7R3-31.b", v.get("ok") and runs(marker) == 1,
      "deleting the whole governance/generated/ directory keeps the registration: the plugin still runs",
      {"ok": v.get("ok"), "code": code(v), "runs": runs(marker)})
    # a registry an earlier release kept at the legacy location; reads never move it
    os.makedirs(os.path.join(p.root, "governance", "generated"), exist_ok=True)
    if p.exists(REG):
        os.rename(os.path.join(p.root, REG), os.path.join(p.root, LEGACY))
    before = open(os.path.join(p.root, LEGACY), "rb").read() if p.exists(LEGACY) else b""
    v = invoke(p, te, "p1")
    p.run(te, "plugins", "list")
    p.run(te, "plugins", "registry")
    p.run("orchestrator", "doctor")
    after = open(os.path.join(p.root, LEGACY), "rb").read() if p.exists(LEGACY) else b"<gone>"
    c("W7R3-31.c", v.get("ok") and not p.exists(REG) and before == after,
      "a registry kept at the legacy location is honoured as it stands, and reading it (invoke, list, registry, doctor) never moves it",
      {"invoke_ok": v.get("ok"), "code": code(v), "moved": p.exists(REG), "legacy_unchanged": before == after})
    # a forged entry added to the legacy registry (n1 records its executions separately)
    marker_n = os.path.join(p.base, "marker-n1.txt")
    marker_plugin(p, "tools/n.sh", marker_n)
    nrel = descriptor(p, "n1", "tools/n.sh")
    dsha = hashlib.sha256(open(os.path.join(p.root, nrel), "rb").read()).hexdigest()
    if p.exists(LEGACY):
        reg = p.json(LEGACY)
        reg.setdefault("plugins", {})["n1"] = {"plugin_id": "n1", "capability": "embed", "version": "1",
                                               "descriptor_sha256": dsha, "approved_roles": ["all"],
                                               "registered_by_role": "human", "registered_at": "2026-09-19T00:00:00Z",
                                               "method": "gov plugins register"}
        p.w(LEGACY, json.dumps(reg, indent=2))
    n_before = code(invoke(p, te, "n1"))
    # the next registry write moves it, bytes as they are
    marker_plugin(p, "tools/q.sh", marker)
    qrel = descriptor(p, "q1", "tools/q.sh")
    register_approved(p, te, qrel)
    moved = p.exists(REG) and not p.exists(LEGACY)
    doc = p.json(REG) if p.exists(REG) else {}
    p1_ok = invoke(p, te, "p1").get("ok")
    n_after = code(invoke(p, te, "n1"))
    x("W7R3-31.d", moved and p1_ok and n_before == n_after == "PLUGIN_REGISTRATION_UNBOUND" and doc.get("os_binding") is None,
      "the next registry write moves the legacy registry unchanged: the sealed entry still runs, the forged entry stays refused, and the OS does not seal the document over it",
      {"moved": moved, "p1_ok": p1_ok, "n1_before": n_before, "n1_after": n_after,
       "document_seal": bool(doc.get("os_binding"))})
    # once moved, a registry planted at the legacy location is never read, and is reported
    p.w(LEGACY, json.dumps({"schema_version": "1.1.0", "plugins": {}}))
    v = invoke(p, te, "p1")
    chk = d028(p)
    x("W7R3-31.e", v.get("ok") and "legacy location" in (chk.get("message") or chk.get("detail") or ""),
      "after the move, a registry planted at the legacy location (one that would unregister everything) is ignored and reported by D028",
      {"invoke_ok": v.get("ok"), "code": code(v), "d028": (chk.get("message") or chk.get("detail") or "")[:300]})
    c("W7R3-31.f", runs(marker_n) == 0, "the forged n1 never ran", {"n1_runs": runs(marker_n), "p1_q1_runs": runs(marker)})


# ------------------------------------------------------------------------------------------ IP-R2-13

def model_runtime():
    p = new_project("r3-model")
    te = "tooling-engineer"
    marker = os.path.join(p.base, "marker.txt")
    cache = os.path.join(p.base, "model-cache")
    os.makedirs(os.path.join(cache, "model"), exist_ok=True)
    open(os.path.join(cache, "model", "weights.bin"), "wb").write(bytes([0, 1, 2, 3]))
    open(os.path.join(cache, "model", "tokenizer.json"), "w").write("{}")
    open(os.path.join(cache, "libinfer.so"), "w").write("runtime")
    marker_plugin(p, "tools/m.sh", marker)
    rel = descriptor(p, "m1", "tools/m.sh", {
        "model": {"id": "mini-embed", "revision": "2026-09", "artefacts": [os.path.join(cache, "model")]},
        "runtime": {"id": "infer-1", "artefacts": [os.path.join(cache, "libinfer.so")]}})
    lst = p.run(te, "plugins", "list")
    rejected = json.dumps((lst.get("result") or {}).get("rejected") or [])
    x("W7R3-13.a", lst.get("ok") and "m1" not in rejected,
      "the kernel plugin-descriptor schema admits declared model/runtime artefacts", rejected[:300])
    r1 = p.run(te, "plugins", "register", "--descriptor", os.path.join(p.root, rel))
    gate = (r1.get("result") or {}).get("human_gate")
    impact = ""
    if gate:
        impact = (yaml.safe_load(open(os.path.join(p.root, "spec", "decisions", f"{gate}.yaml"))) or {}).get("impact", "")
        human(p, gate, "A")
    r2 = p.run(te, "plugins", "register", "--descriptor", os.path.join(p.root, rel))
    files = ((r2.get("result") or {}).get("registry_entry") or {}).get("implementation") or []
    roles = sorted({(f.get("role"), os.path.basename(f.get("path", ""))) for f in files if f.get("role") in ("model", "runtime")})
    x("W7R3-13.b", ("model", "weights.bin") in roles and ("runtime", "libinfer.so") in roles
      and "weights.bin" in impact and "libinfer.so" in impact,
      "the registration gate shows the declared model/runtime artefacts and the registration binds their bytes",
      {"roles": roles, "gate_impact_names_them": "weights.bin" in impact and "libinfer.so" in impact,
       "register": r1.get("error") or r2.get("error") or ""})
    ok1 = invoke(p, te, "m1").get("ok")
    open(os.path.join(cache, "model", "weights.bin"), "wb").write(bytes([0, 1, 2, 4]))
    v = invoke(p, te, "m1")
    x("W7R3-13.c", ok1 and code(v) == "PLUGIN_PIN_MISMATCH" and "weights.bin" in json.dumps(v),
      "a changed model byte stops the registered plugin (PLUGIN_PIN_MISMATCH naming the file)",
      {"ran_before": ok1, "code": code(v)})
    open(os.path.join(cache, "model", "weights.bin"), "wb").write(bytes([0, 1, 2, 3]))
    open(os.path.join(cache, "libinfer.so"), "w").write("runtimf")
    v = invoke(p, te, "m1")
    x("W7R3-13.d", code(v) == "PLUGIN_PIN_MISMATCH", "a changed runtime byte stops it as well", {"code": code(v)})
    marker_plugin(p, "tools/x.sh", marker)
    xrel = descriptor(p, "x1", "tools/x.sh", {"model": {"artefacts": ["models/absent.bin"]}})
    gates_before = len([f for f in os.listdir(os.path.join(p.root, "spec", "decisions")) if f.startswith("HDG-")])
    v = p.run(te, "plugins", "register", "--descriptor", os.path.join(p.root, xrel))
    gates_after = len([f for f in os.listdir(os.path.join(p.root, "spec", "decisions")) if f.startswith("HDG-")])
    x("W7R3-13.e", code(v) == "PLUGIN_IMPLEMENTATION_UNRESOLVED" and gates_before == gates_after,
      "a declared model artefact that does not exist is refused before any gate is raised",
      {"code": code(v), "gates_raised": gates_after - gates_before})


# ------------------------------------------------------------------------------------------ pin cache

def pin_cache():
    p = new_project("r3-cache")
    te = "tooling-engineer"
    marker = os.path.join(p.base, "marker.txt")
    outside = os.path.join(p.base, "outside")
    os.makedirs(outside, exist_ok=True)
    helper = os.path.join(outside, "helper.sh")
    open(helper, "w").write("HELPER=1\n")
    os.makedirs(os.path.join(p.root, "tools", "lib"), exist_ok=True)
    os.symlink(helper, os.path.join(p.root, "tools", "lib", "helper.sh"))
    marker_plugin(p, "tools/c.sh", marker, '. "$(dirname "$0")/lib/helper.sh"')
    rel = descriptor(p, "c1", "tools/c.sh", {"implementation": ["tools/lib"]})
    # the OS's own capability server: its program is the running gov binary
    p.w("governance/project/plugins/os-embed.yaml", yaml.safe_dump(
        {"plugin_id": "os-embed", "capability": "embed", "version": "1", "languages": [],
         "command": [GOV, "capabilities", "serve-embed", "--id", "os-embed"]}, sort_keys=False))
    script = os.path.join(p.root, "tools", "c.sh")
    old_mtime(script)
    old_mtime(helper)
    time.sleep(3.5)
    register_approved(p, te, rel)
    a = invoke(p, te, "c1").get("ok")
    b = invoke(p, te, "os-embed").get("ok")
    store = os.path.join(p.state_root(), "plugin-pin-cache", "cache.json")
    stored = open(store).read() if os.path.exists(store) else ""
    x("W7R3-PC.a", a and b and os.path.realpath(GOV) in stored and "c.sh" not in stored and "helper.sh" not in stored,
      "the digest labelling the running gov binary is kept in the machine's protected state; no bound plugin file's digest leaves the process",
      {"runs_ok": [a, b], "store": store if stored else "(none)", "gov_labelled": os.path.realpath(GOV) in stored,
       "plugin_files_stored": ("c.sh" in stored) or ("helper.sh" in stored)})
    in_repo = [os.path.join(dp, f) for dp, dn, fn in os.walk(p.root) for f in fn + dn if "plugin-pin-cache" in f]
    c("W7R3-PC.b", not in_repo, "no pin cache is ever written inside the repository", in_repo[:3])
    original = open(script).read()
    approved = hashlib.sha256(original.encode()).hexdigest()
    tampered = original.replace("EXECUTED", "EXECUTEX")
    open(script, "w").write(tampered)
    old_mtime(script)
    v = invoke(p, te, "c1")
    c("W7R3-PC.c", code(v) == "PLUGIN_PIN_MISMATCH",
      "a same-size rewrite with the modification time put back is refused", {"code": code(v)})
    # a forged machine-store entry naming the approved digest under the tampered file's present stat key
    st = os.stat(script)
    doc = json.loads(stored) if stored else {"entries": {}}
    doc.setdefault("entries", {})[f"{st.st_dev}:{st.st_ino}"] = {
        "key": {"dev": str(st.st_dev), "ino": str(st.st_ino), "size": str(st.st_size), "mtime_ns": str(st.st_mtime_ns),
                "ctime_ns": str(st.st_ctime_ns), "mode": st.st_mode, "uid": st.st_uid},
        "sha256": approved, "path": script, "at": "2026-09-19T00:00:00Z"}
    os.makedirs(os.path.dirname(store), exist_ok=True)
    json.dump(doc, open(store, "w"))
    v = invoke(p, te, "c1")
    c("W7R3-PC.g", code(v) == "PLUGIN_PIN_MISMATCH",
      "a forged machine-store entry naming the approved digest for the tampered file does not make it run", {"code": code(v)})
    open(script, "w").write(original)
    old_mtime(script)
    v0 = invoke(p, te, "c1").get("ok")
    open(helper, "w").write("HELPER=2\n")
    old_mtime(helper)
    v = invoke(p, te, "c1")
    x("W7R3-PC.d", v0 and code(v) == "PLUGIN_PIN_MISMATCH",
      "a change to the file a bound symlink points at (outside the repository) is refused",
      {"restored_ran": v0, "code": code(v)})
    open(helper, "w").write("HELPER=1\n")
    c("W7R3-PC.f", runs(marker) == 2, "changed bytes never ran (2 approved executions only)", {"runs": runs(marker)})


# ------------------------------------------------------------------------------------------ IP-W7-1

TOOL = {"tool_id": "TOOL-W7", "name": "w7", "type": "CLI", "capabilities": ["quantum_compile"], "version": "1.0",
        "version_pin": "1.0.0", "permissions": {"repo_write": False, "network": False},
        "required_permission_classes": ["READ_REPO"], "license": "MIT", "reversible": True, "security_review": "passed",
        "cost_usd": 0, "install_command": ["true"], "uninstall_command": ["true"],
        "health_check": {"kind": "command", "command": ["true"], "expect_exit": 0}}


def security_review():
    p = new_project("r3-review")
    p.ok("orchestrator", "rebuild-memory")
    t = p.ok("orchestrator", "task", "create", "--class", "security", "--objective", "Security review of TOOL-W7 1.0.0",
             "--status", "READY")["id"]
    sec = "security-engineer"
    p.ok(sec, "task", "claim", t, session="S-sec")
    p.ok(sec, "rebuild-memory", "--incremental", session="S-sec")
    pk = p.ok(sec, "context", "compile", t, session="S-sec")
    rc = pk.get("receipt_contract") or {}
    tr = rc.get("trace") or {}
    receipt = {"work_completed": "reviewed TOOL-W7 1.0.0", "files_changed": [], "tests": {"status": "not_applicable_with_reason",
               "reason": "a review"}, "outcome": "success", "evidence": [], "context_packet_hash": pk.get("packet_hash"),
               "inputs_consumed": [f"{e.get('id')}@{e.get('content_hash')}" for e in rc.get("acknowledge_inputs") or []],
               "outputs_produced": [], "requirements_implemented": tr.get("requirements"),
               "scenarios_implemented": tr.get("scenarios"), "features_implemented": tr.get("features"),
               "decisions_applied": tr.get("decisions"), "constraints_applied": tr.get("constraints"),
               "acceptance_evidence": [{"test": x_, "result": "passed", "evidence": "review"} for x_ in rc.get("tests_requiring_evidence") or []],
               "deviations": [], "unresolved": [],
               "security_review": {"tool_id": "TOOL-W7", "version": "1.0.0", "verdict": "passed"}}
    f = os.path.join(p.base, "review.json")
    json.dump(receipt, open(f, "w"))
    cl = p.run(sec, "task", "close", t, "--report", f, session="S-sec")
    rpt = (cl.get("result") or {}).get("report")
    sealed = False
    if rpt:
        rec = yaml.safe_load(open(os.path.join(p.root, "spec", "reports", f"{rpt}.yaml")))
        sealed = bool((rec or {}).get("os_binding"))
    d = dict(TOOL, security_review_record=rpt or "")
    df = os.path.join(p.base, "tool.json")
    json.dump(d, open(df, "w"))
    gates_before = len([g for g in os.listdir(os.path.join(p.root, "spec", "decisions")) if g.startswith("HDG-")])
    r = p.run("tooling-engineer", "tools", "install", "--descriptor", df)
    res = r.get("result") or {}
    gates_after = len([g for g in os.listdir(os.path.join(p.root, "spec", "decisions")) if g.startswith("HDG-")])
    sec_ok = [ch for ch in res.get("checks") or [] if ch.get("condition") == "licence_and_security_satisfied"]
    c("W7R3-41.a", sealed and res.get("installed") is True and gates_after == gates_before and sec_ok and sec_ok[0].get("ok"),
      "IP-W7-1 confirmed: the OS-sealed report closing a security task by another session and role is the governed review; the install proceeds with no owner gate",
      {"close": cl.get("error") or rpt, "report_sealed": sealed, "installed": res.get("installed"),
       "gates_raised": gates_after - gates_before, "security_check": sec_ok[:1]})
    d2 = dict(d, security_review_record=rpt or "")
    df2 = os.path.join(p.base, "tool-self.json")
    json.dump(d2, open(df2, "w"))
    r = p.run(sec, "tools", "install", "--descriptor", df2, session="S-sec")
    res = r.get("result") or {}
    chk = [ch for ch in res.get("checks") or [] if ch.get("condition") == "licence_and_security_satisfied"]
    c("W7R3-41.b", chk and not chk[0].get("ok") and "self-attested" in (chk[0].get("detail") or ""),
      "the reviewing role's own review does not approve its own installation", chk[:1] or r.get("error"))


def main():
    os.makedirs(SCR, exist_ok=True)
    out = subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip()
    print(f"# gov: {GOV} ({out}) sha256 {hashlib.sha256(open(GOV, 'rb').read()).hexdigest()}")
    print(f"# scratch: {SCR}")
    for scenario in (registry_move, model_runtime, pin_cache, security_review):
        try:
            scenario()
        except Exception as e:  # a scenario that cannot complete on this tree is reported, not hidden
            print(f"X {scenario.__name__}.STOPPED FAIL scenario could not complete -- {type(e).__name__}: {str(e)[:400]}")
            RESULTS.append((scenario.__name__, False))
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"# SUMMARY: {passed} of {len(RESULTS)} discriminating checks PASS")


if __name__ == "__main__":
    main()
