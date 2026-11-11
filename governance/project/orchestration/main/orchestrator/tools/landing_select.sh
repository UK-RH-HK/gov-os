#!/usr/bin/env bash
# DEC-1100 (2)-(4) (P-SELECT-FIXES-1 (iii), trigger (a), mechanism (a); in the CTO's tools first): a scoped test
# selection after every landing on w2/integrate that holds a commit outside a ticket touching the settings, the tool
# registry or the test map. It follows the landing and never holds it.
#
#   landing_select.sh --hook               the hook's form (ACT-SELECT-HOOK-1): the range from the last head this tool
#                                          examined (log/landing-select.head) to w2/integrate's head now; a first call
#                                          with no state takes the branch's previous reflog value
#   landing_select.sh [--fg] <old> <new>   an explicit range (the CTO by hand, e.g. after a deferred landing)
#   landing_select.sh --dry <old> <new>    decide only: print the commits that would start a run, run nothing
#
# A commit is OUTSIDE A TICKET when it carries `Role: owner` (an ACT), or no `Task: DAEO-<ticket>` other than
# DAEO-sdxk (the CTO's own, `decision-record`, or none). Only first-parent commits of old..new are read, so a ticket's
# merge is one commit, judged by its own trailers. A commit TOUCHES THE TRIGGER PATHS when its own change (against its
# first parent) holds .claude/settings*.json, .rulesync/** (the settings' source, P-SELECT-FIXES-1 S7),
# governance/project/tool-registry.yaml or governance/project/test-map.yaml.
#
# When one or more do, the run starts detached (its own session; the caller returns at once):
#   1. a `git clone --shared` of the repository at <new> (~/gov-os-runs/W2-00/landing-select/<stamp>), its store seeded
#      and rebuilt as a close's clone is (seed_store.py rebuild: DEC-1032);
#   2. lead_verify.sh --fg on it (the close's form: select_tests.py, the parallel run, the serial phase, each pytest
#      under heavy_slot.sh), the selection being those commits' own changes (select_tests.py --merge <c,...>, newest
#      first) on the tree at <new>: scoped, never the full suite (DEC-968); a refused selection is REFUSED, never green;
#   3. the verdict (GREEN, RED, REFUSED, INCOMPLETE, HELD) in log/landing-select.log and one item in the dispatcher's
#      inbox; the clone is removed unless the verdict is RED.
# Never during a FRESH-80 or E4 hold (log/act-in-progress.txt naming FRESH-80 or E4): the landing is DEFERRED, logged,
# and the state is not advanced, so the next landing's range holds it (or run it by hand: --fg <old> <new>). The hold is
# checked again inside the heavy slot just before each pytest starts (exit 75, verdict HELD).
# The operator agent's commit freeze (ACT-OPERATOR-1, DEC-1106 (3)): while <operator root>/install/act-in-progress.txt
# exists the live tree is mid-apply, so --hook waits for it to clear (polling, LANDING_OPWAIT seconds at most) before it
# takes its lock and reads its range; still there then, the landing is DEFERRED, logged, the state not advanced (the
# next landing's range holds it; a stale freeze is the owner's to remove). --fg refuses while it exists (HELD, 4).
# The landing check (OPERATOR-AGENT-1 §3, S16): every range --hook examines is also given to the install's
# landing_check.py; each commit outside a ticket on a (b) or (O) control path without `Role: owner`, or without
# `Role: operator` and an `Act:` trailer, becomes one P1 item in the dispatcher's inbox (status P1).
# Exit: 0 (also for a deferred or a quiet landing; --hook always 0); 2 usage or an unreadable range; with --fg, the
# run's own code (0 green, 1 red, 2 refused, 3 incomplete, 4 held).
# Env (for the tests; defaults in brackets): LANDING_REPO [the main tree], LANDING_BRANCH [w2/integrate],
# LANDING_ORCH [the CTO's folder: log/, dispatch/inbox/], LANDING_CLONES [~/gov-os-runs/W2-00/landing-select],
# LANDING_VERIFY [tools/lead_verify.sh], LANDING_PREP [seed_store.py rebuild], LANDING_HEAVY [tools/heavy_slot.sh],
# LANDING_SELECT [tools/select_tests.py], LANDING_DISK [tools/disk_gate.sh], LANDING_OPFREEZE [the operator's freeze,
# /home/usain/gov-os-operator/install/act-in-progress.txt], LANDING_OPCHECK [its install's landing_check.py],
# LANDING_OPWAIT [3600], LANDING_OPPOLL [30].
set -u
# A hook runs with git's own variables (a landing made in a worktree exports GIT_DIR=<main>/.git/worktrees/<name>, which
# would turn every `git -C <path>` below, the clone's checkout included, onto that worktree): none is kept.
for v in $(compgen -e | grep '^GIT_'); do unset "$v"; done
SELF=$(readlink -f "${BASH_SOURCE[0]}")
TOOLS=$(dirname "$SELF")
ORCH=${LANDING_ORCH:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
HOLD=$ORCH/log/act-in-progress.txt
held() { [ -f "$HOLD" ] && grep -qE 'FRESH-80|E4' "$HOLD" 2>/dev/null; }

# The slot form (lead_verify.sh calls `bash $LEAD_VERIFY_SLOT <pytest command>`): the heavy slot, then the hold
# checked again once the slot is taken, then the command.
if [ "${LANDING_AS_SLOT:-}" = 1 ]; then
  if [ "${LANDING_IN_SLOT:-}" = 1 ]; then
    if held; then
      echo "landing_select: a FRESH-80 or E4 hold began; this pytest is not started" >&2
      [ -n "${LANDING_RUN_DIR:-}" ] && : > "$LANDING_RUN_DIR/held"
      exit 75
    fi
    # The hook starts this run in the background, where SIGINT (and under nohup SIGHUP) begins ignored and is
    # inherited: W2-96's signal cases then fail (6 false reds on 11-11 13:42, 16 of 16 green from a plain shell).
    exec env --default-signal=INT,HUP "$@"
  fi
  LANDING_IN_SLOT=1 exec bash "${LANDING_HEAVY:-$TOOLS/heavy_slot.sh}" bash "$SELF" "$@"
fi

REPO=${LANDING_REPO:-/home/usain/Dynamic-Agentic-Engineering-OS}
BRANCH=${LANDING_BRANCH:-w2/integrate}
LOG=$ORCH/log/landing-select.log
STATE=$ORCH/log/landing-select.head
LOCK=$ORCH/log/landing-select.lock
INBOX=$ORCH/dispatch/inbox
CLONES=${LANDING_CLONES:-$HOME/gov-os-runs/W2-00/landing-select}
OPFREEZE=${LANDING_OPFREEZE:-/home/usain/gov-os-operator/install/act-in-progress.txt}
OPCHECK=${LANDING_OPCHECK:-/home/usain/gov-os-operator/install/landing_check.py}
OPWAIT=${LANDING_OPWAIT:-3600}
OPPOLL=${LANDING_OPPOLL:-30}
opfrozen() { [ -e "$OPFREEZE" ] || [ -L "$OPFREEZE" ]; }
opwhat() { head -c 160 "$OPFREEZE" 2>/dev/null | head -1 | cut -d' ' -f1-3; }
TRIGGER='^(\.claude/settings[^/]*\.json|\.rulesync/.+|governance/project/tool-registry\.yaml|governance/project/test-map\.yaml)$'
mkdir -p "$ORCH/log"
say() { printf '%s %s\n' "$(date '+%F %T')" "$*" >> "$LOG"; }
g() { git -C "$REPO" "$@"; }
short() { printf '%s' "${1:0:12}"; }

outside() {  # $1 commit: 0 when it is outside a ticket
  local role task t
  role=$(g log -1 --format='%(trailers:key=Role,valueonly,separator=%x2C)' "$1")
  case ",${role// /}," in *,owner,*) return 0 ;; esac
  task=$(g log -1 --format='%(trailers:key=Task,valueonly,separator=%x2C)' "$1")
  local IFS=,
  for t in $task; do
    t=${t// /}
    [[ "$t" =~ ^DAEO-[a-z0-9]+$ ]] && [ "$t" != DAEO-sdxk ] && return 1
  done
  return 0
}
touched() {  # $1 commit: the trigger paths its own change holds (against its first parent), one per line
  g rev-parse -q --verify "$1^1" >/dev/null || return 0
  g -c core.quotePath=false diff --no-renames --name-only "$1^1" "$1" | grep -E "$TRIGGER"
}
decide() {  # $1 old, $2 new: prints "<commit> <paths, comma-joined>" per commit that starts a run, newest first
  local c p
  for c in $(g rev-list --first-parent "$1..$2"); do
    outside "$c" || continue
    p=$(touched "$c" | paste -sd, -)
    [ -n "$p" ] && echo "$c $p"
  done
}
inbox_item() {  # $1 status word, $2 body
  local stamp f n=1
  mkdir -p "$INBOX" || return 0
  stamp=$(date +%Y%m%d-%H%M%S); f=$INBOX/$stamp-landing-select.txt
  while ! (set -o noclobber; printf '%s' "$2" > "$f") 2>/dev/null; do n=$((n + 1)); f=$INBOX/$stamp-landing-select-$n.txt; done
}
landing_check() {  # $1 old, $2 new: the install's landing check (S16) on the range; one P1 inbox item per flagged commit
  [ -f "$OPCHECK" ] || { say "landing check: $OPCHECK absent; not run"; return 0; }
  local out rc
  out=$(env -u PYTHONPATH -u PYTHONHOME /usr/bin/python3 -I "$OPCHECK" --repo "$REPO" "$1..$2" 2>/dev/null); rc=$?
  printf '%s' "$out" | /usr/bin/python3 -I -c '
import json, sys
try:
    items = json.loads(sys.stdin.read() or "null")
    assert isinstance(items, list)
except Exception:
    items = [{"commit": None, "reason": "the landing check printed no JSON list"}]
for i in items:
    print("%s\t%s\t%s\t%s" % ((i.get("commit") or "-")[:12], ",".join(i.get("paths") or [])[:300],
                                (i.get("subject") or "")[:120], (i.get("reason") or "")[:200]))
' | while IFS=$'\t' read -r c p s why; do
    say "landing check: P1 $c ($p): $why"
    inbox_item P1 "log: $LOG
Landing check (OPERATOR-AGENT-1 §3, S16) after the landing $(short "$1")..$(short "$2") on $BRANCH: commit $c ($s) touches $p: $why
status: P1
"
  done
  [ "$rc" = 0 ] || say "landing check: exit $rc on $(short "$1")..$(short "$2")"
  return 0
}

run() {  # $1 stamp, $2 old, $3 new, $4 commits (comma-joined, newest first): the run, in the foreground of its caller
  local stamp=$1 old=$2 new=$3 commits=$4 out=$ORCH/log/landing-select/$1 clone=$CLONES/$1 rc verdict summary tmp=""
  mkdir -p "$out" "$CLONES"
  echo "$$" > "$out/run.pid"
  finish() {  # $1 verdict, $2 code, $3 summary
    echo "$2" > "$out/run.exit"
    say "run $stamp ($(short "$old")..$(short "$new")): $1: $3"
    inbox_item "$1" "log: $out
Landing select: $1 after the landing $(short "$old")..$(short "$new") on $BRANCH (commits outside a ticket on the trigger paths: $commits): $3
status: $1
"
    if [ "$1" != RED ] && [ -d "$clone" ]; then rm -rf "$clone"; fi
    if [ "$1" != RED ] && [ -n "$tmp" ] && [ -d "$tmp" ]; then rm -rf "$tmp"; fi  # a red keeps its failed tmp_paths
    return "$2"
  }
  held && { finish HELD 4 "a FRESH-80 or E4 hold began before the run; nothing run (run it by hand after the hold: landing_select.sh --fg $old $new)"; return; }
  local disk; disk=$(bash "${LANDING_DISK:-$TOOLS/disk_gate.sh}" 2>&1) || { finish INCOMPLETE 3 "not started: $disk"; return; }
  git clone -q --shared --no-checkout "$REPO" "$clone" > "$out/clone.txt" 2>&1 \
    && git -C "$clone" checkout -q --detach "$new" >> "$out/clone.txt" 2>&1 \
    || { finish INCOMPLETE 3 "the clone at $(short "$new") failed ($out/clone.txt)"; return; }
  if [ -n "${LANDING_PREP+x}" ]; then
    (cd "$clone" && eval "$LANDING_PREP") > "$out/prep.txt" 2>&1
  else
    local py; py=$(head -1 "$HOME/.local/bin/gov" 2>/dev/null | sed 's/^#!//'); [ -x "$py" ] || py=python3
    (cd "$clone" && env -u PYTHONPATH "$py" "$TOOLS/seed_store.py" rebuild "$clone" --who "landing-select $stamp") \
      > "$out/prep.txt" 2>&1
  fi || { finish INCOMPLETE 3 "the clone's store rebuild failed ($out/prep.txt)"; return; }
  cat > "$out/select.py" <<EOF
# landing_select.sh's selection for lead_verify.sh: select_tests.py on these commits' own changes (--merge), tree at HEAD
import os, sys
sel = os.environ.get("LANDING_SELECT") or "$TOOLS/select_tests.py"
os.execvp(sys.executable, [sys.executable, sel, *sys.argv[1:], "--merge", "$commits"])
EOF
  mkdir -p "$out/verify"  # lead_verify.sh with LEAD_VERIFY_PREPARED=1 does not create its folder (found 11-09 12:16)
  # The run's TMPDIR is short (DEC-1104 (3), found 11-09): a test's Unix socket lives under it, at
  # <TMPDIR>/pytest-of-<user>/pytest-<n>/popen-gw<k>/h<m>/.cache/gov-os/rerank.sock, and a socket's path is at most
  # 107 bytes. /tmp/gov-os-landing-<stamp> (43 bytes) left too little once a slot's few workers reached h10: 11
  # reranker cases red with "AF_UNIX path too long". /tmp/gov-os-ls-XXXXXX (21 bytes) leaves about 20 to spare.
  tmp=$(mktemp -d /tmp/gov-os-ls-XXXXXX) || { finish INCOMPLETE 3 "no temporary folder under /tmp"; return; }
  echo "$tmp" > "$out/tmpdir"
  LANDING_AS_SLOT=1 LANDING_RUN_DIR=$out LEAD_VERIFY_PREPARED=1 LEAD_VERIFY_OUT=$out/verify \
    LEAD_VERIFY_SELECT=$out/select.py LEAD_VERIFY_SLOT=$SELF LEAD_VERIFY_TMPDIR=$tmp \
    bash "${LANDING_VERIFY:-$TOOLS/lead_verify.sh}" --fg "$clone" W2-00 DAEO-sdxk > "$out/verify.log" 2>&1 \
    < /dev/null
  rc=$?
  summary=$(cat "$out/verify/summary.txt" 2>/dev/null || tail -1 "$out/verify.log")
  if [ -e "$out/held" ]; then finish HELD 4 "a FRESH-80 or E4 hold began during the run: $summary"; return; fi
  case "$rc" in
    0) verdict=GREEN ;; 1) verdict=RED ;; 2) verdict=REFUSED ;; *) verdict=INCOMPLETE rc=3 ;;
  esac
  [ "$verdict" = RED ] && summary="$summary; the clone kept: $clone (DEC-968: fix at once or revert)"
  finish "$verdict" "$rc" "$summary"
}

