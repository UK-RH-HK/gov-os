#!/usr/bin/env bash
# The rehearsal of re-pin window 5 (DEC-1057: every ACT rehearsed end to end before the hand-over), changing nothing
# live: REPIN-COMMANDS-W5.sh runs as the operator will, but with its GOV_REPIN_* paths in a scratch mirror:
#   <S>/home/.local/bin/gov -> <S>/home/.local/share/gov-os/pin-bcea09060ebc/bin/gov (that folder a link to the live
#   pin, only read); <S>/home/gov-os-worktrees/W2-00-store{-a,-b} shared clones of the main tree at the live halves'
#   commits with copies of their stores (SQLite's backup; the live halves only read), the link on the live one;
#   <S>/repo a shared clone for the registry commit; <S>/hold the CTO's hold; <S>/hooks a scratch hooks folder holding a
#   copy of the live reference-transaction hook (the live .git/hooks is never touched; the script only reads it now);
#   GOV_REPIN_SKIP_RERANK=1: the live shared reranker is not restarted (part C still compares its bytes with the new
#   pin's, and part D still searches through it).
# The real HOME stays: the shared reranker's socket and the machine-wide vector cache are the operator's.
# Before and after, the live paths are recorded. Two groups: what only a re-pin could change (the gov link and its
# script, the pins and wheels, the hook, the registry file, the reranker's pid) must be UNCHANGED; what moves with the
# CTO's own landings on w2/integrate (the live hook refreshes the live store after each: the store link, its halves, the
# heads) is shown, and compared strictly only if the head did not move during the run.
#     bash rehearse_repin7.sh [<scratch dir, default /tmp/gov-os-emg-repin5/r>] [run | neg-src | neg-uncommitted | neg-check]
# run (default): the whole script, expecting exit 0. The negative runs expect a STOP, with nothing switched:
#   neg-src          a branch whose src/ differs from the candidate (the frozen-src rule, part 0);
#   neg-uncommitted  an uncommitted change in src/ (part 0);
#   neg-check        a check of part B fails after the store was rebuilt and its link flipped (the staged W2-141 hook
#                    names a gov module the pin lacks): the store link must be put back.
set -euo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
O=$R/.gov-runtime/scratch/orchestrator/pin
S=${1:-/tmp/gov-os-emg-repin5/r}
MODE=${2:-run}
LIVE=/home/usain/gov-os-worktrees
LIVEPINS=/home/usain/.local/share/gov-os
OLD=bcea09060ebc
[ ! -e "$S" ] || { echo "$S exists: remove it first"; exit 2; }
live_fixed() {
  echo "gov link: $(readlink /home/usain/.local/bin/gov) -> $(readlink -f /home/usain/.local/bin/gov)"
  echo "gov script sha256: $(sha256sum < "$(readlink -f /home/usain/.local/bin/gov)" | cut -c1-12)"
  echo "pins: $(ls $LIVEPINS | tr '\n' ' ')"
  echo "pin dirs sha256 of their gov scripts: $(for p in $LIVEPINS/pin-*; do printf '%s:%s ' "$(basename "$p")" "$(sha256sum < "$p/bin/gov" | cut -c1-8)"; done)"
  echo "wheels: $(ls $LIVEPINS/wheels | tr '\n' ' ')"
  echo "hooks: $(ls $R/.git/hooks | grep -v '\.sample$' | tr '\n' ' ')"
  echo "hook reference-transaction sha256: $(sha256sum < $R/.git/hooks/reference-transaction | cut -c1-12)"
  echo "registry file sha256: $(sha256sum < $R/governance/project/tool-registry.yaml | cut -c1-12)"
  echo "shared reranker pid: $(bash $R/.gov-runtime/scratch/orchestrator/tools/tree_busy.sh --cmd rerank_service.py 2>/dev/null | awk '/^BUSY/ && !s {s = $2} END {print s}')"
}
live_moves() {
  echo "store link: $(readlink $LIVE/W2-00-store) -> $(readlink -f $LIVE/W2-00-store) at $(git -C "$(readlink -f $LIVE/W2-00-store)" rev-parse --short=12 HEAD)"
  echo "store halves: a at $(git -C $LIVE/W2-00-store-a rev-parse --short=12 HEAD), b at $(git -C $LIVE/W2-00-store-b rev-parse --short=12 HEAD)"
  echo "w2/integrate: $(git -C "$R" rev-parse --short=12 w2/integrate)"
}
LIVELOG=$R/.gov-runtime/scratch/orchestrator/log/integration-store.log
mkdir -p "$S/home/.local/bin" "$S/home/.local/share/gov-os" "$S/home/gov-os-worktrees" "$S/tmp" "$S/hooks"
echo "======== rehearsal of re-pin window 5 ($MODE), $(date '+%F %T')"
echo "======== the live paths before"
live_fixed | tee "$S/fixed-before.txt"
live_moves | tee "$S/moves-before.txt"
loglines=$(wc -l < "$LIVELOG")
ln -s $LIVEPINS/pin-$OLD "$S/home/.local/share/gov-os/pin-$OLD"
ln -s "$S/home/.local/share/gov-os/pin-$OLD/bin/gov" "$S/home/.local/bin/gov"
for h in a b; do
  src=$LIVE/W2-00-store-$h; dst=$S/home/gov-os-worktrees/W2-00-store-$h
  git clone -q --shared --no-checkout "$R" "$dst"
  git -C "$dst" checkout -q --detach "$(git -C "$src" rev-parse HEAD)"
  mkdir -p "$dst/.gov-runtime"
  for db in store.db query-vector-cache.db; do
    [ -f "$src/.gov-runtime/$db" ] || continue
    python3 - "$src/.gov-runtime/$db" "$dst/.gov-runtime/$db" <<'EOF'
