#!/usr/bin/env bash
# Re-pin window 4 (DEC-1087 (8)): the owner's act, by the owner's operator. gov from the wheel of w2/integrate's commit
# C below, which carries W2-92 (the stated links), W2-32 S11 (the candidate pool; switched on in retrieval.yaml by the
# CTO's commit right after this act, since the old pin refuses the key),
# W2-131 and W2-133 (register ids), W2-112 (the shared reranker releases its memory after each request), W2-134 and
# W2-61h S7 (the measure re-anchors; source families), W2-135 (a line over 4,000 characters cut), W2-116 (the
# integration store, refreshed after every merge; GOV_STORE for every worker) and W2-129 (gov links), with D-6 part 1
# and D-9's records. The integration store is rebuilt at C, the shared reranker restarted from the new pin (class 3,
# since W2-112 changed its service), and W2-116's reference-transaction hook installed.
# Run in a PLAIN TERMINAL (not inside a Claude session: it reinstalls gov, DEC-928 item 3):
#     bash REPIN-COMMANDS-W4.sh 2>&1 | tee ~/repin-w4.log
# It stops at the first failure. Before the switch (parts 0, A, S, B, C) a failure prints STOP and leaves what sessions
# use as it was (the new pin beside the old; the store link back on its old half). After the switch (parts D, H) a
# failed check switches straight back to the old pin, restarts the reranker from it, removes the hook, and prints
# ROLLED BACK: then tell the CTO.
# Paths: the live ones by default; the operator sets none of the GOV_REPIN_* variables. The CTO's rehearsal (DEC-1057)
# points them at a scratch copy: GOV_REPIN_LINK_HOME, GOV_REPIN_PINS, GOV_REPIN_STORE_LINK, GOV_REPIN_REGISTRY_REPO,
# GOV_REPIN_HOLD, GOV_REPIN_TMP, GOV_REPIN_HOOKS (the hooks folder), GOV_REPIN_SKIP_RERANK=1 (the rehearsal does not
# restart the live service; it checks the bytes only).
set -Eeuo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
C=bcea09060ebc              # w2/integrate's head on 2026-11-06 with every DEC-1087 build merged (W2-112's release last)
EPOCH=1794008644            # the commit's time: the wheel is reproducible
SHA=11a16d0fb0f9d1a23df72474a99c320c48f61a9cd025d8b320a2f1e4eb93d406   # the CTO's dry run: two builds, the same bytes
OLD=8284fb408bd4
case "$C$EPOCH$SHA" in *__*) echo "STOP: the commit, epoch or sha256 is not filled in (the CTO's hand-over)"; exit 1;; esac
FULL=$(git -C "$R" rev-parse --verify --quiet "$C^{commit}") || { echo "STOP: commit $C is not in the repository"; exit 1; }
LH=${GOV_REPIN_LINK_HOME:-$HOME}
P=${GOV_REPIN_PINS:-$HOME/.local/share/gov-os}
LINK=${GOV_REPIN_STORE_LINK:-$HOME/gov-os-worktrees/W2-00-store}
REG=${GOV_REPIN_REGISTRY_REPO:-$R}
HOLD=${GOV_REPIN_HOLD:-$R/.gov-runtime/scratch/orchestrator/log/act-in-progress.txt}
X=${GOV_REPIN_TMP:-/tmp/repin-$C}
HOOKS=${GOV_REPIN_HOOKS:-$R/.git/hooks}
GPU_LOCK=/tmp/gov-os-d4b-rebuild.lock
GPU_BEFORE=14000
GPU_STOP=15500
export GOV_REPIN_LINK_HOME=$LH GOV_REPIN_PINS=$P GOV_REPIN_REGISTRY_REPO=$REG
BIN=$LH/.local/bin
N=$P/pin-$C
W=$P/wheels/$C/gov-0.1.0-py3-none-any.whl
O=$R/.gov-runtime/scratch/orchestrator/pin
T=$R/.gov-runtime/scratch/orchestrator/tools
SMI=/usr/lib/wsl/lib/nvidia-smi
PREV=""; PHASE=before; HOOK_NEW=""; SVC_RESTARTED=""
mkdir -p "$X"

