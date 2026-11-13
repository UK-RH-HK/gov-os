"""Builds after/quiet_check.py and after/nightly_restart.sh from before/ (DEC-1159 (1): the nightly beside the leads)."""
from pathlib import Path

D = Path(__file__).resolve().parent


def rep(s, a, b):
    assert s.count(a) == 1, a[:70]
    return s.replace(a, b)


s = (D / "before/quiet_check.py").read_text()
s = rep(s, "    quiet_check.py [--no-load] [--own-off]   --no-load leaves out the load test, --own-off accepts dispatch/OFF as the\n",
        "    quiet_check.py [--no-load] [--own-off] [--beside-leads]   --no-load leaves out the load test, --own-off accepts\n"
        "                                     dispatch/OFF as the\n")
s = rep(s, "What counts as something else running",
        "--beside-leads (DEC-1159 (1), the owner 2026-11-13: the nightly runs beside the leads, in its own capped unit): leads and\n"
        "their work are not \"something else running\": a running or launching lead, a lead's or slot's job, a heavy slot held, a\n"
        "heavy step outside a slot, a process in a worktree or the runs folder, pytest, heavy_slot.sh, launch_worker.sh,\n"
        "launch_now.sh, rebuild_slot.sh, a rebuild lock, and the load are left out. Still counted: a landing, a close, the merge queue, an ACT,\n"
        "the operator's freeze, a memory measure, another nightly, the main tree (a merge, a change, a young head), the rg storm,\n"
        "and the dispatcher's status being unreadable or stale. The nightly takes its heavy slots and the rebuild lock itself.\n\n"
        "What counts as something else running")
s = rep(s, "def process_reasons():\n    out = []\n    for pid, argv, cwd in processes():",
        "LEAD_SCRIPTS = (\"heavy_slot.sh\", \"rebuild_slot.sh\", \"launch_worker.sh\", \"launch_now.sh\")   # leads' own: left out --beside-leads (the nightly takes the rebuild lock itself)\n\n\n"
        "def process_reasons(beside=False):\n    out = []\n    for pid, argv, cwd in processes():")
s = rep(s, "        if any(cwd.startswith(r) for r in BUSY_ROOTS) and not cwd.startswith(OWN_RUNS):",
        "        in_busy = any(cwd.startswith(r) for r in BUSY_ROOTS) and not cwd.startswith(OWN_RUNS)\n"
        "        if beside and in_busy:\n"
        "            continue   # a lead's or worker's process (a landing's clone is named by the status and the job scripts)\n"
        "        if in_busy:")
s = rep(s, "        if why is None and any(b in JOB_SCRIPTS for b in base):",
        "        if why is None and any(b in JOB_SCRIPTS and not (beside and b in LEAD_SCRIPTS) for b in base):")
s = rep(s, "        if why is None and (prog in (\"pytest\", \"py.test\") or module == \"pytest\" or script in (\"pytest\", \"py.test\")):",
        "        if why is None and not beside and (prog in (\"pytest\", \"py.test\") or module == \"pytest\"\n"
        "                                           or script in (\"pytest\", \"py.test\")):")
s = rep(s, "def lock_reasons():\n    out = [f\"heavy slot {n} is held\" for n in (1, 2, 3) if lock_busy(f\"{SLOT_DIR}/gov-os-heavy-slot-{n}.lock\")]\n"
           "    out += [f\"a rebuild lock is held: {os.path.basename(p)}\" for p in sorted(glob.glob(REBUILD_GLOB)) if lock_busy(p)]",
        "def lock_reasons(beside=False):\n    out = []\n"
        "    if not beside:   # --beside-leads: the nightly waits for the slots and the rebuild lock itself (nightly.sh)\n"
        "        out += [f\"heavy slot {n} is held\" for n in (1, 2, 3) if lock_busy(f\"{SLOT_DIR}/gov-os-heavy-slot-{n}.lock\")]\n"
        "        out += [f\"a rebuild lock is held: {os.path.basename(p)}\" for p in sorted(glob.glob(REBUILD_GLOB)) if lock_busy(p)]")
