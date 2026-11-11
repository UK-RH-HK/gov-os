#!/bin/bash
# The launch rehearsal for the two briefs: a FAKE product repository with the launch scaffold (tools/mk_fake_examin.py), a
# PLANTED sets root (tmp/sr2, dummy approved list), and the real launch script run with --dry (it builds the wall and stops:
# no session starts). Checks that each brief's front matter resolves for kind writer, the tree is built from the scaffold
# commit, the selection is drawn, the briefs are left out of the tree, and a delivery of the visible/ sub-folder works.
#   bash launch_rehearsal.sh            the log is ../launch-rehearsal.log (ends "failures: <n>")
set -u
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/examin-sets
GOV=$D/tmp/clone
FE=$D/tmp/fake-examin
SR=$D/tmp/sr2
RUNS=$D/tmp/runs2
TREES=$D/tmp/trees2
PY=/home/usain/.local/share/gov-os/pin-797495bdfc70/bin/python
LOG=$D/launch-rehearsal.log
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
ok() { echo "ok   $1"; }
bad() { echo "FAIL $1"; FAILS=$((FAILS + 1)); }
chmod -R u+w "$TREES" "$SR" "$RUNS" "$FE" "$D/tmp/delivered-tmp" 2>/dev/null
rm -rf "$FE" "$SR" "$RUNS" "$TREES" "$D/tmp/delivered-tmp" "$D/tmp/out-set"
mkdir -p "$SR/indep-walls" "$RUNS" "$TREES"
$PY -I $D/tools/mk_fake_examin.py "$FE" "$GOV" "$D/EXAMIN-writer.md" "$D/PROVING-GROUND-writer.md" > $D/tmp/scaffold.txt || { bad "scaffold"; exit 1; }
sed 's/^/     /' $D/tmp/scaffold.txt
PIN=$(awk '$1=="pin"{print $2}' $D/tmp/scaffold.txt)
COPY=$(awk '$1=="copy"{print $2}' $D/tmp/scaffold.txt)
: > "$SR/indep-walls/APPROVED"
awk '$1=="template"{print $3 "  template  governance/project/indep-walls/" $2}' $D/tmp/scaffold.txt >> "$SR/indep-walls/APPROVED"
awk '$1=="brief" && $2=="examin-writer.md"{print $3 "  brief  writer  governance/project/indep-briefs/" $2}' $D/tmp/scaffold.txt >> "$SR/indep-walls/APPROVED"
awk '$1=="brief" && $2=="proving-ground-writer.md"{print $3 "  brief  writer  governance/project/indep-briefs/" $2}' $D/tmp/scaffold.txt >> "$SR/indep-walls/APPROVED"
cd "$FE" || exit 1
LAUNCH=$GOV/governance/project/orchestration/tools/indep_launch.py
run() { # run <set> <brief file name> <sha>
  GOV_INDEP_RUNS_DIR=$RUNS GOV_INDEP_TREES_DIR=$TREES $PY -I $LAUNCH --sets-root "$SR" --kind writer \
    --brief "governance/project/indep-briefs/$2" --brief-sha256 "$3" --commit "$PIN" --set "$1" --round 1 --seed 17 --dry
}
for pair in "examin examin-writer.md" "adoption-proving-ground proving-ground-writer.md"; do
  set -- $pair
  sha=$(awk -v n="$2" '$1=="brief" && $2==n{print $3}' $D/tmp/scaffold.txt)
  echo "--- launch --dry: set $1, brief $2"
  run "$1" "$2" "$sha" > $D/tmp/launch.out 2>&1; rc=$?
  tail -1 $D/tmp/launch.out | cut -c1-400 | sed 's/^/     /'
  [ "$rc" = 0 ] && ok "L1 [$1] the launch script accepts the brief and builds the wall (exit 0)" || { bad "L1 [$1] exit $rc"; sed 's/^/     /' $D/tmp/launch.out | cut -c1-300; }
done
echo "--- the walls the dry runs left (planted sets root only)"
for w in "$SR"/indep-walls/writer/*; do
  [ -d "$w" ] || continue
  run_id=$(basename "$w")
  echo "wall $run_id"
  [ -f "$w/brief.md" ] && ok "W1 [$run_id] brief.md is in the wall" || bad "W1 [$run_id] no brief.md"
  [ "$(cat "$w/input/selection.json" | $PY -I -c 'import json,sys; d=json.load(sys.stdin); print(d["commit"]==sys.argv[1], d["last_audit"], len(d["changed"]), len(d["sample"]))' "$PIN")" ] && echo "     selection: $($PY -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print("commit is the pin:", d["commit"]==sys.argv[2], "| last_audit:", d["last_audit"], "| changed:", len(d["changed"]), "| sample:", len(d["sample"]))' "$w/input/selection.json" "$PIN")"
  t="$TREES/writer-$run_id"
  [ -d "$t" ] && ok "W2 [$run_id] the tree is built ($(find "$t" -type f | wc -l) files)" || bad "W2 [$run_id] no tree"
  [ "$(cat "$t/governance/project/indep-walls/COPY-HEAD.txt" 2>/dev/null)" = "$COPY" ] && ok "W3 [$run_id] COPY-HEAD.txt in the tree holds the copy's own commit" || bad "W3 [$run_id] COPY-HEAD.txt"
  [ ! -e "$t/governance/project/indep-briefs" ] && ok "W4 [$run_id] the briefs folder is left out of the tree" || bad "W4 [$run_id] briefs are in the tree"
  [ -f "$t/src/mod00.py" ] && ok "W5 [$run_id] the product files are in the tree" || bad "W5 [$run_id] no product files"
done
echo "--- a delivery of a visible/ sub-folder and DRAW.txt (the launch script's own copy_set, round 1 move)"
mkdir -p $D/tmp/out-set/visible
for f in q01 q02; do echo "id: $f" > $D/tmp/out-set/$f.yaml; echo "id: v$f" > $D/tmp/out-set/visible/$f.yaml; done
echo "1 code-location SEED+k=18 even visible=q01 hidden=q02" > $D/tmp/out-set/DRAW.txt
$PY -I -c "
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location('il', '$LAUNCH'); il = importlib.util.module_from_spec(spec); spec.loader.exec_module(il)
dst = '$D/tmp/delivered-tmp'
got = il.copy_set('$D/tmp/out-set', dst)
print(sorted(r for r, _ in got))
sys.exit(0 if sorted(r for r, _ in got) == ['DRAW.txt', 'q01.yaml', 'q02.yaml', 'visible/q01.yaml', 'visible/q02.yaml'] else 1)
" && ok "D1 copy_set carries the sub-folder and DRAW.txt" || bad "D1 copy_set"
$PY -I -c "
import glob, sys
files = sorted(p.rsplit('/',1)[1] for p in glob.glob('$D/tmp/delivered-tmp/*.yaml'))
print('measure reads hidden/*.yaml (not recursive):', files)
sys.exit(0 if files == ['q01.yaml', 'q02.yaml'] else 1)" && ok "D2 a glob of hidden/*.yaml, as the measure reads it, holds the hidden half only" || bad "D2 glob"
echo
echo "failures: $FAILS"
