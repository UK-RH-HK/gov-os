"""Replay every logged refusal (guard-refusals.jsonl, rebuilt by rebuild4.py into corpus4.json) through today's
hook (ACT-GUARD-FIX-3's files, identical to .claude/hooks/) and the ACT-GUARD-FIX-4 candidate, as Claude Code runs
them. Rows 50-53 carry no tool_use id: measured as their twins (54, 55, 58, 59), as ACT-GUARD-FIX-3 did.
Usage: replay4.py [--json out.json]"""
import json
import os
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hookrun import MAIN, run  # noqa: E402

H4 = os.path.join(os.path.dirname(HERE), "pretooluse.py")
H3 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "act-guard-fix-3", "pretooluse.py")
TWIN = {50: 54, 51: 55, 52: 58, 53: 59}
corpus = json.load(open(os.path.join(HERE, "corpus4.json")))
# The roles of rows 61-86, from each row's note (the CTO's labels): the CTO and leads run as orchestrator.
ROLE = {**{i: "orchestrator" for i in (61, 62, 63, 70, 71, 72)},
        **{i: "independent-auditor" for i in (64, 67, 68, 69, 75, 76)},
        **{i: "engineer" for i in (65, 66, 73, 74, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86)}}
LAUNCH = re.compile(r"/tmp/gov-launch-[a-z-]+-[a-z0-9]{8}")


def root_of(cwd):
    m = re.match(r"(/home/usain/gov-os-worktrees/[^/]+)", cwd or "")
    return m.group(1) if m else MAIN


def rule_of(text):
    text = text or ""
    if text.startswith(("a command that may write", "implementer never", "only the independent test designer")):
        return "rule 1"
    if text.startswith("a reviewer or auditor"):
        return "rule 5"
    if text.startswith("the call reads a secret"):
        return "rule 3"
    return "rule 2"


def case(row):
    src = corpus[TWIN.get(row["i"], row["i"])]
    role = src.get("launch_role") if src.get("from") == "fix-3 corpus" else ROLE.get(src["i"], "orchestrator")
    role = role or "orchestrator"
    tmpdir = src.get("tmpdir")
    if tmpdir is None and src.get("from") != "fix-3 corpus":
        m = LAUNCH.search(json.dumps(src.get("input")))
        tmpdir = m.group(0) if m else None
    cwd = src.get("cwd") or MAIN
    kw = dict(cwd=cwd, root=root_of(cwd), agent=src.get("agent_type"), tmpdir=tmpdir)
    g3 = run(H3, role, src["tool"], src["input"], **kw)
    g4 = run(H4, role, src["tool"], src["input"], **kw)
    return {"i": row["i"], "twin": TWIN.get(row["i"]), "rule": rule_of(row["rule"]), "role": role,
            "verdict": row.get("verdict"), "today": g3[0], "fix4": g4[0], "why4": g4[1], "why3": g3[1],
            "note": (row.get("note") or "")[:160]}


with ThreadPoolExecutor(6) as ex:
    rows = list(ex.map(case, corpus))

by = Counter((r["rule"], r["today"], r["fix4"]) for r in rows)
print(f"{len(rows)} logged refusals replayed (rule, today's hook, fix-4):")
for k in sorted(by):
    print("  ", k, by[k])
for rule in ("rule 1", "rule 5", "rule 2", "rule 3"):
    rs = [r for r in rows if r["rule"] == rule]
    print(f"  {rule}: logged {len(rs)}, refused today {sum(r['today'] != 'allow' for r in rs)}, "
          f"refused by fix-4 {sum(r['fix4'] != 'allow' for r in rs)}")
print("refused by fix-4:")
for r in rows:
    if r["fix4"] != "allow":
        print(f"   row {r['i']} {r['rule']} {r['role']} | {r['why4'][:120]} | {r['note'][:110]}")
print("passed by fix-4, refused today:", [r["i"] for r in rows if r["today"] != "allow" and r["fix4"] == "allow"])
print("refused by fix-4, passed today:", [r["i"] for r in rows if r["today"] == "allow" and r["fix4"] != "allow"])
if "--json" in sys.argv:
    json.dump(rows, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
