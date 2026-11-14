#!/usr/bin/env bash
# Re-pin from release 0.1.0 (DEC-1178 (3); P-RELEASE-1 §6): the owner's act, by the owner's operator, after the owner
# made release 0.1.0 (§4: `gov release 0.1.0` at C, the record committed, the annotated tag v0.1.0 on the record commit).
# gov from the wheel of release 0.1.0: the commit C the release record names, built here twice and checked against the
# wheel sha256 the record states. Nothing is typed in by hand from the record: part R reads the tag and the record and
# stops unless they agree with the four values below, which the CTO's fill_release.sh wrote from the same tag (RL-1).
# The integration store is rebuilt at w2/integrate's head AT RUN TIME (the head is the record commit, or later record
# commits; the script stops if src/, pyproject.toml or anything else the wheel is built from differs between C and that
# head, RL-3), the shared reranker restarted from the new pin if its bytes changed (class 3). The git hooks are NOT
# touched: .git/hooks/reference-transaction refreshes the store through ~/.local/bin/gov and follows the new pin.
# Run in a PLAIN TERMINAL (not inside a Claude session: it reinstalls gov, DEC-928 item 3):
#     bash REPIN-COMMANDS-REL-0.1.0.sh 2>&1 | tee -ai ~/repin-rel-0.1.0.log
# (tee -a keeps an earlier run's log; -i keeps tee writing through a Ctrl-C, so the log shows what the script did then.)
# It stops at the first failure. A Ctrl-C, a TERM or a hang-up (a closed terminal) is handled as a failure of the part
# it lands in: before the switch, the store rebuild (if running) is stopped within seconds (60 s at most), the store
# link goes back, STOP; after it, ROLLED BACK. Before the switch (parts 0, R, A, S, B, C) a failure prints STOP and leaves what
# sessions use as it was (the new pin beside the old; the store link back on its old half). After the switch (parts D,
# H) a failed check switches straight back to the old pin, restarts the reranker from it, and prints ROLLED BACK: then
# tell the CTO.
# Paths: the live ones by default; the operator sets none of the GOV_REPIN_* variables. The CTO's rehearsal (DEC-1057)
# points them at a scratch copy: GOV_REPIN_LINK_HOME, GOV_REPIN_PINS, GOV_REPIN_STORE_LINK, GOV_REPIN_REGISTRY_REPO,
# GOV_REPIN_HOLD, GOV_REPIN_TMP, GOV_REPIN_HOOKS (only read here), GOV_REPIN_SKIP_RERANK=1 (the live service is not
# restarted; its bytes are compared), GOV_REPIN_RELEASE_REPO (where the tag and the record are read: a scratch clone
# holding a scratch release). GOV_REPIN_BRANCH and GOV_REPIN_INPUT_REPO exist for the negative runs of the frozen-src rule.
set -Eeuo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
BRANCH=${GOV_REPIN_BRANCH:-w2/integrate}   # GOV_REPIN_BRANCH and GOV_REPIN_INPUT_REPO: the rehearsal's negative runs only
INPUT_REPO=${GOV_REPIN_INPUT_REPO:-$R}
REL_REPO=${GOV_REPIN_RELEASE_REPO:-$R}
VERSION=0.1.0
TAG=v0.1.0
C=__C__                     # the release record's commit (12 digits): the tag's commit's parent
EPOCH=__EPOCH__             # C's commit time: the wheel is reproducible
SHA=__SHA__                 # the wheel sha256 the release record states
RECORD=__RECORD__           # the sha256 of docs/releases/0.1.0/manifest.json at the tag
OLD=797495bdfc70            # window 5's pin, live until this act
REL=docs/releases/$VERSION
case "$C$EPOCH$SHA$RECORD" in *__*) echo "STOP: the commit, epoch, wheel sha256 or record sha256 is not filled in (the CTO's fill_release.sh)"; exit 1;; esac
FULL=$(git -C "$R" rev-parse --verify --quiet "$C^{commit}") || { echo "STOP: commit $C is not in the repository"; exit 1; }
LH=${GOV_REPIN_LINK_HOME:-$HOME}
P=${GOV_REPIN_PINS:-$HOME/.local/share/gov-os}
LINK=${GOV_REPIN_STORE_LINK:-$HOME/gov-os-worktrees/W2-00-store}
REG=${GOV_REPIN_REGISTRY_REPO:-$R}
HOLD=${GOV_REPIN_HOLD:-$R/.gov-runtime/scratch/orchestrator/log/act-in-progress.txt}
X=${GOV_REPIN_TMP:-/tmp/repin-rel-$VERSION}
HOOKS=${GOV_REPIN_HOOKS:-$R/.git/hooks}
GPU_LOCK=/tmp/gov-os-d4b-rebuild.lock
GPU_BEFORE=14000
GPU_STOP=15500
export GOV_REPIN_LINK_HOME=$LH GOV_REPIN_PINS=$P GOV_REPIN_REGISTRY_REPO=$REG
BIN=$LH/.local/bin
N=$P/pin-$C
W=$P/wheels/$C/gov-0.1.0-py3-none-any.whl
O=$R/.gov-runtime/scratch/orchestrator/drafts/repin-rel-0.1.0
PIN_TOOLS=$R/.gov-runtime/scratch/orchestrator/pin
T=$R/.gov-runtime/scratch/orchestrator/tools
SMI=/usr/lib/wsl/lib/nvidia-smi
# What the wheel is built from: src/ (the packages and their package data) and pyproject.toml; and, should they ever
# appear, the files setuptools would also read from the export's root.
INPUTS=(src pyproject.toml setup.py setup.cfg MANIFEST.in ':(glob)LICEN[CS]E*' ':(glob)COPYING*' ':(glob)NOTICE*' ':(glob)AUTHORS*')
PREV=""; PHASE=before; SVC_RESTARTED=""; STOREREF=""; TAGC=""; PREV_CUR=""; rp=""; RP_STARTING=""
# An earlier run's folder is kept, moved aside with its time (its diagnostics), never removed.
if [ -e "$X" ]; then XOLD=$X.$(date +%Y%m%d-%H%M%S); mv -T "$X" "$XOLD" && echo "an earlier run's $X is kept as $XOLD"; fi
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
  printf '{"at": "%s", "class": 3, "reason": "re-pin from release %s (the service bytes changed since pin-%s)", "pid_before": "%s", "pid_after": "%s"}\n' \
    "$(date '+%F %T')" "$VERSION" "$OLD" "$s" "$(svc_pid)" >> "$R/.gov-runtime/scratch/orchestrator/log/restarts.jsonl"
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
# A Ctrl-C, a TERM or a hang-up (window 5's review F5, this act's F7; review r2 F1). The store refresh of part S runs in
# its own session (setsid), so a Ctrl-C does not reach it: it is stopped here by its process group (TERM), polled every
# half second until no live process is left in it, KILLed after 60 s; if it moved the store link, the link goes back
# (restore_store). Then as a failure of the phase: STOP, or ROLLED BACK. No watchdog process: the handler polls.
grp_alive() { ps -o stat= -g "$1" 2> /dev/null | awk '$1 !~ /^Z/ {n++} END {exit n ? 0 : 1}'; }  # a live member left
on_signal() {  # $1 the signal
  trap - ERR; trap '' INT TERM HUP PIPE; set +e
  # The refresh's pid, also when the signal came between its start and `rp=$!` (review r2 F5): $! is set as soon as
  # the background job is forked; RP_STARTING says that job is the refresh.
  if [ -z "$rp" ] && [ -n "$RP_STARTING" ]; then rp=${!:-}; fi
  if [ -n "$rp" ]; then
    kill -TERM -- "-$rp" 2> /dev/null
    local n=0  # TERM again at each poll: a signal right after the fork can come before the child's setsid made the group
    while grp_alive "$rp" && [ $n -lt 120 ]; do sleep 0.5; n=$((n + 1)); kill -TERM -- "-$rp" 2> /dev/null; done
    if grp_alive "$rp"; then kill -KILL -- "-$rp" 2> /dev/null; sleep 0.5; fi
    wait "$rp" 2> /dev/null
    echo; echo "the store refresh (pid $rp, its process group) was stopped, $((n / 2)) s after the signal$(grp_alive "$rp" && echo ', BUT A PROCESS OF IT IS STILL LIVE: tell the CTO')"
  fi
  if [ -z "$PREV" ] && [ -n "$PREV_CUR" ] && [ "$(readlink -f "$LINK")" != "$PREV_CUR" ]; then PREV=$PREV_CUR; fi
  case $PHASE in
    before) stop "interrupted ($1) before the switch";;
    switched) rollback "interrupted ($1) after the switch";;
    *) echo; echo "INTERRUPTED ($1) after the live checks: pin-$C is live and checked; the registry step may not have finished. Tell the CTO."; exit 1;;
  esac
}
trap 'on_signal INT' INT
trap 'on_signal TERM' TERM
trap 'on_signal HUP' HUP

