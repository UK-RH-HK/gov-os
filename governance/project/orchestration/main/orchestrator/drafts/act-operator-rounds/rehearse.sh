#!/usr/bin/env bash
# ACT-OPERATOR-ROUNDS-1's rehearsal (DEC-1057), round 2. Exactly as the owner will run it, only the root substituted:
# its own clone of w2/integrate (git clone --no-hardlinks of the main tree's committed head), HOME planted (a copy of the live
# install) under this folder's tmp/, the untracked tools and this folder's apply.sh and code/ copied into the clone at the
# same relative paths. The owner's steps are READ FROM section 5 of the package and run line by line (the `cd` line takes
# the clone's root); every other command is apply.sh's own. Writes only under $W (this folder's tmp/world); reads the live
# install and the main tree (cp and git clone only). The log ends with "failures: <n>".
#   bash rehearse.sh > rehearsal.log
# Results it logs that the package's section 6 reports (review round 1, P1-F5): the new cases on the OLD code, the CTO's
# tools/test_verdict.py on the old and the new verdict.py, and the whole operator and W2-148 suites on the applied tree.
# This ACT's package has no manifest.json (class (O): the owner applies it by hand; the operator refuses it at G6), so the
# "checks" are the owner's own lines from section 5, each run exactly as written with `bash -c`, with its exit logged.
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REAL=$(cd "$HERE/../../../../.." && pwd)
W=$HERE/tmp/world
export TMPDIR=$HERE/tmp
export PYTHONDONTWRITEBYTECODE=1
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
HOME_REAL=$HOME
REL=.gov-runtime/scratch/orchestrator/drafts/act-operator-rounds
TOOLS_REL=.gov-runtime/scratch/orchestrator/tools
fails=0
ok() { echo "ok:   $*"; }
bad() { echo "FAIL: $*"; fails=$((fails+1)); }
expect() {  # expect <0|nz> "<what>" cmd...   (stdout and stderr kept in $OUT)
  local want=$1 what=$2; shift 2
  OUT=$("$@" 2>&1); local rc=$?
  if { [ "$want" = 0 ] && [ $rc = 0 ]; } || { [ "$want" = nz ] && [ $rc != 0 ]; }; then ok "$what (exit $rc)"; else bad "$what (exit $rc, wanted $want): $(printf '%s' "$OUT" | tail -5)"; fi
}
has() { case "$OUT" in *"$1"*) ok "  output has: $1" ;; *) bad "  output lacks: $1 in: $(printf '%s' "$OUT" | tail -5)" ;; esac; }
hasnt() { case "$OUT" in *"$1"*) bad "  output has: $1" ;; *) ok "  output lacks: $1" ;; esac; }

# ------------------------------------------------------------------------------------------------ the world
FIVE="governance/project/operator tests/unit/operator tests/acceptance/W2-148"   # the five paths live in these folders; other helpers write elsewhere in the main tree meanwhile
live_status_before=$(git -C "$REAL" status --short -- $FIVE | LC_ALL=C sort | sha256sum | cut -c1-16)
live_inst_before=$(cd "$HOME_REAL/gov-os-operator/install" && find . -path ./__pycache__ -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)
rm -rf "$W"; mkdir -p "$W/home"
echo "== the clone: git clone --no-hardlinks of the main tree's committed head"
git clone -q --no-hardlinks "$REAL" "$W/root" && ok "cloned $(git -C "$W/root" branch --show-current) at $(git -C "$W/root" rev-parse HEAD | cut -c1-12)"
[ -z "$(git -C "$W/root" status --short)" ] && ok "the clone is clean" || bad "the clone is not clean"
mkdir -p "$W/root/$TOOLS_REL" "$W/root/$REL"
cp -a "$REAL/$TOOLS_REL/." "$W/root/$TOOLS_REL/" && find "$W/root/$TOOLS_REL" -name __pycache__ -prune -exec rm -rf {} +
cp -a "$HERE/apply.sh" "$HERE/code" "$W/root/$REL/"
[ -z "$(git -C "$W/root" status --short)" ] && ok "the untracked tools and drafts copied in (ignored by git, as in the main tree)" || bad "copying the tools and drafts changed git status"
echo "== the planted HOME: a copy of the live install (log/ and queue/ empty)"
mkdir -p "$W/home/gov-os-operator/log" "$W/home/gov-os-operator/queue"
chmod 700 "$W/home/gov-os-operator/queue"
cp -a "$HOME_REAL/gov-os-operator/install" "$W/home/gov-os-operator/install"
rm -rf "$W/home/gov-os-operator/install/__pycache__"
INST=$W/home/gov-os-operator/install
OP=$W/home/gov-os-operator
ROOT=$W/root
G=$ROOT/$REL

