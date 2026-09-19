#!/usr/bin/env bash
# P2-AR-0041 (round-3 integration) — re-run each round-3 builder's OWN probes against the integrated binary.
#
# Every probe is run UNEDITED from where it was merged (release/capability-baseline/repair-1/r3-<ws>/evidence/), with
# the integrated tree as WT and its target/release/gov as the binary; those probes write only to stdout and to a
# private scratch directory, never into their workstream's directory. Two exceptions, each labelled:
#   * WS-3's R3-WS03-probes.py drives the P2-ADJ-0002 surface the integration unified (`trust t2-binding --provision`,
#     the bundle format): it is run UNEDITED (to show exactly what changed) and as the labelled derived copy
#     derived/R3-WS03-probes.unified.P2-AR-0041.py (its header lists every change);
#   * WS-4's observational probe is run through run-observe.P2-AR-0041.sh, a copy of WS-4's runner changed only in
#     where it reads the probe and writes its output; ws04d runs the labelled derived copy
#     derived/ws04r3_observe.claim-time.P2-AR-0041.rs (obs_b premises changed by WS-5; header lists them).
#   * WS-2's WS02-r3-supplementary.py is also run as the labelled derived copy
#     derived/WS02-r3-supplementary.chain-na.P2-AR-0041.py (fixture states the scenario chain WS-5 now computes; header lists it).
# Outputs: unedited/<name>.out and derived-runs/<name>.out beside this script. Scratch: $P2AR0041_SCRATCH (required).
#
# Usage: run-builder-probes.sh <which>...   which ∈ ws02 ws02d ws03 ws03d ws04 ws04d ws06 ws07 ws07ip ws08inv ws09
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(git -C "$HERE" rev-parse --show-toplevel)"
R="$WT/release/capability-baseline/repair-1"
GOVBIN="$WT/target/release/gov"
SCRB="${P2AR0041_SCRATCH:?set P2AR0041_SCRATCH}"
mkdir -p "$SCRB" "$HERE/unedited" "$HERE/derived-runs"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
hdr() {  # hdr <out> <probe-file>
  {
    echo "# P2-AR-0041 builder-probe re-run: $2"
    echo "# probe sha256 $(sha256sum "$2" | cut -c1-64)"
    echo "# integrated tree $WT HEAD $(git -C "$WT" rev-parse HEAD); product files differing: $(git -C "$WT" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock | wc -l)"
    echo "# gov $GOVBIN sha256 $(sha256sum "$GOVBIN" | cut -c1-64)"
    echo "# date $(date -u +%FT%TZ)"
  } > "$1"
}
for w in "$@"; do
  S="$(mktemp -d "$SCRB/bp-$w-XXXXXX")"
  case "$w" in
    ws02)
      P="$R/r3-ws02/evidence/WS02-r3-supplementary.py"; O="$HERE/unedited/WS02-r3-supplementary.out"; hdr "$O" "$P"
      ( WT="$WT" GOV="$GOVBIN" P2AR0033_SCRATCH="$S" timeout 3000 python3 "$P" ) >> "$O" 2>&1; echo "[exit=$?]" >> "$O" ;;
    ws02d)
      P="$HERE/derived/WS02-r3-supplementary.chain-na.P2-AR-0041.py"; O="$HERE/derived-runs/WS02-r3-supplementary.chain-na.P2-AR-0041.out"; hdr "$O" "$P"
      ( WT="$WT" GOV="$GOVBIN" P2AR0033_SCRATCH="$S" timeout 3000 python3 "$P" ) >> "$O" 2>&1; echo "[exit=$?]" >> "$O" ;;
    ws03)
      P="$R/r3-ws03/evidence/R3-WS03-probes.py"; O="$HERE/unedited/R3-WS03-probes.out"; hdr "$O" "$P"
      ( timeout 3000 python3 "$P" "$GOVBIN" "$S" ) >> "$O" 2>&1; echo "[exit=$?]" >> "$O" ;;
    ws03d)
      P="$HERE/derived/R3-WS03-probes.unified.P2-AR-0041.py"; O="$HERE/derived-runs/R3-WS03-probes.unified.P2-AR-0041.out"; hdr "$O" "$P"
      ( timeout 3000 python3 "$P" "$GOVBIN" "$S" ) >> "$O" 2>&1; echo "[exit=$?]" >> "$O" ;;
    ws04)
      P2AR0035_SCRATCH="$S" bash "$HERE/run-observe.P2-AR-0041.sh" integrated "$(git -C "$WT" rev-parse HEAD)" "" \
        ws04r3::a_cit_declined_during_another_tasks_claim_does_not_block_its_close ;;
    ws04d)
      OBSERVE_PROBE="$HERE/derived/ws04r3_observe.claim-time.P2-AR-0041.rs" P2AR0035_SCRATCH="$S" \
        bash "$HERE/run-observe.P2-AR-0041.sh" integrated-derived "$(git -C "$WT" rev-parse HEAD)" ;;
    ws06)
      P2AR0037_SCRATCH="$S" bash "$R/r3-ws06/evidence/RUN-SUPP.sh" "$WT" "$HERE/unedited/SUPP-ws06-r3.out" ;;
    ws07)
      P="$R/r3-ws07/evidence/ws07_r3_named_checks.py"; O="$HERE/unedited/ws07_r3_named_checks.out"; hdr "$O" "$P"
      ( GOV_BIN="$GOVBIN" WS07R3_SCRATCH="$S" timeout 3000 python3 "$P" ) >> "$O" 2>&1; echo "[exit=$?]" >> "$O" ;;
    ws07ip)
      P="$R/r3-ws07/evidence/ip_task_close_registration.py"; O="$HERE/unedited/ip_task_close_registration.out"; hdr "$O" "$P"
      ( GOV_BIN="$GOVBIN" WS07R3_SCRATCH="$S" SCRATCH="$S" timeout 3000 python3 "$P" ) >> "$O" 2>&1; echo "[exit=$?]" >> "$O" ;;
    ws08inv)
      P="$R/r3-ws08/evidence/r1-invariants.sh"; O="$HERE/unedited/ws08-r1-invariants.out"; hdr "$O" "$P"
      ( bash "$P" 53897c1a44157e5af81b176017bc7ded6a63b9cd ) >> "$O" 2>&1; echo "[exit=$?]" >> "$O" ;;
    ws09)
      P="$R/r3-ws09-11/evidence/probes/tiny_unprovisioned_adoption.py"; O="$HERE/unedited/tiny_unprovisioned_adoption.out"; hdr "$O" "$P"
      ( GOV_BIN="$GOVBIN" SCRATCH="$S" timeout 3000 python3 "$P" ) >> "$O" 2>&1; echo "[exit=$?]" >> "$O" ;;
    *) echo "unknown: $w"; exit 2 ;;
  esac
done