import sqlite3, sys
a = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True); b = sqlite3.connect(sys.argv[2]); a.backup(b); b.close(); a.close()
EOF
  done
  for d in codeintel rebuild; do [ -e "$src/.gov-runtime/$d" ] && cp -a "$src/.gov-runtime/$d" "$dst/.gov-runtime/"; done
  echo "half $h: $(git -C "$dst" rev-parse --short=12 HEAD), store $(du -sh "$dst/.gov-runtime" | cut -f1)"
done
ln -s "$S/home/gov-os-worktrees/W2-00-store-$(readlink -f "$LIVE/W2-00-store" | sed 's/.*-//')" "$S/home/gov-os-worktrees/W2-00-store"
: > "$S/home/gov-os-worktrees/W2-00-store.lock"
git clone -q --shared "$R" "$S/repo"
echo "registry clone at $(git -C "$S/repo" rev-parse --short=12 HEAD) on $(git -C "$S/repo" branch --show-current)"
cp -p "$R/.git/hooks/reference-transaction" "$S/hooks/reference-transaction"
echo "scratch hook: $(sha256sum < "$S/hooks/reference-transaction" | cut -c1-12) (a copy of the live one)"
echo "rehearsal of re-pin window 5 ($MODE), $(date '+%F %T')" > "$S/hold"
START_STORE=$(readlink -f "$S/home/gov-os-worktrees/W2-00-store")
echo "mirror ready: gov -> $(readlink "$S/home/.local/bin/gov"); store -> $(readlink "$S/home/gov-os-worktrees/W2-00-store")"
EXTRA=()
case "$MODE" in
  run) ;;
  neg-src|neg-uncommitted)
    git clone -q --shared "$R" "$S/inputs"
    if [ "$MODE" = neg-src ]; then
      git -C "$S/inputs" checkout -q -b negtest
      echo "# the negative run's change" >> "$S/inputs/src/gov/__init__.py"
      git -C "$S/inputs" add src/gov/__init__.py
      git -C "$S/inputs" -c user.name=rehearsal -c user.email=r@localhost commit -q -m "negative run: src differs"
      EXTRA=(GOV_REPIN_INPUT_REPO="$S/inputs" GOV_REPIN_BRANCH=negtest)
    else
      echo "# the negative run's uncommitted change" >> "$S/inputs/src/gov/__init__.py"
      EXTRA=(GOV_REPIN_INPUT_REPO="$S/inputs")
    fi;;
  neg-check)
    mkdir -p "$S/badstaged"
    cp "$R/docs/changes/W2-141-hook/role_reads.py" "$S/badstaged/role_reads.py"
    { cat "$R/docs/changes/W2-141-hook/pretooluse.py"; printf '\nfrom gov.guard.nonexistent_module import nothing  # the negative run\n'; } > "$S/badstaged/pretooluse.py"
    EXTRA=(REPIN_STAGED_HOOK="$S/badstaged");;
  *) echo "unknown mode $MODE"; exit 2;;
esac
echo "======== the operator's script, against the mirror"
t0=$(date +%s)
rc=0
set +e
env GOV_REPIN_LINK_HOME="$S/home" GOV_REPIN_PINS="$S/home/.local/share/gov-os" \
    GOV_REPIN_STORE_LINK="$S/home/gov-os-worktrees/W2-00-store" GOV_REPIN_REGISTRY_REPO="$S/repo" \
    GOV_REPIN_HOLD="$S/hold" GOV_REPIN_TMP="$S/x" GOV_REPIN_HOOKS="$S/hooks" GOV_REPIN_SKIP_RERANK=1 \
    GOV_STORE_LOG="$S/integration-store.log" SEED_LOG="$S/seed.jsonl" "${EXTRA[@]}" \
    TMPDIR="$S/tmp" bash "$O/REPIN-COMMANDS-W5.sh" 2>&1 | tee "$S/script.out"
