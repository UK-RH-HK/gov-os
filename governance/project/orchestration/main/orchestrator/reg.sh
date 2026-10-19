#!/bin/bash
# Full regression in the main tree, in the form of gov close's own test runs (DEC-527, DEC-532):
# everything under tests/ in parallel with the cases of tests/acceptance/serial-only.txt kept out,
# then those cases alone in one serial run, then the plan validator.
# Prints one line per part; a part's full output is kept beside the summary only when it is not green.
# Usage: bash reg.sh <output directory>   (the caller redirects stdout to the summary file)
# For use only once the parallel-run follow-up of W1-30 is merged (the plugin lives in src/gov/close/pytest_plugin).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
out="$1"
root=/home/usain/Dynamic-Agentic-Engineering-OS
plugin_dir="$root/src/gov/close/pytest_plugin"
part() {
  local name="$1" tmp start
  shift
  tmp="$(mktemp)"
  start=$(date +%s)
  "$@" >"$tmp" 2>&1
  local last
  last="$(tail -1 "$tmp")"
  echo "$name: $last [$(( $(date +%s) - start )) s wall, load $(cut -d' ' -f1 /proc/loadavg)]"
  case "$last" in *failed*|*error*) cp "$tmp" "$out/$name.full.txt" ;; *passed*) ;; *) cp "$tmp" "$out/$name.full.txt" ;; esac
  rm -f "$tmp"
}
part parallel env PYTHONPATH="$root/src:$plugin_dir" GOV_CLOSE_SERIAL_ONLY_OF="$root" \
  python3 -m pytest tests -q -p no:cacheprovider --tb=line --no-header -n auto -p gov_close_serial_only
mapfile -t declared < <(PYTHONPATH="$plugin_dir" python3 -c "
import gov_close_serial_only as s
from pathlib import Path
print('\n'.join(s.entries(Path('$root'))))
")
echo "declared entries: ${#declared[@]}"
if [ "${#declared[@]}" -gt 0 ]; then
  part serial-afterwards env PYTHONPATH="$root/src" python3 -m pytest "${declared[@]}" -q -p no:cacheprovider --tb=line --no-header
fi
echo "validator: $(python3 docs/plan/tools/validate_s1.py 2>&1 | tail -1)"
echo "PARTS: read every line above; a part is green only if its line has 'passed' and no 'failed' and no 'error'"
