"""DEC-953 item 2: the four-rule hook's two-minute check. Runs .claude/hooks/pretooluse.py under the pinned judge's
interpreter with event JSON, as the registered hook line does, and checks each kept rule refuses and each lifted form
passes. Prints one line per case and a last line PASS or FAIL. Usage: python3 guard4_check.py [hook path]"""
import json
import os
import subprocess
import sys

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
HOOK = ROOT + "/.claude/hooks/pretooluse.py"
LINE, PROJECT = None, ROOT
if len(sys.argv) > 2 and sys.argv[1] == "--settings":  # python3 guard4_check.py --settings <project root>
    PROJECT = sys.argv[2]
    LINE = json.load(open(PROJECT + "/.claude/settings.json"))["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    ROOT = PROJECT  # the planted paths are the tested tree's own
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
HELD = ROOT + "/governance/project/held-out.yaml"

# The hidden set's own glob and a measured role, read from the path map (no contents read).
import yaml  # noqa: E402
sets = (yaml.safe_load(open(ROOT + "/governance/project/path-map.yaml")).get("evaluation_sets") or {})
hidden_glob, measured = None, "engineer"
for entry in sets.values():
    if isinstance(entry, dict) and entry.get("hidden"):
        hidden_glob = entry["hidden"][0]
        measured = (entry.get("measures") or {}).get("roles", ["engineer"])[0]
        break
hidden_file = (hidden_glob or "fixtures/evaluation/x/hidden/**").replace("**", "q01.yaml").replace("*", "q01")
held = yaml.safe_load(open(HELD)).get("held_out_paths") or []
held_path = held[0] if held else None  # used only as an argument; never printed, never read

CASES = [
    # (name, role, tool, input, expected: deny|ask|allow)
    ("rule1 engineer Write acceptance", "engineer", "Write",
     {"file_path": ROOT + "/tests/acceptance/W2-64/t.py", "content": "x"}, "deny"),
    ("rule1 engineer bash redirect acceptance", "engineer", "Bash",
     {"command": "echo x > tests/acceptance/W2-64/t.py"}, "deny"),
    ("rule1 orchestrator Edit acceptance", "orchestrator", "Edit",
     {"file_path": ROOT + "/tests/acceptance/W2-64/t.py", "old_string": "a", "new_string": "b"}, "deny"),
    ("rule1 test designer Write acceptance", "independent-test-designer", "Write",
     {"file_path": ROOT + "/tests/acceptance/W2-64/t.py", "content": "x"}, "allow"),
    ("rule2 measured role reads hidden", measured, "Read", {"file_path": ROOT + "/" + hidden_file}, "deny"),
    ("rule2 held-out named", "orchestrator", "Bash", {"command": "ls " + (held_path or "/nonexistent-held")},
     "deny" if held_path else "allow"),
    ("rule2 measured role reads hidden in another worktree", measured, "Read",
     {"file_path": "/home/usain/gov-os-worktrees/W2-87/" + hidden_file}, "deny"),
    ("rule2 measured role reads hidden in a run clone", measured, "Bash",
     {"command": "cat /home/usain/gov-os-runs/W2-61/repo/" + hidden_file}, "deny"),
    ("rule2 measured role reads hidden in the main tree", measured, "Read",
     {"file_path": "/home/usain/Dynamic-Agentic-Engineering-OS/" + hidden_file}, "deny"),
    ("rule5 auditor writes its probe record", "independent-auditor", "Write",
     {"file_path": ROOT + "/docs/probes/DAEO-x/PR-x.md", "content": "x"}, "allow"),
    ("rule5 auditor writes its audit report", "independent-auditor", "Write",
     {"file_path": ROOT + "/docs/audit/wave-2/report.md", "content": "x"}, "allow"),
    ("rule5 auditor bash writes its record", "independent-auditor", "Bash",
     {"command": "echo x > docs/probes/DAEO-x/PR-x.md"}, "allow"),
    ("rule5 auditor writes /tmp", "independent-auditor", "Write", {"file_path": "/tmp/gov-guard4-a.txt", "content": "x"},
     "allow"),
    ("rule5 auditor edits code", "independent-auditor", "Edit",
     {"file_path": ROOT + "/src/gov/close/command.py", "old_string": "a", "new_string": "b"}, "deny"),
    ("rule5 auditor writes a test", "independent-auditor", "Write",
     {"file_path": ROOT + "/tests/unit/test_x.py", "content": "x"}, "deny"),
    ("rule5 auditor edits a ticket", "independent-auditor", "Edit",
     {"file_path": ROOT + "/.tickets/DAEO-sdxk.md", "old_string": "a", "new_string": "b"}, "deny"),
    ("rule5 auditor edits the register", "independent-auditor", "Edit",
     {"file_path": ROOT + "/docs/DECISION_REGISTER.md", "old_string": "a", "new_string": "b"}, "deny"),
    ("rule5 auditor edits a lead handover", "independent-auditor", "Write",
     {"file_path": ROOT + "/.gov-runtime/scratch/lead/CHECKPOINT.md", "content": "x"}, "deny"),
    ("rule5 auditor bash writes code", "independent-auditor", "Bash", {"command": "echo x > src/gov/x.py"}, "deny"),
    ("rule5 auditor unreadable bash", "independent-auditor", "Bash", {"command": "mkdir -p $D/t"}, "deny"),
    ("rule5 auditor reads code", "independent-auditor", "Read", {"file_path": ROOT + "/src/gov/close/command.py"},
     "allow"),
    ("rule3 read .env", "engineer", "Read", {"file_path": ROOT + "/.env"}, "deny"),
    ("rule3 cat ssh key", "orchestrator", "Bash", {"command": "cat ~/.ssh/id_ed25519"}, "deny"),
    ("rule4 engineer pip install", "engineer", "Bash", {"command": "pip install requests"}, "deny"),
    ("rule4 CTO (orchestrator on W2-00) pip install", "orchestrator", "Bash", {"command": "pip install requests"},
     "ask"),
    ("rule4 lead (orchestrator on W2-87) pip install", "orchestrator@DAEO-s9qc", "Bash",
     {"command": "pip install requests"}, "deny"),
    ("rule4 lead (orchestrator on W2-64) npm install", "orchestrator@DAEO-0uhh", "Bash",
     {"command": "npm install left-pad"}, "deny"),
    ("rule4 CTO's engineer subagent pip install", "orchestrator", "Bash", {"command": "pip install requests"}, "deny"),
    ("rule4 sudo", "orchestrator", "Bash", {"command": "sudo ls"}, "deny"),
    ("lifted heredoc to tmp", "engineer", "Bash", {"command": "cat > /tmp/gov-guard4-x.txt <<EOF\nif a > 1:\nEOF"}, "allow"),
    ("lifted engineer writes src", "engineer", "Write", {"file_path": ROOT + "/src/gov/other.py", "content": "x"}, "allow"),
    ("lifted var write target", "engineer", "Bash", {"command": "mkdir -p $D/t"}, "allow"),
    ("lifted backticks", "engineer", "Bash", {"command": "echo `date` > /tmp/gov-guard4-y.txt"}, "allow"),
    ("lifted inline python braces", "engineer", "Bash", {"command": "python3 -c \"print({1: 2})\""}, "allow"),
    ("lifted rm", "lead", "Bash", {"command": "rm -rf /tmp/gov-guard4-nothing"}, "allow"),
    ("lifted engineer reads acceptance", "engineer", "Read",
     {"file_path": ROOT + "/tests/acceptance/W2-64/README.md"}, "allow"),
    ("lifted CronCreate", "orchestrator", "CronCreate", {"cron": "0 7 * * *", "prompt": "x"}, "allow"),
    ("lifted general-purpose subagent write", "orchestrator", "Write",
     {"file_path": "/tmp/gov-guard4-z.txt", "content": "x"}, "allow"),
]

ok = True
for name, role, tool, tin, want in CASES:
    agent = None
    if "subagent" in name:
        agent = "engineer" if "engineer subagent" in name else "general-purpose"
    event = {"tool_name": tool, "tool_input": tin, "cwd": ROOT, "session_id": "guard4-check", "agent_type": agent}
    role, _, ticket = role.partition("@")
    env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket or "DAEO-sdxk", CLAUDE_PROJECT_DIR=ROOT)
    if LINE:  # the registered hook line itself, as Claude Code runs it, from a settings file
        env["CLAUDE_PROJECT_DIR"] = PROJECT
        p = subprocess.run(["sh", "-c", LINE], input=json.dumps(event), capture_output=True, text=True, env=env,
                           timeout=60)
    else:
        p = subprocess.run([PY, "-E", HOOK], input=json.dumps(event), capture_output=True, text=True, env=env,
                           timeout=60)
    got = "allow"
    if p.returncode == 2:
        got = "deny(exit 2)"
    elif p.stdout.strip():
        got = json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"]
    good = got == want or (want == "deny" and got.startswith("deny"))
    ok &= good
    print(("ok   " if good else "FAIL ") + f"{name}: want {want}, got {got}" + ("" if good else f" | {p.stderr[-200:]}"))
print("PASS" if ok else "FAIL")
