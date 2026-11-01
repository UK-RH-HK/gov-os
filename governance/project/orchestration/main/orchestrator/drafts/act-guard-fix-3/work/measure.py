"""Drive a candidate PreToolUse hook as Claude Code would (JSON on stdin, pinned interpreter with -E) over the
rebuilt refusal corpus and the planted cases. Usage: measure.py <hook.py> [--json out.json] [--quiet]"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
HOOK = sys.argv[1]
OUT = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
corpus = json.load(open(os.path.join(HERE, "corpus.json")))

# Rows 50-53 carry no tool_use id; the transcripts show four rule-1 Bash refusals in the CTO's tree on 1 Nov after
# 15:00 (rows 54, 55, 58, 59) matching their descriptions, so each is measured as its twin.
TWIN = {50: 54, 51: 55, 52: 58, 53: 59}
AUDITOR_RULES = ("a reviewer or auditor", "the call reads a secret")


def root_of(cwd):
    m = re.match(r"(/home/usain/gov-os-worktrees/[^/]+)", cwd or "")
    return m.group(1) if m else MAIN


def setting(row):
    """The session as it ran: a launched worker's role and TMPDIR from its launch folder (gov-launch-<role>-<id>),
    which its scratchpad paths show; otherwise the CTO or a lead (orchestrator, TMPDIR unset). Row 60 was the CTO's
    research subagent (GOV_ROLE orchestrator, agent type research)."""
    cwd = row["cwd"] or MAIN
    return row.get("launch_role") or "orchestrator", cwd, root_of(cwd)


def classify(rule):
    if rule.startswith("a command that may write") or rule.startswith("implementer never") or \
            rule.startswith("only the independent test designer"):
        return "rule1"
    if rule.startswith("a reviewer or auditor"):
        return "rule5"
    if rule.startswith("the call reads a secret"):
        return "rule3"
    if "listing whose start" in rule:
        return "rule2-listing"
    return "other"


def run(tool, tin, cwd, root, role, ticket="", agent=None, tmpdir=None):
    event = {"tool_name": tool, "tool_input": tin, "cwd": cwd, "session_id": "guard-fix-3", "agent_type": agent}
    env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket, CLAUDE_PROJECT_DIR=root)
    env.pop("TMPDIR", None)
    if tmpdir:
        env["TMPDIR"] = tmpdir
    p = subprocess.run([PY, "-E", HOOK], input=json.dumps(event), capture_output=True, text=True, env=env, timeout=90)
    if p.returncode == 2:
        return "deny", "exit 2: " + p.stderr[-200:]
    if p.stdout.strip():
        h = json.loads(p.stdout)["hookSpecificOutput"]
        return h["permissionDecision"], h["permissionDecisionReason"]
    return "allow", ""


def corpus_case(row):
    src = corpus[TWIN.get(row["i"], row["i"])]
    role, cwd, root = setting(src)
    got, why = run(src["tool"], src["input"], cwd, root, role, agent=src.get("agent_type"), tmpdir=src.get("tmpdir"))
    return {"i": row["i"], "twin": TWIN.get(row["i"]), "logged": classify(row["rule"] or ""), "role": role,
            "verdict": "fp", "got": got, "why": why}


# The planted cases, read from guard4_check.py (its CASES list, without running its loop).
g4 = open(MAIN + "/.gov-runtime/scratch/orchestrator/tools/guard4_check.py").read()
ns = {"__name__": "g4", "sys": sys}
saved = sys.argv
sys.argv = ["guard4_check.py"]
exec(g4[:g4.index("ok = True")], ns)
sys.argv = saved
planted = list(ns["CASES"])
extra = json.load(open(os.path.join(HERE, "planted_extra.json"))) if os.path.exists(os.path.join(HERE, "planted_extra.json")) else []
planted += [tuple(c) for c in extra]


def planted_case(c):
    name, role, tool, tin, want = c
    agent = None
    if "subagent" in name:
        agent = "engineer" if "engineer subagent" in name else "general-purpose"
    role, _, ticket = role.partition("@")
    got, why = run(tool, tin, MAIN, MAIN, role, ticket or "DAEO-sdxk", agent)
    good = got == want or (want == "deny" and got.startswith("deny"))
    return {"name": name, "want": want, "got": got, "ok": good, "why": why}


with ThreadPoolExecutor(8) as ex:
    rows = list(ex.map(corpus_case, corpus))
    pl = list(ex.map(planted_case, planted))

from collections import Counter
by = Counter((r["logged"], r["got"]) for r in rows)
print("corpus (61 rows, all logged false positives):")
for k in sorted(by):
    print("  ", k, by[k])
fp = sum(r["got"] == "deny" for r in rows)
print(f"  still refused: {fp}/61 = {100*fp/61:.1f}%")
for r in rows:
    if r["got"] != "allow" and "--quiet" not in sys.argv:
        print("   refused row", r["i"], r["logged"], r["role"], "|", r["why"][:110])
bad = [p for p in pl if not p["ok"]]
deny_want = sum(p["want"] == "deny" for p in pl)
missed = [p for p in pl if p["want"] == "deny" and not p["got"].startswith("deny")]
print(f"planted: {len(pl) - len(bad)}/{len(pl)} as expected; deny-cases {deny_want}, missed (allowed) {len(missed)}")
for p in bad:
    print("   FAIL", p["name"], "want", p["want"], "got", p["got"], "|", p["why"][:120])
if OUT:
    json.dump({"corpus": rows, "planted": pl}, open(OUT, "w"), indent=1)
