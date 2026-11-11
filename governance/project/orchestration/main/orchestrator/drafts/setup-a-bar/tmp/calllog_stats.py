#!/usr/bin/env python3
"""Counts from the guard's call log (hashes only, no content). Reads the day files, never salt.key."""
import collections
import glob
import json
import os
import re
import sys

UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
base = os.path.expanduser("~/.gov-os/guard-calls")
days = sorted(glob.glob(os.path.join(base, "????-??-??.jsonl")))
tot = collections.Counter()
for path in days:
    day = os.path.basename(path)[:10]
    rows = []
    bad = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                rows.append(json.loads(line))
            except Exception:
                bad += 1
    live = [r for r in rows if UUID.match(r.get("session", "")) and r.get("tree") in ("main", "worktree")]
    other = len(rows) - len(live)
    print("== %s: lines %d (bad %d), live %d, other (replays, rehearsals, runs) %d" % (day, len(rows), bad, len(live), other))
    dec = collections.Counter(r["decision"] for r in live)
    print("   decisions:", dict(dec))
    ref = [r for r in live if r["decision"] != "allow"]
    print("   non-allow by rule:", dict(collections.Counter("%s/%s" % (r["rule"], r["decision"]) for r in ref)))
    print("   by tool:", dict(collections.Counter(r["tool"] for r in live)))
    print("   by role:", dict(collections.Counter(r["role"] for r in live)))
    print("   non-allow by role/tool:", dict(collections.Counter("%s/%s" % (r["role"], r["tool"]) for r in ref)))
    print("   rules among allow:", dict(collections.Counter(r["rule"] for r in live if r["decision"] == "allow")))
    print("   sessions:", len(set(r["session"] for r in live)), "distinct actions:", len(set(r["sha256"] for r in live)))
    print("   trees:", dict(collections.Counter(r["tree"] for r in rows)))
    ms = sorted(r.get("ms", 0) for r in live)
    if ms:
        print("   ms median %s p99 %s max %s" % (ms[len(ms) // 2], ms[int(len(ms) * .99)], ms[-1]))
    tot.update(["live"] * len(live))
    tot.update(["refusals"] * len(ref))
    tot.update(["error"] * sum(1 for r in ref if r["rule"] == "error"))
    # error rows by tool and role
    err = [r for r in ref if r["rule"] == "error"]
    print("   error by tool/role/ticket:", dict(collections.Counter("%s/%s/%s" % (r["tool"], r["role"], r["ticket"]) for r in err)))
print(dict(tot))
