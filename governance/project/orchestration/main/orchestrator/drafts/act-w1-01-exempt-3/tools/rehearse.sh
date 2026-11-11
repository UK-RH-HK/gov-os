#!/bin/bash
# ACT-W1-01-EXEMPT-3's rehearsal, as the owner's operator will run it, in a --no-hardlinks clone of w2/integrate under
# drafts/act-w1-01-exempt-3/tmp/clone, with HOME planted under tmp/home. Only the repository root is substituted (the clone for
# the main tree). Nothing live is changed (the main tree is only cloned from and its map hashed, read only).
#   bash rehearse.sh            runs every step; the log is ../rehearsal.first.log (ends "failures: <n>")
# It reads tmp/manifest.first.draft.json (python3 -I tools/build.py first --draft first): every checks[].cmd is run exactly
# as written with `bash -c` from the clone and its exit logged (review F1 of ACT-EXAMIN-SETS-1). The log holds no live head,
# pid, date or live count line (review lessons of ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1), so a re-run gives the same bytes.
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
D=$ORCH/drafts/act-w1-01-exempt-3
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
CL=$D/tmp/clone
ACT=$D/acts/ACT-W1-01-EXEMPT-3
EX=$ORCH/acts/ACT-EXAMIN-SETS-1
PY=$(head -1 /home/usain/.local/bin/gov | cut -c3-)
P=governance/project/path-map.yaml
LOG=$D/rehearsal.first.log
CASES="tests/acceptance/W1-01/test_w1_01_history.py::test_only_the_test_designer_commits_to_acceptance_tests tests/acceptance/W1-01/test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass"
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
ok() { echo "ok   $1"; }
bad() { echo "FAIL $1"; FAILS=$((FAILS + 1)); }
OUT=$D/tmp/.rehearsal-out
expect_exit() { # expect_exit <label> <want> <cmd...>
  local label="$1" want="$2"; shift 2
  "$@" > $OUT 2>&1; local rc=$?
  sed 's/^/     /' $OUT | cut -c1-230 | head -40
  [ "$rc" = "$want" ] && ok "$label (exit $rc)" || bad "$label: want exit $want, got $rc"
}
sha() { sha256sum "$1" | cut -c1-64; }
j() { python3 -I -c "import json,sys; m=json.load(open('$D/tmp/manifest.first.draft.json')); $1"; }
w101() { # w101: run W1-01's two history cases (the ones that judge DEC-253 and acceptance_exemptions) in the clone; sets W_RC, W_SUM, W_WHO
  ( cd $CL && PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$CL/src TMPDIR=$D/tmp bash $ORCH/tools/heavy_slot.sh python3 -m pytest $CASES -q -p no:cacheprovider -o tmp_path_retention_policy=failed --no-header ) > $D/tmp/.w101.out 2>&1
  W_RC=$?
  W_SUM=$(grep -E "^[0-9]+ (passed|failed)" $D/tmp/.w101.out | tail -1 | sed 's/ in [0-9.]*s.*//')
  W_WHO=$(grep -E "^E +[0-9a-f]{12}$" $D/tmp/.w101.out | sed 's/^E *//' | tr '\n' ' ')
}

