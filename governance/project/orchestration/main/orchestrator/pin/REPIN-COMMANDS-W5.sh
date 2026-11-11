#!/usr/bin/env bash
# Re-pin window 5, the lift's (DEC-1125 (3) (i)): the owner's act, by the owner's operator. gov from the wheel of
# w2/integrate's commit C below, which carries every build since window 4's pin (bcea09060ebc): W2-20 (the resource gate,
# gov resources, the heavy-job slots), W2-56 (gov launch on the guard alone), W2-136 (gov plan), W2-152 (gov brief),
# W2-153 (the role template at launch), W2-141 (the guard's rule on an engineer's wide search), W2-145 (no private
# reranker), W2-137 (the reranker's request cap 64), W2-138 (the store's commit and folder in every search result),
# W2-150 (the gov.util modules), W2-96 (gov accept's opt-in suites), D-6 part 2 (W2-92, W2-129, W2-55).
# The integration store is rebuilt at w2/integrate's head AT RUN TIME (records may have moved since C; the script stops
# if src/, pyproject.toml or anything else the wheel is built from differs between C and that head, so the code that
# builds the store is C's own), the shared reranker restarted from the new pin (class 3, since W2-145 and W2-137
# changed its service). The git hooks are NOT touched: window 4 installed .git/hooks/reference-transaction, later ACTs
# (ACT-OPERATOR-1, ACT-SELECT-HOOK-1) added to it, and it refreshes the store through ~/.local/bin/gov, so it follows
# the new pin by itself.
# Run in a PLAIN TERMINAL (not inside a Claude session: it reinstalls gov, DEC-928 item 3):
#     bash REPIN-COMMANDS-W5.sh 2>&1 | tee ~/repin-w5.log
# It stops at the first failure. Before the switch (parts 0, A, S, B, C) a failure prints STOP and leaves what sessions
# use as it was (the new pin beside the old; the store link back on its old half). After the switch (parts D, H) a
# failed check switches straight back to the old pin, restarts the reranker from it, and prints ROLLED BACK: then tell
# the CTO.
# Paths: the live ones by default; the operator sets none of the GOV_REPIN_* variables. The CTO's rehearsal (DEC-1057)
# points them at a scratch copy: GOV_REPIN_LINK_HOME, GOV_REPIN_PINS, GOV_REPIN_STORE_LINK, GOV_REPIN_REGISTRY_REPO,
# GOV_REPIN_HOLD, GOV_REPIN_TMP, GOV_REPIN_HOOKS (the hooks folder, only read here), GOV_REPIN_SKIP_RERANK=1 (the
# rehearsal does not restart the live service; it checks the bytes only). GOV_REPIN_BRANCH and GOV_REPIN_INPUT_REPO
# (a scratch clone with a branch whose src/ differs) exist for the rehearsal's negative run of the frozen-src rule.
set -Eeuo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
BRANCH=${GOV_REPIN_BRANCH:-w2/integrate}   # GOV_REPIN_BRANCH and GOV_REPIN_INPUT_REPO: the rehearsal's negative runs only
INPUT_REPO=${GOV_REPIN_INPUT_REPO:-$R}
C=797495bdfc70              # w2/integrate's head on 2026-11-11 01:08 UTC, the lift's candidate (src/ frozen from then)
EPOCH=1794359304            # the commit's time: the wheel is reproducible
SHA=04b094fbd587869036aea6ac1e4af2f86d1254fb484d71826c66ed1bc077d7c3   # the CTO's dry run: two builds, the same bytes
OLD=bcea09060ebc
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
# What the wheel is built from: src/ (the packages and their package data) and pyproject.toml; and, should they ever
# appear, the files setuptools would also read from the export's root.
INPUTS=(src pyproject.toml setup.py setup.cfg MANIFEST.in ':(glob)LICEN[CS]E*' ':(glob)COPYING*' ':(glob)NOTICE*' ':(glob)AUTHORS*')
PREV=""; PHASE=before; SVC_RESTARTED=""; STOREREF=""
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
  printf '{"at": "%s", "class": 3, "reason": "re-pin window 5 (W2-145 and W2-137 changed the service)", "pid_before": "%s", "pid_after": "%s"}\n' \
    "$(date '+%F %T')" "$s" "$(svc_pid)" >> "$R/.gov-runtime/scratch/orchestrator/log/restarts.jsonl"
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
  restore_store
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

