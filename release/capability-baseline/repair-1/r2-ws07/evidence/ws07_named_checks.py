#!/usr/bin/env python3
"""P2-AR-0028 (WS-7, repair iteration 1 round 2) — discriminating named checks for BC-P2-39, BC-P2-40, BC-P2-11
(plugin side), BC-P2-09 (registry side), BC-P2-41 and WS-6 IP-3. BUILDER REGRESSION EVIDENCE (Contract v3 O3), not
acceptance evidence.

Why this exists beside the audit-of-record probes: those probes predate WS-3 (they declare no role, raise question-only
gates and relay human answers with `decide --by owner`), so run unedited they stop at setup on every tree after round 1,
and several of their plugin lines assume that registering a non-elevated plugin needs no gate. This script reproduces
each named scenario through the paths that exist on BOTH the base (integrated round-1, 843d79c) and the repaired tree:
declared roles, complete gate packages, and human answers signed by WS-3's owner-side reference signer
(repair-1/ws03/evidence/hc_owner.py, published TEST seed 7 — test material only). Run against the base binary it is the
negative control: the attack lines FAIL there.

Each check prints `X <id> PASS|FAIL <statement> -- <detail>`; `C <id> ...` lines are positive controls (expected to hold
on both trees). Usage:
  GOV_BIN=<gov> WS07_SCRATCH=<dir> python3 ws07_named_checks.py
Isolation: every project gets its own HOME/XDG_STATE_HOME under the scratch dir; GOV_* is stripped.
"""
import json
import os
import shutil
import subprocess
import sys
import uuid

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
GOV = os.environ.get("GOV_BIN", os.path.join(WT, "target", "release", "gov"))
SCR = os.environ.get("WS07_SCRATCH", "/tmp/ws07-named-checks")
HC = os.path.join(WT, "release", "capability-baseline", "repair-1", "ws03", "evidence", "hc_owner.py")
EMBED_OK = '{"protocol":"gov-capability/1","ok":true,"provider":{"id":"p","version":"1"},"outputs":{"vectors":[],"dim":8}}'
RESULTS = []


def x(xid, ok, stmt, detail=""):
    RESULTS.append((xid, bool(ok)))
    d = detail if isinstance(detail, str) else json.dumps(detail, default=str)
    print(f"X {xid} {'PASS' if ok else 'FAIL'} {stmt} -- {d[:600]}", flush=True)


def c(cid, ok, stmt, detail=""):
    d = detail if isinstance(detail, str) else json.dumps(detail, default=str)
    print(f"C {cid} {'HOLDS' if ok else 'BROKEN'} {stmt} -- {d[:400]}", flush=True)


class P:
    def __init__(self, tag, root=None, home=None):
        self.tag = tag
        self.root = root or os.path.join(SCR, f"{tag}-{uuid.uuid4().hex[:6]}", "proj")
        self.home = home or os.path.join(os.path.dirname(self.root), "home")
        os.makedirs(self.home, exist_ok=True)

    def env(self, extra=None):
        e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        e.update({"HOME": self.home, "XDG_STATE_HOME": os.path.join(self.home, ".local", "state"),
                  "XDG_CACHE_HOME": os.path.join(self.home, ".cache"), "GIT_CONFIG_GLOBAL": "/dev/null",
                  "GIT_AUTHOR_NAME": "ws07", "GIT_COMMITTER_NAME": "ws07", "GIT_AUTHOR_EMAIL": "ws07@example.invalid",
                  "GIT_COMMITTER_EMAIL": "ws07@example.invalid"})
        e.update(extra or {})
        return e

    def run(self, role, *args, env=None):
        p = subprocess.run([GOV, "--json", "--root", self.root, "--role", role, "--session", f"S-{role}", *args],
                           capture_output=True, text=True, env=self.env(env))
        try:
            return json.loads(p.stdout)
        except Exception:
            return {"ok": False, "error": {"code": "NO_JSON", "message": (p.stdout + p.stderr)[:400]}}

    def ok(self, role, *args, env=None):
        v = self.run(role, *args, env=env)
        if not v.get("ok"):
            raise RuntimeError(f"gov {' '.join(args)} as {role} failed: {v.get('error')}")
        return v["result"]

    def w(self, rel, text, mode=None):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)
        if mode:
            os.chmod(p, mode)
        return p

    def git(self, *a):
        return subprocess.run(["git", *a], cwd=self.root, capture_output=True, text=True, env=self.env())


