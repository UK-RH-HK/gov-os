#!/usr/bin/env bash
# Implementer evidence collection. Every row carries one of PASS | FAIL | NOT_AVAILABLE | NOT_RUN | NOT_APPLICABLE.
# An unavailable tool is NOT_AVAILABLE (never counted as a pass), a tool present but not executed is NOT_RUN, and a
# check that does not apply is NOT_APPLICABLE with the reason (verifier M15 / directive §11).
#
# P2-PERF-0001 / R7 (2026-09-22): a test command that produced no `test result` line used to report NOT_RUN, so a
# suite that failed to compile, was killed, or aborted before libtest printed its summary read as "present but not
# executed" rather than red. A reader scanning for FAIL saw none. Every test row now derives from BOTH the summary
# line AND the command's own exit status (`${PIPESTATUS[0]}`, which is why `pipefail` is set), and anything other
# than an `ok` line with a zero exit is FAIL. NOT_RUN now means only what the header says it means: a deliberate
# decision not to run. Proven with an intentionally failing test before being relied on.
set -u
set -o pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/.cargo/bin:$PATH"
EV="$ROOT/release/evidence"; mkdir -p "$EV"
cd "$ROOT"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"; COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
{ echo "toolchain:"; rustc --version; cargo --version; python3 --version 2>&1; git --version; } > "$EV/toolchain.txt"
tool_status() { # name, probe command...
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "$name: available"; else echo "$name: NOT_AVAILABLE"; fi
}
{ tool_status clippy cargo clippy --version; tool_status rustfmt cargo fmt --version; tool_status python3 python3 --version; tool_status pytest python3 -c "import pytest"; } > "$EV/tool-status.txt"
cargo build --release 2>&1 | tail -3 > "$EV/build.txt"; BUILD_RC=${PIPESTATUS[0]}
status_of_test_result() { # summary line, command exit status -> PASS/FAIL with counts. Fails closed on both.
  local line="$1"; local rc="${2:-1}"
  if [ "$rc" -ne 0 ]; then
    if [ -z "$line" ]; then echo "FAIL (exit $rc, and no 'test result' line: the suite did not run to completion)"
    else echo "FAIL (exit $rc) ($line)"; fi
  elif [ -z "$line" ]; then echo "FAIL (exit 0 but no 'test result' line: nothing proves the suite ran)"
  elif echo "$line" | grep -q "^test result: ok"; then echo "PASS ($(echo "$line" | sed -E 's/^test result: ok\. //; s/; 0 ignored.*//'))"
  else echo "FAIL ($line)"; fi; }
cargo test -p gov-runtime 2>&1 | tee "$EV/unit-tests.txt" | grep -E "^test result" | head -1 > "$EV/unit-summary.raw"
UNIT_RC=${PIPESTATUS[0]}
status_of_test_result "$(cat "$EV/unit-summary.raw")" "$UNIT_RC" > "$EV/unit-summary.txt"
cargo test -p gov-cli --test certification -- --test-threads=4 2>&1 | tee "$EV/certification-tests.txt" | grep -E "^test result" | tail -1 > "$EV/certification-summary.raw"
CERT_RC=${PIPESTATUS[0]}
status_of_test_result "$(cat "$EV/certification-summary.raw")" "$CERT_RC" > "$EV/certification-summary.txt"
if python3 -c "import pytest" >/dev/null 2>&1; then
  ( cd capabilities/python && PYTHONPATH=. python3 -m pytest -q ../tests 2>&1 ) | tee "$EV/python-plugin-tests.txt" | tail -1 > "$EV/python-summary.raw"
  if grep -qE "^[0-9]+ passed" "$EV/python-summary.raw" && ! grep -qE "failed|error" "$EV/python-summary.raw"; then echo "PASS ($(cat "$EV/python-summary.raw"))" > "$EV/python-summary.txt"; else echo "FAIL ($(cat "$EV/python-summary.raw"))" > "$EV/python-summary.txt"; fi
else echo "NOT_AVAILABLE (pytest not installed)" > "$EV/python-summary.txt"; fi
if cargo clippy --version >/dev/null 2>&1; then
  cargo clippy --workspace --all-targets 2> "$EV/clippy.txt" >/dev/null; CLIPPY_RC=$?
  W=$(grep -cE "^warning: " "$EV/clippy.txt" || true); E=$(grep -cE "^error(\[|:)" "$EV/clippy.txt" || true)
  if [ "$CLIPPY_RC" -eq 0 ] && [ "$E" -eq 0 ]; then echo "PASS (exit 0, warnings=$W, errors=0; warning lines include per-crate summaries)" > "$EV/clippy-summary.txt"; else echo "FAIL (exit $CLIPPY_RC, warnings=$W, errors=$E)" > "$EV/clippy-summary.txt"; fi