echo "--- 0. set-up: a planted HOME, a fresh clone of the main tree's HEAD (w2/integrate)"
rm -rf $D/tmp/home $CL
mkdir -p $D/tmp/home
[ -f /home/usain/.gitconfig ] && cp -p /home/usain/.gitconfig $D/tmp/home/.gitconfig
export HOME=$D/tmp/home
git clone -q --no-hardlinks $MAIN $CL || { echo "FAIL clone"; echo "failures: 99"; exit 1; }
git -C $CL rev-parse --short=12 HEAD > $D/tmp/clone.head   # kept out of the hashed log
cd $CL || exit 1
echo "the main tree's map $(sha $MAIN/$P | cut -c1-12) (read only); the clone's map $(sha $P | cut -c1-12); the bundle's before $(cut -d'|' -f3 $ACT/list.txt | cut -c1-12), after $(cut -d'|' -f4 $ACT/list.txt | cut -c1-12)"
[ "$(sha $P)" = "$(cut -d'|' -f3 $ACT/list.txt)" ] && ok "A0 the clone's map is the frozen before (the bundle is not stale)" || bad "A0 the clone's map is not the frozen before"
[ "$(sha $MAIN/$P)" = "$(cut -d'|' -f3 $ACT/list.txt)" ] && ok "A1 the main tree's map (read only) is the frozen before" || bad "A1 the main tree's map moved"
[ -z "$(git status --porcelain)" ] && ok "A2 the clone is clean" || bad "A2 the clone is not clean"
git log -1 --format=%s 6fbe73b1adde40571f00d490b4b478cf86b70a52 | cut -c1-60 | sed 's/^/     the owner commit: /'
echo "     its Role trailer: $(git log -1 --format='%(trailers:key=Role,valueonly)' 6fbe73b1adde40571f00d490b4b478cf86b70a52 | tr -d '\n')"
echo "     its acceptance-test change: $(git diff-tree --no-commit-id --name-only -r 6fbe73b1adde40571f00d490b4b478cf86b70a52 -- tests/acceptance | tr '\n' ' ')"
echo "     DEC-1136 in the clone's register: $(grep -c '^### DEC-1136 ' docs/DECISION_REGISTER.md) entry"

echo "--- A3. W1-01's two cases that judge DEC-253 and acceptance_exemptions, BEFORE the apply: red, naming 6fbe73b1adde"
w101
echo "     pytest exit $W_RC; $W_SUM; named: $W_WHO"
{ [ "$W_RC" != 0 ] && [ "$W_SUM" = "1 failed, 1 passed" ] && [ "$W_WHO" = "6fbe73b1adde " ]; } && ok "A3 red before: the history case fails naming 6fbe73b1adde only; the merges case passes" || bad "A3 not the expected red ($W_SUM; $W_WHO)"

echo "--- B. the states before the apply"
expect_exit "B1 check: state before" 0 bash $ACT/apply.sh check
expect_exit "B2 verify refused before the apply" 3 bash $ACT/apply.sh verify
expect_exit "B3 undo before the apply says nothing to undo" 0 bash $ACT/apply.sh undo

echo "--- C. the PLAIN apply (no backup, no environment variable), as the operator runs it"
expect_exit "C1 apply" 0 bash $ACT/apply.sh apply
cmp -s $P $ACT/after/repo/$P && ok "C2 the map is the frozen after, byte for byte" || bad "C2 not the frozen after"
[ "$(stat -c %a $P)" = "$(stat -c %a $ACT/before/repo/$P)" ] && ok "C3 the mode is kept ($(stat -c %a $P))" || bad "C3 the mode changed"
st="$(git status --porcelain)"
[ "$st" = " M $P" ] && ok "C4 git status lists only the map: [$st]" || bad "C4 git status: [$st]"
[ -z "$(ls governance/project/ | grep -E 'act-tmp|\.bak')" ] && ok "C5 no temp or backup file beside the map" || bad "C5 a stray file"
expect_exit "C6 check: state applied" 0 bash $ACT/apply.sh check
expect_exit "C7 verify exit 0" 0 bash $ACT/apply.sh verify
expect_exit "C8 apply again changes nothing" 0 bash $ACT/apply.sh apply
git diff -- $P > $D/path-map.diff
echo "     the diff against the map: $(git diff --numstat -- $P | tr '\t' ' ')"
[ "$(git diff --numstat -- $P | cut -f1,2 | tr '\t' ' ')" = "2 0" ] && ok "C9 two lines added, none removed" || bad "C9 numstat is not 2 0"
grep -c '^+' $D/path-map.diff > /dev/null
[ "$(git diff -U0 -- $P | grep -c '^+  - commit: "6fbe73b1adde40571f00d490b4b478cf86b70a52"')" = 1 ] && ok "C10 the added entry names the full id" || bad "C10 the entry's id"

