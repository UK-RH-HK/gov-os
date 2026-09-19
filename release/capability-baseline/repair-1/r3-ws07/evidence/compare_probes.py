#!/usr/bin/env python3
"""P2-AR-0038 — pair the audit-of-record probe lines and the named checks between the base run (53897c1) and the final
run of this branch, per mode, and print a verdict per line. Adapted from the round-2 WS-7 pairing
(repair-1/r2-ws07/evidence/compare_probes.py): same line table for the round-2 plugin/tool lines (here they show
that round 3 regressed none of them), plus the round-3 probes (beta-r D6, synthesis AC16-X2) and named checks. A
builder's summary of regression evidence, not an acceptance judgement.
Usage: python3 compare_probes.py <base-label> <final-label>"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE, FINAL = sys.argv[1], sys.argv[2]


def read(label, name):
    p = os.path.join(HERE, "probes", label, name)
    return open(p).read() if os.path.exists(p) else ""


def after(text, header, marker, n=1):
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


F4 = "gamma-r.F4-plugins.{mode}.out"
F23 = "gamma-r.F2F3-tools.{mode}.out"
LINES = [
    ("F4.b1 UNDER-declaration (BC-P2-39)", F4, "F4.b1", "UNDER-declaration", 1, lambda l: "ok=False" in l),
    ("F4.b1 side effect of the under-declared plugin (absent line = no side effect)", F4, "F4.b1", "UNDER-declaration", 2, lambda l: "side effect present" not in l),
    ("F4.b3/b4 TOFU reset re-baselines drifted bytes (BC-P2-40)", F4, "F4.b3/b4", "after reset", 0, lambda l: "ok=False" in l),
    ("F4.b3/b4 interpreter-only command runs unpinned (BC-P2-40)", F4, "F4.b3/b4", "interpreter-only command", 1, lambda l: "ok=False" in l),
    ("F4.b5 re-registering while the gate is PENDING returns the SAME gate (BC-P2-11)", F4, "F4.b5 ", "while it is PENDING", 1, "SAME_GATE"),
    ("F4.b5.x unrelated answered gate registers a plugin (BC-P2-11)", F4, "F4.b5.x", "register a NEW network plugin", 1, lambda l: "registered= False" in l),
    ("F4.b5.x the plugin then runs", F4, "F4.b5.x", "register a NEW network plugin", 2, lambda l: "ok=False" in l),
    ("F4.b2.x forged registry entry runs (BC-P2-09)", F4, "F4.b2.x", "netplug is now 'registered'", 1, lambda l: "ok=False" in l),
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


def x_lines(text):
    return re.findall(r"^X (\S+) (PASS|FAIL)", text, flags=re.M)


def stop_of(text):
    for l in reversed(text.splitlines()):
        if l.startswith("required command failed") or l.startswith("RuntimeError") or l.startswith("SUMMARY"):
            return l[:230]
    return "(no stop line)"


for mode in ("direct", "shim"):
    print(f"\n######## mode={mode}  base={BASE}  final={FINAL}")
    print("## round-2 WS-7 lines (regression check: both trees carry the round-2 repair)")
    for lid, f, hdr, marker, off, pred in LINES:
        fn = f.format(mode=mode)
        tb, ta = read(BASE, fn), read(FINAL, fn)
        b = after(tb, hdr, marker, off)
        a = after(ta, hdr, marker, off)
        print(f"- {lid}\n    base  [{verdict(pred, b, tb)}] {b}\n    final [{verdict(pred, a, ta)}] {a}")
    for name in ("synthesis.LEAD-X4-registered-module-plugin-unpinned", "synthesis.AC16-X2-authority-gate-chain",
                 "beta-r.D6-rebuild-guarantee"):
        for label in (BASE, FINAL):
            t = read(label, f"{name}.{mode}.out")
            print(f"- {name} {label}: X lines {x_lines(t)}; stop: {stop_of(t)}")

print("\nNote: in mode=direct the probes cannot produce a human answer on either tree (WS-3 refuses `decide --by owner`),"
      "\nso lines that need one are measured in mode=shim. beta-r D6 and synthesis AC16-X2 stop at their task-claim setup on"
      "\nboth trees (WS-5's DAG rules, BC-P2-16/BC-P2-34), before any registry line: they are not discriminating here; the"
      "\nround-3 named checks cover the registry move through legitimate paths.")
print("\n######## WS-7 round-3 named checks (legitimate paths; base is the negative control)")
for label in (BASE, FINAL):
    p = os.path.join(HERE, "probes", f"ws07-r3-named-checks.{label}.out")
    t = open(p).read() if os.path.exists(p) else ""
    s = [l for l in t.splitlines() if l.startswith("# SUMMARY")]
    print(f"- {label}: {s[-1] if s else '(no output)'}")
    for l in t.splitlines():
        if l.startswith(("X ", "C ")):
            print("    " + l[:150])

print("\n######## gamma-r F4 through the labelled derived copy (registry path only; derived/F4-plugins.registry-path.P2-AR-0038.sh), shim")
t = read(FINAL, "derived.gamma-r.F4-plugins.registry-path.shim.out")
for lid, f, hdr, marker, off, pred in LINES:
    if f != F4:
        continue
    a = after(t, hdr, marker, off)
    print(f"- {lid}\n    final [{verdict(pred, a, t)}] {a}")
