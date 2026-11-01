#!/bin/bash
# Lead's run-2 verification (DEC-954): a scoped run of the corrected tests, in the close's form (one parallel run,
# the serial-only plugin, retention failed, JUnit XML). No lock: a scoped run takes none (DEC-952 item 5).
L=/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
W=/home/usain/gov-os-worktrees/W2-64
until [ ! -e "$F/NIGHTLY-RUNNING" ] && [ ! -e "$F/CLOSE-RUNNING" ]; do sleep 60; done
bash "$F/tools/disk_gate.sh" > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/disk-gate-scoped.txt 2>&1 || { echo 99 > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/scoped.exit; exit 99; }
cd "$W" || exit 98
mkdir -p /tmp/gov-os-lead-W2-64
python3 /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/scoped_files.py > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/scoped-files.txt
mapfile -t FILES < <(grep -v '^#' "$L/scoped-files.txt")
cat /proc/loadavg > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/scoped.load
date > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/scoped.start
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=/tmp/gov-os-lead-W2-64 PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=$W python3 -m pytest "${FILES[@]}" -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/scoped.xml > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/scoped.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/scoped.exit
date > /home/usain/gov-os-worktrees/W2-64/.gov-runtime/scratch/lead/log/scoped.end