restore_store() {
  if [ -n "$PREV" ] && [ "$(readlink -f "$LINK")" != "$PREV" ]; then
    ( flock -w 600 9 && ln -sfn "$PREV" "$LINK.tmp" && mv -T "$LINK.tmp" "$LINK" ) 9>>"$LINK.lock" \
      && echo "the store link is back on $(basename "$PREV")" || echo "the store link could not be put back on $PREV"
  fi
}
svc_pid() { { bash "$T/tree_busy.sh" --cmd rerank_service.py 2> /dev/null || true; } | awk '/^BUSY/ && !s {s = $2} END {print s}'; }
restart_reranker() {  # class 3: stop the running service by its pid; a search through the current gov starts it again
  [ "${GOV_REPIN_SKIP_RERANK:-0}" = 1 ] && { echo "the reranker restart is skipped (rehearsal)"; return 0; }
  local s; s=$(svc_pid)
  if [ -n "$s" ]; then bash "$T/proc.sh" stop --grace 30 "$s" || return 1; fi
  (cd "$LINK" && GOV_RERANK_IDLE_S=43200 "$BIN/gov" retrieve "what decides a close" --json > "$X/restart.json" 2> /dev/null) || return 1
  printf '{"at": "%s", "class": 3, "reason": "re-pin window 4 (W2-112 changed the service)", "pid_before": "%s", "pid_after": "%s"}\n' \
    "$(date '+%F %T')" "$s" "$(svc_pid)" >> "$R/.gov-runtime/scratch/orchestrator/log/restarts.jsonl"
}
remove_hook() {
  if [ -n "$HOOK_NEW" ]; then
    rm -f "$HOOKS/reference-transaction"
    [ -e "$HOOKS/reference-transaction.before-w4" ] && mv "$HOOKS/reference-transaction.before-w4" "$HOOKS/reference-transaction"
    echo "the reference-transaction hook is removed"
  fi
}
stop() {
  trap - ERR; echo; echo "STOP: $1"; restore_store
  echo "Nothing was switched: $BIN/gov is still pin-$OLD. Tell the CTO."
  [ -e "$N" ] && echo "(to run this again later, the CTO says when: rm -rf $N)"
  exit 1
}
rollback() {
  trap - ERR
  ln -sfn "$P/pin-$OLD/bin/gov" "$BIN/gov.new" && mv -Tf "$BIN/gov.new" "$BIN/gov"; hash -r
  restore_store; remove_hook
  [ -n "$SVC_RESTARTED" ] && { restart_reranker && echo "the reranker is restarted from pin-$OLD" || echo "the reranker restart from pin-$OLD failed: tell the CTO"; }
  echo; echo "ROLLED BACK: $1"; echo "$BIN/gov -> $(readlink -f "$BIN/gov"). Tell the CTO."; exit 1
}
on_err() {
  case $PHASE in
    before) stop "a command failed at line $1 (above)";;
    switched) rollback "a command failed at line $1 (above)";;
    *) trap - ERR; echo; echo "FAILED after the live checks, at line $1: pin-$C is live and checked; the registry step did not finish. Tell the CTO."; exit 1;;
  esac
}
trap 'on_err $LINENO' ERR

