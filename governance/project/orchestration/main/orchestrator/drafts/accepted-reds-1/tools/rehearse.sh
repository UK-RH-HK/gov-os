#!/bin/bash
# ACT-ACCEPTED-REDS-1's rehearsal, as the owner's operator will run it, in a --no-hardlinks clone of w2/integrate under
# drafts/accepted-reds-1/tmp/clone, with HOME planted under tmp/home. Only the repository root is substituted (the clone for
# the main tree). ACT-EXAMIN-SETS-1 is applied FIRST in the clone, by its own apply.sh (the plain apply), and committed there.
# Nothing live is changed or touched (the main tree is only cloned from and its map hashed, read only).
#   bash rehearse.sh            runs every step; the log is ../rehearsal.log (ends "failures: <n>")
# It reads tmp/manifest.draft.json (python3 tools/make_manifest.py --draft first): every checks[].cmd is run exactly as
# written with `bash -c` from the clone and its exit and count logged (review F1 of ACT-EXAMIN-SETS-1).
set -u
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/accepted-reds-1
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
CL=$D/tmp/clone
ACT=$D/acts/ACT-ACCEPTED-REDS-1
EX=$ORCH/acts/ACT-EXAMIN-SETS-1
T=$D/tools
PY=/home/usain/.local/share/gov-os/pin-797495bdfc70/bin/python
P=governance/project/path-map.yaml
LOG=$D/rehearsal.log
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
N=0
ok() { N=$((N + 1)); echo "ok   $1"; }
bad() { N=$((N + 1)); echo "FAIL $1"; FAILS=$((FAILS + 1)); }
OUT=$D/tmp/.rehearsal-out
expect_exit() { # expect_exit <label> <want> <cmd...>
  local label="$1" want="$2"; shift 2
  "$@" > $OUT 2>&1; local rc=$?
  sed 's/^/     /' $OUT | cut -c1-230 | head -40
  [ "$rc" = "$want" ] && ok "$label (exit $rc)" || bad "$label: want exit $want, got $rc"
}
sha() { sha256sum "$1" | cut -c1-64; }
j() { python3 -I -c "import json,sys; m=json.load(open('$D/tmp/manifest.draft.json')); $1"; }

echo "--- 0. set-up: a planted HOME, a fresh clone of the main tree's HEAD (w2/integrate)"
rm -rf $D/tmp/home $CL
mkdir -p $D/tmp/home
[ -f /home/usain/.gitconfig ] && cp -p /home/usain/.gitconfig $D/tmp/home/.gitconfig
export HOME=$D/tmp/home
git clone -q --no-hardlinks $MAIN $CL || { echo "FAIL clone"; echo "failures: 99"; exit 1; }
cd $CL || exit 1
echo "clone HEAD $(git rev-parse --short=12 HEAD) on $(git rev-parse --abbrev-ref HEAD); register holds DEC-1134: $(grep -c '^### DEC-1134 ' docs/DECISION_REGISTER.md)"
echo "main tree's map $(sha $MAIN/$P | cut -c1-12) (read only); clone's map $(sha $P | cut -c1-12); EXAMIN-SETS-1 before $(cut -d'|' -f3 $EX/list.txt | cut -c1-12), after $(cut -d'|' -f4 $EX/list.txt | cut -c1-12); this ACT's before $(cut -d'|' -f3 $ACT/list.txt | cut -c1-12), after $(cut -d'|' -f4 $ACT/list.txt | cut -c1-12)"
[ "$(sha $P)" = "$(cut -d'|' -f3 $EX/list.txt)" ] && ok "A0 the clone's map is EXAMIN-SETS-1's frozen before (fb52ab2d...)" || bad "A0 the clone's map is not EXAMIN-SETS-1's before"
[ "$(cut -d'|' -f3 $ACT/list.txt)" = "$(cut -d'|' -f4 $EX/list.txt)" ] && ok "A1 this ACT's before is EXAMIN-SETS-1's after (b1ffdb0b...)" || bad "A1 the chain is broken"
[ "$(sha $MAIN/$P)" = "$(cut -d'|' -f3 $EX/list.txt)" ] && ok "A2 the main tree's map (read only) is still EXAMIN-SETS-1's before" || bad "A2 the main tree's map moved"
cp -p $P $D/tmp/map.live-before
echo "git status of the clone: [$(git status --porcelain | wc -l)] lines"

