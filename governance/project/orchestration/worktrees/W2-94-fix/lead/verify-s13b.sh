#!/usr/bin/env bash
# rebuild, gov accept, then the scoped lead_verify, for the S13 path-case revision (900035fdd) (W2-94-fix)
L=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/log
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
cd /home/usain/gov-os-worktrees/W2-94-fix || exit 2
env PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash $T/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-94-fix > $L/rebuild-s13b.txt 2>&1
echo "rebuild rc=$?" >> $L/rebuild-s13b.txt
gov accept W2-94 --root /home/usain/gov-os-worktrees/W2-94-fix > $L/accept-s13b.txt 2>&1
echo "accept rc=$?" >> $L/accept-s13b.txt
bash $T/lead_verify.sh /home/usain/gov-os-worktrees/W2-94-fix W2-94 DAEO-g87r > $L/lead-verify-s13b.txt 2>&1
echo "lead_verify rc=$?" >> $L/lead-verify-s13b.txt