rc=${PIPESTATUS[0]}
set -e
echo "======== the script ended: exit $rc, $(( $(date +%s) - t0 )) s"
echo "======== the live paths after"
live_fixed > "$S/fixed-after.txt"; live_moves > "$S/moves-after.txt"
cat "$S/fixed-after.txt" "$S/moves-after.txt"
bad=0
if cmp -s "$S/fixed-before.txt" "$S/fixed-after.txt"; then
  echo "the live gov link, script, pins, wheels, hook, registry file and reranker pid: UNCHANGED (every line equal before and after)"
else echo "the live fixed paths: DIFFER, in:"; diff "$S/fixed-before.txt" "$S/fixed-after.txt" || true; bad=1; fi
if cmp -s "$S/moves-before.txt" "$S/moves-after.txt"; then
  echo "the live store link, its halves and w2/integrate: UNCHANGED"
elif [ "$(sed -n 's/^w2\/integrate: //p' "$S/moves-before.txt")" != "$(sed -n 's/^w2\/integrate: //p' "$S/moves-after.txt")" ]; then
  echo "the live store link and halves moved WITH w2/integrate (the CTO's landing during the run: the live hook refreshed the live store, not this rehearsal):"
  diff "$S/moves-before.txt" "$S/moves-after.txt" || true
  echo "the live store log's new lines (the hook's runs):"; tail -n +"$((loglines + 1))" "$LIVELOG" | grep -E "built|fresh|not refreshed" | cut -c1-160 || true
else echo "the live store link or halves DIFFER while w2/integrate did not move:"; diff "$S/moves-before.txt" "$S/moves-after.txt" || true; bad=1; fi
echo "the scratch hook after: $(sha256sum < "$S/hooks/reference-transaction" | cut -c1-12) (the script only reads it)"
[ "$(sha256sum < "$S/hooks/reference-transaction" | cut -c1-12)" = "$(sha256sum < "$R/.git/hooks/reference-transaction" | cut -c1-12)" ] || { echo "the scratch hook differs from the live one"; bad=1; }
case "$MODE" in
  run)
    echo "the scratch registry commit: $(git -C "$S/repo" log -1 --format='%h %s' | cut -c1-120)"
    python3 -c "import yaml; d=yaml.safe_load(open('$S/repo/governance/project/tool-registry.yaml')); g=[t for t in d['tools'] if t.get('name')=='gov']; print('the scratch registry parses; gov entries:', len(g), g[0]['sha256'][:12], g[0]['date'])"
    git -C "$S/repo" log -1 --format='%B' | tail -4 | sed 's/^/  commit message: /'
    [ "$bad" = 0 ] && [ "$rc" = 0 ] && echo "REHEARSAL OK: exit 0" || { echo "REHEARSAL NOT OK (exit $rc, live check $bad)"; exit 1; }
    exit 0;;
  neg-src|neg-uncommitted)
    want='differs between'; [ "$MODE" = neg-uncommitted ] && want='uncommitted changes in src'
    if [ "$rc" = 1 ] && grep -q "^STOP: .*$want" "$S/script.out" && grep -q "Nothing was switched" "$S/script.out" \
       && [ ! -e "$S/home/.local/share/gov-os/pin-797495bdfc70" ] && [ "$(readlink -f "$S/home/gov-os-worktrees/W2-00-store")" = "$START_STORE" ] \
       && [ "$(readlink -f "$S/home/.local/bin/gov")" = "$(readlink -f "$LIVEPINS/pin-$OLD/bin/gov")" ] && [ "$bad" = 0 ]; then
      echo "NEGATIVE RUN OK ($MODE): STOP at part 0 before anything was built or switched"; exit 0
    fi;;
  neg-check)
    if [ "$rc" = 1 ] && grep -q "^CHECK FAILED: a gov name the staged W2-141 hooks import" "$S/script.out" && grep -q "^STOP: a check before the switch failed" "$S/script.out" \
       && grep -q "the store link is back on" "$S/script.out" && [ "$(readlink -f "$S/home/gov-os-worktrees/W2-00-store")" = "$START_STORE" ] \
       && [ "$(readlink -f "$S/home/.local/bin/gov")" = "$(readlink -f "$LIVEPINS/pin-$OLD/bin/gov")" ] && [ "$bad" = 0 ]; then
      echo "NEGATIVE RUN OK ($MODE): STOP at part B, the store link put back on $(basename "$START_STORE"), the gov link unchanged"; exit 0
    fi;;
esac
echo "NEGATIVE RUN NOT OK ($MODE): exit $rc; see above"; exit 1
