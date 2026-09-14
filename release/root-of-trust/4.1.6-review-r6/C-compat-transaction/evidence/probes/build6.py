#!/usr/bin/env python3
"""AR-0017 builder: a real legacy project made by the real 4.1.5 binary, migrated to the RoT-1 revision-6 layout as the pack
specifies it at 4106885 (`08` §2–§3, `26` §2 and §7, `18` §5.1, §8, §9.1; `20` §3, `13` §6).

Legacy base recipe (attributed): init 4.1.4 -> gated update to 4.1.5 leaving the legacy update snapshot -> restricted
classifications added after the update -> task, gate, CIT, handoff, lesson packet, plugin, tool descriptor, adapters,
memory index. The argument shapes follow review r5 C `build5.py` (AR-0013), which reproduced them from review r4 C; the code
is AR-0017's. The revision-6 layout is encoded from the pack text, not from the LAY6 copy.

Installed kernel: the 4.1.6 `framework/` tree at 4106885 (the kernel a genuine 4.1.6 install would carry), without any
KERNEL_MANIFEST.json. Trust statements are the pack's unsigned review fixtures (`examples/rev2`), which no probe here verifies.

Trees
  L0       legacy project (control)
  R6       migrated machine: `.gitignore` surgery, quarantine of the legacy update snapshot and legacy migration residue,
           `trust-tx/LOCK` and `trust-tx/done/<TX>/journal.json`, a RoT-1 snapshot under `snapshots/<CI>/`
  R6RES    second machine on the same commit: legacy update snapshot still at `.governance-runtime/update/4.1.5/`, no trust-tx
  R6CRASH  R6 plus crash residue of an interrupted RoT-1 update: `trust-tx/<TX2>/{journal.json (phase swapped), trust.next/,
           trust.prev/, overlay.prev/}` (not VTS-registered on this machine: foreign)
  R6V      R6 plus a committed legacy 4.1.5 sub-project at `vendor/legacypkg`
Usage: build6.py <fresh-dir>
"""
import base64, json, os, re, secrets, shutil, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c6lib as L  # noqa
import yaml

MARK1 = "AR0017RESTRICTEDMARKER"
MARK2 = "AR0017CUSTOMERMARKER"
TX_DONE = "TX-" + "1d" * 16
TX_CRASH = "TX-" + "c7" * 16


def envfor(S, tag):
    return L.child_env(os.path.join(S, "homes", tag), os.path.join(S, "caches", tag))


def g(root, *a, **k):
    return L.git(root, *a, home=os.path.join(os.path.dirname(root), "githome"), **k)


