#!/usr/bin/env bash
# The memory audit's cron wrapper (W2-172, W2-187 I11; DEC-1125 (2), DEC-1179 (5)): runs what is due, in this order.
# Usage: memaudit_cron.sh [--repo <dir>]  (default: the top level of the current directory; the wrapper goes there).
# Weekly, Monday 21:00 is the schedule's line (an ACT installs it, never this file); `due` decides weekly or monthly, so
# that line never changes. Writes only <key folder>/cron.log and what the steps it starts write.
#
# With a live standing set (`standing live` exits 0): `due` and `due --fresh`; then, when either is due, `maintain`; then
# `standing run` when `due`; `maintain` once more when that run's last line ends `misses`; then `run` when `due --fresh`.
# Any other answer of `standing live` is today's path, unchanged: `due`, then `run`.
# Last, when a step started that cycle (on today's path too), `push`: with GOV_MEMAUDIT_PUSH declared, the weekly scan, then
# the push on a clean scan, and `push` itself writes one more cron.log line (the step `push`) and the digest's last line;
# undeclared, it prints `PUSH none: no declaration` (this wrapper's stdout) and writes nothing. The exit stays the audit
# steps' own.
set -u
PY="${GOV_MEMAUDIT_PYTHON:-/usr/bin/python3}"
ROOT="${GOV_MEMAUDIT_SETS_ROOT:-$HOME/gov-os-eval}"
RUNS="${GOV_INDEP_RUNS_DIR:-$HOME/gov-os-runs}"
GATE="${GOV_MEMAUDIT_GATE:-$HOME/.local/bin/gov resources --check}"

REPO=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        --repo) REPO="${2:-}"; shift 2 || shift ;;
        --repo=*) REPO="${1#--repo=}"; shift ;;
        *) shift ;;
    esac
done
[ -n "$REPO" ] || REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO" || exit 4

LIVE="$("$PY" -m gov.memaudit standing live --sets-root "$ROOT" --repo "$REPO" 2>/dev/null)"
LIVE_RC=$?
KEY="$(printf '%s\n' "$LIVE" | sed -n 's/^KEY //p' | head -n 1)"
if [ -n "$KEY" ]; then
    LOG="$RUNS/indep/memaudit/$KEY/cron.log"
else
    LOG="$RUNS/indep/memaudit/cron.log"
fi

mkdir -p "$(dirname "$LOG")"
AT="${GOV_MEMAUDIT_NOW:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"

log() { # <due true|false> <started true|false> <exit>
    printf '{"at": "%s", "due": %s, "mode": "%s", "reason": "%s", "started": %s, "exit": %s}\n' \
        "$AT" "$1" "${MODE:-}" "${REASON:-}" "$2" "$3" >> "$LOG"
}

push_step() { # the weekly scan and push (W2-187 I13): the last step; it writes its own cron.log line and digest line
    # `push` says `PUSH none: no declaration` (nothing written) when the cron line declares no push, and that line, like
    # every other, reaches this wrapper's stdout; the exit stays the audit steps' own
    GOV_MEMAUDIT_CRON_LOG="$LOG" "$PY" -m gov.memaudit push --sets-root "$ROOT" --repo "$REPO"
}

OUT="$("$PY" -m gov.memaudit due --sets-root "$ROOT" 2>/dev/null)"
RC=$?
MODE="$(printf '%s\n' "$OUT" | sed -n 's/^MODE //p')"
REASON="$(printf '%s\n' "$OUT" | sed -n 's/^REASON //p')"

if [ "$LIVE_RC" -eq 0 ]; then # a live standing set: the standing run and the fresh set, each when due
    FOUT="$("$PY" -m gov.memaudit due --fresh --sets-root "$ROOT" 2>/dev/null)"
    FRC=$?
    if [ "$RC" -gt 1 ] || [ "$FRC" -gt 1 ]; then # `due` itself failed: say so in the log and stop
        [ "$RC" -gt 1 ] && CODE="$RC" || CODE="$FRC"
        log false false "$CODE"
        exit "$CODE"
    fi
    if [ "$RC" -eq 1 ] && [ "$FRC" -eq 1 ]; then # neither is due: nothing starts
        log false false 0
        exit 0
    fi
    "$PY" -m gov.memaudit maintain --sets-root "$ROOT" || true # never a gate: the audit goes on whatever it finds
    CODE=0
    if [ "$RC" -eq 0 ]; then
        SOUT="$("$PY" -m gov.memaudit standing run --sets-root "$ROOT" --gate-cmd "$GATE")"
        CODE=$?
        printf '%s\n' "$SOUT"
        case "$(printf '%s\n' "$SOUT" | tail -n 1)" in
            *misses) "$PY" -m gov.memaudit maintain --sets-root "$ROOT" || true ;; # at once after a miss, same cycle
        esac
    fi
    if [ "$FRC" -eq 0 ]; then
        "$PY" -m gov.memaudit run --sets-root "$ROOT" --gate-cmd "$GATE"
        CODE=$?
    fi
    log true true "$CODE"
    push_step # a standing or fresh step started this cycle: the weekly scan, then the push on a clean scan
    exit "$CODE"
fi

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
push_step # today's path too, declared or not: an undeclared push only says so
exit "$RC"
