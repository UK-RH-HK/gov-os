#!/usr/bin/env bash
# The serial-only cases of tests/acceptance/serial-only.txt, alone and without -n, as gov close runs them
# (DEC-889 items 6 and 12), with the retention option (DEC-905). Usage: serial3.sh <junit xml path>
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
mapfile -t ENTRIES < <(sed -e 's/[[:space:]]#.*$//' -e 's/^#.*$//' -e 's/[[:space:]]*$//' tests/acceptance/serial-only.txt | grep -v '^$')
GIVEN="$(printf '%s\n' "${ENTRIES[@]}")"
echo "serial-only entries: ${#ENTRIES[@]}"
export PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
export TMPDIR=/tmp/gov-os-lead-W2-07
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src:/home/usain/gov-os-worktrees/W2-07/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-07
export GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN"
python3 -m pytest "${ENTRIES[@]}" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$1"