else echo "NOT_AVAILABLE (cargo-clippy not installed)" > "$EV/clippy-summary.txt"; fi
if cargo fmt --version >/dev/null 2>&1; then
  if cargo fmt --all -- --check > "$EV/rustfmt.txt" 2>&1; then echo "PASS (rustfmt --check: formatted)" > "$EV/rustfmt-summary.txt"; else echo "FAIL (rustfmt --check reports $(grep -c '^Diff in' "$EV/rustfmt.txt") differences; see rustfmt.txt)" > "$EV/rustfmt-summary.txt"; fi
else echo "NOT_AVAILABLE (rustfmt not installed)" > "$EV/rustfmt-summary.txt"; fi
rm -f "$EV/clippy-diagnostic-count.txt" "$EV/unit-summary.raw" "$EV/certification-summary.raw" "$EV/python-summary.raw"
HELD="$EV/heldout-rerun-summary.txt"; if [ -f "$ROOT/release/verification/4.1.2/heldout-rerun-4.1.5/summary.txt" ]; then cp "$ROOT/release/verification/4.1.2/heldout-rerun-4.1.5/summary.txt" "$HELD"; else echo "NOT_RUN (first verifier harness not rerun in this collection)" > "$HELD"; fi
HELD2="$EV/heldout-v2-rerun-summary.txt"; if [ -f "$ROOT/release/verification/4.1.3/heldout-new-rerun-4.1.5/summary.txt" ]; then cp "$ROOT/release/verification/4.1.3/heldout-new-rerun-4.1.5/summary.txt" "$HELD2"; else echo "NOT_RUN (second verifier harness not rerun in this collection)" > "$HELD2"; fi
HELD3="$EV/heldout-v3-rerun-summary.txt"; if [ -f "$ROOT/release/verification/4.1.4/heldout-v3-rerun-4.1.5/summary.txt" ]; then cp "$ROOT/release/verification/4.1.4/heldout-v3-rerun-4.1.5/summary.txt" "$HELD3"; else echo "NOT_RUN (third verifier harness not rerun in this collection)" > "$HELD3"; fi
UNIT="$(cat "$EV/unit-summary.txt")"; CERT="$(cat "$EV/certification-summary.txt")"; PY="$(cat "$EV/python-summary.txt")"; CL="$(cat "$EV/clippy-summary.txt")"; FM="$(cat "$EV/rustfmt-summary.txt")"
CERT_LIST="$(grep -E '^test .* \.\.\. (ok|FAILED)$' "$EV/certification-tests.txt" | sed 's/^test /- /')"
UNIT_LIST="$(grep -E '^test .* \.\.\. (ok|FAILED)$' "$EV/unit-tests.txt" | sed 's/^test /- /')"
cat > "$ROOT/docs/EVIDENCE.md" <<MD
# Implementer test evidence — agentic-engineering-os $(grep -E '^version:' framework/KERNEL.yaml | awk '{print $2}') (repair candidate)

Collected: $STAMP · commit: $COMMIT · script: \`scripts/collect_evidence.sh\` · raw outputs: \`release/evidence/\`

> Implementer evidence only. Certification remains pending independent re-verification.
> Status vocabulary: PASS | FAIL | NOT_AVAILABLE (tool missing) | NOT_RUN (not executed) | NOT_APPLICABLE (with reason).
> An unavailable tool is never counted as evidence.

## Toolchain and tool status
\`\`\`
$(cat "$EV/toolchain.txt")
$(cat "$EV/tool-status.txt")
\`\`\`

## Results
| Suite | Result |
|---|---|
| Rust unit tests (gov-runtime) | $UNIT |
| Certification harness (7 fixtures + architectural + repair regressions for the 4.1.2, 4.1.3 and 4.1.4 findings) | $CERT |
| Python capability plugin tests | $PY |
| Clippy (\`cargo clippy --all-targets\`) | $CL |
| rustfmt (\`cargo fmt --check\`) | $FM |
| Release build (\`cargo build --release\`) | $( [ "$BUILD_RC" -eq 0 ] && echo "PASS (exit 0)" || echo "FAIL (exit $BUILD_RC)" ) |
| First independent held-out harness rerun (unchanged, 4.1.2 verifier) | $(cat "$HELD") |
| Second independent held-out harness rerun (unchanged, 4.1.3 verifier) | $(cat "$HELD2") |
| Third independent held-out harness rerun (unchanged, 4.1.4 verifier) | $(cat "$HELD3") |

## Certification tests
$CERT_LIST

## Unit tests
$UNIT_LIST
MD
echo "evidence written: docs/EVIDENCE.md ($UNIT | $CERT | $PY | clippy: $CL)"
