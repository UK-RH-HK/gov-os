#!/usr/bin/env bash
# a stand-in for nightly_cron.sh: records what the wrapper gave it
cg=/sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup)
{ echo "ran"; echo "workers=$PYTEST_XDIST_AUTO_NUM_WORKERS"; echo "memmax=$(cat $cg/memory.max 2>&1)"; echo "swapmax=$(cat $cg/memory.swap.max 2>&1)";
  echo "oomgroup=$(cat $cg/memory.oom.group 2>&1)"; echo "oomadj=$(cat /proc/self/oom_score_adj)"; echo "off=$([ -e "$NR_ORCH/dispatch/OFF" ] && echo yes || echo no)"; } > "$NR_MARK"
exit 0
