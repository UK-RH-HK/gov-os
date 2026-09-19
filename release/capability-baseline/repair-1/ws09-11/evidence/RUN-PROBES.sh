#!/usr/bin/env bash
# P2-AR-0021 probe re-runs (regression evidence only). Runs the audit-of-record probes named by repair-delta for
# BC-P2-21/33/50/52 UNEDITED from their merged evidence directories, plus the builder probes, against the binary at
# <worktree>/target/release/gov (or GOV_BIN for the builder/synth probes), writing outputs to OUT (default: ./after).
# Usage (from the worktree root, after `cargo build --release`):
#   OUT=release/capability-baseline/repair-1/ws09-11/evidence/after SCR=<scratch> bash release/capability-baseline/repair-1/ws09-11/evidence/RUN-PROBES.sh
set -u
WT="$(pwd)"
OUT="${OUT:-$WT/release/capability-baseline/repair-1/ws09-11/evidence/after}"
SCR="${SCR:-$(mktemp -d)}"
mkdir -p "$OUT" "$SCR"/{x5,r12,s4raw,s4prep,s4neg,t1,z,q,b}
A0="$WT/release/capability-baseline/audit-0"
SYNTH_SCRATCH="$SCR/x5" python3 "$A0/synthesis/evidence/LEAD-X5-adoption-rerun-archives-os-adapter.py" > "$OUT/LEAD-X5-adoption-rerun-archives-os-adapter.out" 2>&1
(cd "$A0/beta-r/evidence" && PROBE_TMP="$SCR/r12" python3 R1-R2-legacy-and-chat-retirement.py) > "$OUT/R1-R2-legacy-and-chat-retirement.out" 2>&1
(cd "$A0/alpha-r/evidence" && RAW_SQL_STORE=1 PROBE_TMP="$SCR/s4raw" python3 S4-adopt-end-to-end.py) > "$OUT/S4-adopt-raw-sql-chat-store.out" 2>&1
(cd "$A0/alpha-r/evidence" && PROBE_TMP="$SCR/s4prep" python3 S4-adopt-end-to-end.py) > "$OUT/S4-adopt-end-to-end.out" 2>&1
(cd "$A0/alpha-r/evidence" && PROBE_TMP="$SCR/s4neg" python3 S4-T2-B2-negative.py) > "$OUT/S4-T2-B2-negative.out" 2>&1
(cd "$A0/alpha-r/evidence" && PROBE_TMP="$SCR/t1" python3 T1-roles.py) > "$OUT/T1-roles.out" 2>&1
(cd "$A0/zeta-r/evidence" && ZPROBE_SCRATCH="$SCR/z" python3 W01b-migration-plan-identity.py) > "$OUT/W01b-migration-plan-identity.out" 2>&1
(cd "$A0/zeta-r/evidence" && ZPROBE_SCRATCH="$SCR/z" python3 W01-artefact-identity.py) > "$OUT/W01-artefact-identity.out" 2>&1
SCRATCH="$SCR/q" bash "$A0/epsilon-r/evidence/Q-learning-upstream.sh" > "$OUT/Q-learning-upstream.out" 2>&1
SYNTH_SCRATCH="$SCR/b" python3 "$WT/release/capability-baseline/repair-1/ws09-11/evidence/B-ws0911-regression-probes.py" > "$OUT/B-ws0911-regression-probes.out" 2>&1
echo "done: $OUT"