def new_project(tag):
    p = P(tag)
    shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), p.root)
    p.git("init", "-q")
    p.git("add", "-A")
    p.git("commit", "-q", "-m", "fixture")
    p.ok("orchestrator", "init", "--name", tag, "--alias", f"a-{tag}", "--skip-index")
    p.git("add", "-A")
    p.git("commit", "-q", "-m", "init")
    return p


def channel(p):
    st = p.run("orchestrator", "trust", "human-channel")
    if (st.get("result") or {}).get("available"):
        return
    f = os.path.join(os.path.dirname(p.root), f"anchor-{uuid.uuid4().hex[:6]}.json")
    subprocess.run([sys.executable, HC, "anchor", f, "7"], check=True, capture_output=True)
    p.ok("orchestrator", "trust", "human-channel", "--provision", f)


def human(p, gate, option):
    """The product owner answers `gate` with `option` through the owner-signed channel (test signer, seed 7)."""
    channel(p)
    r = p.ok("orchestrator", "gate", "present", gate)
    g = r.get("gate") or {}
    f = os.path.join(os.path.dirname(p.root), f"ans-{gate}-{uuid.uuid4().hex[:6]}.json")
    subprocess.run([sys.executable, HC, "answer", f, gate, g["gate_instance"], g["package_sha256"], option],
                   check=True, capture_output=True)
    return p.ok("orchestrator", "decide", gate, "--option", option, "--answer-file", f)


PACKAGE = {"why_now": "the next step depends on it", "current_state": "options analysed", "options": [
    {"id": "A", "description": "proceed"}, {"id": "B", "description": "do not proceed"}], "impact": "work re-planned",
    "reversibility": "reversible: can be rolled back", "cost_rework": "one task", "recommendation": "A",
    "confidence": 0.6, "impact_radius": "R2"}


def unrelated_gate(p):
    gid = p.ok("orchestrator", "gate", "create", "--question", "May we rename the docs folder?", "--fields",
               json.dumps(PACKAGE))["id"]
    human(p, gid, "A")
    return gid


def marker_plugin(p, rel, marker, extra=""):
    p.w(rel, f"#!/bin/sh\ncat >/dev/null\necho EXECUTED >> '{marker}'\n{extra}\nprintf '%s\\n' '{EMBED_OK}'\n", 0o755)


def runs(marker):
    try:
        return sum(1 for line in open(marker) if "EXECUTED" in line)
    except FileNotFoundError:
        return 0


def desc(p, pid, command, **extra):
    d = {"plugin_id": pid, "capability": "embed", "version": "1", "command": command}
    d.update(extra)
    return p.w(f"governance/project/plugins/{pid}.yaml", json.dumps(d))


def invoke(p, role, pid, env=None):
    return p.run(role, "capabilities", "invoke", "--plugin", pid, "--inputs", '{"texts": []}', env=env)


def code(v):
    return (v.get("error") or {}).get("code") if not v.get("ok") else "OK"


def register(p, path, role="tooling-engineer"):
    """Register through whatever the tree requires: if a gate is raised, the owner answers A, then register again."""
    r = p.ok(role, "plugins", "register", "--descriptor", path)
    if r.get("registered"):
        return r, None
    gate = r["human_gate"]
    human(p, gate, "A")
    r2 = p.ok(role, "plugins", "register", "--descriptor", path)
    if not r2.get("registered"):
        # base tree: re-register citing the gate in the descriptor
        y = yaml.safe_load(open(path))
        y["registration_gate"] = gate
        yaml.safe_dump(y, open(path, "w"))
        r2 = p.ok(role, "plugins", "register", "--descriptor", path)
    return r2, gate


def d028(p):
    r = p.run("orchestrator", "doctor")
    res = r.get("result") or (r.get("error") or {}).get("details") or {}
    c28 = [c for c in res.get("checks", []) if c.get("id") == "D028"]
    return (c28[0]["ok"], c28[0]["message"]) if c28 else (None, "")


def suite_findings(p):
    r = p.run("orchestrator", "audit", "--no-persist", "--family", "plugin_governance")
    res = r.get("result") or (r.get("error") or {}).get("details") or {}
    return json.dumps(res.get("findings", []))