# The owner's lines, read from section 5 of the package (the first fenced block after "## 5."), each as written
mapfile -t OL < <(awk '/^## 5\./{s=1} s&&/^> ```$/{n++; next} s&&n==1&&/^> /{sub(/^> /,""); print} n==2{exit}' "$HERE/ACT-OPERATOR-ROUNDS-1.md")
[ "${#OL[@]}" = 8 ] && ok "section 5 holds 8 command lines" || bad "section 5 holds ${#OL[@]} command lines, wanted 8"
line() { printf '%s\n' "${OL[@]}" | grep -m1 -- "$1"; }
CD_LINE=$(line '^cd ')
G_LINE=$(line '^G=')
CHECK=$(line 'apply.sh check'); APPLY=$(line 'apply.sh apply'); SHA_LINE=$(line '^sha256sum'); STAT=$(line '^git status'); ADD=$(line '^git add'); COMMIT=$(line '^git commit')
UNDO='bash $G/apply.sh undo'      # section 5's "Undo:" line, as written there
for l in "$CD_LINE" "$G_LINE" "$CHECK" "$APPLY" "$SHA_LINE" "$STAT" "$ADD" "$COMMIT"; do [ -n "$l" ] || bad "a command line of section 5 was not found"; done
EXPECT_APPROVED=$(printf '%s' "$SHA_LINE" | grep -oE '[0-9a-f]{64}' | head -1)
grep -c "$EXPECT_APPROVED" "$HERE/ACT-OPERATOR-ROUNDS-1.md" | grep -qv '^0$' && ok "the package states the APPROVED to expect: ${EXPECT_APPROVED:0:12}" || bad "no APPROVED sha in section 5"
# `cd /home/usain/Dynamic-Agentic-Engineering-OS` becomes the clone's root; nothing else changes
owner() {  # owner "<a line as written>": from the root, HOME planted, G as the message sets it, run with bash -c
  ( cd "$ROOT" && eval "${G_LINE%%#*}" && export G && HOME=$W/home bash -c "$1" ) 2>&1
}
echo "   the cd line, as written: $CD_LINE  (run here as: cd $ROOT)"
echo "   the G line, as written:  $G_LINE"

# ------------------------------------------------------------------------------------------------ P1-F5 (a), (b)
pyt() {  # pyt <dir> <pytest args>: through the heavy gate, the user's pytest, the dir's own code
  local d=$1; shift
  ( cd "$d" && HOME=$W/home PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=$d/src \
      bash "$REAL/$TOOLS_REL/heavy_slot.sh" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed "$@" 2>&1 )
}
echo "== (a) the 17 new cases on the OLD code (the clone as committed, only the new test file added)"
cp "$HERE/code/tests/unit/operator/test_dec1131_rounds.py" "$ROOT/tests/unit/operator/"
pyt "$ROOT" tests/unit/operator/test_dec1131_rounds.py > "$W/old17.out"; tail -3 "$W/old17.out"
grep -q "14 failed, 3 passed" "$W/old17.out" && ok "the new cases on the old code: 14 fail, 3 pass (the 3 need no change)" || bad "old code: not 14 failed, 3 passed"
rm -f "$ROOT/tests/unit/operator/test_dec1131_rounds.py"
[ -z "$(git -C "$ROOT" status --short)" ] && ok "the clone is clean again" || bad "the clone is not clean"
echo "== (b) the CTO's tools/test_verdict.py on the old and the new verdict.py"
mkdir -p "$W/cto-old" "$W/cto-new"
cp "$HERE/before/cto-verdict.py" "$W/cto-old/verdict.py"; cp "$HERE/after/cto-test_verdict.py" "$W/cto-old/test_verdict.py"
cp "$HERE/after/cto-verdict.py" "$W/cto-new/verdict.py"; cp "$HERE/after/cto-test_verdict.py" "$W/cto-new/test_verdict.py"
pyt "$W/cto-old" test_verdict.py > "$W/cto-old.out"; tail -1 "$W/cto-old.out"
grep -q "3 failed, 5 passed" "$W/cto-old.out" && ok "test_verdict.py on the old verdict.py: 3 failed, 5 passed" || bad "old verdict.py: not 3 failed, 5 passed"
pyt "$W/cto-new" test_verdict.py > "$W/cto-new.out"; tail -1 "$W/cto-new.out"
grep -q "^8 passed" "$W/cto-new.out" && ok "test_verdict.py on the new verdict.py: 8 passed" || bad "new verdict.py: not 8 passed"
cmp -s "$HERE/after/cto-verdict.py" "$HERE/code/governance/project/operator/verdict.py" && ok "the CTO's verdict.py is the operator's, byte for byte" || bad "the two verdict.py differ"
cmp -s "$REAL/$TOOLS_REL/verdict.py" "$HERE/before/cto-verdict.py" && ok "the CTO's live tools/verdict.py is the 'before' file" || bad "live tools/verdict.py is not the 'before' file"

