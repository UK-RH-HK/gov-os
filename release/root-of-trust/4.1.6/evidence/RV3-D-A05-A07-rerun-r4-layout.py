#!/usr/bin/env python3
"""RV3-D-A05, A06, A07 re-run on the RoT-1 revision-4 layout (AR-0005).

Attribution: copied from review r3 synthesis D `D-synthesis/evidence/RV3-D-legacy-git-restore.py` (AR-0004), run with the
real legacy 4.1.5 binary and Git. The input tree is reviewer C's L3 layout with the only revision-4 layout delta applied
to the migration commit: `.gitignore` ignores `/.governance-runtime/*` and re-includes `!/.governance-runtime/migration`
(RV3-L7), instead of ignoring the whole directory. The only code change: the A07 "untrack ignored files" commit is made
with `check=False`, because under revision 4 the idiom lists no file and there is nothing to commit; the result records
whether a commit happened. A05 and A06 are unchanged and are expected to reproduce the documented legacy outcome of
residual LR-2 (RV3-M6): revision 4 does not claim to stop Git restoring pre-migration history.
Usage: python3 RV3-D-A05-A07-rerun-r4-layout.py <scratch-dir> <L3-with-r4-ignore-rules> [gov-4.1.5]
"""
import hashlib, json, os, shutil, subprocess, sys
import yaml

SCRATCH = os.path.abspath(sys.argv[1]); L3 = os.path.abspath(sys.argv[2])
GOV = sys.argv[3] if len(sys.argv) > 3 else "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.5"
CLEAN = "/usr/bin:/bin"
MARK = "RV3DPOSTMIGRATIONMARKER"
os.makedirs(SCRATCH, exist_ok=False)


def env_for(tag):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
    h = os.path.join(SCRATCH, "homes", tag); os.makedirs(h, exist_ok=True)
    e.update({"PATH": CLEAN, "HOME": h, "GOV_KERNEL_CACHE": os.path.join(SCRATCH, "caches", tag), "XDG_CONFIG_HOME": h + "/.config",
              "XDG_STATE_HOME": h + "/.local/state", "XDG_CACHE_HOME": h + "/.cache"})
    return e


def git(cwd, *a, check=True):
    r = subprocess.run(["git", "-c", "user.name=rv3d", "-c", "user.email=rv3d@x", "-c", "advice.detachedHead=false", *a], cwd=cwd,
                       capture_output=True, text=True, env={"PATH": CLEAN, "HOME": cwd})
    if check and r.returncode:
        raise RuntimeError(f"git {a}: {r.stderr}")
    return r


def gov(root, args, env):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-rv3d", "--role", "orchestrator", *args], cwd=root, env=env,
                       capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    try:
        d = json.loads(r.stdout)
    except Exception:
        d = {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}
    d["_rc"] = r.returncode
    return d


def code(d):
    e = d.get("error")
    return e.get("code") if isinstance(e, dict) else None


def tree_digest(p):
    if not os.path.exists(p):
        return "<absent>"
    h = hashlib.sha256()
    for dp, dns, fns in sorted(os.walk(p)):
        dns.sort()
        for fn in sorted(fns):
            fp = os.path.join(dp, fn)
            h.update(os.path.relpath(fp, p).encode() + b"\0" + (open(fp, "rb").read() if os.path.isfile(fp) else b"<special>"))
    return h.hexdigest()[:16]


def kind(p):
    return "link" if os.path.islink(p) else "dir" if os.path.isdir(p) else "file" if os.path.isfile(p) else "absent"


OCC = ["governance/kernel", "governance/project", "governance/generated", "governance/framework.lock", "spec/audits/GOVERNANCE-ADOPTION", ".governance-runtime/migration"]


def types(d):
    return {p: kind(os.path.join(d, p)) for p in OCC + ["governance/trust", "governance/overlay"]}


def overlay_classifies(d, pattern):
    try:
        return any(c.get("pattern") == pattern for c in (yaml.safe_load(open(d + "/governance/overlay/DATA_SENSITIVITY.yaml")).get("classifications") or []))
    except Exception:
        return None


