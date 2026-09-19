#!/usr/bin/env python3
"""P2-AR-0032 — pair every verdict line of each round-2 builder's own probe as recorded on the builder's branch with
the same line run against the integrated binary: unedited (unedited/) and, where one was needed, through a labelled
derived copy (derived-runs/). A line that PASSed on the builder's branch and FAILs (or is not reached) integrated is
listed; its explanation is in the integration report §7. Usage: python3 compare_builder_probes.py"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PAIRS = [  # (probe, builder's recorded after-run, unedited integrated, derived integrated or None)
    ("WS-2 WS02-r2-supplementary", "r2-ws02/evidence/WS02-r2-supplementary.out", "ws02-r2-supplementary.out",
     "derived_WS02-r2-supplementary.fixtures.P2-AR-0032.py.out"),
    ("WS-3 R2-WS03-probes", "r2-ws03/evidence/probes/R2-WS03-probes.final.out", "ws03-r2-probes.out", None),
    ("WS-3 ws03_named_checks.r2-derived", "r2-ws03/evidence/probes/ws03-named-checks.r2-derived.final.out",
     "ws03-r2-named-checks.out", None),
    ("WS-4 ws04r2-scenarios (through the evidence adapter)", "r2-ws04/evidence/after/derived.ws04r2-scenarios.out",
     "ws04-r2-scenarios.out", "derived_ws04r2-scenarios.held-task.P2-AR-0032.py.out"),
    ("WS-5 ws05_r2_supplementary", "r2-ws05/evidence/supplementary/ws05-r2-supplementary.after-090eded.out",
     "ws05-r2-supplementary.out", "derived_ws05_r2_supplementary.root-channel.P2-AR-0032.py.out"),
    ("WS-6 SUPP-ws06-r2", "r2-ws06/evidence/SUPP-ws06-r2.out", "ws06-r2-supplementary.out",
     "derived_SUPP-ws06-r2.root-channel.P2-AR-0032.py.out"),
    ("WS-6 SUPP-ws06-behaviours (round 1, re-run by WS-6 in round 2)", "r2-ws06/evidence/after/round1-SUPP-ws06-behaviours.out",
     "ws06-r1-supplementary.out", "derived_SUPP-ws06-behaviours.root-channel-registered.P2-AR-0032.py.out"),
    ("WS-7 ws07_named_checks", "r2-ws07/evidence/probes/ws07-named-checks.final-371794a.out", "ws07-r2-named-checks.out",
     "derived_ws07_named_checks.root-channel.P2-AR-0032.py.out"),
    ("WS-8 WS08-P1 (round-1 probe, derived owner-channel copy)", "r2-ws08/evidence/ws08-round1-probes-after-cf13dee/WS08-P1.out",
     "ws08-r1-P1.out", None),
    ("WS-8 WS08-P2", "r2-ws08/evidence/ws08-round1-probes-after-cf13dee/WS08-P2.out", "ws08-r1-P2.out", None),
    ("WS-8 WS08-P3", "r2-ws08/evidence/ws08-round1-probes-after-cf13dee/WS08-P3.out", "ws08-r1-P3.out", None),
    ("WS-8 WS08-P4 (round-1 probe, derived owner-channel copy)", "r2-ws08/evidence/ws08-round1-probes-after-cf13dee/WS08-P4.out",
     "ws08-r1-P4.out", None),
    ("WS-8 cold_cache_scheduler", "r2-ws08/evidence/concurrency/cold_cache_scheduler.after-cf13dee.out", "ws08-cold-cache.out", None),
    ("WS-9/11 R2-ws0911-named-checks", "r2-ws09-11/evidence/probes/R2-named-checks.candidate.out", "ws09-11-r2-named-checks.out",
     "derived_R2-ws0911-named-checks.root-channel.P2-AR-0032.py.out"),
    ("WS-10 ws10_supplementary", "r2-ws10/evidence/probes/ws10-supplementary.after.out", "ws10-r2-supplementary.out",
     "derived_ws10_supplementary.root-channel.P2-AR-0032.py.out"),
]
LINE = [re.compile(r"^(?:CHECK|X|C|W)\s+(\S+)\s+(PASS|FAIL)\b"), re.compile(r"^\[(PASS|FAIL)\]\s+([^:]+):"),
        re.compile(r"^(PASS|FAIL)\s{2}(\S+)\s{2}")]


def verdicts(path):
    out = {}
    if not path or not os.path.exists(path):
        return None
    for line in open(path, errors="replace"):
        line = line.rstrip("\n")
        for i, rx in enumerate(LINE):
            m = rx.match(line)
            if m:
                cid, v = (m.group(1), m.group(2)) if i == 0 else (m.group(2), m.group(1))
                out.setdefault(cid.strip(), v)
                break
    return out


def tally(v):
    return "n/a" if v is None else f"{sum(1 for x in v.values() if x == 'PASS')}/{len(v)}"


for name, rec, une, der in PAIRS:
    a = verdicts(os.path.join(R, rec))
    b = verdicts(os.path.join(HERE, "unedited", une))
    c = verdicts(os.path.join(HERE, "derived-runs", der)) if der else None
    print(f"\n## {name}\n   builder recorded: {tally(a)}   integrated unedited: {tally(b)}   integrated derived: {tally(c)}")
    for cid, v in (a or {}).items():
        ub = (b or {}).get(cid, "not reached")
        dc = (c or {}).get(cid, "not reached") if c is not None else "-"
        if v == "PASS" and ub != "PASS":
            print(f"   PASS->{ub:12s} unedited | derived: {dc:12s} {cid}")
        elif v != ub:
            print(f"   {v}->{ub:12s} unedited | derived: {dc:12s} {cid}")
    if c is not None:
        regress = [cid for cid, v in (a or {}).items() if v == "PASS" and c.get(cid) != "PASS"]
        print(f"   lines PASS on the builder's branch and not PASS through the derived copy: {regress or 'none'}")
