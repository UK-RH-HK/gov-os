#!/usr/bin/env bash
# DEC-1100 (3), ACT-SELECT-HOOK-1: the rehearsal, end to end, in a scratch clone. Changes nothing live.
#   bash rehearse.sh [step ...]   default: every step, in order; the log goes to rehearsal.log beside this file
# Steps: live_before prepare check apply undo reapply behaviour faults hook_direct final_undo live_after
# Layout: ~/gov-os-runs/SELECT-HOOK-rehearsal (made by this script, marked by its .select-hook-rehearsal file):
#   Dynamic-Agentic-Engineering-OS  a --shared clone at the main tree's HEAD, on its own w2/integrate; its
#                                   .git/hooks/reference-transaction starts as the live hook's exact bytes
#   wt                              a worktree of the clone (a landing made from a worktree exports GIT_DIR to the hook)
#   rec/                            what the stubs record; slots/ the private heavy-slot locks; clones/ the tool's clones
# apply.sh runs on the exact bytes (check, apply, undo, apply again). For the landings, the installed hook is the same
# file with three substitutions only (shown by diff): the main tree's path -> the clone's, ~/.local/bin/gov -> a stub
# that records its call (no real rebuild), the store's refresh lock -> a private one. The tool runs in the clone with a
# stub verifier (no pytest), passed to it through git's environment as the hook inherits it.
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/select-hook
BASE=$HOME/gov-os-runs/SELECT-HOOK-rehearsal
R=$BASE/Dynamic-Agentic-Engineering-OS
WT=$BASE/wt
RH=$R/$SUB/drafts/select-hook
HOOK=$R/.git/hooks/reference-transaction
REC=$BASE/rec
LOG=${REHEARSAL_LOG:-$HERE/rehearsal.log}
LIVE=".git/hooks/reference-transaction $SUB/tools/landing_select.sh governance/project/test-map.yaml .claude/settings.json"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
say() { printf '\n== %s (%s)\n' "$1" "$(date '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
hashes() { (cd "$MAIN" && sha256sum $LIVE); }
TLOG=$R/$SUB/log/landing-select.log
export LANDING_VERIFY=$BASE/stub_verify.sh LANDING_PREP=true LANDING_CLONES=$BASE/clones LANDING_DISK=$BASE/stub_disk.sh \
  STUB_REC=$REC
GC=(-c user.name=rehearsal -c user.email=r@r)
land() {  # $1 path, $2 trailers: change the path on the clone's w2/integrate (checked out in the clone), commit; prints ms
  local t0 t1; mkdir -p "$(dirname "$R/$1")"; echo "$RANDOM" >> "$R/$1"
  git -C "$R" add -f -- "$1"
  t0=$(date +%s%N); git -C "$R" "${GC[@]}" commit -q -m "rehearsal: $1" -m "$2" -- "$1"; echo $? > "$BASE/last_rc"
  t1=$(date +%s%N); echo $(( (t1 - t0) / 1000000 ))
}
wait_line() {  # $1 file, $2 grep -E pattern, $3 seconds: a bounded wait for a line (the detached work writes it)
  local end=$(( $(date +%s) + $3 ))
  until grep -qE -- "$2" "$1" 2>/dev/null; do [ "$(date +%s)" -ge "$end" ] && return 1; sleep 0.2; done
}
wait_runs() {  # every detached run the tool's log names, by pid (tools/proc.sh), bounded
  local p; for p in $(sed -n 's/.*started detached, pid \([0-9]*\).*/\1/p' "$TLOG" 2>/dev/null); do
    bash "$MAIN/$SUB/tools/proc.sh" wait --max 60 --every 1 "$p" >/dev/null || bad "run pid $p still going after 60 s"
  done
}
refreshes() { grep -c '^gov rebuild --integration w2/integrate' "$REC/gov.txt" 2>/dev/null || echo 0; }
rewrite() {  # $1 hook file -> $2: the three substitutions
  sed -e "s#$MAIN#$R#g" -e "s#/home/usain/.local/bin/gov#$BASE/stub_gov.sh#g" \
      -e "s#/home/usain/gov-os-worktrees/W2-00-store.refresh.lock#$BASE/refresh.lock#g" "$1" > "$2"; chmod 755 "$2"
}

step_live_before() { say "live_before: the live files' hashes"; hashes | tee "$BASE.live-before.txt"; }
step_prepare() {
  say "prepare: the clone, the stubs, the live hook's exact bytes"
  if [ -e "$BASE" ]; then
    [ -f "$BASE/.select-hook-rehearsal" ] || { bad "$BASE exists and is not this script's"; return 1; }
    git -C "$R" worktree remove --force "$WT" 2>/dev/null; rm -rf "$BASE"
  fi
  mkdir -p "$BASE" "$REC" "$BASE/slots" "$BASE/clones" && : > "$BASE/.select-hook-rehearsal"
  git clone -q --shared --no-checkout "$MAIN" "$R" || { bad "clone"; return 1; }
  git -C "$R" checkout -q -B w2/integrate "$(git -C "$MAIN" rev-parse HEAD)" || { bad "checkout"; return 1; }
  git -C "$R" worktree add -q -b rehearsal-wt "$WT" HEAD || bad "worktree"
  mkdir -p "$R/$SUB/tools" "$R/$SUB/drafts" "$R/$SUB/log" "$R/$SUB/dispatch/inbox"
  cp -p "$MAIN/$SUB/tools/"{landing_select.sh,heavy_slot.sh,proc.sh,disk_gate.sh} "$R/$SUB/tools/"
  sed -i "s#$MAIN#$R#g" "$R/$SUB/tools/landing_select.sh"
  printf 'SLOTS=3\nWORKERS=6\nDIR=%s\n' "$BASE/slots" > "$R/$SUB/tools/heavy_slots.conf"
  cp -a "$HERE" "$R/$SUB/drafts/" && rm -rf "$RH/backup" "$RH/rehearsal.log"
  cp -p "$MAIN/.git/hooks/reference-transaction" "$HOOK"
  printf '#!/bin/sh\necho "gov $* cwd=$(pwd) GIT_DIR=${GIT_DIR-unset} slot=${GOV_HEAVY_SLOT-}" >> %s/gov.txt\n' "$REC" > "$BASE/stub_gov.sh"
  printf '#!/bin/sh\nexit 0\n' > "$BASE/stub_disk.sh"
  cat > "$BASE/stub_verify.sh" <<'EOF'
#!/usr/bin/env bash
[ "$1" = --fg ] && shift
mkdir -p "$LEAD_VERIFY_OUT"
echo "verify tree=$1 head=$(git -C "$1" rev-parse HEAD) $(grep -o -- '"--merge", "[^"]*"' "$LEAD_VERIFY_SELECT")" >> "$STUB_REC/verify.txt"
echo "stub summary" > "$LEAD_VERIFY_OUT/summary.txt"; exit 0
EOF
  chmod 755 "$BASE"/stub_*.sh
  echo "clone $R at $(git -C "$R" rev-parse --short=12 HEAD) on $(git -C "$R" branch --show-current); worktree $WT"
  cmp -s "$HOOK" "$MAIN/.git/hooks/reference-transaction" && echo "the clone's hook: the live hook's exact bytes" || bad "hook copy"
}
step_check() { say "check: apply.sh check"; bash "$RH/apply.sh" check || bad "check"; }
step_apply() {
  say "apply: apply.sh apply"
  bash "$RH/apply.sh" apply || bad "apply"
  cmp -s "$HOOK" "$RH/reference-transaction.candidate" && echo "the hook is the candidate" || bad "not the candidate"
  diff "$RH/backup/reference-transaction" "$HOOK"
}
step_undo() {
  say "undo: apply.sh undo"
  bash "$RH/apply.sh" undo || bad "undo"
  cmp -s "$HOOK" "$MAIN/.git/hooks/reference-transaction" && [ "$(stat -c %a "$HOOK")" = 755 ] \
    && echo "undo: byte for byte the live hook, mode 755" || bad "undo not byte for byte"
}
step_reapply() {
  say "reapply: the backup moved aside, apply again (for the landings)"
  mv "$RH/backup" "$BASE/backup-1" && bash "$RH/apply.sh" apply >/dev/null && echo "applied again: $(sha256sum "$HOOK" | cut -c1-12)" \
    || bad "reapply"
}
step_behaviour() {
  say "behaviour: landings through the hook, before the line and with it"
  cp -p "$HOOK" "$BASE/hook.applied"
  rewrite "$RH/backup/reference-transaction" "$BASE/hook.before.run"; rewrite "$BASE/hook.applied" "$BASE/hook.after.run"
  echo "the substitutions (before -> run copy):"; diff "$RH/backup/reference-transaction" "$BASE/hook.before.run" | sed 's/^/  /'
  echo "the run copies differ by the one line only:"; diff "$BASE/hook.before.run" "$BASE/hook.after.run" | sed 's/^/  /'
  local i ms before=() after=() n
  cp -p "$BASE/hook.before.run" "$HOOK"
  for i in $(seq 1 10); do before+=("$(land governance/project/orchestration/rehearsal-$i.md 'Task: DAEO-sdxk')"); done
  [ "$(git -C "$R" log --format=%s w2/integrate | grep -c '^rehearsal: governance/project/orchestration/rehearsal-')" = 10 ] || bad "a commit before the line failed"
  wait_line "$REC/gov.txt" . 30; sleep 1
  n=$(refreshes); echo "before the line: 10 landings, store refreshes started: $n"
  [ "$n" -ge 1 ] || bad "no refresh before the line"
  [ -e "$TLOG" ] && bad "the tool ran before the line" || echo "before the line: the tool never ran"
  : > "$REC/gov.txt"
  cp -p "$BASE/hook.after.run" "$HOOK"
  for i in $(seq 1 10); do after+=("$(land governance/project/orchestration/rehearsal-b$i.md 'Task: DAEO-sdxk')"); done
  [ "$(git -C "$R" log --format=%s w2/integrate | grep -c '^rehearsal: governance/project/orchestration/rehearsal-b')" = 10 ] || bad "a commit with the line failed"
  wait_line "$TLOG" "none outside a ticket" 30 || bad "the tool did not log the records landings"
  wait_line "$REC/gov.txt" . 30; sleep 1
  n=$(refreshes); echo "with the line: 10 landings, store refreshes started: $n"
  [ "$n" -ge 1 ] || bad "no refresh with the line"
  med() { printf '%s\n' "$@" | sort -n | awk '{a[NR]=$1} END {print a[int((NR+1)/2)]}'; }
  echo "commit time, median of 10: before the line $(med "${before[@]}") ms (max $(printf '%s\n' "${before[@]}" | sort -n | tail -1)), with it $(med "${after[@]}") ms (max $(printf '%s\n' "${after[@]}" | sort -n | tail -1)); each: ${before[*]} / ${after[*]}"
  echo "-- a settings commit by the owner (an ACT): a run starts, on that commit"
  : > "$REC/gov.txt"
  ms=$(land .claude/settings.json $'Task: DAEO-sdxk\nRole: owner'); local c; c=$(git -C "$R" rev-parse HEAD)
  wait_line "$TLOG" "${c:0:12} \(.claude/settings.json\)" 30 && wait_runs && wait_line "$TLOG" ": GREEN: stub summary" 30 \
    && grep -q "head=$c \"--merge\", \"$c\"" "$REC/verify.txt" && echo "settings landing (${ms} ms): run on ${c:0:12}, GREEN, the stub saw --merge $c" \
    || bad "settings landing did not run as expected"
  [ "$(ls "$R/$SUB/dispatch/inbox" | wc -l)" = 1 ] && echo "one inbox item: $(ls "$R/$SUB/dispatch/inbox")" || bad "inbox"
  wait_line "$REC/gov.txt" . 30 && echo "the store refresh started too: $(head -1 "$REC/gov.txt" | cut -c1-120)" || bad "no refresh"
  echo "-- a ticket's merge touching settings: no run"
  git -C "$R" checkout -q -b w2/W2-99 && land .claude/settings.json $'Task: DAEO-ab12\nRole: engineer' >/dev/null
  git -C "$R" checkout -q w2/integrate
  git -C "$R" "${GC[@]}" merge -q --no-ff w2/W2-99 -m "Merge w2/W2-99" -m $'Task: DAEO-ab12\nRole: orchestrator'
  c=$(git -C "$R" rev-parse HEAD)
  wait_line "$TLOG" "\.\.${c:0:12}: 1 commit\(s\); none outside" 30 && echo "ticket merge ${c:0:12}: none outside a ticket" || bad "ticket merge"
  echo "-- a commit on another branch: the hook fires neither line"
  local nl; nl=$(wc -l < "$TLOG"); : > "$REC/gov.txt"
  git -C "$R" checkout -q -b side && land .claude/settings.json 'Task: DAEO-sdxk' >/dev/null; git -C "$R" checkout -q w2/integrate
  sleep 2; [ "$(wc -l < "$TLOG")" = "$nl" ] && [ ! -s "$REC/gov.txt" ] && echo "another branch: nothing" || bad "another branch fired"
  echo "-- a landing made from a worktree (git exports GIT_DIR=<clone>/.git/worktrees/wt to the hook)"
  local wh; wh=$(git -C "$WT" rev-parse HEAD)
  git -C "$WT" checkout -q --detach "$(git -C "$R" rev-parse w2/integrate)"
  echo "$RANDOM" >> "$WT/governance/project/test-map.yaml"
  git -C "$WT" "${GC[@]}" commit -q -m "rehearsal: map from the worktree" -m 'Task: DAEO-sdxk' -- governance/project/test-map.yaml
  c=$(git -C "$WT" rev-parse HEAD); wh=$(git -C "$WT" rev-parse HEAD)
  (cd "$WT" && git update-ref refs/heads/w2/integrate "$c")
  wait_line "$TLOG" "${c:0:12} \(governance/project/test-map.yaml\)" 30 && wait_runs \
    && grep -q "head=$c \"--merge\", \"$c\"" "$REC/verify.txt" && [ "$(git -C "$WT" rev-parse HEAD)" = "$wh" ] \
    && echo "worktree landing ${c:0:12}: the run's clone at it; the worktree's HEAD untouched" || bad "worktree landing"
  wait_line "$REC/gov.txt" "worktrees/wt" 30 && echo "note (W2-116's own line, unchanged): its refresh ran with $(grep -o 'GIT_DIR=[^ ]*worktrees/wt' "$REC/gov.txt" | head -1)"
  git -C "$R" checkout -q -f w2/integrate
  echo "-- a FRESH-80 hold: the landing deferred, the refresh line unchanged"
  echo "FRESH-80 HOLD: rehearsal" > "$R/$SUB/log/act-in-progress.txt"
  land .claude/settings.json 'Task: DAEO-sdxk' >/dev/null
  wait_line "$TLOG" "DEFERRED, a FRESH-80 or E4 hold" 30 && echo "hold: DEFERRED logged" || bad "hold"
  rm -f "$R/$SUB/log/act-in-progress.txt"
}
step_faults() {
  say "faults: the tool slow, failing or missing never delays or fails the transaction"
  local T=$R/$SUB/tools/landing_select.sh ms rc
  mv "$T" "$BASE/landing_select.real"
  printf '#!/usr/bin/env bash\nsleep 30\n' > "$T"
  ms=$(land governance/project/orchestration/fault-slow.md 'Task: DAEO-sdxk'); rc=$(cat "$BASE/last_rc")
  echo "the tool sleeping 30 s: commit rc $rc in $ms ms"; [ "$ms" -lt 3000 ] || bad "a slow tool delayed the commit"
  printf '#!/usr/bin/env bash\nexit 1\n' > "$T"
  ms=$(land governance/project/orchestration/fault-exit.md 'Task: DAEO-sdxk'); rc=$(cat "$BASE/last_rc")
  echo "the tool exiting 1: commit rc $rc in $ms ms"; [ "$rc" = 0 ] || bad "a failing tool failed the commit"
  rm -f "$T"
  ms=$(land governance/project/orchestration/fault-missing.md 'Task: DAEO-sdxk'); rc=$(cat "$BASE/last_rc")
  echo "the tool missing: commit rc $rc in $ms ms"; [ "$rc" = 0 ] || bad "a missing tool failed the commit"
  git -C "$R" log -3 --format='  %h %s' w2/integrate
  mv "$BASE/landing_select.real" "$T"
}
step_hook_direct() {
  say "hook_direct: the hook run by hand, every state, exit always 0"
  local h; h=$(git -C "$R" rev-parse w2/integrate)
  for st in prepared aborted committed; do
    echo "0000000000000000000000000000000000000000 $h refs/heads/w2/integrate" | "$HOOK" "$st"; echo "  $st: exit $?"
  done
  echo "$h $h refs/heads/other" | "$HOOK" committed; echo "  committed, another ref: exit $?"
  : | "$HOOK" committed; echo "  committed, empty input: exit $?"
}
step_final_undo() {
  say "final_undo: the applied hook back, then apply.sh undo"
  cp -p "$BASE/hook.applied" "$HOOK"
  bash "$RH/apply.sh" undo || bad "final undo"
  cmp -s "$HOOK" "$MAIN/.git/hooks/reference-transaction" && echo "the clone's hook: byte for byte the live hook again" || bad "final undo bytes"
  wait_runs
}
step_live_after() {
  say "live_after: the live files' hashes"
  hashes > "$BASE.live-after.txt"; cat "$BASE.live-after.txt"
  cmp -s "$BASE.live-before.txt" "$BASE.live-after.txt" && echo "live files: unchanged" || bad "a live file changed"
  [ ! -e "$MAIN/$SUB/log/landing-select.log" ] && echo "the live tool log: not written" || bad "the live tool log was written"
}

steps=("$@")
[ ${#steps[@]} -eq 0 ] && steps=(live_before prepare check apply undo reapply behaviour faults hook_direct final_undo live_after)
echo "rehearse.sh: $(date '+%F %T'); steps: ${steps[*]}"
for s in "${steps[@]}"; do "step_$s"; done
echo; echo "rehearse.sh: done $(date '+%F %T'): $FAILS failure(s)"
exit $((FAILS > 0))
