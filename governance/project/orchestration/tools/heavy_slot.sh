#!/usr/bin/env bash
# The heavy-job slot, as a thin wrapper over the product (W2-199, the run-time tool, slice 2; was the scratch script of
# the same name with heavy_slots.conf). The product does the work: it holds the run until the machine has room (the load
# under start_below), takes one slot of its set, confines the run to the slot's CPUs, sizes its workers and thread
# budget, and logs the run in ~/.gov-os/runtime/log.jsonl.
#   bash heavy_slot.sh <the run's command and arguments>
#   bash heavy_slot.sh --held <slot numbers, comma-separated> <command>   (a caller that holds slots itself: no lock)
# Exits with the command's code (0 included); a run that cannot start ends with the product's own code (never 213).
# The sizes are derived from the machine (gov dispatch limits) and read no heavy_slots.conf. The environment the product
# reads, unchanged from the script's: GOV_HEAVY_SLOTS (the slot count), GOV_HEAVY_WORKERS (workers per slot),
# GOV_HEAVY_START_BELOW (an absolute start load), GOV_HEAVY_PRIORITY and GOV_HEAVY_PRIO_CAP (the merge queue and the
# closes are served first and hold at most the cap). A caller's own PYTEST_XDIST_AUTO_NUM_WORKERS (the nightly's serial
# phase sets 1) becomes --workers. The command sees PYTEST_XDIST_AUTO_NUM_WORKERS, GOV_HEAVY_SLOT, GOV_HEAVY_CPUS and
# GOV_HEAVY_ADMITTED=1 (a run it starts is nested: never held, no slot).
# heavy-slot: --held   (this line tells a caller the form is supported)
held=() workers=()
if [ "${1:-}" = --held ]; then held=(--held "${2-}"); shift 2 2>/dev/null || shift; fi
case "${PYTEST_XDIST_AUTO_NUM_WORKERS:-}" in ""|*[!0-9]*|0) ;; *) workers=(--workers "$PYTEST_XDIST_AUTO_NUM_WORKERS") ;; esac
# `python3 -m gov.cli.main` where PYTHONPATH names a source tree (a worktree's src), else the installed `gov`.
gov=(gov)
IFS=: read -ra trees <<< "${PYTHONPATH:-}"
for tree in "${trees[@]}"; do
  [ -f "$tree/gov/cli/main.py" ] && { gov=(python3 -m gov.cli.main); break; }
done
exec "${gov[@]}" resources --slot test "${held[@]}" "${workers[@]}" -- "$@"
