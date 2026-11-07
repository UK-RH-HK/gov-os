#!/usr/bin/env bash
# W2-137's S5 (DEC-1090 (2)): a clone of w2/integrate with W2-137 (and W2-138) merged, searched with the clone's own
# code against the live shared reranker (the pinned service; W2-137 changes the client's cap, the service already
# accepts 512). (1) 20 and 10 searches at once, three rounds each, by W2-112's method (conc.py: nvidia-smi every 0.25 s,
# the reranker's MEMORY lines, errors and fallbacks); (2) the 138 through the measure, against E0 (hit@5 and MRR within
# 1). One GPU job in its own process group, the backstop armed. Counts only.
set -uo pipefail
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b; S=$HOME/gov-os-runs/PAT-1
R=/home/usain/Dynamic-Agentic-Engineering-OS; RUN=$HOME/gov-os-runs/D4B/w2-137-s5; C=$RUN/repo; OUT=$RUN/out; mkdir -p "$OUT"
exec > >(tee -a "$RUN/s5.log") 2>&1
unset GOV_STORE GOV_TICKET
G=$(ps -o pgid= -p $$ | tr -d ' '); setsid bash $O/tools/gpu_backstop.sh "$G" < /dev/null > /dev/null 2>&1 & BS=$!
COMMIT=$(git -C "$R" rev-parse w2/integrate)
echo "== $(date '+%F %T') W2-137 S5 at ${COMMIT:0:12}; backstop $BS on group $G"
[ -d "$C" ] || git clone -q --no-hardlinks "$R" "$C"
git -C "$C" fetch -q "$R" "+refs/heads/*:refs/remotes/main/*" && git -C "$C" checkout -q --detach "$COMMIT" || { echo "STOP: checkout"; exit 1; }
grep -q 'MAX_REQUEST_TEXTS = 64' "$C/src/gov/retrieval/rerank.py" || { echo "STOP: the clone lacks W2-137"; exit 1; }
SEED=$(flock /home/usain/gov-os-worktrees/W2-00-store.lock readlink -f /home/usain/gov-os-worktrees/W2-00-store)
t0=$(date +%s); flock /tmp/gov-os-d4b-rebuild.lock bash $O/tools/rebuild_pinned.sh "$C" --seed "$SEED" > "$RUN/rebuild.out" 2>&1 || { echo "REBUILD FAILED"; exit 1; }
echo "rebuild: $(( $(date +%s) - t0 )) s (seed $SEED)"
cat > "$OUT/gov" <<EOG
#!/usr/bin/env bash
if [ "\$1" = retrieve ] && [ -n "\${GOV_KEEP:-}" ]; then
  n=\$(flock "\$GOV_KEEP/.n.lock" sh -c 'n=\$(cat "\$0/.n" 2>/dev/null || echo 0); n=\$((n+1)); echo \$n > "\$0/.n"; echo \$n' "\$GOV_KEEP")
  PYTHONPATH="$C/src" python3 -m gov.cli.main "\$@" | tee "\$GOV_KEEP/\$(printf %05d \$n).json"; exit \${PIPESTATUS[0]}
fi
PYTHONPATH="$C/src" exec python3 -m gov.cli.main "\$@"
EOG
chmod +x "$OUT/gov"
echo "== bursts"
CONC_GOV="$OUT/gov" CONC_ROOT="$C" python3 -I $S/conc.py "$OUT/conc.json" c20 c10 c20 c10 c20 c10
echo "== the 138"
for set in memory-retrieval:all:r80 memory-verdict:hidden:r60; do
  IFS=: read -r ST PART N <<< "$set"; K=$HOME/gov-os-eval/runs/w2-137-s5/$N; mkdir -p "$K" "$OUT/$N"; : > "$K/.n"
  env GOV_ROLE=orchestrator GOV_KEEP="$K" TMPDIR=/tmp/gov-os-emg-s5 PYTHONPATH="$C/src" bash $O/tools/heavy_slot.sh \
    python3 -m gov.retrieval.measure "$ST" --root "$C" --sets-root "$HOME/gov-os-eval" --part "$PART" --out "$OUT/$N" --gov "$OUT/gov" \
    > "$OUT/$N/measure.txt" 2> "$OUT/$N/measure.err" || echo "MEASURE FAILED ($N)"
done
python3 -I $D/e0_figures.py "W2-137 S5 (cap 64, integrate ${COMMIT:0:12})" $OUT/r80/measure.txt $OUT/r60/measure.txt
python3 -I $D/e0_figures.py "E0 (pin, cap 16)" $HOME/gov-os-runs/D4B/w4-e0/out/r80/measure.txt $HOME/gov-os-runs/D4B/w4-e0/out/r60/measure.txt
python3 -I $D/score138.py --same $OUT/r80/measure.txt $OUT/r60/measure.txt $HOME/gov-os-runs/D4B/w4-e0/out/r80/measure.txt $HOME/gov-os-runs/D4B/w4-e0/out/r60/measure.txt
bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1
echo "== $(date '+%F %T') S5 done"
