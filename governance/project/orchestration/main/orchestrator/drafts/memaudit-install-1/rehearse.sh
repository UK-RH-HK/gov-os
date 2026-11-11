#!/usr/bin/env bash
# ACT-MEMORY-AUDIT-INSTALL-1: the rehearsal, end to end, in a clone with a planted HOME and a planted sets root (DEC-1057).
# Changes nothing live and starts no session (every launch is --dry); never opens the real sets root or the real runs.
# Everything it writes is under work/ beside this file (removed at the end unless KEEP=1).
#   bash rehearse.sh            the log: rehearsal.log beside this file
# Layout ($BASE = <this folder>/work):
#   $BASE/repo     the --no-hardlinks clone of the main tree at its head (the launch script, the template, the five
#                  set-up A briefs, the path map and the hook as they are live)
#   $BASE/home     the planted HOME; $BASE/home/planted-sets the planted sets root; runs and wall trees beside it
# Order: the live list planted as the last applied ACT left it (APPROVED.before); an approved-path launch refused
# before; check refusals; check, apply, a second apply, the commit (exactly 3 A); the list read back; the launch's
# own stage-10 checks on every brief line; a dry launch under each of the three (and the five set-up A briefs);
# a changed byte refused; the path map's structural pass; undo.
if [ -z "${MI_FRESH:-}" ]; then
  exec env -i HOME="$HOME" USER="${USER:-usain}" LOGNAME="${LOGNAME:-usain}" PATH="/usr/local/bin:/usr/bin:/bin" \
    LANG="${LANG:-C.UTF-8}" MI_HEAD="${MI_HEAD:-}" KEEP="${KEEP:-}" MI_FRESH=1 bash --noprofile --norc "$0" "$@"
