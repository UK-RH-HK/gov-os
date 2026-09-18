#!/usr/bin/env bash
set -euo pipefail
GOV="$1"; PROJ="$2"

echo "=== E1-b1: L0-L5 executable ==="
# Test authority level parsing and role checking
"$GOV" --root "$PROJ" --json --role orchestrator status 2>&1 | head -5
echo "--- L0 role (independent-auditor) cannot create tasks ---"
"$GOV" --root "$PROJ" --json --role independent-auditor task create --class discovery --objective "test" 2>&1 || true
echo "--- L4 orchestrator can create tasks ---"
"$GOV" --root "$PROJ" --json --role orchestrator task create --class discovery --objective "E1 auth test" 2>&1 | head -5

echo "=== E1-b2: Role authority checked on every privileged path ==="
echo "--- L1 backend-engineer cannot answer gate ---"
"$GOV" --root "$PROJ" --json --role backend-engineer gate answer HDG-0001 --option A --by human 2>&1 || true

echo "=== E1-b3: Lower roles cannot manufacture higher-trust facts ==="
echo "--- L1 role cannot create handoff to orchestrator ---"
"$GOV" --root "$PROJ" --json --role backend-engineer handoff create --task TASK-0001 --to-role orchestrator 2>&1 || true

echo "=== E1-b4: Independent auditors constrained ==="
echo "--- L0 independent-auditor cannot create tasks ---"
"$GOV" --root "$PROJ" --json --role independent-auditor task create --class implementation --objective "unauthorized" 2>&1 || true
echo "--- L0 independent-auditor can read status ---"
"$GOV" --root "$PROJ" --json --role independent-auditor status 2>&1 | head -3