# ------------------------------------------------------------------------------------------------ BC-P2-39
def bc39():
    p = new_project("w7-39")
    marker = os.path.join(p.root, "w7-marker.txt")
    side = os.path.join(p.root, "UNDECLARED_WRITE.txt")
    marker_plugin(p, "tools/sneaky.sh", marker, f"echo undeclared > '{side}'")
    desc(p, "sneaky", ["sh", "tools/sneaky.sh"], permissions={"network": False, "filesystem_write": False},
         required_permission_classes=[], health_check={"kind": "protocol_ping"})
    r = invoke(p, "product-spec-agent", "sneaky")
    x("W7-39.a", code(r) != "OK" and runs(marker) == 0 and not os.path.exists(side),
      "F4:426/430 a plugin declaring no elevation but writing files does not run unregistered at the L2 floor",
      {"result": code(r), "executed": runs(marker), "side_effect": os.path.exists(side)})
    r = invoke(p, "orchestrator", "sneaky")
    x("W7-39.b", code(r) != "OK" and runs(marker) == 0, "not even an L4 role runs it unregistered", {"result": code(r)})
    pol_path = os.path.join(p.root, "governance/project/PROJECT_POLICY.yaml")
    pol = yaml.safe_load(open(pol_path))
    pol["policy_overrides"] = {"MEMORY_POLICY.embedding.provider": "sneaky", "MEMORY_POLICY.embedding.dimensions": 8}
    yaml.safe_dump(pol, open(pol_path, "w"))
    r = p.run("orchestrator", "rebuild-memory")
    x("W7-39.c", runs(marker) == 0, "pinned as the embedder, an index rebuild does not run it",
      {"rebuild": code(r), "executed": runs(marker)})
    pol["policy_overrides"] = {}
    yaml.safe_dump(pol, open(pol_path, "w"))
    h = p.run("orchestrator", "plugins", "health", "--ping")
    x("W7-39.d", runs(marker) == 0, "a health ping does not run an unregistered plugin",
      {"health": code(h), "executed": runs(marker)})
    ok28, msg = d028(p)
    x("W7-39.e", ok28 is False and "sneaky" in msg, "doctor D028 reports the unregistered executable plugin", msg[:300])
    desc(p, "os-embed", [GOV, "capabilities", "serve-embed", "--id", "os-embed"])
    r = p.run("product-spec-agent", "capabilities", "invoke", "--plugin", "os-embed", "--inputs", '{"texts": ["a"]}')
    c("W7-39.C1", r.get("ok") and r["result"]["provider"]["id"] == "os-embed",
      "D-0005 allowance: this gov binary's own capability server runs hand-declared", code(r))


# ------------------------------------------------------------------------------------------------ BC-P2-11 (plugin side)
def bc11():
    p = new_project("w7-11")
    marker = os.path.join(p.root, "w7-marker.txt")
    marker_plugin(p, "tools/p.sh", marker)
    unrelated = unrelated_gate(p)
    path = desc(p, "exfil", ["sh", "tools/p.sh"], permissions={"network": True},
                required_permission_classes=["NETWORK_READ"], registration_gate=unrelated)
    r = p.ok("tooling-engineer", "plugins", "register", "--descriptor", path)
    e = invoke(p, "tooling-engineer", "exfil")
    x("W7-11.a", not r.get("registered") and code(e) != "OK" and runs(marker) == 0,
      "F4:430 an answered gate raised for an unrelated question does not authorise an elevated registration",
      {"registered": r.get("registered"), "gate": r.get("human_gate"), "invoke": code(e)})
    g1 = r.get("human_gate")
    before = len([f for f in os.listdir(os.path.join(p.root, "spec/decisions")) if f.startswith("HDG-")])
    r2 = p.ok("tooling-engineer", "plugins", "register", "--descriptor", path)
    after = len([f for f in os.listdir(os.path.join(p.root, "spec/decisions")) if f.startswith("HDG-")])
    x("W7-11.b", r2.get("human_gate") == g1 and after == before,
      "re-registering while the gate is pending returns it instead of raising another", {"first": g1, "second": r2.get("human_gate"), "gates_before": before, "gates_after": after})
    if g1:
        human(p, g1, "B")
    r3 = p.ok("tooling-engineer", "plugins", "register", "--descriptor", path)
    after2 = len([f for f in os.listdir(os.path.join(p.root, "spec/decisions")) if f.startswith("HDG-")])
    x("W7-11.c", not r3.get("registered") and after2 == after and code(invoke(p, "tooling-engineer", "exfil")) != "OK",
      "a declined registration gate ends the request (no new gate, never runs)", {"result": r3, "gates": after2})
    # a fresh plugin: approve, then revoke
    path = desc(p, "elev", ["sh", "tools/p.sh"], required_permission_classes=["NETWORK_READ"])
    rr, gate = register(p, path)
    ok_run = code(invoke(p, "tooling-engineer", "elev")) == "OK"
    c("W7-11.C1", rr.get("registered") and ok_run, "an approved registration runs", {"gate": gate})
    if gate:
        p.ok("orchestrator", "gate", "revoke", gate)
    e = invoke(p, "tooling-engineer", "elev")
    x("W7-11.d", code(e) != "OK", "revoking the approving gate stops the plugin at its next execution", code(e))
    # a changed permission set after approval
    path = desc(p, "w1", ["sh", "tools/p.sh"], required_permission_classes=["NETWORK_READ"])
    register(p, path)
    y = yaml.safe_load(open(path))
    y["required_permission_classes"] = ["NETWORK_READ", "NETWORK_WRITE"]
    yaml.safe_dump(y, open(path, "w"))
    r = p.ok("orchestrator", "plugins", "register", "--descriptor", path)
    x("W7-11.e", not r.get("registered"), "widening the permission set after approval needs a new approval", {"registered": r.get("registered"), "gate": r.get("human_gate")})


