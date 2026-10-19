"""Append one scratch file to one tracked file: python3 append.py <source name in scratch> <register|bootstrap>."""
import sys

SCRATCH = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/"
TARGETS = {
    "register": "/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md",
    "bootstrap": "/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/bootstrap.md",
}
text = open(SCRATCH + sys.argv[1], encoding="utf-8").read()
target = TARGETS[sys.argv[2]]
old = open(target, encoding="utf-8").read()
with open(target, "a", encoding="utf-8") as f:
    f.write(("" if old.endswith("\n") else "\n") + text)
print("appended", len(text), "chars to", target)
