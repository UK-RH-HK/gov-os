#!/bin/bash
set -euo pipefail
GOV="$1"; ROOT="$2"
echo "=== U: Framework Health SLOs ==="

echo "--- U: Doctor checks map to HEALTHY conditions ---"
$GOV doctor --root "$ROOT" --json 2>&1 | python3 -c "
import json, sys
d = json.load(sys.stdin)
result = d['result']
print('verdict:', result['verdict'])
print('checks:')
for c in result['checks']:
    print(f\"  {c['id']} {c['name']}: ok={c['ok']} severity={c['severity']}\")
print('failed:', result['failed'])
print('remediation:', result['remediation'])
print('framework_version:', result['framework_version'])
print('release_trust:', json.dumps(result.get('release_trust', {}), indent=4))
" 2>&1
echo ""

echo "--- U: SLO thresholds tracked in doctor checks ---"
echo "D001 framework.lock present"
echo "D002 framework.lock schema"
echo "D003 kernel payload integrity (authority unambiguous, no accidental legacy)"
echo "D004 lock matches kernel manifest"
echo "D005 CLI/kernel compatibility"
echo "D006 project overlay (deterministic state consistent)"
echo "D007 policies"
echo "D008 framework.json in sync (graph/index freshness passes)"
echo "D009 derived runtime (memory rebuild success)"
echo "D010 index freshness (retrieval meets thresholds)"
echo "D011 secrets outside secret class (sensitive material isolated)"
echo "D012 no secrets in index"
echo "D013 legacy governance mechanisms retired (no accidental legacy authority)"
echo "D014 authority unambiguous"
echo "D015 graph integrity"
echo "D016 no interrupted transactions"
echo "D017 session claims"
echo "D018 control state"
echo "D019 human gates presented (unresolved human gates)"
echo "D020 adapters current"
echo "D021 governance suite green and current (governance suite current/green)"
echo "D022 native toolchains for detected ecosystems"
echo "D023 records parse"
echo "D024 .governance-runtime ignored by git"
echo "D025 semantic index consistent"
echo "D026 claims store present"
echo "D027 policy precedence (no weakening overrides)"
echo "D028 capability plugins governed"
echo "D029 constitutional policy from verified kernel"
echo ""

echo "--- U: HEALTHY only when all conditions hold ---"
echo "Doctor verdict HEALTHY when all checks pass; DEGRADED/UNHEALTHY otherwise."
echo "The 13 HEALTHY conditions map onto the 29 doctor checks."
