#!/usr/bin/env bash
# ACT-STOP-IDLE-1 (DEC-1110 (1)): the CTO's idle check as a second Stop hook.  apply.sh check | apply | undo
#   check  the three draft files hash as reviewed; the targets absent (or already these files); the settings file is
#          the rehearsed one (state old) or carries the entry (state applied); the draft tests pass on the draft hook
#   apply  check; settings.local.json backed up beside this file; the hook and its tests installed (sha256 checked);
#          the one Stop entry added (sha256 checked against the rehearsed bytes); only that entry differs; the
#          installed tests and the inbox waiter's tests pass; the hook's command, as Claude Code runs it, answers
#          nothing for another session
#   undo   the backup put back if the settings still hash as written (else only the entry removed); the two files
#          removed if they are untracked and unchanged (if committed: `git revert` that commit); the hook's turn
#          state removed (its log kept as the record)
# STOPIDLE_REPO points it at a clone for the rehearsal; the pinned "after" hash is checked only for the live tree.
set -u
A=$(cd "$(dirname "$0")" && pwd)
LIVE=/home/usain/Dynamic-Agentic-Engineering-OS
REPO=${STOPIDLE_REPO:-$LIVE}
BK=$A/backup
HOOK_SHA=d56a7aa7933197c3089a513f78c26c5b870644885dd01f01f0478d22d74a3ada
TEST_SHA=a58027c533fd81768a7782027be10370222f08b3a759325ca6704826d529b1f4
EDIT_SHA=b9afa575c4ed90e1b06d880f10db94ed39f0e796361481f3135b6fac4dd21f80
SET_BEFORE=2b8909d236b70f8cef97eb23d5023b151dbc05e9ec879a189caee70bfb33d477
SET_AFTER_LIVE=d715292711a2c38fe7ea3830df3c1000b001c7348876f74902fd683981d98624
HOOK_DST=$REPO/governance/project/orchestration/tools/stop_idle_check.py
TEST_DST=$REPO/tests/unit/orchestration/test_stop_idle_check.py
SET=$REPO/.claude/settings.local.json
STATE_FILE=$REPO/.gov-runtime/scratch/orchestrator/log/stop-idle-state.json
say() { echo "apply.sh: $*"; }
die() { echo "apply.sh: REFUSED: $*" >&2; exit 1; }
sha() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }
edit() { python3 -I "$A/settings_edit.py" "$@"; }

expected_after() { edit expect "$SET" "$REPO"; }

settings_state() {  # old | applied | other
  local s; s=$(sha "$SET")
  if [ "$s" = "$SET_BEFORE" ]; then echo old; return; fi
  if grep -q 'stop_idle_check.py' "$SET" 2>/dev/null; then
    if [ "$REPO" = "$LIVE" ] && [ "$s" != "$SET_AFTER_LIVE" ]; then echo other; else echo applied; fi
    return
  fi
  echo other
}

check() {
  [ "$(sha "$A/stop_idle_check.py")" = "$HOOK_SHA" ] || die "stop_idle_check.py is not the reviewed file (sha256 $(sha "$A/stop_idle_check.py"))"
  [ "$(sha "$A/test_stop_idle_check.py")" = "$TEST_SHA" ] || die "test_stop_idle_check.py is not the reviewed file"
  [ "$(sha "$A/settings_edit.py")" = "$EDIT_SHA" ] || die "settings_edit.py is not the reviewed file"
  say "the three draft files hash as reviewed (hook ${HOOK_SHA:0:12}, tests ${TEST_SHA:0:12}, edit ${EDIT_SHA:0:12})"
  for pair in "$HOOK_DST:$HOOK_SHA" "$TEST_DST:$TEST_SHA"; do
    local f=${pair%%:*} want=${pair##*:}
    if [ -e "$f" ] && [ "$(sha "$f")" != "$want" ]; then die "$f exists and is not the reviewed file"; fi
  done
  local st; st=$(settings_state)
  [ "$st" = other ] && die "$SET is neither the rehearsed file (${SET_BEFORE:0:12}) nor the applied one: re-rehearse"
  if [ "$REPO" = "$LIVE" ] && [ "$st" = old ]; then
    [ "$(expected_after)" = "$SET_AFTER_LIVE" ] || die "the settings edit would not write the rehearsed bytes"
  fi
  grep -q 'stop_waiter_check.py' "$SET" || die "the inbox waiter's Stop entry is missing from $SET: look first"
  local out
  out=$(cd /tmp && GOV_STOPIDLE_HOOK="$A/stop_idle_check.py" \
        GOV_STOPIDLE_LIVE_DND="$REPO/governance/project/orchestration/packages/DECIDED-NOT-DONE.md" \
        python3 -m pytest -q -p no:cacheprovider "$A/test_stop_idle_check.py" 2>&1 | tail -1)
  case "$out" in *" passed"*) case "$out" in *failed*|*error*) die "the draft tests: $out";; esac;; *) die "the draft tests: $out";; esac
  say "the draft tests on the draft hook: $out"
  say "state: $st (settings $(sha "$SET" | cut -c1-12))"
  STATE=$st
}

