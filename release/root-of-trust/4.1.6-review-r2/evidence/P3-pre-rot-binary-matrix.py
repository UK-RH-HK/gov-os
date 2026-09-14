#!/usr/bin/env python3
"""P3 — Pre-RoT binaries against a project in the RoT-1 revision 2 trust format (`13` §3). Scratch only.

Extends the architect's F1 (which ran read-only commands and one `kernel reinstall`) to every destructive or exempt
command, for the real 4.1.5 binary and the real 4.1.2 binary, and to two alternative layouts that move the boundary
to "fail before any write".

Base project (built with 4.1.5): init 4.1.4 -> gated update to 4.1.5, which leaves the normal unconsumed update snapshot
`.governance-runtime/update/4.1.5/`. After that update the team adds project-owned strengthening: a DATA_SENSITIVITY
classification making `product/restricted-plan.md` restricted. The project is then rewritten into the RoT-1 layout
(4.1.5 payload stands in for the 4.1.6 kernel, as in F1).

Layouts:
  V0  pack layout: lock 2.0.0 with sentinels, tombstone KERNEL_MANIFEST.json, governance/trust/{FORMAT,release.dsse.json}
  V1  V0 + legacy lock path occupied by a directory (RoT-1 lock would live under governance/trust/)
  V3  V1 + legacy kernel path occupied by a regular file (RoT-1 kernel would live under governance/trust/)

For each binary x layout x command, on a fresh copy: ok/code; whether governance/ or spec/ changed; whether the
project-owned classification survived; the lock and tombstone state; the old binary's own trust view afterwards; whether
restricted material is retrievable through the old binary afterwards; and the installation state a RoT-1 binary would
compute (`18` §9) with the RoT-1 remedy's effect on the overlay (`20` §8: remedies write only Protected Paths).
"""
import hashlib, json, os, shutil, sqlite3, subprocess, tempfile
import yaml

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
GOV415 = os.environ.get("GOV415", REPO + "/target/release/gov")
GOV412 = os.environ.get("GOV412", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/f305345b-0820-4eb0-bb85-2afc50580a75/scratchpad/wt-412/target/release/gov")
SCRATCH = os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir()
S = tempfile.mkdtemp(prefix="p3-prerot-", dir=SCRATCH)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
SENT = "ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-verify-this-project"
MARK = "P3RESTRICTEDMARKER"
EXAMPLE_ENV = REPO + "/release/root-of-trust/4.1.6/examples/rev2/release-final.dsse.json"


def gov(binary, root, *a, role="orchestrator"):
    r = subprocess.run([binary, "--json", "--root", root, "--session", "S-p3", "--role", role, *a], env=ENV, capture_output=True, text=True, timeout=600)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True)


code = lambda d: (d.get("error") or {}).get("code")


def tree_hash(root, sub):
    h = hashlib.sha256()
    base = os.path.join(root, sub)
    if not os.path.exists(base):
        return "absent"
    if os.path.isfile(base) or os.path.islink(base):
        return "file:" + hashlib.sha256(open(base, "rb").read()).hexdigest()[:16]
    for dp, dns, fns in os.walk(base):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            h.update(os.path.relpath(p, root).encode() + b"\0" + (open(p, "rb").read() if os.path.isfile(p) else b"<dir>"))
    return h.hexdigest()[:16]


def classification_present(root):
    try:
        ds = yaml.safe_load(open(root + "/governance/project/DATA_SENSITIVITY.yaml"))
        return any(c.get("pattern") == "product/restricted-plan.md" for c in (ds.get("classifications") or []))
    except Exception:
        return None


