#!/usr/bin/env bash
# The rehearsal of the re-pin from release 0.1.0 (DEC-1057: every ACT rehearsed end to end before the hand-over), changing
# nothing live. rehearse_repin7.sh's mirror, plus a SCRATCH RELEASE:
#   <S>/release  a shared clone of the main tree, its local w2/integrate at the stand-in C (the main tree's w2/integrate
#                head when the rehearsal starts); the record made there by the live pin's own release code
#                (gov.release.build, what `gov release 0.1.0` runs, without its typed code), committed as §4 step 5
#                commits it, and an annotated scratch tag v0.1.0 on that record commit (§4 step 6). The tag and commit
#                exist only in that clone: the main tree gets no tag, no ref and no commit.
#   then fill_release.sh fills the operator's script from that clone into <S>, and the filled script runs as the
#   operator will, with GOV_REPIN_RELEASE_REPO=<S>/release and its other GOV_REPIN_* paths in the mirror:
#   <S>/home/.local/bin/gov -> <S>/home/.local/share/gov-os/pin-797495bdfc70/bin/gov (that folder a link to the live
#   pin, only read); <S>/home/gov-os-worktrees/W2-00-store{-a,-b} shared clones at the live halves' commits with copies
#   of their stores (SQLite's backup; the live halves only read), the link on the live one; <S>/repo a shared clone for
#   the registry commit; <S>/hold the CTO's hold; <S>/hooks a copy of the live reference-transaction hook;
#   GOV_REPIN_SKIP_RERANK=1 (the live shared reranker is not restarted; part C compares its bytes, part D searches it).
# The frozen-src rule and the store are checked against the main tree's w2/integrate (the record commit is only in the
# scratch clone, so part R's "the tag is in the branch's history" line runs only when the two repositories are one, as
# live).
# Before and after, the live paths are recorded: what only this act could change (the gov link and its script, the
# pins and wheels, the hook, the registry file, the reranker's pid, the main tree's tags and docs/releases/) must be
# UNCHANGED; what moves with the CTO's own landings (the store link, its halves, the heads) is shown, and compared
# strictly only if the head did not move during the run.
#     bash rehearse_rel.sh [<scratch dir, default /tmp/gov-os-rel-repin/r>] [MODE]
# MODE: run (default): the whole script, expecting exit 0. The negative runs expect a STOP, with nothing switched:
#   neg-src          a branch whose src/ differs from C (the frozen-src rule, part 0);
#   neg-uncommitted  an uncommitted change in src/ (part 0);
#   neg-check        a check of part B fails after the store was rebuilt and its link flipped (the staged W2-141 hook
#                    names a gov module the pin lacks): the store link must be put back;
#   neg-tag          the scratch tag moved onto C itself, not the record commit (part R; fill_release.sh refuses too);
#   neg-manifest     manifest.json changed after manifest.sha256 was written, in a record commit on C (part R;
#                    fill_release.sh refuses too);
#   neg-sha          the filled script's SHA is not the record's wheel sha256 (a hand-copy slip; part R);
#   neg-int          a TERM to the script while part S's store refresh runs (the INT/TERM trap, review F7; a Ctrl-C
#                    takes the same handler, but a background job in a script ignores INT, so TERM is sent): the
#                    refresh's process group must be gone, STOP within 30 s of the TERM (review r2 F1), the store
#                    link as at the start 20 s later.
set -euo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
B=$R/.gov-runtime/scratch/orchestrator/drafts/repin-rel-0.1.0
S=${1:-/tmp/gov-os-rel-repin/r}
MODE=${2:-run}
LIVE=/home/usain/gov-os-worktrees
LIVEPINS=/home/usain/.local/share/gov-os
OLD=797495bdfc70
case "$MODE" in run|neg-src|neg-uncommitted|neg-check|neg-tag|neg-manifest|neg-sha|neg-int) ;; *) echo "unknown mode $MODE"; exit 2;; esac
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
  echo "main tree tags v*: $(git -C "$R" tag -l 'v*' | tr '\n' ' ')(end)"
  echo "main tree docs/releases: $(ls "$R/docs/releases" | tr '\n' ' ')"
}
live_moves() {
  echo "store link: $(readlink $LIVE/W2-00-store) -> $(readlink -f $LIVE/W2-00-store) at $(git -C "$(readlink -f $LIVE/W2-00-store)" rev-parse --short=12 HEAD)"
  echo "store halves: a at $(git -C $LIVE/W2-00-store-a rev-parse --short=12 HEAD), b at $(git -C $LIVE/W2-00-store-b rev-parse --short=12 HEAD)"
  echo "w2/integrate: $(git -C "$R" rev-parse --short=12 w2/integrate)"
}
LIVELOG=$R/.gov-runtime/scratch/orchestrator/log/integration-store.log
mkdir -p "$S/home/.local/bin" "$S/home/.local/share/gov-os" "$S/home/gov-os-worktrees" "$S/tmp" "$S/hooks"
echo "======== rehearsal of the re-pin from release 0.1.0 ($MODE), $(date '+%F %T')"
echo "======== the live paths before"
live_fixed | tee "$S/fixed-before.txt"
live_moves | tee "$S/moves-before.txt"
loglines=$(wc -l < "$LIVELOG")
STANDIN=$(git -C "$R" rev-parse w2/integrate)
echo "the stand-in C: ${STANDIN:0:12} (the main tree's w2/integrate head now)"