# ------------------------------------------------------------------------------------------------ BC-P2-40
def bc40():
    p = new_project("w7-40")
    marker = os.path.join(p.root, "w7-marker.txt")
    p.w("synthmod/__init__.py", "")
    good = f"import sys\nsys.stdin.read()\nopen({marker!r}, 'a').write('EXECUTED\\n')\nprint({EMBED_OK!r})\n"
    p.w("synthmod/__main__.py", good)
    path = desc(p, "synthmod", ["python3", "-m", "synthmod"], permissions={"network": True},
                required_permission_classes=["NETWORK_READ"])
    r, _ = register(p, path)
    entry = r.get("registry_entry") or {}
    x("W7-40.a", bool(entry.get("implementation_sha256")) and "synthmod/__main__.py" in json.dumps(entry.get("implementation_files")),
      "F4:428 a registered module-form plugin's implementation bytes are bound", {k: entry.get(k) for k in ("implementation_sha256", "implementation_files")})
    invoke(p, "tooling-engineer", "synthmod")
    n = runs(marker)
    p.w("synthmod/__main__.py", good.replace("EXECUTED", "EXECUTED SWAPPED"))
    e = invoke(p, "tooling-engineer", "synthmod")
    ok28, msg = d028(p)
    x("W7-40.b", code(e) != "OK" and runs(marker) == n and ok28 is False,
      "F4:429 swapping the module after approval fails closed and doctor reports it", {"invoke": code(e), "d028": msg[:200]})
    p.w("synthmod/__main__.py", good)
    os.makedirs(os.path.join(p.root, "synthmod/__pycache__"), exist_ok=True)
    p.w("synthmod/__pycache__/__main__.cpython-399.pyc", "planted")
    e = invoke(p, "tooling-engineer", "synthmod")
    x("W7-40.c", code(e) != "OK", "a planted byte-code file in the bound package fails closed", code(e))
    shutil.rmtree(os.path.join(p.root, "synthmod/__pycache__"))
    inj = os.path.join(os.path.dirname(p.root), "inject")
    os.makedirs(inj, exist_ok=True)
    inj_marker = os.path.join(os.path.dirname(p.root), "INJECTED")
    open(os.path.join(inj, "sitecustomize.py"), "w").write(f"open({inj_marker!r}, 'w').write('x')\n")
    e = invoke(p, "tooling-engineer", "synthmod", env={"PYTHONPATH": inj})
    x("W7-40.d", not os.path.exists(inj_marker), "code injected through the caller's PYTHONPATH never runs inside an approved plugin",
      {"invoke": code(e), "injected_ran": os.path.exists(inj_marker)})
    # inline code
    code_s = f"cat >/dev/null; echo EXECUTED >> '{marker}'; printf '%s\\n' '{EMBED_OK}'"
    path = desc(p, "inline", ["sh", "-c", code_s])
    register(p, path)
    y = yaml.safe_load(open(path))
    y["command"][2] = code_s.replace("EXECUTED", "EXECUTED EDITED")
    yaml.safe_dump(y, open(path, "w"))
    n = runs(marker)
    e = invoke(p, "tooling-engineer", "inline")
    x("W7-40.e", code(e) != "OK" and runs(marker) == n, "editing a registered plugin's inline code fails closed", code(e))
    # unregistered: machine-local reset / TOFU
    marker_plugin(p, "tools/tofu.sh", marker)
    desc(p, "tofu", ["sh", "tools/tofu.sh"])
    invoke(p, "tooling-engineer", "tofu")
    marker_plugin(p, "tools/tofu.sh", marker, "echo drifted")
    shutil.rmtree(os.path.join(p.root, ".governance-runtime", "plugins"), ignore_errors=True)
    n = runs(marker)
    e = invoke(p, "tooling-engineer", "tofu")
    x("W7-40.f", code(e) != "OK" and runs(marker) == n,
      "F4:428 a reset of machine-local state does not let drifted, never-approved bytes run", code(e))
    # fresh clone of a tampered, registered plugin
    p.w("synthmod/__main__.py", good.replace("EXECUTED", "EXECUTED TAMPERED"))
    p.git("add", "-A")
    p.git("commit", "-q", "-m", "tampered")
    q = P("w7-40-clone")
    os.makedirs(os.path.dirname(q.root), exist_ok=True)
    subprocess.run(["git", "clone", "-q", p.root, q.root], check=True, capture_output=True)
    n = runs(marker)
    e = invoke(q, "tooling-engineer", "synthmod")
    x("W7-40.g", code(e) != "OK" and runs(marker) == n, "a fresh clone on another machine does not run the tampered bytes",
      code(e))


