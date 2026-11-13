#!/bin/bash
# ACT-EXAMIN-WRITERS-INSTALL-1's rehearsal (DEC-1057): a --no-hardlinks clone of w2/integrate, a planted HOME and a planted
# sets root under /tmp/claude-1000/ewi-tmp/work. The real sets root and the run folders are never named: HOME is the
# planted one for every command, so the path map's "~/gov-os-eval" resolves to the planted root. The planted list holds
# the six template lines hashed from the clone's own template (the dry launch's stage 11 needs them) and brief and
# operator lines in the list's form with INVENTED hashes. Writes only under the work folder and this bundle's rehearsal.log.
#   bash rehearse.sh          (ends "failures: <n>")
set -u
A=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/ACT-EXAMIN-WRITERS-INSTALL-1
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
W=/tmp/claude-1000/ewi-tmp/work
LOG=$A/rehearsal.log
PY=/home/usain/.local/share/gov-os/pin-797495bdfc70/bin/python
[ -x "$PY" ] || PY=python3
export TMPDIR=/tmp/claude-1000/ewi-tmp
export HOME=$W/home
LAUNCHER=governance/project/orchestration/tools/indep_launch.py
P1=governance/project/indep-briefs/examin-sets/EXAMIN-writer.md
H1=d37834e08c86e24c0fdb1884c4f11164d734af4dcb4b3a5536bd20e3efc0085f
P2=governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md
H2=57820503b56948bf9e6ebe41abb2182c9a81db234e685218f21f71c69076549c
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0; N=0
ok() { N=$((N + 1)); echo "ok   $1"; }
bad() { N=$((N + 1)); FAILS=$((FAILS + 1)); echo "FAIL $1"; }
t() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
run() { # run <id> <want exit> <command...>: runs it (output indented), checks the exit code
  local id="$1" want="$2" rc; shift 2
  "$@" > "$W/out.txt" 2>&1; rc=$?
  sed 's/^/     /' "$W/out.txt" | cut -c1-260
  if [ "$rc" = "$want" ]; then ok "$id (exit $rc)"; else bad "$id (exit $rc, want $want)"; fi
}
grepout() { grep -q -- "$1" "$W/out.txt"; }
ap() { (cd "$C" && bash "$A/apply.sh" "$@"); }
launch() { # launch <brief path> <sha> <set> [kind]
  (cd "$C" && GOV_INDEP_RUNS_DIR=$W/runs GOV_INDEP_TREES_DIR=$W/trees "$PY" -I "$C/$LAUNCHER" --sets-root "$SR" \
    --kind "${4:-writer}" --brief "$1" --brief-sha256 "$2" --commit "$(git -C "$C" rev-parse HEAD)" --set "$3" --round 1 --seed 17 --dry)
}
lsha() { sha256sum "$1" | cut -c1-64; }
fake() { printf 'planted-%s' "$1" | sha256sum | cut -c1-64; }
same_list() { cmp -s "$W/APPROVED.before" "$LIST"; }
no_tmp() { [ -z "$(find "$SR/indep-walls" "$C/governance/project/indep-briefs" -maxdepth 1 -name '*act-*' 2>/dev/null)" ]; }
put_list() { chmod u+w "$LIST" 2>/dev/null; rm -f "$LIST"; cat "$1" > "$LIST"; chmod 400 "$LIST"; }

