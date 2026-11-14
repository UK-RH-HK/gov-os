import json, subprocess, os, sys
W = "/home/usain/gov-os-worktrees/W2-88b"
C = "/home/usain/gov-os-runs/W2-88b/redis"
cases = {
 "heredoc": f"mkdir -p {C}/docs/audit && cat > {C}/docs/audit/A5-path-map-verdict.md <<'V'\n---\nid: x\n---\nV",
 "add": f"git -C {C} add -- docs/audit/A5-path-map-verdict.md",
 "commit": f'git -C {C} -c user.name="independent-auditor (W2-88b A5)" -c user.email="auditor@example.invalid" commit -q -m "A5 verdict" --trailer "Role: independent-auditor"',
 "log": f"git -C {C} log -1 --format='%H %(trailers:key=Role,valueonly)'",
}
env = dict(os.environ, GOV_ROLE="independent-auditor", GOV_TICKET="DAEO-aks1", CLAUDE_PROJECT_DIR=W, PYTHONPATH=W + "/src")
for cwd in (W, C):
    for k, cmd in cases.items():
        data = {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": cwd, "agent_type": "independent-auditor"}
        p = subprocess.run(["python3", W + "/.claude/hooks/pretooluse.py"], input=json.dumps(data), capture_output=True, text=True, env=env, cwd=W)
        out = (p.stdout.strip() or "(allow: no output)")[:300]
        print(f"cwd={os.path.basename(cwd)} {k}: rc={p.returncode} {out} {p.stderr.strip()[:200]}")
# the Write tool form too
data = {"tool_name": "Write", "tool_input": {"file_path": C + "/docs/audit/A5-path-map-verdict.md", "content": "x"}, "cwd": W, "agent_type": "independent-auditor"}
p = subprocess.run(["python3", W + "/.claude/hooks/pretooluse.py"], input=json.dumps(data), capture_output=True, text=True, env=env, cwd=W)
print("Write tool:", p.returncode, (p.stdout.strip() or "(allow)")[:300])
