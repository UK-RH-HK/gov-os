#!/usr/bin/env bash
# Implementer evidence collection. Tool availability is recorded explicitly: an unavailable tool is reported as NOT_RUN
# and never counted as a passing or failing result (verifier M15).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/.cargo/bin:$PATH"
EV="$ROOT/release/evidence"; mkdir -p "$EV"
cd "$ROOT"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"; COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
{ echo "toolchain:"; rustc --version; cargo --version; python3 --version 2>&1; git --version; } > "$EV/toolchain.txt"
tool_status() { # name, probe command...
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "$name: available"; else echo "$name: NOT_INSTALLED"; fi
}
{ tool_status clippy cargo clippy --version; tool_status rustfmt cargo fmt --version; tool_status python3 python3 --version; tool_status pytest python3 -c "import pytest"; } > "$EV/tool-status.txt"
cargo build --release 2>&1 | tail -3 > "$EV/build.txt"; BUILD_RC=${PIPESTATUS[0]}
cargo test -p gov-runtime 2>&1 | tee "$EV/unit-tests.txt" | grep -E "^test result" | head -1 > "$EV/unit-summary.txt"
cargo test -p gov-cli --test certification -- --test-threads=4 2>&1 | tee "$EV/certification-tests.txt" | grep -E "^test result" | tail -1 > "$EV/certification-summary.txt"
if python3 -c "import pytest" >/dev/null 2>&1; then ( cd capabilities/python && PYTHONPATH=. python3 -m pytest -q ../tests 2>&1 ) | tee "$EV/python-plugin-tests.txt" | tail -1 > "$EV/python-summary.txt"; else echo "NOT_RUN (pytest not installed)" > "$EV/python-summary.txt"; fi
if cargo clippy --version >/dev/null 2>&1; then
  cargo clippy --all-targets 2> "$EV/clippy.txt" >/dev/null; CLIPPY_RC=$?
  W=$(grep -cE "^warning: " "$EV/clippy.txt" || true); E=$(grep -cE "^error(\[|:)" "$EV/clippy.txt" || true)
  echo "RAN exit=$CLIPPY_RC warnings=$W errors=$E" > "$EV/clippy-summary.txt"
else echo "NOT_RUN (cargo-clippy not installed)" > "$EV/clippy-summary.txt"; fi
if cargo fmt --version >/dev/null 2>&1; then
  if cargo fmt --all -- --check > "$EV/rustfmt.txt" 2>&1; then echo "RAN formatted=yes" > "$EV/rustfmt-summary.txt"; else echo "RAN formatted=no (diff in rustfmt.txt; formatting is advisory in this release)" > "$EV/rustfmt-summary.txt"; fi
else echo "NOT_RUN (rustfmt not installed)" > "$EV/rustfmt-summary.txt"; fi
rm -f "$EV/clippy-diagnostic-count.txt"
HELD="$EV/heldout-rerun-summary.txt"; [ -f "$ROOT/release/verification/4.1.2/heldout-rerun/summary.txt" ] && cp "$ROOT/release/verification/4.1.2/heldout-rerun/summary.txt" "$HELD" || echo "not run in this collection" > "$HELD"
UNIT="$(cat "$EV/unit-summary.txt")"; CERT="$(cat "$EV/certification-summary.txt")"; PY="$(cat "$EV/python-summary.txt")"; CL="$(cat "$EV/clippy-summary.txt")"; FM="$(cat "$EV/rustfmt-summary.txt")"
CERT_LIST="$(grep -E '^test .* \.\.\. (ok|FAILED)$' "$EV/certification-tests.txt" | sed 's/^test /- /')"
UNIT_LIST="$(grep -E '^test .* \.\.\. (ok|FAILED)$' "$EV/unit-tests.txt" | sed 's/^test /- /')"
cat > "$ROOT/docs/EVIDENCE.md" <<MD
# Implementer test evidence — agentic-engineering-os $(grep -E '^version:' framework/KERNEL.yaml | awk '{print $2}') (repair candidate)

Collected: $STAMP · commit: $COMMIT · script: \`scripts/collect_evidence.sh\` · raw outputs: \`release/evidence/\`

> Implementer evidence only. Certification remains pending independent re-verification.
> Unavailable tools are reported as NOT_RUN and are never counted as evidence.

## Toolchain and tool status
\`\`\`
$(cat "$EV/toolchain.txt")
$(cat "$EV/tool-status.txt")
\`\`\`

## Results
| Suite | Result |
|---|---|
| Rust unit tests (gov-runtime) | $UNIT |
| Certification harness (7 fixtures + architectural + repair regressions) | $CERT |
| Python capability plugin tests | $PY |
| Clippy (\`cargo clippy --all-targets\`) | $CL |
| rustfmt (\`cargo fmt --check\`) | $FM |
| Release build (\`cargo build --release\`) | exit $BUILD_RC |
| Independent held-out harness rerun (unchanged, 4.1.2 verifier) | $(cat "$HELD") |

## Certification tests
$CERT_LIST

## Unit tests
$UNIT_LIST
MD
echo "evidence written: docs/EVIDENCE.md ($UNIT | $CERT | $PY | clippy: $CL)"
