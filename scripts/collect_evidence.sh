#!/usr/bin/env bash
# Implementer evidence collection: builds the release binary, runs unit + certification suites and the Python
# plugin tests, and records raw outputs under release/evidence/ plus a summary in docs/EVIDENCE.md.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/.cargo/bin:$PATH"
EV="$ROOT/release/evidence"; mkdir -p "$EV"
cd "$ROOT"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
{ echo "toolchain:"; rustc --version; cargo --version; python3 --version 2>&1; git --version; } > "$EV/toolchain.txt"
cargo build --release 2>&1 | tail -3 > "$EV/build.txt"; BUILD_RC=${PIPESTATUS[0]}
cargo test -p gov-runtime 2>&1 | tee "$EV/unit-tests.txt" | grep -E "^test result" | head -1 > "$EV/unit-summary.txt"
cargo test -p gov-cli --test certification -- --test-threads=4 2>&1 | tee "$EV/certification-tests.txt" | grep -E "^test result" | tail -1 > "$EV/certification-summary.txt"
( cd capabilities/python && PYTHONPATH=. python3 -m pytest -q ../tests 2>&1 ) | tee "$EV/python-plugin-tests.txt" | tail -1 > "$EV/python-summary.txt"
cargo clippy --all-targets -q 2>&1 | grep -cE "^(warning|error)" > "$EV/clippy-diagnostic-count.txt" || true
UNIT="$(cat "$EV/unit-summary.txt")"; CERT="$(cat "$EV/certification-summary.txt")"; PY="$(cat "$EV/python-summary.txt")"
CERT_LIST="$(grep -E '^test .* \.\.\. (ok|FAILED)$' "$EV/certification-tests.txt" | sed 's/^test /- /' )"
UNIT_LIST="$(grep -E '^test .* \.\.\. (ok|FAILED)$' "$EV/unit-tests.txt" | sed 's/^test /- /' )"
cat > "$ROOT/docs/EVIDENCE.md" <<MD
# Implementer test evidence — agentic-engineering-os 4.1.2 (release candidate)

Collected: $STAMP · commit: $COMMIT · script: \`scripts/collect_evidence.sh\` · raw outputs: \`release/evidence/\`

> This is **implementer** evidence. It does not certify the release. Status remains
> READY_FOR_INDEPENDENT_OS_VERIFICATION until an independent verifier records a verdict.

## Toolchain
\`\`\`
$(cat "$EV/toolchain.txt")
\`\`\`

## Results
| Suite | Result |
|---|---|
| Rust unit tests (gov-runtime) | $UNIT |
| Certification harness (7 fixtures + architectural tests) | $CERT |
| Python capability plugin tests | $PY |
| Release build (\`cargo build --release\`) | exit $BUILD_RC |

## Certification tests
$CERT_LIST

## Unit tests
$UNIT_LIST

## What each certification test proves
See [docs/FIXTURES.md](FIXTURES.md) and the fixture READMEs under \`fixtures/\`.
MD
echo "evidence written: docs/EVIDENCE.md ($UNIT | $CERT | $PY)"
