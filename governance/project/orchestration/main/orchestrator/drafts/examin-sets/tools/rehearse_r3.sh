#!/bin/bash
# Round 3's rehearsal of the CHAIN on the live map 30233a092a4b (ACT-OPERATOR-HOURS-2's second commit moved the map): ACT-EXAMIN-SETS-1
# (class (a)), then ACT-ACCEPTED-REDS-1 (class (O), by hand), then ACT-PATHMAP-EXP-1 (class (b)), in ONE --no-hardlinks clone of
# w2/integrate under ~/gov-os-runs/W2-00/pathmap-chain-r3/clone, as each operator will run it: EXAMIN by the agent's apply.sh (the plain
# apply), committed in the clone as the agent would (Role: operator); REDS by the package's section 5 commit line with `Role: owner`;
# EXP by its own apply.sh, committed as the agent would. HOME is planted (tmp/home: a copy of the git identity file, and links to
# ~/.local/bin and ~/.local/share so `head -1 ~/.local/bin/gov` reads the pin). The guard's cases run on a PLANTED sets root
# (tmp/planted/gov-os-eval, dummy files); the real sets root is never opened, listed or named to a hook.
# Nothing live is changed (the main tree is cloned from and its map hashed, read only).
#   bash rehearse_r3.sh        runs every step; the log is ../rehearsal.r3.log (ends "failures: <n>")
# Every checks[].cmd of the three manifests is run exactly as written with `bash -c` from the clone and its exit logged (review F1
# of ACT-EXAMIN-SETS-1). The log holds no head, pid, date or count line of the live tree (nor a test count or a time), so a re-run
# gives the same bytes. It reads <tmp>/manifest.{examin,reds,exp}.draft.json (python3 -I tools/build_r3.py draft first).
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
D=$ORCH/drafts/examin-sets
DR=$ORCH/drafts/accepted-reds-1
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
DE=$ORCH/drafts/pathmap-exp-1
RUN=/home/usain/gov-os-runs/W2-00/pathmap-chain-r3
CL=$RUN/clone
EX=$D/acts-r3/ACT-EXAMIN-SETS-1
RD=$DR/acts-r3/ACT-ACCEPTED-REDS-1
EP=$DE/acts-r3/ACT-PATHMAP-EXP-1
EX2=$ORCH/acts/ACT-EXAMIN-SETS-1.r2-e8020292
RD2=$ORCH/acts/ACT-ACCEPTED-REDS-1.r2-b8df21d8
EP2=$ORCH/acts/ACT-PATHMAP-EXP-1.r2-9a945c99
EX1=$ORCH/acts/ACT-EXAMIN-SETS-1.r1-97d45565
RD1=$DR/acts/ACT-ACCEPTED-REDS-1.r1
SLOT=$ORCH/tools/heavy_slot.sh
T=$D/tools
TR=$DR/tools
PY=$(head -1 /home/usain/.local/bin/gov | cut -c3-)
P=governance/project/path-map.yaml
LOG=$D/rehearsal.r3.log
export TMPDIR=$RUN/tmp
TMPDIR=$RUN/tmp
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
N=0
ok() { N=$((N + 1)); echo "ok   $1"; }
bad() { N=$((N + 1)); echo "FAIL $1"; FAILS=$((FAILS + 1)); }
OUT=$TMPDIR/.rehearsal-out
expect_exit() { # expect_exit <label> <want> <cmd...>
  local label="$1" want="$2"; shift 2
  "$@" > $OUT 2>&1; local rc=$?
  sed 's/^/     /' $OUT | cut -c1-230 | head -40
  [ "$rc" = "$want" ] && ok "$label (exit $rc)" || bad "$label: want exit $want, got $rc"
}
expect_exit_tail() { # as expect_exit, shows only the last 3 lines (long case lists)
  local label="$1" want="$2"; shift 2
  "$@" > $OUT 2>&1; local rc=$?
  tail -3 $OUT | sed 's/^/     /' | cut -c1-230
  [ "$rc" = "$want" ] && ok "$label (exit $rc)" || bad "$label: want exit $want, got $rc"
}
sha() { sha256sum "$1" | cut -c1-64; }
jx() { python3 -I -c "import json,sys; m=json.load(open('$1')); $2"; }
nostray() { [ -z "$(ls governance/project/ | grep -E 'act-tmp|\.bak')" ]; }
runchecks() { # runchecks <draft manifest> <label prefix> <bundle>: every checks[].cmd as written, bash -c, from the clone
  local dm="$1" pre="$2" bun="$3" ncheck i cmd want cnt rc
  ncheck=$(jx $dm "print(len(m['checks']))")
  i=0
  while [ "$i" -lt "$ncheck" ]; do
    cmd=$(jx $dm "print(m['checks'][$i]['cmd'])")
    want=$(jx $dm "print(m['checks'][$i]['exit'])")
    cnt=$(jx $dm "print(m['checks'][$i]['count'])")
    echo "     check $((i + 1)) cmd: $(echo "$cmd" | cut -c1-200)"
    ( cd $CL && bash -c "$cmd" ) > $OUT 2>&1; rc=$?
    sed 's/^/     out: /' $OUT | cut -c1-200 | head -10
    echo "     exit $rc (manifest says $want); manifest count: $cnt (the check prints no count)"
    [ "$rc" = "$want" ] && ok "$pre$((i + 1)) check $((i + 1)) as written: exit $rc" || bad "$pre$((i + 1)) check $((i + 1)): want $want, got $rc"
    i=$((i + 1))
  done
  rm -rf $TMPDIR/probe-before; mkdir -p $TMPDIR/probe-before/governance/project
  cp $bun/before/repo/$P $TMPDIR/probe-before/$P
  cmd=$(jx $dm "print(m['checks'][1]['cmd'])")
  ( cd $TMPDIR/probe-before && bash -c "$cmd" ) > /dev/null 2>&1; rc=$?
  [ "$rc" = 1 ] && ok "${pre}x check 2 exits 1 on the before map, so it tells before from after (exit $rc)" || bad "${pre}x check 2 on the before map exits $rc"
}

