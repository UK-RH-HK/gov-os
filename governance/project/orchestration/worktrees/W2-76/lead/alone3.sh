#!/usr/bin/env bash
# Run 3: each red not this ticket's, re-run alone after the other suites and after the fresh rebuild (DEC-757
# practice). Cases from alone3.txt, one per line. Writes log/alone3.out.
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
PLUG=$W/src/gov/close/pytest_plugin
cd "$W" || exit 2
until python3 "$W/.gov-runtime/scratch/lead/loadok.py"; do sleep 60; done
: > "$LOG/alone3.out"
while read -r case; do
  [ -n "$case" ] || continue
  echo "== $(date '+%T') $case; load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG/alone3.out"
  env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS -u GOV_REBUILD_LOCK TMPDIR=/tmp/gov-os-lead-W2-76 "PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=$W/src:$PLUG GOV_CLOSE_SERIAL_ONLY_OF=$W \
    GOV_CLOSE_SERIAL_ONLY_GIVEN="$case" python3 -m pytest "$case" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rfE --no-header >> "$LOG/alone3.out" 2>&1
  echo "exit $?" >> "$LOG/alone3.out"
done < "$W/.gov-runtime/scratch/lead/alone3.txt"
echo done > "$LOG/alone3.exit"
