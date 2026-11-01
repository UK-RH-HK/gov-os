#!/usr/bin/env bash
# W2-54's live-session case, once, outside the sandbox (nightly-routed; the designer cannot launch it).
cd /home/usain/gov-os-worktrees/W2-90b || exit 9
TMPDIR=/tmp/gov-os-lead-W2-90b PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-90b/src python3 -m pytest "tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py::test_inside_a_launched_sandboxed_worker_one_text_gets_one_answer_where_the_cache_cannot_be_written" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/live-w2-54.xml > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/live-w2-54.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/live-w2-54.exit
