import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hookrun import run, MAIN

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H4 = os.path.join(D, "pretooluse.py")
H3 = os.path.join(os.path.dirname(D), "act-guard-fix-3", "pretooluse.py")
WT = "/home/usain/gov-os-worktrees/EMG-queue"
cases = [
    ("orchestrator", "rm -rf /"),
    ("orchestrator", "rm -rf ~"),
    ("orchestrator", "rm -rf /home/usain/Dynamic-Agentic-Engineering-OS"),
    ("orchestrator", "rm -rf ."),
    ("orchestrator", "rm -rf .git"),
    ("orchestrator", "rm README.md"),
    ("orchestrator", "rm -rf docs"),
    ("orchestrator", "rm -rf .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/work/nothing"),
    ("orchestrator", "rm -rf /tmp/gov-os-emg-e3/x"),
    ("orchestrator", "rm -rf /tmp"),
    ("orchestrator", "rm -f ~/.bashrc"),
    ("orchestrator", "rm -rf \"$NOPE\"/"),
    ("orchestrator", "rm -rf \"$NOPE\"/*"),
    ("orchestrator", "d=$(mktemp -d); rm -rf \"$d\""),
    ("orchestrator", "out=$(mktemp -d); rm -f \"$out/x\""),
    ("orchestrator", "rm -rf \"${NOPE:?}\"/"),
    ("orchestrator", "for d in /tmp/a /; do rm -rf $d; done"),
    ("orchestrator", "cd / && rm -rf home"),
    ("orchestrator", "rm -rf ~/gov-os-worktrees"),
    ("orchestrator", "rm -rf ~/gov-os-worktrees/EMG-nothing"),
    ("orchestrator", "rm -rf ~/gov-os-runs/x"),
    ("orchestrator", "bash -c 'rm -rf /'"),
    ("orchestrator", "echo $(rm -rf ~)"),
    ("orchestrator", "rm -rf ./*"),
    ("engineer", "rm tests/acceptance/W2-64/t.py"),
    ("engineer", "cat > tests/acceptance/W2-64/t.py <<'EOF'\nx\nEOF"),
    ("engineer", "X=$(pwd); touch $X/tests/acceptance/W2-64/t.py"),
    ("engineer", "python3 -c \"open('tests/acceptance/W2-64/t.py','w')\""),
    ("independent-auditor", "B=$(mktemp -d); mkdir $B/r"),
    ("independent-auditor", "touch src/gov/x.py"),
    ("orchestrator", "grep -rn rm src | head"),
    ("orchestrator", "rm -f \"unclosed"),
]
for role, cmd in cases:
    a4 = run(H4, role, "Bash", {"command": cmd})
    a3 = run(H3, role, "Bash", {"command": cmd})
    print(f"{a3[0]:6} -> {a4[0]:6} {role[:12]:12} {cmd[:60]!r:64} {a4[1][:150]}")