echo "--- B. REVERSED ORDER: this ACT first, on the map as it is today (EXAMIN-SETS-1 not applied): it must refuse and touch nothing"
before_sha=$(sha $P)
expect_exit "B1 check refuses (state other)" 3 bash $ACT/apply.sh check
expect_exit "B2 apply refuses" 3 bash $ACT/apply.sh apply
expect_exit "B3 undo refuses" 3 bash $ACT/apply.sh undo
expect_exit "B4 verify refuses" 3 bash $ACT/apply.sh verify
[ "$(sha $P)" = "$before_sha" ] && ok "B5 the map is byte for byte as it was" || bad "B5 the map changed"
[ -z "$(git status --porcelain)" ] && ok "B6 the clone's git status is empty (nothing created beside the map)" || bad "B6 the clone has changes: $(git status --porcelain)"
[ -z "$(ls governance/project/ | grep act-tmp)" ] && ok "B7 no temp file left beside the map" || bad "B7 a temp file is left"

echo "--- C. ACT-EXAMIN-SETS-1 first (its own apply.sh, the plain apply), committed in the clone as the operator would"
expect_exit "C1 EXAMIN check: state before" 0 bash $EX/apply.sh check
expect_exit "C2 EXAMIN apply" 0 bash $EX/apply.sh apply
expect_exit "C3 EXAMIN verify" 0 bash $EX/apply.sh verify
git commit -q -m "ACT-EXAMIN-SETS-1: applied by the operator agent (rehearsal clone)" --trailer "Role: operator" --trailer "Act: ACT-EXAMIN-SETS-1" -- $P && ok "C4 EXAMIN committed in the clone" || bad "C4 commit"
[ "$(sha $P)" = "$(cut -d'|' -f3 $ACT/list.txt)" ] && ok "C5 the clone's map is now this ACT's frozen before (b1ffdb0b...)" || bad "C5 the map is not this ACT's before"

echo "--- D. this ACT's states before the apply"
expect_exit "D1 check: state before" 0 bash $ACT/apply.sh check
expect_exit "D2 verify refused before the apply" 3 bash $ACT/apply.sh verify
expect_exit "D3 undo before the apply says nothing to undo" 0 bash $ACT/apply.sh undo

echo "--- E. the PLAIN apply (no backup, no environment variable), as the operator runs it"
expect_exit "E1 apply" 0 bash $ACT/apply.sh apply
cmp -s $P $ACT/after/repo/$P && ok "E2 the map is the frozen after, byte for byte" || bad "E2 not the frozen after"
[ "$(stat -c %a $P)" = "$(stat -c %a $ACT/before/repo/$P)" ] && ok "E3 the mode is kept ($(stat -c %a $P))" || bad "E3 the mode changed"
st="$(git status --porcelain)"
[ "$st" = " M $P" ] && ok "E4 git status lists only the map: [$st]" || bad "E4 git status: [$st]"
[ -z "$(ls governance/project/ | grep -E 'act-tmp|\.bak')" ] && ok "E5 no temp or backup file beside the map" || bad "E5 a stray file"
expect_exit "E6 check: state applied" 0 bash $ACT/apply.sh check
expect_exit "E7 verify exit 0" 0 bash $ACT/apply.sh verify
expect_exit "E8 apply again changes nothing" 0 bash $ACT/apply.sh apply
git diff -U3 -- $P | tail -n +5 | sed 's/^\(@@ [^@]* @@\).*/\1/' > $D/tmp/clone.hunk   # git adds the nearest key after the second @@; diff(1) does not
tail -n +3 $D/accepted-reds.diff > $D/tmp/draft.hunk
cmp -s $D/tmp/clone.hunk $D/tmp/draft.hunk && ok "E9 the clone's diff (from the EXAMIN-applied map) is the drafted hunk, accepted-reds.diff, byte for byte (after its two header lines)" || bad "E9 the diff differs from the drafted hunk"
expect_exit "E10 pinned judge, applied but not yet committed by the owner: neither test counted, each refused as 'no commit of the history adds it'" 0 $PY -I $T/ratchet_probe.py $CL pending
git diff --numstat -- $P | sed 's/^/     numstat: /'