def rot1_state(root, kernel_tree_before):
    """`18` §9 as specified, with `governance/trust/release.dsse.json` standing for the statement the kernel must match."""
    g = root + "/governance"
    if os.path.exists(g + "/trust/FORMAT"):
        try:
            fmt = json.load(open(g + "/trust/FORMAT"))
            if fmt.get("trust_format") != "rot-1":
                return {"state": "FORMAT_UNSUPPORTED"}
        except Exception:
            return {"state": "FORMAT_UNSUPPORTED(unparseable)"}
    tx = os.path.isdir(g + "/.tx") and any(os.path.exists(os.path.join(g, ".tx", d, "journal.json")) for d in os.listdir(g + "/.tx"))
    parts = {"lock": os.path.isfile(g + "/framework.lock"), "kernel_dir": os.path.isdir(g + "/kernel"),
             "FORMAT": os.path.isfile(g + "/trust/FORMAT"), "statement": os.path.isfile(g + "/trust/release.dsse.json")}
    if tx:
        st = "IN_TRANSACTION"
    elif not any(parts.values()):
        st = "ABSENT"
    elif all(parts.values()):
        st = "COMPLETE"
    else:
        st = "PARTIAL"
    verdict = None
    if st == "COMPLETE":
        verdict = "INTACT(matches statement)" if tree_hash(root, "governance/kernel") == kernel_tree_before else "KERNEL_TAMPERED"
    return {"state": st, "components": parts, "kernel_vs_statement": verdict,
            "overlay_restored_by_rot1_remedy": False}  # 20 §8 remedies are install transactions over Protected Paths only


def build_base():
    root = S + "/base"
    os.makedirs(root)
    git(root, "init", "-q"); git(root, "commit", "-q", "--allow-empty", "-m", "i")
    b = {"init_4.1.4": gov(GOV415, root, "init", "--source", REPO + "/release/releases/4.1.4", "--name", "p3", "--skip-index").get("ok")}
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "4.1.4")
    first = gov(GOV415, root, "update", "--apply", "--source", REPO + "/release/releases/4.1.5")
    gid = ((first.get("error") or {}).get("details") or {}).get("gate")
    b["present"] = gov(GOV415, root, "gate", "present", gid).get("ok")
    b["decide"] = gov(GOV415, root, "decide", gid, "--option", "A", "--by", "owner").get("ok")
    ap = gov(GOV415, root, "update", "--apply", "--approve", "--source", REPO + "/release/releases/4.1.5")
    b["update_to_4.1.5_applied"] = (ap.get("result") or {}).get("applied")
    b["unconsumed_update_snapshot"] = os.path.exists(root + "/.governance-runtime/update/4.1.5/snapshot.json")
    # project-owned strengthening added after the update
    os.makedirs(root + "/product", exist_ok=True)
    open(root + "/product/restricted-plan.md", "w").write(f"# Plan\n\n{MARK} proprietary customer terms\n")
    dsp = root + "/governance/project/DATA_SENSITIVITY.yaml"
    ds = yaml.safe_load(open(dsp))
    ds.setdefault("classifications", []).append({"pattern": "product/restricted-plan.md", "class": "restricted", "reason": "customer terms"})
    yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
    git(root, "add", "-A"); git(root, "commit", "-q", "-m", "classify")
    gov(GOV415, root, "rebuild-memory")
    b["control_restricted_retrievable_before_rot1"] = retrievable(GOV415, root)
    b["kernel_trust_verified_before_rot1"] = (gov(GOV415, root, "kernel", "trust").get("result") or {}).get("verified")
    return root, b


def retrievable(binary, root):
    q = gov(binary, root, "memory", "query", MARK)
    return [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if "restricted-plan" in (h.get("path") or "")]


def to_layout(src, dst, layout):
    shutil.copytree(src, dst, symlinks=True)
    g = dst + "/governance"
    lock = yaml.safe_load(open(g + "/framework.lock"))
    lock.update({"lock_schema_version": "2.0.0", "trust_format": "rot-1", "kernel_manifest_hash": SENT, "release_hash": SENT,
                 "kernel": {"tree_digest": "sha256:" + "0" * 64, "manifest_digest": "sha256:" + "0" * 64},
                 "release_statement_digest": "sha256:" + "a" * 64, "source": "release:agentic-engineering-os@4.1.6"})
    m = json.load(open(g + "/kernel/KERNEL_MANIFEST.json"))
    m.update({"trust_format": "rot-1", "notice": SENT, "files": {"TRUST-FORMAT-ROT-1/requires-gov-4.1.6": "0" * 64}, "payload_hash": SENT})
    os.makedirs(g + "/trust/state", exist_ok=True)
    open(g + "/trust/FORMAT", "w").write('{"minimum_reader":"4.1.6","trust_format":"rot-1"}')
    shutil.copy(EXAMPLE_ENV, g + "/trust/release.dsse.json")
    if layout == "V0":
        yaml.safe_dump(lock, open(g + "/framework.lock", "w"), sort_keys=False)
        json.dump(m, open(g + "/kernel/KERNEL_MANIFEST.json", "w"), indent=2)
    if layout in ("V1", "V3"):
        os.remove(g + "/framework.lock")
        os.makedirs(g + "/framework.lock")
        open(g + "/framework.lock/ROT-1-TRUST-FORMAT-requires-gov-4.1.6", "w").write(SENT + "\n")
        yaml.safe_dump(lock, open(g + "/trust/framework.lock", "w"), sort_keys=False)
        json.dump(m, open(g + "/kernel/KERNEL_MANIFEST.json", "w"), indent=2)
    if layout == "V3":
        shutil.move(g + "/kernel", g + "/trust/kernel")
        open(g + "/kernel", "w").write(SENT + "\n")
    git(dst, "add", "-A"); git(dst, "commit", "-q", "-m", f"rot-1 layout {layout}")
    return dst


