#!/usr/bin/env bash
# P2-AR-0054 (round-4 integration) — run BOTH merged builders' own probes against the INTEGRATED tree's release `gov`.
# Every probe of record is run UNEDITED from its own evidence directory; the residual branch's labelled derived copies
# are run as they are. Output is written ONLY under this directory (unedited/ and derived-runs/); no other
# workstream's repair-1/ directory is written to. Modelled on the round-3 integration's run-builder-probes.sh.
#
# usage: run-builder-probes.sh <probe-key> [more keys...]     (keys below)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
GOV="$WT/target/release/gov"
R1="$WT/release/capability-baseline/repair-1"
SCR="$WT/target/P2-AR-0054/probes"
mkdir -p "$SCR" "$HERE/unedited" "$HERE/derived-runs"
for k in $(env | grep -o '^GOV_[A-Z_]*'); do unset "$k"; done
hdr() { echo "# P2-AR-0054 builder-probe re-run on the integrated tree"; echo "# probe $1"; echo "# probe sha256 $(sha256sum "$1" | cut -d' ' -f1)";
        echo "# tree $WT HEAD $(git -C "$WT" rev-parse HEAD) dirty-product-files $(git -C "$WT" status --porcelain -- runtime cli framework tests | wc -l)";
        echo "# gov $GOV sha256 $(sha256sum "$GOV" | cut -d' ' -f1)"; echo "# date $(date -u +%FT%TZ)"; }
S() { local d="$SCR/$1-$(date +%s)"; mkdir -p "$d"; echo "$d"; }

for key in "$@"; do
case "$key" in
  # ---- WS-1 (P2-AR-0042), all unedited from r4-ws01/evidence ----
  owner-mutation-controls)
    P="$R1/r4-ws01/evidence/mutation-controls/owner-mutation-controls.py"
    { hdr "$P"; GOV="$GOV" WT="$WT" SCRATCH="$(S omc)" python3 "$P" 2>&1; echo "[exit=$?]"; } > "$HERE/unedited/owner-mutation-controls.out" ;;
  bc-p2-01-controls)
    P="$R1/ws01-12/evidence/bc-p2-01/mutation-controls.py"
    { hdr "$P"; ( cd "$R1/ws01-12/evidence/bc-p2-01" && python3 "$P" "$(S bc01)" ) 2>&1; echo "[exit=$?]"; } > "$HERE/unedited/bc-p2-01-round1-mutation-controls.out" ;;
  planted-faults)
    P="$R1/r4-ws01/evidence/owner-faults/planted-faults.py"
    { hdr "$P"; GOV="$GOV" SCRATCH="$(S faults)" python3 "$P" 2>&1; echo "[exit=$?]"; } > "$HERE/unedited/planted-faults.out" ;;
  release-tamper)
    P="$R1/r4-ws01/evidence/owner-faults/release-tamper.py"
    { hdr "$P"; GOV="$GOV" REPO="$WT" SCRATCH="$(S tamper)" python3 "$P" 2>&1; echo "[exit=$?]"; } > "$HERE/unedited/release-tamper.out" ;;
  product-mutations)
    P="$R1/r4-ws01/evidence/owner-faults/product-mutations.sh"
    T="$SCR/mutants/tree"; mkdir -p "$T"; git -C "$WT" archive HEAD | tar -x -C "$T"
    hdr "$P" > "$HERE/unedited/product-mutations.out"
    bash "$P" "$T" "$SCR/mutants/target" "$SCR/mutants/out.txt"; cat "$SCR/mutants/out.txt" >> "$HERE/unedited/product-mutations.out" ;;
  # ---- residual branch (P2-AR-0043 / -0053 / -0055) ----
  int3-o1)
    P="$R1/r3-ws07/evidence/ip_task_close_registration.py"
    { hdr "$P"; GOV_BIN="$GOV" WS07R3_SCRATCH="$(S ipreg-u)" python3 "$P" 2>&1; echo "[exit=$?]"; } > "$HERE/unedited/ip_task_close_registration.unedited.out"
    D="$R1/r4-residual/evidence/int3-o1/ip_task_close_registration.INT3-O1.P2-AR-0043.py"
    { hdr "$D"; GOV_BIN="$GOV" WS07R3_SCRATCH="$(S ipreg-d)" python3 "$D" 2>&1; echo "[exit=$?]"; } > "$HERE/derived-runs/ip_task_close_registration.INT3-O1.P2-AR-0043.out" ;;
  ws07-named)
    P="$R1/r3-ws07/evidence/ws07_r3_named_checks.py"
    { hdr "$P"; GOV_BIN="$GOV" WS07R3_SCRATCH="$(S named-u)" python3 "$P" 2>&1; echo "[exit=$?]"; } > "$HERE/unedited/ws07_r3_named_checks.unedited.out"
    D="$R1/r4-residual/evidence/int3-o1/ws07_r3_named_checks.INT3-O1.P2-AR-0043.py"
    { hdr "$D"; GOV_BIN="$GOV" WS07R3_SCRATCH="$(S named-d)" python3 "$D" 2>&1; echo "[exit=$?]"; } > "$HERE/derived-runs/ws07_r3_named_checks.INT3-O1.P2-AR-0043.out" ;;
  r4-o1)
    P="$R1/r4-residual/evidence/r4-o1/tools_install_task_close.py"
    { hdr "$P"; GOV_BIN="$GOV" WS07R3_SCRATCH="$(S r4o1)" python3 "$P" 2>&1; echo "[exit=$?]"; } > "$HERE/unedited/tools_install_task_close.out" ;;
  ws06-supp)
    P="$R1/r3-ws06/evidence/SUPP-ws06-r3.py"
    { hdr "$P"; GOV="$GOV" GOV_BIN="$GOV" WT="$WT" SCRATCH="$(S ws06)" python3 "$P" 2>&1; echo "[exit=$?]"; } > "$HERE/unedited/SUPP-ws06-r3.out" ;;
  *) echo "unknown probe key: $key" ;;
esac
echo "done: $key"
done
