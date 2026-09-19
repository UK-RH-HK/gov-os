#!/usr/bin/env python3
"""P2-AR-0027: pair every verdict line of a probe run on the base binary (integrated round-1 tree 843d79c) with the same
line of the run on this worktree's binary. Marked formats: beta-r `[PASS] id: ...`, zeta-r `OBS id: PASS -- ...`,
synthesis `X id PASS ...`, delta-r `CHECK id PASS|FAIL ...` (first token after the id).
Usage: compare_probes.py <before-dir> <after-dir> [<glob-suffix>]
"""
import re
import sys
from pathlib import Path

PATS = [
    re.compile(r"^\[(PASS|FAIL)\] (\S+?):"),
    re.compile(r"^OBS (\S+): (PASS|FAIL)"),
    re.compile(r"^X (\S+) (PASS|FAIL)"),
    re.compile(r"^(?:CHECK )?(\S+) (PASS|FAIL)\b"),
]


def verdicts(path):
    out = {}
    for line in Path(path).read_text(errors="replace").splitlines():
        for i, p in enumerate(PATS):
            m = p.match(line)
            if m:
                a, b = m.groups()
                key, v = (b, a) if i == 0 else (a, b)
                out.setdefault(key, v)
                break
    return out


def main():
    before, after = Path(sys.argv[1]), Path(sys.argv[2])
    suffix = sys.argv[3] if len(sys.argv) > 3 else ""
    tot = {"FAIL->PASS": 0, "PASS->FAIL": 0, "same": 0, "only-before": 0, "only-after": 0}
    for fb in sorted(before.glob(f"*{suffix}.out")):
        fa = after / fb.name
        if not fa.exists():
            print(f"{fb.name}: no after-run")
            continue
        vb, va = verdicts(fb), verdicts(fa)
        rows = []
        for k in sorted(set(vb) | set(va)):
            b, a = vb.get(k), va.get(k)
            if b and a and b == a:
                tot["same"] += 1
                continue
            if b and a:
                kind = f"{b}->{a}"
            elif b:
                kind = "only-before"
            else:
                kind = "only-after"
            tot[kind] = tot.get(kind, 0) + 1
            rows.append(f"    {kind:12s} {k}")
        pb = sum(v == "PASS" for v in vb.values())
        pa = sum(v == "PASS" for v in va.values())
        print(f"{fb.name}: before {pb}/{len(vb)} PASS, after {pa}/{len(va)} PASS")
        for r in rows:
            print(r)
    print("TOTAL", tot)


if __name__ == "__main__":
    main()
