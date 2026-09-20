#!/usr/bin/env python3
"""LABELLED DERIVED COPY (P2-AR-0043, round 4, INT3-O1) of WS-7's probe
release/capability-baseline/repair-1/r3-ws07/evidence/ip_task_close_registration.py (P2-AR-0038).

Changes against the original, and nothing else:
  a. `register_approved` answers every gate the registration raises: the execution approval (`human_gate`, subject
     `plugin-registration`) AND the gate of the change transaction the OS proposed for the registration
     (`change_transaction.human_gate`), both through the same owner-signed channel helper (`nc.human`), then
     registers again. The original answers only the first. (INT3-O1: a registration is a material governance and
     security change carried out by its own change transaction, Contract v3 K3; its execution approval, F4, does not
     stand in for the change approval.)
  b. prints the change transaction (id, status, gate, effective triggers) and whether its recorded CIT-E writes cover
     the descriptor's current bytes, plus per-step wall-clock timings.
The scenario (task class, allowed paths, descriptor, receipt, close) is the original's, unchanged.

Usage: GOV_BIN=<gov> WS07R3_SCRATCH=<dir> python3 ip_task_close_registration.INT3-O1.P2-AR-0043.py
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
WS07 = os.path.join(WT, "release", "capability-baseline", "repair-1", "r3-ws07", "evidence")
sys.path.insert(0, WS07)
import ws07_r3_named_checks as nc  # noqa: E402  (read-only import of WS-7's helpers, unchanged)
import ip_task_close_registration as orig  # noqa: E402  (the original's receipt helper, unchanged)

T0 = time.time()


def t(label):
    print(f"# t+{time.time() - T0:7.1f}s {label}", flush=True)


def register_approved_both(p, role, rel):
    """(change a) answer every gate the registration raises, then register again."""
    df = os.path.join(p.root, rel)
    r = p.run(role, "plugins", "register", "--descriptor", df)
    t("first plugins register")
    answered = []
    for _ in range(3):
        res = r.get("result") or {}
        if res.get("registered"):
            return r, res
        gates = [g for g in (res.get("human_gate"), (res.get("change_transaction") or {}).get("human_gate"))
                 if g and g not in answered]
        if not gates:
            return r, res
        for g in gates:
            nc.human(p, g, "A")
            answered.append(g)
            t(f"owner answered {g}")
        print("first request:", json.dumps({"human_gate": res.get("human_gate"), "change_transaction": res.get("change_transaction")})[:900])
        r = p.run(role, "plugins", "register", "--descriptor", df)
        t("plugins register again")
    return r, (r.get("result") or {})


def main():
    print(f"# gov {nc.GOV}")
    p = nc.new_project("ip-close-int3o1")
    t("project provisioned and initialised")
    p.ok("orchestrator", "rebuild-memory")
    te, s = "tooling-engineer", "S-tool"
    task = p.ok("orchestrator", "task", "create", "--class", "tooling", "--objective", "register the p1 plugin", "--status",
                "READY", "--allowed", "tools/**,governance/project/plugins/**")["id"]
    p.ok(te, "task", "claim", task, session=s)
    t("task claimed")
    marker = os.path.join(p.base, "marker.txt")
    nc.marker_plugin(p, "tools/p.sh", marker)
    rel = nc.descriptor(p, "p1", "tools/p.sh")
    r, res = register_approved_both(p, te, rel)
    print("registered:", res.get("registered"), res.get("registry"))
    ct = res.get("change_transaction") or {}
    print("change transaction:", json.dumps({k: ct.get(k) for k in ("cit", "cit_status", "human_gate", "radius", "effective_triggers")}))
    if ct.get("cit"):
        c = nc.yaml.safe_load(open(os.path.join(p.root, "spec", "decisions", f"{ct['cit']}.yaml")))
        now = hashlib.sha256(open(os.path.join(p.root, rel), "rb").read()).hexdigest()
        writes = (c.get("execution") or {}).get("writes") or []
        cover = [w for w in writes if w.get("path") == rel]
        print("CIT-E writes cover the descriptor's current bytes:", bool(cover) and cover[0].get("sha256") == now,
              "| origin:", c.get("origin"), "| system.kind:", (c.get("system") or {}).get("kind"),
              "| approval gate:", (c.get("approval") or {}).get("gate"), "| execution gate (registry):",
              ((res.get("registry_entry") or {}).get("registration_gate")))
    changed = p.git("status", "--porcelain").stdout
    print("# working-tree changes during the task:\n" + changed)
    p.ok(te, "rebuild-memory", "--incremental", session=s)
    f = orig.receipt(p, te, s, task, ["tools/p.sh", rel])
    v = p.run(te, "task", "close", task, "--report", f, session=s)
    t("task close")
    err = v.get("error") or {}
    print("close ok:", v.get("ok"), "code:", err.get("code"))
    if v.get("ok"):
        print("task status:", (v.get("result") or {}).get("task_status"))
    d = err.get("details") or {}
    print("undeclared:", json.dumps(d.get("undeclared")), "out_of_scope:", json.dumps(d.get("out_of_scope")),
          "t2_violations:", json.dumps(d.get("t2_violations"))[:300])
    if not v.get("ok"):
        print("message:", (err.get("message") or "")[:500])


if __name__ == "__main__":
    main()