echo "--- 0. set-up: a planted HOME, a planted sets root, a fresh clone of the main tree's HEAD (w2/integrate)"
rm -rf $TMPDIR/home $TMPDIR/planted $CL
mkdir -p $TMPDIR/home/.local
[ -f /home/usain/.gitconfig ] && cp -p /home/usain/.gitconfig $TMPDIR/home/.gitconfig
ln -s /home/usain/.local/bin $TMPDIR/home/.local/bin
ln -s /home/usain/.local/share $TMPDIR/home/.local/share
PH=$TMPDIR/planted
E=$PH/gov-os-eval/fixtures/evaluation
for s in examin adoption-proving-ground; do
  mkdir -p $E/$s/hidden/visible $E/$s/visible
  for f in $E/$s/hidden/q01.yaml $E/$s/hidden/visible/q01.yaml $E/$s/visible/q01.yaml $E/$s/XCHECK-r1.md; do echo "dummy" > $f; done
done
mkdir -p $PH/gov-os-eval/governance/project
export HOME=$TMPDIR/home
git clone -q --no-hardlinks $MAIN $CL || { echo "FAIL clone"; echo "failures: 99"; exit 1; }
git -C $CL rev-parse --short=12 HEAD > $TMPDIR/clone.head   # kept out of the hashed log
cd $CL || exit 1
echo "main tree's map $(sha $MAIN/$P | cut -c1-12) (read only); clone's map $(sha $P | cut -c1-12)"
echo "EXAMIN before $(cut -d'|' -f3 $EX/list.txt | cut -c1-12), after $(cut -d'|' -f4 $EX/list.txt | cut -c1-12); REDS before $(cut -d'|' -f3 $RD/list.txt | cut -c1-12), after $(cut -d'|' -f4 $RD/list.txt | cut -c1-12)"
[ "$(sha $P)" = "$(cut -d'|' -f3 $EX/list.txt)" ] && ok "A0 the clone's map is EXAMIN's frozen before (30233a09: after ACT-OPERATOR-HOURS-2's exemption commit)" || bad "A0 the clone's map is not EXAMIN's before (stale bundle)"
[ "$(cut -d'|' -f3 $RD/list.txt)" = "$(cut -d'|' -f4 $EX/list.txt)" ] && ok "A1 REDS's before is EXAMIN's after, and EXP's before is REDS's after (the chain 30233a09 to 1fe00f43 to e4281125 to 805bd918)" || bad "A1 the chain is broken"
[ "$(cut -d'|' -f3 $EP/list.txt)" = "$(cut -d'|' -f4 $RD/list.txt)" ] && ok "A1b EXP's before is REDS's after" || bad "A1b EXP's chain link is broken"
[ "$(sha $MAIN/$P)" = "$(cut -d'|' -f3 $EX/list.txt)" ] && ok "A2 the main tree's map (read only) is EXAMIN's before" || bad "A2 the main tree's map moved"
[ -z "$(git status --porcelain)" ] && ok "A3 the clone is clean" || bad "A3 the clone is not clean"
[ "$(cut -d'|' -f4 $EX/list.txt | cut -c1-8)" = 1fe00f43 ] && [ "$(cut -d'|' -f4 $RD/list.txt | cut -c1-8)" = e4281125 ] && [ "$(cut -d'|' -f4 $EP/list.txt | cut -c1-8)" = 805bd918 ] && ok "A4 the chain's hashes are 1fe00f43, e4281125, 805bd918" || bad "A4 the chain's hashes differ from the build's"
cp -p $P $TMPDIR/map.orig
echo "     the chain: live $(cut -d'|' -f3 $EX/list.txt | cut -c1-12) -> EXAMIN after $(cut -d'|' -f4 $EX/list.txt | cut -c1-12) -> REDS after $(cut -d'|' -f4 $RD/list.txt | cut -c1-12) -> EXP after $(cut -d'|' -f4 $EP/list.txt | cut -c1-12)"
echo "     DEC-1136 in the clone's register: $(grep -c '^### DEC-1136 ' docs/DECISION_REGISTER.md) entry"
echo "     no bundle touches tests/acceptance/: EXAMIN touches $(jx $TMPDIR/manifest.examin.draft.json "print([t['path'] for t in m['touched']])"), REDS touches $(jx $TMPDIR/manifest.reds.draft.json "print([t['path'] for t in m['touched']])"), EXP touches $(jx $TMPDIR/manifest.exp.draft.json "print([t['path'] for t in m['touched']])") (DEC-1136 (2) adds no entry)"