echo "== 0. preconditions"
[ "$(readlink -f "$BIN/gov")" = "$(readlink -f "$P/pin-$OLD/bin/gov")" ] || stop "$BIN/gov is not pin-$OLD"
[ ! -e "$N" ] || stop "$N already exists"
[ -f "$HOLD" ] || stop "the CTO's hold ($HOLD) is not written"
case "$(readlink -f "$LINK")" in *-a|*-b) ;; *) stop "$LINK does not name W2-00-store-a or -b";; esac
git -C "$LINK" rev-parse HEAD >/dev/null || stop "the store $LINK is not a git tree"
[ -x "$SMI" ] || stop "nvidia-smi is not at $SMI"
[ -d "$HOOKS" ] || stop "the hooks folder $HOOKS is not there"
git -C "$R" show "$FULL:governance/project/rebuild.yaml" | grep -q '^integration_store:' || stop "rebuild.yaml at $C names no integration_store"
# The pool (W2-32 S11) is switched on in retrieval.yaml by the CTO's commit AFTER this act: pin-$OLD refuses a pool:
# key (CONFIG_INVALID), so it must not be in any tree the old pin reads before the switch.
if git -C "$R" show "$FULL:governance/project/retrieval.yaml" | grep -q '^pool:'; then
  stop "retrieval.yaml at $C already holds pool: (pin-$OLD would refuse it): the CTO switches it on after the act"
fi
echo "ok (gov -> pin-$OLD; store -> $(basename "$(readlink -f "$LINK")") at $(git -C "$LINK" rev-parse --short=12 HEAD))"

echo "== A. the wheel of $C, built twice from clean exports, checked against the dry run; its own environment"
for n in 1 2; do
  rm -rf "$X/src-$n" "$X/wheel-$n"; mkdir -p "$X/src-$n" "$X/wheel-$n"
  git -C "$R" archive "$FULL" | tar -x -C "$X/src-$n"
  SOURCE_DATE_EPOCH=$EPOCH python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w "$X/wheel-$n" "$X/src-$n" > /dev/null
done
a=$(sha256sum "$X/wheel-1/gov-0.1.0-py3-none-any.whl" | cut -d' ' -f1); b=$(sha256sum "$X/wheel-2/gov-0.1.0-py3-none-any.whl" | cut -d' ' -f1)
echo "build 1 $a"; echo "build 2 $b"
[ "$a" = "$b" ] || stop "the two builds differ"
[ "$a" = "$SHA" ] || stop "the wheel's sha256 is not the dry run's ($SHA)"
mkdir -p "$P/wheels/$C"
cp "$X/wheel-1/gov-0.1.0-py3-none-any.whl" "$W"
echo "$SHA  $W" | sha256sum -c -
python3 -m venv --system-site-packages "$N"
"$N/bin/python" -m pip install -q --no-deps --no-index "$W"
head -1 "$N/bin/gov"

echo "== S. the integration store rebuilt at $C in the spare half, by $C's own code; the link flips on success"
for job in measure.sh measure_rx.sh rebuild_slot.sh; do
  waited=0
  while bash "$T/tree_busy.sh" --cmd "$job" > /dev/null 2>&1; do
    [ $waited -lt 7200 ] || stop "a GPU job ($job) still runs after 2 hours"
    [ $((waited % 300)) = 0 ] && echo "waiting: $job runs (GPU work takes turns)"
    sleep 30; waited=$((waited + 30))
  done
done
used=$("$SMI" --query-gpu=memory.used --format=csv,noheader,nounits | head -1 | tr -d ' ')
echo "GPU before the rebuild: $used MiB used"
[ "$used" -le $GPU_BEFORE ] || stop "the GPU has $used MiB used, above $GPU_BEFORE: the rebuild waits (tell the CTO)"
PREV_CUR=$(readlink -f "$LINK")
t0=$(date +%s)
setsid flock -w 7200 -o "$GPU_LOCK" env -u SEED_REBUILD_CMD GOV_STORE_LINK="$LINK" GOV_STORE_REF="$FULL" \
  bash "$T/refresh_integration_store.sh" > "$X/refresh.out" 2>&1 < /dev/null &
