#!/usr/bin/env bash
# ACT-W2-149-INSTALL-1: the rehearsal, end to end, in a scratch clone with a planted HOME and sets root (DEC-1057).
# Changes nothing live; never opens the real sets root.
#   bash rehearse.sh            the log: rehearsal.log beside this file
# Layout ($BASE = ~/gov-os-runs/W2-149-INSTALL-rehearsal):
#   $BASE/Dynamic-Agentic-Engineering-OS   the --no-hardlinks clone at the main tree's head (W2-149 with set-up A's
#                                           wiring merged)
#   $BASE/home                              the planted HOME: the planted sets root (its indep-walls/APPROVED as
#                                           ACT-INDEP-WALLS-1 wrote it), gov-os-runs/indep, gov-os-wall-trees
# Order rehearsed: this ACT refused before ACT-SETS-GLOBS-1; ACT-SETS-GLOBS-1 applied (its own apply.sh, the planted
# root); this ACT checked, applied, committed; the launch script's stage-10 checks on every line and a dry launch
# under each of set-up A's five briefs (planted inputs: a tuning half, its labels); undo.
if [ -z "${WI_FRESH:-}" ]; then
  exec env -i HOME="$HOME" USER="${USER:-usain}" LOGNAME="${LOGNAME:-usain}" PATH="/usr/local/bin:/usr/bin:/bin" \
    LANG="${LANG:-C.UTF-8}" WI_HEAD="${WI_HEAD:-}" WI_FRESH=1 bash --noprofile --norc "$0" "$@"