echo "--- B. REVERSED ORDER: REDS first, on the map as it is today (EXAMIN not applied): it must refuse and touch nothing"
before_sha=$(sha $P)
expect_exit "B1 REDS check refuses (state other)" 3 bash $RD/apply.sh check
expect_exit "B2 REDS apply refuses" 3 bash $RD/apply.sh apply
expect_exit "B3 REDS undo refuses" 3 bash $RD/apply.sh undo
expect_exit "B4 REDS verify refuses" 3 bash $RD/apply.sh verify
for s in check apply undo verify; do expect_exit "B4b EXP $s refuses on the live map (EXAMIN and REDS not applied)" 3 bash $EP/apply.sh $s; done
[ "$(sha $P)" = "$before_sha" ] && ok "B5 the map is byte for byte as it was" || bad "B5 the map changed"
[ -z "$(git status --porcelain)" ] && ok "B6 the clone's git status is empty (nothing created beside the map)" || bad "B6 the clone has changes: $(git status --porcelain)"
nostray && ok "B7 no temp file left beside the map" || bad "B7 a temp file is left"
echo "--- B8. the round-1 bundles (built on fb52ab2d) and the round-2 bundles (built on f4029cfb) refuse on the live map and touch nothing"
for b in "$EX1" "$RD1" "$EX2" "$RD2" "$EP2"; do
  for s in check apply undo verify; do
    bash $b/apply.sh $s > $OUT 2>&1; rc=$?
    [ "$rc" = 3 ] && ok "B8 earlier round $(basename $b) $s refuses (exit $rc)" || bad "B8 earlier round $(basename $b) $s: want exit 3, got $rc"
  done
done
[ "$(sha $P)" = "$before_sha" ] && [ -z "$(git status --porcelain)" ] && nostray && ok "B9 the map is untouched by the earlier rounds' bundles" || bad "B9 an earlier round's bundle changed something"

