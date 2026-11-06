#!/usr/bin/env bash
# D-4b's memory measure at one point (DEC-1055 (7); W2-61's procedure, docs/research/W2-61-baseline.md §8).
#   measure.sh <point: m1|m2|m3> <commit> [--pinned-too]
# A clone of the commit; its store rebuilt (the D-4b rebuild lock); the hidden half's line-cited gold sources re-pinned
# at the clone's head (repin_gold.py, counts only); the visible half copied from the clone into the sets root outside
# every tree (~/gov-os-eval); W2-61's measure on all 48 questions with the CLONE'S OWN CODE: two runs on one index, a
# rebuild, a third with --compare (the noise band). --pinned-too adds one run with the pinned gov (the baseline only).
# Only the CTO runs it (measure.py refuses the hidden part to a measured role). Prints counts and figures only.
set -euo pipefail
POINT=$1; COMMIT=$2; PINNED=${3:-}
R=/home/usain/Dynamic-Agentic-Engineering-OS
O=$R/.gov-runtime/scratch/orchestrator
EVAL=$HOME/gov-os-eval
RUN=$HOME/gov-os-runs/D4B/$POINT
LOG=$RUN/measure.log
mkdir -p "$RUN"
exec > >(tee -a "$LOG") 2>&1
echo "== $(date '+%F %T') D-4b $POINT at $COMMIT"
[ -d "$RUN/repo" ] || git clone -q --no-hardlinks "$R" "$RUN/repo"
# every branch of the main repository (a short id cannot be fetched by name), then the commit
git -C "$RUN/repo" fetch -q "$R" "+refs/heads/*:refs/remotes/main/*" && git -C "$RUN/repo" checkout -q --detach "$COMMIT"
HEAD12=$(git -C "$RUN/repo" rev-parse --short=12 HEAD); echo "clone at $HEAD12"
# the clone's own gov, for the measure's calls
# DEC-1068 (4): every search's ranked output kept, in call order (the measure calls in question order, and its text log
# names each question's calls), so a run can be re-scored after an approved label change without running again. Kept
# in the sets root (mode 700, outside every tree); no argument (no question text) is stored.
cat > "$RUN/gov" <<EOF
#!/usr/bin/env bash
if [ "\$1" = retrieve ] && [ -n "\${GOV_KEEP:-}" ]; then
  n=\$(flock "\$GOV_KEEP/.n.lock" sh -c 'n=\$(cat "\$0/.n" 2>/dev/null || echo 0); n=\$((n+1)); echo \$n > "\$0/.n"; echo \$n' "\$GOV_KEEP")
  PYTHONPATH="$RUN/repo/src" python3 -m gov.cli.main "\$@" | tee "\$GOV_KEEP/\$(printf %05d \$n).json"
  exit \${PIPESTATUS[0]}
fi
PYTHONPATH="$RUN/repo/src" exec python3 -m gov.cli.main "\$@"
EOF
chmod +x "$RUN/gov"
rebuild() {
  local t0=$(date +%s)
  flock /tmp/gov-os-d4b-rebuild.lock env -u GOV_TICKET PYTHONPATH="$RUN/repo/src" \
    bash "$O/tools/rebuild_slot.sh" "$RUN/repo" --seed > "$RUN/rebuild-$1.out" 2>&1 || { echo "REBUILD FAILED ($1)"; tail -5 "$RUN/rebuild-$1.out"; exit 1; }
  echo "rebuild $1: $(( $(date +%s) - t0 )) s"
}
rebuild 1
echo "-- the hidden half's gold sources re-pinned at $HEAD12"
# DEC-1084 (ACT-GUARD-SETS-1): the sets-root form; no line names a hidden folder (the tools build it)
python3 "$O/drafts/d4b/repin_gold.py" --sets-root "$EVAL" --set memory-retrieval --part hidden "$RUN/repo" --write || { echo "REPIN UNRESOLVED: stop, to the owner"; exit 1; }
echo "-- the visible half's anchors at $HEAD12 (a dry run: any unresolved anchor stops the measure)"
python3 "$O/drafts/d4b/repin_gold.py" "$RUN/repo/fixtures/evaluation/memory-retrieval/visible" "$RUN/repo" || { echo "VISIBLE ANCHORS UNRESOLVED: a test designer re-anchors them before the measure"; exit 1; }
echo "-- the visible half from the clone"
# Overwritten file by file, never deleted: the guard refuses the CTO's deletes outside the project (DEC-1050 (8)), and
# a script must not route round that (DEC-849). The visible set only grows; a file the clone lacks is named and stops.
mkdir -p "$EVAL/fixtures/evaluation/memory-retrieval/visible"
cp -a "$RUN/repo/fixtures/evaluation/memory-retrieval/visible/." "$EVAL/fixtures/evaluation/memory-retrieval/visible/"
extra=$(comm -13 <(ls "$RUN/repo/fixtures/evaluation/memory-retrieval/visible") <(ls "$EVAL/fixtures/evaluation/memory-retrieval/visible"))
[ -z "$extra" ] || { echo "STOP: the sets root's visible half holds files the clone lacks: $extra"; exit 1; }
echo "visible questions: $(ls "$EVAL/fixtures/evaluation/memory-retrieval/visible" | wc -l); hidden: $(python3 -I "$O/drafts/d4b/count_gold.py" --sets-root "$EVAL" --set memory-retrieval --part hidden "$RUN/repo" | sed -n 's/^questions: \([0-9]*\);.*/\1/p')"
measure() {
  local tag=$1; shift
  local t0=$(date +%s)
  local keep=$EVAL/runs/$POINT/$tag; mkdir -p "$keep"; chmod 700 "$EVAL/runs" 2>/dev/null; : > "$keep/.n"
  GOV_KEEP=$keep env -u GOV_TICKET PYTHONPATH="$RUN/repo/src" bash "$O/tools/heavy_slot.sh" python3 -m gov.retrieval.measure memory-retrieval \
    --root "$RUN/repo" --sets-root "$EVAL" --part all --out "$RUN/records" "$@" > "$RUN/measure-$tag.txt" 2>&1 || { echo "MEASURE FAILED ($tag)"; tail -5 "$RUN/measure-$tag.txt"; exit 1; }
  echo "measure $tag: $(( $(date +%s) - t0 )) s"; { grep -iE "^(hit@5|full evidence|total|budget)" "$RUN/measure-$tag.txt" || true; } | sed -n 1,8p
}
measure run1 --gov "$RUN/gov"
FIRST=$(ls -t "$RUN/records"/*.json | head -1)
measure run2 --gov "$RUN/gov"
rebuild 2
measure run3 --gov "$RUN/gov" --compare "$FIRST"
[ "$PINNED" = --pinned-too ] && measure pinned --gov "$HOME/.local/bin/gov"
echo "== $(date '+%F %T') done; records in $RUN/records"
