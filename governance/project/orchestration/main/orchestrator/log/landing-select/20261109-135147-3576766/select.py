# landing_select.sh's selection for lead_verify.sh: select_tests.py on these commits' own changes (--merge), tree at HEAD
import os, sys
sel = os.environ.get("LANDING_SELECT") or "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py"
os.execvp(sys.executable, [sys.executable, sel, *sys.argv[1:], "--merge", "8038e0ee648cf9b0cc89ad34aab388d81a03bf2c"])