# ------------------------------------------------------------------------------------------------ apply.sh, the refusals
echo "== apply.sh, the cases (the owner's own lines where the message has them)"
expect 0 "the owner's check, on the before state" owner "$CHECK"; has "state: before"; has "check: ready to apply"
touch "$OP/queue/x.req"
expect nz "check refuses while a request waits in queue/" owner "$CHECK"; has "a request waits"
rm -f "$OP/queue/x.req"
touch "$INST/act-in-progress.txt"
expect nz "check refuses while the freeze is held" owner "$CHECK"; has "freeze is held"
rm -f "$INST/act-in-progress.txt"
touch "$OP/log/journal.json"
expect nz "apply refuses while the journal exists" owner "$APPLY"; has "journal"
rm -f "$OP/log/journal.json"
( exec 8>>"$OP/log/launch.lock"; flock -n 8; sleep 4 ) &
LOCKPID=$!
sleep 1
expect nz "apply refuses while a launch holds log/launch.lock" owner "$APPLY"; has "a launch is running"
wait "$LOCKPID"
[ ! -e "$G/backup" ] && ok "a refused apply left no backup/" || bad "a refused apply left backup/"
printf 'x' >> "$ROOT/governance/project/operator/verdict.py"
expect nz "check refuses a repository file moved since the build" owner "$CHECK"; has "neither as built before"
git -C "$ROOT" checkout -q -- governance/project/operator/verdict.py
expect 0 "check again on the before state" owner "$CHECK"
chmod u+w "$INST"; echo "# stray" > "$INST/stray.txt"
expect nz "check refuses an unlisted file in the install" owner "$CHECK"; has "neither as built before"
rm -f "$INST/stray.txt"
before_inst=$(cd "$INST" && find . -path ./__pycache__ -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum | sha256sum)
before_approved=$(sha256sum "$INST/APPROVED" | cut -c1-64)

# ------------------------------------------------------------------------------------------------ flow A: apply, look, test, undo
echo "== flow A: the owner's lines (check, apply, sha256sum, git status), the suites on the applied tree, then undo"
expect 0 "the owner's apply (plain, as typed)" owner "$APPLY"; has "the install's own APPROVED check: ok"; has "state applied"
echo "$OUT" | grep '^APPROVED ' | sed 's/^/   /'
expect 0 "the owner's sha256sum line" owner "$SHA_LINE"
case "$OUT" in "$EXPECT_APPROVED "*) ok "the APPROVED the package says to expect: $EXPECT_APPROVED" ;; *) bad "APPROVED is not the one section 5 expects: $OUT" ;; esac
expect 0 "the owner's git status line" owner "$STAT"
echo "$OUT" | sed 's/^/   /'
[ "$(echo "$OUT" | grep -c .)" = 5 ] && [ "$(echo "$OUT" | grep -c '^ M')" = 4 ] && [ "$(echo "$OUT" | grep -c '^??')" = 1 ] && ok "5 paths changed (4 M, 1 ??), as section 5 says" || bad "git status is not 4 M and 1 ??"
expect nz "a second apply is refused" owner "$APPLY"; has "not in the before state"
expect 0 "check reads already applied" owner "$CHECK"; has "already applied"
left=$(find "$INST" "$ROOT" -name '.*.act-operator-rounds-1.*' -not -path '*/.git/*' 2>/dev/null | wc -l)
[ "$left" = 0 ] && ok "no temp file left beside any written file (mktemp names removed by the rename)" || bad "$left temp files left"
[ -z "$(ls "$G/backup" | grep 'APPROVED.new')" ] && ok "no APPROVED.new.* left in backup/" || bad "APPROVED.new left in backup/"
echo "-- the installed files are byte for byte the repository's"
cmp "$INST/verdict.py" "$ROOT/governance/project/operator/verdict.py" && ok "install verdict.py = repository verdict.py" || bad "verdict.py differs"
cmp "$INST/operator_run.py" "$ROOT/governance/project/operator/operator_run.py" && ok "install operator_run.py = repository operator_run.py" || bad "operator_run.py differs"
(cd "$INST" && sha256sum -c --quiet APPROVED) && ok "every file in the install hashes as APPROVED says" || bad "APPROVED does not match"
echo "-- the operator's own unit tests and W2-148's acceptance tests on the applied tree (nothing deselected)"
pyt "$ROOT" tests/unit/operator tests/acceptance/W2-148 > "$W/pytest.out"; tail -4 "$W/pytest.out"
grep -qE "^[0-9]+ passed" <(tail -1 "$W/pytest.out") && ! tail -1 "$W/pytest.out" | grep -q "failed\|error" && ok "unit and acceptance tests pass on the applied tree: $(tail -1 "$W/pytest.out")" || bad "tests not all green"
echo "-- undo (before any commit)"
expect 0 "the owner's undo" owner "$UNDO"; has "state before (undone)"
[ "$(sha256sum "$INST/APPROVED" | cut -c1-64)" = "$before_approved" ] && ok "APPROVED as before" || bad "APPROVED differs after undo"
[ "$(cd "$INST" && find . -path ./__pycache__ -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum | sha256sum)" = "$before_inst" ] && ok "every install file byte for byte as before" || bad "install differs after undo"
[ -z "$(git -C "$ROOT" status --short)" ] && ok "the tree is clean again (git status empty)" || bad "the tree differs after undo"
expect nz "undo again is refused" owner "$UNDO"; has "not as this ACT left it"
expect 0 "check reads ready to apply again" owner "$CHECK"; has "check: ready to apply"