rp=$!
peak=0; over=""
while kill -0 $rp 2>/dev/null; do
  u=$("$SMI" --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ') || u=0
  [ "${u:-0}" -gt $peak ] && peak=$u
  if [ -z "$over" ] && [ "${u:-0}" -gt $GPU_STOP ]; then over=$u; kill -TERM -- -$rp 2>/dev/null || true; fi
  sleep 2
done
rrc=0; wait $rp || rrc=$?
t1=$(date +%s)
cat "$X/refresh.out"
[ "$(readlink -f "$LINK")" != "$PREV_CUR" ] && PREV=$PREV_CUR
echo "the rebuild: exit $rrc, $((t1 - t0)) s wall, GPU peak $peak MiB"
[ -z "$over" ] || stop "the GPU reached $over MiB (above $GPU_STOP): the rebuild was stopped"
[ "$rrc" = 0 ] || stop "the store rebuild failed (exit $rrc)"
[ "$(git -C "$LINK" rev-parse HEAD)" = "$FULL" ] || stop "the store link does not name a half at $FULL"
echo "the store: $LINK -> $(basename "$(readlink -f "$LINK")") at $C"

echo "== B. every check before the switch, through $N by its path"
REPIN_OLD_PY="$P/pin-$OLD/bin/python" bash "$O/repin6_checks.sh" "$N" "$X/checks" "$LINK" "$FULL" | tee "$X/checks.txt" || true
tail -1 "$X/checks.txt" | grep -q '^ALL CHECKS PASS' || stop "a check before the switch failed (above)"

echo "== C. the quiet point"
for job in close_build.py nightly.sh "merge_queue.py run"; do
  if bash "$T/tree_busy.sh" --cmd "$job" > /dev/null 2>&1; then stop "a close, the nightly or a landing is running ($job)"; fi
done
svc=$(svc_pid)
if [ -n "$svc" ]; then
  file=$(tr '\0' '\n' < /proc/$svc/cmdline | grep 'rerank_service\.py$' | head -1)
  if cmp -s "$file" "$N/lib/python3.12/site-packages/gov/retrieval/rerank_service.py"; then
    echo "the shared reranker: pid $svc, the same bytes as the new pin's: no restart needed"; NEED_RESTART=0
  else
    echo "the shared reranker: pid $svc from $file differs from the new pin's (W2-112): restarted after the switch (class 3)"; NEED_RESTART=1
  fi
else
  echo "the shared reranker is not running: the first search starts it from the new pin"; NEED_RESTART=0
fi

echo "== D. the switch (an atomic rename), then the shared reranker restarted from the new pin"
PHASE=switched
ln -sfn "$N/bin/gov" "$BIN/gov.new" && mv -Tf "$BIN/gov.new" "$BIN/gov"; hash -r
[ "$(readlink -f "$BIN/gov")" = "$(readlink -f "$N/bin/gov")" ] || rollback "the link does not name pin-$C"
echo "$BIN/gov -> $(readlink -f "$BIN/gov")"
if [ "$NEED_RESTART" = 1 ]; then
  SVC_RESTARTED=1
  restart_reranker || rollback "the shared reranker did not restart from the new pin"
  if [ "${GOV_REPIN_SKIP_RERANK:-0}" != 1 ]; then
    s=$(svc_pid); [ -n "$s" ] || rollback "no shared reranker runs after the restart"
    f=$(tr '\0' '\n' < /proc/$s/cmdline | grep 'rerank_service\.py$' | head -1)
    case "$f" in "$N"/*) echo "the shared reranker: pid $s from the new pin";; *) rollback "the restarted reranker ($f) is not the new pin's";; esac
  fi
fi
smoke=$(bash "$O/smoke_repin5.sh" "$LH" "$X/smoke" 2>&1) || true; echo "$smoke"
{ grep -q '^1 Read README.md: exit 0' <<<"$smoke" && ! grep -q '^1 .*deny' <<<"$smoke"; } || rollback "the guard refused a plain Read"
grep -q '^2 Write tests/acceptance: exit 0; "permissionDecision": *"deny"' <<<"$smoke" \
  || grep -q '^2 Write tests/acceptance: exit 2' <<<"$smoke" || rollback "the guard did not refuse an acceptance-test write"
grep -q '^3 no judge reachable: exit 2' <<<"$smoke" || rollback "the guard did not refuse with no judge"
t0=$(date +%s.%N)
(cd "$LINK" && "$BIN/gov" retrieve "what decides a close" --json > "$X/search.json") || rollback "a search through the new pin failed"
t=$(echo "$(date +%s.%N) - $t0" | bc)
python3 -c "import json,sys; r=json.load(open(sys.argv[1]))['result']; f=r['facets']; sys.exit(0 if all(f[k]['available'] for k in ('lexical','semantic')) and (r.get('rerank') or {}).get('by') == 'service' else 1)" \
  "$X/search.json" || rollback "a search through the new pin lost a facet or the shared reranker"
echo "a search through $BIN/gov on the store: both facets available, rerank.by service, $t s"

echo "== H. W2-116's hook: the integration store refreshed after every update of w2/integrate"
[ -e "$HOOKS/reference-transaction" ] && mv "$HOOKS/reference-transaction" "$HOOKS/reference-transaction.before-w4"
cat > "$HOOKS/reference-transaction" <<'HOOK'
#!/bin/sh
# W2-116 (DEC-1087 (3)), installed by re-pin window 4: refresh the integration store after every landing on
# w2/integrate (does nothing at an unchanged head). F5: no inherited Python setting; F6: the refresh lock before the
# heavy slot; R2-F2: flock -o, so no child keeps the lock.
[ "$1" = committed ] || exit 0
grep -q ' refs/heads/w2/integrate$' || exit 0
setsid -f env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u GOV_REBUILD_LOCK sh -c 'cd /home/usain/Dynamic-Agentic-Engineering-OS && exec flock -o /home/usain/gov-os-worktrees/W2-00-store.refresh.lock bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh /home/usain/.local/bin/gov rebuild --integration w2/integrate' >> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/integration-store.log 2>&1 </dev/null
exit 0
HOOK
chmod +x "$HOOKS/reference-transaction"; HOOK_NEW=1
sh -n "$HOOKS/reference-transaction" || rollback "the hook does not parse"
"$BIN/gov" rebuild --help 2>&1 | grep -q -- '--integration' || rollback "the new pin's gov rebuild offers no --integration"
echo "the hook is installed; the new pin's gov rebuild offers --integration (its first run is the next merge's)"
PHASE=live

echo "== E. the registry entry (refuses unless A and D hold), committed as the owner's"
python3 "$O/repin6_registry.py" "$C" "$SHA" "$EPOCH"
git -C "$REG" commit -q -m "DEC-1087 (8): re-pin window 4, gov from the wheel of $C (W2-92, W2-32 S11 with the pool on, W2-131, W2-133, W2-112, W2-134, W2-135, W2-116 with its hook, W2-129; the store rebuilt; the reranker restarted)" \
  --trailer "Task: decision-record" --trailer "Implements: DEC-1087" --trailer "Role: owner" -- governance/project/tool-registry.yaml
echo "committed: $(git -C "$REG" log -1 --format='%h %s' | cut -c1-100)"
trap - ERR
echo; echo "RE-PIN DONE: pin-$C is live; pin-$OLD kept for the rollback; the store at $C; the reranker from the new pin; the hook installed. Tell the CTO."

# ---- Rollback by hand (if anything goes wrong after the switch) -------------------------------------------------------
#   ln -sfn ~/.local/share/gov-os/pin-8284fb408bd4/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
#   rm -f /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/reference-transaction
#   then the reranker: bash .../tools/proc.sh stop <its pid>; one gov retrieve starts it from the old pin. Revert the
#   registry commit.
