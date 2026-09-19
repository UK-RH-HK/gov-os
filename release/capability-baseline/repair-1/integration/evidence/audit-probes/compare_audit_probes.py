#!/usr/bin/env python3
"""P2-AR-0022 — verdict-line comparison of audit-of-record probes: each builder's recorded AFTER run (on its own
branch) against the integrated re-runs (./ws04-zeta = WS-4's runner, unedited; ./integrated = run-audit-probe.sh
unedited; ./shim = through gov-owner-channel-shim.py). Only probes that print verdict markers are compared here
(zeta-r `OBS id: PASS`, beta-r `[PASS] id`, delta-r / epsilon-r `CHECK id PASS`, synthesis `X id PASS`); unmarked
probes are reviewed by normalised diff (see the integration report).

Usage: python3 compare_audit_probes.py [builder ...]    (reads only; prints the table)
"""
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # release/capability-baseline/repair-1


def rec(ws, *parts):
    return os.path.join(R, ws, "evidence", *parts)


ZETA = ["W00-harness-smoke", "W01-artefact-identity", "W01b-migration-plan-identity", "W02-typed-contracts", "W03-task-input-manifest",
        "W04-context-delivery", "W04b-input-class-delivery", "W05-consumption-receipt", "W06-staleness-propagation",
        "W07-orphan-detection", "W08-lineage", "W09-session-handoff-continuity", "W10-hard-invariant-attacks",
        "W11-quantitative-health", "W12-scheduler-integration", "FR-freshness-invalidation"]
BETA_AFTER = ["C3-semantic-memory", "C4-lexical-memory", "C5-code-structural-memory", "C7-episodic-memory", "C8-failure-memory",
              "C9-context-packet", "D1-incremental-freshness", "D2-retrieval-router", "D3-hierarchical-retrieval", "X-K2-D1-W6-interactions"]
BETA_OTHER = ["C1-deterministic-structured-memory", "C10-capability-memory", "C2-relationship-graph", "C6-temporal-memory",
              "D4-component-separation", "D5-model-selection", "D6-rebuild-guarantee", "DERIVED-views-reconciliation",
              "FRESH-evidence-invalidation", "R1-R2-legacy-and-chat-retirement", "R3-archive-policy", "SCALE-retrieval-latency"]

MANIFEST = {  # builder -> [(label, recorded file, {mode: integrated file})]
    "WS-4 (P2-AR-0017) zeta-r": [(p, rec("ws04", "after", f"{p}.out"),
                                   {"integrated": os.path.join(HERE, "ws04-zeta", f"{p}.out"), "shim": os.path.join(HERE, "shim", f"zeta-r.{p}.out")})
                                  for p in ZETA],
    "WS-6 (P2-AR-0019) beta-r": [(p, rec("ws06", "after" if p in BETA_AFTER else "after-other", f"{p}.out"),
                                   {"integrated": os.path.join(HERE, "integrated", f"beta-r.{p}.out"), "shim": os.path.join(HERE, "shim", f"beta-r.{p}.out")})
                                  for p in BETA_AFTER + BETA_OTHER],
    "WS-9/11 (P2-AR-0021)": [(p, rec("ws09-11", "after", f"{o}.out"),
                               {"integrated": os.path.join(HERE, "integrated", f"{f}.{p}.out"), "shim": os.path.join(HERE, "shim", f"{f}.{p}.out")})
                              for f, p, o in [("synthesis", "LEAD-X5-adoption-rerun-archives-os-adapter", "LEAD-X5-adoption-rerun-archives-os-adapter"),
                                              ("beta-r", "R1-R2-legacy-and-chat-retirement", "R1-R2-legacy-and-chat-retirement"),
                                              ("zeta-r", "W01b-migration-plan-identity", "W01b-migration-plan-identity"),
                                              ("zeta-r", "W01-artefact-identity", "W01-artefact-identity")]],
    "WS-3 (P2-AR-0016) delta-r / synthesis": [(p, rec("ws03", "probes", "final-roleshim", f"{f}.{p}.out") if os.path.exists(rec("ws03", "probes", "final-roleshim", f"{f}.{p}.out")) else rec("ws03", "probes", "final-unedited", f"{f}.{p}.out"),
                                               {"integrated": os.path.join(HERE, "integrated", f"{f}.{p}.out"), "shim": os.path.join(HERE, "shim", f"{f}.{p}.out")})
                                              for f, p in [("delta-r", "L1-contradiction-resolution"), ("delta-r", "L2-decision-package"),
                                                           ("delta-r", "L3-gate-presentation-attacks"), ("delta-r", "L3-supplement"),
                                                           ("delta-r", "M1-M3-routing"), ("synthesis", "AC16-X2-authority-gate-chain")]],
    "WS-5 (P2-AR-0018) delta-r": [(p, rec("ws05", "probe-reruns", "delta-r", f"{p}.repaired.out"),
                                    {"integrated": os.path.join(HERE, "integrated", f"delta-r.{p}.out"), "shim": os.path.join(HERE, "shim", f"delta-r.{p}.out")})
                                   for p in ["J1-J2-research-experiments", "L3-gate-presentation-attacks"]],
    "WS-2 (P2-AR-0015)": [(p, rec("ws02", "after", o),
                            {"integrated": os.path.join(HERE, "integrated", f"{f}.{p}.out"), "shim": os.path.join(HERE, "shim", f"{f}.{p}.out")})
                           for f, p, o in [("delta-r", "FRESH-invalidation", "delta-r-FRESH-invalidation.out"),
                                           ("beta-r", "FRESH-evidence-invalidation", "beta-r-FRESH-evidence-invalidation.out"),
                                           ("zeta-r", "FR-freshness-invalidation", "zeta-r-FR-freshness-invalidation.out"),
                                           ("synthesis", "AC16-X1-upstream-change-chain", "AC16-X1-upstream-change-chain.out")]],
    "WS-8 (P2-AR-0020) synthesis": [("AC16-X3-ingress-root-of-trust-chain", rec("ws08", "probes-after-63f82ba", "AC16-X3.out"),
                                      {"integrated": os.path.join(HERE, "integrated", "synthesis.AC16-X3-ingress-root-of-trust-chain.out"),
                                       "shim": os.path.join(HERE, "shim", "synthesis.AC16-X3-ingress-root-of-trust-chain.out")})],
    "WS-1/12 (P2-AR-0014)": [(p, rec("ws01-12", "probes-after", o),
                               {"integrated": os.path.join(HERE, "integrated", f"{f}.{p}.out"), "shim": os.path.join(HERE, "shim", f"{f}.{p}.out")})
                              for f, p, o in [("beta-r", "DERIVED-views-reconciliation", "beta-r.DERIVED-views-reconciliation.out"),
                                              ("delta-r", "DERIVED-VIEWS-JKLMN", "delta-r.DERIVED-VIEWS-JKLMN.out"),
                                              ("zeta-r", "DV-derived-view-reconciliation", "zeta-r.DV-derived-view-reconciliation.out")]],
}