# The frozen-src rule: the wheel is built from C's clean export, so nothing it is built from may differ between C and
# the branch's head now (the CTO freezes src/ for the night; record commits go on), nor in the main tree's own files.
same_inputs() {  # $1 where it is checked (for the message)
  local head; head=$(git -C "$INPUT_REPO" rev-parse --verify --quiet "$BRANCH^{commit}") || stop "$BRANCH does not exist ($1)"
  git -C "$INPUT_REPO" merge-base --is-ancestor "$FULL" "$head" || stop "$C is not in $BRANCH's history any more ($1): $BRANCH was moved off the candidate"
  if ! git -C "$INPUT_REPO" diff --quiet "$FULL" "$head" -- "${INPUTS[@]}"; then
    echo "what differs between $C and $BRANCH (${head:0:12}):"; git -C "$INPUT_REPO" diff --stat "$FULL" "$head" -- "${INPUTS[@]}" | tail -8
    stop "src/, pyproject.toml or another input of the wheel differs between $C and $BRANCH ($1): the wheel would not be what the tree holds; the CTO decides a new candidate"
  fi
  if [ -n "$(git -C "$INPUT_REPO" status --porcelain --untracked-files=no -- src pyproject.toml)" ]; then
    stop "the tree has uncommitted changes in src/ or pyproject.toml ($1)"
  fi
  HEADRT=$head
}

echo "== 0. preconditions"
[ "$(readlink -f "$BIN/gov")" = "$(readlink -f "$P/pin-$OLD/bin/gov")" ] || stop "$BIN/gov is not pin-$OLD"
"$P/pin-$OLD/bin/gov" --help > /dev/null 2>&1 || stop "pin-$OLD does not run (the rollback needs it)"
[ ! -e "$N" ] || stop "$N already exists"
[ -f "$HOLD" ] || stop "the CTO's hold ($HOLD) is not written"
case "$(readlink -f "$LINK")" in *-a|*-b) ;; *) stop "$LINK does not name W2-00-store-a or -b";; esac
git -C "$LINK" rev-parse HEAD >/dev/null || stop "the store $LINK is not a git tree"
[ -x "$SMI" ] || stop "nvidia-smi is not at $SMI"
[ -d "$HOOKS" ] || stop "the hooks folder $HOOKS is not there"
# The hook is window 4's, with later ACTs' lines: this script only reads it. It must be there, parse, and refresh the
# store through the gov link (so the new pin runs it after the switch).
[ -x "$HOOKS/reference-transaction" ] || stop "$HOOKS/reference-transaction is not there or not executable (window 4 installed it)"
sh -n "$HOOKS/reference-transaction" || stop "the reference-transaction hook does not parse"
grep -q 'gov rebuild --integration w2/integrate' "$HOOKS/reference-transaction" || stop "the reference-transaction hook does not refresh the integration store"
same_inputs "at the start"
# The owner's registry commit (part E) is path-limited, but it must not carry the CTO's unfinished edit, and it lands on
# whatever branch the tree is on: that must be w2/integrate.
[ "$(git -C "$REG" rev-parse --abbrev-ref HEAD)" = w2/integrate ] || stop "the tree $REG is not on w2/integrate (the registry commit would land elsewhere)"
[ -z "$(git -C "$REG" status --porcelain -- governance/project/tool-registry.yaml)" ] || stop "$REG/governance/project/tool-registry.yaml has uncommitted changes (the owner's commit would carry them)"
git -C "$INPUT_REPO" show "$HEADRT:governance/project/rebuild.yaml" | grep -q '^integration_store:' || stop "rebuild.yaml at $BRANCH names no integration_store"
echo "ok (gov -> pin-$OLD; store -> $(basename "$(readlink -f "$LINK")") at $(git -C "$LINK" rev-parse --short=12 HEAD); $BRANCH at ${HEADRT:0:12}, $C and it the same wheel inputs; the hook is only read)"

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

echo "== S. the integration store rebuilt at $BRANCH's head in the spare half, by the code of $C (the same bytes as that head's); the link flips on success"
same_inputs "before the rebuild"
STOREREF=$HEADRT
# --force: since window 4's hook keeps the store at the branch's head, the ready half is usually at it already, and a
# plain refresh would answer "fresh" and leave the store built by the OLD pin's code. The act wants the store built by
# the new code (which the checks then search), so the spare half is rebuilt at that head regardless.
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
setsid flock -w 7200 -o "$GPU_LOCK" env -u SEED_REBUILD_CMD GOV_STORE_LINK="$LINK" GOV_STORE_REF="$STOREREF" \
  bash "$T/refresh_integration_store.sh" --force > "$X/refresh.out" 2>&1 < /dev/null &
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
[ "$(git -C "$LINK" rev-parse HEAD)" = "$STOREREF" ] || stop "the store link does not name a half at ${STOREREF:0:12}"
echo "the store: $LINK -> $(basename "$(readlink -f "$LINK")") at ${STOREREF:0:12} ($BRANCH's head)"

