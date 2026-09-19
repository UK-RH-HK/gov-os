#!/usr/bin/env python3
"""P2-AR-0032 (round-2 integration builder) — the G0 registration of every subcommand the round-2 workstreams added
(P2-HO-0030 "Guard registration"), observed through the integrated binary. Integration evidence only (Contract v3 O3).

Labels (from `control::COMMAND_GUARDS` as merged): WS-2 `health qualify`; WS-3 `memory miss`, `memory failures`; WS-4
`cit classify`, `cit propagate`, `cit propagate --dry-run`, `context staleness`, `checkpoint freshness`, `session close`;
WS-6 `memory integrity`, `memory profile` (and `memory select --gate`, which keeps the existing `memory select` label);
WS-10 `research|experiment|data|scenario` (20 labels). WS-7 and WS-9/11 added no subcommand.

R0  the registration read from the source: each label once, with the class stated in the integration report.
R1  unfrozen: every Read label runs on a project holding the records it reads (a feature chain, a task with a packet
    and a checkpoint, concluded research, a designed experiment, an undetected direct upstream edit) and changes no
    governed file (spec/, governance/, framework.json, every tracked file) — i.e. Read is its true class.
R2  under FREEZE_WRITES and under PAUSE: every Write label is refused FROZEN / PAUSED (exit 4) and changes no governed
    file; every Read label still runs (not refused by the control, not G0_UNCLASSIFIED) and changes no governed file.
R3  authority: an undeclared invocation carries no privileged authority (WS-3 BC-P2-08) — every Write label of an L1+
    class is refused AUTHORITY_DENIED for it; `health qualify` (record_audit, L0) is treated exactly as `audit`.
R4  the unfrozen Write labels really write (so the Write class is not a mis-registration of a read): `cit propagate`
    propagates the detected direct edit, `session close` writes a checkpoint, `research sync` / `memory miss` record.

Usage: GOV=<gov> P2AR0032_SCRATCH=<dir> python3 round2_labels_g0_probe.py
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GOV = os.environ.get("GOV", os.path.join(WT, "target", "release", "gov"))
SCR = os.environ.get("P2AR0032_SCRATCH") or tempfile.mkdtemp(prefix="p2ar0032-g0-")
os.makedirs(SCR, exist_ok=True)
RESULTS = []


def check(name, ok, what, detail=None):
    RESULTS.append((name, bool(ok)))
    print(f"CHECK {name} {'PASS' if ok else 'FAIL'} {what}", flush=True)
    if detail is not None:
        print("      detail:", json.dumps(detail, sort_keys=True, default=str)[:4000], flush=True)


def env_for(root):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GOV_") and not k.startswith("XDG_")}
    e.update({"GOV_CANONICAL_ROOT": WT, "XDG_STATE_HOME": root + ".machine", "XDG_CACHE_HOME": root + ".cache",
              "HOME": root + ".home", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "p",
              "GIT_AUTHOR_EMAIL": "p@example.invalid", "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@example.invalid",
              "PYTHONDONTWRITEBYTECODE": "1"})
    os.makedirs(e["HOME"], exist_ok=True)
    return e


def gov(root, *args, role="orchestrator", session="S-g0"):
    cmd = [GOV, "--json", "--root", root, "--session", session]
    if role:
        cmd += ["--role", role]
    cmd += list(args)
    p = subprocess.run(cmd, capture_output=True, text=True, env=env_for(root), cwd=SCR)
    try:
        v = json.loads(p.stdout)
    except Exception:
        v = {"ok": False, "error": {"code": "NON_JSON", "message": (p.stdout + p.stderr)[-400:]}}
    v["_exit"] = p.returncode
    return v


def must(v, what):
    assert v.get("ok"), f"{what}: {json.dumps(v)[:1500]}"
    return v["result"]


def code(v):
    return (v.get("error") or {}).get("code")


def git(root, *a):
    return subprocess.run(["git", *a], cwd=root, env=env_for(root), capture_output=True, text=True)


def governed_hash(root):
    """Governed state: every file under spec/ and governance/, framework.json, and every tracked file."""
    h = hashlib.sha256()
    paths = set(git(root, "ls-files").stdout.split())
    for base in ("spec", "governance"):
        for d, _, fs in os.walk(os.path.join(root, base)):
            for f in fs:
                paths.add(os.path.relpath(os.path.join(d, f), root))
    if os.path.exists(os.path.join(root, "framework.json")):
        paths.add("framework.json")
    for rel in sorted(paths):
        p = os.path.join(root, rel)
        h.update(rel.encode())
        h.update(open(p, "rb").read() if os.path.isfile(p) else b"<absent>")
    return h.hexdigest()


def changed_governed(root, before_files):
    now = governed_files(root)
    return sorted(k for k in set(before_files) | set(now) if before_files.get(k) != now.get(k))


def governed_files(root):
    out = {}
    paths = set(git(root, "ls-files").stdout.split())
    for base in ("spec", "governance"):
        for d, _, fs in os.walk(os.path.join(root, base)):
            for f in fs:
                paths.add(os.path.relpath(os.path.join(d, f), root))
    for rel in sorted(paths):
        p = os.path.join(root, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None
    return out


# ------------------------------------------------------------------------------------------------ R0 registration
src = open(os.path.join(WT, "runtime/src/orchestration/control.rs")).read()
table = src.split("pub const COMMAND_GUARDS")[1].split("];")[0]
entries = re.findall(r'\b(g|outside)\("([^"]+)",\s*"([^"]*)"(?:,\s*(Read|Write))?\)', table)
count = {}
for _, label, _, _ in entries:
    count[label] = count.get(label, 0) + 1
guards = {label: (kind, cls, eff) for kind, label, cls, eff in entries}
WRITE = {"health qualify": "record_audit", "memory miss": "record_failure_memory", "cit propagate": "simulate_cit",
         "session close": "checkpoint", "memory select": "memory_select"}
for l in ("research record", "research update", "research conclude", "research withdraw", "research sync",
          "experiment design", "experiment update", "experiment run", "experiment reproduce", "experiment conclude",
          "experiment abandon", "data register"):
    WRITE[l] = "mutate_spec_other"
WRITE["experiment promote"] = "approve_cit_human"
READ = ["memory failures", "memory integrity", "memory profile", "cit classify", "cit propagate --dry-run",
        "context staleness", "checkpoint freshness", "research show", "research check", "experiment show",
        "experiment check", "data show", "scenario trace", "scenario check"]
reg = {l: guards.get(l) for l in list(WRITE) + READ}
check("R0.registered",
      all(guards.get(l) == ("g", c, "Write") for l, c in WRITE.items())
      and all(guards.get(l) == ("g", "read", "Read") for l in READ)
      and all(count.get(l) == 1 for l in list(WRITE) + READ)
      and all(n == 1 for n in count.values()),
      "every round-2 label is classified exactly once in COMMAND_GUARDS, at the class stated in the integration report "
      f"({len(WRITE)} Write incl. the existing `memory select`, {len(READ)} Read); no label appears twice in the table "
      f"({len(count)} labels)", {"labels": reg, "duplicates": {k: n for k, n in count.items() if n != 1}})
authority = open(os.path.join(WT, "framework/policies/AUTHORITY_POLICY.yaml")).read()
check("R0.classes-declared",
      all(re.search(rf"^\s+{re.escape(c)}:\s*L\d", authority, flags=re.M) for c in set(WRITE.values()) | {"read"}),
      "every authority class these labels name is declared in the kernel AUTHORITY_POLICY",
      {c: bool(re.search(rf"^\s+{re.escape(c)}:\s*L\d", authority, flags=re.M)) for c in sorted(set(WRITE.values()) | {"read"})})

# ------------------------------------------------------------------------------------------------ a populated project
root = os.path.join(SCR, "proj")
if os.path.exists(root):
    shutil.move(root, root + f".old-{os.getpid()}")
shutil.copytree(os.path.join(WT, "fixtures", "greenfield", "project"), root)
for a in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "fixture"]):
    git(root, *a)
must(gov(root, "init", "--name", "g0", "--alias", "g0"), "init (bootstrap: the binary's own payload)")


def wy(rel, doc):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    import yaml  # noqa: PLC0415
    open(p, "w").write(yaml.safe_dump(doc, sort_keys=False))


wy("spec/features/F-0001.yaml", {"id": "F-0001", "type": "feature", "title": "Totals", "status": "ACTIVE",
                                 "state_class": "AUTHORITATIVE", "requirements": ["REQ-0001"], "scenarios": ["SCN-0001"],
                                 "readiness": {"requirements": "PRESENT"}})
wy("spec/requirements/REQ-0001.yaml", {"id": "REQ-0001", "type": "requirement", "title": "Totals are exact",
                                       "status": "ACTIVE", "state_class": "AUTHORITATIVE", "feature": "F-0001",
                                       "kind": "functional", "statement": "totals are integer cents",
                                       "acceptance_criteria": ["2 x 199 = 398"]})
wy("spec/scenarios/SCN-0001.yaml", {"id": "SCN-0001", "type": "scenario", "title": "Cart total", "status": "ACTIVE",
                                    "state_class": "AUTHORITATIVE", "feature": "F-0001", "requirements": ["REQ-0001"],
                                    "then": ["total is 398"], "success_criteria": ["exact"], "failure_criteria": ["drift"]})
git(root, "add", "-A")
git(root, "commit", "-qm", "spec")
must(gov(root, "rebuild-memory"), "rebuild-memory")
task = must(gov(root, "task", "create", "--class", "documentation", "--objective", "document totals", "--status", "READY",
                "--fields", json.dumps({"requirements": ["REQ-0001"], "scenarios": ["SCN-0001"]})), "task create")["id"]
must(gov(root, "context", "compile", task), "context compile")
ckpt = must(gov(root, "checkpoint", "create", "--task", task, "--next-action", "continue"), "checkpoint")["id"]
res = must(gov(root, "research", "record", "--fields", json.dumps({
    "title": "Rounding study", "question": "Do totals drift?", "reason": "exactness", "method": "enumerate carts",
    "sources": ["internal benchmark"], "measurements": [{"name": "drift", "value": 0}], "uncertainty": "small sample",
    "conclusion": "integer cents never drift", "confidence": 0.8})), "research record")
res_id = sorted(f[:-5] for f in os.listdir(os.path.join(root, "spec/research")) if f.endswith(".yaml"))[-1]
exp = must(gov(root, "experiment", "design", "--fields", json.dumps({
    "title": "Cart enumeration", "hypothesis": "no drift", "method": "enumerate carts", "data_provenance": "synthetic",
    "outputs": ["spec/experiments/carts/"]})), "experiment design")
exp_id = sorted(f[:-5] for f in os.listdir(os.path.join(root, "spec/experiments")) if f.endswith(".yaml"))[-1]
git(root, "add", "-A")
git(root, "commit", "-qm", "populated")
# an upstream change made directly (not through a CIT), not yet propagated
req = os.path.join(root, "spec/requirements/REQ-0001.yaml")
open(req, "w").write(open(req).read().replace("totals are integer cents", "totals are integer cents, rounded half-even"))
git(root, "add", "-A")
git(root, "commit", "-qm", "direct upstream edit")
must(gov(root, "rebuild-memory", "--incremental"), "rebuild-memory --incremental")
print(f"# project {root}; task {task}; checkpoint {ckpt}; research {res_id}; experiment {exp_id}", flush=True)

ORACLE = os.path.join(WT, "release/capability-baseline/repair-1/ws01-12/evidence/bc-p2-51/samples/format-sample.oracle.json")
WRITE_ARGS = {
    "health qualify": ["health", "qualify", "--oracle", ORACLE, "--report", ORACLE],
    "memory miss": ["memory", "miss", "--query", "where is the rounding rule?"],
    "cit propagate": ["cit", "propagate"],
    "session close": ["session", "close"],
    "memory select": ["memory", "select", "builtin:64", "--gate", "HDG-9999"],
    "research record": ["research", "record", "--draft", "--fields", json.dumps({"title": "draft", "question": "q?"})],
    "research update": ["research", "update", res_id, "--fields", "{}"],
    "research conclude": ["research", "conclude", res_id],
    "research withdraw": ["research", "withdraw", res_id, "--reason", "probe"],
    "research sync": ["research", "sync"],
    "experiment design": ["experiment", "design", "--fields", json.dumps({"title": "x", "hypothesis": "h", "method": "m",
                                                                          "data_provenance": "synthetic"})],
    "experiment update": ["experiment", "update", exp_id, "--fields", "{}"],
    "experiment run": ["experiment", "run", exp_id, "--results", json.dumps({"drift": 0})],
    "experiment reproduce": ["experiment", "reproduce", exp_id, "--results", json.dumps({"drift": 0})],
    "experiment conclude": ["experiment", "conclude", exp_id, "--fields", "{}"],
    "experiment abandon": ["experiment", "abandon", exp_id, "--reason", "probe"],
    "experiment promote": ["experiment", "promote", exp_id, "--paths", "src/lib.rs"],
    "data register": ["data", "register", "--fields", json.dumps({"title": "d"})],
}
READ_ARGS = {
    "memory failures": ["memory", "failures"],
    "memory integrity": ["memory", "integrity"],
    "memory profile": ["memory", "profile"],
    "cit classify": ["cit", "classify", "--paths", "spec/requirements/REQ-0001.yaml", "--base", "HEAD~1"],
    "cit propagate --dry-run": ["cit", "propagate", "--dry-run"],
    "context staleness": ["context", "staleness", task],
    "checkpoint freshness": ["checkpoint", "freshness", ckpt],
    "research show": ["research", "show", res_id],
    "research check": ["research", "check"],
    "experiment show": ["experiment", "show", exp_id],
    "experiment check": ["experiment", "check"],
    "data show": ["data", "show", "DATA-0001"],
    "scenario trace": ["scenario", "trace", "F-0001"],
    "scenario check": ["scenario", "check"],
}
assert set(WRITE_ARGS) == set(WRITE) and set(READ_ARGS) == set(READ)


def run_reads(tag):
    rows = {}
    for label, args in READ_ARGS.items():
        before = governed_files(root)
        v = gov(root, *args)
        rows[label] = {"ok": v.get("ok"), "code": code(v), "governed_changed": changed_governed(root, before)}
    return rows


# ------------------------------------------------------------------------------------------------ R1 unfrozen reads
rows = run_reads("unfrozen")
check("R1.reads-write-nothing",
      all(r["code"] not in ("G0_UNCLASSIFIED", "FROZEN", "PAUSED") and not r["governed_changed"] for r in rows.values())
      and all(rows[l]["ok"] for l in READ if l != "data show"),
      "every round-2 Read label runs on records it reads (all succeed; `data show` of an unknown id answers typed) and "
      "changes no governed file", rows)
stale = must(gov(root, "context", "staleness", task), "context staleness")
check("R1.detection-is-read",
      any(x.get("id") == "REQ-0001" and x.get("propagated") is False for x in stale.get("stale_inputs", [])),
      "the direct upstream edit is detected by the read-only `context staleness` and stays unpropagated after every read "
      "(`cit propagate --dry-run` included)", stale.get("stale_inputs"))

# ------------------------------------------------------------------------------------------------ R2 emergency controls
for mode, refusal in (("freeze-writes", "FROZEN"), ("pause", "PAUSED")):
    must(gov(root, mode, "--reason", "g0 probe"), mode)
    rows = {}
    for label, args in WRITE_ARGS.items():
        before = governed_files(root)
        v = gov(root, *args)
        rows[label] = {"code": code(v), "exit": v["_exit"], "governed_changed": changed_governed(root, before)}
    check(f"R2.{mode}.writes-refused",
          all(x["code"] == refusal and x["exit"] == 4 and not x["governed_changed"] for x in rows.values()),
          f"under {mode.upper()} every round-2 Write label is refused {refusal} (exit 4) and changes no governed file", rows)
    rows = run_reads(mode)
    check(f"R2.{mode}.reads-run",
          all(x["code"] not in ("FROZEN", "PAUSED", "G0_UNCLASSIFIED") and not x["governed_changed"] for x in rows.values()),
          f"under {mode.upper()} every round-2 Read label runs (not refused by the control) and changes no governed file",
          rows)
    must(gov(root, "resume"), "resume")

# ------------------------------------------------------------------------------------------------ R3 authority
rows = {}
for label, args in WRITE_ARGS.items():
    if label == "health qualify":
        continue
    before = governed_files(root)
    v = gov(root, *args, role=None)
    rows[label] = {"code": code(v), "governed_changed": changed_governed(root, before)}
check("R3.undeclared-refused", all(x["code"] == "AUTHORITY_DENIED" and not x["governed_changed"] for x in rows.values()),
      "an undeclared invocation of every round-2 Write label of an L1+ class is refused AUTHORITY_DENIED and writes nothing",
      rows)
ref_l0 = gov(root, "audit", "--no-persist", role="independent-auditor")
q_l0 = gov(root, *WRITE_ARGS["health qualify"], role="independent-auditor")
check("R3.health-qualify-record-audit",
      code(q_l0) != "AUTHORITY_DENIED" and code(ref_l0) != "AUTHORITY_DENIED",
      "`health qualify` (record_audit, L0) is authorised for a declared L0 auditor exactly like `audit`; its refusal here is "
      "the command's own validation of the sample documents, not an authority decision",
      {"audit --no-persist (L0)": ref_l0.get("ok") or code(ref_l0), "health qualify (L0)": q_l0.get("ok") or code(q_l0)})

# ------------------------------------------------------------------------------------------------ R4 the writes write
out = {}
before = governed_files(root)
v = gov(root, "cit", "propagate")
out["cit propagate"] = {"ok": v.get("ok"), "propagated": (v.get("result") or {}).get("propagated"),
                        "governed_changed": len(changed_governed(root, before))}
before = governed_files(root)
v = gov(root, "session", "close", "--task", task)
out["session close"] = {"ok": v.get("ok"), "governed_changed": len(changed_governed(root, before))}
before = governed_files(root)
v = gov(root, "memory", "miss", "--query", "where is the rounding rule?", role="backend-engineer")
out["memory miss"] = {"ok": v.get("ok"), "status": (v.get("result") or {}).get("status"),
                      "governed_changed": len(changed_governed(root, before))}
check("R4.writes-write",
      all(x["ok"] and x["governed_changed"] > 0 for x in out.values()),
      "unfrozen, the Write labels change governed state (propagation markers, the before_session_close checkpoint, a "
      "memory-quality failure record) — Write is their true class", out)

print(f"\nSUMMARY {sum(1 for _, ok in RESULTS if ok)}/{len(RESULTS)} PASS")
