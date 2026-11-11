#!/usr/bin/env bash
# ACT-OPERATOR-ROUNDS-1's rehearsal (DEC-1057): apply.sh on a planted HOME (a copy of the live install) and a planted tree
# (a git repository holding the repository files as they are now), then the operator's own unit tests and W2-148's
# acceptance tests on the applied tree. Writes only under $W (this folder's tmp/world). Reads the live install (cp only).
#   bash rehearse.sh > rehearsal.log        (the log ends with "failures: <n>")
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REAL=$(cd "$HERE/../../../../.." && pwd)
W=$HERE/tmp/world
export TMPDIR=$HERE/tmp
export PYTHONDONTWRITEBYTECODE=1
fails=0
ok() { echo "ok:   $*"; }
bad() { echo "FAIL: $*"; fails=$((fails+1)); }
expect() {  # expect <0|nonzero> "<what>" cmd...   (stdout and stderr kept in $OUT)
  local want=$1 what=$2; shift 2
  OUT=$("$@" 2>&1); local rc=$?
  if { [ "$want" = 0 ] && [ $rc = 0 ]; } || { [ "$want" = nz ] && [ $rc != 0 ]; }; then ok "$what (exit $rc)"; else bad "$what (exit $rc, wanted $want): $OUT"; fi
}
has() { case "$OUT" in *"$1"*) ok "  output has: $1" ;; *) bad "  output lacks: $1 in: $OUT" ;; esac; }

rm -rf "$W"; mkdir -p "$W/home" "$W/root"
echo "== the planted HOME: a copy of the live install"
mkdir -p "$W/home/gov-os-operator/log" "$W/home/gov-os-operator/queue"
chmod 700 "$W/home/gov-os-operator/queue"
cp -a "$HOME/gov-os-operator/install" "$W/home/gov-os-operator/install"
rm -rf "$W/home/gov-os-operator/install/__pycache__"
echo "== the planted tree: the repository files as they are now, in a git repository of its own"
for p in governance/project/operator tests/unit/operator tests/acceptance/W2-148 tests/acceptance/conftest.py tests/conftest.py \
         governance/project/indep-walls governance/project/orchestration/tools docs/changes/W2-148-evidence.md \
         governance/project/orchestration/packages/ACT-OPERATOR-1.md governance/project/orchestration/packages/OPERATOR-AGENT-1.md; do
  [ -e "$REAL/$p" ] || continue
  mkdir -p "$W/root/$(dirname "$p")"; cp -a "$REAL/$p" "$W/root/$p"
done
find "$W/root" -name __pycache__ -prune -exec rm -rf {} +
G=$W/root/.gov-runtime/scratch/orchestrator/drafts/act-operator-rounds
mkdir -p "$G"; cp -a "$HERE/apply.sh" "$HERE/code" "$G/"
git -C "$W/root" init -q -b main && echo ".gov-runtime/" >> "$W/root/.git/info/exclude" && git -C "$W/root" add -A >/dev/null 2>&1
git -C "$W/root" -c user.email=t@t -c user.name=t commit -q -m base && ok "the planted tree committed"
git -C "$W/root" status --short | head -3
HOME_REAL=$HOME
run() { HOME=$W/home bash "$G/apply.sh" "$@"; }
INST=$W/home/gov-os-operator/install
OP=$W/home/gov-os-operator