echo "--- F. every manifest checks[].cmd, exactly as written, with bash -c from the clone (review F1)"
ncheck=$(j "print(len(m['checks']))")
i=0
while [ "$i" -lt "$ncheck" ]; do
  cmd=$(j "print(m['checks'][$i]['cmd'])")
  want=$(j "print(m['checks'][$i]['exit'])")
  cnt=$(j "print(m['checks'][$i]['count'])")
  echo "     check $((i + 1)) cmd: $(echo "$cmd" | cut -c1-200)"
  ( cd $CL && bash -c "$cmd" ) > $OUT 2>&1; rc=$?
  sed 's/^/     out: /' $OUT | cut -c1-200 | head -10
  echo "     exit $rc (manifest says $want); count: n/a (manifest count: $cnt; no count is printed by this check)"
  [ "$rc" = "$want" ] && ok "F$((i + 1)) check $((i + 1)) as written: exit $rc" || bad "F$((i + 1)) check $((i + 1)): want $want, got $rc"
  i=$((i + 1))
done
mkdir -p $D/tmp/probe-before/governance/project
cp $ACT/before/repo/$P $D/tmp/probe-before/$P
cmd=$(j "print(m['checks'][1]['cmd'])")
( cd $D/tmp/probe-before && bash -c "$cmd" ) > /dev/null 2>&1; rc=$?
[ "$rc" = 1 ] && ok "F3 check 2 exits 1 on the before map, so it tells before from after (exit $rc)" || bad "F3 check 2 on the before map exits $rc"
echo "main tree's own checks, for the record: python3 -c 'import yaml' = $(python3 -c 'import yaml; print(yaml.__version__)' 2>&1 | tail -1)"

echo "--- G. the validate step (DEC-895) on the drafted patch with the pinned judge's readers, against the register as it stands"
expect_exit "G1 validate_entry.py (PASS for both, pending the owner's commit)" 0 $PY -E $ORCH/tools/validate_entry.py $D/accepted-reds.diff

echo "--- H. the owner's operator's commit, by hand, as the message gives it (Role: owner), then the pinned judge's ratchet reader"
cd $CL
git commit -q -m "ACT-ACCEPTED-REDS-1: accepted_reds lists the two warm real-model latency cases (W1-19, W2-13) until W2-155 closes (DEC-1134)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1134, DEC-1125" --trailer "Role: owner" -- governance/project/path-map.yaml && ok "H1 committed with Role: owner" || bad "H1 commit"
echo "     trailers: $(git log -1 --format='%(trailers:only,unfold,separator=; )')"
[ -z "$(git status --porcelain)" ] && ok "H2 the clone is clean after the commit" || bad "H2 not clean"
git branch -q owner-ok
expect_exit "H3 both tests counted (accepted) by gov.close.ratchet.counted_entries, no finding" 0 $PY -I $T/ratchet_probe.py $CL counted
( cd $CL && $PY -I -c 'from gov.close import ratchet; c,f=ratchet.counted_entries(".","accepted_reds"); print(len(c),len(f))' ) > $OUT 2>&1
[ "$(cat $OUT)" = "2 0" ] && ok "H3b the message's own one-line reader, run from the repository root: prints 2 0" || bad "H3b the one-line reader printed: $(cat $OUT)"
expect_exit "H4 apply_accepted_reds, both red: ok true, each covered (reported failed)" 0 $PY -I $T/ratchet_probe.py $CL both-red
expect_exit "H5 a listed test that passes: a finding, the entry must leave" 0 $PY -I $T/ratchet_probe.py $CL one-passes
expect_exit "H6 another red is still refused" 0 $PY -I $T/ratchet_probe.py $CL other-red
echo "--- H7. the same commit with Role: operator (what the operator agent would make): the ratchet refuses both entries"
git commit -q --amend -m "ACT-ACCEPTED-REDS-1: as an operator-agent commit" --trailer "Role: operator" --trailer "Act: ACT-ACCEPTED-REDS-1" -- governance/project/path-map.yaml >/dev/null
expect_exit "H7 both refused: added without Role: owner" 0 $PY -I $T/ratchet_probe.py $CL not-owner
git reset -q --hard owner-ok
expect_exit "H8 restored: both counted again" 0 $PY -I $T/ratchet_probe.py $CL counted