echo "======== the scratch release 0.1.0 at the stand-in C (a scratch clone only)"
REL=$S/release
git clone -q --shared --no-checkout "$R" "$REL"
git -C "$REL" checkout -q -B w2/integrate "$STANDIN"
[ -z "$(git -C "$REL" tag -l 'v0.1.0')" ] || { echo "the scratch clone already has a v0.1.0 tag"; exit 1; }
[ -z "$(git -C "$REL" status --porcelain --untracked-files=all)" ] || { echo "the scratch clone is not clean"; exit 1; }
(cd "$S/tmp" && "$LIVEPINS/pin-$OLD/bin/python" -E -c 'import sys; from pathlib import Path; from gov.release import build; print("record:", build(Path(sys.argv[1]), "0.1.0"))' "$REL")
(cd "$REL/docs/releases/0.1.0" && sha256sum -c manifest.sha256)
echo "scratch status: $(git -C "$REL" status --porcelain | tr '\n' ' ')"
git -C "$REL" add docs/releases/0.1.0
git -C "$REL" -c user.name=rehearsal -c user.email=rehearsal@localhost commit -q -F - <<EOF
Release 0.1.0: the record of the first numbered, frozen release (W2-16, DEC-772) [SCRATCH REHEARSAL]

Built by gov release 0.1.0 from ${STANDIN:0:12} on w2/integrate (the rehearsal's stand-in C).

Role: owner
Task: DAEO-sdxk
Implements: DEC-772, DEC-1089, DEC-0000
EOF
git -C "$REL" -c user.name=rehearsal -c user.email=rehearsal@localhost tag -a v0.1.0 -m "Release 0.1.0 (W2-16) [SCRATCH REHEARSAL]"
echo "scratch tag: v0.1.0 -> $(git -C "$REL" rev-parse --short=12 'v0.1.0^{commit}') (parent $(git -C "$REL" rev-parse --short=12 'v0.1.0^{commit}^')), $(git -C "$REL" cat-file -t refs/tags/v0.1.0)"
python3 -c 'import json,sys; m=json.load(open(sys.argv[1])); print("scratch record: version", m["version"], "commit", m["commit"][:12], "cli", m["cli_version"], "wheel", m["wheel"]["name"], m["wheel"]["sha256"][:12], "files", len(m["files"]))' "$REL/docs/releases/0.1.0/manifest.json"

echo "======== fill_release.sh from the scratch release"
F=$S/REPIN-COMMANDS-REL-0.1.0.sh
bash "$B/fill_release.sh" "${STANDIN:0:12}" "$REL" "$F"
diff <(sed 's/^\(C\|EPOCH\|SHA\|RECORD\)=[^ ]*/\1=__FILLED__/' "$F") <(sed 's/^\(C\|EPOCH\|SHA\|RECORD\)=[^ ]*/\1=__FILLED__/' "$B/REPIN-COMMANDS-REL.template.sh") > /dev/null \
  && echo "the filled script differs from the template in the four value lines only" || { echo "the filled script differs from the template beyond the four values"; exit 1; }

# the mirror (rehearse_repin7.sh's)
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
echo "rehearsal of the re-pin from release 0.1.0 ($MODE), $(date '+%F %T')" > "$S/hold"
START_STORE=$(readlink -f "$S/home/gov-os-worktrees/W2-00-store")
echo "mirror ready: gov -> $(readlink "$S/home/.local/bin/gov"); store -> $(readlink "$S/home/gov-os-worktrees/W2-00-store")"

EXTRA=()
FILLREF=""
case "$MODE" in
  run|neg-int) ;;
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
  neg-tag)
    git -C "$REL" -c user.name=rehearsal -c user.email=rehearsal@localhost tag -f -a v0.1.0 -m "the negative run: the tag on C" "$STANDIN" > /dev/null
    echo "neg-tag: the scratch tag moved to $(git -C "$REL" rev-parse --short=12 'v0.1.0^{commit}') (C itself)";;
  neg-manifest)
    git -C "$REL" reset -q --hard "$STANDIN"
    git -C "$REL" checkout -q 'v0.1.0^{commit}' -- docs/releases/0.1.0
    python3 - "$REL/docs/releases/0.1.0/manifest.json" <<'EOF'