def build_base(S):
    root = os.path.join(S, "L0")
    os.makedirs(root)
    fx = os.path.join(S, "fixtures")
    os.makedirs(fx, exist_ok=True)
    env = envfor(S, "base")
    G = L.BINS["4.1.5"]
    f, ids = {}, {}
    g(root, "init", "-q")
    g(root, "commit", "-q", "--allow-empty", "-m", "empty")
    f["init_4.1.4"] = L.gov(G, ["init", "--source", L.REL["4.1.4"], "--name", "ar17", "--skip-index"], env, root, root).get("ok")
    g(root, "add", "-A"); g(root, "commit", "-q", "-m", "legacy 4.1.4 install")
    first = L.gov(G, ["update", "--apply", "--source", L.REL["4.1.5"]], env, root, root)
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    f["update_gate"] = gid
    L.gov(G, ["gate", "present", gid], env, root, root)
    f["decide"] = L.gov(G, ["decide", gid, "--option", "A", "--by", "owner"], env, root, root).get("ok")
    ap = L.gov(G, ["update", "--apply", "--approve", "--source", L.REL["4.1.5"]], env, root, root)
    f["update_applied"] = ap.get("ok")
    f["legacy_update_snapshot"] = L.kind(os.path.join(root, ".governance-runtime/update/4.1.5")) == "dir"
    for p, t in (("product/restricted-plan.md", "# Plan\n\n%s proprietary customer terms\n" % MARK1),
                 ("product/customers/acme.md", "# ACME\n\n%s contract value and contacts\n" % MARK2),
                 ("product/readme.md", "# Product\n\nordinary notes\n"), ("docs/guide.md", "# Guide\n\nordinary docs\n")):
        os.makedirs(os.path.dirname(os.path.join(root, p)), exist_ok=True)
        open(os.path.join(root, p), "w").write(t)
    dsp = os.path.join(root, "governance/project/DATA_SENSITIVITY.yaml")
    ds = yaml.safe_load(open(dsp)) or {}
    ds.setdefault("classifications", []).extend([
        {"pattern": "product/restricted-plan.md", "class": "restricted", "reason": "customer terms"},
        {"pattern": "product/customers/**", "class": "restricted", "reason": "customer records"}])
    yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
    t = L.gov(G, ["task", "create", "--class", "documentation", "--objective", "ar17 task", "--title", "ar17", "--status", "READY"], env, root, root)
    ids["TASK"] = L.result(t).get("id") or "TASK-0001"
    gg = L.gov(G, ["gate", "create", "--question", "ar17 gate?", "--fields", json.dumps({"options": [{"id": "A", "description": "yes"}, {"id": "B", "description": "no"}], "impact_radius": "R1", "confidence": 0.9, "reversibility": "reversible"})], env, root, root)
    ids["GATE"] = L.result(gg).get("id") or gid
    L.gov(G, ["gate", "present", ids["GATE"]], env, root, root)
    mf = os.path.join(fx, "cit-manifest.json")
    json.dump([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\nAR17 CIT WROTE THIS\n"}], open(mf, "w"))
    ids["MANIFEST"] = mf
    c = L.gov(G, ["cit", "propose", "--proposal", "ar17 change", "--trigger", "editorial", "--targets", ids["TASK"], "--manifest", mf], env, root, root)
    ids["CIT"] = L.result(c).get("id") or "CIT-0001"
    f["cit_simulate"] = L.gov(G, ["cit", "simulate", ids["CIT"]], env, root, root).get("ok")
    f["cit_approve"] = L.gov(G, ["cit", "approve", ids["CIT"], "--by", "orchestrator", "--method", "auto"], env, root, root).get("ok")
    h = L.gov(G, ["handoff", "create", "--to-role", "backend-engineer", "--task", ids["TASK"]], env, root, root)
    ids["HANDOFF"] = L.result(h).get("id") or "H-0001"
    os.makedirs(os.path.join(root, "spec/lessons"), exist_ok=True)
    shutil.copy(os.path.join(L.SCR, "fixtures-src", "L-0001.yaml"), os.path.join(root, "spec/lessons/L-0001.yaml"))
    up = L.gov(G, ["upstream", "prepare", "L-0001"], env, root, root)
    pk = L.result(up).get("packet") or L.result(up).get("path")
    ids["PACKET"] = os.path.join(fx, "packet.yaml")
    if pk and os.path.exists(pk):
        shutil.copy(pk, ids["PACKET"])
    else:
        open(ids["PACKET"], "w").write("id: L-0001\n")
    os.makedirs(os.path.join(root, "tools"), exist_ok=True)
    open(os.path.join(root, "tools/probe.sh"), "w").write("#!/bin/sh\ncat >/dev/null\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"probe\",\"version\":\"1\"},\"outputs\":{\"symbols\":[],\"imports\":[],\"calls\":[],\"chunks\":[]}}'\n")
    os.chmod(os.path.join(root, "tools/probe.sh"), 0o755)
    os.makedirs(os.path.join(root, "governance/project/plugins"), exist_ok=True)
    desc = 'plugin_id: p-probe\ncapability: code_intel\ncommand: ["tools/probe.sh"]\nversion: "1"\nlanguages: ["python"]\n'
    open(os.path.join(root, "governance/project/plugins/p-probe.yaml"), "w").write(desc)
    ids["PLUGIN_DESCRIPTOR"] = os.path.join(fx, "p-probe.yaml")
    open(ids["PLUGIN_DESCRIPTOR"], "w").write(desc)
    f["plugin_register"] = L.gov(G, ["plugins", "register", "--descriptor", ids["PLUGIN_DESCRIPTOR"]], env, root, root).get("ok")
    ids["TOOL_DESCRIPTOR"] = os.path.join(fx, "tool.json")
    json.dump({"tool_id": "ar17tool", "name": "ar17tool", "type": "CLI", "capabilities": ["run_tests"], "version": "1", "version_pin": "1.0.0", "license": "MIT",
               "reversible": True, "cost_usd": 0.0, "install_command": ["true"], "uninstall_command": ["true"],
               "required_permission_classes": ["RUN_TESTS"], "health_check": {"kind": "command_exists", "command": ["true"]}}, open(ids["TOOL_DESCRIPTOR"], "w"))
    ids["REPORT"] = os.path.join(fx, "report.json")
    json.dump({"work_completed": "ar17", "files_changed": ["README.md"], "tests": {"status": "not_applicable_with_reason", "reason": "ar17"}, "outcome": "success", "evidence": []}, open(ids["REPORT"], "w"))
    ids["RETURN"] = os.path.join(fx, "return.json")
    json.dump({"task": ids["TASK"], "status": "success", "work_completed": "x", "files_changed": [], "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [],
               "lessons": [], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "close"}, open(ids["RETURN"], "w"))
    f["adapters_generate"] = L.gov(G, ["adapters", "generate"], env, root, root).get("ok")
    g(root, "add", "-A"); g(root, "commit", "-q", "-m", "legacy project state + restricted classifications")
    f["rebuild"] = L.gov(G, ["rebuild-memory"], env, root, root).get("ok")
    for m in (MARK1, MARK2):
        q = L.gov(G, ["memory", "query", m], env, root, root)
        f["control_hits_" + m] = [x.get("path") for x in (L.result(q).get("hits") or [])]
    f["kernel_trust_verified"] = L.result(L.gov(G, ["kernel", "trust"], env, root, root)).get("verified")
    f["gitignore"] = open(os.path.join(root, ".gitignore")).read() if os.path.exists(os.path.join(root, ".gitignore")) else None
    f["runtime_entries"] = sorted(os.listdir(os.path.join(root, ".governance-runtime")))
    f["update_snapshot_entries"] = sorted(os.listdir(os.path.join(root, ".governance-runtime/update/4.1.5"))) if f["legacy_update_snapshot"] else None
    return root, f, ids


DIR_IGNORE = re.compile(r"^/?\.governance-runtime/?$")


def gitignore_surgery(text):
    """26 §8 (RV4-M6) and §2: drop every `.governance-runtime/` directory-ignore line (with or without leading or trailing slash),
    keep every other line, add the two child-glob rules once."""
    out = [l for l in text.splitlines() if not DIR_IGNORE.match(l.strip())]
    for r in ("/.governance-runtime/*", "!/.governance-runtime/migration"):
        if r not in out:
            out.append(r)
    return "\n".join(out) + "\n"


def dsse(payload, ptype):
    pb = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {"payloadType": ptype, "payload": base64.b64encode(pb).decode(),
            "signatures": [{"keyid": "ed25519:" + "0" * 64, "sig": base64.b64encode(b"ar17-unsigned-review-fixture").decode()}]}, L.sha(pb)


def write_trust_tree(t, S, project_trust_id):
    """08 §2 trust tree: FORMAT, .gitattributes, registration.dsse.json, framework.lock (3.0.0), kernel/**, release.dsse.json,
    lineage/, state/, root/, profiles/."""
    os.makedirs(t)
    shutil.copytree(os.path.join(L.SCR, "framework-4.1.6"), os.path.join(t, "kernel"))
    for dp, dns, fns in os.walk(os.path.join(t, "kernel")):
        os.chmod(dp, 0o755)
        for n in fns:
            os.chmod(os.path.join(dp, n), 0o644)
    km = os.path.join(t, "kernel", "KERNEL_MANIFEST.json")
    if L.kind(km) == "file":
        os.unlink(km)
    rcs = {k: v[1] for k, v in L.kernel_file_map(os.path.join(t, "kernel")).items() if v[0] == "file"}
    ex = os.path.join(L.PACK, "examples")
    for sub in ("state", "lineage", "profiles", "root"):
        os.makedirs(os.path.join(t, sub))
    reg, reg_d = dsse(json.load(open(os.path.join(ex, "rev6", "release-registration.payload.example.json"))),
                      "application/vnd.governance-os.release-registration.v2+json")
    json.dump(reg, open(os.path.join(t, "registration.dsse.json"), "w"))
    lock = json.load(open(os.path.join(ex, "rev3", "framework-lock-3.0.0.example.json")))
    lock["project_trust_id"] = project_trust_id
    lock.setdefault("kernel", {})["files"] = {k: "sha256:" + v for k, v in sorted(rcs.items())}
    lock["registration_digest"] = "sha256:" + reg_d
    open(os.path.join(t, "framework.lock"), "w").write(json.dumps(lock, sort_keys=True, separators=(",", ":")))
    open(os.path.join(t, "FORMAT"), "wb").write(L.FORMAT_BYTES)
    open(os.path.join(t, ".gitattributes"), "wb").write(L.GITATTR_BYTES)
    r2 = os.path.join(ex, "rev2")
    shutil.copy(os.path.join(r2, "release-final.dsse.json"), os.path.join(t, "release.dsse.json"))
    shutil.copy(os.path.join(r2, "release-candidate.dsse.json"), os.path.join(t, "lineage", "candidate.dsse.json"))
    for fn in ("trust-state.1.dsse.json", "trust-state.2.dsse.json", "trust-state.3.dsse.json", "trust-policy.v1.dsse.json",
               "certification.1-CERTIFIED.dsse.json", "verification-attestation.dsse.json", "revocation.1.dsse.json"):
        shutil.copy(os.path.join(r2, fn), os.path.join(t, "state", fn))
    shutil.copy(os.path.join(r2, "trust-root.v1.dsse.json"), os.path.join(t, "root", "2.dsse.json"))
    shutil.copy(os.path.join(r2, "retrieval-profile.dsse.json"), os.path.join(t, "profiles", "hashed-ngram.dsse.json"))
    return rcs


def to_r6(S, base, name, quarantine=True, txarea=True):
    dst = os.path.join(S, name)
    shutil.copytree(base, dst, symlinks=True)
    aside = os.path.join(S, "aside", name)
    os.makedirs(aside)
    gdir = os.path.join(dst, "governance")
    ptid = secrets.token_hex(16)
    # 26 §7 step 1: quarantine legacy runtime residue
    rt = os.path.join(dst, ".governance-runtime")
    q = os.path.join(rt, "legacy-quarantine")
    if quarantine and L.kind(os.path.join(rt, "update")) == "dir":
        os.makedirs(q, exist_ok=True)
        os.rename(os.path.join(rt, "update"), os.path.join(q, "update"))
    if L.kind(os.path.join(rt, "migration")) == "dir":
        os.makedirs(q, exist_ok=True)
        os.rename(os.path.join(rt, "migration"), os.path.join(q, "migration"))
    # step 2: move kernel (aside: the legacy kernel is replaced), overlay, views, adoption evidence
    os.rename(os.path.join(gdir, "kernel"), os.path.join(aside, "legacy-kernel"))
    os.rename(os.path.join(gdir, "framework.lock"), os.path.join(aside, "legacy-framework.lock"))
    os.rename(os.path.join(gdir, "project"), os.path.join(gdir, "overlay"))
    if L.kind(os.path.join(gdir, "generated")) == "dir":
        os.rename(os.path.join(gdir, "generated"), os.path.join(gdir, "views"))
    if L.kind(os.path.join(dst, "spec/audits/GOVERNANCE-ADOPTION")) == "dir":
        os.rename(os.path.join(dst, "spec/audits/GOVERNANCE-ADOPTION"), os.path.join(dst, "spec/audits/ADOPTION"))
    # step 3: governance/trust/**
    rcs = write_trust_tree(os.path.join(gdir, "trust"), S, ptid)
    # step 4: occupation entries
    for p in ("kernel", "project", "generated"):
        open(os.path.join(gdir, p), "w").write(L.SENTINEL + "\n")
    os.makedirs(os.path.join(gdir, "framework.lock"))
    open(os.path.join(gdir, "framework.lock", L.OCC_DIR_SENTINEL), "w").write(L.SENTINEL + "\n")
    os.makedirs(os.path.join(dst, "spec/audits"), exist_ok=True)
    open(os.path.join(dst, "spec/audits/GOVERNANCE-ADOPTION"), "w").write(L.SENTINEL + "\n")
    open(os.path.join(rt, "migration"), "w").write(L.SENTINEL + "\n")
    # step 5: ignore rule with surgery
    gi = os.path.join(dst, ".gitignore")
    old = open(gi).read() if os.path.exists(gi) else ""
    open(gi, "w").write(gitignore_surgery(old))
    # transaction area and RoT-1 snapshot (18 §5.1, 20 §3)
    if txarea:
        os.makedirs(os.path.join(rt, "trust-tx", "done", TX_DONE))
        open(os.path.join(rt, "trust-tx", "LOCK"), "w").write("")
        json.dump({"operation": "update", "phase": "verified", "aro_ci": "sha256:" + "a" * 64, "previous_ci": "sha256:" + "b" * 64},
                  open(os.path.join(rt, "trust-tx", "done", TX_DONE, "journal.json"), "w"))
        sd = os.path.join(rt, "snapshots", "sha256-" + "b" * 16)
        os.makedirs(os.path.join(sd, "statements"))
        shutil.copy(os.path.join(gdir, "trust", "release.dsse.json"), os.path.join(sd, "statements", "release.dsse.json"))
        shutil.copytree(os.path.join(gdir, "overlay"), os.path.join(sd, "overlay"))
        json.dump({"kind": "rot1-update-snapshot", "ci": "sha256:" + "b" * 64}, open(os.path.join(sd, "snapshot.json"), "w"))
    g(dst, "add", "-A")
    g(dst, "add", "-f", ".governance-runtime/migration")
    g(dst, "commit", "-q", "-m", "rot-1 revision-6 layout migration (%s)" % name)
    facts = {"gitignore": open(gi).read(), "surgery_idempotent": gitignore_surgery(open(gi).read()) == open(gi).read(),
             "tracked_but_ignored": g(dst, "ls-files", "-ci", "--exclude-standard").stdout.split(),
             "tracked_runtime": g(dst, "ls-files", ".governance-runtime").stdout.split(),
             "state_r6": L.state_r6(dst, rcs=rcs), "head": g(dst, "rev-parse", "HEAD").stdout.strip(),
             "pre_migration": g(dst, "rev-parse", "HEAD~1").stdout.strip(), "governance_entries": sorted(os.listdir(gdir)),
             "project_trust_id": ptid}
    return dst, facts, rcs


def make_res(S, r6):
    dst = os.path.join(S, "R6RES")
    shutil.copytree(r6, dst, symlinks=True)
    rt = os.path.join(dst, ".governance-runtime")
    aside = os.path.join(S, "aside", "R6RES")
    os.makedirs(aside)
    os.rename(os.path.join(rt, "legacy-quarantine", "update"), os.path.join(rt, "update"))
    os.rename(os.path.join(rt, "trust-tx"), os.path.join(aside, "trust-tx"))
    os.rename(os.path.join(rt, "snapshots"), os.path.join(aside, "snapshots"))
    return dst


def make_crash(S, r6):
    dst = os.path.join(S, "R6CRASH")
    shutil.copytree(r6, dst, symlinks=True)
    tx = os.path.join(dst, ".governance-runtime", "trust-tx", TX_CRASH)
    os.makedirs(tx)
    shutil.copytree(os.path.join(dst, "governance", "trust"), os.path.join(tx, "trust.prev"), symlinks=True)
    shutil.copytree(os.path.join(dst, "governance", "trust"), os.path.join(tx, "trust.next"), symlinks=True)
    os.makedirs(os.path.join(tx, "overlay.prev"))
    shutil.copytree(os.path.join(dst, "governance", "overlay"), os.path.join(tx, "overlay.prev", "overlay"))
    shutil.copytree(os.path.join(dst, "governance", "views"), os.path.join(tx, "overlay.prev", "views"))
    json.dump({"operation": "update", "phase": "swapped", "aro_ci": "sha256:" + "c" * 64, "previous_ci": "sha256:" + "a" * 64},
              open(os.path.join(tx, "journal.json"), "w"))
    return dst


def make_vendor(S, r6):
    dst = os.path.join(S, "R6V")
    shutil.copytree(r6, dst, symlinks=True)
    sub = os.path.join(dst, "vendor", "legacypkg")
    os.makedirs(sub)
    open(os.path.join(sub, "README.md"), "w").write("# legacypkg\n")
    r = L.gov(L.BINS["4.1.5"], ["init", "--source", L.REL["4.1.5"], "--name", "legacypkg", "--skip-index"], envfor(S, "r6v"), sub, sub)
    g(dst, "add", "-A")
    g(dst, "commit", "-q", "-m", "vendored legacy sub-project")
    return dst, r.get("ok")


if __name__ == "__main__":
    S = os.path.abspath(sys.argv[1])
    os.makedirs(S)
    base, bf, ids = build_base(S)
    r6, f6, rcs = to_r6(S, base, "R6")
    res = make_res(S, r6)
    crash = make_crash(S, r6)
    ven, ven_ok = make_vendor(S, r6)
    trees = {"L0": base, "R6": r6, "R6RES": res, "R6CRASH": crash, "R6V": ven}
    out = {"scratch": S, "trees": trees, "ids": ids, "rcs": rcs, "base_facts": bf, "R6": f6, "vendor_init_ok": ven_ok,
           "states": {k: L.state_r6(v, rcs=rcs) for k, v in trees.items()},
           "sizes": {k: sum(os.lstat(os.path.join(dp, n)).st_size for dp, dn, fn in os.walk(v) for n in fn) for k, v in trees.items()},
           "entries": {k: len(L.tree_map(v)) for k, v in trees.items()},
           "binaries_sha256": {v: L.sha_file(L.BINS[v]) for v in L.VERSIONS}}
    json.dump(out, open(os.path.join(S, "trees.json"), "w"), indent=1)
    print(L.scrub(json.dumps({k: v for k, v in out.items() if k not in ("rcs",)}, indent=1, default=str)))