# ------------------------------------------------------------------------------------------------ BC-P2-09 (registry)
def bc09():
    p = new_project("w7-09")
    marker = os.path.join(p.root, "w7-marker.txt")
    marker_plugin(p, "tools/net.sh", marker)
    unrelated = unrelated_gate(p)
    npath = desc(p, "netplug", ["sh", "tools/net.sh"], permissions={"network": True})
    import hashlib
    reg_p = os.path.join(p.root, "governance/generated/plugin-registry.json")
    reg = json.load(open(reg_p)) if os.path.exists(reg_p) else {"schema_version": "1.0.0", "plugins": {}}
    rel = "tools/net.sh"
    impl = hashlib.sha256((rel + ":" + hashlib.sha256(open(os.path.join(p.root, rel), "rb").read()).hexdigest() + "\n").encode()).hexdigest()
    reg["plugins"]["netplug"] = {"plugin_id": "netplug", "capability": "embed", "version": "1", "descriptor_path": "plugins/netplug.yaml",
                                 "descriptor_sha256": hashlib.sha256(open(npath, "rb").read()).hexdigest(), "implementation_sha256": impl,
                                 "implementation_files": [rel], "approved_roles": ["all"], "required_permission_classes": [],
                                 "permissions": {"network": True}, "registration_gate": unrelated, "registered_by_session": "S-owner",
                                 "registered_by_role": "human", "registered_at": "2026-09-19T00:00:00Z", "method": "gov plugins register"}
    os.makedirs(os.path.dirname(reg_p), exist_ok=True)
    json.dump(reg, open(reg_p, "w"), indent=2)
    e = invoke(p, "tooling-engineer", "netplug")
    ok28, msg = d028(p)
    sf = suite_findings(p)
    x("W7-09.a", code(e) != "OK" and runs(marker) == 0, "F4:427 a hand-written registry entry is not honoured", code(e))
    x("W7-09.b", ok28 is False and "netplug" in msg and "netplug" in sf,
      "doctor D028 and the plugin_governance suite family report the forged entry", {"d028": msg[:200], "suite_mentions": "netplug" in sf})


# ------------------------------------------------------------------------------------------------ BC-P2-41 + IP-3
def tool(p, name, **extra):
    d = {"tool_id": "TOOL-W7", "name": "w7", "type": "CLI", "capabilities": ["quantum_compile"], "version": "1.0",
         "version_pin": "1.0.0", "permissions": {"repo_write": False, "network": False}, "required_permission_classes": ["READ_REPO"],
         "license": "MIT", "reversible": True, "security_review": "passed", "cost_usd": 0, "install_command": ["true"],
         "uninstall_command": ["true"], "health_check": {"kind": "command", "command": ["true"], "expect_exit": 0}}
    d.update(extra)
    f = os.path.join(os.path.dirname(p.root), f"tool-{name}.json")
    json.dump(d, open(f, "w"))
    return f