echo "--- D. every manifest checks[].cmd, exactly as written, with bash -c from the clone (review F1)"
ncheck=$(j "print(len(m['checks']))")
i=0
while [ "$i" -lt "$ncheck" ]; do
  cmd=$(j "print(m['checks'][$i]['cmd'])")
  want=$(j "print(m['checks'][$i]['exit'])")
  cnt=$(j "print(m['checks'][$i]['count'])")
  echo "     check $((i + 1)) cmd: $(echo "$cmd" | cut -c1-160)..."
  ( cd $CL && bash -c "$cmd" ) > $OUT 2>&1; rc=$?
  sed 's/^/     out: /' $OUT | cut -c1-200 | head -10
  echo "     exit $rc (manifest says $want); manifest count: $cnt (the check prints no count)"
  [ "$rc" = "$want" ] && ok "D$((i + 1)) check $((i + 1)) as written: exit $rc" || bad "D$((i + 1)) check $((i + 1)): want $want, got $rc"
  i=$((i + 1))
done
mkdir -p $D/tmp/probe-before/governance/project
cp $ACT/before/repo/$P $D/tmp/probe-before/$P
cmd=$(j "print(m['checks'][1]['cmd'])")
( cd $D/tmp/probe-before && bash -c "$cmd" ) > /dev/null 2>&1; rc=$?
[ "$rc" = 1 ] && ok "D3 check 2 exits 1 on the before map, so it tells before from after (exit $rc)" || bad "D3 check 2 on the before map exits $rc"

echo "--- E. the validate step (DEC-895) on the patch, with the pinned judge's readers, against the register as it stands (it holds DEC-1136)"
expect_exit "E1 validate_entry.py (PASS: DEC-1136 is the owner's and names 6fbe73b1a)" 0 $PY -E $ORCH/tools/validate_entry.py $D/path-map.diff
expect_exit "E2 placeholder scan of the patch" 0 python3 -I $ORCH/tools/placeholder_scan.py $D/path-map.diff

echo "--- F. the owner's operator's commit, by hand, as the package's section 5 gives it (Role: owner); then W1-01 must be green"
git commit -q -m "ACT-W1-01-EXEMPT-3: acceptance_exemptions lists the owner's ACT-OPERATOR-ROUNDS-1 commit 6fbe73b1adde (DEC-1136 (1))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1136, DEC-906, DEC-253" --trailer "Role: owner" -- governance/project/path-map.yaml
echo "     trailers: $(git log -1 --format='%(trailers:only,unfold,separator=; )')"
[ -z "$(git status --porcelain)" ] && ok "F1 the clone is clean after the commit" || bad "F1 not clean"
git branch -q owner-ok
w101
echo "     pytest exit $W_RC; $W_SUM"
{ [ "$W_RC" = 0 ] && [ "$W_SUM" = "2 passed" ]; } && ok "F2 W1-01's two cases are green after the owner's commit: 2 passed" || bad "F2 not green ($W_SUM; $W_WHO)"
( cd $CL && $PY -I -c 'import sys,yaml; from pathlib import Path; from gov.close import gates; s=yaml.safe_load(open("governance/project/path-map.yaml")); print("6fbe73b1adde40571f00d490b4b478cf86b70a52" in gates.owner_listed(Path("."), s))' ) > $OUT 2>&1
[ "$(cat $OUT)" = True ] && ok "F3 the close's gate (h) reader, gates.owner_listed, counts the commit as owner-listed under DEC-1136" || bad "F3 owner_listed printed: $(head -c 200 $OUT)"
echo "--- F4. information, not a gate: the same entry committed as Role: operator (what the operator agent would make)"
git commit -q --amend -m "ACT-W1-01-EXEMPT-3: as an operator-agent commit" --trailer "Role: operator" --trailer "Act: ACT-W1-01-EXEMPT-3" -- governance/project/path-map.yaml >/dev/null
w101
echo "     W1-01's cases with the entry in a Role: operator commit: pytest exit $W_RC; $W_SUM (W1-01 reads the list by full id and decision shape only; that the entry is the owner's own commit is DEC-906's rule and class-rules.yaml's row path-map, class (O))"
git reset -q --hard owner-ok

