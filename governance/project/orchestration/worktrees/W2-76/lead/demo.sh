#!/usr/bin/env bash
# Run 2: one of run 1's lock-made reds, run while hold.sh (tag demo-hold) holds the machine's rebuild lock, with this
# worktree's code and the root conftest's GOV_REBUILD_LOCK: does the override reach its rebuild?
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
cd "$W" || exit 2
until [ -s "$LOG/demo-hold.times" ]; do sleep 5; done
{ date '+start %F %T'; grep -F ":$(stat -c %i /tmp/gov-os-rebuild.lock) " /proc/locks; } > "$LOG/demo.times"
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src \
  python3 -m pytest "tests/acceptance/W1-07/test_w1_07_config.py::test_a_missing_path_map_is_not_an_error[rebuild]" \
  "tests/acceptance/W1-27/test_w1_27_recovery_check_r2.py::test_recovery_rebuild_command_not_unconditionally_exit_zero" \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE > "$LOG/demo.out" 2>&1
echo "exit $? $(tail -1 "$LOG/demo.out")" >> "$LOG/demo.times"
{ date '+end %F %T'; grep -F ":$(stat -c %i /tmp/gov-os-rebuild.lock) " /proc/locks; } >> "$LOG/demo.times"
echo done > "$LOG/demo.exit"
