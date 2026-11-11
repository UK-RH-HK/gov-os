"""Writes tools/checks.json: the manifest's checks, each a command run with `bash -c` from the repository root.
   0 syntax of the two files (no byte-code written)   1 the Stop hook's behaviour (tools/hook_check.py as a here-document)
   2 the dispatcher's idle item (tools/dispatcher_check.py)   3 both files tracked in git.
No check needs pytest (the operator's dry run plants HOME, which hides the user-site pytest); the unit tests are the
companion test change (companion-tests.diff)."""
import json
import os

D = os.path.dirname(os.path.abspath(__file__))
HOOK = "governance/project/orchestration/tools/stop_idle_check.py"
DISP = "governance/project/orchestration/tools/dispatch/dispatcher.py"


def body(name):
    with open(os.path.join(D, name)) as f:
        text = f.read()
    assert "PYEOF" not in text
    return text


checks = [
    {"cmd": "python3 -I -c 'import ast,sys; [ast.parse(open(p).read(), p) for p in sys.argv[1:]]' %s %s" % (HOOK, DISP),
     "exit": 0, "count": None},
    {"cmd": "python3 -I - <<'PYEOF'\n" + body("hook_check.py") + "PYEOF", "exit": 0, "count": 2},
    {"cmd": "python3 -I - <<'PYEOF'\n" + body("dispatcher_check.py") + "PYEOF", "exit": 0, "count": 4},
    {"cmd": "git ls-files --error-unmatch %s %s" % (HOOK, DISP), "exit": 0, "count": None},
]
with open(os.path.join(D, "checks.json"), "w") as f:
    json.dump(checks, f, indent=1)
    f.write("\n")
print(len(checks), "checks written")
