#!/bin/bash
# Run 6: the reds not of W2-05's own suite, run on the integration branch's tree (W2-00-store, read only:
# no bytecode, no cache, temp folders in this lead's TMPDIR), to tell which this branch caused.
OUT=/tmp/gov-os-lead-W2-05/v6-results
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/v6
T=/home/usain/gov-os-worktrees/W2-00-store
cd "$T" || exit 9
git -C "$T" rev-parse --short=12 HEAD > "$LOG/integrate.head"
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/gov-os-lead-W2-05 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
PYTHONPATH=$T/src \
  env -u GIT_DIR -u GIT_INDEX_FILE \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfEs \
  "tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through[npm-install]" \
  "tests/acceptance/W2-59/test_w2_59_hook_lines.py::test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src[preToolUse[0]]" \
  "tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py" \
  "tests/acceptance/W2-72/test_w2_72_merge_tree_that_cannot_run.py" > "$OUT/integrate.txt" 2>&1
echo $? > "$LOG/integrate.exit"
