#!/bin/bash
cd "/home/usain/gov-os-worktrees/W2-177" || exit 2
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-177/src PYTHONUSERBASE=/home/usain/.local
export TMPDIR=$(mktemp -d /tmp/w2-177-acc.XXXXXX) || { echo "no TMPDIR outside the repository"; exit 3; }
[ -n "$TMPDIR" ] || exit 3
python3 -c 'import signal; print("SIGINT-ignored-at-start:", int(signal.getsignal(signal.SIGINT) == signal.SIG_IGN))'
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest \
  tests/acceptance/W2-96/test_w2_96_at_run_2.py \
  tests/acceptance/W2-96/test_w2_96_at_no_leak.py \
  tests/acceptance/W2-56/test_w2_56_endings.py \
  -q -rfEs -p no:cacheprovider -o tmp_path_retention_policy=failed
code=$?
rm -rf -- "$TMPDIR"
exit $code
