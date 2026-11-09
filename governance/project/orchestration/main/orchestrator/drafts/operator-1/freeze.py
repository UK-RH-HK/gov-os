#!/usr/bin/env python3
"""ACT-OPERATOR-1: write the built hashes into apply.sh (run after build.py, before the rehearsal).

    python3 freeze.py <main tree>

Each `NAME=<value>` line of apply.sh's hash block is set from the file it stands for; install.sums is rebuilt from the
tree's governance/project/operator/ at HEAD with the two code drafts in place. Prints each value.
"""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = sys.argv[1] if len(sys.argv) > 1 else "/home/usain/Dynamic-Agentic-Engineering-OS"
T = ".gov-runtime/scratch/orchestrator/tools"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def head_blob(rel):
    return hashlib.sha256(subprocess.run(["git", "-C", MAIN, "show", f"HEAD:{rel}"], capture_output=True,
                                         check=True).stdout).hexdigest()


# install.sums: every tracked file of the operator folder at HEAD, operator_run.py from the draft, plus freeze_gate.py
files = subprocess.run(["git", "-C", MAIN, "ls-files", "governance/project/operator"], capture_output=True, text=True,
                       check=True).stdout.split()
rows = []
for f in files:
    rel = f[len("governance/project/operator/"):]
    h = sha(os.path.join(HERE, "code/operator_run.py")) if rel == "operator_run.py" else head_blob(f)
    rows.append((rel, h))
rows.append(("freeze_gate.py", sha(os.path.join(HERE, "code/freeze_gate.py"))))
with open(os.path.join(HERE, "install.sums"), "w") as fo:
    for rel, h in sorted(rows):
        fo.write(f"{h}  {rel}\n")

V = {
    "HOOK_PRE_AFTER": sha(os.path.join(HERE, "pretooluse.pre.candidate.py")),
    "HOOK_POST_AFTER": sha(os.path.join(HERE, "pretooluse.post.candidate.py")),
    "MAP_BEFORE": head_blob("governance/project/path-map.yaml"),
    "MAP_AFTER": sha(os.path.join(HERE, "path-map.candidate.yaml")),
    "RUN_BEFORE": head_blob("governance/project/operator/operator_run.py"),
    "RUN_AFTER": sha(os.path.join(HERE, "code/operator_run.py")),
    "GATE_AFTER": sha(os.path.join(HERE, "code/freeze_gate.py")),
    "UNIT_AFTER": sha(os.path.join(HERE, "code/test_act_operator_1.py")),
    "MQ_BEFORE": head_blob("governance/project/orchestration/tools/merge_queue.py"),
    "MQ_AFTER": sha(os.path.join(HERE, "code/merge_queue.py")),
    "GITHOOK_AFTER": sha(os.path.join(HERE, "reference-transaction.candidate")),
    "LS_BEFORE": sha(os.path.join(MAIN, T, "landing_select.sh")),
    "LS_AFTER": sha(os.path.join(HERE, "landing_select.candidate.sh")),
    "TLS_BEFORE": sha(os.path.join(MAIN, T, "test_landing_select.sh")),
    "TLS_AFTER": sha(os.path.join(HERE, "test_landing_select.candidate.sh")),
    "SUMS": sha(os.path.join(HERE, "install.sums")),
    "SETTINGS_BUILT": sha(os.path.join(HERE, "operator-settings.json")),
    "CRONLINE_SHA": sha(os.path.join(HERE, "crontab.line")),
}
p = os.path.join(HERE, "apply.sh")
text = open(p).read()
for k, v in V.items():
    text, n = re.subn(rf"^{k}=.*$", f"{k}={v}", text, count=1, flags=re.M)
    if n != 1:
        sys.exit(f"freeze.py: no line {k}= in apply.sh")
    print(f"{k}={v[:12]}")
if "@" in "".join(ln for ln in text.splitlines() if re.match(r"^[A-Z_]+=", ln)):
    sys.exit("freeze.py: a placeholder is left in apply.sh")
open(p, "w").write(text)
