"""Read-only: which existing review records change READY if a KPI line marked fail blocks (and if any value but pass does).
   python3 -I scan_history.py <repo root> <folder holding verdict_old.py, the verdict.py before this ACT>
Paths under a folder named hidden or memory-verdict* are excluded in git's own pathspec, so their contents are never read."""
import json, os, re, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[2])
import verdict_old as old
root = sys.argv[1]
files = subprocess.run(["git", "-C", root, "grep", "-l", "```verdict", "--", ".", ":(exclude)**/hidden/**",
                        ":(exclude)**/memory-verdict*/**"], capture_output=True, text=True).stdout.split()
changed_fail, changed_notpass, total, rows = [], [], 0, []
for f in files:
    if "/hidden" in f or "memory-verdict" in f:
        continue
    text = open(os.path.join(root, f), errors="replace").read()
    ok, _ = old.ready(text)
    if ok is None:
        continue
    total += 1
    blocks = list(old.BLOCK.finditer(text))
    try:
        kp = json.loads(blocks[-1].group(1))["kpis"]
    except Exception:
        continue
    fails = [k.get("kpi") for k in kp if isinstance(k, dict) and k.get("verdict") == "fail"]
    notpass = [k.get("kpi") for k in kp if isinstance(k, dict) and k.get("verdict") != "pass"]
    if ok and fails:
        changed_fail.append((f, fails))
    if ok and notpass:
        changed_notpass.append((f, notpass))
print("records with a verdict block:", total)
print("READY today, last block has a KPI marked fail:", len(changed_fail))
for f, k in changed_fail: print("  ", f, k)
print("READY today, last block has a KPI not marked pass:", len(changed_notpass))
for f, k in changed_notpass:
    if (f, k) not in changed_fail: print("  ", f, k)
