"""Writes tools/checks.json: the manifest's four checks, each a command run with `bash -c` from the repository root.
   0 syntax   1 structure (order of the gate check, the registration and the exec; the lead command kept; nothing by
   process name)   2 behaviour (tools/launch_gate_check.sh embedded as a here-document: stub claude and gov, an open and
   a shut gate)   3 the companion test change has landed (a stand-in gov in the two existing launcher test beds).
No check needs pytest: the operator's dry run plants HOME, which hides the user-site pytest."""
import json
import os

D = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(D, "launch_gate_check.sh")) as f:
    body = f.read()
assert "EOF" not in body
R = "governance/project/orchestration/tools/dispatch/launch_now.sh"
structure = (
    "python3 -I -c 'import sys; t=open(\"%s\").read(); c=\"\\n\".join(l for l in t.splitlines() if not l.lstrip().startswith(\"#\")); "
    "i=[c.index(x) for x in (\"resources --check\",\"resources --register\",\"\\nexec \")]; "
    "bad=(\"pgrep\",\"pkill\",\"killall\",\"pidof\"); "
    "sys.exit(0 if i==sorted(i) and \"LAUNCH_GATE_SHUT\" in c and \"LAUNCH_NOT_REGISTERED\" in c and "
    "\"--append-system-prompt-file\" in c and not any(b in c for b in bad) else 1)'" % R)
checks = [
    {"cmd": "bash -n " + R, "exit": 0, "count": None},
    {"cmd": structure, "exit": 0, "count": None},
    {"cmd": "bash <<'EOF'\n" + body + "EOF", "exit": 0, "count": None},
    {"cmd": "grep -q 'bin/gov' tests/unit/launch/test_w2_153_template.py && grep -q '\"bin\" / \"gov\"' tests/acceptance/W2-153/w2_153_support.py",
     "exit": 0, "count": None},
]
with open(os.path.join(D, "checks.json"), "w") as f:
    json.dump(checks, f, indent=1)
    f.write("\n")
print(len(checks), "checks written")