apply() {
  check
  if [ "$STATE" = applied ] && [ "$(sha "$HOOK_DST")" = "$HOOK_SHA" ] && [ "$(sha "$TEST_DST")" = "$TEST_SHA" ]; then
    say "already applied: nothing to do"; return 0
  fi
  mkdir -p "$BK"
  if [ "$STATE" = old ]; then
    cp -p "$SET" "$BK/settings.local.json.before"
    [ "$(sha "$BK/settings.local.json.before")" = "$SET_BEFORE" ] || die "the backup does not hash as the settings did"
    sha "$BK/settings.local.json.before" > "$BK/settings.local.json.before.sha256"
    say "settings backed up: $BK/settings.local.json.before (${SET_BEFORE:0:12})"
  fi
  install -m 0644 "$A/stop_idle_check.py" "$HOOK_DST" && install -m 0644 "$A/test_stop_idle_check.py" "$TEST_DST" \
    || die "the files could not be installed"
  [ "$(sha "$HOOK_DST")" = "$HOOK_SHA" ] && [ "$(sha "$TEST_DST")" = "$TEST_SHA" ] || die "installed files do not hash as reviewed"
  say "installed: governance/project/orchestration/tools/stop_idle_check.py, tests/unit/orchestration/test_stop_idle_check.py"
  local want got; want=$(expected_after); got=$(edit add "$SET" "$REPO") || die "the settings edit failed"
  [ "$got" = "$want" ] || die "the settings now hash $got, not $want"
  [ "$REPO" != "$LIVE" ] || [ "$got" = "$SET_AFTER_LIVE" ] || die "the settings now hash $got, not the rehearsed $SET_AFTER_LIVE"
  say "settings: the idle check's Stop entry added (sha256 ${got:0:12})"
  edit verify "$BK/settings.local.json.before" "$SET" || die "the settings differ by more than the one entry: run undo"
  local t
  t=$(cd "$REPO" && python3 -m pytest -q -p no:cacheprovider tests/unit/orchestration/test_stop_idle_check.py \
      tests/unit/orchestration/test_stop_waiter_check.py 2>&1 | tail -1)
  case "$t" in *" passed"*) case "$t" in *failed*|*error*) die "the installed tests: $t (run undo)";; esac;; *) die "the installed tests: $t (run undo)";; esac
  say "installed tests (the idle check and the inbox waiter's): $t"
  local cmd ans
  cmd=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print([h["command"] for e in d["hooks"]["Stop"] for h in e["hooks"] if "stop_idle_check.py" in h["command"]][0])' "$SET")
  ans=$(echo '{"session_id": "not-the-cto", "stop_hook_active": false}' | bash -c "$cmd"; echo "rc=$?")
  [ "$ans" = "rc=0" ] || die "the hook's command answered '$ans' for another session (run undo)"
  say "the hook's command as Claude Code runs it: another session, no answer, exit 0"
  say "APPLIED. It takes effect in the CTO's session at its next settings reload or restart."
}

undo() {
  local s; s=$(sha "$SET")
  if grep -q 'stop_idle_check.py' "$SET"; then
    if [ -f "$BK/settings.local.json.before" ] && [ "$(sha "$BK/settings.local.json.before")" = "$SET_BEFORE" ] \
        && [ "$s" = "$(edit expect "$BK/settings.local.json.before" "$REPO")" ]; then
      cp -p "$BK/settings.local.json.before" "$SET"; say "settings: the backup put back (${SET_BEFORE:0:12})"
    else
      edit remove "$SET" >/dev/null || die "could not remove the entry"; say "settings changed since apply: only the idle check's entry removed ($(sha "$SET" | cut -c1-12))"
    fi
  else
    say "settings: no idle check entry (nothing to undo there)"
  fi
  for pair in "$HOOK_DST:$HOOK_SHA" "$TEST_DST:$TEST_SHA"; do
    local f=${pair%%:*} want=${pair##*:}
    [ -e "$f" ] || continue
    if git -C "$REPO" ls-files --error-unmatch "${f#$REPO/}" >/dev/null 2>&1; then
      say "${f#$REPO/} is committed: left in place (inert without the entry); remove it with git revert of the ACT's commit"
    elif [ "$(sha "$f")" = "$want" ]; then
      rm -f -- "$f"; say "removed ${f#$REPO/}"
    else
      mkdir -p "$BK"; mv -- "$f" "$BK/"; say "${f#$REPO/} was changed after apply: moved to $BK/"
    fi
  done
  rm -f -- "$STATE_FILE"
  say "UNDONE (log/stop-idle.log kept as the record). State now: $(settings_state)"
}

case "${1:-}" in
  check) check;;
  apply) apply;;
  undo) undo;;
  *) sed -n 2,13p "$0"; exit 2;;
esac