echo "== B. every check before the switch, through $N by its path"
REPIN_OLD_PY="$P/pin-$OLD/bin/python" bash "$O/repin7_checks.sh" "$N" "$X/checks" "$LINK" "$STOREREF" | tee "$X/checks.txt" || true
tail -1 "$X/checks.txt" | grep -q '^ALL CHECKS PASS' || stop "a check before the switch failed (above)"

echo "== C. the quiet point"
for job in close_build.py nightly.sh "merge_queue.py run"; do
  if bash "$T/tree_busy.sh" --cmd "$job" > /dev/null 2>&1; then stop "a close, the nightly or a landing is running ($job)"; fi
done
same_inputs "at the quiet point"
svc=$(svc_pid)
if [ -n "$svc" ]; then
  file=$(tr '\0' '\n' < /proc/$svc/cmdline | grep 'rerank_service\.py$' | head -1)
  if cmp -s "$file" "$N/lib/python3.12/site-packages/gov/retrieval/rerank_service.py"; then
    echo "the shared reranker: pid $svc, the same bytes as the new pin's: no restart needed"; NEED_RESTART=0
  else
    echo "the shared reranker: pid $svc from $file differs from the new pin's (W2-145, W2-137): restarted after the switch (class 3)"; NEED_RESTART=1
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
python3 -c "import json,sys; r=json.load(open(sys.argv[1]))['result']; f=r['facets']; sys.exit(0 if all(f[k]['available'] for k in ('lexical','semantic')) and (r.get('rerank') or {}).get('by') == 'service' and (r.get('store') or {}).get('commit') == sys.argv[2] else 1)" \
  "$X/search.json" "$STOREREF" || rollback "a search through the new pin lost a facet or the shared reranker, or does not name the store's commit"
echo "a search through $BIN/gov on the store: both facets available, rerank.by service, the store's commit named, $t s"

echo "== H. W2-116's hook (window 4's, with the later ACTs' lines; not rewritten): it refreshes the store through the new pin"
sh -n "$HOOKS/reference-transaction" || rollback "the hook does not parse"
grep -q '/\.local/bin/gov rebuild --integration w2/integrate' "$HOOKS/reference-transaction" || rollback "the hook does not refresh through the gov link (~/.local/bin/gov)"
"$BIN/gov" rebuild --help 2>&1 | grep -q -- '--integration' || rollback "the new pin's gov rebuild offers no --integration"
echo "the hook is unchanged and refreshes through the gov link, now the new pin; the new pin's gov rebuild offers --integration (its first run is the next landing's: the registry commit below)"
PHASE=live

echo "== E. the registry entry (refuses unless A and D hold), committed as the owner's"
python3 "$O/repin7_registry.py" "$C" "$SHA" "$EPOCH"
git -C "$REG" commit -q -m "DEC-1125 (3): re-pin window 5, gov from the wheel of $C (W2-20, W2-56, W2-136, W2-152, W2-153, W2-141, W2-145, W2-137, W2-138, W2-150, W2-96, D-6 part 2; the store rebuilt; the reranker restarted; the hooks not touched)" \
  --trailer "Task: decision-record" --trailer "Implements: DEC-1125" --trailer "Role: owner" -- governance/project/tool-registry.yaml
echo "committed: $(git -C "$REG" log -1 --format='%h %s' | cut -c1-100)"
trap - ERR
echo; echo "RE-PIN DONE: pin-$C is live; pin-$OLD kept for the rollback; the store at ${STOREREF:0:12}; the reranker from the new pin; the hooks untouched. Tell the CTO."

# ---- Rollback by hand (if anything goes wrong after the switch) -------------------------------------------------------
#   ln -sfn ~/.local/share/gov-os/pin-bcea09060ebc/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
#   then the reranker: bash .../tools/proc.sh stop <its pid>; one gov retrieve starts it from the old pin. Revert the
#   registry commit. (No hook to remove: this act wrote none.)