PATTERNS = [re.compile(r"^CHECK (\S+) (PASS|FAIL)\b"), re.compile(r"^X (\S+) (PASS|FAIL)\b"), re.compile(r"^OBS (\S+?): (PASS|FAIL)\b"),
            re.compile(r"^W (\S+) (PASS|FAIL)\b"), re.compile(r"^(PASS|FAIL)\s{2}(\S+)\s")]
BRACKET = re.compile(r"^\[(PASS|FAIL)\] (.*)$")


def verdicts(path):
    out = OrderedDict()
    if not os.path.exists(path):
        return None
    for line in open(path, errors="replace"):
        line = line.rstrip("\n")
        m = BRACKET.match(line)
        if m:
            v, rest = m.group(1), m.group(2)
            k = rest.split(" — ")[0] if " — " in rest else (rest.split(":")[0] if re.match(r"^[A-Za-z0-9][\w.()\[\]-]*:", rest) else rest[:90])
            out.setdefault(k, []).append(v)
            continue
        for pat in PATTERNS:
            m = pat.match(line)
            if m:
                a, b = m.group(1), m.group(2)
                k, v = (b, a) if a in ("PASS", "FAIL") else (a, b)
                out.setdefault(k, []).append(v)
                break
    return OrderedDict((k, "PASS" if all(x == "PASS" for x in vs) else "FAIL") for k, vs in out.items())


only = sys.argv[1:]
grand = {"PASS->FAIL": 0, "FAIL->PASS": 0}
for builder, rows in MANIFEST.items():
    if only and not any(o in builder for o in only):
        continue
    print(f"\n# {builder}")
    for label, recorded, runs in rows:
        rv = verdicts(recorded)
        if rv is None:
            print(f"  {label}: no recorded after-run at {os.path.relpath(recorded, R)}")
            continue
        line = f"  {label}: recorded {sum(v == 'PASS' for v in rv.values())}P/{sum(v == 'FAIL' for v in rv.values())}F"
        details = []
        for mode, f in runs.items():
            got = verdicts(f)
            if got is None:
                line += f" | {mode}: not run"
                continue
            reg = [k for k, v in rv.items() if v == "PASS" and got.get(k) == "FAIL"]
            imp = [k for k, v in rv.items() if v == "FAIL" and got.get(k) == "PASS"]
            miss = [k for k in rv if k not in got]
            line += f" | {mode}: {sum(v == 'PASS' for v in got.values())}P/{sum(v == 'FAIL' for v in got.values())}F, PASS->FAIL {len(reg)}, FAIL->PASS {len(imp)}, not reached {len(miss)}"
            if mode == "shim":
                grand["PASS->FAIL"] += len(reg)
                grand["FAIL->PASS"] += len(imp)
            for k in reg:
                details.append(f"      [{mode}] PASS->FAIL {k}")
            for k in imp:
                details.append(f"      [{mode}] FAIL->PASS {k}")
            for k in miss[:25]:
                details.append(f"      [{mode}] not reached {k}")
        print(line)
        for d in details:
            print(d)
print(f"\nTOTAL over the shim runs: {grand}")
