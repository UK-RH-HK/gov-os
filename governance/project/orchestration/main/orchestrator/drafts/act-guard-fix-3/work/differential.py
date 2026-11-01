"""Differential check on the real command history: every Bash command in the session transcripts that names the
acceptance tests (judged as an orchestrator, rule 1) and every command of an auditor session (rule 5), run through
the live hook's copy and the candidate. Lists each command the live copy refuses and the candidate allows, and the
reverse, by index only; commands are kept in this scratch folder (diff_cmds.json), never printed here.
Usage: differential.py <live hook> <candidate hook>"""
import glob, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
LIVE, CAND = sys.argv[1], sys.argv[2]
MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"

cases, seen = [], set()
for f in glob.glob(os.path.expanduser("~/.claude/projects/*/**/*.jsonl"), recursive=True):
    if os.path.getmtime(f) < 1793000000:
        continue
    try:
        txt = open(f).read()
    except OSError:
        continue
    m = re.findall(r'(/tmp/(?:[\w.-]+/){0,2}?)claude-1000/-home', txt)
    top = max(set(m), key=m.count).rstrip("/") if m else "/tmp"
    auditor = "gov-launch-independent-auditor" in top
    for line in txt.splitlines():
        if '"tool_use"' not in line or '"Bash"' not in line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        for blk in (ev.get("message") or {}).get("content") or []:
            if not isinstance(blk, dict) or blk.get("type") != "tool_use" or blk.get("name") != "Bash":
                continue
            cmd = (blk.get("input") or {}).get("command")
            if not isinstance(cmd, str) or len(cmd) > 32768:
                continue
            role = "independent-auditor" if auditor else "orchestrator"
            if role == "orchestrator" and "tests/acceptance" not in cmd:
                continue
            key = (cmd, role)
            if key in seen:
                continue
            seen.add(key)
            cwd = ev.get("cwd") or MAIN
            root = (re.match(r"(/home/usain/gov-os-worktrees/[^/]+)", cwd) or [None])[0] or MAIN
            cases.append({"cmd": cmd, "role": role, "cwd": cwd, "root": root,
                          "tmpdir": top if top != "/tmp" else None})


def run(hook, c):
    env = dict(os.environ, GOV_ROLE=c["role"], GOV_TICKET="", CLAUDE_PROJECT_DIR=c["root"])
    env.pop("TMPDIR", None)
    if c["tmpdir"]:
        env["TMPDIR"] = c["tmpdir"]
    ev = {"tool_name": "Bash", "tool_input": {"command": c["cmd"]}, "cwd": c["cwd"], "session_id": "diff"}
    try:
        p = subprocess.run([PY, "-E", hook], input=json.dumps(ev), capture_output=True, text=True, env=env, timeout=90)
    except subprocess.TimeoutExpired:
        return "timeout", ""
    if p.returncode == 2:
        return "deny", "exit2 " + p.stderr[-160:]
    if p.stdout.strip():
        h = json.loads(p.stdout)["hookSpecificOutput"]
        return h["permissionDecision"], h["permissionDecisionReason"][:90]
    return "allow", ""


def both(c):
    return run(LIVE, c), run(CAND, c)


with ThreadPoolExecutor(10) as ex:
    res = list(ex.map(both, cases))
json.dump([dict(c, live=r[0], cand=r[1]) for c, r in zip(cases, res)], open(os.path.join(HERE, "diff_cmds.json"), "w"))
from collections import Counter
print("commands:", len(cases), Counter(c["role"] for c in cases))
print("outcomes (live, candidate):", Counter((r[0][0], r[1][0]) for r in res))
for i, (c, r) in enumerate(zip(cases, res)):
    if r[0][0] != r[1][0]:
        print(f"  #{i} {c['role'][:5]} live={r[0][0]:5} cand={r[1][0]:5} | live: {r[0][1][:60]} | cand: {r[1][1][:60]}")