import json, sys
p = sys.argv[1]; m = json.load(open(p)); m["release_notes"].append("- a line added after the hash (the negative run)")
open(p, "w").write(json.dumps(m, indent=2) + "\n")
EOF
    git -C "$REL" add docs/releases/0.1.0
    git -C "$REL" -c user.name=rehearsal -c user.email=rehearsal@localhost commit -q -m "the negative run: manifest.json changed after its hash"
    git -C "$REL" -c user.name=rehearsal -c user.email=rehearsal@localhost tag -f -a v0.1.0 -m "the negative run" > /dev/null
    echo "neg-manifest: the scratch tag now on $(git -C "$REL" rev-parse --short=12 'v0.1.0^{commit}') (parent $(git -C "$REL" rev-parse --short=12 'v0.1.0^{commit}^')), manifest.json edited after its hash";;
  neg-sha)
    sed -i 's/^SHA=[0-9a-f]\{64\}/SHA=0000000000000000000000000000000000000000000000000000000000000000/' "$F"
    echo "neg-sha: the filled SHA line now: $(grep '^SHA=' "$F" | cut -c1-30)...";;
esac
if [ "$MODE" = neg-tag ] || [ "$MODE" = neg-manifest ]; then
  set +e; bash "$B/fill_release.sh" "${STANDIN:0:12}" "$REL" "$S/refill.sh" > "$S/refill.out" 2>&1; frc=$?; set -e
  cat "$S/refill.out"
  if [ "$frc" = 1 ] && grep -q '^REFUSED, nothing written' "$S/refill.out" && [ ! -e "$S/refill.sh" ]; then FILLREF=ok; echo "fill_release.sh refuses the tampered release, writing nothing"; else FILLREF=bad; echo "fill_release.sh did NOT refuse the tampered release (exit $frc)"; fi
fi

echo "======== the operator's script (filled from the scratch release), against the mirror"
t0=$(date +%s)
rc=0
set +e
sha256sum -c --quiet "$S/REPIN-REL-0.1.0.sha256" && echo "the hash list: $(wc -l < "$S/REPIN-REL-0.1.0.sha256") files OK (the operator's first check)" \
  || { [ "$MODE" = neg-sha ] && echo "the hash list fails on the edited script, as it would for the operator (neg-sha runs the script anyway, to show part R's stop)"; } \
  || { echo "the hash list does not hold"; exit 1; }