COMMANDS = {
    "kernel_verify": ["kernel", "verify"],
    "doctor": ["doctor"],
    "task_create": ["task", "create", "--title", "x", "--objective", "y", "--class", "implementation"],
    "rebuild_memory": ["rebuild-memory"],
    "update_rollback": ["update", "--rollback"],
    "init_force": None,  # per binary
    "kernel_reinstall": ["kernel", "reinstall"],
    "recover": ["recover"],
}


def run_matrix(base):
    res = {}
    for layout in ("V0", "V1", "V3"):
        lay = to_layout(base, f"{S}/layout-{layout}", layout)
        kt = tree_hash(lay, "governance/kernel") if layout != "V3" else tree_hash(lay, "governance/trust/kernel")
        res[layout] = {}
        for bname, binary, own in (("4.1.5", GOV415, "4.1.5"), ("4.1.2", GOV412, "4.1.2")):
            res[layout][bname] = {}
            for cname, args in COMMANDS.items():
                c = f"{S}/run-{layout}-{bname}-{cname}"
                shutil.copytree(lay, c, symlinks=True)
                before = {s: tree_hash(c, s) for s in ("governance", "spec")}
                if args is None:
                    args = ["init", "--force", "--source", f"{REPO}/release/releases/{own}", "--name", "p3", "--skip-index"]
                r = gov(binary, c, *args)
                after = {s: tree_hash(c, s) for s in ("governance", "spec")}
                row = {"ok": r.get("ok"), "code": code(r), "governance_changed": before["governance"] != after["governance"],
                       "spec_changed": before["spec"] != after["spec"], "project_classification_survives": classification_present(c)}
                lk = c + "/governance/framework.lock"
                row["legacy_lock"] = ("dir" if os.path.isdir(lk) else ("rot1-sentinel" if SENT in open(lk).read() else "overwritten-1.1.0")) if os.path.exists(lk) else "absent"
                mp = c + "/governance/kernel/KERNEL_MANIFEST.json"
                row["tombstone"] = ("present" if SENT in open(mp).read() else "overwritten") if os.path.isfile(mp) else ("kernel-path-is-file" if os.path.isfile(c + "/governance/kernel") else "absent")
                if r.get("ok") and row["governance_changed"]:
                    if bname == "4.1.5":
                        row["old_binary_kernel_trust_verified_after"] = (gov(binary, c, "kernel", "trust").get("result") or {}).get("verified")
                    else:
                        row["old_binary_kernel_verify_ok_after"] = ((gov(binary, c, "kernel", "verify").get("result") or {}).get("ok"))
                    gov(binary, c, "rebuild-memory")
                    row["restricted_retrievable_via_old_binary_after"] = retrievable(binary, c)
                row["rot1_view"] = rot1_state(c, kt) if layout == "V0" else "n/a (alternative layout; RoT-1 would read governance/trust/)"
                res[layout][bname][cname] = row
    return res


base, b = build_base()
out = {"scratch": S, "binaries": {"4.1.5": subprocess.run([GOV415, "--version"], capture_output=True, text=True).stdout.strip(),
                                   "4.1.2": subprocess.run([GOV412, "--version"], capture_output=True, text=True).stdout.strip()},
       "base": b, "matrix": run_matrix(base)}
print(json.dumps(out, indent=2))
