#!/usr/bin/env bash
# P2-AR-0014: re-run the audit-of-record probes named for BC-P2-01 / BC-P2-51, unedited, from the merged evidence
# directories; stdout+stderr of each go to $OUT/<probe>.out (never into the audit-0 evidence directories).
# usage: OUT=<dir> SCR=<scratch parent> bash run-probes.sh   (from anywhere; WT is fixed below)
set -u
WT=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/wt/p2-repair1-ws01-12
A=$WT/release/capability-baseline/audit-0
: "${OUT:?}"; : "${SCR:?}"
mkdir -p "$OUT" "$SCR" "$SCR/alpha" "$SCR/beta" "$SCR/delta" "$SCR/epsilon" "$SCR/zeta"
export PATH="$HOME/.cargo/bin:$PATH"
cd "$WT"
hdr() { echo "# P2-AR-0014 re-run of $1 (unedited) at worktree HEAD $(git -C "$WT" rev-parse HEAD) dirty=$(git -C "$WT" status --porcelain | wc -l); gov sha256 $(sha256sum "$WT/target/release/gov" | cut -c1-64); $(date -u +%FT%TZ)"; }
run() { local name="$1"; shift; { hdr "$name"; "$@"; echo "# exit=$?"; } > "$OUT/$name.out" 2>&1; echo "$name done"; }
run AC01-09-13-14-universe-identity-binding python3 "$A/synthesis/evidence/AC01-09-13-14-universe-identity-binding.py"
run AC06-oracle-format-search bash "$A/synthesis/evidence/AC06-oracle-format-search.sh"
(cd "$A/alpha-r/evidence" && PROBE_TMP="$SCR/alpha" run alpha-r.C0-contract-derived-views python3 C0-contract-derived-views.py)
PROBE_TMP="$SCR/beta" run beta-r.DERIVED-views-reconciliation python3 "$A/beta-r/evidence/DERIVED-views-reconciliation.py"
run gamma-r.DV-derived-views python3 "$A/gamma-r/evidence/DV-derived-views.py"
PROBE_SCRATCH="$SCR/delta" run delta-r.DERIVED-VIEWS-JKLMN python3 "$A/delta-r/evidence/DERIVED-VIEWS-JKLMN.py"
SCRATCH="$SCR/epsilon" run epsilon-r.V-oracle-format-and-contract-views bash "$A/epsilon-r/evidence/V-oracle-format-and-contract-views.sh"
ZPROBE_SCRATCH="$SCR/zeta" run zeta-r.DV-derived-view-reconciliation python3 "$A/zeta-r/evidence/DV-derived-view-reconciliation.py"
