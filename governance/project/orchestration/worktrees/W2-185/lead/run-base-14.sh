#!/bin/bash
B=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/tmp/base14-e2a0d6191
rm -rf "$B"; mkdir -p "$B"
git -C /home/usain/gov-os-worktrees/W2-185 archive e2a0d6191 | tar -x -C "$B"
cd "$B"
mapfile -t IDS < <(python3 - <<'PY'
import re
for l in open('/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/lead/log/verify-red-ids-997e25f1e.txt'):
    l=l.strip()
    if not l: continue
    cls,name=l.split('::',1)
    parts=cls.split('.')
    # find the module part (test_*)
    i=max(k for k,p in enumerate(parts) if p.startswith('test_'))
    path='/'.join(parts[:i+1])+'.py'
    rest=parts[i+1:]
    print('::'.join([path]+rest+[name]))
PY
)
env TMPDIR=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/tmp PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/empty-home PYTHONPATH=$B/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest --optin lifted,breadth "${IDS[@]}" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf
rc=$?
cd /; rm -rf "$B"; exit $rc