# ------------------------------------------------------------------------------------------------ flow B: the owner's whole message, then undo after the commit
echo "== flow B: the owner's whole message (apply, git add, git commit), then undo AFTER the commit"
expect 0 "apply" owner "$APPLY"
expect 0 "the owner's git add line" owner "$ADD"
expect 0 "the owner's git commit line, as written" owner "$COMMIT"; echo "   commit $(git -C "$ROOT" rev-parse HEAD | cut -c1-12), $(git -C "$ROOT" show --stat --format= HEAD | tail -1 | sed "s/^ *//")"
[ -z "$(git -C "$ROOT" status --short)" ] && ok "the tree is clean after the owner's commit" || bad "the tree is not clean after the commit"
git -C "$ROOT" log -1 --format=%B | grep -q "^Task: DAEO-sdxk" && git -C "$ROOT" log -1 --format=%B | grep -q "^Implements: DEC-1131" && ok "the commit carries the message's trailers" || bad "trailers missing"
expect 0 "undo after the commit (the working tree then differs from the commit)" owner "$UNDO"; has "state before (undone)"
[ "$(git -C "$ROOT" status --short | wc -l)" = 5 ] && ok "undo after the commit leaves 5 paths in the working tree (4 M, 1 D), as section 5 says" || bad "undo after commit: not 5 paths"
git -C "$ROOT" add governance/project/operator/verdict.py governance/project/operator/operator_run.py tests/unit/operator/test_w2_148_parts.py tests/acceptance/W2-148/w2_148_support.py tests/unit/operator/test_dec1131_rounds.py
git -C "$ROOT" commit -q -m "ACT-OPERATOR-ROUNDS-1 undone" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1131" --trailer "Role: owner" && ok "the undone commit (the same five paths, the same three trailers)" || bad "the undone commit failed"
[ -z "$(git -C "$ROOT" status --short)" ] && ok "clean after the undone commit" || bad "not clean after the undone commit"
expect 0 "check reads ready to apply again" owner "$CHECK"; has "check: ready to apply"

# ------------------------------------------------------------------------------------------------ the tampered backups (P1-F2)
echo "== a tampered backup stops the undo (before any write)"
expect 0 "apply again" owner "$APPLY"
chmod u+w "$G/backup/install/verdict.py"; echo x >> "$G/backup/install/verdict.py"
expect nz "undo refuses an install backup that does not match its SHA256SUMS" owner "$UNDO"; has "does not match its SHA256SUMS"
cp -p "$REAL/governance/project/operator/verdict.py" "$G/backup/install/verdict.py"
BV=$G/backup/repo/governance/project/operator/verdict.py
echo "# tampered together with its SHA256SUMS" >> "$BV"
( cd "$G/backup" && find install repo -type f | LC_ALL=C sort | xargs sha256sum > SHA256SUMS )
snap=$(git -C "$ROOT" status --short | LC_ALL=C sort | sha256sum); sums=$(cd "$INST" && sha256sum verdict.py operator_run.py APPROVED)
expect nz "undo refuses a repository backup altered together with its SHA256SUMS (P1-F2)" owner "$UNDO"; has "is not the before file"; has "nothing changed"
[ "$(git -C "$ROOT" status --short | LC_ALL=C sort | sha256sum)" = "$snap" ] && [ "$(cd "$INST" && sha256sum verdict.py operator_run.py APPROVED)" = "$sums" ] && ok "nothing was written: the tree and the install are as the refusal found them" || bad "the refused undo wrote something"
cp -p "$REAL/governance/project/operator/verdict.py" "$BV"
( cd "$G/backup" && find install repo -type f | LC_ALL=C sort | xargs sha256sum > SHA256SUMS )
expect 0 "undo with the backups mended" owner "$UNDO"
[ -z "$(git -C "$ROOT" status --short)" ] && ok "clean again" || bad "tree differs"

