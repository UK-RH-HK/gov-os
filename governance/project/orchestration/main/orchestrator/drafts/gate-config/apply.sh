#!/usr/bin/env bash
# DEC-1103 (1), ACT-GATE-CONFIG-1: W2-20's machine gate file, ~/.gov-os/machine/gate.json, written by
# `gov resources --init-config` from W2-20's own code (branch w2/W2-20, head b0acd966b, its worktree), so W2-20's gate
# reads this machine's limits and admits launches instead of refusing every one on the missing file.
#   bash apply.sh check   W2-20's code as built, the interpreter, the file's state (absent | applied | other) and the
#                         bytes init would write (their sha256); changes nothing
#   bash apply.sh apply   runs `gov resources --init-config` (W2-20's code), checks the written file's sha256 against
#                         the bytes expected, records it; then W2-20's gate admits a session and refuses an over-limit
#                         one (a GPU need above the card). A file already there is backed up and never overwritten
#                         (P-3): apply stops
#   bash apply.sh undo    removes the file apply wrote if it still hashes as written (else moves it aside to the
#                         backup), and the side files apply's own gate reading made where there were none
# HOME decides where the file goes (the rehearsal gives a throwaway HOME). Backups and records go to $GATE_BACKUP,
# default backup/ beside this file. It commits nothing and touches nothing in any repository.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
W=${GATE_W2_20:-/home/usain/gov-os-worktrees/W2-20}
W_HEAD=b0acd966b                       # W2-20's head as reviewed (round 1 settled, integrate merged)
CONFIG_SHA=79d3c3450bc9b449aa86dd77d92f0a9fd9eced703fdcc833fd7b2586e5c78328  # src/gov/resources/config.py at that head
REAL_HOME=/home/usain
REAL_SHA=de4fb326288d80d9d627ad910542ae5d86834c98a3d8895c0e16b9ece2fcd457    # the file for HOME=/home/usain, CPUs 0-19
BACKUP=${GATE_BACKUP:-$HERE/backup}
MACHINE=$HOME/.gov-os/machine
F=$MACHINE/gate.json
die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }

