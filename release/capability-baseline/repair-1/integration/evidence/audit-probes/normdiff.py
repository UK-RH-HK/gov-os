#!/usr/bin/env python3
"""P2-AR-0022 — normalised diff of an UNMARKED audit-of-record probe output (gamma-r, alpha-r, epsilon-r print
observations, not PASS/FAIL verdicts): a builder's recorded after-run against the integrated re-run. Volatile tokens are
normalised (absolute paths, timestamps, hashes, UUIDs, durations, session ids, pids, run headers) so that what remains is
behaviour. The integration report reviews every remaining difference.

Usage: python3 normdiff.py <recorded.out> <integrated.out> [<out.diff>]
"""
import difflib
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
    (re.compile(r"\"process_id\": \d+"), "\"process_id\": <n>"),
]
DROP = re.compile(r"^(# P2-AR-|# worktree HEAD|# probe sha256|# date |# HEAD |# gov |# command:|\[exit=|exit=\d+$|binary:|### )")


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
    a, b = norm(sys.argv[1]), norm(sys.argv[2])
    d = list(difflib.unified_diff(a, b, "recorded (builder branch)", "integrated", n=0, lineterm=""))
    changed = sum(1 for x in d if (x.startswith("+") or x.startswith("-")) and not x.startswith(("+++", "---")))
    text = "\n".join(d)
    if len(sys.argv) > 3:
        open(sys.argv[3], "w").write(f"# normalised diff: {sys.argv[1]}\n#   vs {sys.argv[2]}\n# changed lines: {changed}\n{text}\n")
    print(f"{changed:5d} changed lines  {sys.argv[2].split('/')[-1]}")


if __name__ == "__main__":
    main()