echo "--- C. ACT-EXAMIN-SETS-1: the agent's apply.sh, the plain apply"
expect_exit "C1 check: state before" 0 bash $EX/apply.sh check
expect_exit "C2 verify refused before the apply" 3 bash $EX/apply.sh verify
expect_exit "C3 undo before the apply says nothing to undo" 0 bash $EX/apply.sh undo
expect_exit_tail "C4 the guard's cases on the map BEFORE the entries (the gap check; the same answers after)" 0 $PY -I $T/examin_check.py $CL $PH --expect before
expect_exit "C5 apply (plain: no backup, no environment variable)" 0 bash $EX/apply.sh apply
cmp -s $P $EX/after/repo/$P && ok "C6 the map is the frozen after, byte for byte" || bad "C6 not the frozen after"
[ "$(stat -c %a $P)" = "$(stat -c %a $EX/before/repo/$P)" ] && ok "C7 the mode is kept ($(stat -c %a $P))" || bad "C7 the mode changed"
st="$(git status --porcelain)"
[ "$st" = " M $P" ] && ok "C8 git status lists only the map: [$st]" || bad "C8 git status: [$st]"
nostray && ok "C9 no temp or backup file beside the map" || bad "C9 a stray file"
expect_exit "C10 check: state applied" 0 bash $EX/apply.sh check
expect_exit "C11 verify exit 0" 0 bash $EX/apply.sh verify
expect_exit "C12 apply again changes nothing" 0 bash $EX/apply.sh apply
echo "     numstat: $(git diff --numstat -- $P | tr '\t' ' ')"
git diff -U0 -- $P | grep '^+' | grep -v '^+++' | sed 's/^+//' > $TMPDIR/added.examin
cmp -s $TMPDIR/added.examin $T/entries.yaml && ok "C13 the added lines are tools/entries.yaml byte for byte (the r1 and r2 entries)" || bad "C13 the added lines differ from entries.yaml"
git diff -U0 -- $P | grep '^+' | grep -v '^+++' | sed 's/^+//' > $TMPDIR/added.examin2
diff <(diff -U0 $EX1/before/repo/$P $EX1/after/repo/$P | grep '^[+-]' | grep -v '^+++\|^---') <(git diff -U0 -- $P | grep '^[+-]' | grep -v '^+++\|^---') > /dev/null && ok "C14 the added lines equal r1's added lines (diff of the r1 bundle's before and after)" || bad "C14 the added lines differ from r1's"
diff <(diff -U0 $EX2/before/repo/$P $EX2/after/repo/$P | grep '^[+-]' | grep -v '^+++\|^---') <(git diff -U0 -- $P | grep '^[+-]' | grep -v '^+++\|^---') > /dev/null && ok "C14b the added lines equal r2's added lines (diff of the r2 bundle's before and after)" || bad "C14b the added lines differ from r2's"
echo "     hunk header, r2 bundle: $(diff -U0 $EX2/before/repo/$P $EX2/after/repo/$P | grep '^@@' | cut -d' ' -f1-3); this round: $(git diff -U0 -- $P | grep '^@@' | cut -d' ' -f1-3)"
echo "--- D. EXAMIN's checks as written, the guard after, the sets-root step and the store checks"
runchecks $TMPDIR/manifest.examin.draft.json "D" $EX
expect_exit_tail "D4 the guard's cases on the applied map (the same answers as before)" 0 $PY -I $T/examin_check.py $CL $PH --expect after
SRM=$PH/gov-os-eval/$P
cp -p $TMPDIR/map.orig $SRM
cp -p $SRM $TMPDIR/srm.orig
expect_exit "D5 sets-root step: check says state before" 0 env PY=$PY bash $T/sets_root_map.sh check $SRM
expect_exit "D6 sets-root step: apply" 0 env PY=$PY bash $T/sets_root_map.sh apply $SRM
cmp -s $SRM $P && ok "D7 the planted sets root's map now equals the applied repository map" || bad "D7 the maps differ"
expect_exit "D8 sets-root step: check says state applied" 0 env PY=$PY bash $T/sets_root_map.sh check $SRM
expect_exit "D9 sets-root step: apply again changes nothing" 0 env PY=$PY bash $T/sets_root_map.sh apply $SRM
expect_exit "D10 store_check (evaluation_sets, set_fault, measure gate, kept_out)" 0 env PYTHONPATH=$CL/src $PY -I $T/store_check.py $CL $PH/gov-os-eval
expect_exit "D11 sets-root step: undo restores the planted map" 0 env PY=$PY bash $T/sets_root_map.sh undo $SRM
cmp -s $SRM $TMPDIR/srm.orig && ok "D12 undone byte for byte" || bad "D12 undo differs"
git commit -q -m "ACT-EXAMIN-SETS-1: applied by the operator agent (rehearsal clone)" --trailer "Role: operator" --trailer "Act: ACT-EXAMIN-SETS-1" -- $P && ok "D13 EXAMIN committed in the clone as the agent would (Role: operator)" || bad "D13 commit"
[ -z "$(git status --porcelain)" ] && ok "D14 the clone is clean after the commit" || bad "D14 not clean"
[ "$(sha $P)" = "$(cut -d'|' -f3 $RD/list.txt)" ] && ok "D15 the clone's map is now REDS's frozen before (0ec1d20d)" || bad "D15 the map is not REDS's before"
for s in check apply undo verify; do expect_exit "D16 EXP $s refuses on EXAMIN's after (REDS not applied)" 3 bash $EP/apply.sh $s; done
nostray && [ -z "$(git status --porcelain)" ] && ok "D17 the refusals changed nothing" || bad "D17 a refusal changed something"