RUNENV=(GOV_REPIN_LINK_HOME="$S/home" GOV_REPIN_PINS="$S/home/.local/share/gov-os"
    GOV_REPIN_STORE_LINK="$S/home/gov-os-worktrees/W2-00-store" GOV_REPIN_REGISTRY_REPO="$S/repo"
    GOV_REPIN_HOLD="$S/hold" GOV_REPIN_TMP="$S/x" GOV_REPIN_HOOKS="$S/hooks" GOV_REPIN_SKIP_RERANK=1
    GOV_REPIN_RELEASE_REPO="$REL"
    GOV_STORE_LOG="$S/integration-store.log" SEED_LOG="$S/seed.jsonl" "${EXTRA[@]}" TMPDIR="$S/tmp")
INTPID=""; INTLATE=""; INTSECS=999
if [ "$MODE" = neg-int ]; then
  env "${RUNENV[@]}" bash "$F" > "$S/script.out" 2>&1 &
  sp=$!
  waited=0
  while kill -0 "$sp" 2> /dev/null && [ ! -e "$S/x/refresh.out" ] && [ $waited -lt 7200 ]; do sleep 2; waited=$((waited + 2)); done
  sleep 10
  echo "neg-int: TERM to the script (pid $sp) $(( $(date +%s) - t0 )) s in, $([ -e "$S/x/refresh.out" ] && echo 'the store refresh started' || echo 'the store refresh NOT started')"
  tk=$(date +%s.%N)
  kill -TERM "$sp" 2> /dev/null
  wait "$sp"; rc=$?
  INTSECS=$(echo "$(date +%s.%N) - $tk" | bc); INTSECS=${INTSECS%.*}; INTSECS=${INTSECS:-0}
  echo "neg-int: the script ended ${INTSECS} s after the TERM (exit $rc)"
  cat "$S/script.out"
  INTPID=$(sed -n 's/^the store refresh (pid \([0-9]*\),.*/\1/p' "$S/script.out" | head -1)
  sleep 20
  INTLATE=$(readlink -f "$S/home/gov-os-worktrees/W2-00-store")
  echo "neg-int: 20 s after the script ended, the store link -> $(basename "$INTLATE") (at the start $(basename "$START_STORE")); the refresh's process group ${INTPID:-?}: $([ -n "$INTPID" ] && [ -z "$(ps -o pid= -g "$INTPID" 2> /dev/null)" ] && echo gone || echo 'NOT gone or not named')"
else
  env "${RUNENV[@]}" bash "$F" 2>&1 | tee "$S/script.out"
  rc=${PIPESTATUS[0]}