echo "--- 0. set-up ($(date -u +%FT%TZ))"
chmod -R u+w "$W" 2>/dev/null; rm -rf "$W"; mkdir -p "$W/home" "$W/runs" "$W/trees"
MAIN_HEAD=$(git -C "$MAIN" rev-parse HEAD); MAIN_ST=$(git -C "$MAIN" status --porcelain | sha256sum | cut -c1-64)
DRAFTS=$(sha256sum "$MAIN/.gov-runtime/scratch/orchestrator/drafts/examin-sets/EXAMIN-writer.md" "$MAIN/.gov-runtime/scratch/orchestrator/drafts/examin-sets/PROVING-GROUND-writer.md" | cut -c1-64 | tr '\n' ' ')
echo "main tree head $MAIN_HEAD (read only); status sha256 ${MAIN_ST:0:12}"
git clone -q --no-hardlinks -b w2/integrate "$MAIN" "$W/clone" || { bad "clone"; echo "failures: $FAILS"; exit 1; }
C=$W/clone
git -C "$C" config user.name rehearsal; git -C "$C" config user.email rehearsal@localhost.invalid
BASE=$(git -C "$C" rev-parse HEAD)
echo "clone head $BASE"
t "S1 the clone's head is the main tree's head" '[ "$BASE" = "$MAIN_HEAD" ]'
t "S2 the clone holds neither brief and no examin-sets folder" '[ ! -e "$C/governance/project/indep-briefs/examin-sets" ]'
t "S3 the bundle's frozen copies hash as approved (DEC-1143 (1))" '[ "$(lsha "$A/after/repo/$P1")" = $H1 ] && [ "$(lsha "$A/after/repo/$P2")" = $H2 ]'
t "S4 the drafts the owner approved hash as the frozen copies" '[ "$DRAFTS" = "$H1 $H2 " ]'
SR=$W/home/gov-os-eval
LIST=$SR/indep-walls/APPROVED
mkdir -p "$SR/indep-walls"; chmod 700 "$SR/indep-walls"
{
  echo "# ACT-INDEP-WALLS-1: the owner's approved list (DEC-1101 (2)). PLANTED for the rehearsal: the template lines are"
  echo "# hashed from the clone's template; every brief and operator hash below is invented."
  for n in README.md settings.json.tmpl wall_hook.py CLAUDE.md.tmpl kinds.yaml tree-exclude.txt; do
    echo "$(lsha "$C/governance/project/indep-walls/$n")  template governance/project/indep-walls/$n"
  done
  echo "# ACT-W2-149-INSTALL-1 (planted): the set-up A briefs"
  echo "$(fake l1)  brief labeller governance/project/indep-briefs/sgx1/labeller.md"
  echo "$(fake l2)  brief labeller governance/project/indep-briefs/sgx1/labeller-2.md"
  echo "$(fake w1)  brief writer governance/project/indep-briefs/sgx1/writer-tuning.md"
  echo "$(fake w2)  brief writer governance/project/indep-briefs/sgx1/writer-heldout.md"
  echo "$(fake a1)  brief auditor governance/project/indep-briefs/sgx1/overlap-auditor.md"
  echo "# The operator agent's two fixed briefs (planted)"
  echo "$(fake o1)  brief operator governance/project/operator/brief.md"
  echo "$(fake o2)  brief operator governance/project/operator/reviewer-brief.md"
  echo "# ACT-MEMORY-AUDIT-INSTALL-1 (planted): the memory audit's three"
  echo "$(fake m1)  brief writer governance/project/indep-briefs/memory-audit/writer.md"
  echo "$(fake m2)  brief checker governance/project/indep-briefs/memory-audit/checker.md"
  echo "$(fake m3)  brief auditor governance/project/indep-briefs/memory-audit/auditor.md"
} > "$W/APPROVED.before"
put_list "$W/APPROVED.before"
BEFORE_SHA=$(lsha "$LIST")
echo "planted list: $(wc -l < "$LIST") lines, sha256 ${BEFORE_SHA:0:12}, mode $(stat -c %a "$LIST"), folder $(stat -c %a "$SR/indep-walls")"

