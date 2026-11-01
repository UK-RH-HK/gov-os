#!/usr/bin/env bash
# The lead's verification after the rebuild: collect-only (DEC-868), the scoped run (suite.py), then gov check.
cd /home/usain/gov-os-worktrees/W2-108 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log
until [ -s "$LOG/rebuild-verify2.exit" ]; do sleep 20; done
[ "$(cat "$LOG/rebuild-verify2.exit")" = "0" ] || { echo rebuild-failed > "$LOG/verify.state"; exit 7; }
PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src python3 -c "import gov; print(gov.__file__)" > "$LOG/verify-gov-file.txt" 2>&1
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/verify-disk.txt" 2>&1 || { echo disk-shut > "$LOG/verify.state"; exit 8; }
du -s --inodes /tmp/gov-os-lead-W2-108 > "$LOG/verify-scratch-before.txt" 2>&1
du -sh /tmp/gov-os-lead-W2-108 >> "$LOG/verify-scratch-before.txt" 2>&1
echo collect > "$LOG/verify.state"
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src TMPDIR=/tmp/gov-os-lead-W2-108 python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$LOG/verify-collect.txt" 2>&1
echo $? > "$LOG/verify-collect.exit"
echo suites > "$LOG/verify.state"
TMPDIR=/tmp/gov-os-lead-W2-108 python3 /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/suite.py "$LOG/select-4.json" v2
echo check > "$LOG/verify.state"
TMPDIR=/tmp/gov-os-lead-W2-108 PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src python3 -m gov.cli.main check --json > "$LOG/verify-check.json" 2>&1
echo $? > "$LOG/verify-check.exit"
du -s --inodes /tmp/gov-os-lead-W2-108 > "$LOG/verify-scratch-after.txt" 2>&1
du -sh /tmp/gov-os-lead-W2-108 >> "$LOG/verify-scratch-after.txt" 2>&1
echo done > "$LOG/verify.state"
