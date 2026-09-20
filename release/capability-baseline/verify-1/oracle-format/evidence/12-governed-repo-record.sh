#!/usr/bin/env bash
# P2-AR-0045 — iteration-0 A0-V1-01 said "a fault-manifest record lacking every V1 field is accepted".
# Plant exactly that record in a governed repository and run the governance suite.
# Usage: 12-governed-repo-record.sh <initialised project root>   (run from the Governance OS repository root)
set -u
GOV="$PWD/target/release/gov"
FMT="$PWD/release/capability-baseline/verify-1/oracle-format/evidence/_auditfmt.py"
P="$1"
cat > "$P/spec/reports/FM-0001-fault-manifest.md" <<'R'
---
id: FM-0001
type: fault-manifest
title: injected defect catalogue
status: CURRENT
---

Nothing here names a single V1 field.
R
echo "--- with the bare fault-manifest record present ---"
(cd "$P" && "$GOV" --json --role orchestrator audit 2>&1) | python3 "$FMT"
mv "$P/spec/reports/FM-0001-fault-manifest.md" "$P/../moved-aside-FM-0001-fault-manifest.md"
echo "--- after moving it aside (rm is denied in this environment) ---"
(cd "$P" && "$GOV" --json --role orchestrator audit 2>&1) | python3 "$FMT"
