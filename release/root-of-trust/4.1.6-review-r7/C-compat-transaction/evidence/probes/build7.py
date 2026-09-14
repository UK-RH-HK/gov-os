#!/usr/bin/env python3
"""AR-0021 builder: a real legacy project made by the real 4.1.5 binary, migrated to the RoT-1 revision-7 layout as the pack
specifies it at d07d200 (`26` §2 and §7, `08` §2–§3, `18` §5.1, §8, §9.1, `20` §3 and §9), plus the local machine state the
revision-7 transaction rules read (a per-project record model outside the tree, `20` §9, `24` §8).

Legacy base recipe (attributed): init 4.1.4 -> gated update to 4.1.5 leaving the legacy update snapshot -> two restricted
classifications -> task, gate, CIT, handoff, lesson packet, plugin, tool descriptor, adapters, memory index. The argument shapes
follow reviewer C's earlier builders (AR-0013/AR-0017); the code is AR-0021's.

Installed kernel: the `framework/` tree at d07d200 without KERNEL_MANIFEST.json. Statements are unsigned review fixtures wrapping
the pack's revision-7 example payloads; no probe verifies them (the legacy binaries do not read them; the predicate checks layout).

Trees
  L0       legacy project (control)
  R7       migrated machine: quarantine, `trust-tx/LOCK`, `trust-tx/done/<TXD>/journal.json` (registered as done in the record),
           a RoT-1 snapshot; record {project_trust_id, identity (st_dev, st_ino of the common dir), paths, done_tx, open_tx: []}
  R7RES    second machine on the same commit: legacy update snapshot at `.governance-runtime/update/4.1.5/`, no trust-tx, no record
  R7CRASH  R7 plus crash residue `trust-tx/<TXC>/{journal swapped, trust.next, trust.prev, overlay.prev}` NOT registered (foreign)
  R7OPEN   R7 plus an honoured open transaction `trust-tx/<TXO>/` at phase `swapped` (the record lists TXO)
  R7V      R7 plus a committed legacy 4.1.5 sub-project at vendor/legacypkg
  R7WT     `git worktree add` of a clone of R7 (base R7WTBASE); one record for the shared common directory with both paths
Usage: build7.py <fresh-dir>
"""
import base64, json, os, re, secrets, shutil, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as L  # noqa
import yaml

TXD, TXC, TXO = "TX-" + "d0" * 16, "TX-" + "c7" * 16, "TX-" + "0e" * 16


def env(S, tag):
    return L.env_child(os.path.join(S, "homes", tag), os.path.join(S, "caches", tag))


def g(S, cwd, *a, **k):
    return L.git(cwd, *a, home=os.path.join(S, "githome"), **k)


def identity(root):
    c = L.git(root, "rev-parse", "--git-common-dir", check=False).stdout.strip()
    c = c if os.path.isabs(c) else os.path.join(root, c)
    st = os.stat(os.path.realpath(c))
    return [st.st_dev, st.st_ino]


