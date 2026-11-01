#!/bin/bash
# Run 7: reproduce W2-50's red: run the secrets check in the kept project, once plainly and once in the pinned
# program environment a declared check gets (GIT_* cleared, system and global configuration unread).
P=/tmp/gov-os-lead-W2-05/pytest-of-usain/pytest-25/test_a_large_store_among_many_0/w2-50/home/gov-os-worktrees/W2-90
cd "$P" || exit 9
echo "== plain"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src timeout 600 python3 -m gov.secrets > /tmp/gov-os-lead-W2-05/v7-results/secrets-plain.out 2>&1
echo "exit $?"
tail -30 /tmp/gov-os-lead-W2-05/v7-results/secrets-plain.out | cut -c1-300
echo "== gov check (this worktree's code), secrets entry only"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src timeout 900 python3 -m gov.cli.main check --json > /tmp/gov-os-lead-W2-05/v7-results/secrets-check.json 2> /tmp/gov-os-lead-W2-05/v7-results/secrets-check.err
echo "exit $?"
python3 /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/secrets_stderr.py /tmp/gov-os-lead-W2-05/v7-results/secrets-check.json
