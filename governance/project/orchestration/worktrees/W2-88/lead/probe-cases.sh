#!/usr/bin/env bash
# the four cases that read this repository's probe records (round 2's reds), through the heavy slot
mkdir -p /tmp/gov-os-lead-W2-88 /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home
cd /home/usain/gov-os-worktrees/W2-88 || exit 2
env HOME=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/empty-home TMPDIR=/tmp/gov-os-lead-W2-88 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W1-08 tests/acceptance/W1-26 tests/acceptance/W2-02 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -k "probe_schema_accepts_this_repository or probe_records_are_well_formed or names_a_probe_record or core_schema_is_green_on_this_repository" \
  > /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/probe-cases.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/probe-cases.exit
