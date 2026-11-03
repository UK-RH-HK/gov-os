#!/bin/bash
# DEC-1033 interim, the owner's order of 2026-11-02 ~15:50: until the re-pin and ACT-QUERY-GPU-2, nothing starts the
# query embedding server (port 11435) with the GPU visible. Installed as ~/.local/bin/ollama: gov's automatic start
# (old pin and new code alike) finds `ollama` on PATH before ~/.local/ollama/bin/ollama, so every start comes here.
# `ollama serve` for 11435: on CPUs 8-11 at nice 0 (ACT-QUERY-CPUS-1), output to its log, the caller recorded; the GPU
# hidden unless the device file ($HOME/.ollama/query-server-device) reads `gpu` (ACT-QUERY-GPU-2 writes it, so a
# restart in its gap, or any later automatic start, comes back on the GPU with the same caps and log).
# Anything else: the real binary, unchanged.
REAL="${GOV_OLLAMA_WRAP_REAL:-/home/usain/.local/ollama/bin/ollama}"
LOGDIR="${GOV_OLLAMA_WRAP_LOGDIR:-$HOME/.ollama}"
if [ "${1:-}" = serve ]; then
  # A server outlives the run that started it: never keep a heavy slot's thread budget (DEC-1038; review F3)
  unset GOMAXPROCS OMP_NUM_THREADS MKL_NUM_THREADS OPENBLAS_NUM_THREADS RAYON_NUM_THREADS NUMEXPR_NUM_THREADS \
        NUMEXPR_MAX_THREADS VECLIB_MAXIMUM_THREADS GOV_HEAVY_THREAD_BUDGET
  case "${OLLAMA_HOST:-}" in
    *:11435|*:11435/)
      device=cpu
      [ "$(head -c 3 "$LOGDIR/query-server-device" 2>/dev/null)" = gpu ] && device=gpu
      if [ "$device" = cpu ]; then export CUDA_VISIBLE_DEVICES=-1; else unset CUDA_VISIBLE_DEVICES; fi
      caller=$(tr '\0' ' ' < "/proc/$PPID/cmdline" 2>/dev/null | cut -c1-300)
      printf '%s query server started (%s) by the wrapper; caller pid %s cwd %s: %s\n' "$(date -Is)" "$device" "$PPID" \
        "$(readlink "/proc/$PPID/cwd" 2>/dev/null)" "$caller" >> "$LOGDIR/query-autostart.log"
      exec taskset -c 8-11 "$REAL" "$@" >> "$LOGDIR/serve-11435.log" 2>&1
      ;;
  esac
fi
exec "$REAL" "$@"