echo "--- E. ACT-ACCEPTED-REDS-1: the states before the apply, then the PLAIN apply"
expect_exit "E1 check: state before" 0 bash $RD/apply.sh check
expect_exit "E2 verify refused before the apply" 3 bash $RD/apply.sh verify
expect_exit "E3 undo before the apply says nothing to undo" 0 bash $RD/apply.sh undo
expect_exit "E4 apply" 0 bash $RD/apply.sh apply
cmp -s $P $RD/after/repo/$P && ok "E5 the map is the frozen after, byte for byte" || bad "E5 not the frozen after"
[ "$(stat -c %a $P)" = "$(stat -c %a $RD/before/repo/$P)" ] && ok "E6 the mode is kept ($(stat -c %a $P))" || bad "E6 the mode changed"
st="$(git status --porcelain)"
[ "$st" = " M $P" ] && ok "E7 git status lists only the map: [$st]" || bad "E7 git status: [$st]"
nostray && ok "E8 no temp or backup file beside the map" || bad "E8 a stray file"
expect_exit "E9 check: state applied" 0 bash $RD/apply.sh check
expect_exit "E10 verify exit 0" 0 bash $RD/apply.sh verify
expect_exit "E11 apply again changes nothing" 0 bash $RD/apply.sh apply
git diff -U3 -- $P > $DR/accepted-reds.r3.diff
git diff -U3 -- $P | tail -n +5 | sed 's/^\(@@ [^@]* @@\).*/\1/' > $TMPDIR/clone.hunk
diff -U3 --label a/$P --label b/$P $RD/before/repo/$P $RD/after/repo/$P | tail -n +3 | sed 's/^\(@@ [^@]* @@\).*/\1/' > $TMPDIR/bundle.hunk
cmp -s $TMPDIR/clone.hunk $TMPDIR/bundle.hunk && ok "E12 the clone's diff is the diff of the bundle's before and after copies, hunk for hunk" || bad "E12 the hunks differ"
echo "     hunk header: $(grep '^@@' $TMPDIR/clone.hunk | head -1); numstat: $(git diff --numstat -- $P | tr '\t' ' ')"
git diff -U0 -- $P | grep '^+' | grep -v '^+++' | sed 's/^+//' | tail -n +2 > $TMPDIR/added.reds
tail -n +2 $TR/entries.yaml > $TMPDIR/entries.reds.tail
cmp -s $TMPDIR/added.reds $TMPDIR/entries.reds.tail && ok "E13 the added entries are tools/entries.yaml byte for byte (the r1 entries)" || bad "E13 the entries differ from entries.yaml"
diff <(diff -U0 $RD1/before/repo/$P $RD1/after/repo/$P | grep '^[+-]' | grep -v '^+++\|^---') <(git diff -U0 -- $P | grep '^[+-]' | grep -v '^+++\|^---') > /dev/null && ok "E14 the changed lines equal r1's changed lines" || bad "E14 the changed lines differ from r1's"
diff <(diff -U0 $RD2/before/repo/$P $RD2/after/repo/$P | grep '^[+-]' | grep -v '^+++\|^---') <(git diff -U0 -- $P | grep '^[+-]' | grep -v '^+++\|^---') > /dev/null && ok "E14b the changed lines equal r2's changed lines" || bad "E14b the changed lines differ from r2's"
echo "     hunk header, r2 bundle: $(diff -U0 $RD2/before/repo/$P $RD2/after/repo/$P | grep '^@@' | cut -d' ' -f1-3); this round: $(git diff -U0 -- $P | grep '^@@' | cut -d' ' -f1-3)"
expect_exit "E15 pin's judge, applied but not yet committed by the owner: neither test counted, each refused as 'no commit of the history adds it'" 0 $PY -I $TR/ratchet_probe.py $CL pending
echo "--- F. REDS's checks as written, with bash -c from the clone"
runchecks $TMPDIR/manifest.reds.draft.json "F" $RD
echo "--- G. the validate step (DEC-895) on this round's patch (the clone's diff), with the pin's python, against the register as it stands"
expect_exit "G1 validate_entry.py (PASS for both entries, pending the owner's commit)" 0 $PY -E $ORCH/tools/validate_entry.py $DR/accepted-reds.r3.diff
grep -q 'PASS' $OUT && [ "$(grep -c 'PASS' $OUT)" -ge 2 ] && ok "G2 a PASS line for each of the two entries" || bad "G2 fewer than two PASS lines"

