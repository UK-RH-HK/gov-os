#!/usr/bin/env bash
# Run 2's verification in the close's form, under the lock, with the retention option. One part per call:
#   parallel  the full parallel run (every listed entry deselected by the close's plugin)
#   serial    the entries the list keeps in the close (route serial), alone, as gov close's run afterwards
#   nightly   the entries the list routes to the nightly, alone (evidence that they still run; not the close)
cd /home/usain/gov-os-worktrees/W2-57 || exit 1
V=/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/log/verify2
part="$1"
export TMPDIR=/tmp/gov-os-lead-W2-57
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src:/home/usain/gov-os-worktrees/W2-57/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-57
echo "$part start $(date '+%F %T') load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$V/times.txt"
case "$part" in
  parallel)
    flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
      -o tmp_path_retention_policy=failed -rs --tb=line --junitxml="$V/parallel.xml" > "$V/parallel.txt" 2>&1
    rc=$? ;;
  serial|nightly)
    mapfile -t E < "$V/$part-entries.txt"
    export GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat "$V/$part-entries.txt")"
    flock /tmp/gov-os-verify.lock python3 -m pytest "${E[@]}" -q -p no:cacheprovider -p gov_close_serial_only \
      -o tmp_path_retention_policy=failed -rs --tb=line --junitxml="$V/$part.xml" > "$V/$part.txt" 2>&1
    rc=$? ;;
  *) echo "unknown part $part"; exit 2 ;;
esac
echo "$part exit $rc end $(date '+%F %T') load $(cut -d' ' -f1-3 /proc/loadavg) | $(tail -1 "$V/$part.txt")" >> "$V/times.txt"
echo $rc > "$V/$part.exit"