fg="" dry="" hook=""
case "${1:-}" in
  --fg) fg=1; shift ;;
  --dry) dry=1; shift ;;
  --hook) hook=1; shift ;;
  --run) shift; [ $# = 4 ] || exit 2; run "$@"; exit $? ;;
esac

if [ -n "$hook" ]; then
  waited=0
  while opfrozen; do
    if [ "$waited" -ge "$OPWAIT" ]; then
      say "hook: the operator's commit freeze ($(opwhat)) still holds after ${waited}s: DEFERRED, nothing examined, state not advanced (the next landing's range holds this one; a stale freeze is the owner's to remove)"
      exit 0
    fi
    sleep "$OPPOLL"; waited=$((waited + OPPOLL))
  done
  [ "$waited" -gt 0 ] && say "hook: waited ${waited}s for the operator's commit freeze to clear"
  exec 9>> "$LOCK"; flock -w 120 9 || { say "hook: the state lock was not free in 120 s; nothing examined"; exit 0; }
  new=$(g rev-parse -q --verify "refs/heads/$BRANCH") || { say "hook: no branch $BRANCH; nothing examined"; exit 0; }
  old=$(cat "$STATE" 2>/dev/null)
  if [ -z "$old" ] || ! g cat-file -e "$old^{commit}" 2>/dev/null; then
    old=$(g rev-parse -q --verify "refs/heads/$BRANCH@{1}") || { echo "$new" > "$STATE"; say "hook: no previous head of $BRANCH; state set to $(short "$new"), nothing examined"; exit 0; }
  fi
  [ "$old" = "$new" ] && exit 0
  if ! g merge-base --is-ancestor "$old" "$new"; then
    base=$(g merge-base "$old" "$new") || { echo "$new" > "$STATE"; say "hook: $(short "$old") and $(short "$new") share no history; state set, nothing examined"; exit 0; }
    say "hook: $BRANCH moved off $(short "$old") (not an ancestor of $(short "$new")): examining from the merge base $(short "$base")"
    old=$base
  fi
else
  [ $# = 2 ] || { sed -n 2,40p "$SELF" | grep -n '' | sed -n '1,12p' >&2; exit 2; }
  old=$(g rev-parse -q --verify "$1^{commit}") && new=$(g rev-parse -q --verify "$2^{commit}") \
    || { echo "landing_select: not a commit range in $REPO: $1 $2" >&2; exit 2; }
fi

found=$(decide "$old" "$new")
if [ -n "$dry" ]; then
  if [ -n "$found" ]; then echo "$found"; else echo "none"; fi
  exit 0
fi
if [ -n "$fg" ] && opfrozen; then
  say "landing $(short "$old")..$(short "$new"): HELD, the operator's commit freeze ($(opwhat)); run it again once it is gone"
  echo "landing_select: HELD: the operator's commit freeze $OPFREEZE exists" >&2
  exit 4
fi
if held; then
  say "landing $(short "$old")..$(short "$new"): DEFERRED, a FRESH-80 or E4 hold ($(head -1 "$HOLD" | cut -c1-80)); state not advanced${found:+; would run on $(echo "$found" | cut -c1-12 | paste -sd' ' -)}"
  exit 0
fi
[ -n "$hook" ] && echo "$new" > "$STATE"
[ -n "$hook" ] && landing_check "$old" "$new"
n=$(g rev-list --first-parent --count "$old..$new")
if [ -z "$found" ]; then
  say "landing $(short "$old")..$(short "$new"): $n commit(s); none outside a ticket on the trigger paths"
  exit 0
fi
commits=$(echo "$found" | cut -d' ' -f1 | paste -sd, -)
stamp=$(date +%Y%m%d-%H%M%S)-$$
say "landing $(short "$old")..$(short "$new"): $n commit(s); outside a ticket on the trigger paths: $(echo "$found" | while read -r c p; do printf '%s (%s) ' "$(short "$c")" "$p"; done)"
if [ -n "$fg" ]; then
  say "run $stamp: in the foreground"
  run "$stamp" "$old" "$new" "$commits"; exit $?
fi
mkdir -p "$ORCH/log/landing-select/$stamp"
setsid bash "$SELF" --run "$stamp" "$old" "$new" "$commits" < /dev/null >> "$ORCH/log/landing-select/$stamp/run.log" 2>&1 9>&- &
say "run $stamp: started detached, pid $! (its own session); folder $ORCH/log/landing-select/$stamp"
exit 0
