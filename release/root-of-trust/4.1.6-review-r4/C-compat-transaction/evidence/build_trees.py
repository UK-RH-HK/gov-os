#!/usr/bin/env python3
"""AR-0007 builder. (1) A real legacy project made by the real 4.1.5 binary: init 4.1.4, gated update to 4.1.5 (legacy
update snapshot), a project `restricted` classification added after the update, and realistic prior state (task, gate,
CIT, handoff, lesson packet, registered plugin, tool descriptor, memory index, adapters). (2) The RoT-1 revision-4 layout
of `26` §2 / `08` §2 built from it and committed as a migration commit on top of the legacy history, in variants:

  R4     legacy `.governance-runtime/` ignore line REPLACED by `/.governance-runtime/*` + `!/.governance-runtime/migration`;
         legacy update snapshot quarantined to `.governance-runtime/legacy-quarantine/` (a machine that ran the first RoT-1
         transaction); a completed transaction area `trust-tx/done/<TX>` and an update snapshot `snapshots/<CI>/` present
  R4RES  same commit as R4; runtime as a second machine that pulled the migration commit: legacy update snapshot
         `.governance-runtime/update/4.1.5/` still in place, no RoT-1 transaction area
  R4APP  the ignore rule APPENDED to the legacy `.gitignore` (the legacy `.governance-runtime/` line kept) — the literal
         reading of `26` §7 step 5 "write the ignore rule" on a real legacy project; otherwise as R4
  L0     the legacy project unchanged (positive control)

Usage: build_trees.py <fresh-scratch-dir>   (prints JSON with tree paths and facts)
"""
import json, os, secrets, shutil, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c4lib import *  # noqa
import yaml

PACK = os.path.join(WT, "release", "root-of-trust", "4.1.6")


