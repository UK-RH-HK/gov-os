#!/usr/bin/env bash
# ACT-GATE-CONFIG-2 (DEC-1103 (1); the CTO's ruling 2026-11-09): W2-20's machine gate file rewritten for round 2's
# configuration format, frozen from W2-20's head 28fbcfebf. ACT-GATE-CONFIG-1's file (sha256 de4fb326288d…, round 1's
# key names) is moved aside and kept; `gov resources --init-config` from W2-20's code at 28fbcfebf writes the new one.
#   bash apply.sh check   W2-20's code as built, the interpreter, the file's state (old | absent | applied | other)
#                         and the bytes init would write (their sha256); changes nothing
#   bash apply.sh apply   moves ACT-1's file aside (kept in the backup with its sha256), runs `gov resources
#                         --init-config` (W2-20's code), checks the written file against the bytes expected; then W2-20's
#                         gate admits a session and refuses an over-limit start (a GPU need above the card). A file that
#                         is neither ACT-1's nor the expected one is backed up and never overwritten: apply stops
#   bash apply.sh undo    removes the file apply wrote if it still hashes as written (else moves it aside to the
#                         backup), puts ACT-1's file back (its sha256 checked), and removes the side files apply's own
#                         gate reading made where there were none
# HOME decides where the file goes (the rehearsal gives a throwaway HOME). Backups and records go to $GATE_BACKUP,
# default backup/ beside this file. It commits nothing and touches nothing in any repository.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
W=${GATE_W2_20:-/home/usain/gov-os-worktrees/W2-20}
W_HEAD=28fbcfebf                       # W2-20's head: round 2 and the designer's rounds 4-6 (the format frozen here)
CONFIG_SHA=560c8d58d35a001dc083a980720e4dfd3a36b3e4ac5ad8525dabb80d6803bcad  # src/gov/resources/config.py at that head
OLD_SHA=de4fb326288d80d9d627ad910542ae5d86834c98a3d8895c0e16b9ece2fcd457     # ACT-GATE-CONFIG-1's file
NEW_SHA=52e32fc182d6e07c856512eb6926e7442eb16c856b46194f35d522e238c44034     # the file init writes (CPUs 0-19; no HOME in it)
REAL_HOME=/home/usain
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

built() {  # W2-20's code is the frozen head's, and the interpreter runs it
  [ -d "$W/src/gov/resources" ] || die "$W has no src/gov/resources (W2-20's worktree)"
  [ "$(sha "$W/src/gov/resources/config.py")" = "$CONFIG_SHA" ] || die "W2-20's config.py differs from 28fbcfebf's (the frozen format)"
  local head; head=$(git -C "$W" rev-parse HEAD)
  case "$head" in "$W_HEAD"*) ;; *) echo "note: W2-20's worktree is at ${head:0:12}, not $W_HEAD; its config.py is 28fbcfebf's (checked), so the format is the frozen one";; esac
  local mod; mod=$(w2 -c 'import gov.resources.config as c; print(c.__file__)') || die "$PY cannot import W2-20's code"
  [ "$mod" = "$W/src/gov/resources/config.py" ] || die "$PY imports $mod, not W2-20's"
  echo "W2-20: $W at ${head:0:12}; config.py $CONFIG_SHA; interpreter $PY ($("$PY" --version 2>&1))"
}
expected() {  # the sha256 of the bytes init would write here, from W2-20's template (nothing written)
  local e; e=$(w2 "$HERE/expected.py") || die "expected.py failed"
  [ "$e" = "$NEW_SHA" ] || die "init would write $e here, not the reviewed $NEW_SHA (another CPU set? run it outside any taskset or slot)"
  echo "$e"
}
state() {  # old | absent | applied | other
  if [ ! -e "$F" ] && [ ! -L "$F" ]; then echo absent
  elif [ -f "$F" ] && [ ! -L "$F" ] && [ "$(sha "$F")" = "$NEW_SHA" ]; then echo applied
  elif [ -f "$F" ] && [ ! -L "$F" ] && [ "$(sha "$F")" = "$OLD_SHA" ]; then echo old
  else echo other; fi
}
listing() { (cd "$MACHINE" && find . -mindepth 1 -maxdepth 1 -printf '%P\n' | sort) 2>/dev/null || true; }

