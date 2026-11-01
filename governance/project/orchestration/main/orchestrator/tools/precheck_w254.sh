#!/usr/bin/env bash
# Before the batch re-run (RESUME HERE item 2): W2-54's green-here and time-limit cases, alone, on a rebuilt clean
# clone of CLOSE-HEAD (the corrected register, 6fd19a5f re-mark). Prints PASS/FAIL per case.
set -u
ROOT=/home/usain/Dynamic-Agentic-Engineering-OS
HEAD=$(cat "$ROOT/.gov-runtime/scratch/orchestrator/CLOSE-HEAD")
DIR=/home/usain/gov-os-runs/W2-00/precheck-w254-$(date +%Y%m%d-%H%M)
mkdir -p "$DIR"
export TMPDIR=/tmp/gov-os-precheck-w254
mkdir -p "$TMPDIR"
git clone -q --no-hardlinks "$ROOT" "$DIR/repo" && git -C "$DIR/repo" checkout -q "$HEAD" || exit 4
cd "$DIR/repo" || exit 4
echo "$(date '+%T') clone at $(git rev-parse --short=12 HEAD); rebuild"
t0=$(date +%s)
PYTHONPATH="$DIR/repo/src" flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$DIR/rebuild.out" 2> "$DIR/rebuild.err"
echo "$(date '+%T') rebuild rc=$? in $(( $(date +%s) - t0 )) s"
PYTHONPATH="$DIR/repo/src" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --timeout=900 \
  "tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here" \
  "tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit" \
  > "$DIR/pytest.out" 2>&1
rc=$?
tail -15 "$DIR/pytest.out"
echo "$(date '+%T') pytest rc=$rc dir=$DIR"