echo "--- H. the owner's operator's commit, by hand, as section 5's commit line gives it (Role: owner), then the pin's ratchet reader"
git commit -q -m "ACT-ACCEPTED-REDS-1: accepted_reds lists the two warm real-model latency cases (W1-19, W2-13) until W2-155 closes (DEC-1134)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1134, DEC-1125" --trailer "Role: owner" -- governance/project/path-map.yaml && ok "H1 committed with Role: owner" || bad "H1 commit"
echo "     trailers: $(git log -1 --format='%(trailers:only,unfold,separator=; )')"
[ -z "$(git status --porcelain)" ] && ok "H2 the clone is clean after the commit" || bad "H2 not clean"
git branch -q owner-ok
expect_exit "H3 both tests counted (accepted) by gov.close.ratchet.counted_entries, no finding" 0 $PY -I $TR/ratchet_probe.py $CL counted
( cd $CL && "$(head -1 ~/.local/bin/gov | cut -c3-)" -I -c 'from gov.close import ratchet; c,f=ratchet.counted_entries(".","accepted_reds"); print(len(c),len(f))' ) > $OUT 2>&1
[ "$(cat $OUT)" = "2 0" ] && ok "H4 section 5's own one-line reader (the pin read from ~/.local/bin/gov), from the repository root: prints 2 0" || bad "H4 the one-line reader printed: $(cat $OUT)"
expect_exit "H5 apply_accepted_reds, both red: ok true, each covered (reported failed)" 0 $PY -I $TR/ratchet_probe.py $CL both-red
expect_exit "H6 a listed test that passes: a finding, the entry must leave" 0 $PY -I $TR/ratchet_probe.py $CL one-passes
expect_exit "H7 another red is still refused" 0 $PY -I $TR/ratchet_probe.py $CL other-red
echo "--- H8. the same commit with Role: operator (what the operator agent would make): the ratchet refuses both entries"
git commit -q --amend -m "ACT-ACCEPTED-REDS-1: as an operator-agent commit" --trailer "Role: operator" --trailer "Act: ACT-ACCEPTED-REDS-1" -- governance/project/path-map.yaml >/dev/null
expect_exit "H8 both refused: added without Role: owner" 0 $PY -I $TR/ratchet_probe.py $CL not-owner
git reset -q --hard owner-ok
expect_exit "H9 restored: both counted again" 0 $PY -I $TR/ratchet_probe.py $CL counted