# The interpreter: the pin's (the shebang of ~/.local/bin/gov, as the hooks read it), else python3. W2-20's src goes
# first on PYTHONPATH, so its code runs whatever the pin holds (checked below by the module's file).
PY=
if [ -f "$HOME/.local/bin/gov" ]; then read -r PY < "$HOME/.local/bin/gov"; PY=${PY#'#!'}; fi
[ -z "$PY" ] && [ -f "$REAL_HOME/.local/bin/gov" ] && { read -r PY < "$REAL_HOME/.local/bin/gov"; PY=${PY#'#!'}; }
[ -n "$PY" ] && [ -x "$PY" ] || PY=$(command -v python3)
w2() { (cd "$W" && env -u GOV_TICKET PYTHONPATH="$W/src" PYTHONDONTWRITEBYTECODE=1 "$PY" "$@"); }
gov() { w2 -m gov.cli.main "$@"; }

built() {  # W2-20's code is the reviewed head's, and the interpreter runs it
  [ -d "$W/src/gov/resources" ] || die "$W has no src/gov/resources (W2-20's worktree)"
  local head; head=$(git -C "$W" rev-parse HEAD)
  case "$head" in "$W_HEAD"*) ;; *) die "W2-20's worktree is at $head, not $W_HEAD (ask the CTO)";; esac
  [ "$(sha "$W/src/gov/resources/config.py")" = "$CONFIG_SHA" ] || die "W2-20's config.py differs from the built one"
  local mod; mod=$(w2 -c 'import gov.resources.config as c; print(c.__file__)') || die "$PY cannot import W2-20's code"
  [ "$mod" = "$W/src/gov/resources/config.py" ] || die "$PY imports $mod, not W2-20's"
  echo "W2-20: $W at ${head:0:12}; config.py $CONFIG_SHA; interpreter $PY ($("$PY" --version 2>&1))"
}
expected() {  # the sha256 of the bytes init would write here, from W2-20's template (nothing written)
  local e; e=$(w2 "$HERE/expected.py" --home "$HOME") || die "expected.py failed"
  if [ "$HOME" = "$REAL_HOME" ] && [ "$e" != "$REAL_SHA" ]; then
    die "init would write $e here, not the reviewed $REAL_SHA (another CPU set? run it outside any taskset or slot)"
  fi
  echo "$e"
}
state() {  # absent | applied | other
  if [ ! -e "$F" ] && [ ! -L "$F" ]; then echo absent
  elif [ -f "$F" ] && [ ! -L "$F" ] && [ "$(sha "$F")" = "$1" ]; then echo applied
  else echo other; fi
}

cmd=${1:-}
echo "apply.sh $cmd: HOME $HOME; file $F"
case "$cmd" in
  check)
    built; e=$(expected); s=$(state "$e")
    echo "expected: init writes $e$([ "$HOME" = "$REAL_HOME" ] && echo ' (the reviewed bytes for this machine)')"
    echo "now: state $s$([ -e "$F" ] && echo "; $(sha "$F")")"
    case "$s" in
      absent) echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      other) die "a different $F is there: it is never overwritten (P-3); ask the CTO" ;;
    esac ;;
  apply)
    built; e=$(expected); s=$(state "$e")
    case "$s" in
      applied) echo "apply: already applied ($e); nothing to do"; exit 0 ;;
      other) mkdir -p "$BACKUP"; cp -p "$F" "$BACKUP/gate.json.found"; (cd "$BACKUP" && sha256sum gate.json.found > gate.json.found.sha256)
             die "a different $F is there (backed up to $BACKUP/gate.json.found, $(sha "$F")): never overwritten (P-3)" ;;
    esac
    [ -e "$BACKUP/applied.sha256" ] && die "$BACKUP holds an earlier apply's record: move it aside first"
    mkdir -p "$BACKUP"
    { [ -d "$MACHINE" ] && (cd "$MACHINE" && find . -mindepth 1 -maxdepth 1 -printf '%P\n' | sort); } > "$BACKUP/machine-before.txt" || true
    echo "the machine folder before: $(paste -sd' ' "$BACKUP/machine-before.txt")"
    gov resources --init-config > "$BACKUP/init.json" 2> "$BACKUP/init.err" || { cat "$BACKUP/init.err" >&2; die "init-config failed"; }
    got=$(sha "$F")
    echo "$got  $F" > "$BACKUP/applied.sha256"
    [ "$got" = "$e" ] || die "the written file hashes to $got, not $e: run undo"
    echo "written: $F ($got, $(stat -c %s "$F") bytes, mode $(stat -c %a "$F"))"
    # W2-20's gate on the file: a session admitted (the check every launch runs), an over-limit start refused
    if gov resources --check > "$BACKUP/check-session.json" 2>&1; then echo "gate: a session start is admitted (exit 0)"
    else cat "$BACKUP/check-session.json" >&2; echo "apply.sh: the file is written but the gate is shut on a reading (above): the file stays; tell the CTO" >&2; fi
    set +e; gov resources --check --gpu-need-mib 20000 > "$BACKUP/check-over.json" 2>&1; rc=$?; set -e
    [ "$rc" = 3 ] && echo "gate: a start declaring 20000 MiB of GPU (above the card) is refused (exit 3)" \
      || { cat "$BACKUP/check-over.json" >&2; die "the over-limit start was not refused (exit $rc): run undo"; }
    (cd "$MACHINE" && find . -mindepth 1 -maxdepth 1 -printf '%P\n' | sort) > "$BACKUP/machine-after.txt"
    comm -13 "$BACKUP/machine-before.txt" "$BACKUP/machine-after.txt" | grep -vx gate.json > "$BACKUP/created.txt" || true
    echo "apply: done. Side files the gate's own reading made: $(paste -sd' ' "$BACKUP/created.txt")" ;;
  undo)
    [ -f "$BACKUP/applied.sha256" ] || die "no record of an apply in $BACKUP"
    rec=$(cut -d' ' -f1 "$BACKUP/applied.sha256")
    if [ ! -e "$F" ]; then echo "undo: $F is already gone"
    elif [ "$(sha "$F")" = "$rec" ]; then rm -f "$F"; echo "undo: removed $F ($rec)"
    else mv -f "$F" "$BACKUP/gate.json.changed-$(date +%Y%m%d-%H%M%S)"; echo "undo: $F had changed since the apply; moved to $BACKUP"; fi
    while read -r name; do
      [ -n "$name" ] && [ -e "$MACHINE/$name" ] && rm -rf "${MACHINE:?}/$name" && echo "undo: removed the side file $MACHINE/$name"
    done < "$BACKUP/created.txt"
    if [ -s "$BACKUP/machine-before.txt" ] || [ -d "$MACHINE" ]; then
      now=$( (cd "$MACHINE" && find . -mindepth 1 -maxdepth 1 -printf '%P\n' | sort) 2>/dev/null || true)
      [ "$now" = "$(cat "$BACKUP/machine-before.txt")" ] && echo "undo: the machine folder holds what it held before the apply" \
        || echo "undo: note: the machine folder now holds: $now"
    fi
    mv "$BACKUP/applied.sha256" "$BACKUP/applied.sha256.undone-$(date +%Y%m%d-%H%M%S)"
    echo "undo: done" ;;
  *) echo "usage: bash apply.sh check|apply|undo" >&2; exit 2 ;;
esac
