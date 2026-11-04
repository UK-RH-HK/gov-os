#!/usr/bin/env bash
# Re-pin window 3 (DEC-1068 (e)): the owner's act, by the owner's operator. gov from the wheel of w2/integrate's
# 8284fb408bd4 (the night of DEC-1067: W2-32's G1, S8 routing by question type and the phrasings, the reranker requests
# bounded at 16 texts and 24,000 padded characters, contextual headers when embedded, switched on in rebuild.yaml and
# retrieval.yaml), with the integration store re-embedded with headers at the same commit as part of it.
# Run in a PLAIN TERMINAL (not inside a Claude session: it reinstalls gov, DEC-928 item 3):
#     bash REPIN-COMMANDS-8284fb408bd4.sh 2>&1 | tee ~/repin-8284fb408bd4.log
# It stops at the first failure. Before the switch (parts 0, A, S, B, C) a failure prints STOP and leaves what sessions
# use as it was (the new pin sits beside the old one; the store link is put back on its old half). After the switch
# (part D) a failed check switches straight back to the old pin by itself and prints ROLLED BACK: then tell the CTO.
# Paths: the live ones by default; the operator sets none of the GOV_REPIN_* variables. The CTO's rehearsal
# (DEC-1057) points them at a scratch copy: GOV_REPIN_LINK_HOME (the HOME of .local/bin/gov), GOV_REPIN_PINS (the
# pins' folder), GOV_REPIN_STORE_LINK (the integration store's link), GOV_REPIN_REGISTRY_REPO (where the registry
# entry is committed), GOV_REPIN_HOLD (the CTO's hold file), GOV_REPIN_TMP (this run's scratch).
set -Eeuo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
C=8284fb408bd4              # w2/integrate's head on 2026-11-04 09:18 (DEC-1068 recorded)
FULL=$(git -C "$R" rev-parse --verify --quiet "$C^{commit}") || { echo "STOP: commit $C is not in the repository"; exit 1; }
EPOCH=1793783907           # the commit's time: the wheel is reproducible
SHA=82fbe15b2fccfe2c06872b6389a2ca8dc67c601d08efbf53e63801c41860c02e   # the CTO's dry run: two builds, the same bytes
OLD=9894b0cf
LH=${GOV_REPIN_LINK_HOME:-$HOME}
P=${GOV_REPIN_PINS:-$HOME/.local/share/gov-os}
LINK=${GOV_REPIN_STORE_LINK:-$HOME/gov-os-worktrees/W2-00-store}
REG=${GOV_REPIN_REGISTRY_REPO:-$R}
HOLD=${GOV_REPIN_HOLD:-$R/.gov-runtime/scratch/orchestrator/log/act-in-progress.txt}
X=${GOV_REPIN_TMP:-/tmp/repin-$C}
GPU_LOCK=/tmp/gov-os-d4b-rebuild.lock   # GPU work takes turns (DEC-1068 (4)): the night's rebuild lock
GPU_BEFORE=14000            # MiB used, at most, before the re-embed starts
GPU_STOP=15500              # MiB used: the re-embed is stopped (its own process group) past it
export GOV_REPIN_LINK_HOME=$LH GOV_REPIN_PINS=$P GOV_REPIN_REGISTRY_REPO=$REG
BIN=$LH/.local/bin
N=$P/pin-$C
W=$P/wheels/$C/gov-0.1.0-py3-none-any.whl
O=$R/.gov-runtime/scratch/orchestrator/pin
T=$R/.gov-runtime/scratch/orchestrator/tools
SMI=/usr/lib/wsl/lib/nvidia-smi
PREV=""                     # the store half the link named before the refresh, once the refresh flipped it
PHASE=before                # before | switched | live
mkdir -p "$X"

restore_store() {
  if [ -n "$PREV" ] && [ "$(readlink -f "$LINK")" != "$PREV" ]; then
    ( flock -w 600 9 && ln -sfn "$PREV" "$LINK.tmp" && mv -T "$LINK.tmp" "$LINK" ) 9>>"$LINK.lock" \
      && echo "the store link is back on $(basename "$PREV")" || echo "the store link could not be put back on $PREV"
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
  restore_store
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
[ "$(git -C "$R" rev-parse "$FULL^{commit}")" = "$FULL" ] || stop "commit $FULL is not in the repository"
[ -f "$HOLD" ] || stop "the CTO's hold ($HOLD) is not written"
case "$(readlink -f "$LINK")" in *-a|*-b) ;; *) stop "$LINK does not name W2-00-store-a or -b";; esac
git -C "$LINK" rev-parse HEAD >/dev/null || stop "the store $LINK is not a git tree"
[ -x "$SMI" ] || stop "nvidia-smi is not at $SMI"
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

echo "== S. the integration store re-embedded with headers at $C, in the spare half; the link flips on success"
for job in measure.sh measure_rx.sh rebuild_slot.sh; do
  waited=0
  while bash "$T/tree_busy.sh" --cmd "$job" > /dev/null 2>&1; do
    [ $waited -lt 7200 ] || stop "a GPU job ($job) still runs after 2 hours"
    [ $((waited % 300)) = 0 ] && echo "waiting: $job runs (GPU work takes turns)"
    sleep 30; waited=$((waited + 30))
  done