echo "--- H10. ACT-PATHMAP-EXP-1: the chain's third link, by its own apply.sh (the agent's route), on REDS's committed after"
git branch -q reds-ok
expect_exit "H10 EXP check: state before (REDS's after)" 0 bash $EP/apply.sh check
grep -qx "state before (sha256 $(cut -d'|' -f4 $RD/list.txt | cut -c1-12))" $OUT && ok "H11 the check line is 'state before (sha256 $(cut -d'|' -f4 $RD/list.txt | cut -c1-12))'" || bad "H11 the check line differs"
expect_exit "H12 EXP verify refused before the apply" 3 bash $EP/apply.sh verify
expect_exit "H13 EXP undo before the apply says nothing to undo" 0 bash $EP/apply.sh undo
expect_exit "H14 EXP apply (plain)" 0 bash $EP/apply.sh apply
cmp -s $P $EP/after/repo/$P && ok "H15 the map is the frozen after, byte for byte" || bad "H15 not the frozen after"
[ "$(stat -c %a $P)" = "$(stat -c %a $EP/before/repo/$P)" ] && ok "H16 the mode is kept ($(stat -c %a $P))" || bad "H16 the mode changed"
st="$(git status --porcelain)"
[ "$st" = " M $P" ] && ok "H17 git status lists only the map: [$st]" || bad "H17 git status: [$st]"
nostray && ok "H18 no temp or backup file beside the map" || bad "H18 a stray file"
expect_exit "H19 EXP check: state applied" 0 bash $EP/apply.sh check
expect_exit "H20 EXP verify exit 0" 0 bash $EP/apply.sh verify
expect_exit "H21 EXP apply again changes nothing" 0 bash $EP/apply.sh apply
echo "     numstat: $(git diff --numstat -- $P | tr '\t' ' ')"
git diff -U0 -- $P | grep '^[+-]' | grep -v '^+++\|^---' > $TMPDIR/exp.changed
[ "$(cat $TMPDIR/exp.changed)" = '+      - "experiments/**"' ] && ok "H22 the one changed line is '      - \"experiments/**\"' added" || bad "H22 the changed lines: $(cat $TMPDIR/exp.changed)"
diff <(diff -U0 $EP2/before/repo/$P $EP2/after/repo/$P | grep '^[+-]' | grep -v '^+++\|^---') $TMPDIR/exp.changed > /dev/null && ok "H23 the added line equals r2's added line (diff of the r2 bundle's before and after)" || bad "H23 the added line differs from r2's"
echo "     hunk header, r2 bundle: $(diff -U0 $EP2/before/repo/$P $EP2/after/repo/$P | grep '^@@' | cut -d' ' -f1-3); this round: $(git diff -U0 -- $P | grep '^@@' | cut -d' ' -f1-3)"
echo "--- H24. EXP's checks as written, each with bash -c (check 1 is gov.check.pathmap), and check 2 on the before map"
runchecks $TMPDIR/manifest.exp.draft.json "HX" $EP
git commit -q -m "ACT-PATHMAP-EXP-1: applied by the operator agent (rehearsal clone)" --trailer "Role: operator" --trailer "Act: ACT-PATHMAP-EXP-1" -- $P && ok "H30 EXP committed in the clone as the agent would (Role: operator)" || bad "H30 commit"
[ -z "$(git status --porcelain)" ] && ok "H31 the clone is clean after the commit" || bad "H31 not clean"
git branch -q exp-ok
expect_exit "H32 the ratchet still counts both tests (REDS's Role: owner commit is the one that added them)" 0 $PY -I $TR/ratchet_probe.py $CL counted
echo "--- H33. the whole chain applied: gov.check.pathmap and W1-01's folder (no bundle touches tests/acceptance/)"
( cd $CL && PYTHONPATH=src python3 -m gov.check.pathmap ) > $OUT 2>&1; rc=$?
sed 's/^/     out: /' $OUT | cut -c1-200 | head -5
[ "$rc" = 0 ] && ok "H33 gov.check.pathmap on the chain's end state: exit $rc" || bad "H33 gov.check.pathmap exit $rc"
bash $SLOT env TMPDIR=$TMPDIR PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$CL/src python3 -m pytest tests/acceptance/W1-01 -q -p no:cacheprovider -o tmp_path_retention_policy=failed > $TMPDIR/w1-01.out 2>&1; rc=$?
tail -3 $TMPDIR/w1-01.out | cut -c1-200 > $TMPDIR/w1-01.tail     # the count and the time stay out of the hashed log
[ "$rc" = 0 ] && ok "H34 tests/acceptance/W1-01 on the chain's end state: pytest exit $rc" || { bad "H34 tests/acceptance/W1-01: pytest exit $rc"; sed 's/^/     out: /' $TMPDIR/w1-01.tail; }

echo "--- I. undo in the reverse order, from the committed states: EXP first, then REDS, then EXAMIN"
expect_exit "I0a REDS undo with EXP on top refuses" 3 bash $RD/apply.sh undo
expect_exit "I0b EXAMIN undo with EXP on top refuses" 3 bash $EX/apply.sh undo
git status --porcelain | grep -q . && bad "I0c the refused undos changed the clone" || ok "I0c the refused undos changed nothing"
expect_exit "I0d EXP undo" 0 bash $EP/apply.sh undo
cmp -s $P $EP/before/repo/$P && ok "I0e the map is EXP's frozen before (REDS's after), byte for byte" || bad "I0e undo differs"
expect_exit "I0f EXP undo again: nothing to undo" 0 bash $EP/apply.sh undo
expect_exit "I1 REDS undo" 0 bash $RD/apply.sh undo
cmp -s $P $RD/before/repo/$P && ok "I2 the map is REDS's frozen before (EXAMIN's after), byte for byte" || bad "I2 undo differs"
[ "$(git status --porcelain)" = " M $P" ] && ok "I3 git status lists only the map" || bad "I3 git status: $(git status --porcelain)"
expect_exit "I4 REDS undo again: nothing to undo" 0 bash $RD/apply.sh undo
expect_exit "I5 EXAMIN verify: the map is EXAMIN's applied state" 0 bash $EX/apply.sh verify
expect_exit "I6 EXAMIN undo" 0 bash $EX/apply.sh undo
cmp -s $P $EX/before/repo/$P && ok "I7 the map is the live map again (30233a09), byte for byte" || bad "I7 undo differs"
git checkout -q -- $P; git reset -q --hard exp-ok
nostray && ok "I8 no temp file left" || bad "I8 a temp file is left"
echo "--- I9. undo of EXAMIN while REDS and EXP are on top refuses (undo EXP, then REDS, first)"
expect_exit "I9 EXAMIN undo on EXP's after: refused" 3 bash $EX/apply.sh undo
git status --porcelain | grep -q . && bad "I9b the refused undo changed the clone" || ok "I9b the refused undo changed nothing"

