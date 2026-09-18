#!/usr/bin/env bash
# P2-AR-0007 synthesis: re-run the probe scripts of every family audit of record WITHOUT touching the family evidence
# directories of record. The probes write their .out files next to themselves, so they are run inside a disposable
# local clone of the audited commit (CLONE), built there with `cargo build --release` (binary sha256 must equal the
# worktree's). Regenerated outputs are then compared to the committed ones by COMPARE-family-outputs.py.
# usage: CLONE=<clone at 11d051e, built> SCR=<scratch parent> bash RERUN-family-probes.sh <family>
#   family: alpha-r | beta-r | gamma-r | delta-r | epsilon-r | zeta-r
set -u
F="$1"; : "${CLONE:?}"; : "${SCR:?}"
EV="$CLONE/release/capability-baseline/audit-0/$F/evidence"
mkdir -p "$SCR/$F"
echo "# family $F  clone HEAD $(git -C "$CLONE" rev-parse HEAD)  gov sha256 $(sha256sum "$CLONE/target/release/gov" | cut -c1-64)  start $(date -u +%FT%TZ)"
case "$F" in
  alpha-r)
    cd "$EV"
    export PROBE_TMP="$SCR/$F"
    for p in A1-policy-precedence A2-01-unprovisioned-posture A2-02-provisioned-ingress A2-03-post-install-tamper \
             A2-04-lock-identity-and-masquerade A2-05-rotation-revocation-recovery A2-06-offline-verification \
             A2-07-interrupted-install A2-08-reinstall-version-change A3-security-sensitivity A4-budget-governance \
             A5-emergency-controls B-repository-contract C0-contract-derived-views FRESH-invalidation S1-S2-release \
             S3-S4-role-flag-authority S3-init S4-T2-B2-negative S4-adopt-end-to-end S5-update S6-cross-machine T1-roles; do
      s=$(date +%s); (echo "# command: PROBE_TMP=<scratch> python3 $p.py"; python3 "$p.py" 2>&1) > "$p.out"; echo "$p exit=$? $(( $(date +%s)-s ))s"
    done
    (echo "# command: PROBE_TMP=<scratch> RAW_SQL_STORE=1 python3 S4-adopt-end-to-end.py  (fixture used as shipped, without the README-documented sqlite preparation)"; RAW_SQL_STORE=1 python3 S4-adopt-end-to-end.py 2>&1) > S4-adopt-raw-sql-chat-store.out; echo "S4-raw exit=$?"
    bash A2-00-ingress-census.sh > A2-00-ingress-census.out 2>&1; echo "A2-00 exit=$?"
    ;;
  beta-r)
    PROBE_TMP="$SCR/$F" bash "$EV/RUN-ALL.sh" ;;
  gamma-r)
    cd "$EV"
    for p in E1-authority E2-roles E3-handoffs E4-claims F1-skills F2F3-tools F4-plugins F5-layers FRESH-invalidation \
             G1G2-command-surface H1-lineage H2H3-readiness H4-scenarios-data-tests I1I2-tasks I3-generation I4-parallel; do
      s=$(date +%s); PROBES="$SCR/$F" bash "$p.sh" > "$p.out" 2>&1; echo "$p exit=$? $(( $(date +%s)-s ))s"
    done
    python3 DV-derived-views.py > DV-derived-views.out 2>&1; echo "DV exit=$?" ;;
  delta-r)
    PROBE_SCRATCH="$SCR/$F" bash "$EV/RUN-ALL.sh" ;;
  epsilon-r)
    cd "$CLONE" && bash "$EV/RUN-ALL.sh" "$SCR/$F" > "$SCR/$F.RUN-ALL.out" 2>&1; cat "$SCR/$F.RUN-ALL.out" ;;
  zeta-r)
    ZPROBE_SCRATCH="$SCR/$F" bash "$EV/run-all.sh" ;;
esac
echo "# family $F end $(date -u +%FT%TZ)"
