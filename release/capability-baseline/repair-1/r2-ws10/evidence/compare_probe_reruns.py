#!/usr/bin/env python3
"""P2-AR-0031 — compare audit-of-record probe re-runs, BEFORE (base binary on the base tree) vs AFTER (this worktree).

Marked probes (zeta-r `OBS id: PASS`, beta-r `[PASS] id`, delta-r / epsilon-r `CHECK id PASS`, synthesis `X id PASS`)
are compared verdict by verdict; every probe, marked or not, also gets a normalised diff (volatile tokens replaced — the
normalisation rules are the integration builder's, repair-1/integration/evidence/audit-probes/normdiff.py, copied).

Usage: python3 compare_probe_reruns.py <before-dir> <after-dir> <diff-out-dir>      (prints the table)
"""
import difflib
import os
import re
import sys

RULES = [
    (re.compile(r"/(?:tmp|home|var)/[^\s\"',)\]}]*"), "<path>"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?\b"), "<ts>"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"), "<uuid>"),
    (re.compile(r"\b[0-9a-f]{12,64}\b"), "<hex>"),
    (re.compile(r"\b\d+(?:\.\d+)?\s?(?:ms|s)\b"), "<dur>"),
    (re.compile(r"\bS-[A-Za-z0-9]{6,}\b"), "<session>"),
    (re.compile(r"\bpid[=: ]\d+\b"), "pid=<n>"),
    # P2-AR-0031 additions: the delta-r harness's random session ids, and the harnesses' scratch-dir suffixes
    (re.compile(r"\bprobe-[0-9a-f]{8}\b"), "probe-<session>"),
    (re.compile(r"\bHR-\d{8}T\d{9}Z-[0-9a-f]{8}\b"), "HR-<id>"),
    (re.compile(r"\"process_id\": \d+"), "\"process_id\": <n>"),
]
DROP = re.compile(r"^(# P2-AR-|# tree |# worktree HEAD|# probe sha256|# date |# HEAD |# gov |# command:|\[exit=|exit=\d+$|binary:|### )")
MARKS = [
    re.compile(r"^OBS (\S+): (PASS|FAIL)"),
    re.compile(r"^\[(PASS|FAIL)\] (\S+?):?\s"),
    re.compile(r"^CHECK (\S+) (PASS|FAIL)"),
    re.compile(r"^X (\S+) (PASS|FAIL)"),
]


def verdicts(path):
    out = {}
    for line in open(path, errors="replace"):
        for rx in MARKS:
            m = rx.match(line)
            if m:
                a, b = m.groups()
                cid, v = (b, a) if a in ("PASS", "FAIL") else (a, b)
                out[cid] = v
    return out


def norm(path):
    out = []
    for line in open(path, errors="replace"):
        line = line.rstrip("\n")
        if DROP.match(line):
            continue
        for rx, rep in RULES:
            line = rx.sub(rep, line)
        out.append(line)
    return out


def main():
    before, after, dout = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(dout, exist_ok=True)
    names = sorted(f for f in os.listdir(before) if f.endswith(".out"))
    print(f"{'probe':62} {'marks':>6} {'P→F':>4} {'F→P':>4} {'norm-diff lines':>16}")
    for n in names:
        a, b = os.path.join(before, n), os.path.join(after, n)
        if not os.path.exists(b):
            print(f"{n:62} (no after run)")
            continue
        va, vb = verdicts(a), verdicts(b)
        pf = sorted(k for k in va if va[k] == "PASS" and vb.get(k) == "FAIL")
        fp = sorted(k for k in va if va[k] == "FAIL" and vb.get(k) == "PASS")
        gone = sorted(k for k in va if k not in vb)
        new = sorted(k for k in vb if k not in va)
        d = list(difflib.unified_diff(norm(a), norm(b), "before", "after", n=0, lineterm=""))
        with open(os.path.join(dout, n.replace(".out", ".diff")), "w") as f:
            f.write("\n".join(d) + ("\n" if d else ""))
        changed = sum(1 for x in d if x[:1] in "+-" and not x.startswith(("+++", "---")))
        print(f"{n:62} {len(va):>6} {len(pf):>4} {len(fp):>4} {changed:>16}")
        for k in pf:
            print(f"    PASS→FAIL {k}")
        for k in fp:
            print(f"    FAIL→PASS {k}")
        for k in gone:
            print(f"    verdict missing after: {k}")
        for k in new:
            print(f"    new verdict after: {k} {vb[k]}")


if __name__ == "__main__":
    main()