def base_legacy(S):
    root = os.path.join(S, "L0")
    os.makedirs(root)
    fx = os.path.join(S, "fixtures")
    os.makedirs(fx, exist_ok=True)
    E, G = env(S, "base"), L.BINS["4.1.5"]
    f, ids = {}, {}
    g(S, root, "init", "-q"); g(S, root, "commit", "-q", "--allow-empty", "-m", "empty")
    f["init_4.1.4"] = L.gov(G, ["init", "--source", L.REL["4.1.4"], "--name", "ar21", "--skip-index"], E, root, root).get("ok")
    g(S, root, "add", "-A"); g(S, root, "commit", "-q", "-m", "legacy 4.1.4")
    first = L.gov(G, ["update", "--apply", "--source", L.REL["4.1.5"]], E, root, root)
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    f["update_gate"] = gid
    L.gov(G, ["gate", "present", gid], E, root, root)
    f["decide"] = L.gov(G, ["decide", gid, "--option", "A", "--by", "owner"], E, root, root).get("ok")
    f["update_applied"] = L.gov(G, ["update", "--apply", "--approve", "--source", L.REL["4.1.5"]], E, root, root).get("ok")
    f["legacy_update_snapshot"] = L.kind(os.path.join(root, ".governance-runtime/update/4.1.5")) == "dir"
    for p, t in (("product/restricted-plan.md", "# Plan\n\n%s customer terms\n" % L.MARK1), ("product/customers/acme.md", "# ACME\n\n%s contract\n" % L.MARK2),
                 ("product/readme.md", "# Product\n\nnotes\n"), ("docs/guide.md", "# Guide\n")):
        os.makedirs(os.path.dirname(os.path.join(root, p)), exist_ok=True)
        open(os.path.join(root, p), "w").write(t)
    dsp = os.path.join(root, "governance/project/DATA_SENSITIVITY.yaml")
    ds = yaml.safe_load(open(dsp)) or {}
    ds.setdefault("classifications", []).extend([{"pattern": "product/restricted-plan.md", "class": "restricted", "reason": "customer terms"},
                                                 {"pattern": "product/customers/**", "class": "restricted", "reason": "customer records"}])
    yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
    ids["TASK"] = L.res(L.gov(G, ["task", "create", "--class", "documentation", "--objective", "ar21", "--title", "ar21", "--status", "READY"], E, root, root)).get("id") or "TASK-0001"
    gg = L.gov(G, ["gate", "create", "--question", "ar21?", "--fields", json.dumps({"options": [{"id": "A", "description": "y"}, {"id": "B", "description": "n"}],
                                                                                   "impact_radius": "R1", "confidence": 0.9, "reversibility": "reversible"})], E, root, root)
    ids["GATE"] = L.res(gg).get("id") or gid
    L.gov(G, ["gate", "present", ids["GATE"]], E, root, root)
    ids["MANIFEST"] = os.path.join(fx, "cit-manifest.json")
    json.dump([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\nAR21 CIT\n"}], open(ids["MANIFEST"], "w"))
    ids["CIT"] = L.res(L.gov(G, ["cit", "propose", "--proposal", "ar21", "--trigger", "editorial", "--targets", ids["TASK"], "--manifest", ids["MANIFEST"]], E, root, root)).get("id") or "CIT-0001"
    f["cit_simulate"] = L.gov(G, ["cit", "simulate", ids["CIT"]], E, root, root).get("ok")
    f["cit_approve"] = L.gov(G, ["cit", "approve", ids["CIT"], "--by", "orchestrator", "--method", "auto"], E, root, root).get("ok")
    ids["HANDOFF"] = L.res(L.gov(G, ["handoff", "create", "--to-role", "backend-engineer", "--task", ids["TASK"]], E, root, root)).get("id") or "HND-0001"
    os.makedirs(os.path.join(root, "spec/lessons"), exist_ok=True)
    shutil.copy(os.path.join(S, "fixtures-src", "L-0001.yaml"), os.path.join(root, "spec/lessons/L-0001.yaml"))
    up = L.res(L.gov(G, ["upstream", "prepare", "L-0001"], E, root, root))
    ids["PACKET"] = os.path.join(fx, "packet.yaml")
    pk = up.get("packet") or up.get("path")
    shutil.copy(pk, ids["PACKET"]) if pk and os.path.exists(pk) else open(ids["PACKET"], "w").write("id: L-0001\n")
    os.makedirs(os.path.join(root, "tools"), exist_ok=True)
    open(os.path.join(root, "tools/probe.sh"), "w").write("#!/bin/sh\ncat >/dev/null\nprintf '{\"protocol\":\"gov-capability/1\",\"ok\":true,\"provider\":{\"id\":\"probe\",\"version\":\"1\"},\"outputs\":{\"symbols\":[],\"imports\":[],\"calls\":[],\"chunks\":[]}}'\n")
    os.chmod(os.path.join(root, "tools/probe.sh"), 0o755)
    desc = 'plugin_id: p-probe\ncapability: code_intel\ncommand: ["tools/probe.sh"]\nversion: "1"\nlanguages: ["python"]\n'
    os.makedirs(os.path.join(root, "governance/project/plugins"), exist_ok=True)
    open(os.path.join(root, "governance/project/plugins/p-probe.yaml"), "w").write(desc)
    ids["PLUGIN_DESCRIPTOR"] = os.path.join(fx, "p-probe.yaml"); open(ids["PLUGIN_DESCRIPTOR"], "w").write(desc)
    f["plugin_register"] = L.gov(G, ["plugins", "register", "--descriptor", ids["PLUGIN_DESCRIPTOR"]], E, root, root).get("ok")
    ids["TOOL_DESCRIPTOR"] = os.path.join(fx, "tool.json")
    json.dump({"tool_id": "ar21tool", "name": "ar21tool", "type": "CLI", "capabilities": ["run_tests"], "version": "1", "version_pin": "1.0.0", "license": "MIT", "reversible": True,
               "cost_usd": 0.0, "install_command": ["true"], "uninstall_command": ["true"], "required_permission_classes": ["RUN_TESTS"],
               "health_check": {"kind": "command_exists", "command": ["true"]}}, open(ids["TOOL_DESCRIPTOR"], "w"))
    ids["REPORT"] = os.path.join(fx, "report.json")
    json.dump({"work_completed": "ar21", "files_changed": ["README.md"], "tests": {"status": "not_applicable_with_reason", "reason": "ar21"}, "outcome": "success", "evidence": []}, open(ids["REPORT"], "w"))
    ids["RETURN"] = os.path.join(fx, "return.json")
    json.dump({"task": ids["TASK"], "status": "success", "work_completed": "x", "files_changed": [], "evidence": [], "tests": {"status": "passed"}, "discoveries": [], "risks": [],
               "lessons": [], "proposed_decisions": [], "unresolved": [], "recommended_next_action": "close"}, open(ids["RETURN"], "w"))
    f["adapters"] = L.gov(G, ["adapters", "generate"], E, root, root).get("ok")
    g(S, root, "add", "-A"); g(S, root, "commit", "-q", "-m", "legacy state + restricted classifications")
    f["rebuild"] = L.gov(G, ["rebuild-memory"], E, root, root).get("ok")
    for m in (L.MARK1, L.MARK2):
        f["control_hits_" + m] = sorted({h.get("path") for h in (L.res(L.gov(G, ["memory", "query", m], E, root, root)).get("hits") or []) if isinstance(h, dict)})
    f["kernel_trust_verified"] = L.res(L.gov(G, ["kernel", "trust"], E, root, root)).get("verified")
    f["gitignore"] = open(os.path.join(root, ".gitignore")).read()
    return root, f, ids


def surgery(text):
    out = [l for l in text.splitlines() if not re.match(r"^/?\.governance-runtime/?$", l.strip())]
    for r in ("/.governance-runtime/*", "!/.governance-runtime/migration"):
        if r not in out:
            out.append(r)
    return "\n".join(out) + "\n"


def wrap(payload, ptype):
    pb = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {"payloadType": ptype, "payload": base64.b64encode(pb).decode(), "signatures": [{"keyid": "ed25519:" + "0" * 64, "sig": base64.b64encode(b"ar21-unsigned-fixture").decode()}]}, L.sha(pb)


def trust_tree(S, t, ptid):
    ex = os.path.join(L.EXPORT, "release/root-of-trust/4.1.6/examples")
    os.makedirs(t)
    shutil.copytree(os.path.join(S, "framework-4.1.6"), os.path.join(t, "kernel"))
    km = os.path.join(t, "kernel", "KERNEL_MANIFEST.json")
    if L.kind(km) == "file":
        os.unlink(km)
    for dp, dns, fns in os.walk(os.path.join(t, "kernel")):
        os.chmod(dp, 0o755)
        for n in fns:
            os.chmod(os.path.join(dp, n), 0o644)
    rcs = L.kernel_files(os.path.join(t, "kernel"))[0]
    for sub in ("state", "root", "lineage", "profiles"):
        os.makedirs(os.path.join(t, sub))
    r7 = os.path.join(ex, "rev7")
    reg, regd = wrap(json.load(open(os.path.join(r7, "release-registration.payload.example.json"))), "application/vnd.rot1r7.release-registration+json")
    json.dump(reg, open(os.path.join(t, "registration.dsse.json"), "w"))
    for fn, name, pt in (("trust-state.payload.example.json", "trust-state.1.dsse.json", "trust-state"), ("trust-policy.payload.example.json", "trust-policy.v4.dsse.json", "trust-policy"),
                         ("revocation.payload.example.json", "revocation.1.dsse.json", "revocation"), ("verification-attestation.payload.example.json", "verification-attestation.1.dsse.json", "verification-attestation")):
        json.dump(wrap(json.load(open(os.path.join(r7, fn))), "application/vnd.rot1r7.%s+json" % pt)[0], open(os.path.join(t, "state", name), "w"))
    json.dump(wrap(json.load(open(os.path.join(r7, "trust-root.payload.example.json"))), "application/vnd.rot1r7.trust-root+json")[0], open(os.path.join(t, "root", "1.dsse.json"), "w"))
    shutil.copy(os.path.join(ex, "rev2", "release-final.dsse.json"), os.path.join(t, "release.dsse.json"))
    shutil.copy(os.path.join(ex, "rev2", "release-candidate.dsse.json"), os.path.join(t, "lineage", "candidate.dsse.json"))
    shutil.copy(os.path.join(ex, "rev2", "retrieval-profile.dsse.json"), os.path.join(t, "profiles", "hashed-ngram.dsse.json"))
    lock = json.load(open(os.path.join(ex, "rev3", "framework-lock-3.0.0.example.json")))
    lock["project_trust_id"] = ptid
    lock.setdefault("kernel", {})["files"] = {k: "sha256:" + v for k, v in sorted(rcs.items())}
    lock["registration_digest"] = "sha256:" + regd
    open(os.path.join(t, "framework.lock"), "w").write(json.dumps(lock, sort_keys=True, separators=(",", ":")))
    open(os.path.join(t, "FORMAT"), "w").write(json.dumps(L.FORMAT_OBJ, sort_keys=True, separators=(",", ":")))
    open(os.path.join(t, ".gitattributes"), "wb").write(L.GITATTR)
    return rcs


def to_r7(S, L0, name):
    d = os.path.join(S, name)
    shutil.copytree(L0, d, symlinks=True)
    aside = os.path.join(S, "aside", name)
    os.makedirs(aside)
    gd, rt = os.path.join(d, "governance"), os.path.join(d, ".governance-runtime")
    q = os.path.join(rt, "legacy-quarantine")
    for leg in ("update", "migration"):
        if L.kind(os.path.join(rt, leg)) == "dir":
            os.makedirs(q, exist_ok=True)
            os.rename(os.path.join(rt, leg), os.path.join(q, leg))
    os.rename(os.path.join(gd, "kernel"), os.path.join(aside, "legacy-kernel"))
    os.rename(os.path.join(gd, "framework.lock"), os.path.join(aside, "legacy-framework.lock"))
    os.rename(os.path.join(gd, "project"), os.path.join(gd, "overlay"))
    if L.kind(os.path.join(gd, "generated")) == "dir":
        os.rename(os.path.join(gd, "generated"), os.path.join(gd, "views"))
    if L.kind(os.path.join(d, "spec/audits/GOVERNANCE-ADOPTION")) == "dir":
        os.rename(os.path.join(d, "spec/audits/GOVERNANCE-ADOPTION"), os.path.join(d, "spec/audits/ADOPTION"))
    ptid = secrets.token_hex(16)
    rcs = trust_tree(S, os.path.join(gd, "trust"), ptid)
    for p in ("kernel", "project", "generated"):
        open(os.path.join(gd, p), "w").write(L.SENTINEL + "\n")
    os.makedirs(os.path.join(gd, "framework.lock"))
    open(os.path.join(gd, "framework.lock", L.OCC_DIR_SENTINEL), "w").write(L.SENTINEL + "\n")
    os.makedirs(os.path.join(d, "spec/audits"), exist_ok=True)
    open(os.path.join(d, "spec/audits/GOVERNANCE-ADOPTION"), "w").write(L.SENTINEL + "\n")
    open(os.path.join(rt, "migration"), "w").write(L.SENTINEL + "\n")
    gi = os.path.join(d, ".gitignore")
    open(gi, "w").write(surgery(open(gi).read() if os.path.exists(gi) else ""))
    os.makedirs(os.path.join(rt, "trust-tx", "done", TXD))
    open(os.path.join(rt, "trust-tx", "LOCK"), "w").write("")
    json.dump({"operation": "update", "phase": "verified", "project_trust_id": ptid}, open(os.path.join(rt, "trust-tx", "done", TXD, "journal.json"), "w"))
    sd = os.path.join(rt, "snapshots", "sha256-" + "b" * 16)
    os.makedirs(os.path.join(sd, "statements"))
    shutil.copy(os.path.join(gd, "trust", "release.dsse.json"), os.path.join(sd, "statements", "release.dsse.json"))
    shutil.copytree(os.path.join(gd, "overlay"), os.path.join(sd, "overlay"))
    g(S, d, "add", "-A"); g(S, d, "add", "-f", ".governance-runtime/migration")
    g(S, d, "commit", "-q", "-m", "RoT-1 revision-7 layout migration")
    facts = {"head": g(S, d, "rev-parse", "HEAD").stdout.strip(), "pre_migration": g(S, d, "rev-parse", "HEAD~1").stdout.strip(),
             "tracked_but_ignored": g(S, d, "ls-files", "-ci", "--exclude-standard").stdout.split(), "tracked_runtime": g(S, d, "ls-files", ".governance-runtime").stdout.split(),
             "project_trust_id": ptid}
    record = {"project_trust_id": ptid, "identity": identity(d), "paths": [os.path.realpath(d)], "open_tx": [], "done_tx": [TXD], "highest_sequence": 6}
    return d, facts, rcs, record


def rebind(record, root, **kw):
    r = dict(record, identity=identity(root), paths=[os.path.realpath(root)])
    r.update(kw)
    return r


def add_tx(d, tx, phase):
    t = os.path.join(d, ".governance-runtime", "trust-tx", tx)
    os.makedirs(t)
    shutil.copytree(os.path.join(d, "governance/trust"), os.path.join(t, "trust.prev"), symlinks=True)
    shutil.copytree(os.path.join(d, "governance/trust"), os.path.join(t, "trust.next"), symlinks=True)
    os.makedirs(os.path.join(t, "overlay.prev"))
    shutil.copytree(os.path.join(d, "governance/overlay"), os.path.join(t, "overlay.prev", "overlay"))
    shutil.copytree(os.path.join(d, "governance/views"), os.path.join(t, "overlay.prev", "views"))
    json.dump({"operation": "update", "phase": phase}, open(os.path.join(t, "journal.json"), "w"))


def main():
    S = os.path.abspath(sys.argv[1])
    os.makedirs(S)
    for x in ("bin", "releases", "fixtures-src", "framework-4.1.6"):
        os.symlink(os.path.join(L.SCR, x), os.path.join(S, x))
    L0, bf, ids = base_legacy(S)
    R7, f7, rcs, rec = to_r7(S, L0, "R7")
    trees, records = {"L0": L0, "R7": R7}, {"R7": rec}
    res_ = os.path.join(S, "R7RES"); shutil.copytree(R7, res_, symlinks=True)
    os.makedirs(os.path.join(S, "aside", "R7RES"))
    os.rename(os.path.join(res_, ".governance-runtime/legacy-quarantine/update"), os.path.join(res_, ".governance-runtime/update"))
    for x in ("trust-tx", "snapshots"):
        os.rename(os.path.join(res_, ".governance-runtime", x), os.path.join(S, "aside", "R7RES", x))
    trees["R7RES"], records["R7RES"] = res_, None
    cr = os.path.join(S, "R7CRASH"); shutil.copytree(R7, cr, symlinks=True); add_tx(cr, TXC, "swapped")
    trees["R7CRASH"], records["R7CRASH"] = cr, rebind(rec, cr)
    op = os.path.join(S, "R7OPEN"); shutil.copytree(R7, op, symlinks=True); add_tx(op, TXO, "swapped")
    trees["R7OPEN"], records["R7OPEN"] = op, rebind(rec, op, open_tx=[TXO])
    ven = os.path.join(S, "R7V"); shutil.copytree(R7, ven, symlinks=True)
    sub = os.path.join(ven, "vendor", "legacypkg"); os.makedirs(sub); open(os.path.join(sub, "README.md"), "w").write("# legacypkg\n")
    bf["vendor_init"] = L.gov(L.BINS["4.1.5"], ["init", "--source", L.REL["4.1.5"], "--name", "legacypkg", "--skip-index"], env(S, "ven"), sub, sub).get("ok")
    g(S, ven, "add", "-A"); g(S, ven, "commit", "-q", "-m", "vendored legacy sub-project")
    trees["R7V"], records["R7V"] = ven, rebind(rec, ven)
    wb = os.path.join(S, "R7WTBASE"); g(S, S, "clone", "-q", R7, wb)
    wt = os.path.join(S, "R7WT"); g(S, wb, "worktree", "add", "-q", wt, "HEAD")
    trees["R7WTBASE"], trees["R7WT"] = wb, wt
    records["R7WTBASE"] = rebind(rec, wb, done_tx=[])
    records["R7WT"] = dict(records["R7WTBASE"], paths=[os.path.realpath(wb), os.path.realpath(wt)])
    states = {k: L.state_r7(v, records.get(k), identity(v) if L.kind(os.path.join(v, ".git")) != "absent" else None, rcs) for k, v in trees.items()}
    out = {"scratch": S, "trees": trees, "records": records, "ids": ids, "rcs": rcs, "base_facts": bf, "R7": f7, "states": states,
           "entries": {k: len(L.tmap(v)) for k, v in trees.items()}, "binaries_sha256": {v: L.fsha(L.BINS[v]) for v in L.VERSIONS},
           "tx": {"done": TXD, "crash": TXC, "open": TXO}}
    L.dump(out, os.path.join(S, "trees.json"))
    json.dump(out, open(os.path.join(S, "trees.raw.json"), "w"), default=lambda o: sorted(o) if isinstance(o, set) else str(o))
    print(L.scrub(json.dumps({k: v for k, v in out.items() if k not in ("rcs",)}, indent=1, default=str)))


if __name__ == "__main__":
    main()