# ------------------------------------------------------------------------------------------------ a stop part way (P1-F3)
echo "== apply stops part way: the repository files written, the install folder not writable"
chmod a-w "$INST"
expect nz "apply stops part way when the install cannot be written" owner "$APPLY"; has "stopped part way"; has "restore by hand"; has "cp -pf"
RESTORE=$OUT
chmod u+w "$INST"
[ "$(git -C "$ROOT" status --short | wc -l)" = 5 ] && ok "the repository step had been done (5 paths changed), so undo has no applied state to take" || bad "the repository step was not done"
expect nz "undo refuses the part-way state" owner "$UNDO"; has "not as this ACT left it"
printf '%s\n' "$RESTORE" | grep -E '^  (cp|rm) ' | sed 's/^  //' > "$W/restore.lines"
[ "$(wc -l < "$W/restore.lines")" = 7 ] && ok "the message names 7 restore lines (the install's 3 files in two lines, and the five repository paths)" || bad "restore lines: $(wc -l < "$W/restore.lines")"
expect 0 "the printed restore lines, run exactly as printed" bash "$W/restore.lines"
mv "$G/backup" "$W/backup.partial"
[ -z "$(git -C "$ROOT" status --short)" ] && ok "after the hand restore the tree is clean" || bad "tree differs after the hand restore"
expect 0 "after the hand restore check reads before" owner "$CHECK"; has "state: before"; has "check: ready to apply"
[ "$(cd "$INST" && find . -path ./__pycache__ -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum | sha256sum)" = "$before_inst" ] && ok "every install file as at the start" || bad "install differs after the hand restore"

# ------------------------------------------------------------------------------------------------ history scan (P1-F7)
echo "== the committed records with a verdict block, read only (scan_history.py, hidden and memory-verdict paths excluded)"
mkdir -p "$W/oldv"; cp "$HERE/before/verdict.py" "$W/oldv/verdict_old.py"
python3 -I "$HERE/scan_history.py" "$ROOT" "$W/oldv" > "$W/scan.out" 2>&1; cat "$W/scan.out"
grep -q "^records with a verdict block: 57$" "$W/scan.out" && grep -q "marked fail in the last block\|last block has a KPI marked fail: 3" "$W/scan.out" && ok "57 records, 3 change reading (the package says the same)" || bad "the scan differs from the package's 57 and 3"

echo "== the live files are untouched"
sha256sum "$HOME_REAL/gov-os-operator/install/verdict.py" "$HOME_REAL/gov-os-operator/install/operator_run.py" | cut -c1-12
[ "$(sha256sum "$HOME_REAL/gov-os-operator/install/APPROVED" | cut -c1-64)" = b4a15c8f3b7c769259f25b8d71406e6c7d387d30c021343f26f4bad6e3831fa4 ] && ok "live APPROVED unchanged" || bad "live APPROVED changed"
[ "$(sha256sum "$HOME_REAL/gov-os-operator/install/verdict.py" | cut -c1-64)" = 277c8ca9f06c90906397579f4d5bd144fb506a40b0836eb2a8f9c1443d909378 ] && ok "live verdict.py unchanged" || bad "live verdict.py changed"
[ "$(cd "$HOME_REAL/gov-os-operator/install" && find . -path ./__pycache__ -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)" = "$live_inst_before" ] && ok "every live install file unchanged" || bad "a live install file changed"
[ "$(git -C "$REAL" status --short -- $FIVE | LC_ALL=C sort | sha256sum | cut -c1-16)" = "$live_status_before" ] && ok "the live tree's git status unchanged under the three folders the five paths live in" || bad "the live tree's git status changed under those folders"
[ ! -e "$HERE/backup" ] && ok "no backup/ in the live drafts folder" || bad "backup/ in the live drafts folder"
echo "failures: $fails"