done
used=$("$SMI" --query-gpu=memory.used --format=csv,noheader,nounits | head -1 | tr -d ' ')
echo "GPU before the re-embed: $used MiB used"
[ "$used" -le $GPU_BEFORE ] || stop "the GPU has $used MiB used, above $GPU_BEFORE: the re-embed waits (tell the CTO)"
PREV_CUR=$(readlink -f "$LINK")
t0=$(date +%s)
setsid flock -w 7200 -o "$GPU_LOCK" env GOV_STORE_LINK="$LINK" GOV_STORE_REF="$FULL" \
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
echo "the refresh: exit $rrc, $((t1 - t0)) s wall (the lock's wait included), GPU peak $peak MiB"
[ -z "$over" ] || stop "the GPU reached $over MiB (above $GPU_STOP): the re-embed was stopped"
[ "$rrc" = 0 ] || stop "the store refresh failed (exit $rrc; ${GOV_STORE_LOG:-$R/.gov-runtime/scratch/orchestrator/log/integration-store.log}.err)"
[ "$(git -C "$LINK" rev-parse HEAD)" = "$FULL" ] || stop "the store link does not name a half at $FULL"
python3 - "${GOV_STORE_LOG:-$R/.gov-runtime/scratch/orchestrator/log/integration-store.log}.json" <<'EOF' || true
import json, sys
try:
    t = open(sys.argv[1]).read(); r = json.loads(t[t.index("{"):])["result"]
except (OSError, ValueError, KeyError):
    sys.exit(0)  # "fresh at": nothing was rebuilt
print("rebuild timing:", json.dumps(r.get("timing")))
s = (r.get("stores") or {}).get("semantic") or {}
print("semantic:", json.dumps({k: v for k, v in s.items() if not isinstance(v, list)})[:600])
EOF
echo "the store: $LINK -> $(basename "$(readlink -f "$LINK")") at $C"

echo "== B. every check before the switch, through $N by its path (the store's and the guard's included)"
REPIN_OLD_PY="$P/pin-$OLD/bin/python" bash "$O/repin5_checks.sh" "$N" "$X/checks" "$LINK" "$FULL" | tee "$X/checks.txt" || true
tail -1 "$X/checks.txt" | grep -q '^ALL CHECKS PASS' || stop "a check before the switch failed (above)"

echo "== C. the quiet point"
for job in close_build.py nightly.sh "merge_queue.py run"; do
  if bash "$T/tree_busy.sh" --cmd "$job" > /dev/null 2>&1; then stop "a close, the nightly or a landing is running ($job)"; fi
done
echo "processes of the old pin now (expected: the shared reranker service, and none or sub-second hooks; they finish"
echo "on the old code, which stays):"
bash "$T/tree_busy.sh" --cmd "$P/pin-$OLD" 2> /dev/null || true
svc=$({ bash "$T/tree_busy.sh" --cmd rerank_service.py 2> /dev/null || true; } | awk '/^BUSY/ && !s {s = $2} END {print s}')
if [ -n "$svc" ]; then
  file=$(tr '\0' '\n' < /proc/$svc/cmdline | grep 'rerank_service\.py$' | head -1)
  cmp -s "$file" "$N/lib/python3.12/site-packages/gov/retrieval/rerank_service.py" \
    || stop "the running reranker service's code ($file) differs from the new pin's: a class 3 restart would be needed (tell the CTO)"
  echo "the shared reranker: pid $svc from $file, the same bytes as the new pin's: it keeps serving, no restart"
else
  echo "the shared reranker is not running: the first search starts it from the new pin (class 3's start)"
fi
if (cd "$LINK" && "$P/pin-$OLD/bin/gov" retrieve "what decides a close" --json > "$X/old-search.json" 2> /dev/null) \
   && python3 -c "import json,sys; f=json.load(open(sys.argv[1]))['result']['facets']; sys.exit(0 if all(f[k]['available'] for k in ('lexical','semantic')) else 1)" "$X/old-search.json"; then
  echo "pin-$OLD on the new store: both facets available (a rollback needs only the gov link)"
else
  echo "NOTE: pin-$OLD does not search the new store with both facets: a rollback by hand also puts the store link back"
fi

echo "== D. the switch (an atomic rename: no moment without a gov)"
PHASE=switched
ln -sfn "$N/bin/gov" "$BIN/gov.new" && mv -Tf "$BIN/gov.new" "$BIN/gov"; hash -r
[ "$(readlink -f "$BIN/gov")" = "$(readlink -f "$N/bin/gov")" ] || rollback "the link does not name pin-$C"
echo "$BIN/gov -> $(readlink -f "$BIN/gov")"
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
PHASE=live

echo "== E. the registry entry (refuses unless A and D hold), committed as the owner's"
python3 "$O/repin5_registry.py" "$C" "$SHA" "$EPOCH"
git -C "$REG" commit -q -m "DEC-1068: re-pin window 3, gov from the wheel of $C (the night of DEC-1067: G1, S8 routing and phrasings, the padded reranker bound, contextual headers; the integration store re-embedded with headers)" \
  --trailer "Task: decision-record" --trailer "Implements: DEC-1068" --trailer "Role: owner" -- governance/project/tool-registry.yaml
echo "committed: $(git -C "$REG" log -1 --format='%h %s' | cut -c1-100)"
trap - ERR
echo; echo "RE-PIN DONE: pin-$C is live; pin-$OLD kept for the rollback; the store at $C with headers. Tell the CTO."

# ---- Rollback by hand (one step) --------------------------------------------------------------------------------------
#   ln -sfn ~/.local/share/gov-os/pin-9894b0cf/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
#   then revert the registry commit. The store stays at 8284fb408bd4 (pin-9894b0cf searches it with both facets: the
#   rehearsal checked it).
