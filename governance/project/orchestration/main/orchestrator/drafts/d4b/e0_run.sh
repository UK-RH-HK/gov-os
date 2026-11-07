#!/usr/bin/env bash
# E0 (SEVEN-ANSWERS §7; DEC-1087 (11), DEC-1090 (1); declared in packages/LIFT-1/E0-DECLARATION.md before the run):
# the 138 through the live product on window 4's pin. A measure clone at c00d525fd420 (window 4's commit with the pool
# switched on), its store built by the PINNED gov (seeded from the integration store), then the product's measure run
# by the pin's own python with every search through ~/.local/bin/gov (pin-bcea09060ebc) on the live shared servers.
# Gold is re-anchored in memory per commit by the measure itself (W2-134): nothing writes the sets root. Counts only.
# One GPU job: its own process group, the GPU backstop armed on it, every heavy step through heavy_slot.sh.
set -uo pipefail
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator; D=$O/drafts/d4b
R=/home/usain/Dynamic-Agentic-Engineering-OS; COMMIT=c00d525fd4200303f4ad0fcc7e013d49e60dc2a6
RUN=$HOME/gov-os-runs/D4B/w4-e0; C=$RUN/repo; OUT=$RUN/out; mkdir -p "$OUT"
PINPY=$HOME/.local/share/gov-os/pin-bcea09060ebc/bin/python; GOV=$HOME/.local/bin/gov
exec > >(tee -a "$RUN/e0.log") 2>&1
unset GOV_STORE GOV_TICKET
G=$(ps -o pgid= -p $$ | tr -d ' '); setsid bash $O/tools/gpu_backstop.sh "$G" < /dev/null > /dev/null 2>&1 & BS=$!
echo "== $(date '+%F %T') E0: pin $(readlink -f $GOV); backstop $BS on group $G"
[ -d "$C" ] || git clone -q --no-hardlinks "$R" "$C"
git -C "$C" fetch -q "$R" "+refs/heads/*:refs/remotes/main/*" && git -C "$C" checkout -q --detach "$COMMIT" || { echo "STOP: checkout"; exit 1; }
echo "clone at $(git -C "$C" rev-parse --short=12 HEAD)"
t0=$(date +%s)
# the seed: the ready half the link points to, read under the integration store's own lock (a refresh holds it)
SEED=$(flock /home/usain/gov-os-worktrees/W2-00-store.lock readlink -f /home/usain/gov-os-worktrees/W2-00-store); echo "seed: $SEED"
flock /tmp/gov-os-d4b-rebuild.lock bash $O/tools/rebuild_pinned.sh "$C" --seed "$SEED" > "$RUN/rebuild.out" 2>&1 \
  || { echo "REBUILD FAILED"; tail -5 "$RUN/rebuild.out"; exit 1; }
echo "rebuild: $(( $(date +%s) - t0 )) s"
cat > "$OUT/gov" <<EOG
#!/usr/bin/env bash
if [ "\$1" = retrieve ] && [ -n "\${GOV_KEEP:-}" ]; then
  n=\$(flock "\$GOV_KEEP/.n.lock" sh -c 'n=\$(cat "\$0/.n" 2>/dev/null || echo 0); n=\$((n+1)); echo \$n > "\$0/.n"; echo \$n' "\$GOV_KEEP")
  s=\$(date +%s%N); "$GOV" "\$@" | tee "\$GOV_KEEP/\$(printf %05d \$n).json"; rc=\${PIPESTATUS[0]}
  echo \$(( (\$(date +%s%N) - s) / 1000000 )) >> "\$GOV_MS"; exit \$rc
fi
exec "$GOV" "\$@"
EOG
chmod +x "$OUT/gov"
for set in memory-retrieval:all:r80 memory-verdict:hidden:r60; do
  IFS=: read -r S PART N <<< "$set"; K=$HOME/gov-os-eval/runs/w4-e0/$N; mkdir -p "$K" "$OUT/$N"; : > "$K/.n"; : > "$OUT/$N/ms"
  t0=$(date +%s)
  env GOV_ROLE=orchestrator GOV_KEEP="$K" GOV_MS="$OUT/$N/ms" TMPDIR=/tmp/gov-os-emg-e0 \
    bash $O/tools/heavy_slot.sh "$PINPY" -m gov.retrieval.measure "$S" --root "$C" --sets-root "$HOME/gov-os-eval" --part "$PART" \
    --out "$OUT/$N" --gov "$OUT/gov" > "$OUT/$N/measure.txt" 2> "$OUT/$N/measure.err" || echo "MEASURE FAILED ($N)"
  echo "$N: $(( $(date +%s) - t0 )) s; median call $(sort -n $OUT/$N/ms | awk '{a[NR]=$1} END {if (NR) print a[int((NR+1)/2)]}') ms; unresolved anchors: $(grep -c -i unresolved $OUT/$N/measure.err)"
done
python3 -I $D/e0_figures.py "E0 (pin-bcea09060ebc, pool on, c00d525f)" $OUT/r80/measure.txt $OUT/r60/measure.txt
python3 -I $D/e0_figures.py "S11's check 11-06 (the clone's code at S11's merge, pool on)" $HOME/gov-os-runs/D4B/w4-32-product/r80/measure.txt $HOME/gov-os-runs/D4B/w4-32-product/r60/measure.txt
python3 -I $D/score138.py --same $OUT/r80/measure.txt $OUT/r60/measure.txt $HOME/gov-os-runs/D4B/w4-32-product/r80/measure.txt $HOME/gov-os-runs/D4B/w4-32-product/r60/measure.txt
bash $O/tools/proc.sh stop --grace 5 "$BS" > /dev/null 2>&1
echo "== $(date '+%F %T') E0 done"
