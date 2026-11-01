#!/bin/bash
# The head's measure alone (its store is rebuilt: log/head-rebuild.*), visible half only, compared with the control.
export TMPDIR=/tmp/gov-os-lead-W2-91
cd /home/usain/gov-os-runs/W2-91/head || exit 90
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/head-measure.start
env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-91/base/src python3 -m gov.retrieval.measure memory-retrieval --root /home/usain/gov-os-runs/W2-91/head --sets-root /home/usain/gov-os-runs/W2-91/base --part visible --gov /home/usain/.local/bin/gov --out /home/usain/gov-os-runs/W2-91/records --json --compare /home/usain/gov-os-runs/W2-91/records/measure-memory-retrieval-visible-20261101T173426352951Z.json > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/head-measure.json 2> /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/head-measure.err
echo $? > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/head-measure.exit
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/head-measure.end
