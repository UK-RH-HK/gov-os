#!/usr/bin/env bash
# W2-37's acceptance and unit suites with the code-graph tool on PATH (CODEINTEL_OFF_PATH empty: the root conftest's
# _CBM_SUITES does not name W2-37, so its local_only code-graph cases would skip otherwise).
set -u
mkdir -p /tmp/gov-os-lead-W2-37
cd /home/usain/gov-os-worktrees/W2-37 || exit 2
out=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/log/${1:-acc-cbm}.txt
env TMPDIR=/tmp/gov-os-lead-W2-37 PYTHONUSERBASE=/home/usain/.local CODEINTEL_OFF_PATH= \
  PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-37 tests/unit/impact -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -rfEs --junitxml=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/log/${1:-acc-cbm}.xml > "$out" 2>&1
echo "rc=$?" >> "$out"
grep -E "^(FAILED|ERROR|SKIPPED)|passed|failed|^rc=" "$out" | cut -c1-250
