#!/usr/bin/env python3
# DERIVED COPY (P2-AR-0032, round-2 integration builder) of WS-5's evidence adapter
#   release/capability-baseline/repair-1/r2-ws05/evidence/audit-probes/gov-adapter.py (P2-AR-0026; itself derived from
#   the round-1 integration adapter, adaptations (a)-(c), plus (d) receipt completion and (e) passed -> n/a).
# Changes, and nothing else:
#  (b') where the original provisioned a standalone human-channel anchor for the test owner key when the machine had
#      no channel, this copy provisions the throw-away root that delegates `human-gate` to the same key and re-verifies
#      the installed kernel (p2ar0032_root_channel.provision): P2-ADJ-0001 (WS-3 round 2, merged) turned the
#      standalone anchor off. Adaptations (a)-(e) are otherwise the originals'.
"""P2-AR-0026 evidence adapter — NOT product code. Derived from the round-1 integration adapter
(repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py, P2-AR-0022): adaptations (a)-(c) are that
file's, unchanged; (d) is new and is described at the end of this docstring.

P2-AR-0022's description follows. Runs the real integrated `gov` for an audit-of-record probe that
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

  (d) [P2-AR-0026] `task close <id> --report <file>` whose report lacks the Contract v3 W5 receipt fields that WS-4 /
      WS-5 now require at close (BC-P2-20) is completed with what a worker following the packet's `receipt_contract`
      returns: the packet is compiled for the task by the same caller (`context compile`), and ONLY ABSENT fields are
      added — `context_packet_hash`, `inputs_consumed` (the contract's inputs at their current hashes),
      `outputs_produced` (= the report's files_changed), the contract's trace ids (only when the report names no
      implemented/applied ids at all), `acceptance_evidence` for the declared tests (result mirrors the report's
      tests.status), and empty `deviations` / `unresolved`. Fields the probe supplied — including fabricated ones —
      are kept, and the adapted report is written to a new file; the probe's own report file is untouched. This
      adaptation masks the receipt requirement itself, so zeta-r W05/W08 (the receipt probes) are measured only in the
      unadapted mode.
  (e) [P2-AR-0026] in a report adapted under (d), a bare `tests.status: passed` becomes `not_applicable_with_reason`
      (reason recorded): since WS-2's close gate (BC-P2-43, wired at close in this round) a `passed` claim needs
      recorded, current product-test evidence, which the audit fixtures never record; lines about that rule (epsilon-r
      O1 §H) are measured in the unadapted mode. The per-test `acceptance_evidence` added by (d) then mirrors the
      adapted status.

Every other invocation is passed through byte-for-byte. Each adaptation is logged to $P2AR0026_SHIM_LOG.
Environment (probe harnesses strip GOV_*): P2AR0026_REAL_GOV (the gov binary), P2AR0026_HC_OWNER (hc_owner.py),
P2AR0026_SHIM_LOG (optional log file).
"""
import json
import os
import subprocess
import sys
import tempfile
import uuid

