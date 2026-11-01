#!/bin/bash
# Run 4 of the lead (DEC-987): rebuild (one at a time, DEC-939), gov check, select_tests, keyword_warn, scratch measure,
# then the scoped run in the close's form through verify_lock.sh (heavy-job slot, DEC-979 D1, DEC-984).
cd /home/usain/gov-os-worktrees/W2-96 || exit 9
L=/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/log
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$L/disk-gate5a.txt" 2>&1 || { echo 8 > "$L/rebuild-5.exit"; exit 8; }
date -u +%FT%TZ > "$L/rebuild-5.start"
TMPDIR=/tmp/gov-os-lead-W2-96 PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$L/rebuild-5.json" 2>&1
echo $? > "$L/rebuild-5.exit"
date -u +%FT%TZ >> "$L/rebuild-5.start"
TMPDIR=/tmp/gov-os-lead-W2-96 PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)" > "$L/govfile5b.txt" 2>&1
TMPDIR=/tmp/gov-os-lead-W2-96 PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m gov.cli.main check --json > "$L/check5.json" 2>&1
echo $? > "$L/check5.exit"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py /home/usain/gov-os-worktrees/W2-96 W2-96 DAEO-ouet > "$L/select5.json" 2> "$L/select5.err"
echo $? > "$L/select5.exit"
python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/keyword_warn.py /home/usain/gov-os-worktrees/W2-96 > "$L/keyword5.out" 2>&1
du -sh /tmp/gov-os-lead-W2-96 /home/usain/gov-os-worktrees/W2-96/.gov-runtime > "$L/scratch5-before.txt" 2>&1
du -s --inodes /tmp/gov-os-lead-W2-96 /home/usain/gov-os-worktrees/W2-96/.gov-runtime >> "$L/scratch5-before.txt" 2>&1
if [ "$(cat "$L/select5.exit")" != "0" ]; then echo select-failed > "$L/verify5.done"; exit 7; fi
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$L/disk-gate5b.txt" 2>&1 || { echo disk-shut > "$L/verify5.done"; exit 8; }
date -u +%FT%TZ > "$L/verify5.start"
python3 /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/verify5.py both
date -u +%FT%TZ >> "$L/verify5.start"
echo done > "$L/verify5.done"
