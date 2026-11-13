"""ACT-CONTEXT-WATCH-1's behaviour check of the hook the registration runs (run from the repository root with
`python3 -I - < this file`, in the manifest as a here-document). Runs template/governance/kernel/hooks/context_watch.py as
the registered command does (the interpreter with -E, no byte-code) on planted PostToolUse events: a planted project folder in
a fresh temporary directory, a planted transcript, GOV_ROLE engineer on a planted ticket (a worker on claude-opus-5-5: its own window, 1,000,000; no
session has a token cap, DEC-1141). Nothing live is read or written. Prints 8 and exits 0 when: 180,000 tokens (the withdrawn
cap's 90 %) gives no output; 50 % and 84 % give no output; 85 % gives one
additionalContext (with READ FIRST and the not-a-stop sentence) and no decision key; the next call in the session gives
none; a fall to 40 % re-arms and 99 % reminds once more; a subagent's event (agent_id) gives none; a missing transcript, a
malformed (cut) assistant line and an empty event give no output and exit 0."""
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HOOK = os.path.abspath("template/governance/kernel/hooks/context_watch.py")
T = tempfile.mkdtemp(prefix="context-watch-1-check-")
os.makedirs(os.path.join(T, "proj"))
n = 0


def ok(cond, what):
    global n
    if not cond:
        sys.stderr.write("FAIL: " + what + "\n")
        sys.exit(1)
    n += 1


def transcript(tokens, name="t.jsonl", tail=""):
    p = os.path.join(T, name)
    line = {"type": "assistant", "message": {"model": "claude-opus-5-5", "usage": {
        "input_tokens": 1, "cache_creation_input_tokens": 0, "cache_read_input_tokens": tokens - 1}}}
    with open(p, "w") as f:
        f.write(json.dumps({"type": "user", "message": {"content": "x"}}) + "\n" + json.dumps(line) + "\n" + tail)
    return p


def run(stdin, sid="s1"):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "CLAUDE_PROJECT_DIR": os.path.join(T, "proj"),
           "GOV_ROLE": "engineer", "GOV_TICKET": "W2-9", "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, "-E", "-B", HOOK], input=stdin, capture_output=True, text=True, env=env, cwd=T)


def event(path, sid="s1", **extra):
    return json.dumps({"hook_event_name": "PostToolUse", "session_id": sid, "transcript_path": path,
                       "cwd": os.path.join(T, "proj"), "tool_name": "Bash", **extra})


for pct, tokens in ((18, 180000), (50, 500000), (84, 840000)):
    r = run(event(transcript(tokens, f"p{pct}.jsonl"), sid=f"s{pct}"))
    ok(r.returncode == 0 and r.stdout == "", f"{pct} % gives no output")
r = run(event(transcript(850000, "p85.jsonl")))
out = json.loads(r.stdout) if r.stdout else {}
ctx = out.get("hookSpecificOutput", {}).get("additionalContext", "")
ok(r.returncode == 0 and out["hookSpecificOutput"]["hookEventName"] == "PostToolUse" and "READ FIRST:" in ctx
   and "not a stop" in ctx and "decision" not in out, "85 % gives one additionalContext")
r = run(event(transcript(950000, "p95.jsonl")))
ok(r.returncode == 0 and r.stdout == "", "the next call in the session gives none")
run(event(transcript(400000, "p40.jsonl")))
r = run(event(transcript(990000, "p99.jsonl")))
ok(r.returncode == 0 and r.stdout.count("additionalContext") == 1, "a fall to 40 % re-arms")
r = run(event(transcript(950000, "px.jsonl"), sid="s77", agent_id="a1"))
ok(r.returncode == 0 and r.stdout == "", "a subagent's event gives none")
mal = os.path.join(T, "pm.jsonl")
open(mal, "w").write('{"type": "assistant", "message": {"usage": {"input_tokens": 190000, TRUNCATED\n')
bad = [run(event("/nonexistent/none.jsonl", sid="s5")), run(event(mal, sid="s6")), run("")]
ok(all(b.returncode == 0 and b.stdout == "" for b in bad), "missing transcript, a cut assistant line, empty event")
print(n)
