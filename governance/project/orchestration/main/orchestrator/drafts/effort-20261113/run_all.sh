#!/usr/bin/env bash
# Re-run the whole measurement. Read-only on the repository and logs; writes only into this folder. No pytest.
set -eu
D=$(cd "$(dirname "$0")" && pwd)
ORCH=$(cd "$D/../.." && pwd)
export EFFORT_NOW=${EFFORT_NOW:-$(( $(date -u +%s) / 60 * 60 ))}
NOWISO=$(date -u -d "@$EFFORT_NOW" +%Y-%m-%dT%H:%M)
python3 -I "$ORCH/tools/lead_ledger.py" --since 2026-11-11T13:31 --now "$NOWISO" --out "$D/lead-ledger-window.jsonl" >/dev/null
cd "$D"
python3 -I build.py --W 30 && python3 -I aggregate.py units.jsonl
python3 -I build.py --W 15 >/dev/null && python3 -I aggregate.py units-W15.jsonl >/dev/null
python3 -I build.py --W 60 >/dev/null && python3 -I aggregate.py units-W60.jsonl >/dev/null
python3 -I build.py --W 30 >/dev/null   # leave build-meta for the default
echo "now=$NOWISO"
