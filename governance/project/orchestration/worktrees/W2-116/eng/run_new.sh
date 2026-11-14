#!/bin/bash
cd /home/usain/gov-os-worktrees/W2-116 || exit 2
bash .gov-runtime/scratch/eng/pt.sh tests/unit/rebuild/test_w2_116_when_due.py \
  tests/unit/status/test_w2_116_integration_store.py tests/unit/retrieval/test_w2_116_token_mark.py \
  > .gov-runtime/scratch/eng/out-new.txt 2>&1
echo "exit=$?" >> .gov-runtime/scratch/eng/out-new.txt