cmd=${1:-}
echo "apply.sh $cmd: HOME $HOME; file $F"
case "$cmd" in
  check)
    built; e=$(expected); s=$(state)
    echo "expected: init writes $e (the reviewed bytes)"
    echo "now: state $s$([ -e "$F" ] && echo "; $(sha "$F")")"
    case "$s" in
      old) echo "check: ready to apply (ACT-GATE-CONFIG-1's file is there; apply moves it aside and keeps it)" ;;
      absent) echo "check: ready to apply (no file there)" ;;
      applied) echo "check: already applied" ;;
      other) die "a file that is neither ACT-1's nor the expected one is at $F: it is never overwritten; ask the CTO" ;;
    esac ;;
  apply)
    built; e=$(expected); s=$(state)
    case "$s" in
      applied) echo "apply: already applied ($e); nothing to do"; exit 0 ;;
      other) mkdir -p "$BACKUP"; cp -p "$F" "$BACKUP/gate.json.found"; (cd "$BACKUP" && sha256sum gate.json.found > gate.json.found.sha256)
             die "a file that is neither ACT-1's nor the expected one is at $F (backed up to $BACKUP/gate.json.found, $(sha "$F")): never overwritten" ;;
    esac
    [ -e "$BACKUP/applied.sha256" ] && die "$BACKUP holds an earlier apply's record: move it aside first"
    mkdir -p "$BACKUP"
    listing > "$BACKUP/machine-before.txt"
    echo "the machine folder before: $(paste -sd' ' "$BACKUP/machine-before.txt")"
    if [ "$s" = old ]; then
      mv "$F" "$BACKUP/gate.json.act1"
      (cd "$BACKUP" && sha256sum gate.json.act1 > gate.json.act1.sha256)
      [ "$(sha "$BACKUP/gate.json.act1")" = "$OLD_SHA" ] || die "the moved file does not hash as ACT-1's"
      echo "moved aside: ACT-GATE-CONFIG-1's file to $BACKUP/gate.json.act1 ($OLD_SHA)"
    fi
    gov resources --init-config > "$BACKUP/init.json" 2> "$BACKUP/init.err" || { cat "$BACKUP/init.err" >&2; die "init-config failed: run undo"; }
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
    listing > "$BACKUP/machine-after.txt"
    comm -13 "$BACKUP/machine-before.txt" "$BACKUP/machine-after.txt" | grep -vx gate.json > "$BACKUP/created.txt" || true
    echo "apply: done. Side files the gate's own reading made: $(paste -sd' ' "$BACKUP/created.txt")" ;;
  undo)
    [ -f "$BACKUP/applied.sha256" ] || die "no record of an apply in $BACKUP"
    rec=$(cut -d' ' -f1 "$BACKUP/applied.sha256")
    if [ ! -e "$F" ]; then echo "undo: $F is already gone"
    elif [ "$(sha "$F")" = "$rec" ]; then rm -f "$F"; echo "undo: removed $F ($rec)"
    else mv -f "$F" "$BACKUP/gate.json.changed-$(date +%Y%m%d-%H%M%S)"; echo "undo: $F had changed since the apply; moved to $BACKUP"; fi
    if [ -f "$BACKUP/gate.json.act1" ]; then
      [ "$(sha "$BACKUP/gate.json.act1")" = "$OLD_SHA" ] || die "the kept ACT-1 file no longer hashes as $OLD_SHA"
      mv "$BACKUP/gate.json.act1" "$F"
      echo "undo: ACT-GATE-CONFIG-1's file put back ($(sha "$F"))"
    fi
    while read -r name; do
      [ -n "$name" ] && [ -e "$MACHINE/$name" ] && rm -rf "${MACHINE:?}/$name" && echo "undo: removed the side file $MACHINE/$name"
    done < "$BACKUP/created.txt"
    [ "$(listing)" = "$(cat "$BACKUP/machine-before.txt")" ] && echo "undo: the machine folder holds what it held before the apply" \
      || echo "undo: note: the machine folder now holds: $(listing | paste -sd' ')"
    mv "$BACKUP/applied.sha256" "$BACKUP/applied.sha256.undone-$(date +%Y%m%d-%H%M%S)"
    echo "undo: done" ;;
  *) echo "usage: bash apply.sh check|apply|undo" >&2; exit 2 ;;
esac
