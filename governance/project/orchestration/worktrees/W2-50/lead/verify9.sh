#!/bin/bash
# W2-50 run 9 verification at the merged head. Usage: verify9.sh <stage>
#   a: W2-50 acceptance, tests/unit/guard, tests/unit/launch, each its own process; then gov check
#   p: the close's parallel run of tests/ (DEC-889 items 6 and 12)
#   s: the serial-only cases alone; then the collection as the close runs it (DEC-868)
# Each step writes <name>.txt, <name>.exit (and .xml) under log/v9/. A step with an .exit file is skipped (resume).
W=/home/usain/gov-os-worktrees/W2-50
OUT=$W/.gov-runtime/scratch/lead/log/v9
mkdir -p $OUT
cd $W || exit 9
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
gates() {
  until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
  until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
  echo "$1 $(date -Is) $(cat /proc/loadavg)" >> $OUT/starts.txt
}
step() {  # step <name> <command...>
  local n=$1; shift
  [ -e $OUT/$n.exit ] && return
  gates $n
  "$@" > $OUT/$n.txt 2>&1
  echo $? > $OUT/$n.exit
  echo "$n end $(date -Is)" >> $OUT/starts.txt
}
case $1 in
a)
  step w2-50 env PYTHONPATH=$W/src python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs --junitxml=$OUT/w2-50.xml
  step unit-guard env PYTHONPATH=$W/src python3 -m pytest tests/unit/guard -q -p no:cacheprovider -rs --junitxml=$OUT/unit-guard.xml
  step unit-launch env PYTHONPATH=$W/src python3 -m pytest tests/unit/launch -q -p no:cacheprovider -rs --junitxml=$OUT/unit-launch.xml
  step check env PYTHONPATH=$W/src python3 -m gov.cli.main check --json
  ;;
p)
  step parallel env PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=$W python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -rs --junitxml=$OUT/parallel.xml
  ;;
s)
  ENTRIES=$(grep -v '^[[:space:]]*#' tests/acceptance/serial-only.txt | sed 's/[[:space:]]#.*$//; s/[[:space:]]*$//' | grep -v '^$')
  printf '%s\n' "$ENTRIES" > $OUT/serial-entries.txt
  mapfile -t ARGS < $OUT/serial-entries.txt
  step serial env PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=$W GOV_CLOSE_SERIAL_ONLY_GIVEN="$ENTRIES" python3 -m pytest "${ARGS[@]}" -q -p no:cacheprovider -p gov_close_serial_only -rs --junitxml=$OUT/serial.xml
  step collect env PYTHONPATH=$W/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header
  ;;
esac
echo "stage $1 done $(date -Is)" >> $OUT/starts.txt
touch $OUT/stage-$1.done
