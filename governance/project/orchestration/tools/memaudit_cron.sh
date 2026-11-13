#!/usr/bin/env bash
# The memory audit's cron wrapper (W2-172, DEC-1125 (2)): runs `due`, and starts the cycle only when an audit is due.
# Run from the repository (cwd). Weekly, Monday 21:00 is the schedule's line (an ACT installs it, never this file); `due`
# decides weekly or monthly, so that line never changes. Writes only <runs>/indep/memaudit/cron.log and what `run` writes.
set -u
PY="${GOV_MEMAUDIT_PYTHON:-/usr/bin/python3}"
ROOT="${GOV_MEMAUDIT_SETS_ROOT:-$HOME/gov-os-eval}"
RUNS="${GOV_INDEP_RUNS_DIR:-$HOME/gov-os-runs}"
LOG="$RUNS/indep/memaudit/cron.log"
GATE="${GOV_MEMAUDIT_GATE:-$HOME/.local/bin/gov resources --check}"

mkdir -p "$(dirname "$LOG")"
AT="${GOV_MEMAUDIT_NOW:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"

log() { # <due true|false> <started true|false> <exit>
    printf '{"at": "%s", "due": %s, "mode": "%s", "reason": "%s", "started": %s, "exit": %s}\n' \
        "$AT" "$1" "${MODE:-}" "${REASON:-}" "$2" "$3" >> "$LOG"
}

OUT="$("$PY" -m gov.memaudit due --sets-root "$ROOT" 2>/dev/null)"
RC=$?
MODE="$(printf '%s\n' "$OUT" | sed -n 's/^MODE //p')"
REASON="$(printf '%s\n' "$OUT" | sed -n 's/^REASON //p')"

if [ "$RC" -eq 1 ]; then # not due: nothing starts
    log false false 0
    exit 0
fi
if [ "$RC" -ne 0 ]; then # `due` itself failed: say so in the log and stop
    log false false "$RC"
    exit "$RC"
fi

"$PY" -m gov.memaudit run --sets-root "$ROOT" --gate-cmd "$GATE"
RC=$?
log true true "$RC"
exit "$RC"
