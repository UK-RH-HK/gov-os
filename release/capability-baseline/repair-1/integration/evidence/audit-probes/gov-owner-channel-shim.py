#!/usr/bin/env python3
"""P2-AR-0022 evidence adapter — NOT product code. Runs the real integrated `gov` for an audit-of-record probe that
predates WS-3 (BC-P2-08/-10/-49), adapting ONLY the three paths WS-3 removed by design, so the probe's other lines can
be evaluated on the integrated tree:

  (a) an invocation that declares no role (no --role, no GOV_ROLE, no adopt-stage --reviewer-role/--verifier-role) gets
      `--role orchestrator` (as WS-3's gov-role-shim.sh does);
  (b) `decide <gate> --option X` given without --answer-file (the pre-WS-3 `--by <someone>` relay, often under
      `--role human`) for a gate the OS has ALREADY rendered (`gate show`: presentation.package_sha256; the adapter
      never presents a gate itself, and a decide on a never-rendered gate is passed through unchanged) becomes the human
      channel: the owner signs an answer bound to that instance and package with WS-3's test-material reference signer (repair-1/ws03/evidence/hc_owner.py,
      published seed 7), a standalone human-channel anchor for that key is provisioned from outside the repository if
      the machine has no channel yet, and the document is relayed by `--role orchestrator` (L3) — NOT the probe's role;
      a decide whose role cannot relay (L1/L2 workers, which WS-3 refuses anyway) is passed through unchanged, so
      refusal checks keep their meaning;
  (c) `gate create --fields <json>` whose package lacks decision-package fields gets generic, substantive values for
      the ABSENT fields only (BC-P2-49); fields the probe supplied are untouched; `gate create` without --fields gets
      the whole package.

Every other invocation is passed through byte-for-byte. Each adaptation is logged to $P2AR0022_SHIM_LOG.
Environment (probe harnesses strip GOV_*): P2AR0022_REAL_GOV (the gov binary), P2AR0022_HC_OWNER (hc_owner.py),
P2AR0022_SHIM_LOG (optional log file).
"""
import json
import os
import subprocess
import sys
import tempfile
import uuid

REAL = os.environ["P2AR0022_REAL_GOV"]
HC = os.environ["P2AR0022_HC_OWNER"]
LOG = os.environ.get("P2AR0022_SHIM_LOG")
PACKAGE = {"why_now": "the next step depends on this decision", "current_state": "options analysed, none chosen",
           "options": [{"id": "A", "description": "proceed as proposed"}, {"id": "B", "description": "do not proceed"}],
           "impact": "dependent work is re-planned", "reversibility": "reversible: the change can be rolled back",
           "cost_rework": "one task of rework if reversed", "recommendation": "A", "confidence": 0.6, "impact_radius": "R2"}
# roles whose pre-WS-3 `decide --by <someone else>` was a relayed HUMAN answer; any other role's decide (an L1/L2
# worker, whose refusal a probe may be testing) is passed through unchanged
RELAY_ROLES = {"orchestrator", "human", "product-owner", "owner", "migration-executor"}


def log(msg):
    if LOG:
        with open(LOG, "a") as f:
            f.write(msg + "\n")


def split(argv):
    """(global options before the subcommand, the subcommand words onwards)."""
    g, i = [], 0
    takes = {"--root", "--role", "--session"}
    while i < len(argv):
        a = argv[i]
        if a in takes and i + 1 < len(argv):
            g += [a, argv[i + 1]]
            i += 2
        elif a.startswith("--"):
            g.append(a)
            i += 1
        else:
            break
    return g, argv[i:]


def opt(lst, name):
    if name in lst:
        j = lst.index(name)
        return lst[j + 1] if j + 1 < len(lst) else None
    return None


def drop(lst, name, has_value=True):
    out, i = [], 0
    while i < len(lst):
        if lst[i] == name:
            i += 2 if has_value else 1
            continue
        out.append(lst[i])
        i += 1
    return out


def run_json(args):
    p = subprocess.run([REAL, "--json", *args], capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"ok": False}


def main():
    argv = sys.argv[1:]
    g, cmd = split(argv)
    # adopt stages may declare the acting role with their own stage flag (WS-3 `declared_role`): that is a declaration
    declared = "--role" in g or bool(os.environ.get("GOV_ROLE")) or any(f in cmd for f in ("--reviewer-role", "--verifier-role"))
    if not declared:
        g = g + ["--role", "orchestrator"]
        log(f"(a) role declared: orchestrator for {' '.join(cmd[:3])}")
    role = opt(g, "--role") or os.environ.get("GOV_ROLE")
    root = opt(g, "--root") or os.getcwd()
    base = [x for x in g if x != "--json"]
    if len(cmd) >= 2 and cmd[0] == "gate" and cmd[1] == "create":
        f = opt(cmd, "--fields")
        try:
            cur = json.loads(f) if f else {}
        except Exception:
            cur = None
        if isinstance(cur, dict):
            added = [k for k in PACKAGE if k not in cur]
            if added:
                new = dict(PACKAGE)
                new.update(cur)
                cmd = drop(cmd, "--fields") + ["--fields", json.dumps(new)]
                log(f"(c) gate create: package fields added {added}")
    by = opt(cmd, "--by") if cmd else None
    human_relay = by is None or by != role or role == "human"  # `--by <acting role>` is an agent resolution: untouched
    if cmd and cmd[0] == "decide" and "--answer-file" not in cmd and len(cmd) >= 2 and role in RELAY_ROLES and human_relay:
        gate, option = cmd[1], opt(cmd, "--option")
        rb = drop(base, "--role") + ["--role", "orchestrator"]
        # the adapter never presents a gate itself: it signs only for a package the OS has already rendered (read with
        # `gate show`), so a probe's "decide on a never-presented gate is refused" check keeps its meaning
        shown = (run_json([*rb, "gate", "show", gate]).get("result") or {}).get("gate") or {}
        sha = (shown.get("presentation") or {}).get("package_sha256")
        if option and sha and shown.get("gate_instance"):
            st = run_json([*rb, "trust", "human-channel"])
            if not ((st.get("result") or {}).get("available")):
                d = tempfile.mkdtemp(prefix="p2ar0022-admin-")
                af = os.path.join(d, "anchor.json")
                subprocess.run([sys.executable, HC, "anchor", af, "7"], check=True, capture_output=True)
                pr = run_json([*rb, "trust", "human-channel", "--provision", af])
                log(f"(b) human channel provisioned from {af}: {pr.get('ok')}")
            gg = {"gate_instance": shown.get("gate_instance"), "package_sha256": sha}
            d = tempfile.mkdtemp(prefix="p2ar0022-owner-")
            af = os.path.join(d, f"answer-{gate}-{uuid.uuid4().hex[:6]}.json")
            subprocess.run([sys.executable, HC, "answer", af, gate, str(gg.get("gate_instance")), str(gg.get("package_sha256")),
                            option], check=True, capture_output=True)
            rest = drop(cmd, "--by")
            log(f"(b) decide {gate} --option {option}: owner-signed answer relayed by orchestrator (probe role was {role})")
            js = ["--json"] if "--json" in g else []
            os.execv(REAL, [REAL, *js, *rb, *rest, "--answer-file", af])
    os.execv(REAL, [REAL, *g, *cmd])


if __name__ == "__main__":
    main()