fi
set -e
echo "======== the script ended: exit $rc, $(( $(date +%s) - t0 )) s"
echo "======== the live paths after"
live_fixed > "$S/fixed-after.txt"; live_moves > "$S/moves-after.txt"
cat "$S/fixed-after.txt" "$S/moves-after.txt"
bad=0
if cmp -s "$S/fixed-before.txt" "$S/fixed-after.txt"; then
  echo "the live gov link, script, pins, wheels, hook, registry file, reranker pid, main-tree tags and docs/releases: UNCHANGED (every line equal before and after)"
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
C12=${STANDIN:0:12}
nothing_built() { [ ! -e "$S/home/.local/share/gov-os/pin-$C12" ] && [ ! -e "$S/home/.local/share/gov-os/wheels" ]; }
nothing_switched() {  # the gov link and the store link as at the start; the live paths unchanged; the script said so
  [ "$(readlink -f "$S/home/gov-os-worktrees/W2-00-store")" = "$START_STORE" ] \
    && [ "$(readlink -f "$S/home/.local/bin/gov")" = "$(readlink -f "$LIVEPINS/pin-$OLD/bin/gov")" ] && [ "$bad" = 0 ] \
    && grep -q "Nothing was switched" "$S/script.out" && [ "$rc" = 1 ]
}
case "$MODE" in
  run)
    echo "the scratch registry commit: $(git -C "$S/repo" log -1 --format='%h %s' | cut -c1-140)"
    python3 -c "import yaml; d=yaml.safe_load(open('$S/repo/governance/project/tool-registry.yaml')); g=[t for t in d['tools'] if t.get('name')=='gov']; print('the scratch registry parses; gov entries:', len(g), g[0]['sha256'][:12], g[0]['date'], g[0]['approved_by'])"
    echo "  its trailers: $(git -C "$S/repo" log -1 --format='%(trailers:only,unfold)' | tr '\n' ';')"
    tr=$(git -C "$S/repo" log -1 --format='%(trailers:only,unfold)')
    grep -qx 'Role: owner' <<<"$tr" && grep -qx 'Task: decision-record' <<<"$tr" && grep -qx 'Implements: DEC-1178' <<<"$tr" || { echo "the registry commit's trailers are not the three"; bad=1; }
    grep -q "^release check: the wheel's sha256 = the record's" "$S/script.out" || { echo "the release check line is missing"; bad=1; }
    [ "$bad" = 0 ] && [ "$rc" = 0 ] && echo "REHEARSAL OK: exit 0" || { echo "REHEARSAL NOT OK (exit $rc, live check $bad)"; exit 1; }
    exit 0;;
  neg-src|neg-uncommitted)
    want='differs between'; [ "$MODE" = neg-uncommitted ] && want='uncommitted changes in src'
    if nothing_switched && nothing_built && grep -q "^STOP: .*$want" "$S/script.out" && ! grep -q '^== R\.' "$S/script.out"; then
      echo "NEGATIVE RUN OK ($MODE): STOP at part 0 before anything was read, built or switched"; exit 0
    fi;;
  neg-check)
    if nothing_switched && grep -q "^CHECK FAILED: a gov name the staged W2-141 hooks import" "$S/script.out" && grep -q "^STOP: a check before the switch failed" "$S/script.out" \
       && grep -q "the store link is back on" "$S/script.out"; then
      echo "NEGATIVE RUN OK ($MODE): STOP at part B, the store link put back on $(basename "$START_STORE"), the gov link unchanged"; exit 0
    fi;;
  neg-int)
    if nothing_switched && grep -q "^STOP: interrupted (TERM) before the switch" "$S/script.out" && grep -q '^== S\.' "$S/script.out" \
       && ! grep -q '^== B\.' "$S/script.out" && [ -n "$INTPID" ] && [ -z "$(ps -o pid= -g "$INTPID" 2> /dev/null)" ] \
       && [ "$INTLATE" = "$START_STORE" ] && [ "$INTSECS" -lt 30 ]; then
      echo "NEGATIVE RUN OK ($MODE): TERM during part S's refresh: the refresh's group stopped, STOP ${INTSECS} s after the TERM, the store link on $(basename "$START_STORE") 20 s later, the gov link unchanged"; exit 0
    fi;;
  neg-tag|neg-manifest|neg-sha)
    case "$MODE" in
      neg-tag) want='is not on the record commit whose parent is\|is not a commit with one parent';;
      neg-manifest) want="does not match its manifest.sha256";;
      neg-sha) want="the manifest's wheel sha256 .* is not the one filled in";;
    esac
    if nothing_switched && nothing_built && grep -q "^STOP: .*$want" "$S/script.out" && ! grep -q '^== A\.' "$S/script.out" \
       && { [ "$MODE" = neg-sha ] || [ "$FILLREF" = ok ]; }; then
      echo "NEGATIVE RUN OK ($MODE): STOP at part R before anything was built or switched$([ "$MODE" = neg-sha ] || echo '; fill_release.sh refused it too')"; exit 0
    fi;;
esac
echo "NEGATIVE RUN NOT OK ($MODE): exit $rc; see above"; exit 1
