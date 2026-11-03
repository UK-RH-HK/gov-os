#!/bin/bash
# The lead's run of the W2-112 acceptance tests outside the sandbox, then gov accept, each through the gate (DEC-1038 (4)).
cd /home/usain/gov-os-worktrees/W2-112 || exit 99
export TMPDIR=/tmp/gov-os-lead-W2-112
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src
L=/home/usain/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead/log
python3 -c "import gov; print(gov.__file__)" > $L/acc-2.log 2>&1
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-112 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs >> $L/acc-2.log 2>&1
echo $? > $L/acc-2.exit
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m gov.cli.main accept DAEO-clon --json > $L/accept-2.json 2> $L/accept-2.err
echo $? > $L/accept-2.exit