# The frozen-src rule (RL-3): the wheel is built from C's clean export, so nothing it is built from may differ between C
# and the branch's head now (the CTO's hold keeps src/ still from "release ready" to this act; record commits go on),
# nor in the main tree's own files.
same_inputs() {  # $1 where it is checked (for the message)
  local head; head=$(git -C "$INPUT_REPO" rev-parse --verify --quiet "$BRANCH^{commit}") || stop "$BRANCH does not exist ($1)"
  git -C "$INPUT_REPO" merge-base --is-ancestor "$FULL" "$head" || stop "$C is not in $BRANCH's history any more ($1): $BRANCH was moved off the release"
  if ! git -C "$INPUT_REPO" diff --quiet "$FULL" "$head" -- "${INPUTS[@]}"; then
    echo "what differs between $C and $BRANCH (${head:0:12}):"; git -C "$INPUT_REPO" diff --stat "$FULL" "$head" -- "${INPUTS[@]}" | tail -8
    stop "src/, pyproject.toml or another input of the wheel differs between $C and $BRANCH ($1): the pin would not be the release; the CTO decides (a new release, 0.1.1)"
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
[ -x "$HOOKS/reference-transaction" ] || stop "$HOOKS/reference-transaction is not there or not executable (window 4 installed it)"
sh -n "$HOOKS/reference-transaction" || stop "the reference-transaction hook does not parse"
grep -q 'gov rebuild --integration w2/integrate' "$HOOKS/reference-transaction" || stop "the reference-transaction hook does not refresh the integration store"
same_inputs "at the start"
[ "$(git -C "$REG" rev-parse --abbrev-ref HEAD)" = w2/integrate ] || stop "the tree $REG is not on w2/integrate (the registry commit would land elsewhere)"
[ -z "$(git -C "$REG" status --porcelain -- governance/project/tool-registry.yaml)" ] || stop "$REG/governance/project/tool-registry.yaml has uncommitted changes (the owner's commit would carry them)"
git -C "$INPUT_REPO" show "$HEADRT:governance/project/rebuild.yaml" | grep -q '^integration_store:' || stop "rebuild.yaml at $BRANCH names no integration_store"
echo "ok (gov -> pin-$OLD; store -> $(basename "$(readlink -f "$LINK")") at $(git -C "$LINK" rev-parse --short=12 HEAD); $BRANCH at ${HEADRT:0:12}, $C and it the same wheel inputs; the hook is only read)"

echo "== R. release $VERSION: the tag $TAG and its record, checked against the values filled in (RL-1)"
[ "$(git -C "$REL_REPO" cat-file -t "refs/tags/$TAG" 2>/dev/null)" = tag ] || stop "$TAG is not an annotated tag in $REL_REPO (§4 step 6: git tag -a)"
TAGC=$(git -C "$REL_REPO" rev-parse --verify --quiet "$TAG^{commit}") || stop "$TAG names no commit"
parents=$(git -C "$REL_REPO" rev-list --parents -n 1 "$TAGC" | wc -w)
[ "$parents" = 2 ] || stop "$TAG's commit ${TAGC:0:12} is not a commit with one parent (a merge, or the root)"
[ "$(git -C "$REL_REPO" rev-parse "$TAGC^")" = "$FULL" ] || stop "$TAG is not on the record commit whose parent is $C (it is on ${TAGC:0:12}, parent $(git -C "$REL_REPO" rev-parse --short=12 "$TAGC^")): §4 step 6 tags the record commit"
changed=$(git -C "$REL_REPO" diff --name-only "$FULL" "$TAGC" | sort | tr '\n' ' ')
[ "$changed" = "$REL/manifest.json $REL/manifest.sha256 " ] || stop "between $C and $TAG more than the release record changed: $changed"
mkdir -p "$X/release/$REL"
git -C "$REL_REPO" show "$TAGC:$REL/manifest.json" > "$X/release/$REL/manifest.json"
git -C "$REL_REPO" show "$TAGC:$REL/manifest.sha256" > "$X/release/$REL/manifest.sha256"
(cd "$X/release/$REL" && sha256sum -c --strict manifest.sha256) || stop "the record's manifest.json does not match its manifest.sha256"
rec=$(sha256sum < "$X/release/$REL/manifest.json" | cut -d' ' -f1)
[ "$rec" = "$RECORD" ] || stop "the record's manifest.json has sha256 $rec, not the one filled in ($RECORD)"
why=$(python3 - "$X/release/$REL/manifest.json" "$VERSION" "$FULL" "$SHA" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
w = m.get("wheel") or {}
bad = []
if m.get("version") != sys.argv[2]: bad.append(f"version {m.get('version')!r}")
if m.get("commit") != sys.argv[3]: bad.append(f"commit {m.get('commit')!r}")
if m.get("cli_version") != "0.1.0": bad.append(f"cli_version {m.get('cli_version')!r}")
if w.get("name") != "gov-0.1.0-py3-none-any.whl": bad.append(f"wheel name {w.get('name')!r}")
if w.get("sha256") != sys.argv[4]: bad.append(f"the manifest's wheel sha256 {w.get('sha256')!r} is not the one filled in")
print("; ".join(bad))
EOF
) || stop "the record's manifest.json cannot be read"
[ -z "$why" ] || stop "the record does not name what was filled in: $why"
[ "$(git -C "$R" show -s --format=%ct "$FULL")" = "$EPOCH" ] || stop "EPOCH $EPOCH is not $C's commit time"
# The record's own check, by the release code of the old pin (the code `gov release` ran): the shipped template/ files
# at the tag hash to the record's list.
git -C "$REL_REPO" archive "$TAGC" template | tar -x -C "$X/release"
"$P/pin-$OLD/bin/python" -E -c 'import sys; from pathlib import Path; from gov.release import verify; d, h = verify(Path(sys.argv[1]), sys.argv[2]); print("verify:", h)' \
  "$X/release" "$VERSION" || stop "the record's own check (gov.release.verify) refuses the tag's tree"
if [ "$REL_REPO" = "$INPUT_REPO" ]; then
  git -C "$REL_REPO" merge-base --is-ancestor "$TAGC" "$HEADRT" || stop "$TAG's commit is not in $BRANCH's history (§4 commits the record on w2/integrate)"
fi
echo "ok ($TAG -> ${TAGC:0:12}, parent $C; the record only; manifest.sha256 holds; record sha256 ${RECORD:0:12}; version, commit, cli_version, wheel name and sha256 as filled in; verify holds)"

echo "== A. the wheel of $C, built twice from clean exports, checked against the release record's sha256; its own environment"
for n in 1 2; do
  rm -rf "$X/src-$n" "$X/wheel-$n"; mkdir -p "$X/src-$n" "$X/wheel-$n"
  git -C "$R" archive "$FULL" | tar -x -C "$X/src-$n"
  SOURCE_DATE_EPOCH=$EPOCH python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w "$X/wheel-$n" "$X/src-$n" > /dev/null
done
a=$(sha256sum "$X/wheel-1/gov-0.1.0-py3-none-any.whl" | cut -d' ' -f1); b=$(sha256sum "$X/wheel-2/gov-0.1.0-py3-none-any.whl" | cut -d' ' -f1)
echo "build 1 $a"; echo "build 2 $b"
[ "$a" = "$b" ] || stop "the two builds differ"
[ "$a" = "$SHA" ] || stop "the wheel's sha256 is not the release record's ($SHA)"
mkdir -p "$P/wheels/$C"
cp "$X/wheel-1/gov-0.1.0-py3-none-any.whl" "$W"
echo "$SHA  $W" | sha256sum -c -
python3 -m venv --system-site-packages "$N"
"$N/bin/python" -m pip install -q --no-deps --no-index "$W"
head -1 "$N/bin/gov"

echo "== S. the integration store rebuilt at $BRANCH's head in the spare half, by the code of $C (the same bytes as that head's); the link flips on success"
same_inputs "before the rebuild"
STOREREF=$HEADRT
# --force: the hook keeps the store at the branch's head, so a plain refresh would answer "fresh" and leave the store
# built by the OLD pin's code. The act wants the store built by the new code (which the checks then search).
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
RP_STARTING=1   # from here the trap takes $! as the refresh's pid, should it come before the next line
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
rp=""; RP_STARTING=""
t1=$(date +%s)
cat "$X/refresh.out"
[ "$(readlink -f "$LINK")" != "$PREV_CUR" ] && PREV=$PREV_CUR
echo "the rebuild: exit $rrc, $((t1 - t0)) s wall, GPU peak $peak MiB"
[ -z "$over" ] || stop "the GPU reached $over MiB (above $GPU_STOP): the rebuild was stopped"
[ "$rrc" = 0 ] || stop "the store rebuild failed (exit $rrc)"
[ "$(git -C "$LINK" rev-parse HEAD)" = "$STOREREF" ] || stop "the store link does not name a half at ${STOREREF:0:12}"
echo "the store: $LINK -> $(basename "$(readlink -f "$LINK")") at ${STOREREF:0:12} ($BRANCH's head)"

echo "== B. every check before the switch, through $N by its path"
REPIN_OLD_PY="$P/pin-$OLD/bin/python" bash "$O/rel_checks.sh" "$N" "$X/checks" "$LINK" "$STOREREF" | tee "$X/checks.txt" || true
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
    echo "the shared reranker: pid $svc from $file differs from the new pin's: restarted after the switch (class 3)"; NEED_RESTART=1
  fi
else
  echo "the shared reranker is not running: the first search starts it from the new pin"; NEED_RESTART=0
fi

echo "== D. the switch (an atomic rename), then the shared reranker restarted from the new pin if its bytes changed"
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
smoke=$(bash "$PIN_TOOLS/smoke_repin5.sh" "$LH" "$X/smoke" 2>&1) || true; echo "$smoke"
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
# P-RELEASE-1 §5's two added lines: the pin is the release's wheel, and the gov link names it.
[ "$(sha256sum < "$W" | cut -d' ' -f1)" = "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["wheel"]["sha256"])' "$X/release/$REL/manifest.json")" ] \
  || rollback "the installed wheel's sha256 is not the release record's"
case "$(readlink -f "$BIN/gov")" in */pin-$C/bin/gov) ;; *) rollback "readlink -f $BIN/gov does not name pin-$C";; esac
echo "release check: the wheel's sha256 = the record's ($SHA); readlink -f $BIN/gov names pin-$C"
ghelp=$("$BIN/gov" --help 2>&1) || rollback "gov --help through the new pin failed"
grep -qE '^ +adapters ' <<<"$ghelp" && grep -qE '^ +wait ' <<<"$ghelp" || rollback "the new pin's gov lists no adapters or no wait (P-2)"
echo "gov adapters and gov wait are there (P-2)"

