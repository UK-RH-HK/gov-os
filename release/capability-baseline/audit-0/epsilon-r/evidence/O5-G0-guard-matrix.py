#!/usr/bin/env python3
"""O5 tier G0 "Guard — every privileged/mutating command" (Contract v3 line 793).

For every mutating `gov` command: set up objects it needs, then run it
  (1) with FREEZE_WRITES active, (2) with PAUSE active, (3) as role independent-auditor (L0), (4) as research-agent (L1),
and record the error code and whether governed state actually changed (hash of spec/, governance/, framework.json and
.governance-runtime/ excluding the telemetry log, which every invocation appends to).

Run from the worktree root:  python3 release/capability-baseline/audit-0/epsilon-r/evidence/O5-G0-guard-matrix.py
Env: SCRATCH (work dir), GOV (binary), WT (worktree).
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile, yaml

EVD = os.path.dirname(os.path.abspath(__file__))
WT = os.environ.get("WT") or os.path.abspath(os.path.join(EVD, "../../../../.."))
GOV = os.environ.get("GOV") or os.path.join(WT, "target/release/gov")
SCRATCH = os.environ.get("SCRATCH") or tempfile.mkdtemp()
ENV = dict(os.environ, GOV_CANONICAL_ROOT=WT, PATH=os.path.expanduser("~/.cargo/bin") + ":" + os.environ["PATH"])
for k in ("GOV_SESSION", "GOV_ROLE", "GOV_MACHINE_STATE_DIR"):
    ENV.pop(k, None)


def gov(root, *args, role="orchestrator", session="S-g0"):
    e = dict(ENV, XDG_STATE_HOME=root + ".machine")
    p = subprocess.run([GOV, "--json", "--root", root, "--session", session, "--role", role, *args],
                       capture_output=True, text=True, env=e, cwd=root)
    try:
        d = json.loads(p.stdout)
    except Exception:
        d = {"ok": False, "error": {"code": "NON_JSON", "message": (p.stdout + p.stderr)[:200]}}
    return p.returncode, d


def state_hash(root):
    h = hashlib.sha256()
    for top in ("spec", "governance", "framework.json", ".governance-runtime", "docs", "src"):
        base = os.path.join(root, top)
        paths = []
        if os.path.isfile(base):
            paths = [base]
        else:
            for d, _, fs in os.walk(base):
                for f in fs:
                    paths.append(os.path.join(d, f))
        for p in sorted(paths):
            rel = os.path.relpath(p, root)
            if rel.startswith(".governance-runtime/telemetry/"):
                continue
            h.update(rel.encode())
            with open(p, "rb") as fh:
                h.update(hashlib.sha256(fh.read()).digest())
    return h.hexdigest()


def git(root, *a):
    subprocess.run(["git", *a], cwd=root, capture_output=True)


def wy(root, rel, d):
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    yaml.safe_dump(d, open(p, "w"), sort_keys=False)


def fresh(name):
    """byte copy of the HEALTHY baseline created by lib.sh (SCRATCH/base)"""
    src = os.path.join(SCRATCH, "base")
    if not os.path.isdir(src):
        subprocess.run(["bash", "-c", f'source "{EVD}/lib.sh"; base_project >/dev/null'], env=dict(ENV, SCRATCH=SCRATCH))
    dst = os.path.join(SCRATCH, name)
    for d in (dst, dst + ".machine"):
        shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(src, dst, symlinks=True)
    if os.path.isdir(src + ".machine"):
        shutil.copytree(src + ".machine", dst + ".machine", symlinks=True)
    return dst


def setup(root):
    """objects the commands need; returns ids"""
    ids = {}
    readiness = {x["id"]: "PRESENT" for x in yaml.safe_load(open(os.path.join(WT, "framework/taxonomy/READINESS_DIMENSIONS.yaml")))["dimensions"]}
    readiness["scenarios"] = "MISSING"
    wy(root, "spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "f", "status": "ACTIVE", "readiness": readiness})
    wy(root, "spec/lessons/L-0001.yaml", {"id": "L-0001", "type": "lesson", "title": "framework lesson", "status": "ACTIVE", "state_class": "EVIDENCE",
                                           "scope": "FRAMEWORK", "lifecycle": "corroborated", "category": "memory", "problem_statement": "index lagged",
                                           "generic_failure_mode": "advisory freshness", "impact": "stale retrieval", "evidence_strength": "high",
                                           "suggested_change": "enforce", "sources": ["RPT-9"]})
    for n in ("T1", "T2", "T3"):
        rc, d = gov(root, "task", "create", "--class", "documentation", "--objective", f"g0 {n}", "--allowed", "docs/**", "--status", "READY")
        ids[n] = d["result"]["id"]
    rc, d = gov(root, "gate", "create", "--question", "probe gate?", "--fields",
                json.dumps({"options": [{"id": "A", "description": "a"}, {"id": "B", "description": "b"}], "why_now": "probe", "impact": "none", "reversibility": "reversible", "recommendation": "A", "confidence": 0.5}))
    ids["G1"] = (d.get("result") or {}).get("id")
    rc, d = gov(root, "gate", "create", "--question", "probe gate 2?", "--fields",
                json.dumps({"options": [{"id": "A", "description": "a"}, {"id": "B", "description": "b"}], "why_now": "probe", "impact": "none", "reversibility": "reversible", "recommendation": "A", "confidence": 0.5}))
    ids["G2"] = (d.get("result") or {}).get("id")
    rc, d = gov(root, "cit", "propose", "--proposal", "edit docs note", "--targets", "docs/note.md")
    ids["C1"] = (d.get("result") or {}).get("id")
    rc, d = gov(root, "handoff", "create", "--to-role", "backend-engineer", "--task", ids["T3"])
    ids["H1"] = (d.get("result") or {}).get("id")
    gov(root, "gate", "present", ids["G1"])
    gov(root, "task", "claim", ids["T1"])
    os.makedirs(os.path.join(root, "docs"), exist_ok=True)
    json.dump({"work_completed": "x", "tests": {"status": "not_applicable_with_reason"}, "files_changed": [], "evidence": []}, open(os.path.join(SCRATCH, "g0-report.json"), "w"))
    json.dump({"task": ids["T3"], "status": "success", "work_completed": "x", "files_changed": [], "evidence": [], "tests": {"status": "passed"},
               "discoveries": [], "risks": [], "lessons": ["a lesson"], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "none"},
              open(os.path.join(SCRATCH, "g0-return.json"), "w"))
    json.dump({"model": "m", "provider": "p", "task_class": "documentation", "reasoning_effort": "low", "cost": 0.01, "latency_ms": 10,
               "pass": True, "repair_count": 0, "reviewer_findings": 0}, open(os.path.join(SCRATCH, "g0-route.json"), "w"))
    yaml.safe_dump({"id": "TOOL-PROBE-001", "name": "probe", "type": "cli", "version": "1", "licence": "MIT"}, open(os.path.join(SCRATCH, "g0-tool.yaml"), "w"))
    yaml.safe_dump({"plugin_id": "probe-plugin", "capability": "embed", "version": "1", "protocol": "gov-capability/1", "command": ["true"]}, open(os.path.join(SCRATCH, "g0-plugin.yaml"), "w"))
    os.makedirs(os.path.join(SCRATCH, "g0-canon", "lessons", "inbox"), exist_ok=True)
    git(root, "add", "-A"); git(root, "commit", "-qm", "g0 setup")
    gov(root, "rebuild-memory", "--incremental")
    return ids


def commands(ids):
    S = SCRATCH
    return [
        ("task create", ["task", "create", "--class", "documentation", "--objective", "new", "--allowed", "docs/**"]),
        ("task status", ["task", "status", ids["T2"], "BLOCKED"]),
        ("task claim", ["task", "claim", ids["T2"]]),
        ("task release", ["task", "release", ids["T1"]]),
        ("task close", ["task", "close", ids["T1"], "--report", f"{S}/g0-report.json"]),
        ("task replan", ["task", "replan"]),
        ("continue --claim", ["continue", "--claim"]),
        ("cit propose", ["cit", "propose", "--proposal", "another", "--targets", "docs/x.md"]),
        ("cit simulate", ["cit", "simulate", ids["C1"] or "CIT-0001"]),
        ("cit approve", ["cit", "approve", ids["C1"] or "CIT-0001", "--by", "human"]),
        ("cit reject", ["cit", "reject", ids["C1"] or "CIT-0001", "--reason", "x"]),
        ("cit execute", ["cit", "execute", ids["C1"] or "CIT-0001"]),
        ("cit rollback", ["cit", "rollback", ids["C1"] or "CIT-0001"]),
        ("checkpoint create", ["checkpoint", "create", "--next-action", "x"]),
        ("checkpoint watchdog", ["checkpoint", "watchdog", "--utilisation", "0.99"]),
        ("context compile", ["context", "compile", ids["T2"]]),
        ("handoff create", ["handoff", "create", "--to-role", "backend-engineer", "--task", ids["T2"]]),
        ("handoff return", ["handoff", "return", ids["H1"] or "HO-0001", "--file", f"{S}/g0-return.json"]),
        ("gate create", ["gate", "create", "--question", "q?"]),
        ("gate present", ["gate", "present", ids["G1"] or "HG-0001"]),
        ("decide", ["decide", ids["G1"] or "HG-0001", "--option", "A", "--by", "human"]),
        ("gate revoke", ["gate", "revoke", ids["G2"] or "HG-0002", "--reason", "x"]),
        ("readiness plan", ["readiness", "plan", "F-0001"]),
        ("route --record", ["route", "--record", f"{S}/g0-route.json"]),
        ("telemetry emit", ["telemetry", "emit", "--name", "probe.event"]),
        ("audit (persist)", ["audit"]),
        ("verify governance", ["verify", "governance"]),
        ("verify product", ["verify", "product"]),
        ("rebuild-memory", ["rebuild-memory"]),
        ("memory rebuild", ["memory", "rebuild"]),
        ("memory heldout-starter --force", ["memory", "heldout-starter", "--force"]),
        ("memory benchmark --record", ["memory", "benchmark", "--record"]),
        ("adapters generate", ["adapters", "generate"]),
        ("tools registry", ["tools", "registry"]),
        ("tools install", ["tools", "install", "--descriptor", f"{S}/g0-tool.yaml"]),
        ("plugins register", ["plugins", "register", "--descriptor", f"{S}/g0-plugin.yaml"]),
        ("upstream prepare", ["upstream", "prepare", "L-0001"]),
        ("upstream submit", ["upstream", "submit", "PKT-0001", "--destination", f"{S}/g0-canon/lessons/inbox", "--approved-by", "human"]),
        ("kernel override", ["kernel", "override", "--reason", "x"]),
        ("kernel reinstall", ["kernel", "reinstall"]),
        ("update --apply", ["update", "--apply"]),
        ("update --rollback", ["update", "--rollback"]),
        ("recover", ["recover"]),
        ("claims sweep", ["claims", "sweep"]),
        ("adopt baseline", ["adopt", "baseline"]),
        ("init --force", ["init", "--force"]),
        ("pause", ["pause", "--reason", "x"]),
        ("freeze-writes", ["freeze-writes", "--reason", "x"]),
    ]


def run_mode(mode):
    rows = []
    for label, args in commands({"T1": "TASK-0001", "T2": "TASK-0002", "T3": "TASK-0003", "G1": None, "G2": None, "C1": None, "H1": None}):
        root = fresh(f"g0-{mode}")
        ids = setup(root)
        args = [a for a in dict(commands(ids))[label]]
        role = "orchestrator"
        if mode == "freeze":
            gov(root, "freeze-writes", "--reason", "g0 probe")
        elif mode == "pause":
            gov(root, "pause", "--reason", "g0 probe")
        elif mode == "L0":
            role = "independent-auditor"
        elif mode == "L1":
            role = "research-agent"
        before = state_hash(root)
        if label == "upstream submit":  # needs a prepared packet (prepared before the control state is set)
            pass
        rc, d = gov(root, *args, role=role)
        after = state_hash(root)
        code = None if d.get("ok") else (d.get("error") or {}).get("code")
        rows.append({"command": label, "exit": rc, "ok": bool(d.get("ok")), "error": code, "state_changed": before != after})
    return rows


def run_mode_submit(mode):
    """upstream submit needs a packet prepared while RUNNING"""
    root = fresh(f"g0-{mode}-sub"); setup(root)
    gov(root, "upstream", "prepare", "L-0001")
    role = "orchestrator"
    if mode == "freeze": gov(root, "freeze-writes", "--reason", "p")
    if mode == "pause": gov(root, "pause", "--reason", "p")
    if mode == "L0": role = "independent-auditor"
    if mode == "L1": role = "research-agent"
    before = state_hash(root)
    rc, d = gov(root, "upstream", "submit", "PKT-0001", "--destination", f"{SCRATCH}/g0-canon/lessons/inbox", "--approved-by", "human", role=role)
    return {"command": "upstream submit (prepared first)", "exit": rc, "ok": bool(d.get("ok")), "error": None if d.get("ok") else (d.get("error") or {}).get("code"), "state_changed": before != state_hash(root)}


if __name__ == "__main__":
    print(f"# GOV={GOV}\n# SCRATCH={SCRATCH}")
    table = {}
    for mode in ("baseline", "freeze", "pause", "L0", "L1"):
        rows = run_mode(mode) + [run_mode_submit(mode)]
        for r in rows:
            table.setdefault(r["command"], {})[mode] = r
    hdr = f"{'command':34} | {'RUNNING/orchestrator':26} | {'FREEZE_WRITES':26} | {'PAUSED':26} | {'role L0 independent-auditor':30} | {'role L1 research-agent':26}"
    print(hdr); print("-" * len(hdr))
    def cell(r):
        if r is None: return "-"
        return (("ok" if r["ok"] else (r["error"] or "ERR")) + (" [MUTATED]" if r["state_changed"] else ""))[:30]
    unguarded_freeze, unguarded_pause, unguarded_l0 = [], [], []
    for cmd, m in table.items():
        print(f"{cmd:34} | {cell(m.get('baseline')):26} | {cell(m.get('freeze')):26} | {cell(m.get('pause')):26} | {cell(m.get('L0')):30} | {cell(m.get('L1')):26}")
        if m.get("freeze", {}).get("state_changed"): unguarded_freeze.append(cmd)
        if m.get("pause", {}).get("state_changed"): unguarded_pause.append(cmd)
        if m.get("L0", {}).get("state_changed"): unguarded_l0.append(cmd)
    print("\nstate mutated while FREEZE_WRITES active:", unguarded_freeze)
    print("state mutated while PAUSED:", unguarded_pause)
    print("state mutated by role L0 independent-auditor:", unguarded_l0)
    json.dump(table, open(os.path.join(SCRATCH, "g0-matrix.json"), "w"), indent=1)