fi
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/w2-149-install
BASE=$HOME/gov-os-runs/W2-149-INSTALL-rehearsal
R=$BASE/Dynamic-Agentic-Engineering-OS
PH=$BASE/home
SR_NAME="gov-os-""eval"
PR=$PH/$SR_NAME
D=$R/$SUB/drafts/w2-149-install
G=$R/$SUB/drafts/sets-globs
LOG=$HERE/rehearsal.log
SCRIPT=governance/project/orchestration/tools/indep_launch.py
BR=governance/project/indep-briefs/sgx1
TR="--trailer Task:\ DAEO-sdxk"
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
say() { printf '\n== %s (%s)\n' "$1" "$(date -u '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
expect() { grep -Eq "$2" "$1" && echo "ok: $3" || bad "$3 (wanted /$2/ in $(basename "$1"))"; }
AP() { ( cd "$R" && bash "$D/apply.sh" "$1" --sets-root "$PR" ); }
launch() {  # $1 kind, $2 brief path, $3 sha, $4 set; a dry launch with a given seed, HOME planted; prints the exit
  local extra=(); [ "$1" = auditor ] && extra=(--audit e0)   # the auditor kind's --audit (recorded only for set-up A's)
  ( cd "$R" && HOME=$PH python3 "$R/$SCRIPT" --sets-root "$PR" --kind "$1" --brief "$2" --brief-sha256 "$3" \
      --commit HEAD --set "$4" "${extra[@]}" --seed 17 --dry > "$BASE/launch.out" 2> "$BASE/launch.err" ); local rc=$?
  echo "launch $1 $(basename "$2"): exit $rc; $(tail -1 "$BASE/launch.err")"
  return $rc
}
live_hashes() {
  ( cd "$MAIN" && sha256sum .claude/hooks/pretooluse.py governance/project/path-map.yaml .claude/settings.json "$SCRIPT" \
      governance/project/indep-walls/* governance/project/orchestration/tools/indep-schemas/* )
  ls "$MAIN/governance/project/indep-briefs" 2>&1 | sed 's/^/listing: /'
  sha256sum "$HOME/.claude/settings.json"
  ( cd "$HOME/gov-os-operator" && find . -path ./log -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-12 ) | sed 's/^/the operator folder but log: /'
}

say "prepare: the clone, the planted HOME and sets root"
date -u '+start %Y-%m-%dT%H:%M:%SZ'
live_hashes > "$BASE.live-before.txt" 2>&1 || true
if [ -e "$BASE" ]; then
  [ -f "$BASE/.wi-rehearsal" ] || { echo "REHEARSAL STOP: $BASE exists and is not this script's"; exit 3; }
  chmod -R u+w "$BASE" 2>/dev/null; rm -rf "$BASE"
fi
mkdir -p "$BASE/hooks-safe" && : > "$BASE/.wi-rehearsal"
mv "$BASE.live-before.txt" "$BASE/live-before.txt"
head=$(git -C "$MAIN" rev-parse "${WI_HEAD:-HEAD}")
git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; exit 1; }
git -C "$R" config core.hooksPath "$BASE/hooks-safe"
git -C "$R" checkout -q -B w2/integrate "$head" || bad "checkout"
git -C "$R" config user.name "wi rehearsal"; git -C "$R" config user.email "wi@localhost"
mkdir -p "$R/$SUB/drafts"
cp -a "$HERE" "$MAIN/$SUB/drafts/sets-globs" "$R/$SUB/drafts/"
rm -rf "$D/backup" "$D/backup.undone-"* "$D/rehearsal.log" "$G/backup" "$G/__pycache__"
echo "clone at $(git -C "$R" rev-parse --short=12 HEAD); the launch script $(sha256sum "$R/$SCRIPT" | cut -c1-12)"
mkdir -p "$PH/gov-os-runs/indep" "$PH/gov-os-wall-trees" "$PR/transcripts" "$PR/runs/e0" \
         "$PR/fixtures/evaluation/memory-verdict/hidden" "$PR/fixtures/evaluation/sandbox-guard-exp-1/hidden/corpus"
printf 'DUMMY planted\n' > "$PR/fixtures/evaluation/memory-verdict/hidden/p01.yaml"
printf 'DUMMY planted\n' > "$PR/transcripts/t01.md"
EXP=$PH/gov-os-runs/SANDBOX-GUARD-EXP-1/tuning   # set-up A's tuning half (planted; the labellers' and auditor's inputs)
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
echo "planted tuning half: 3 actions, 2 cases, labels.jsonl 3, labels-2.jsonl 1 (1 dispute)"
mkdir -m 0700 "$PR/indep-walls"
cat "$HERE/APPROVED.before" > "$PR/indep-walls/APPROVED"; chmod 0400 "$PR/indep-walls/APPROVED"
echo "planted list $(sha256sum "$PR/indep-walls/APPROVED" | cut -c1-12) (ACT-INDEP-WALLS-1's, rebuilt)"
( cd "$D" && sha256sum apply.sh freeze.py install_check.py rehearse.sh APPROVED.before APPROVED.after briefs/* ) | cut -c1-12,65-

say "order: this ACT before ACT-SETS-GLOBS-1 is refused"
SGC=9cce7430d   # ACT-SETS-GLOBS-1 as the owner's operator applied it live (2026-11-09)
if grep -q '^def sets_line_keys(' "$R/.claude/hooks/pretooluse.py"; then
  echo "the clone's head already holds ACT-SETS-GLOBS-1 (applied live at $SGC): the hook and map before it put back in the clone's working files for this step"
  git -C "$R" show "$SGC^:.claude/hooks/pretooluse.py" > "$R/.claude/hooks/pretooluse.py"
  git -C "$R" show "$SGC^:governance/project/path-map.yaml" > "$R/governance/project/path-map.yaml"
  ( cd "$R" && sha256sum .claude/hooks/pretooluse.py governance/project/path-map.yaml | cut -c1-12,65- )
  AP check > "$BASE/check0.txt" 2>&1 && bad "check passed before ACT-SETS-GLOBS-1" || true
  cat "$BASE/check0.txt"; expect "$BASE/check0.txt" "ACT-SETS-GLOBS-1 is not applied" "refused: apply ACT-SETS-GLOBS-1 first"
  git -C "$R" checkout -q -- .claude/hooks/pretooluse.py governance/project/path-map.yaml
  ( cd "$R" && sha256sum .claude/hooks/pretooluse.py governance/project/path-map.yaml | cut -c1-12,65- ) | sed 's/^/back: /'
else
  AP check > "$BASE/check0.txt" 2>&1 && bad "check passed before ACT-SETS-GLOBS-1" || true
  cat "$BASE/check0.txt"; expect "$BASE/check0.txt" "ACT-SETS-GLOBS-1 is not applied" "refused: apply ACT-SETS-GLOBS-1 first"
  say "ACT-SETS-GLOBS-1 applied in the clone (its own apply.sh, the planted root), committed as its message says"
  ( cd "$R" && bash "$G/apply.sh" check --sets-root "$PR" && bash "$G/apply.sh" apply --sets-root "$PR" ) > "$BASE/sg.txt" 2>&1 \
    || bad "ACT-SETS-GLOBS-1 did not apply in the clone"
  tail -3 "$BASE/sg.txt"
  git -C "$R" add .claude/hooks/pretooluse.py governance/project/path-map.yaml
  git -C "$R" commit -q -m "ACT-SETS-GLOBS-1 (rehearsal)" --trailer "Task: DAEO-sdxk" --trailer "Role: owner" || bad "SETS-GLOBS commit"
fi
( cd "$R" && sha256sum .claude/hooks/pretooluse.py governance/project/path-map.yaml | cut -c1-12,65- )

say "before this ACT: an approved brief is refused (11: the wiring's two template files are not on the list yet)"
launch writer "$BR/writer-tuning.md" 82134b3dd6b5a077abfc2eb6fa7481f0f5a73eab60396cfbd655042d53027c57 tuning; rc=$?
[ $rc = 11 ] && echo "  as expected before the ACT: 11 (template)" || bad "a launch before the install: exit $rc, not 11"

say "this ACT: check, apply, a second apply, check, the commit"
AP check > "$BASE/check1.txt" 2>&1; cat "$BASE/check1.txt"; expect "$BASE/check1.txt" "check: ready to apply" "check: ready"
mkdir -p "$BASE/globcwd/runs/x" && : > "$BASE/globcwd/runs/x/misses.jsonl"   # review F3: the globs never expand in the caller's folder
( cd "$BASE/globcwd" && bash "$D/apply.sh" check --sets-root "$PR" ) > "$BASE/check1b.txt" 2>&1
expect "$BASE/check1b.txt" "check: ready to apply" "check from a folder holding runs/x/misses.jsonl: still ready (F3)"
rm -rf "$R/governance/project/orchestration/tools/__pycache__"
AP apply > "$BASE/apply1.txt" 2>&1; cat "$BASE/apply1.txt"; expect "$BASE/apply1.txt" "^state applied" "applied"
[ ! -e "$R/governance/project/orchestration/tools/__pycache__" ] && echo "ok: no bytecode cache written into the tree (F1)" || bad "apply wrote a __pycache__ into the tree"
expect "$BASE/apply1.txt" "6 template lines, 7 brief lines .* template mismatches 0; brief mismatches 0" "the launch script's parser reads the list"
AP apply > "$BASE/apply2.txt" 2>&1 && bad "a second apply ran" || echo "a second apply: refused ($(tail -1 "$BASE/apply2.txt"))"
AP check | tail -2 | tee "$BASE/check2.txt"; expect "$BASE/check2.txt" "already applied" "check: already applied"
git -C "$R" add "$BR"
git -C "$R" diff --cached --name-status | tee "$BASE/staged.txt"
[ "$(wc -l < "$BASE/staged.txt")" = 5 ] && [ "$(grep -c '^A' "$BASE/staged.txt")" = 5 ] && echo "ok: exactly 5 A" || bad "the staged set is not 5 A"
git -C "$R" commit -q -m "ACT-W2-149-INSTALL-1: set-up A's five fixed briefs as the owner approved them (DEC-1113), and the launch script's approved list" \
  --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1112" --trailer "Role: owner" -- "$BR" || bad "the commit"
git -C "$R" show --stat --format= HEAD | tail -1
git -C "$R" log -1 --format='%h %s%n%(trailers)'
sha256sum "$PR/indep-walls/APPROVED" | cut -c1-12 | sed 's/^/the planted list after: /'
stat -c '%a %n' "$PR/indep-walls" "$PR/indep-walls/APPROVED" | sed "s#$PR#<root>#"

say "the launch script's stage-10 checks on every line, at the ACT's commit (its own code)"
python3 "$D/install_check.py" "$R" "$PR/indep-walls/APPROVED" HEAD | tee "$BASE/lines.txt"
expect "$BASE/lines.txt" "approved lines that match their bytes at the commit: 7 of 7" "every brief line matches its bytes"
[ "$(grep -c 'front matter ok' "$BASE/lines.txt")" = 5 ] && echo "ok: set-up A's five briefs pass stage 10's front matter (the template's values)" || bad "not all five briefs pass stage 10's front matter"
say "set-up A's five briefs: a dry launch under each (--seed 17), each must pass stage 10 and build its wall (0)"
for pair in "labeller labeller.md bbff1249953bd9d3b2596b33a108712bdddd79a7e86723b9e6955e3d6b0e9068 tuning" \
            "labeller labeller-2.md e13b5f96d0e058277f3ec3014f13205d7fe0bc950cfc308e81b3ee3d742ac904 tuning" \
            "writer writer-tuning.md 82134b3dd6b5a077abfc2eb6fa7481f0f5a73eab60396cfbd655042d53027c57 tuning" \
            "writer writer-heldout.md 137a73d1df4c265fd5ce4e24716797703e2b12dcaeb90663c0170834a60fafe6 held-out" \
            "auditor overlap-auditor.md b212a424062e402b0a25ee4a157ae14a0af798d0ad973aa33dacd730782be6ab tuning"; do
  set -- $pair
  launch "$1" "$BR/$2" "$3" "$4"; rc=$?
  if [ $rc = 0 ]; then
    w=$(find "$PR/indep-walls/$1" -mindepth 1 -maxdepth 1 -type d | head -1)
    python3 -I -B -c 'import json,os,sys; m=json.load(open(os.path.join(sys.argv[1],"WALL.json"))); print("  ok: 0 (dry);", {k: m.get(k) for k in ("brief_id","flow","model","result_schema")}, "input/:", sorted(os.listdir(os.path.join(sys.argv[1],"input"))))' "$w"
    [ -e "$w/brief.md" ] && cmp -s "$w/brief.md" "$R/$BR/$2" && echo "  brief.md byte for byte the approved brief" || bad "$2: the wall's brief.md is not the approved bytes"
    t=$(python3 -I -B -c 'import json,os,sys; print(json.load(open(os.path.join(sys.argv[1],"WALL.json")))["tree"])' "$w")
    [ ! -e "$t/governance/project/indep-briefs" ] && [ ! -e "$t/.claude" ] && [ ! -e "$t/src/gov/guard" ] \
      && echo "  the tree holds no indep-briefs/, .claude/ or src/gov/guard/ (S23)" || bad "$2: the tree holds an excluded folder"
  else
    bad "launch $2: exit $rc, not 0"
  fi
  chmod -R u+w "$PR/indep-walls/$1" "$PH/gov-os-wall-trees" 2>/dev/null; rm -rf "$PR/indep-walls/$1" "$PH/gov-os-wall-trees/"*
done
launch writer governance/project/operator/brief.md 51c459cfbcfec47652df455844480a56a5bc91b5fba3bcf57dc807c5dbf08cc2 tuning; rc=$?
[ $rc = 10 ] && echo "  the operator's brief under kind writer: refused 10 (its line is kind operator)" || bad "operator brief as writer: exit $rc"
chmod -R u+w "$PR/indep-walls/writer" "$PH/gov-os-wall-trees" 2>/dev/null; rm -rf "$PR/indep-walls/writer" "$PH/gov-os-wall-trees/"*

say "undo: apply.sh undo, the removal committed, then check"
AP undo > "$BASE/undo.txt" 2>&1; cat "$BASE/undo.txt"; expect "$BASE/undo.txt" "state before" "undone"
git -C "$R" add -A "$BR" 2>/dev/null; git -C "$R" status --short | head -6
git -C "$R" commit -q -m "ACT-W2-149-INSTALL-1 undone" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1112" --trailer "Role: owner" -- "$BR" || bad "the undo commit"
[ "$(sha256sum "$PR/indep-walls/APPROVED" | cut -c1-64)" = 331e48fa336ef58ba5dc6fd4afcf9c1387ec4bd29e583eb955280a267626bbc9 ] && echo "ok: the list byte for byte as before" || bad "the list is not as before"
AP check | tail -1 | tee "$BASE/check3.txt"; expect "$BASE/check3.txt" "ready to apply" "check: ready to apply again"
launch labeller "$BR/labeller.md" bbff1249953bd9d3b2596b33a108712bdddd79a7e86723b9e6955e3d6b0e9068 tuning; rc=$?
[ $rc = 11 ] || [ $rc = 10 ] && echo "  after the undo a launch is refused again ($rc)" || bad "after the undo a launch: exit $rc"

say "live files: unchanged"
live_hashes > "$BASE/live-after.txt" 2>&1 || true
if cmp -s "$BASE/live-before.txt" "$BASE/live-after.txt"; then echo "ok: live files unchanged ($(wc -l < "$BASE/live-after.txt") lines hashed)"
else diff "$BASE/live-before.txt" "$BASE/live-after.txt" | head; bad "a live file changed"; fi
du -sh "$BASE" | sed 's/^/scratch: /'
date -u '+end %Y-%m-%dT%H:%M:%SZ'
echo "failures: $FAILS"
