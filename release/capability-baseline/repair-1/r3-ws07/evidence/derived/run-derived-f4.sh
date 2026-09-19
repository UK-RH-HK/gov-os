#!/usr/bin/env bash
# usage: derived-f4.sh <label>  — runs the labelled derived F4 copy in shim mode against <worktree>/target/release/gov
WT=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/wt/p2-repair1-r3-ws07
SCR=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/p2ar0038
E=$WT/release/capability-baseline/repair-1/r3-ws07/evidence; G=$WT/release/capability-baseline/audit-0/gamma-r/evidence; L=$1
export PYTHONDONTWRITEBYTECODE=1; for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
ROOT=$(mktemp -d $SCR/derived-mirror-XXXXXX); mkdir -p $ROOT/target/release
for e in $(ls -A $WT); do [ "$e" = target ] || ln -sfn "$WT/$e" "$ROOT/$e"; done
cat > $ROOT/target/release/gov <<EOT
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$WT/target/release/gov"
export P2AR0022_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$ROOT/release/capability-baseline/repair-1/integration-2/evidence/builder-probes/derived/gov-owner-channel-shim.root-channel.P2-AR-0032.py" "\$@"
EOT
chmod +x $ROOT/target/release/gov
RUN=$(mktemp -d $SCR/derived-run-XXXXXX); mkdir -p $RUN/tmp; cp $E/derived/F4-plugins.registry-path.P2-AR-0038.sh $RUN/; ln -s $G/lib.sh $RUN/lib.sh
mkdir -p $E/probes/$L; OUT=$E/probes/$L/derived.gamma-r.F4-plugins.registry-path.shim.out
{ echo "# P2-AR-0038 labelled derived probe run: derived/F4-plugins.registry-path.P2-AR-0038.sh mode=shim (lib.sh: symlink to the unedited audit-0 file)"; echo "# HEAD $(git -C $WT rev-parse HEAD); gov $(sha256sum $WT/target/release/gov | cut -c1-64)"; } > $OUT
export P2AR0022_SHIM_LOG=$OUT.shimlog; : > $P2AR0022_SHIM_LOG
( cd $RUN && TMPDIR=$RUN/tmp GOV=$ROOT/target/release/gov WT=$ROOT PROBES=$RUN timeout 1500 bash $RUN/F4-plugins.registry-path.P2-AR-0038.sh ) >> $OUT 2>&1
echo "[exit=$?]" >> $OUT