echo "--- I. undo, from the committed applied state"
expect_exit "I1 undo" 0 bash $ACT/apply.sh undo
cmp -s $P $ACT/before/repo/$P && ok "I2 the map is the frozen before, byte for byte" || bad "I2 undo differs"
[ "$(git status --porcelain)" = " M $P" ] && ok "I3 git status lists only the map" || bad "I3 git status: $(git status --porcelain)"
expect_exit "I4 undo again: nothing to undo" 0 bash $ACT/apply.sh undo
[ -z "$(ls governance/project/ | grep act-tmp)" ] && ok "I5 no temp file left" || bad "I5 a temp file is left"

echo "--- J. refusals (the map is the before again)"
echo "# changed later" >> $P
expect_exit "J1 check refuses a map that changed" 3 bash $ACT/apply.sh check
expect_exit "J2 apply refuses" 3 bash $ACT/apply.sh apply
expect_exit "J3 undo refuses" 3 bash $ACT/apply.sh undo
cp -p $ACT/before/repo/$P $P
mv $P $P.real && ln -s $P.real $P
expect_exit "J4 a link is refused by check" 3 bash $ACT/apply.sh check
expect_exit "J5 a link is refused by apply" 3 bash $ACT/apply.sh apply
rm $P && mv $P.real $P
cmp -s $P $ACT/before/repo/$P && ok "J6 link test left the map as it was" || bad "J6 map differs"
echo "sentinel" > $D/tmp/sentinel.txt
ln -s $D/tmp/sentinel.txt $P.act-tmp
expect_exit "J7 apply with a link planted at the old fixed temp name <map>.act-tmp" 0 bash $ACT/apply.sh apply
[ "$(cat $D/tmp/sentinel.txt)" = sentinel ] && ok "J8 the planted link's target is untouched (review F4)" || bad "J8 the link target was written"
cmp -s $P $ACT/after/repo/$P && ok "J9 the map is the frozen after" || bad "J9 the map differs"
rm -f $P.act-tmp
expect_exit "J10 undo" 0 bash $ACT/apply.sh undo
[ -z "$(ls governance/project/ | grep act-tmp)" ] && ok "J11 no temp file left (mktemp names removed)" || bad "J11 a temp file is left"
rm -rf $D/tmp/bundle-tampered; cp -r $ACT $D/tmp/bundle-tampered; echo "# tampered" >> $D/tmp/bundle-tampered/after/repo/$P
expect_exit "J12 a tampered frozen copy: apply exits 4" 4 bash $D/tmp/bundle-tampered/apply.sh apply
cmp -s $P $ACT/before/repo/$P && ok "J13 the map is untouched by the refused apply" || bad "J13 the map changed"
chmod a-w governance/project
expect_exit "J14 the map's folder not writable: apply exits 5 and nothing changes" 5 bash $ACT/apply.sh apply
chmod u+w governance/project
cmp -s $P $ACT/before/repo/$P && ok "J15 the map is untouched" || bad "J15 the map changed"
[ -z "$(ls governance/project/ | grep act-tmp)" ] && ok "J16 no temp file left" || bad "J16 a temp file is left"

echo "--- K. the live files are unchanged (read only)"
echo "main tree's map $(sha $MAIN/$P | cut -c1-12), EXAMIN-SETS-1's before $(cut -d'|' -f3 $EX/list.txt | cut -c1-12)"
[ "$(sha $MAIN/$P)" = "$(cut -d'|' -f3 $EX/list.txt)" ] && ok "K1 the main tree's map is unchanged" || bad "K1 the main tree's map changed (or EXAMIN-SETS-1 was applied meanwhile)"
echo
echo "checks run: $N"
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