echo "--- A. before the ACT"
run "A1 check by the path map's sets root (~/gov-os-eval under the planted HOME): state before" 0 ap check
t "A1b it says state before and names the path map" 'grepout "state before" && grepout "sets_root_hidden.root"'
run "A2 check with the sets root as the argument: state before" 0 ap check "$SR"
run "A3 verify refuses before the apply" 3 ap verify
run "A4 undo refuses: nothing to undo" 3 ap undo
t "A5 the list is byte for byte as planted" same_list
run "A6 a dry launch under EXAMIN-writer.md before the ACT is refused 10 (the brief is not in the commit)" 10 launch "$P1" "$H1" examin

echo "--- B. apply"
run "B1 apply: state applied" 0 ap apply
t "B1b it says state applied" 'grepout "state applied"'
run "B2 verify" 0 ap verify
run "B3 check: state applied" 0 ap check
t "B4 both files are the frozen copies byte for byte" 'cmp -s "$A/after/repo/$P1" "$C/$P1" && cmp -s "$A/after/repo/$P2" "$C/$P2"'
t "B5 the list is the planted list plus lines.txt, byte for byte" 'cat "$W/APPROVED.before" "$A/lines.txt" | cmp -s - "$LIST"'
t "B6 the list stays 0400 and its folder 0700" '[ "$(stat -c %a "$LIST")" = 400 ] && [ "$(stat -c %a "$SR/indep-walls")" = 700 ]'
t "B7 no temp file left beside the list or the briefs" no_tmp
"$PY" -I -c "
import importlib.util, sys
s = importlib.util.spec_from_file_location('il', sys.argv[1]); il = importlib.util.module_from_spec(s); s.loader.exec_module(il)
t, b = il.parse_approved(open(sys.argv[2], 'rb').read())
mine = [x for x in b if x[2].startswith('governance/project/indep-briefs/examin-sets/')]
print('     parse_approved: %d template lines, %d brief lines; ours: %s' % (len(t), len(b), [(h[:12], k, p) for h, k, p in mine]))
sys.exit(0 if len(t) == 6 and len(b) == 12 and sorted(mine) == sorted([(sys.argv[3], 'writer', sys.argv[4]), (sys.argv[5], 'writer', sys.argv[6])]) else 1)
" "$C/$LAUNCHER" "$LIST" "$H1" "$P1" "$H2" "$P2" && ok "B8 the launch script's parse_approved reads both lines as (sha256, writer, path); 6 template, 12 brief lines" || bad "B8 parse_approved"
AFTER_SHA=$(lsha "$LIST")
run "B9 a second apply is refused" 3 ap apply
t "B9b the list is unchanged by the refused apply" '[ "$(lsha "$LIST")" = "$AFTER_SHA" ]'