def legacy_harm(d, env):
    kt = gov(d, ["kernel", "trust"], env)
    rb = gov(d, ["rebuild-memory"], env)
    mq = gov(d, ["memory", "query", MARK], env)
    hits = [h.get("path") for h in ((mq.get("result") or {}).get("hits") or [])]
    return {"legacy_kernel_trust_ok": kt.get("ok"), "legacy_kernel_trust_code": code(kt), "legacy_verified": (kt.get("result") or {}).get("verified"),
            "rebuild_ok": rb.get("ok"), "rebuild_code": code(rb), "post_migration_classified_file_retrievable": [h for h in hits if h and "customers" in h]}


def prepare(tag):
    d = os.path.join(SCRATCH, tag)
    git(SCRATCH, "clone", "-q", L3, d)
    pre = git(d, "rev-parse", "HEAD~1").stdout.strip()   # the commit before the RoT-1 layout migration commit
    os.makedirs(d + "/product/customers", exist_ok=True)
    open(d + "/product/customers/acme.md", "w").write(f"# ACME\n{MARK} contract value and bank details\n")
    p = d + "/governance/overlay/DATA_SENSITIVITY.yaml"
    ds = yaml.safe_load(open(p))
    ds.setdefault("classifications", []).append({"pattern": "product/customers/**", "class": "restricted", "reason": "post-migration project classification"})
    yaml.safe_dump(ds, open(p, "w"), sort_keys=False)
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", "post-migration classification in governance/overlay")
    return d, pre


out = {"binary": GOV, "binary_sha256": hashlib.sha256(open(GOV, "rb").read()).hexdigest(), "L3": "<C build_base L3 in scratch>"}

# ---------------------------------------------------------------- RV3-D-A05 restore legacy governance paths with one Git command
res05 = {}
for tag, cmd in (("A05a_checkout_pre_governance", lambda d, pre: ["checkout", pre, "--", "governance"]),
                 ("A05b_checkout_pre_targeted", lambda d, pre: ["checkout", pre, "--", "governance/kernel", "governance/project", "governance/framework.lock"]),
                 ("A05c_restore_source_pre", lambda d, pre: ["restore", "--source", pre, "--staged", "--worktree", "--", "governance"])):
    d, pre = prepare(tag)
    env = env_for(tag)
    before = {"types": types(d), "trust": tree_digest(d + "/governance/trust"), "overlay": tree_digest(d + "/governance/overlay"),
              "legacy_status_code_before": code(gov(d, ["kernel", "trust"], env))}
    g = git(d, *cmd(d, pre), check=False)
    after = {"git_rc": g.returncode, "git_stderr": g.stderr[-300:], "types": types(d), "trust_digest_changed": tree_digest(d + "/governance/trust") != before["trust"],
             "trust_present": os.path.isdir(d + "/governance/trust"), "overlay_present": os.path.isdir(d + "/governance/overlay"),
             "overlay_still_classifies_customers": overlay_classifies(d, "product/customers/**"),
             "legacy_manifest_present": os.path.exists(d + "/governance/kernel/KERNEL_MANIFEST.json")}
    after.update(legacy_harm(d, env))
    res05[tag] = {"before": before, "after": after}
    if tag == "A05a_checkout_pre_governance":
        keep_a05a = (d, env)
out["RV3-D-A05_git_restore_of_legacy_paths"] = res05

# ---------------------------------------------------------------- RV3-D-A06 legacy CIT writes RoT-1 paths


