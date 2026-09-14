#!/usr/bin/env python3
"""AR-0013 builder: a real legacy project made by the real 4.1.5 binary, and the RoT-1 revision-5 layout built from it.

Attribution: the legacy base-project recipe (init 4.1.4 -> gated update 4.1.5 leaving the legacy update snapshot ->
restricted classification added after the update -> task, gate, CIT, handoff, lesson packet, plugin, tool descriptor,
adapters, memory index) follows review r4 C `build_trees.py` (AR-0007); the code is re-written. The revision-5 layout is
built from the pack text at cdb4e14: `26` §2, `08` §2–§3 (lock 3.0.0 recording the release content set and the registration
digest), `18` §9.1 (registration.dsse.json in the trust entry set), `26` §8 (.gitignore surgery), `26` §7 (quarantine).

Trees:
  L0        the legacy project (control)
  R5        migrated machine: legacy .gitignore line removed by the surgery, child-glob rules written; legacy update
            snapshot quarantined; trust-tx/done/<TX> and snapshots/<CI> present
  R5RES     second machine on the same commit: legacy update snapshot still at .governance-runtime/update/4.1.5/, no trust-tx
  R5NOSURG  as R5 but the rules appended to the legacy .gitignore (no surgery) — negative control for RV4-M6
  R5V       R5 plus a committed legacy 4.1.5 sub-project at vendor/legacypkg (monorepo with a legacy component)

Usage: build5.py <fresh-dir>  (writes <fresh-dir>/trees.json)
"""
import base64, json, os, re, secrets, shutil, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c5lib as L  # noqa
import yaml

MARK2 = "AR0013CUSTOMERMARKER"


def envfor(S, tag):
    return L.child_env(os.path.join(S, "homes", tag), os.path.join(S, "caches", tag))


