#!/usr/bin/env python3
"""RV3-B-A03, A14, A16 — held-out probes by review r3 B (AR-0002). Scratch only; the repository is never written.

A03  Same-account writers of anchor and trust-decision files. `24` §3.2 and `27` §3.2 place state pins and operator
     decision pins in `<account-home>/.config/gov/`, and TA-9 assumes the repository writer does not control them. This
     probe shows the real 4.1.5 `gov verify product` executing a command that a repository writer committed
     (`PROJECT_POLICY.tests.product_test_command`, `runtime/src/verification/mod.rs:956-1001`) as the invoking account, and
     that command writing both files. HOME points into scratch; the account-database home is only inspected (os.access),
     never written.

A14  Parser differential. The architecture reference checker parses kernel YAML with PyYAML (YAML 1.1: `on`/`off`/`yes`/
     `no` are booleans); the 4.1.5 runtime parses with serde_yaml. A kernel writing `on` for a `bool_toward` floor passes
     the checker, while the runtime reads a string.

A16  `project_tunable` leaves read by runtime decision points. A kernel changing only such leaves passes the checker; the
     runtime consumers are cited by path.

Environment: GOV (default legacy 4.1.5), REVIEW_REPO (worktree), GOV_REVIEW_SCRATCH. GOV_* stripped; GOV_KERNEL_CACHE and
HOME in scratch.
"""
import json, os, pwd, re, shutil, subprocess, sys, tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("REVIEW_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PACK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
sys.path.insert(0, os.path.join(PACK, "constitutional-surface"))
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

GOV = os.environ.get("GOV", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.5")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
INV = yaml.safe_load(open(os.path.join(PACK, "constitutional-surface", "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
SCRATCH = os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir()
S = tempfile.mkdtemp(prefix="rv3b-a03-", dir=SCRATCH)
HOME = S + "/home"
os.makedirs(HOME, exist_ok=True)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
ENV["HOME"] = HOME
out = {"binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip(), "scratch": "<scratch>"}


def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-rv3b-a03", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-400:], "stderr": r.stderr[-400:]}


def git(root, *a, who="victim"):
    subprocess.run(["git", "-c", f"user.name={who}", "-c", f"user.email={who}@x", *a], cwd=root, check=True, capture_output=True)


def ydump(p, d):
    with open(p, "w") as fh:
        yaml.safe_dump(d, fh, sort_keys=False)


code = lambda d: (d.get("error") or {}).get("code")

# ------------------------------------------------------------------------------------------------ A03
root = S + "/consumer-a03"
os.makedirs(root)
git(root, "init", "-q"); git(root, "commit", "-q", "--allow-empty", "-m", "i")
init = gov(root, "orchestrator", "init", "--source", REL, "--name", "rv3ba03", "--skip-index")
git(root, "add", "-A"); git(root, "commit", "-q", "-m", "installed")
PIN = {"lineage": "sha256:" + "11" * 32, "root_version": 1, "root_digest": "sha256:" + "22" * 32, "policy_version": 2, "policy_digest": "sha256:" + "33" * 32,
       "state_sequence": 5, "state_digest": "sha256:" + "44" * 32, "provisioned_by": "ci-runner-image", "provisioned_at": "2026-09-14T00:00:00Z"}
DECISION = {"gate_kind": "framework_update", "bound_digests": ["sha256:" + "55" * 32, "sha256:" + "66" * 32], "project_trust_id": "*"}
script = ("umask 022; d=\"$HOME/.config/gov\"; mkdir -p \"$d\"; "
          f"printf '%s\\n' '{json.dumps(PIN)}' > \"$d/trust-state-pins\"; "
          f"printf '%s\\n' '{json.dumps(DECISION)}' > \"$d/approved-trust-decisions\"; "
          "echo uid=$(id -u) home=$HOME")
pp = os.path.join(root, "governance", "project", "PROJECT_POLICY.yaml")
doc = yaml.safe_load(open(pp))
doc.setdefault("tests", {})["product_test_command"] = ["sh", "-c", script]
ydump(pp, doc)
git(root, "add", "-A"); git(root, "commit", "-q", "-m", "ci: run product tests", who="a2-collaborator")
ver = gov(root, "orchestrator", "verify", "product")
res = ver.get("result") or {}
pin_path, dec_path = HOME + "/.config/gov/trust-state-pins", HOME + "/.config/gov/approved-trust-decisions"


def info(p):
    if not os.path.exists(p):
        return {"exists": False}
    st = os.stat(p)
    return {"exists": True, "owner_uid": st.st_uid, "mode": oct(st.st_mode & 0o777), "content": open(p).read().strip()}


acct = pwd.getpwuid(os.getuid())
cfg = os.path.join(acct.pw_dir, ".config")
out["A03_same_account_writer"] = {
    "init_ok": init.get("ok"), "verify_product_ok": ver.get("ok"), "verify_product_code": code(ver), "ran": res.get("ran"), "source": res.get("source"),
    "stdout_tail": res.get("stdout_tail"), "invoking_uid": os.getuid(),
    "trust_state_pins": info(pin_path), "approved_trust_decisions": info(dec_path),
    "account_database_home_writable_by_invoking_uid": os.access(acct.pw_dir, os.W_OK),
    "account_database_home_config_dir_exists_and_writable": os.path.isdir(cfg) and os.access(cfg, os.W_OK),
    "note": "HOME was redirected into scratch for the probe; revision 3 resolves <account-home> from the account database, which is the same account's home (inspected, not written)."}
out["A03_verdict"] = {"repository_committed_command_executed_by_gov_as_invoking_account": bool(res.get("ran")) and f"uid={os.getuid()}" in (res.get("stdout_tail") or ""),
                      "pin_and_decision_pin_written_by_that_process": info(pin_path).get("exists") and info(dec_path).get("exists") and info(pin_path).get("owner_uid") == os.getuid()}

# ------------------------------------------------------------------------------------------------ A14
bool_leaves = [(f["path"], l["key"]) for f in INV["files"] if f.get("mode") == "structured" for l in f["leaves"] if l["class"] == "floor" and l.get("op") == "bool_toward" and l.get("strict") is True]
a14_rows = []


def set_token(kdir, rel, key, token):
    p = os.path.join(kdir, rel)
    d = yaml.safe_load(open(p))
    segs = key.split(".")[1:]
    cur = d
    for s in segs[:-1]:
        cur = cur[s]
    cur[segs[-1]] = "__TOKEN__"
    txt = yaml.safe_dump(d, sort_keys=False)
    assert txt.count("__TOKEN__") == 1
    open(p, "w").write(txt.replace("__TOKEN__", token))
    return yaml.safe_load(open(p))


for rel, key in bool_leaves:
    if "[" in key:
        continue
    k = f"{S}/a14-{key.replace('.', '_')}"
    shutil.copytree(REL, k)
    set_token(k + "/kernel", rel, key, "on")
    rep = C.run_check(k + "/kernel", INV, quiet=True)
    parsed = yaml.safe_load(open(os.path.join(k, "kernel", rel)))
    cur = parsed
    for s in key.split(".")[1:]:
        cur = cur.get(s) if isinstance(cur, dict) else None
    a14_rows.append({"key": key, "file": rel, "token": "on", "pyyaml_value": cur, "csi_check_exit": rep["exit"], "src": k})
out["A14_checker_rows"] = [{x: r[x] for x in r if x != "src"} for r in a14_rows]
# consume one on the real 4.1.5 binary and read the runtime's parsed value
target = next((r for r in a14_rows if r["key"] == "TOOL_POLICY.plugins.refuse_on_pin_drift"), a14_rows[0] if a14_rows else None)
if target:
    croot = S + "/consumer-a14"
    os.makedirs(croot)
    git(croot, "init", "-q"); git(croot, "commit", "-q", "--allow-empty", "-m", "i")
    ci = gov(croot, "orchestrator", "init", "--source", target["src"], "--name", "rv3ba14", "--skip-index")
    polname = target["key"].split(".")[0]
    eff = gov(croot, "orchestrator", "policy", "effective", polname)
    r = eff.get("result") or {}
    pol = r.get("effective") or r.get("policy") or {}
    cur = pol
    for s in target["key"].split(".")[1:]:
        cur = cur.get(s) if isinstance(cur, dict) else None
    trust = gov(croot, "orchestrator", "kernel", "trust")
    out["A14_runtime"] = {"key": target["key"], "init_ok": ci.get("ok"), "kernel_trust_verified": (trust.get("result") or {}).get("verified"),
                          "runtime_value": cur, "runtime_value_type": type(cur).__name__, "pyyaml_value": target["pyyaml_value"], "csi_check_exit": target["csi_check_exit"]}

# ------------------------------------------------------------------------------------------------ A16
k16 = S + "/a16"
shutil.copytree(REL, k16)
changes = {
    ("policies/MEMORY_POLICY.yaml", "MEMORY_POLICY.embedding.provider"): "project-embed-plugin",
    ("policies/ARCHIVE_POLICY.yaml", "ARCHIVE_POLICY.default_retrieval_for_archive"): True,
    ("policies/LEARNING_POLICY.yaml", "LEARNING_POLICY.upstream.aggregate_metrics_enabled"): True,
    ("policies/HUMAN_GATE_POLICY.yaml", "HUMAN_GATE_POLICY.continue_independent_work"): True,
}
before = {}
for (rel, key), val in changes.items():
    p = os.path.join(k16, "kernel", rel)
    d = yaml.safe_load(open(p))
    cur = d
    segs = key.split(".")[1:]
    for s in segs[:-1]:
        cur = cur[s]
    before[key] = cur.get(segs[-1])
    cur[segs[-1]] = val
    ydump(p, d)
rep16 = C.run_check(k16 + "/kernel", INV, quiet=True)
classes = {l["key"]: l["class"] for f in INV["files"] if f.get("mode") == "structured" for l in f["leaves"]}
out["A16_project_tunable_consumers"] = {
    "changes": {k: {"genuine": before[k], "tampered": v, "class": classes.get(k)} for (_, k), v in changes.items()},
    "csi_check_exit": rep16["exit"],
    "runtime_consumers": {"MEMORY_POLICY.embedding.provider": "runtime/src/memory/embedder.rs:27,125 (non-builtin id selects an `embed` plugin; indexed text is sent to it)",
                          "ARCHIVE_POLICY.default_retrieval_for_archive": "runtime/src/project.rs:170; runtime/src/paths.rs:288 (default retrieval of `historical` paths)",
                          "LEARNING_POLICY.upstream.aggregate_metrics_enabled": "runtime/src/upstream.rs:140 (upstream packet content)",
                          "HUMAN_GATE_POLICY.continue_independent_work": "runtime/src/status.rs:112 (work continues while a gate is pending)"},
    "23_s6_5_security_decision_points": "authority, secret and sensitivity classification, indexing and export, gate answering, plugin and tool authorisation and installation, precedence and exceptions, install authority, upstream export"}
print(json.dumps(out, indent=1, default=str))
