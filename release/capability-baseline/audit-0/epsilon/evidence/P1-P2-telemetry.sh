#!/bin/bash
set -euo pipefail
GOV="$1"; ROOT="$2"
echo "=== P1: Execution telemetry ==="

echo "--- P1: Telemetry emit test ---"
$GOV telemetry emit --help --root "$ROOT" 2>&1
echo ""
echo "--- P1: Telemetry events after a few commands ---"
# Run a few commands to generate telemetry
$GOV status --root "$ROOT" --json >/dev/null 2>&1
$GOV doctor --root "$ROOT" --json >/dev/null 2>&1
$GOV audit --no-persist --root "$ROOT" --json >/dev/null 2>&1
echo ""
echo "--- P1: Telemetry events JSONL ---"
cat "$ROOT/.governance-runtime/telemetry/events.jsonl" 2>/dev/null | head -3
echo ""
echo "--- P1: Telemetry event fields ---"
cat "$ROOT/.governance-runtime/telemetry/events.jsonl" 2>/dev/null | head -1 | python3 -c "import json,sys; d=json.load(sys.stdin); print('event fields:', sorted(d.keys())); print('attributes:', sorted(d.get('attributes',{}).keys()))"
echo ""

echo "--- P2: Telemetry summary for organisational questions ---"
$GOV telemetry summary --root "$ROOT" --json 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print('summary keys:', sorted(d['result'].keys()))" 2>&1 || echo "could not parse"
echo ""
echo "--- P2: Full summary output ---"
$GOV telemetry summary --root "$ROOT" --json 2>&1 | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['result'], indent=2))" 2>&1 | head -60
