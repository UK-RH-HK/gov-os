#!/usr/bin/env bash
# Run 2, verification step 2: run 1's lock-made reds (W1-07, W1-27, W1-41, W2-69's rebuild cases) run while
# hold.sh's real rebuild holds /tmp/gov-os-rebuild.lock, in the close's form: the parallel part with the serial-only
# plugin, then these suites' serial-only cases alone.
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
PLUG=$W/src/gov/close/pytest_plugin
cd "$W" || exit 2
until [ -s "$LOG/hold.times" ]; do sleep 5; done
du -s --inodes "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 > "$LOG/held.scratch-before" 2>&1
du -sh "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 >> "$LOG/held.scratch-before" 2>&1
{ date '+parallel start %F %T'; grep -F ":$(stat -c %i /tmp/gov-os-rebuild.lock) " /proc/locks; } > "$LOG/held.times"
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src:$PLUG GOV_CLOSE_SERIAL_ONLY_OF=$W \
  python3 -m pytest tests/acceptance/W1-07 tests/acceptance/W1-27 tests/acceptance/W1-41 tests/acceptance/W2-69 -n 8 -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
  --junitxml="$LOG/held-parallel.xml" > "$LOG/held-parallel.out" 2>&1
echo "parallel exit $? $(tail -1 "$LOG/held-parallel.out")" >> "$LOG/held.times"
{ date '+serial start %F %T'; grep -F ":$(stat -c %i /tmp/gov-os-rebuild.lock) " /proc/locks; } >> "$LOG/held.times"
S1=tests/acceptance/W1-07/test_w1_07_help.py::test_help_answers_in_under_300_ms
S2=tests/acceptance/W2-69/test_w2_69_deleted_text_after_rebuild.py::test_the_code_graph_store_holds_no_deleted_word_and_no_free_page_after_a_rebuild
S3=tests/acceptance/W2-69/test_w2_69_review_rebuild_root_and_held_store.py::test_a_rebuild_given_the_project_relatively_returns_its_result_and_compacts_every_store
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src:$PLUG GOV_CLOSE_SERIAL_ONLY_OF=$W \
  GOV_CLOSE_SERIAL_ONLY_GIVEN="$S1
$S2
$S3" python3 -m pytest "$S1" "$S2" "$S3" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
  --junitxml="$LOG/held-serial.xml" > "$LOG/held-serial.out" 2>&1
echo "serial exit $? $(tail -1 "$LOG/held-serial.out")" >> "$LOG/held.times"
{ date '+end %F %T'; grep -F ":$(stat -c %i /tmp/gov-os-rebuild.lock) " /proc/locks; } >> "$LOG/held.times"
du -s --inodes "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 > "$LOG/held.scratch-after" 2>&1
du -sh "$W/.gov-runtime" /tmp/gov-os-lead-W2-76 >> "$LOG/held.scratch-after" 2>&1
echo done > "$LOG/held-suites.exit"
