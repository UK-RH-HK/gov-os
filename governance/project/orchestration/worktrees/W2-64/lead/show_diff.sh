#!/bin/sh
# Read-only: the diff of W1-30's close test since the run-2 merge (lead's scratch).
cd /home/usain/gov-os-worktrees/W2-64 || exit 1
git diff 24d70ca7 HEAD -- tests/acceptance/W1-30/test_w1_30_close.py
