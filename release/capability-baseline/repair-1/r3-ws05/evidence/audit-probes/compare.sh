#!/usr/bin/env bash
# P2-AR-0036 — before/after lines of the probe re-runs in ./base-shim and ./after-shim (both through the evidence
# adapter; base = the round-3 base tree 53897c1 built in scratch, after = this branch). Prints only lines already in
# the outputs; judges nothing. Usage: compare.sh > COMPARE.out
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
hdr() { printf '\n==== %s ====\n' "$1"; }
both() { # <file> <grep -E pattern>
  for m in base-shim after-shim; do
    echo "-- $m (real gov $(sed -n 3p "$m/$1" | sed -n 's/.*real gov \([0-9a-f]\{12\}\).*/\1/p'))"
    grep -E "$2" "$m/$1" | cut -c1-330
  done
}
hdr "gamma-r I3-generation (BC-P2-24 accept: >=1 linked task per source)"
both gamma-r.I3-generation.out '^\s+\[I3\.b'
hdr "epsilon-r O5-scheduler-requirements S8 (BC-P2-24 accept)"
both epsilon-r.O5-scheduler-requirements.out 'task records before/after|generated_work|telemetry event names'
hdr "delta-r K3-auto-impact-simulation (BC-P2-13 accept: K3.b*.mislabel, K3.outside.*)"
both delta-r.K3-auto-impact-simulation.out 'CHECK K3\.(b[0-9]*\.mislabel|outside)'
hdr "gamma-r G1G2-command-surface G1.b3 (BC-P2-13 accept)"
both gamma-r.G1G2-command-surface.out '^\$ \(c\)|^exit=1 ok=false code=(MATERIAL|GOVERNANCE)|CIT records before/after'
hdr "gamma-r FRESH-invalidation (task closes that touch governance files)"
both gamma-r.FRESH-invalidation.out 'close TASK-GOV'
hdr "gamma-r H2H3-readiness (computed chain cells; silent N/A)"
both gamma-r.H2H3-readiness.out 'given "N/A"|invalid \(silent|pre_implementation_ok:'
hdr "gamma-r E4-claims unedited (claims store location; E4.b4 ages the lease in the OLD file)"
both gamma-r.E4-claims.out 'claim store:|claims live in|suite concurrency_claims|dry-run items|recover ok='
hdr "gamma-r E4-claims DERIVED (store path .governance-state/claims.db; after only — the base keeps the old location)"
grep -E 'claim store:|suite concurrency_claims|dry-run items|recover ok=|clone claims' after-shim/derived.E4-claims.state-dir.P2-AR-0036.out | cut -c1-330
hdr "zeta-r W03 unedited: observations that differ"
diff <(grep -E '^OBS' base-shim/zeta-r.W03-task-input-manifest.out | sed 's/ -- .*//') <(grep -E '^OBS' after-shim/zeta-r.W03-task-input-manifest.out | sed 's/ -- .*//')
hdr "zeta-r W03 DERIVED (explicit ids renamed): observations that differ (none expected)"
diff <(grep -E '^OBS' base-shim/derived.W03-task-input-manifest.ids.P2-AR-0036.out | sed 's/ -- .*//') <(grep -E '^OBS' after-shim/derived.W03-task-input-manifest.ids.P2-AR-0036.out | sed 's/ -- .*//') && echo "(identical)"
hdr "zeta-r W06 unedited: result"
for m in base-shim after-shim; do echo "-- $m: $(grep -cE '^OBS .*: PASS' $m/zeta-r.W06-staleness-propagation.out) PASS / $(grep -cE '^OBS .*: FAIL' $m/zeta-r.W06-staleness-propagation.out) FAIL; $(grep -m1 -E 'RuntimeError' $m/zeta-r.W06-staleness-propagation.out | cut -c1-260)"; done
hdr "zeta-r W06 DERIVED (chain cells N/A_WITH_REASON; B1 claim outcome recorded): observations"
diff <(grep -E '^OBS' base-shim/derived.W06-staleness-propagation.chain-na.P2-AR-0036.out | sed 's/ -- .*//') <(grep -E '^OBS' after-shim/derived.W06-staleness-propagation.chain-na.P2-AR-0036.out | sed 's/ -- .*//')
grep -E '^OBS DERIVED-W6-B1' after-shim/derived.W06-staleness-propagation.chain-na.P2-AR-0036.out | cut -c1-420
hdr "delta-r N1-N2-checkpoints (R2-6): marks and where each run stops"
for m in base-shim after-shim; do echo "-- $m: $(grep -cE '(^|\s)PASS(\s|:|$)' $m/delta-r.N1-N2-checkpoints.out) PASS; stops at: $(grep -m1 'unexpected failure' $m/delta-r.N1-N2-checkpoints.out | cut -c1-200)"; done
hdr "beta-r D6-rebuild-guarantee: where each run stops"
for m in base-shim after-shim; do echo "-- $m: $(grep -m1 'required command failed' $m/beta-r.D6-rebuild-guarantee.out | cut -c1-260)"; done
hdr "beta-r D6 DERIVED (claimed task not feature implementation; reranker override not applied): checks and B-deletion diff"
for m in base-shim after-shim; do echo "-- $m"; grep -E '^(PASS|FAIL)  D6|^\[B\] differences|another session claims the previously claimed' $m/derived.D6-rebuild-guarantee.refactor-claim.P2-AR-0036.out | cut -c1-300; done