s = rep(s, "def status_reasons(own_off=False):", "def status_reasons(own_off=False, beside=False):")
s = rep(s, "    if s.get(\"lead_count\"):\n", "    if s.get(\"lead_count\") and not beside:\n")
s = rep(s, "    for j in s.get(\"jobs\") or []:\n",
        "    for j in s.get(\"jobs\") or []:\n"
        "        if beside and j.get(\"kind\") in (\"lead\", \"slot\"):\n"
        "            continue\n")
s = rep(s, "                      (\"pending_launches\", \"a lead is launching\")):\n        if s.get(key):",
        "                      (\"pending_launches\", \"a lead is launching\")):\n"
        "        if beside and key in (\"outside_slot\", \"pending_launches\"):\n"
        "            continue\n"
        "        if s.get(key):")
s = rep(s, "    if s.get(\"slots_held\"):", "    if s.get(\"slots_held\") and not beside:")
s = rep(s, "    reasons = status_reasons(\"--own-off\" in argv) + process_reasons() + lock_reasons() + file_reasons() + tree_reasons()\n"
           "    if \"--no-load\" not in argv:",
        "    beside = \"--beside-leads\" in argv\n"
        "    reasons = (status_reasons(\"--own-off\" in argv, beside) + process_reasons(beside) + lock_reasons(beside)\n"
        "               + file_reasons() + tree_reasons())\n"
        "    if \"--no-load\" not in argv and not beside:")
(D / "after/quiet_check.py").write_text(s)

w = (D / "before/nightly_restart.sh").read_text()
a = """  if out=$(python3 -I "$HERE/quiet_check.py"); then quiet=$((quiet + 1)); else quiet=0; last=$(echo "$out" | head -3 | tr '\\n' ';'); fi
  if [ "$quiet" -ge "$QUIET_N" ]; then
    # the dispatcher's own off switch, then a second look (a lead may have started in the last minute)
    if (set -C; echo "$OFFTOK" > "$OFF") 2>/dev/null; then
      HAVE_OFF=1
      if python3 -I "$HERE/quiet_check.py" --no-load --own-off > /dev/null; then break; fi
      last="something started after the quiet minutes"; rm -f "$OFF"; HAVE_OFF=0; quiet=0
    else
      last="dispatch/OFF is there (not this wrapper's)"; quiet=0
    fi
  fi"""
b = """  # DEC-1159 (1) (the owner, 2026-11-13): the nightly runs beside the leads, in its own capped unit: leads are not waited
  # for (quiet_check.py --beside-leads) and no dispatch/OFF is written, so leads and landings carry on during the run
  if out=$(python3 -I "$HERE/quiet_check.py" --beside-leads); then quiet=$((quiet + 1)); else quiet=0; last=$(echo "$out" | head -3 | tr '\\n' ';'); fi
  [ "$quiet" -ge "$QUIET_N" ] && break"""
w = rep(w, a, b)
w = rep(w, 'say "quiet for $QUIET_N looks; waited $(( $(date +%s) - waited0 )) s; dispatch/OFF written"',
        'say "nothing but leads running for $QUIET_N looks (--beside-leads, DEC-1159 (1)); waited $(( $(date +%s) - waited0 )) s; no dispatch/OFF"')
w = rep(w, "#    does not ping on its own. Once quiet it writes dispatch/OFF (the CTO's own off switch: no lead starts, no landing,",
        "#    does not ping on its own. [DEC-1159 (1): leads are left out of the wait (--beside-leads) and no OFF is written;\n"
        "#    what follows describes the rule before it.] Once quiet it wrote dispatch/OFF (the CTO's own off switch: no lead starts, no landing,")
(D / "after/nightly_restart.sh").write_text(w)
print("built")
