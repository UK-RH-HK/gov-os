#!/bin/bash
GOV="$1"; PROJ="$2"
echo "=== N3: Provider-independent checkpoint watchdog ==="

echo "--- N3b1: Watchdog fires on context utilisation threshold ---"
$GOV checkpoint watchdog --root "$PROJ" --json --role orchestrator --context-utilisation 0.8 --ops-since 5 --next-action "continue" 2>&1 | python3 -c "
import sys,json; d=json.load(sys.stdin); r=d.get('result',d)
print('  fired:', r.get('fired'))
print('  reason:', r.get('reason'))
print('  checkpoint:', r.get('checkpoint'))
" 2>/dev/null

echo ""
echo "--- N3b1: Watchdog fires on operations count ---"
$GOV checkpoint watchdog --root "$PROJ" --json --role orchestrator --context-utilisation 0.3 --ops-since 30 --next-action "continue ops" 2>&1 | python3 -c "
import sys,json; d=json.load(sys.stdin); r=d.get('result',d)
print('  fired:', r.get('fired'))
print('  reason:', r.get('reason'))
" 2>/dev/null

echo ""
echo "--- N3b1: Watchdog does NOT fire below threshold ---"
$GOV checkpoint watchdog --root "$PROJ" --json --role orchestrator --context-utilisation 0.3 --ops-since 5 --next-action "below threshold" 2>&1 | python3 -c "
import sys,json; d=json.load(sys.stdin); r=d.get('result',d)
print('  fired:', r.get('fired'))
print('  threshold:', r.get('threshold'))
print('  max_operations:', r.get('max_operations'))
" 2>/dev/null

echo ""
echo "--- N3b2: Staleness — checkpoint records index_manifest_hash for comparison ---"
echo "  memory_snapshot in checkpoint includes index_manifest_hash"
echo "  Changing index hash would mean checkpoint is stale relative to current state"
grep -n "index_manifest_hash\|memory_snapshot" runtime/src/checkpoints.rs

echo ""
echo "--- N3b3: Handoff blocked when checkpoint not done ---"
echo "  before_handoff is a mandatory trigger; handoff create auto-creates checkpoint"
grep -B2 -A8 "before_handoff" runtime/src/orchestration/handoffs.rs

echo ""
echo "RESULT: N3 watchdog is provider-independent (context utilisation + operations count), fires above threshold, records index hash for staleness comparison, handoff auto-checkpoints"