echo "--- C. the operator's commit (in the clone, the line exactly as the bundle gives it)"
(cd "$C" && git add governance/project/indep-briefs/examin-sets/ && git commit -q -m "ACT-EXAMIN-WRITERS-INSTALL-1: the two walled writer briefs as the owner approved them (DEC-1143 (1)), and their lines in the walls' approved list" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1143, DEC-1130" --trailer "Role: owner") && ok "C1 the commit is made" || bad "C1 the commit"
NS=$(git -C "$C" show --name-status --format= HEAD)
echo "$NS" | sed 's/^/     /'
t "C2 it holds exactly the two files, both A" '[ "$NS" = "$(printf "A\t%s\nA\t%s" "$P1" "$P2")" ]'
MSG=$(git -C "$C" log -1 --format=%B)
t "C3 the three trailers are there" 'echo "$MSG" | grep -qx "Task: DAEO-sdxk" && echo "$MSG" | grep -qx "Implements: DEC-1143, DEC-1130" && echo "$MSG" | grep -qx "Role: owner"'
t "C4 the committed blobs hash as approved" '[ "$(git -C "$C" show HEAD:$P1 | sha256sum | cut -c1-64)" = $H1 ] && [ "$(git -C "$C" show HEAD:$P2 | sha256sum | cut -c1-64)" = $H2 ]'
run "C5 the path map check passes with the two briefs tracked (indep-briefs namespace)" 0 env -C "$C" PYTHONPATH=src python3 -m gov.check.pathmap

echo "--- D. dry launches under both briefs at the commit (planted sets root; --seed 17 --dry; no session starts)"
for spec in "examin $P1 $H1 8 3600" "adoption-proving-ground $P2 $H2 15 5400"; do
  set -- $spec
  bp=$2   # t's own $2 is its test, so the brief's path goes by name inside a t test
  run "D1 [$1] the launch script accepts the brief and builds the wall" 0 launch "$2" "$3" "$1"
  t "D1b [$1] its counts line says dry" 'tail -1 "$W/out.txt" | grep -q "\"status\": *\"dry\""'
  wall=$(grep -l "\"brief\": \"$2\"" "$SR"/indep-walls/writer/*/WALL.json 2>/dev/null | head -1)
  wall=${wall%/WALL.json}
  t "D2 [$1] the wall's brief.md is the approved brief byte for byte" '[ -n "$wall" ] && cmp -s "$wall/brief.md" "$A/after/repo/$bp"'
  "$PY" -I -c "
import json, sys
m = json.load(open(sys.argv[1] + '/WALL.json'))
print('     WALL.json: model %s, effort %s, result_schema %s, budget %s, timeout %s, set %s, selection %s, tree files %s' % (m['model'], m['effort'], m['result_schema'], m['budget_usd'], m['timeout_s'], m['set'], m['selection'], m['tree_files']))
sys.exit(0 if m['model'] == 'claude-sonnet-5-5' and m['effort'] == 'high' and m['result_schema'] == 'writer-result.schema.json' and m['budget_usd'] == int(sys.argv[2]) and m['timeout_s'] == int(sys.argv[3]) and m['brief_sha256'] == sys.argv[4] else 1)
" "$wall" "$4" "$5" "$3" && ok "D3 [$1] WALL.json: the brief's front matter resolved (sonnet, effort high, writer schema, its budget and timeout)" || bad "D3 [$1] WALL.json"
  tree=$W/trees/writer-$(basename "$wall")
  t "D4 [$1] the wall's tree is built and leaves governance/project/indep-briefs out" '[ -d "$tree/governance/project" ] && [ ! -e "$tree/governance/project/indep-briefs" ]'
done
run "D5 EXAMIN's path with PROVING-GROUND's sha256 is refused 10" 10 launch "$P1" "$H2" examin
run "D6 EXAMIN-writer.md under --kind checker is refused 10 (its line gives writer)" 10 launch "$P1" "$H1" examin checker
t "D7 the dry launches left the list unchanged" '[ "$(lsha "$LIST")" = "$AFTER_SHA" ]'

echo "--- E. undo"
run "E1 undo: state before" 0 ap undo
t "E2 the list is byte for byte the planted list (sha256 ${BEFORE_SHA:0:12})" 'same_list && [ "$(lsha "$LIST")" = "$BEFORE_SHA" ]'
t "E3 both files are gone and the examin-sets folder with them" '[ ! -e "$C/$P1" ] && [ ! -e "$C/$P2" ] && [ ! -e "$C/governance/project/indep-briefs/examin-sets" ]'
GS=$(git -C "$C" status --porcelain)
echo "$GS" | sed 's/^/     /'
t "E4 the clone's status is exactly the two removals (D)" '[ "$GS" = "$(printf " D %s\n D %s" "$P1" "$P2")" ]'
run "E5 check: state before" 0 ap check
run "E6 verify refuses after the undo" 3 ap verify
t "E7 the list stays 0400; no temp file left" '[ "$(stat -c %a "$LIST")" = 400 ] && no_tmp'
run "E8 after the undo a dry launch under EXAMIN-writer.md at the commit is refused 10 (no line in the list)" 10 launch "$P1" "$H1" examin

echo "--- F. refusals (each from the planted list and the clone at its first head; each must touch nothing)"
reset() { git -C "$C" reset -q --hard "$BASE"; git -C "$C" clean -fdq governance/project/indep-briefs; put_list "$W/APPROVED.before"; }
untouched() { same_list && [ ! -e "$C/$P2" ]; }
reset
mkdir -p "$W/sr-nolist/indep-walls"; chmod 700 "$W/sr-nolist/indep-walls"
run "F1 the list missing: check is state other" 3 ap check "$W/sr-nolist"
t "F1b it says the list does not exist" 'grepout "does not exist"'
run "F1c the list missing: apply refuses" 3 ap apply "$W/sr-nolist"
t "F1d no list was created and no brief written" '[ ! -e "$W/sr-nolist/indep-walls/APPROVED" ] && [ -z "$(ls -A "$W/sr-nolist/indep-walls")" ] && [ ! -e "$C/$P1" ] && [ ! -e "$C/$P2" ]'
mkdir -p "$W/sr-nowalls"
run "F1e the indep-walls folder missing: apply refuses" 3 ap apply "$W/sr-nowalls"
t "F1f nothing created under that root" '[ -z "$(ls -A "$W/sr-nowalls")" ]'
reset; mkdir -p "$C/governance/project/indep-briefs/examin-sets"; cp "$A/after/repo/$P1" "$C/$P1"
run "F2 one file already present (byte-exact): check is state other" 3 ap check
run "F2b one file already present: apply refuses" 3 ap apply
t "F2c the list is unchanged, the other file not written, the present one unchanged" 'untouched && [ "$(lsha "$C/$P1")" = $H1 ]'
reset; mkdir -p "$C/governance/project/indep-briefs/examin-sets"; { cat "$A/after/repo/$P1"; echo; } > "$C/$P1"; cp "$A/after/repo/$P2" "$C/$P2"
run "F2d both files present, one with a byte added: apply refuses" 3 ap apply
t "F2e the list is unchanged" same_list
reset; { cat "$W/APPROVED.before"; head -1 "$A/lines.txt"; } > "$W/one-line"; put_list "$W/one-line"
run "F3 one line already present: check is state other" 3 ap check
run "F3b one line already present: apply refuses" 3 ap apply
t "F3c the list is unchanged and no brief written" 'cmp -s "$W/one-line" "$LIST" && [ ! -e "$C/$P1" ] && [ ! -e "$C/$P2" ]'
reset; { cat "$W/APPROVED.before"; printf '%s\tbrief\twriter\t%s\n' "$H2" "$P2"; } > "$W/other-spelling"; put_list "$W/other-spelling"
run "F3d the PROVING-GROUND line in another spelling (tabs, which the parser reads): apply refuses" 3 ap apply
t "F3e the list is unchanged" 'cmp -s "$W/other-spelling" "$LIST" && [ ! -e "$C/$P1" ]'
reset; { cat "$W/APPROVED.before"; printf '# a comment that names %s\n' "$P1"; } > "$W/comment"; put_list "$W/comment"
run "F3f a comment naming a brief's path is not a line: check is state before" 0 ap check
reset; head -c -1 "$W/APPROVED.before" > "$W/no-nl"; put_list "$W/no-nl"
run "F4 the list does not end in a newline: apply refuses" 3 ap apply
t "F4b the list is unchanged" 'cmp -s "$W/no-nl" "$LIST" && [ ! -e "$C/$P1" ]'
reset; chmod u+w "$LIST"; mv "$LIST" "$W/real-list"; ln -s "$W/real-list" "$LIST"
run "F5 the list is a link: apply refuses" 3 ap apply
t "F5b the linked file is unchanged" 'cmp -s "$W/APPROVED.before" "$W/real-list" && [ -L "$LIST" ] && [ ! -e "$C/$P1" ]'
rm -f "$LIST"; mv "$W/real-list" "$LIST"; chmod 400 "$LIST"
reset; rm -rf "$W/bundle-tampered"; cp -r "$A" "$W/bundle-tampered"; echo x >> "$W/bundle-tampered/after/repo/$P1"
run "F6 a tampered frozen copy: apply exits 4" 4 env -C "$C" bash "$W/bundle-tampered/apply.sh" apply "$SR"
t "F6b nothing touched" 'same_list && [ ! -e "$C/$P1" ]'
run "F7 a sets root that does not exist: apply refuses" 3 ap apply "$W/no-such-root"
run "F7b a relative sets root: refused 9" 9 ap apply home/gov-os-eval
run "F7c a folder under the sets root named instead of the root: refused 9" 9 ap apply "$SR/indep-walls"
run "F8 not run from the repository's top folder: refused 9" 9 env -C "$C/src" bash "$A/apply.sh" check "$SR"
t "F8b nothing touched" 'same_list && [ ! -e "$C/$P1" ]'
reset; chmod 500 "$SR/indep-walls"
run "F9 the list's folder not writable: apply exits 5" 5 ap apply
chmod 700 "$SR/indep-walls"
t "F9b nothing touched, no temp file, no brief folder" 'same_list && no_tmp && [ ! -e "$C/governance/project/indep-briefs/examin-sets" ]'
reset
run "F10 apply, then a later line is appended after ours" 0 ap apply
chmod u+w "$LIST"; printf '# a later ACT (planted)\n%s  brief checker governance/project/indep-briefs/later/checker.md\n' "$(fake later)" >> "$LIST"; chmod 400 "$LIST"
run "F10b undo removes exactly our two lines" 0 ap undo
t "F10c every other line byte-identical: the planted list plus the later two lines" '{ cat "$W/APPROVED.before"; printf "# a later ACT (planted)\n%s  brief checker governance/project/indep-briefs/later/checker.md\n" "$(fake later)"; } | cmp -s - "$LIST"'
reset
run "F11 apply, then EXAMIN-writer.md is changed" 0 ap apply
echo "edit" >> "$C/$P1"; APPLIED_LIST=$(lsha "$LIST")
run "F11b undo refuses (a later change is not overwritten)" 3 ap undo
run "F11c verify refuses" 3 ap verify
t "F11d nothing touched: the list as applied, the PROVING-GROUND file still there" '[ "$(lsha "$LIST")" = "$APPLIED_LIST" ] && [ "$(lsha "$C/$P2")" = $H2 ]'
reset
run "F12 apply, then the EXAMIN line appended a second time" 0 ap apply
chmod u+w "$LIST"; head -1 "$A/lines.txt" >> "$LIST"; chmod 400 "$LIST"; TWICE=$(lsha "$LIST")
run "F12b undo refuses a line present twice" 3 ap undo
t "F12c nothing touched" '[ "$(lsha "$LIST")" = "$TWICE" ] && [ "$(lsha "$C/$P1")" = $H1 ]'
reset

echo "--- G. the live files (read only)"
t "G1 the main tree's head is unchanged" '[ "$(git -C "$MAIN" rev-parse HEAD)" = "$MAIN_HEAD" ]'
t "G2 the main tree's status is unchanged" '[ "$(git -C "$MAIN" status --porcelain | sha256sum | cut -c1-64)" = "$MAIN_ST" ]'
t "G3 the main tree holds no examin-sets folder" '[ ! -e "$MAIN/governance/project/indep-briefs/examin-sets" ]'
t "G4 the approved drafts are unchanged" '[ "$(sha256sum "$MAIN/.gov-runtime/scratch/orchestrator/drafts/examin-sets/EXAMIN-writer.md" "$MAIN/.gov-runtime/scratch/orchestrator/drafts/examin-sets/PROVING-GROUND-writer.md" | cut -c1-64 | tr "\n" " ")" = "$DRAFTS" ]'
echo
echo "checks run: $N"
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