echo "--- G. undo, from the committed applied state"
expect_exit "G1 undo" 0 bash $ACT/apply.sh undo
cmp -s $P $ACT/before/repo/$P && ok "G2 the map is the frozen before, byte for byte" || bad "G2 undo differs"
[ "$(git status --porcelain)" = " M $P" ] && ok "G3 git status lists only the map" || bad "G3 git status: $(git status --porcelain)"
expect_exit "G4 undo again: nothing to undo" 0 bash $ACT/apply.sh undo
[ -z "$(ls governance/project/ | grep act-tmp)" ] && ok "G5 no temp file left" || bad "G5 a temp file is left"

echo "--- H. refusals (the map is the before again)"
echo "# changed later" >> $P
expect_exit "H1 check refuses a map that changed" 3 bash $ACT/apply.sh check
expect_exit "H2 apply refuses" 3 bash $ACT/apply.sh apply
expect_exit "H3 undo refuses" 3 bash $ACT/apply.sh undo
expect_exit "H3b verify refuses" 3 bash $ACT/apply.sh verify
cp -p $ACT/before/repo/$P $P
echo "--- H4. another path-map ACT applied first (ACT-EXAMIN-SETS-1's after copy as the map): this ACT refuses and touches nothing"
cp -p $EX/after/repo/$P $P
b4=$(sha $P)
expect_exit "H4a check refuses (state other)" 3 bash $ACT/apply.sh check
expect_exit "H4b apply refuses" 3 bash $ACT/apply.sh apply
expect_exit "H4c undo refuses" 3 bash $ACT/apply.sh undo
[ "$(sha $P)" = "$b4" ] && ok "H4d the map is byte for byte as it was" || bad "H4d the map changed"
[ -z "$(ls governance/project/ | grep act-tmp)" ] && ok "H4e no temp file left" || bad "H4e a temp file is left"
cp -p $ACT/before/repo/$P $P
mv $P $P.real && ln -s $P.real $P
expect_exit "H5 a link is refused by check" 3 bash $ACT/apply.sh check
expect_exit "H6 a link is refused by apply" 3 bash $ACT/apply.sh apply
rm $P && mv $P.real $P
cmp -s $P $ACT/before/repo/$P && ok "H7 the link test left the map as it was" || bad "H7 map differs"
echo "sentinel" > $D/tmp/sentinel.txt
ln -s $D/tmp/sentinel.txt $P.act-tmp
expect_exit "H8 apply with a link planted at the old fixed temp name <map>.act-tmp" 0 bash $ACT/apply.sh apply
[ "$(cat $D/tmp/sentinel.txt)" = sentinel ] && ok "H9 the planted link's target is untouched (review F4)" || bad "H9 the link target was written"
cmp -s $P $ACT/after/repo/$P && ok "H10 the map is the frozen after" || bad "H10 the map differs"
rm -f $P.act-tmp
expect_exit "H11 undo" 0 bash $ACT/apply.sh undo
[ -z "$(ls governance/project/ | grep act-tmp)" ] && ok "H12 no temp file left (mktemp names removed)" || bad "H12 a temp file is left"
rm -rf $D/tmp/bundle-tampered; cp -r $ACT $D/tmp/bundle-tampered; echo "# tampered" >> $D/tmp/bundle-tampered/after/repo/$P
expect_exit "H13 a tampered frozen copy: apply exits 4" 4 bash $D/tmp/bundle-tampered/apply.sh apply
cmp -s $P $ACT/before/repo/$P && ok "H14 the map is untouched by the refused apply" || bad "H14 the map changed"
chmod a-w governance/project
expect_exit "H15 the map's folder not writable: apply exits 5 and nothing changes" 5 bash $ACT/apply.sh apply
chmod u+w governance/project
cmp -s $P $ACT/before/repo/$P && ok "H16 the map is untouched" || bad "H16 the map changed"
[ -z "$(ls governance/project/ | grep act-tmp)" ] && ok "H17 no temp file left" || bad "H17 a temp file is left"

echo "--- K. the live files are unchanged (read only)"
echo "the main tree's map $(sha $MAIN/$P | cut -c1-12), the frozen before $(cut -d'|' -f3 $ACT/list.txt | cut -c1-12)"
[ "$(sha $MAIN/$P)" = "$(cut -d'|' -f3 $ACT/list.txt)" ] && ok "K1 the main tree's map is unchanged" || bad "K1 the main tree's map changed (or this ACT was applied meanwhile)"
echo
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