def cit_chain(d, env, tag):
    t = gov(d, ["task", "create", "--class", "documentation", "--objective", "rv3d probe", "--title", "rv3d", "--status", "READY"], env)
    task = (t.get("result") or {}).get("id")
    mf = os.path.join(SCRATCH, f"manifest-{tag}.json")
    json.dump([{"op": "write_file", "path": "governance/overlay/DATA_SENSITIVITY.yaml", "content": "schema_version: 1.0.0\nclassifications: []\n"},
               {"op": "write_file", "path": "governance/trust/kernel/policies/SECURITY_POLICY.yaml", "content": "policy: SECURITY_POLICY\nnever_index_classes: []\n"},
               {"op": "delete_file", "path": "governance/trust/framework.lock"}], open(mf, "w"))
    tb, ob = tree_digest(d + "/governance/trust"), tree_digest(d + "/governance/overlay")
    lock_before = os.path.exists(d + "/governance/trust/framework.lock")
    steps = {"task_create": {"ok": t.get("ok"), "code": code(t), "id": task}}
    rbm = gov(d, ["rebuild-memory"], env)
    steps["rebuild_memory"] = {"ok": rbm.get("ok"), "code": code(rbm)}
    c = gov(d, ["cit", "propose", "--proposal", "rv3d change", "--trigger", "editorial", "--targets", task or "TASK-0001", "--manifest", mf], env)
    cid = (c.get("result") or {}).get("id") or "CIT-0001"
    steps["cit_propose"] = {"ok": c.get("ok"), "code": code(c), "id": cid, "msg": ((c.get("error") or {}).get("message") or "")[:200]}

    def step(name, args):
        r = gov(d, args, env)
        steps[name] = {"ok": r.get("ok"), "code": code(r), "msg": ((r.get("error") or {}).get("message") or "")[:240]}
        return r

    step("cit_simulate", ["cit", "simulate", cid])
    ap = step("cit_approve", ["cit", "approve", cid, "--by", "orchestrator", "--method", "auto"])
    import re as _re
    m = _re.search(r"(HDG-\d+)", json.dumps(ap.get("error") or {}))
    if not ap.get("ok") and m:
        gid = m.group(1)
        step("gate_present", ["gate", "present", gid])
        ap = step("cit_approve_after_present", ["cit", "approve", cid, "--by", "orchestrator", "--method", "auto"])
        if not ap.get("ok"):
            step("decide_gate", ["decide", gid, "--option", "A", "--by", "owner"])
            ap = step("cit_approve_after_decide", ["cit", "approve", cid, "--by", "owner", "--method", "human"])
    step("cit_execute", ["cit", "execute", cid])
    return {"steps": steps, "governance_trust_mutated": tree_digest(d + "/governance/trust") != tb, "governance_overlay_mutated": tree_digest(d + "/governance/overlay") != ob,
            "trust_framework_lock_deleted": lock_before and not os.path.exists(d + "/governance/trust/framework.lock"),
            "overlay_customers_classification_after": overlay_classifies(d, "product/customers/**")}


res06 = {}
d, env = keep_a05a
res06["on_A05a_restored_tree"] = cit_chain(d, env, "a05a")
# independent precondition: reviewer C's full occupation removal followed by legacy init --force
d6 = os.path.join(SCRATCH, "A06_full_removal"); git(SCRATCH, "clone", "-q", L3, d6); env6 = env_for("A06")
git(d6, "rm", "-q", "-r", *OCC); git(d6, "commit", "-q", "-m", "remove occupation entries")
init = gov(d6, ["init", "--force", "--name", "x", "--skip-index"], env6)
res06["on_full_removal_plus_init_force"] = {"init_force": {"ok": init.get("ok"), "code": code(init)}, **cit_chain(d6, env6, "full")}
# control: the intact layout (occupation present) must refuse before any write
dc = os.path.join(SCRATCH, "A06_control_intact"); git(SCRATCH, "clone", "-q", L3, dc); envc = env_for("A06c")
res06["control_intact_layout"] = cit_chain(dc, envc, "control")
out["RV3-D-A06_legacy_cit_writes_rot1_paths"] = res06

# ---------------------------------------------------------------- RV3-D-A07 untracking ignored-but-tracked files
d7 = os.path.join(SCRATCH, "A07"); git(SCRATCH, "clone", "-q", L3, d7)
listed = [x for x in git(d7, "ls-files", "-ci", "--exclude-standard").stdout.splitlines() if x]
for f in listed:
    git(d7, "rm", "-q", "--cached", f)
c7 = git(d7, "commit", "-q", "-m", "stop tracking ignored files", check=False)
d7c = os.path.join(SCRATCH, "A07_fresh_clone"); git(SCRATCH, "clone", "-q", d7, d7c)
out["RV3-D-A07_untrack_ignored_idiom"] = {"idiom_commit_created": c7.returncode == 0, "tracked_but_ignored_listed": listed, "occupation_in_fresh_clone_after": kind(d7c + "/.governance-runtime/migration"),
                                          "occupation_in_fresh_clone_of_L3": kind(os.path.join(SCRATCH, "A06_control_intact", ".governance-runtime/migration")),
                                          "rot1_state_by_18_s9": "PARTIAL(occupation)" if kind(d7c + "/.governance-runtime/migration") != "file" else "COMPLETE"}

print(json.dumps(out, indent=1, sort_keys=True, default=str))