def build_base(S):
    root = os.path.join(S, "L0")
    os.makedirs(root)
    fx = os.path.join(S, "fixtures")
    os.makedirs(fx, exist_ok=True)
    env = envfor(S, "base")
    G = L.BINS["4.1.5"]
    L.git(root, "init", "-q")
    L.git(root, "commit", "-q", "--allow-empty", "-m", "empty")
    f = {}
    f["init_4.1.4"] = L.gov(G, ["init", "--source", L.REL["4.1.4"], "--name", "ar13", "--skip-index"], env, root, root).get("ok")
    L.git(root, "add", "-A"); L.git(root, "commit", "-q", "-m", "legacy 4.1.4 install")
    first = L.gov(G, ["update", "--apply", "--source", L.REL["4.1.5"]], env, root, root)
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    f["update_gate"] = gid
    L.gov(G, ["gate", "present", gid], env, root, root)
    f["decide"] = L.gov(G, ["decide", gid, "--option", "A", "--by", "owner"], env, root, root).get("ok")
    ap = L.gov(G, ["update", "--apply", "--approve", "--source", L.REL["4.1.5"]], env, root, root)
    f["update_applied"] = L.result(ap).get("applied", ap.get("ok"))
    f["legacy_update_snapshot"] = os.path.isdir(os.path.join(root, ".governance-runtime/update/4.1.5"))
    for p, t in (("product/restricted-plan.md", f"# Plan\n\n{L.MARK} proprietary customer terms\n"),
                 ("product/customers/acme.md", f"# ACME\n\n{MARK2} contract value and contacts\n"),
                 ("product/readme.md", "# Product\n\nordinary notes\n"), ("docs/guide.md", "# Guide\n\nordinary docs\n")):
        os.makedirs(os.path.dirname(os.path.join(root, p)), exist_ok=True)
        open(os.path.join(root, p), "w").write(t)
    dsp = os.path.join(root, "governance/project/DATA_SENSITIVITY.yaml")
    ds = yaml.safe_load(open(dsp)) or {}
    ds.setdefault("classifications", []).extend([
        {"pattern": "product/restricted-plan.md", "class": "restricted", "reason": "customer terms"},
        {"pattern": "product/customers/**", "class": "restricted", "reason": "customer records"}])
    yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
    ids = {}
    t = L.gov(G, ["task", "create", "--class", "documentation", "--objective", "ar13 task", "--title", "ar13", "--status", "READY"], env, root, root)
    ids["TASK"] = L.result(t).get("id") or "TASK-0001"
    g = L.gov(G, ["gate", "create", "--question", "ar13 gate?", "--fields", json.dumps({"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "impact_radius": "R1", "confidence": 0.9, "reversibility": "reversible"})], env, root, root)
    ids["GATE"] = L.result(g).get("id") or gid
    L.gov(G, ["gate", "present", ids["GATE"]], env, root, root)
    mf = os.path.join(fx, "cit-manifest.json")
    json.dump([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\nAR13 CIT WROTE THIS\n"}], open(mf, "w"))
    ids["MANIFEST"] = mf
    c = L.gov(G, ["cit", "propose", "--proposal", "ar13 change", "--trigger", "editorial", "--targets", ids["TASK"], "--manifest", mf], env, root, root)
    ids["CIT"] = L.result(c).get("id") or "CIT-0001"
    f["cit_simulate"] = L.gov(G, ["cit", "simulate", ids["CIT"]], env, root, root).get("ok")
    f["cit_approve"] = L.gov(G, ["cit", "approve", ids["CIT"], "--by", "orchestrator", "--method", "auto"], env, root, root).get("ok")
    h = L.gov(G, ["handoff", "create", "--to-role", "backend-engineer", "--task", ids["TASK"]], env, root, root)
    ids["HANDOFF"] = L.result(h).get("id") or "H-0001"
    os.makedirs(os.path.join(root, "spec/lessons"), exist_ok=True)
    shutil.copy(os.path.join(L.WT, "fixtures/upstream-learning/lessons/L-0001.yaml"), os.path.join(root, "spec/lessons/L-0001.yaml"))
    up = L.gov(G, ["upstream", "prepare", "L-0001"], env, root, root)
    pk = L.result(up).get("packet") or L.result(up).get("path")
    ids["PACKET"] = os.path.join(fx, "packet.yaml")
    if pk and os.path.exists(pk):
        shutil.copy(pk, ids["PACKET"])
    else:
        open(ids["PACKET"], "w").write("id: L-0001\n")
    os.makedirs(os.path.join(root, "tools"), exist_ok=True)
    open(os.path.join(root, "tools/probe.sh"), "w").write("#!/bin/sh\ncat >/dev/null\necho EXECUTED >> \"${AR13_MARKER:-/dev/null}\"\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"probe\",\"version\":\"1\"},\"outputs\":{\"symbols\":[],\"imports\":[],\"calls\":[],\"chunks\":[]}}'\n")
    os.chmod(os.path.join(root, "tools/probe.sh"), 0o755)
    os.makedirs(os.path.join(root, "governance/project/plugins"), exist_ok=True)
    desc = 'plugin_id: p-probe\ncapability: code_intel\ncommand: ["tools/probe.sh"]\nversion: "1"\nlanguages: ["python"]\n'
    open(os.path.join(root, "governance/project/plugins/p-probe.yaml"), "w").write(desc)
    ids["PLUGIN_DESCRIPTOR"] = os.path.join(fx, "p-probe.yaml")
    open(ids["PLUGIN_DESCRIPTOR"], "w").write(desc)
    f["plugin_register"] = L.gov(G, ["plugins", "register", "--descriptor", ids["PLUGIN_DESCRIPTOR"]], env, root, root).get("ok")
    ids["TOOL_DESCRIPTOR"] = os.path.join(fx, "tool.json")
    json.dump({"tool_id": "ar13tool", "name": "ar13tool", "type": "CLI", "capabilities": ["run_tests"], "version": "1", "version_pin": "1.0.0", "license": "MIT",
               "reversible": True, "cost_usd": 0.0, "install_command": ["sh", "-c", "echo INSTALLED >> \"${AR13_MARKER:-/dev/null}\""], "uninstall_command": ["true"],
               "required_permission_classes": ["RUN_TESTS"], "health_check": {"kind": "command_exists", "command": ["true"]}}, open(ids["TOOL_DESCRIPTOR"], "w"))
    ids["REPORT"] = os.path.join(fx, "report.json")
    json.dump({"work_completed": "ar13", "files_changed": ["README.md"], "tests": {"status": "not_applicable_with_reason", "reason": "ar13"}, "outcome": "success", "evidence": []}, open(ids["REPORT"], "w"))
    ids["RETURN"] = os.path.join(fx, "return.json")
    json.dump({"task": ids["TASK"], "status": "success", "work_completed": "x", "files_changed": [], "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [],
               "lessons": [], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "close"}, open(ids["RETURN"], "w"))
    f["adapters_generate"] = L.gov(G, ["adapters", "generate"], env, root, root).get("ok")
    L.git(root, "add", "-A"); L.git(root, "commit", "-q", "-m", "legacy project state + restricted classifications")
    f["rebuild"] = L.gov(G, ["rebuild-memory"], env, root, root).get("ok")
    for m in (L.MARK, MARK2):
        q = L.gov(G, ["memory", "query", m], env, root, root)
        f["control_hits_" + m] = [x.get("path") for x in (L.result(q).get("hits") or [])]
    f["kernel_trust_verified"] = L.result(L.gov(G, ["kernel", "trust"], env, root, root)).get("verified")
    f["gitignore"] = open(os.path.join(root, ".gitignore")).read()
    f["root_entries"] = sorted(os.listdir(root))
    f["runtime_entries"] = sorted(os.listdir(os.path.join(root, ".governance-runtime")))
    return root, f, ids


LEGACY_DIR_IGNORE = re.compile(r"^/?\.governance-runtime/?$")


def gitignore_surgery(text):
    """`26` §8 RV4-M6 as written: remove every pre-existing `.governance-runtime/` directory-ignore line (with or without
    leading or trailing slash), preserve all other lines, write the child-glob rules once; idempotent."""
    lines = text.splitlines()
    out = [l for l in lines if not LEGACY_DIR_IGNORE.match(l.strip())]
    for r in ("/.governance-runtime/*", "!/.governance-runtime/migration"):
        if r not in out:
            out.append(r)
    return "\n".join(out) + "\n"


def dsse(payload_obj, ptype):
    pb = json.dumps(payload_obj, sort_keys=True, separators=(",", ":")).encode()
    return {"payloadType": ptype, "payload": base64.b64encode(pb).decode(), "signatures": [{"keyid": "ed25519:" + "0" * 64, "sig": base64.b64encode(b"unsigned-review-fixture").decode()}]}, L.sha(pb)


def to_r5(S, base, name, surgery=True, quarantine=True, txarea=True):
    dst = L.copy_tree(base, os.path.join(S, name))
    aside = os.path.join(S, "aside", name)
    os.makedirs(aside, exist_ok=True)
    g = os.path.join(dst, "governance")
    t = os.path.join(g, "trust")
    for sub in ("state", "lineage", "profiles", "root"):
        os.makedirs(os.path.join(t, sub), exist_ok=True)
    shutil.move(os.path.join(g, "kernel"), os.path.join(t, "kernel"))
    shutil.move(os.path.join(t, "kernel", "KERNEL_MANIFEST.json"), os.path.join(aside, "KERNEL_MANIFEST.json"))
    shutil.move(os.path.join(g, "framework.lock"), os.path.join(aside, "legacy-framework.lock"))
    rcs = {k: v[1] for k, v in L.kernel_file_map(os.path.join(t, "kernel")).items() if v[0] == "file"}
    ex = os.path.join(L.PACK, "examples")
    reg_payload = json.load(open(os.path.join(ex, "rev5/release-registration.payload.example.json")))
    reg_env, reg_digest = dsse(reg_payload, "application/vnd.governance-os.release-registration.v1+json")
    json.dump(reg_env, open(os.path.join(t, "registration.dsse.json"), "w"))
    lock = json.load(open(os.path.join(ex, "rev3/framework-lock-3.0.0.example.json")))
    lock["project_trust_id"] = secrets.token_hex(16)
    lock.setdefault("kernel", {})["files"] = {k: "sha256:" + v for k, v in sorted(rcs.items())}
    lock["registration_digest"] = "sha256:" + reg_digest
    lock["layout_migration"] = {"from_layout": "legacy-4.1.x", "moved": ["governance/kernel->governance/trust/kernel", "governance/project->governance/overlay", "governance/generated->governance/views"],
                                "quarantined": [".governance-runtime/update/4.1.5"] if quarantine else []}
    open(os.path.join(t, "framework.lock"), "w").write(json.dumps(lock, sort_keys=True, separators=(",", ":")))
    open(os.path.join(t, "FORMAT"), "wb").write(L.FORMAT_BYTES)
    open(os.path.join(t, ".gitattributes"), "wb").write(L.GITATTR_BYTES)
    r2 = os.path.join(ex, "rev2")
    shutil.copy(os.path.join(r2, "release-final.dsse.json"), os.path.join(t, "release.dsse.json"))
    shutil.copy(os.path.join(r2, "release-candidate.dsse.json"), os.path.join(t, "lineage/candidate.dsse.json"))
    for fn in ("trust-state.1.dsse.json", "trust-state.2.dsse.json", "trust-state.3.dsse.json", "trust-policy.v1.dsse.json",
               "certification.1-CERTIFIED.dsse.json", "verification-attestation.dsse.json", "revocation.1.dsse.json"):
        shutil.copy(os.path.join(r2, fn), os.path.join(t, "state", fn))
    shutil.copy(os.path.join(r2, "trust-root.v1.dsse.json"), os.path.join(t, "root", "2.dsse.json"))
    shutil.copy(os.path.join(r2, "retrieval-profile.dsse.json"), os.path.join(t, "profiles", "hashed-ngram.dsse.json"))
    shutil.move(os.path.join(g, "project"), os.path.join(g, "overlay"))
    if os.path.isdir(os.path.join(g, "generated")):
        shutil.move(os.path.join(g, "generated"), os.path.join(g, "views"))
    os.makedirs(os.path.join(g, "framework.lock"))
    open(os.path.join(g, "framework.lock", "ROT-1-TRUST-FORMAT"), "w").write(L.SENT + "\n")
    for p in ("kernel", "project", "generated"):
        open(os.path.join(g, p), "w").write(L.SENT + "\n")
    os.makedirs(os.path.join(dst, "spec/audits"), exist_ok=True)
    if os.path.isdir(os.path.join(dst, "spec/audits/GOVERNANCE-ADOPTION")):
        shutil.move(os.path.join(dst, "spec/audits/GOVERNANCE-ADOPTION"), os.path.join(dst, "spec/audits/ADOPTION"))
    open(os.path.join(dst, "spec/audits/GOVERNANCE-ADOPTION"), "w").write(L.SENT + "\n")
    rt = os.path.join(dst, ".governance-runtime")
    q = os.path.join(rt, "legacy-quarantine")
    if os.path.isdir(os.path.join(rt, "migration")):
        os.makedirs(q, exist_ok=True)
        shutil.move(os.path.join(rt, "migration"), os.path.join(q, "migration"))
    open(os.path.join(rt, "migration"), "w").write(L.SENT + "\n")
    if quarantine and os.path.isdir(os.path.join(rt, "update")):
        os.makedirs(q, exist_ok=True)
        shutil.move(os.path.join(rt, "update"), os.path.join(q, "update"))
    TX = "TX-" + "0f" * 16
    if txarea:
        os.makedirs(os.path.join(rt, "trust-tx", "done", TX), exist_ok=True)
        open(os.path.join(rt, "trust-tx", "LOCK"), "w").write("")
        json.dump({"operation": "update", "phase": "verified", "aro_ci": "sha256:" + "a" * 64, "previous_ci": "sha256:" + "b" * 64},
                  open(os.path.join(rt, "trust-tx", "done", TX, "journal.json"), "w"))
        os.makedirs(os.path.join(rt, "snapshots", "ci-previous"), exist_ok=True)
        json.dump({"kind": "rot1-update-snapshot", "ci": "sha256:" + "b" * 64}, open(os.path.join(rt, "snapshots", "ci-previous", "snapshot.json"), "w"))
    gi = os.path.join(dst, ".gitignore")
    old = open(gi).read() if os.path.exists(gi) else ""
    new = gitignore_surgery(old) if surgery else (old if old.endswith("\n") or not old else old + "\n") + "/.governance-runtime/*\n!/.governance-runtime/migration\n"
    open(gi, "w").write(new)
    L.git(dst, "add", "-A")
    L.git(dst, "add", "-f", ".governance-runtime/migration")
    L.git(dst, "commit", "-q", "-m", f"rot-1 revision-5 layout migration ({name})")
    facts = {"gitignore": open(gi).read(), "surgery_idempotent": gitignore_surgery(open(gi).read()) == open(gi).read() if surgery else None,
             "tracked_but_ignored": L.git(dst, "ls-files", "-ci", "--exclude-standard").stdout.split(),
             "tracked_runtime": L.git(dst, "ls-files", ".governance-runtime").stdout.split(),
             "state_r5": L.state_r5(dst), "head": L.git(dst, "rev-parse", "HEAD").stdout.strip(),
             "pre_migration": L.git(dst, "rev-parse", "HEAD~1").stdout.strip(), "governance_entries": sorted(os.listdir(g)),
             "kernel_tampered": L.kernel_tampered(dst, rcs), "registration_digest": reg_digest}
    return dst, facts, rcs


def make_r5res(S, r5):
    dst = L.copy_tree(r5, os.path.join(S, "R5RES"))
    rt = os.path.join(dst, ".governance-runtime")
    aside = os.path.join(S, "aside", "R5RES")
    os.makedirs(aside, exist_ok=True)
    shutil.move(os.path.join(rt, "legacy-quarantine", "update"), os.path.join(rt, "update"))
    shutil.move(os.path.join(rt, "trust-tx"), os.path.join(aside, "trust-tx"))
    shutil.move(os.path.join(rt, "snapshots"), os.path.join(aside, "snapshots"))
    return dst, {"state_r5": L.state_r5(dst), "legacy_update_snapshot": os.path.isdir(os.path.join(rt, "update/4.1.5"))}


def make_r5v(S, r5):
    dst = L.copy_tree(r5, os.path.join(S, "R5V"))
    sub = os.path.join(dst, "vendor", "legacypkg")
    os.makedirs(sub)
    open(os.path.join(sub, "README.md"), "w").write("# legacypkg\n")
    env = envfor(S, "r5v")
    r = L.gov(L.BINS["4.1.5"], ["init", "--source", L.REL["4.1.5"], "--name", "legacypkg", "--skip-index"], env, sub, sub)
    L.git(dst, "add", "-A")
    L.git(dst, "commit", "-q", "-m", "vendored legacy sub-project")
    return dst, {"sub_init_ok": r.get("ok"), "state_r5": L.state_r5(dst)}


if __name__ == "__main__":
    S = os.path.abspath(sys.argv[1])
    os.makedirs(S, exist_ok=False)
    base, bf, ids = build_base(S)
    r5, f5, rcs = to_r5(S, base, "R5")
    res, fres = make_r5res(S, r5)
    nos, fnos, _ = to_r5(S, base, "R5NOSURG", surgery=False)
    r5v, fv = make_r5v(S, r5)
    out = {"scratch": S, "trees": {"L0": base, "R5": r5, "R5RES": res, "R5NOSURG": nos, "R5V": r5v}, "ids": ids, "rcs": rcs,
           "base_facts": bf, "R5": f5, "R5RES": fres, "R5NOSURG": fnos, "R5V": fv,
           "binaries_sha256": {v: L.sha_file(L.BINS[v]) for v in L.VERSIONS}}
    json.dump(out, open(os.path.join(S, "trees.json"), "w"), indent=1)
    print(L.scrub(json.dumps({k: v for k, v in out.items() if k != "rcs"}, indent=1, default=str)))
