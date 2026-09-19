#!/usr/bin/env python3
"""P2-AR-0022 — P2-HO-0019 step 6 comparison: every verdict line of each round-1 builder's OWN probe, as recorded on
that builder's branch (its repair-1/<ws>/evidence/ output), against the same probe re-run on the integrated binary
(./<probe>.integrated.out), plus the role-shim (./<probe>.roleshim.out) and derived owner-channel runs where they exist.
A line that PASSED on the builder's branch and FAILS integrated is an integration regression candidate; each one is
listed with the run that resolves it (or not).

Usage: python3 compare_builder_probes.py   (reads only; prints the table)
"""
import os
import re
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # release/capability-baseline/repair-1

PROBES = [  # probe id, recorded output(s) on the builder's branch, integrated runs to compare (label -> files)
    ("ws01-bc01-mutation-controls", ["ws01-12/evidence/bc-p2-01/mutation-controls.out"], {"integrated": ["ws01-bc01-mutation-controls.integrated.out"]}),
    ("ws01-bc51-oracle-format-checks", ["ws01-12/evidence/bc-p2-51/oracle-format-checks.out"], {"integrated": ["ws01-bc51-oracle-format-checks.integrated.out"]}),
    ("ws02-supplementary", ["ws02/evidence/supplementary/WS02-supplementary.out"], {"integrated": ["ws02-supplementary.integrated.out"]}),
    ("ws03-named-checks", ["ws03/evidence/probes/ws03-named-checks.candidate-final.out"], {"integrated": ["ws03-named-checks.integrated.out"]}),
    ("ws04-scenarios", ["ws04/evidence/after/ws04-scenarios.out"], {"integrated": ["ws04-scenarios.integrated.out"]}),
    ("ws05-supplementary", ["ws05/evidence/supplementary/ws05-supplementary.repaired.out"], {"integrated": ["ws05-supplementary.integrated.out"]}),
    ("ws06-supplementary", ["ws06/evidence/SUPP-ws06-behaviours.out"], {"integrated": ["ws06-supplementary.integrated.out"]}),
    ("ws08-P1..P4", ["ws08/evidence/ws08-probes-after-63f82ba.out"],
     {"integrated": [f"ws08-P{i}.integrated.out" for i in range(1, 5)],
      "roleshim": [f"ws08-P{i}.roleshim.out" for i in range(1, 5)],
      "roleshim + derived owner channel (P1, P4)": ["ws08-P1.derived-owner-channel.roleshim.out", "ws08-P2.roleshim.out",
                                                   "ws08-P3.roleshim.out", "ws08-P4.derived-owner-channel.roleshim.out"]}),
    ("ws09-11-regression-probes", ["ws09-11/evidence/after/B-ws0911-regression-probes.out"],
     {"integrated": ["ws09-11-regression-probes.integrated.out"],
      "derived owner channel": ["ws09-11-regression-probes.derived-owner-channel.out"]}),
]

PATTERNS = [
    re.compile(r"^CHECK (\S+) (PASS|FAIL)\b"),
    re.compile(r"^W (\S+) (PASS|FAIL)\b"),
    re.compile(r"^X (\S+) (PASS|FAIL)\b"),
    re.compile(r"^OBS (\S+?): (PASS|FAIL)\b"),
    re.compile(r"^(S\d[\w.-]*): (PASS|FAIL)\s*$"),
    re.compile(r"^(PASS|FAIL)\s{2}(\S+)\s"),
]
BRACKET = re.compile(r"^\[(PASS|FAIL)\] (.*)$")


def verdicts(paths):
    out = OrderedDict()
    for p in paths:
        full = p if os.path.isabs(p) else (os.path.join(R, p) if "/evidence/" in p else os.path.join(HERE, p))
        if not os.path.exists(full):
            continue
        for line in open(full, errors="replace"):
            line = line.rstrip("\n")
            m = BRACKET.match(line)
            if m:
                v, rest = m.group(1), m.group(2)
                if " — " in rest:
                    k = rest.split(" — ")[0]
                elif ": exit=" in rest:
                    k = rest.split(": exit=")[0]
                elif re.match(r"^[A-Za-z0-9][\w.-]*:", rest):
                    k = rest.split(":")[0]
                else:
                    k = rest[:90]
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


total_regressions = 0
for pid, recorded, runs in PROBES:
    rec = verdicts(recorded)
    print(f"\n## {pid}")
    print(f"recorded on the builder's branch: {sum(v == 'PASS' for v in rec.values())} PASS / {sum(v == 'FAIL' for v in rec.values())} FAIL ({len(rec)} lines)")
    first = None
    for label, files in runs.items():
        got = verdicts(files)
        missing = [k for k in rec if k not in got]
        reg = [k for k, v in rec.items() if v == "PASS" and got.get(k) == "FAIL"]
        imp = [k for k, v in rec.items() if v == "FAIL" and got.get(k) == "PASS"]
        print(f"{label}: {sum(v == 'PASS' for v in got.values())} PASS / {sum(v == 'FAIL' for v in got.values())} FAIL ({len(got)} lines); "
              f"PASS->FAIL {len(reg)}; FAIL->PASS {len(imp)}; recorded lines not reached {len(missing)}")
        for k in reg:
            print(f"    PASS->FAIL  {k}")
        for k in missing[:40]:
            print(f"    NOT REACHED {k}")
        if first is None:
            first = (reg, missing)
    last = verdicts(list(runs.values())[-1])
    unresolved = [k for k, v in rec.items() if v == "PASS" and last.get(k) != "PASS"]
    print(f"=> lines that passed on the builder's branch and do not pass in the last run listed: {len(unresolved)} {unresolved}")
    total_regressions += len(unresolved)
print(f"\nTOTAL unresolved PASS->not-PASS lines over all probes (last run listed per probe): {total_regressions}")