echo "== apply.sh, the cases"
expect 0 "check on the before state" run check; has "state: before"; has "check: ready to apply"
touch "$OP/queue/x.req"
expect nz "check refuses while a request waits in queue/" run check; has "a request waits"
rm -f "$OP/queue/x.req"
touch "$INST/act-in-progress.txt"
expect nz "check refuses while the freeze is held" run check; has "freeze is held"
rm -f "$INST/act-in-progress.txt"
touch "$OP/log/journal.json"
expect nz "apply refuses while the journal exists" run apply; has "journal"
rm -f "$OP/log/journal.json"
( exec 8>>"$OP/log/launch.lock"; flock -n 8; sleep 4 ) &
sleep 1
expect nz "apply refuses while a launch holds log/launch.lock" run apply; has "a launch is running"
wait
printf 'x' >> "$W/root/governance/project/operator/verdict.py"
expect nz "check refuses a repository file moved since the build" run check; has "neither as built before"
git -C "$W/root" checkout -q -- governance/project/operator/verdict.py
expect 0 "check again on the before state" run check
chmod u+w "$INST"; echo "# stray" > "$INST/stray.txt"
expect nz "check refuses an unlisted file in the install" run check; has "neither as built before"
rm -f "$INST/stray.txt"
before_inst=$(cd "$INST" && find . -path ./__pycache__ -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum | sha256sum)
before_approved=$(sha256sum "$INST/APPROVED" | cut -c1-64)
expect 0 "apply" run apply; has "the install's own APPROVED check: ok"; has "state applied"
echo "$OUT" | grep '^APPROVED ' | sed 's/^/   /'
expect nz "a second apply is refused" run apply; has "not in the before state"
expect 0 "check reads already applied" run check; has "already applied"
echo "-- the installed files are byte for byte the repository's"
cmp "$INST/verdict.py" "$W/root/governance/project/operator/verdict.py" && ok "install verdict.py = repository verdict.py" || bad "verdict.py differs"
cmp "$INST/operator_run.py" "$W/root/governance/project/operator/operator_run.py" && ok "install operator_run.py = repository operator_run.py" || bad "operator_run.py differs"
(cd "$INST" && sha256sum -c --quiet APPROVED) && ok "every file in the install hashes as APPROVED says" || bad "APPROVED does not match"
echo "-- the main tree after apply: what the owner commits"
git -C "$W/root" status --short
[ "$(git -C "$W/root" status --short | wc -l)" = 5 ] && ok "5 paths changed (4 M, 1 new)" || bad "not 5 paths"
echo "-- the operator's own tests and W2-148's acceptance tests on the applied tree (two deselected by name: each reads the real repository's history, commit 116c2b413 and the packages' ACT files, which a planted tree lacks; neither reads anything this ACT changes)"
( cd "$W/root" && bash "$REAL/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh" pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -k 'not test_s23_the_record_has_a_row_per_act_file_with_its_class and not test_no_act_file_is_classed_lower_than_the_table' tests/unit/operator tests/acceptance/W2-148 2>&1 | tail -4 ) > "$W/pytest.out"
cat "$W/pytest.out"
grep -q "^ *[0-9]* passed" "$W/pytest.out" && ! grep -q "failed" "$W/pytest.out" && ok "unit and acceptance tests pass on the applied tree" || bad "tests not all green"
echo "-- undo"
expect 0 "undo" run undo; has "state before (undone)"
[ "$(sha256sum "$INST/APPROVED" | cut -c1-64)" = "$before_approved" ] && ok "APPROVED as before" || bad "APPROVED differs after undo"
[ "$(cd "$INST" && find . -path ./__pycache__ -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum | sha256sum)" = "$before_inst" ] && ok "every install file byte for byte as before" || bad "install differs after undo"
[ -z "$(git -C "$W/root" status --short)" ] && ok "the tree is clean again (git status empty)" || bad "the tree differs after undo"
expect nz "undo again is refused" run undo; has "not as this ACT left it"
expect 0 "check reads ready to apply again" run check; has "check: ready to apply"
echo "-- a tampered backup stops the undo"
expect 0 "apply again" run apply
chmod u+w "$G/backup/install/verdict.py"; echo x >> "$G/backup/install/verdict.py"
expect nz "undo refuses a backup that does not match its SHA256SUMS" run undo; has "does not match its SHA256SUMS"
cp -p "$REAL/governance/project/operator/verdict.py" "$G/backup/install/verdict.py"
expect 0 "undo with the backup mended" run undo
[ -z "$(git -C "$W/root" status --short)" ] && ok "clean again" || bad "tree differs"

echo "== the live files are untouched"
sha256sum "$HOME_REAL/gov-os-operator/install/verdict.py" "$HOME_REAL/gov-os-operator/install/operator_run.py" | cut -c1-12
[ "$(sha256sum "$HOME_REAL/gov-os-operator/install/APPROVED" | cut -c1-64)" = b4a15c8f3b7c769259f25b8d71406e6c7d387d30c021343f26f4bad6e3831fa4 ] && ok "live APPROVED unchanged" || bad "live APPROVED changed"
[ "$(sha256sum "$HOME_REAL/gov-os-operator/install/verdict.py" | cut -c1-64)" = 277c8ca9f06c90906397579f4d5bd144fb506a40b0836eb2a8f9c1443d909378 ] && ok "live verdict.py unchanged" || bad "live verdict.py changed"
echo "failures: $fails"