fi
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/memaudit-install-1
BASE=$HERE/work
R=$BASE/repo
PH=$BASE/home
PR=$PH/planted-sets
RUNS=$PH/planted-runs
TREES=$PH/planted-trees
D=$R/$SUB/drafts/memaudit-install-1
LOG=$HERE/rehearsal.log
SCRIPT=governance/project/orchestration/tools/indep_launch.py
BR=governance/project/indep-briefs/memory-audit
SG=governance/project/indep-briefs/sgx1
SRC=governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs
W=bc0894230e3181e5be27726d60e9fb781f9355da1c4f8e76f69b400af97d379b
C=cea517b8da7d4834bb2a698b9c7023670da36f0ceca6b3350656c6db77c45248
A=37be41c3fb2fea1654d68f71f1ecfc5ad4b41faaed9356a27ce1f01d8ef94245
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0; OKS=0
say() { printf '\n== %s (%s)\n' "$1" "$(date -u '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
good() { echo "ok: $1"; OKS=$((OKS + 1)); }
expect() { grep -Eq "$2" "$1" && good "$3" || bad "$3 (wanted /$2/ in $(basename "$1"))"; }
AP() { ( cd "$R" && bash "$D/apply.sh" "$1" --sets-root "$PR" ); }
launch() {  # $1 kind, $2 brief path, $3 sha, $4 set, $5 round, $6 audit (optional); a dry launch, seed 17, HOME planted
  local extra=(); [ -n "${6:-}" ] && extra=(--audit "$6")
  ( cd "$R" && HOME=$PH GOV_INDEP_RUNS_DIR=$RUNS GOV_INDEP_TREES_DIR=$TREES python3 "$R/$SCRIPT" --sets-root "$PR" \
      --kind "$1" --brief "$2" --brief-sha256 "$3" --commit HEAD --set "$4" --round "$5" "${extra[@]}" --seed 17 --dry \
      > "$BASE/launch.out" 2> "$BASE/launch.err" ); local rc=$?
  echo "launch $1 $(basename "$2") round $5: exit $rc; $(tail -1 "$BASE/launch.err")"
  return $rc
}
clean_walls() { chmod -R u+w "$PR/indep-walls" "$TREES" 2>/dev/null; rm -rf "$PR/indep-walls/writer" "$PR/indep-walls/checker" \
                "$PR/indep-walls/auditor" "$PR/indep-walls/labeller" "$TREES"/* 2>/dev/null; mkdir -p "$TREES"; }
live_hashes() {
  ( cd "$MAIN" && sha256sum .claude/hooks/pretooluse.py governance/project/path-map.yaml .claude/settings.json "$SCRIPT" \
      governance/project/indep-walls/* governance/project/orchestration/tools/indep-schemas/* \
      governance/project/operator/class-rules.yaml docs/DECISION_REGISTER.md )
  ls "$MAIN/governance/project/indep-briefs" 2>&1 | sed 's/^/listing: /'
  git -C "$MAIN" status --porcelain | sed 's/^/status: /'
  git -C "$MAIN" rev-parse HEAD | sed 's/^/head: /'
}
wall_facts() {  # $1 = the wall's kind folder; prints WALL.json's facts, the input names, brief.md and tree checks
  local w t; w=$(find "$PR/indep-walls/$1" -mindepth 1 -maxdepth 1 -type d | head -1)
  python3 -I -B -c 'import json,os,sys; m=json.load(open(os.path.join(sys.argv[1],"WALL.json"))); print("  WALL.json:", {k: m.get(k) for k in ("brief_id","flow","model","result_schema","sample","round") if k in m}, "input/:", sorted(os.listdir(os.path.join(sys.argv[1],"input"))))' "$w"
  [ -e "$w/brief.md" ] && cmp -s "$w/brief.md" "$R/$2" && good "  brief.md is byte for byte the approved brief ($(basename "$2"))" || bad "$2: the wall's brief.md is not the approved bytes"
  t=$(python3 -I -B -c 'import json,os,sys; print(json.load(open(os.path.join(sys.argv[1],"WALL.json")))["tree"])' "$w")
  if [ ! -e "$t/governance/project/indep-briefs" ]; then
    good "  the tree holds no governance/project/indep-briefs/ (tree-exclude.txt)"
  else bad "$2: the tree holds governance/project/indep-briefs/"; fi
  echo "  (observed, not a check) the tree still holds packages/MEMORY-AUDIT-1/briefs: $( [ -e "$t/$SRC" ] && echo yes || echo no )"
}

say "prepare: the clone, the planted HOME and sets root"
date -u '+start %Y-%m-%dT%H:%M:%SZ'
live_hashes > "$BASE.live-before.txt" 2>&1 || true
if [ -e "$BASE" ]; then
  [ -f "$BASE/.mi-rehearsal" ] || { echo "REHEARSAL STOP: $BASE exists and is not this script's"; exit 3; }
  chmod -R u+w "$BASE" 2>/dev/null; rm -rf "$BASE"
fi
mkdir -p "$BASE/hooks-safe" && : > "$BASE/.mi-rehearsal"
mv "$BASE.live-before.txt" "$BASE/live-before.txt"
head=$(git -C "$MAIN" rev-parse "${MI_HEAD:-HEAD}")
git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; exit 1; }
git -C "$R" config core.hooksPath "$BASE/hooks-safe"
git -C "$R" checkout -q -B w2/integrate "$head" || bad "checkout"
git -C "$R" config user.name "mi rehearsal"; git -C "$R" config user.email "mi@localhost"
mkdir -p "$R/$SUB/drafts/memaudit-install-1" "$R/$SUB/drafts/w2-149-install"
for f in apply.sh freeze.py install_check.py rehearse.sh APPROVED.before APPROVED.after; do cp -p "$HERE/$f" "$D/$f"; done
cp -a "$HERE/briefs" "$D/briefs"
cp -p "$MAIN/$SUB/drafts/w2-149-install/APPROVED.after" "$R/$SUB/drafts/w2-149-install/APPROVED.after"
echo "clone at $(git -C "$R" rev-parse --short=12 HEAD); the launch script $(sha256sum "$R/$SCRIPT" | cut -c1-12)"
mkdir -p "$PH" "$RUNS/indep" "$TREES" "$PR/transcripts" "$PR/runs/e0" \
         "$PR/fixtures/evaluation/memory-audit-set/hidden" "$PR/fixtures/evaluation/sandbox-guard-exp-1/hidden/corpus"
for i in 01 02 03; do printf 'DUMMY planted question %s\n' "$i" > "$PR/fixtures/evaluation/memory-audit-set/hidden/q$i.yaml"; done
printf 'DUMMY planted notes\n' > "$PR/fixtures/evaluation/memory-audit-set/XCHECK-r1.md"
printf '{"question": "q01", "gold": "g", "answer": "a"}\n' > "$PR/runs/e0/misses.jsonl"
printf 'DUMMY planted\n' > "$PR/transcripts/t01.md"
EXP=$RUNS/SANDBOX-GUARD-EXP-1/tuning   # set-up A's tuning half (planted), for the five set-up A dry launches
mkdir -p "$EXP/corpus" "$EXP/planted" "$EXP/labels"
python3 -I -B - "$EXP" <<'EOF'
import json, os, sys
h = sys.argv[1]
def row(i, src, **kw):
    r = {"id": i, "role": "engineer", "agent": None, "ticket": "DAEO-52ku", "wbs": "W2-149", "tool": "Read",
         "input": {"file_path": "/home/usain/Dynamic-Agentic-Engineering-OS/README.md"},
         "cwd": "/home/usain/Dynamic-Agentic-Engineering-OS", "executable": True, "strata": [], "source": src}
    r.update(kw); return r
w = lambda p, rows: open(os.path.join(h, p), "w").write("".join(json.dumps(r) + "\n" for r in rows))
w("corpus/actions.jsonl", [row(f"r{n}", "replay") for n in range(1, 4)])
w("planted/cases.jsonl", [row(f"p1-c14-00{n}-engineer", "planted-1", rule_class="14", strata=["planted"]) for n in (1, 2)])
lab = lambda i, l: {"id": i, "label": l, "rule_class": 14, "clauses": ["DEC-820"], "reason": ""}
w("labels/labels.jsonl", [lab("r1", "allow"), lab("r2", "allow"), lab("r3", "allow")])
w("labels/labels-2.jsonl", [dict(lab("r2", "refuse"), how="hand", reason="planted")])
EOF
echo "planted: a memory set (3 hidden files, XCHECK-r1.md), runs/e0/misses.jsonl, set-up A's tuning half"
mkdir -m 0700 "$PR/indep-walls"
cat "$HERE/APPROVED.before" > "$PR/indep-walls/APPROVED"; chmod 0400 "$PR/indep-walls/APPROVED"
echo "planted list $(sha256sum "$PR/indep-walls/APPROVED" | cut -c1-12) (the list ACT-W2-149-INSTALL-1 left; rebuilt, 23 lines)"
[ "$(sha256sum "$PR/indep-walls/APPROVED" | cut -c1-64)" = 6b923cb4d552077f99924fd5df38f1a448b21f863c4755c9ff4e0dcfb28ed959 ] \
  && good "APPROVED.before is the recorded 6b923cb4d552" || bad "APPROVED.before is not the recorded sha256"
( cd "$D" && sha256sum apply.sh freeze.py install_check.py rehearse.sh APPROVED.before APPROVED.after briefs/* ) | cut -c1-12,65-
( cd "$R" && git ls-files governance/project/indep-briefs | sed 's/^/tracked before: /' )

say "before this ACT: the briefs where the owner approved them are refused (10: no line on the list)"
for pair in "writer $W writer" "checker $C checker" "auditor $A auditor"; do
  set -- $pair
  rnd=1; set_n=mem-new-1; aud=""
  [ "$1" = checker ] && set_n=memory-audit-set; [ "$1" = auditor ] && { set_n=memory-audit-set; aud=e0; }
  launch "$1" "$SRC/$3.md" "$2" "$set_n" "$rnd" "$aud"; rc=$?
  [ $rc = 10 ] && good "  $1: refused 10 before the install" || bad "$1 before the install: exit $rc, not 10"
  clean_walls
done

say "check refusals (each must stop, change nothing)"
AP check > "$BASE/c0.txt" 2>&1 || bad "check on the clean tree"; expect "$BASE/c0.txt" "check: ready to apply" "check: ready to apply on the clean clone"
chmod u+w "$PR/indep-walls/APPROVED"; printf '#' >> "$PR/indep-walls/APPROVED"; chmod 0400 "$PR/indep-walls/APPROVED"
AP check > "$BASE/c1.txt" 2>&1 && bad "check passed with a changed live list" || true
cat "$BASE/c1.txt"; expect "$BASE/c1.txt" "the live list is not 6b923cb4d552" "refused: the live list is not the one the last ACT left"
AP apply > "$BASE/c1b.txt" 2>&1 && bad "apply ran with a changed live list" || true
expect "$BASE/c1b.txt" "the live list is not 6b923cb4d552" "apply refused too; no backup made"
[ ! -e "$D/backup" ] && [ ! -e "$R/$BR" ] && good "nothing written (no backup, no brief files)" || bad "a refused apply wrote something"
chmod u+w "$PR/indep-walls/APPROVED"; cat "$HERE/APPROVED.before" > "$PR/indep-walls/APPROVED"; chmod 0400 "$PR/indep-walls/APPROVED"
cp -p "$D/briefs/checker.md" "$BASE/checker.md.keep"; printf ' ' >> "$D/briefs/checker.md"
AP check > "$BASE/c2.txt" 2>&1 && bad "check passed with a changed draft brief" || true
expect "$BASE/c2.txt" "the draft briefs/checker.md is not the approved brief" "refused: a draft brief changed by one byte"
cp -p "$BASE/checker.md.keep" "$D/briefs/checker.md"
printf '\n' >> "$R/governance/project/indep-walls/kinds.yaml"
AP check > "$BASE/c3.txt" 2>&1 && bad "check passed with a changed template file" || true
expect "$BASE/c3.txt" "template differs: governance/project/indep-walls/kinds.yaml|a template file in the tree is not the one the list names" "refused: a template file differs from its list line"
git -C "$R" checkout -q -- governance/project/indep-walls/kinds.yaml
cp -p "$R/governance/project/path-map.yaml" "$BASE/map.keep"
grep -vF '"governance/project/indep-briefs/**"' "$BASE/map.keep" > "$R/governance/project/path-map.yaml"
AP check > "$BASE/c4.txt" 2>&1 && bad "check passed without ACT-PATHMAP-NS-2" || true
expect "$BASE/c4.txt" "ACT-PATHMAP-NS-2 is not applied" "refused: the path map names no indep-briefs namespace"
git -C "$R" checkout -q -- governance/project/path-map.yaml
rm -f "$R/$SG/labeller.md"
AP check > "$BASE/c5.txt" 2>&1 && bad "check passed without set-up A's briefs" || true
expect "$BASE/c5.txt" "that ACT first" "refused: set-up A's briefs not in the tree (ACT-W2-149-INSTALL-1 first)"
git -C "$R" checkout -q -- "$SG/labeller.md"
git -C "$R" status --porcelain | sed 's/^/clone status: /'; AP check | tail -1 | sed 's/^/after the refusals: /'

say "this ACT: check, apply, a second apply, check, the commit"
AP check > "$BASE/check1.txt" 2>&1; cat "$BASE/check1.txt"; expect "$BASE/check1.txt" "check: ready to apply" "check: ready"
mkdir -p "$BASE/globcwd/runs/x" && : > "$BASE/globcwd/runs/x/misses.jsonl"
( cd "$BASE/globcwd" && bash "$D/apply.sh" check --sets-root "$PR" ) > "$BASE/check1b.txt" 2>&1
expect "$BASE/check1b.txt" "check: ready to apply" "check from a folder holding runs/x/misses.jsonl: still ready"
AP apply > "$BASE/apply1.txt" 2>&1; cat "$BASE/apply1.txt"; expect "$BASE/apply1.txt" "^state applied" "applied"
[ ! -e "$R/governance/project/orchestration/tools/__pycache__" ] && good "no bytecode cache written into the tree" || bad "apply wrote a __pycache__"
expect "$BASE/apply1.txt" "6 template lines, 10 brief lines .*the memory audit's: auditor, checker, writer; template mismatches 0; brief mismatches 0" "the launch script's parser reads the list: 6 template lines, 10 brief lines, 0 mismatches"
AP apply > "$BASE/apply2.txt" 2>&1 && bad "a second apply ran" || good "a second apply: refused ($(tail -1 "$BASE/apply2.txt"))"
AP check | tail -2 | tee "$BASE/check2.txt"; expect "$BASE/check2.txt" "already applied" "check: already applied"
git -C "$R" add "$BR"
git -C "$R" diff --cached --name-status | tee "$BASE/staged.txt"
[ "$(wc -l < "$BASE/staged.txt")" = 3 ] && [ "$(grep -c '^A' "$BASE/staged.txt")" = 3 ] && good "exactly 3 A: the three briefs" || bad "the staged set is not 3 A"
git -C "$R" commit -q -m "ACT-MEMORY-AUDIT-INSTALL-1: the memory audit's three fixed briefs as the owner approved them (DEC-1129 (2)), and their lines in the launch script's approved list" \
  --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1129" --trailer "Role: owner" -- "$BR" || bad "the commit"
git -C "$R" show --stat --format= HEAD | tail -1
git -C "$R" log -1 --format='%h %s%n%(trailers)'
sha256sum "$PR/indep-walls/APPROVED" | cut -c1-12 | sed 's/^/the planted list after: /'
stat -c '%a %n' "$PR/indep-walls" "$PR/indep-walls/APPROVED" | sed "s#$PR#<root>#"
[ "$(stat -c %a "$PR/indep-walls/APPROVED")" = 400 ] && good "the list is 0400 after the apply" || bad "the list is not 0400"
[ "$(stat -c %a "$PR/indep-walls")" = 700 ] && good "the folder is 0700 still" || bad "the folder mode changed"
[ "$(sha256sum "$PR/indep-walls/APPROVED" | cut -c1-64)" = "$(sha256sum "$HERE/APPROVED.after" | cut -c1-64)" ] && good "the list is APPROVED.after byte for byte" || bad "the list is not APPROVED.after"

say "the launch script's stage-10 checks on every line, at the ACT's commit (its own code)"
python3 -I -B "$D/install_check.py" "$R" "$PR/indep-walls/APPROVED" HEAD | tee "$BASE/lines.txt"
expect "$BASE/lines.txt" "approved lines that match their bytes at the commit: 10 of 10" "every brief line (10) matches its bytes at the commit"
[ "$(grep -c 'front matter ok' "$BASE/lines.txt")" = 8 ] && good "the three memory briefs and the five set-up A briefs pass stage 10's front matter (8 of 8)" || bad "not all eight briefs pass stage 10's front matter"

say "the three memory briefs: a dry launch under each, each must pass the approved check and build its wall (0)"
launch writer "$BR/writer.md" $W mem-new-1 1; rc=$?
if [ $rc = 0 ]; then good "  writer round 1: exit 0 (dry)"; wall_facts writer "$BR/writer.md"; else bad "writer round 1: exit $rc"; fi
clean_walls
launch writer "$BR/writer.md" $W memory-audit-set 2; rc=$?
if [ $rc = 0 ]; then good "  writer round 2: exit 0 (dry)"; wall_facts writer "$BR/writer.md"; else bad "writer round 2: exit $rc"; fi
clean_walls
launch checker "$BR/checker.md" $C memory-audit-set 1; rc=$?
if [ $rc = 0 ]; then good "  checker: exit 0 (dry)"; wall_facts checker "$BR/checker.md"; else bad "checker: exit $rc"; fi
clean_walls
launch auditor "$BR/auditor.md" $A memory-audit-set 1 e0; rc=$?
if [ $rc = 0 ]; then good "  auditor: exit 0 (dry)"; wall_facts auditor "$BR/auditor.md"; else bad "auditor: exit $rc"; fi
clean_walls

say "set-up A's five briefs still pass (a dry launch under each, tuning half)"
for pair in "labeller labeller.md bbff1249953bd9d3b2596b33a108712bdddd79a7e86723b9e6955e3d6b0e9068 tuning" \
            "labeller labeller-2.md e13b5f96d0e058277f3ec3014f13205d7fe0bc950cfc308e81b3ee3d742ac904 tuning" \
            "writer writer-tuning.md 82134b3dd6b5a077abfc2eb6fa7481f0f5a73eab60396cfbd655042d53027c57 tuning" \
            "writer writer-heldout.md 137a73d1df4c265fd5ce4e24716797703e2b12dcaeb90663c0170834a60fafe6 held-out" \
            "auditor overlap-auditor.md b212a424062e402b0a25ee4a157ae14a0af798d0ad973aa33dacd730782be6ab tuning"; do
  set -- $pair
  aud=""; [ "$1" = auditor ] && aud=e0
  # the held-out half's sealed folder is planted empty, so only the tuning half is launched except the held-out writer
  launch "$1" "$SG/$2" "$3" "$4" 1 "$aud"; rc=$?
  if [ $rc = 0 ]; then good "  $2: exit 0 (dry)"; else bad "launch $2: exit $rc, not 0"; fi
  clean_walls
done

say "a changed byte is refused (10), at a second commit in the clone only"
cp -p "$R/$BR/writer.md" "$BASE/writer.md.keep"
printf ' ' >> "$R/$BR/writer.md"
new=$(sha256sum "$R/$BR/writer.md" | cut -c1-64)
git -C "$R" commit -q -m "rehearsal: writer.md changed by one byte" --trailer "Task: DAEO-sdxk" -- "$BR/writer.md" || bad "the rehearsal's second commit"
launch writer "$BR/writer.md" $W mem-new-1 1; rc=$?
[ $rc = 10 ] && good "  the old sha256 against the changed bytes: refused 10 (bytes)" || bad "changed byte, old sha256: exit $rc, not 10"
clean_walls
launch writer "$BR/writer.md" "$new" mem-new-1 1; rc=$?
[ $rc = 10 ] && good "  the new sha256 (a changed byte not on the list): refused 10 (approved)" || bad "changed byte, new sha256: exit $rc, not 10"
python3 -I -B - "$R" "$new" "$BR/writer.md" <<'EOF2' && good "  (by the script's own functions: the bytes at the commit do hash to the new sha256, and no list line holds it: the refusal is the approved check)" || bad "the approved-check reading"
import hashlib, importlib.util, subprocess, sys
repo, new, path = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("il", repo + "/governance/project/orchestration/tools/indep_launch.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
blob = subprocess.run(["git", "-C", repo, "show", "HEAD:" + path], capture_output=True, check=True).stdout
t, b = m.parse_approved(open(repo + "/../home/planted-sets/indep-walls/APPROVED", "rb").read())
sys.exit(0 if hashlib.sha256(blob).hexdigest() == new and not any(h == new for h, _, _ in b) else 1)
EOF2
clean_walls
cp -p "$BASE/writer.md.keep" "$R/$BR/writer.md"
git -C "$R" commit -q -m "rehearsal: writer.md restored" --trailer "Task: DAEO-sdxk" -- "$BR/writer.md" || bad "the restoring commit"
launch checker "$BR/checker.md" $C memory-audit-set 1; rc=$?
launch writer "$BR/checker.md" $C memory-audit-set 1; rc2=$?
[ $rc = 0 ] && [ $rc2 = 10 ] && good "  checker.md under --kind checker: 0; under --kind writer (a kind its line does not give): refused 10" || bad "kind mismatch: $rc / $rc2"
clean_walls
launch writer "$BR/writer.md" $W mem-new-1 1; rc=$?
[ $rc = 0 ] && good "  control: writer.md restored, launches again (0)" || bad "control after the restore: exit $rc"
clean_walls
# a changed byte in the list itself: one brief line's hash with one hex digit changed
cp -p "$PR/indep-walls/APPROVED" "$BASE/APPROVED.keep"
chmod u+w "$PR/indep-walls/APPROVED"
sed -i "s/^${C:0:1}${C:1}  brief checker/$([ "${C:0:1}" = 0 ] && echo 1 || echo 0)${C:1}  brief checker/" "$PR/indep-walls/APPROVED"
chmod 0400 "$PR/indep-walls/APPROVED"
launch checker "$BR/checker.md" $C memory-audit-set 1; rc=$?
[ $rc = 10 ] && good "  a list line with one hex digit changed: refused 10" || bad "changed list line: exit $rc, not 10"
clean_walls
chmod u+w "$PR/indep-walls/APPROVED"; cat "$BASE/APPROVED.keep" > "$PR/indep-walls/APPROVED"; chmod 0400 "$PR/indep-walls/APPROVED"
[ "$(sha256sum "$PR/indep-walls/APPROVED" | cut -c1-64)" = "$(sha256sum "$HERE/APPROVED.after" | cut -c1-64)" ] && good "the planted list put back as APPROVED.after" || bad "the list was not put back"

say "the path map's structural pass over the new tracked paths (the lesson of ACT-PATHMAP-NS-2)"
( cd "$R" && PYTHONPATH="$R/src" python3 -B -m gov.check.pathmap ) > "$BASE/pathmap.txt" 2>&1; rc=$?
cat "$BASE/pathmap.txt" | head -5
[ $rc = 0 ] && good "gov.check.pathmap at the commit with the three briefs tracked: exit 0, no finding (3 files under indep-briefs/memory-audit/ each in one namespace)" || bad "the pathmap check: exit $rc"

say "undo: apply.sh undo, the removal committed as the package's undo line says (no git add), then check"
AP undo > "$BASE/undo.txt" 2>&1; cat "$BASE/undo.txt"; expect "$BASE/undo.txt" "state before" "undone"
git -C "$R" commit -q -m "ACT-MEMORY-AUDIT-INSTALL-1 undone" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1129" --trailer "Role: owner" -- "$BR" || bad "the undo commit"
git -C "$R" show --stat --format= HEAD | tail -1
git -C "$R" show --name-status --format= HEAD | tee "$BASE/undo-staged.txt"
[ "$(grep -c '^D' "$BASE/undo-staged.txt")" = 3 ] && good "the undo commit: exactly 3 D" || bad "the undo commit is not 3 D"
[ "$(sha256sum "$PR/indep-walls/APPROVED" | cut -c1-64)" = 6b923cb4d552077f99924fd5df38f1a448b21f863c4755c9ff4e0dcfb28ed959 ] && good "the list byte for byte as before (6b923cb4d552)" || bad "the list is not as before"
[ -d "$R/governance/project/indep-briefs/sgx1" ] && [ ! -e "$R/$BR" ] && good "set-up A's folder untouched; memory-audit/ gone" || bad "the folders after the undo"
AP check | tail -1 | tee "$BASE/check3.txt"; expect "$BASE/check3.txt" "ready to apply" "check: ready to apply again"
launch writer "$BR/writer.md" $W mem-new-1 1; rc=$?
[ $rc = 10 ] && good "after the undo a launch under the brief is refused again (10)" || bad "after the undo a launch: exit $rc"
clean_walls

say "live files: unchanged"
live_hashes > "$BASE/live-after.txt" 2>&1 || true
if cmp -s "$BASE/live-before.txt" "$BASE/live-after.txt"; then good "live files unchanged ($(wc -l < "$BASE/live-after.txt") lines hashed; the main tree's status and head the same)"
else diff "$BASE/live-before.txt" "$BASE/live-after.txt" | head; bad "a live file changed"; fi
date -u '+end %Y-%m-%dT%H:%M:%SZ'
echo "checks passed: $OKS; failures: $FAILS"
[ -n "${KEEP:-}" ] || { chmod -R u+w "$BASE" 2>/dev/null; rm -rf "$BASE"; echo "work/ removed"; }