echo "== H. W2-116's hook (window 4's, with the later ACTs' lines; not rewritten): it refreshes the store through the new pin"
sh -n "$HOOKS/reference-transaction" || rollback "the hook does not parse"
grep -q '/\.local/bin/gov rebuild --integration w2/integrate' "$HOOKS/reference-transaction" || rollback "the hook does not refresh through the gov link (~/.local/bin/gov)"
"$BIN/gov" rebuild --help 2>&1 | grep -q -- '--integration' || rollback "the new pin's gov rebuild offers no --integration"
echo "the hook is unchanged and refreshes through the gov link, now the new pin; the new pin's gov rebuild offers --integration"
PHASE=live

echo "== E. the registry entry (refuses unless R, A and D hold), committed as the owner's"
python3 "$O/rel_registry.py" "$C" "$SHA" "$EPOCH" "$VERSION" "$TAG" "$RECORD"
git -C "$REG" commit -q -F - --trailer "Task: decision-record" --trailer "Implements: DEC-1178" --trailer "Role: owner" \
  -- governance/project/tool-registry.yaml <<EOF
DEC-1178 (3): re-pin from release $VERSION, gov from the release's wheel (tag $TAG, commit $C, record sha256 ${RECORD:0:12})

The wheel built twice from $C equals the release record's sha256; the store rebuilt at ${STOREREF:0:12}; the hooks not touched.
EOF
echo "committed: $(git -C "$REG" log -1 --format='%h %s' | cut -c1-100)"
trap - ERR
echo; echo "RE-PIN DONE: pin-$C (release $VERSION) is live; pin-$OLD kept for the rollback; the store at ${STOREREF:0:12}; the hooks untouched. Tell the CTO."

# ---- Rollback by hand (if anything goes wrong after the switch) -------------------------------------------------------
#   ln -sfn ~/.local/share/gov-os/pin-797495bdfc70/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
#   then, only if part D restarted the reranker: bash .../tools/proc.sh stop <its pid>; one gov retrieve starts it from
#   the old pin. Revert the registry commit. (No hook to remove: this act wrote none.)
