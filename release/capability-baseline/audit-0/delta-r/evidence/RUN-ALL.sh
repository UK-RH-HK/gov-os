#!/usr/bin/env bash
# P2-AR-0011 (family delta re-audit): re-run every independent probe against the worktree's release binary.
# Prerequisites: `~/.cargo/bin/cargo build --release` in the worktree root; python3 with PyYAML; git.
# Each probe creates disposable projects under $PROBE_SCRATCH (default: $TMPDIR/p2-ar-0011-probes) with an isolated
# XDG_STATE_HOME, so the operator's protected machine state is never read or written.
# Output lines: "$ gov ..." (exact command), "CHECK <id> PASS|FAIL <statement>", "OBSERVE <id> ...", "SUMMARY ...".
set -u
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
for probe in DERIVED-VIEWS-JKLMN J1-J2-research-experiments K1-cit-p K2-cit-e K3-auto-impact-simulation K4-impact-radius \
             L1-contradiction-resolution L2-decision-package L3-gate-presentation-attacks L3-supplement L4-non-global-blocking \
             M1-M3-routing M4-empirical-routing N1-N2-checkpoints N2-significant-mutation-adopt N3-N4-W9-watchdog-handoff \
             FRESH-invalidation; do
  echo "== $probe"
  python3 "$probe.py" > "$probe.out" 2>&1
  grep '^SUMMARY' "$probe.out"
done
# regression (builder tests are regression evidence only, Contract v3 O3)
( cd ../../../../.. && ~/.cargo/bin/cargo test --lib 2>&1 | tail -40 ) > REG-cargo-test-lib.out
( cd ../../../../.. && ~/.cargo/bin/cargo test --test certification 2>&1 | grep -E '^test |test result|running|FAILED|panicked' ) > REG-cargo-test-certification.out