def build_base(S):
    root = os.path.join(S, "base")
    os.makedirs(root)
    fx = os.path.join(S, "fixtures")
    os.makedirs(fx, exist_ok=True)
    env = child_env(S, "base")
    G5 = BINS["4.1.5"]
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "empty")
    facts = {}
    r = gov(G5, ["init", "--source", REL["4.1.4"], "--name", "ar7", "--skip-index"], env, root, root)
    facts["init_4.1.4"] = r.get("ok")
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "legacy 4.1.4 install")
    first = gov(G5, ["update", "--apply", "--source", REL["4.1.5"]], env, root, root)
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    facts["update_gate"] = gid
    facts["gate_present"] = gov(G5, ["gate", "present", gid], env, root, root).get("ok")
    facts["decide"] = gov(G5, ["decide", gid, "--option", "A", "--by", "owner"], env, root, root).get("ok")
    ap = gov(G5, ["update", "--apply", "--approve", "--source", REL["4.1.5"]], env, root, root)
    facts["update_applied"] = result(ap).get("applied", ap.get("ok"))
    facts["legacy_update_snapshot"] = os.path.exists(os.path.join(root, ".governance-runtime/update/4.1.5/snapshot.json"))
    # project-owned strengthening added after the update
    os.makedirs(os.path.join(root, "product"), exist_ok=True)
    open(os.path.join(root, "product/restricted-plan.md"), "w").write(f"# Plan\n\n{MARK} proprietary customer terms\n")
    open(os.path.join(root, "product/readme.md"), "w").write("# Product\n\nordinary product notes\n")
    dsp = os.path.join(root, "governance/project/DATA_SENSITIVITY.yaml")
    ds = yaml.safe_load(open(dsp)) or {}
    ds.setdefault("classifications", []).append({"pattern": "product/restricted-plan.md", "class": "restricted", "reason": "customer terms"})
    yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
    ids = {}
    t = gov(G5, ["task", "create", "--class", "documentation", "--objective", "ar7 task", "--title", "ar7", "--status", "READY"], env, root, root)
    ids["TASK"] = result(t).get("id") or "TASK-0001"
    g = gov(G5, ["gate", "create", "--question", "ar7 gate?", "--fields", json.dumps({"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "impact_radius": "R1", "confidence": 0.9, "reversibility": "reversible"})], env, root, root)
    ids["GATE"] = result(g).get("id") or gid
    gov(G5, ["gate", "present", ids["GATE"]], env, root, root)
    mf = os.path.join(fx, "cit-manifest.json")
    json.dump([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\nAR7 CIT WROTE THIS\n"}], open(mf, "w"))
    ids["MANIFEST"] = mf
    c = gov(G5, ["cit", "propose", "--proposal", "ar7 change", "--trigger", "editorial", "--targets", ids["TASK"], "--manifest", mf], env, root, root)
    ids["CIT"] = result(c).get("id") or "CIT-0001"
    facts["cit_simulate"] = gov(G5, ["cit", "simulate", ids["CIT"]], env, root, root).get("ok")
    facts["cit_approve"] = gov(G5, ["cit", "approve", ids["CIT"], "--by", "orchestrator", "--method", "auto"], env, root, root).get("ok")
    h = gov(G5, ["handoff", "create", "--to-role", "backend-engineer", "--task", ids["TASK"]], env, root, root)
    ids["HANDOFF"] = result(h).get("id") or "H-0001"
    os.makedirs(os.path.join(root, "spec/lessons"), exist_ok=True)
    shutil.copy(os.path.join(WT, "fixtures/upstream-learning/lessons/L-0001.yaml"), os.path.join(root, "spec/lessons/L-0001.yaml"))
    up = gov(G5, ["upstream", "prepare", "L-0001"], env, root, root)
    pk = result(up).get("packet") or result(up).get("path")
    ids["PACKET"] = os.path.join(fx, "packet.yaml")
    if pk and os.path.exists(pk):
        shutil.copy(pk, ids["PACKET"])
    else:
        open(ids["PACKET"], "w").write("id: L-0001\n")
    os.makedirs(os.path.join(root, "tools"), exist_ok=True)
    open(os.path.join(root, "tools/probe.sh"), "w").write("#!/bin/sh\ncat >/dev/null\necho EXECUTED >> \"${AR7_MARKER:-/dev/null}\"\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"probe\",\"version\":\"1\"},\"outputs\":{\"symbols\":[],\"imports\":[],\"calls\":[],\"chunks\":[]}}'\n")
    os.chmod(os.path.join(root, "tools/probe.sh"), 0o755)
    os.makedirs(os.path.join(root, "governance/project/plugins"), exist_ok=True)
    desc = 'plugin_id: p-probe\ncapability: code_intel\ncommand: ["tools/probe.sh"]\nversion: "1"\nlanguages: ["python"]\n'
    open(os.path.join(root, "governance/project/plugins/p-probe.yaml"), "w").write(desc)
    ids["PLUGIN_DESCRIPTOR"] = os.path.join(fx, "p-probe.yaml")
    open(ids["PLUGIN_DESCRIPTOR"], "w").write(desc)
    facts["plugin_register"] = gov(G5, ["plugins", "register", "--descriptor", ids["PLUGIN_DESCRIPTOR"]], env, root, root).get("ok")
    ids["TOOL_DESCRIPTOR"] = os.path.join(fx, "tool.json")
    json.dump({"tool_id": "ar7tool", "name": "ar7tool", "type": "CLI", "capabilities": ["run_tests"], "version": "1", "version_pin": "1.0.0", "license": "MIT",
               "reversible": True, "cost_usd": 0.0, "install_command": ["sh", "-c", "echo INSTALLED >> \"${AR7_MARKER:-/dev/null}\""], "uninstall_command": ["true"],
               "required_permission_classes": ["RUN_TESTS"], "health_check": {"kind": "command_exists", "command": ["true"]}}, open(ids["TOOL_DESCRIPTOR"], "w"))
    ids["REPORT"] = os.path.join(fx, "report.json")
    json.dump({"work_completed": "ar7", "files_changed": ["README.md"], "tests": {"status": "not_applicable_with_reason", "reason": "ar7"}, "outcome": "success", "evidence": []}, open(ids["REPORT"], "w"))
    ids["RETURN"] = os.path.join(fx, "return.json")
    json.dump({"task": ids["TASK"], "status": "success", "work_completed": "x", "files_changed": [], "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [],
               "lessons": [], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "close"}, open(ids["RETURN"], "w"))
    facts["adapters_generate"] = gov(G5, ["adapters", "generate"], env, root, root).get("ok")
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "legacy project state + restricted classification")
    facts["rebuild"] = gov(G5, ["rebuild-memory"], env, root, root).get("ok")
    q = gov(G5, ["memory", "query", MARK], env, root, root)
    facts["control_restricted_hits"] = [x.get("path") for x in (result(q).get("hits") or []) if "restricted" in (x.get("path") or "")]
    facts["kernel_trust_verified"] = result(gov(G5, ["kernel", "trust"], env, root, root)).get("verified")
    facts["gitignore"] = open(os.path.join(root, ".gitignore")).read()
    facts["root_entries"] = sorted(os.listdir(root))
    facts["runtime_entries"] = sorted(os.listdir(os.path.join(root, ".governance-runtime")))
    return root, facts, ids


def ignore_rule(text, mode):
    lines = text.splitlines()
    new = ["/.governance-runtime/*", "!/.governance-runtime/migration"]
    if mode == "replace":
        out, placed = [], False
        for l in lines:
            if l.strip() in (".governance-runtime/", ".governance-runtime", "/.governance-runtime/", "/.governance-runtime"):
                if not placed:
                    out += new
                    placed = True
            else:
                out.append(l)
        if not placed:
            out += new
    else:
        out = lines + new
    return "\n".join(out) + "\n"


def to_r4(S, base, name, ignore_mode):
    dst = copy_tree(base, os.path.join(S, name))
    g = os.path.join(dst, "governance")
    t = os.path.join(g, "trust")
    for sub in ("state", "lineage", "profiles"):
        os.makedirs(os.path.join(t, sub), exist_ok=True)
    shutil.move(os.path.join(g, "kernel"), os.path.join(t, "kernel"))
    aside(S, os.path.join(t, "kernel", "KERNEL_MANIFEST.json"), name)
    legacy_lock = yaml.safe_load(open(os.path.join(g, "framework.lock")))
    aside(S, os.path.join(g, "framework.lock"), name)
    lock = json.load(open(os.path.join(PACK, "examples/rev3/framework-lock-3.0.0.example.json")))
    lock["project_trust_id"] = secrets.token_hex(16)
    lock["layout_migration"] = {"from_layout": "legacy-4.1.x", "moved": ["governance/kernel->governance/trust/kernel", "governance/project->governance/overlay", "governance/generated->governance/views"],
                                "quarantined": [".governance-runtime/update/4.1.5"], "legacy_framework": (legacy_lock or {}).get("framework")}
    open(os.path.join(t, "framework.lock"), "w").write(json.dumps(lock, sort_keys=True, separators=(",", ":")))
    open(os.path.join(t, "FORMAT"), "wb").write(FORMAT_BYTES)
    ex = os.path.join(PACK, "examples/rev2")
    shutil.copy(os.path.join(ex, "release-final.dsse.json"), os.path.join(t, "release.dsse.json"))
    shutil.copy(os.path.join(ex, "release-candidate.dsse.json"), os.path.join(t, "lineage/candidate.dsse.json"))
    for i, f in enumerate(["trust-state.1.dsse.json", "trust-state.2.dsse.json", "trust-state.3.dsse.json", "trust-policy.v1.dsse.json",
                           "certification.1-CERTIFIED.dsse.json", "verification-attestation.dsse.json"]):
        shutil.copy(os.path.join(ex, f), os.path.join(t, "state", f))
    shutil.copy(os.path.join(ex, "retrieval-profile.dsse.json"), os.path.join(t, "profiles/hashed-ngram.dsse.json"))
    shutil.move(os.path.join(g, "project"), os.path.join(g, "overlay"))
    if os.path.isdir(os.path.join(g, "generated")):
        shutil.move(os.path.join(g, "generated"), os.path.join(g, "views"))
    os.makedirs(os.path.join(g, "framework.lock"))
    open(os.path.join(g, "framework.lock", "ROT-1-TRUST-FORMAT"), "w").write(SENT + "\n")
    for p in ("kernel", "project", "generated"):
        open(os.path.join(g, p), "w").write(SENT + "\n")
    os.makedirs(os.path.join(dst, "spec/audits"), exist_ok=True)
    if os.path.isdir(os.path.join(dst, "spec/audits/GOVERNANCE-ADOPTION")):
        shutil.move(os.path.join(dst, "spec/audits/GOVERNANCE-ADOPTION"), os.path.join(dst, "spec/audits/ADOPTION"))
    open(os.path.join(dst, "spec/audits/GOVERNANCE-ADOPTION"), "w").write(SENT + "\n")
    rt = os.path.join(dst, ".governance-runtime")
    q = os.path.join(rt, "legacy-quarantine")
    os.makedirs(q, exist_ok=True)
    if os.path.isdir(os.path.join(rt, "migration")):
        shutil.move(os.path.join(rt, "migration"), os.path.join(q, "migration"))
    open(os.path.join(rt, "migration"), "w").write(SENT + "\n")
    if os.path.isdir(os.path.join(rt, "update")):
        shutil.move(os.path.join(rt, "update"), os.path.join(q, "update"))
    tx = os.path.join(rt, "trust-tx")
    os.makedirs(os.path.join(tx, "done", "TX-0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"), exist_ok=True)
    open(os.path.join(tx, "LOCK"), "w").write("")
    json.dump({"operation": "update", "phase": "verified", "aro_ci": "sha256:aa", "previous_ci": "sha256:bb"},
              open(os.path.join(tx, "done", "TX-0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f", "journal.json"), "w"))
    os.makedirs(os.path.join(rt, "snapshots", "ci-previous"), exist_ok=True)
    json.dump({"kind": "rot1-update-snapshot", "ci": "sha256:bb"}, open(os.path.join(rt, "snapshots", "ci-previous", "snapshot.json"), "w"))
    gi = os.path.join(dst, ".gitignore")
    old_gi = open(gi).read() if os.path.exists(gi) else ""
    new_gi = ignore_rule(old_gi, ignore_mode)
    with open(gi, "w") as f:
        f.write(new_gi)
    git(dst, "add", "-A")
    git(dst, "add", "-f", ".governance-runtime/migration")
    git(dst, "commit", "-q", "-m", f"rot-1 revision-4 layout migration ({name})")
    facts = {"gitignore": open(gi).read(), "tracked_but_ignored": git(dst, "ls-files", "-ci", "--exclude-standard").stdout.split(),
             "tracked_runtime": [x for x in git(dst, "ls-files", ".governance-runtime").stdout.split()],
             "state": installation_state(dst), "governance_entries": sorted(os.listdir(g)), "head": git(dst, "rev-parse", "HEAD").stdout.strip(),
             "pre_migration": git(dst, "rev-parse", "HEAD~1").stdout.strip()}
    return dst, facts


def make_r4res(S, r4):
    dst = copy_tree(r4, os.path.join(S, "R4RES"))
    rt = os.path.join(dst, ".governance-runtime")
    shutil.move(os.path.join(rt, "legacy-quarantine", "update"), os.path.join(rt, "update"))
    aside(S, os.path.join(rt, "trust-tx"), "R4RES")
    aside(S, os.path.join(rt, "snapshots"), "R4RES")
    return dst, {"state": installation_state(dst), "legacy_update_snapshot": os.path.exists(os.path.join(rt, "update/4.1.5/snapshot.json"))}


if __name__ == "__main__":
    S = os.path.abspath(sys.argv[1])
    os.makedirs(S, exist_ok=False)
    base, bfacts, ids = build_base(S)
    r4, f4 = to_r4(S, base, "R4", "replace")
    r4res, fres = make_r4res(S, r4)
    r4app, fapp = to_r4(S, base, "R4APP", "append")
    out = {"scratch": S, "trees": {"L0": base, "R4": r4, "R4RES": r4res, "R4APP": r4app}, "ids": ids,
           "base_facts": bfacts, "R4": f4, "R4RES": fres, "R4APP": fapp}
    json.dump(out, open(os.path.join(S, "trees.json"), "w"), indent=1)
    print(scrub(json.dumps(out, indent=1, default=str), S))