REAL = os.environ["P2AR0026_REAL_GOV"]
HC = os.environ["P2AR0026_HC_OWNER"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2ar0032_root_channel  # noqa: E402  (b')
LOG = os.environ.get("P2AR0026_SHIM_LOG")
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
            if not ((st.get("result") or {}).get("available")):  # (b')
                d = tempfile.mkdtemp(prefix="p2ar0032-admin-")
                how = p2ar0032_root_channel.provision(lambda *a: run_json([*rb, *a]), root, d)
                log(f"(b') human channel: throw-away root delegating human-gate provisioned from {d}: {how}")
            gg = {"gate_instance": shown.get("gate_instance"), "package_sha256": sha}
            d = tempfile.mkdtemp(prefix="p2ar0026-owner-")
            af = os.path.join(d, f"answer-{gate}-{uuid.uuid4().hex[:6]}.json")
            subprocess.run([sys.executable, HC, "answer", af, gate, str(gg.get("gate_instance")), str(gg.get("package_sha256")),
                            option], check=True, capture_output=True)
            rest = drop(cmd, "--by")
            log(f"(b) decide {gate} --option {option}: owner-signed answer relayed by orchestrator (probe role was {role})")
            js = ["--json"] if "--json" in g else []
            os.execv(REAL, [REAL, *js, *rb, *rest, "--answer-file", af])
    if len(cmd) >= 2 and cmd[0] == "task" and cmd[1] == "close" and "--report" in cmd:
        cmd = receipt_adapt(g, cmd)
    os.execv(REAL, [REAL, *g, *cmd])


RECEIPT_TRACE = ("requirements_implemented", "scenarios_implemented", "features_implemented", "decisions_applied",
                 "constraints_applied")


def receipt_adapt(g, cmd):
    """(d) complete a close report that lacks the W5 receipt fields (absent fields only; see the module docstring)."""
    task = cmd[2] if len(cmd) > 2 and not cmd[2].startswith("--") else None
    path = opt(cmd, "--report")
    try:
        rep = json.load(open(path))
    except Exception:
        return cmd
    if not isinstance(rep, dict) or not task:
        return cmd
    missing = [k for k in ("context_packet_hash", "inputs_consumed", "deviations") if k not in rep and not (k == "context_packet_hash" and "packet_hash" in rep)]
    if "unresolved" not in rep and "unknowns" not in rep:
        missing.append("unresolved")
    if not missing:
        return cmd
    base = [x for x in g if x != "--json"]
    pk = (run_json([*base, "context", "compile", task]).get("result") or {})
    rc = pk.get("receipt_contract") or {}
    if not pk.get("packet_hash"):
        log(f"(d) task close {task}: packet could not be compiled; report passed through unchanged")
        return cmd
    added = []
    def put(k, v):
        if k not in rep:
            rep[k] = v
            added.append(k)
    put("context_packet_hash", pk["packet_hash"])
    put("inputs_consumed", [f"{e.get('id')}@{e.get('content_hash')}" for e in rc.get("acknowledge_inputs", [])])
    put("outputs_produced", list(rep.get("files_changed") or []))
    if not any(k in rep for k in RECEIPT_TRACE):
        tr = rc.get("trace") or {}
        for k, src in (("requirements_implemented", "requirements"), ("scenarios_implemented", "scenarios"),
                       ("features_implemented", "features"), ("decisions_applied", "decisions"),
                       ("constraints_applied", "constraints")):
            put(k, list(tr.get(src) or []))
    tests = rep.get("tests") if isinstance(rep.get("tests"), dict) else None
    if tests is not None and tests.get("status") == "passed":
        tests["status"] = "not_applicable_with_reason"
        tests["reason"] = "adapter (e): the probe's 'passed' cannot be verified from recorded product-test evidence in this fixture"
        added.append("tests.status passed->not_applicable_with_reason")
    ts = ((rep.get("tests") or {}).get("status")) or "not_applicable_with_reason"
    ev = []
    for t in rc.get("tests_requiring_evidence", []):
        e = {"test": t, "result": "passed" if ts == "passed" else "not_applicable_with_reason", "evidence": "adapter: mirrors the report's tests.status"}
        if e["result"] != "passed":
            e["reason"] = "adapter: the probe's report states no per-test outcome"
        ev.append(e)
    put("acceptance_evidence", ev)
    put("deviations", [])
    if "unresolved" not in rep and "unknowns" not in rep:
        put("unresolved", [])
    d = tempfile.mkdtemp(prefix="p2ar0026-receipt-")
    newp = os.path.join(d, os.path.basename(path))
    json.dump(rep, open(newp, "w"))
    log(f"(d) task close {task}: receipt fields added {added} (report copied to {newp})")
    return drop(cmd, "--report") + ["--report", newp]


if __name__ == "__main__":
    main()
