#!/usr/bin/env python3
"""P2-AR-0028 — pair the named audit-probe lines (gamma-r F4-plugins / F2F3-tools / FRESH-invalidation, synthesis
LEAD-X4) and the WS-7 named checks between the base run (843d79c) and the final run, per mode, and print a verdict per
line. The verdict is the repair delta's reading of the line (the attack must fail closed); it is a builder's summary of
regression evidence, not an acceptance judgement. Usage: python3 compare_probes.py <base-label> <final-label>"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE, FINAL = sys.argv[1], sys.argv[2]


def read(label, mode, name):
    p = os.path.join(HERE, "probes", f"{label}-{mode}", name)
    return open(p).read() if os.path.exists(p) else ""


def after(text, header, marker, n=1):
    """The n-th line after `marker` inside the section headed `header`."""
    sec = text.split(f"==== {header}", 1)
    if len(sec) < 2:
        return "(section not reached)"
    body = sec[1].split("\n==== ", 1)[0]
    lines = body.splitlines()
    for i, l in enumerate(lines):
        if marker in l:
            j = i + n
            return lines[j].strip()[:170] if j < len(lines) else "(no line)"
    return "(line not reached)"


# (id, file, section header, marker, offset, predicate(line) -> True when the attack failed closed / requirement met)
F4 = "gamma-r.F4-plugins.out"
F23 = "gamma-r.F2F3-tools.out"
LINES = [
    ("F4.b1 UNDER-declaration (BC-P2-39)", F4, "F4.b1", "UNDER-declaration", 1, lambda l: "ok=False" in l),
    ("F4.b1 side effect of the under-declared plugin (absent line = no side effect)", F4, "F4.b1", "UNDER-declaration", 2, lambda l: "side effect present" not in l),
    ("F4.b3/b4 TOFU reset re-baselines drifted bytes (BC-P2-40)", F4, "F4.b3/b4", "after reset", 0, lambda l: "ok=False" in l),
    ("F4.b3/b4 interpreter-only command runs unpinned (BC-P2-40)", F4, "F4.b3/b4", "interpreter-only command", 1, lambda l: "ok=False" in l),
    ("F4.b5 re-registering while the gate is PENDING returns the SAME gate (BC-P2-11)", F4, "F4.b5 ", "while it is PENDING", 1, "SAME_GATE"),
    ("F4.b5.x unrelated answered gate registers a plugin (BC-P2-11)", F4, "F4.b5.x", "register a NEW network plugin", 1, lambda l: "registered= False" in l),
    ("F4.b5.x the plugin then runs", F4, "F4.b5.x", "register a NEW network plugin", 2, lambda l: "ok=False" in l),
    ("F4.b2.x forged registry entry runs (BC-P2-09)", F4, "F4.b2.x", "netplug is now 'registered'", 1, lambda l: "ok=False" in l),
    ("F4.b2.x doctor D028 (the probe prints only its first 400 characters; see W7-09.b)", F4, "F4.b2.x", "netplug is now 'registered'", 3, None),
    ("F4.b2.x suite plugin_governance reports the forged entry", F4, "F4.b2.x", "netplug is now 'registered'", 4, lambda l: "mentioning netplug: []" not in l),
    ("F4.b6 any existing record as security review (BC-P2-41)", F4, "F4.b6", "naming ANY existing record", 1, lambda l: "installed= False" in l),
    ("F3 (b) approved install gate proceeds (BC-P2-41)", F23, "F3.b2..b8", "after approval:", 0, lambda l: "installed= True" in l),
    ("F3 (b) citing the answered gate", F23, "F3.b2..b8", "citing the answered gate", 0, lambda l: "installed= True" in l),
    ("F2.b8.x hand-declared plugin shown registered/approved", F23, "F2.b8.x", "generated tool-registry entry", 0, lambda l: "status=active" not in l),
]


def verdict(pred, line, text=""):
    if pred == "SAME_GATE":
        first = after(text, "F4.b5 ", "register elevated plugin", 1)
        g1 = re.findall(r"gate= (HDG-\d+)", first)
        g2 = re.findall(r"gate= (HDG-\d+)", line)
        return "PASS" if g1 and g2 and g1 == g2 else "FAIL"
    if line == "(no line)" and pred is not None:
        return "PASS" if pred("") else "FAIL"
    if pred is None or line.startswith("("):
        return "INFO"
    return "PASS" if pred(line) else "FAIL"


for mode in ("unedited", "shim"):
    print(f"\n######## mode={mode}  base={BASE}  final={FINAL}")
    for lid, f, hdr, marker, off, pred in LINES:
        tb, ta = read(BASE, mode, f), read(FINAL, mode, f)
        b = after(tb, hdr, marker, off)
        a = after(ta, hdr, marker, off)
        print(f"- {lid}\n    base  [{verdict(pred, b, tb)}] {b}\n    final [{verdict(pred, a, ta)}] {a}")
    for label in (BASE, FINAL):
        t = read(label, mode, "synthesis.LEAD-X4-registered-module-plugin-unpinned.out")
        xs = re.findall(r"^X (\S+) (PASS|FAIL)", t, flags=re.M)
        tail = [l for l in t.splitlines() if l.startswith("SUMMARY") or "Error" in l][-1:] if t else ["(no output)"]
        print(f"- LEAD-X4 {label}: {xs} {tail}")

print("\nNote: in mode=unedited the probes cannot produce a human answer on either tree (WS-3 refuses `decide --by owner`),"
      "\nso lines that need one (F3 (b), F4.b5, F4.b5.x, LEAD-X4) are measured in mode=shim; their unedited lines are not evidence.")
print("\n######## WS-7 named checks (legitimate paths; base is the negative control)")
for label in (BASE, FINAL):
    p = os.path.join(HERE, "probes", f"ws07-named-checks.{label}.out")
    t = open(p).read() if os.path.exists(p) else ""
    s = [l for l in t.splitlines() if l.startswith("SUMMARY")]
    print(f"- {label}: {s[-1] if s else '(no output)'}")