def bc41():
    p = new_project("w7-41")
    unrelated = unrelated_gate(p)
    r = p.ok("tooling-engineer", "tools", "install", "--descriptor", tool(p, "a", security_review_record=unrelated))
    x("W7-41.a", not r.get("installed"), "F4:431 naming an unrelated record is not a security review of the tool",
      [c_["detail"] for c_ in r.get("checks", []) if c_["condition"] == "licence_and_security_satisfied"])
    p.w("spec/reports/RPT-0901.yaml", json.dumps({"id": "RPT-0901", "type": "report", "title": "security review", "status": "ACTIVE",
                                                  "state_class": "EVIDENCE", "task": "TASK-DOC", "outcome": "success"}))
    r = p.ok("tooling-engineer", "tools", "install", "--descriptor", tool(p, "b", tool_id="TOOL-W7B", security_review_record="RPT-0901"))
    x("W7-41.b", not r.get("installed"), "a hand-written report is not a governed security review of the tool",
      [c_["detail"] for c_ in r.get("checks", []) if c_["condition"] == "licence_and_security_satisfied"])
    d = tool(p, "c", tool_id="TOOL-W7C")
    r = p.ok("tooling-engineer", "tools", "install", "--descriptor", d)
    g = r.get("human_gate")
    r2 = p.ok("tooling-engineer", "tools", "install", "--descriptor", d)
    x("W7-41.c", r2.get("human_gate") == g, "re-running a pending install returns its gate instead of raising another",
      {"first": g, "second": r2.get("human_gate")})
    if g:
        human(p, g, "A")
    r3 = p.ok("tooling-engineer", "tools", "install", "--descriptor", d)
    x("W7-41.d", r3.get("installed") is True, "F3:418 a presented, owner-answered A on the installation's gate lets the same install proceed",
      {"installed": r3.get("installed"), "approval": r3.get("approval"), "new_gate": r3.get("human_gate")})
    d2 = tool(p, "d", tool_id="TOOL-W7D")
    r = p.ok("tooling-engineer", "tools", "install", "--descriptor", d2)
    g2 = r.get("human_gate")
    if g2:
        human(p, g2, "B")
    before = len([f for f in os.listdir(os.path.join(p.root, "spec/decisions")) if f.startswith("HDG-")])
    r = p.ok("tooling-engineer", "tools", "install", "--descriptor", d2)
    after = len([f for f in os.listdir(os.path.join(p.root, "spec/decisions")) if f.startswith("HDG-")])
    x("W7-41.e", not r.get("installed") and after == before, "a decline ends the installation request (no new gate)",
      {"installed": r.get("installed"), "declined": r.get("declined"), "gates_before": before, "gates_after": after})
    d3 = tool(p, "e", tool_id="TOOL-W7E", approval_gate=unrelated, human_gate=unrelated)
    r = p.ok("tooling-engineer", "tools", "install", "--descriptor", d3)
    x("W7-41.f", not r.get("installed"), "a gate answered for anything else, cited in the descriptor, never approves an installation",
      {"installed": r.get("installed"), "not_honoured": r.get("gates_not_honoured")})
    p.w("governance/project/tools/TOOL-BROKEN.yaml", json.dumps({"tool_id": "TOOL-BROKEN-001", "name": "broken", "type": "CLI",
        "capabilities": ["lint"], "status": "active", "version": "1", "approved_roles": ["all"],
        "health_check": {"kind": "command", "command": ["false"], "expect_exit": 0}, "required_permission_classes": []}))
    p.ok("orchestrator", "tools", "health")
    recs = []
    for dp, _, fs in os.walk(os.path.join(p.root, "spec")):
        for f in fs:
            if "TOOL-BROKEN-001" in open(os.path.join(dp, f), errors="ignore").read():
                recs.append(os.path.relpath(os.path.join(dp, f), p.root))
    x("W7-IP3", bool(recs), "a failing tool health check leaves a durable failure record", recs)


if __name__ == "__main__":
    os.makedirs(SCR, exist_ok=True)
    print(f"# gov {GOV}")
    for fn in (bc39, bc11, bc40, bc09, bc41):
        try:
            fn()
        except Exception as e:  # a scenario that cannot proceed is reported, not hidden
            print(f"X {fn.__name__}-SCENARIO FAIL scenario could not complete -- {type(e).__name__}: {str(e)[:400]}", flush=True)
            RESULTS.append((fn.__name__, False))
    f = [i for i, ok in RESULTS if not ok]
    print(f"SUMMARY total={len(RESULTS)} pass={len(RESULTS) - len(f)} fail={len(f)} failed={f}")
