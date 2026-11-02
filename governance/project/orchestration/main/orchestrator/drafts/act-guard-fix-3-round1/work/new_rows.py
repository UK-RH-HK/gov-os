"""Rows 61-63 of guard-refusals.jsonl (added during this work): rebuilt from their transcripts, judged by the live copy
and the candidate. Prints decisions only."""
import json, os, subprocess, sys
L = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl"
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
rows = [json.loads(l) for l in open(L) if l.strip()][61:]
for i, r in enumerate(rows, 61):
    inp = None
    for line in open(r["transcript"]):
        if r["key"] in line and '"tool_use"' in line:
            for b in json.loads(line)["message"]["content"]:
                if isinstance(b, dict) and b.get("id") == r["key"]:
                    inp = b["input"]
    out = []
    for hook in sys.argv[1:]:
        env = dict(os.environ, GOV_ROLE="orchestrator", GOV_TICKET="", CLAUDE_PROJECT_DIR=
                   "/home/usain/Dynamic-Agentic-Engineering-OS")
        env.pop("TMPDIR", None)
        ev = {"tool_name": "Bash", "tool_input": inp, "cwd": r["cwd"], "session_id": "x"}
        p = subprocess.run([PY, "-E", hook], input=json.dumps(ev), capture_output=True, text=True, env=env)
        out.append("deny" if p.returncode == 2 or '"deny"' in p.stdout else "allow")
    print(i, r["time"], dict(zip(["live", "candidate"], out)))