echo "--- J. refusals (each bundle on its own frozen before)"
git reset -q --hard exp-ok
for who in EX RD EP; do
  case "$who" in EX) A=$EX ;; RD) A=$RD ;; EP) A=$EP ;; esac
  BEF=$A/before/repo/$P
  cp -p $BEF $P
  echo "# changed later" >> $P
  expect_exit "J1 $who check refuses a map that changed" 3 bash $A/apply.sh check
  expect_exit "J2 $who apply refuses" 3 bash $A/apply.sh apply
  expect_exit "J3 $who undo refuses" 3 bash $A/apply.sh undo
  expect_exit "J3b $who verify refuses" 3 bash $A/apply.sh verify
  cp -p $BEF $P
  mv $P $P.real && ln -s $P.real $P
  expect_exit "J4 $who a link is refused by check" 3 bash $A/apply.sh check
  expect_exit "J5 $who a link is refused by apply" 3 bash $A/apply.sh apply
  rm $P && mv $P.real $P
  cmp -s $P $BEF && ok "J6 $who the link test left the map as it was" || bad "J6 $who map differs"
  echo "sentinel" > $TMPDIR/sentinel.txt
  ln -s $TMPDIR/sentinel.txt $P.act-tmp
  expect_exit "J7 $who apply with a link planted at the old fixed temp name <map>.act-tmp" 0 bash $A/apply.sh apply
  [ "$(cat $TMPDIR/sentinel.txt)" = sentinel ] && ok "J8 $who the planted link's target is untouched (review F4)" || bad "J8 $who the link target was written"
  cmp -s $P $A/after/repo/$P && ok "J9 $who the map is the frozen after" || bad "J9 $who the map differs"
  rm -f $P.act-tmp
  expect_exit "J10 $who undo" 0 bash $A/apply.sh undo
  nostray && ok "J11 $who no temp file left (mktemp names removed)" || bad "J11 $who a temp file is left"
  rm -rf $TMPDIR/bundle-tampered; cp -r $A $TMPDIR/bundle-tampered; echo "# tampered" >> $TMPDIR/bundle-tampered/after/repo/$P
  expect_exit "J12 $who a tampered frozen copy: apply exits 4" 4 bash $TMPDIR/bundle-tampered/apply.sh apply
  cmp -s $P $BEF && ok "J13 $who the map is untouched by the refused apply" || bad "J13 $who the map changed"
  chmod a-w governance/project
  expect_exit "J14 $who the map's folder not writable: apply exits 5 and nothing changes" 5 bash $A/apply.sh apply
  chmod u+w governance/project
  cmp -s $P $BEF && ok "J15 $who the map is untouched" || bad "J15 $who the map changed"
  nostray && ok "J16 $who no temp file left" || bad "J16 $who a temp file is left"
done
cp -p $EX/before/repo/$P $P
git checkout -q -- $P

echo "--- K. the live files are unchanged (read only)"
echo "main tree's map $(sha $MAIN/$P | cut -c1-12), EXAMIN's before $(cut -d'|' -f3 $EX/list.txt | cut -c1-12)"
[ "$(sha $MAIN/$P)" = "$(cut -d'|' -f3 $EX/list.txt)" ] && ok "K1 the main tree's map is unchanged" || bad "K1 the main tree's map changed (or a path-map ACT was applied meanwhile)"
echo
echo "checks run: $N"
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
