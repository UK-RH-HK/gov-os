# landing_select.sh's selection for lead_verify.sh: select_tests.py on these commits' own changes (--merge), tree at HEAD
import os, sys
sel = os.environ.get("LANDING_SELECT") or "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py"
os.execvp(sys.executable, [sys.executable, sel, *sys.argv[1:], "--merge", "8f00bb90810b044d6115c62a73c315fa1e0b16ad"])
