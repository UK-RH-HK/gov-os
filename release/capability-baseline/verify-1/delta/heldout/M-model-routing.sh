#!/usr/bin/env bash
# P2-AR-0049 held-out probe — Gate M (Contract v3:687-711)
#   M1 T0-T3 capability tiers: deterministic/no-LLM, lightweight, strong engineering, frontier
#   M2 a reasoning minimum can be declared and enforced
#   M3 orchestration/memory/audit default to a strong enough tier; provider names are mapped externally
#   M4 telemetry can compare model/provider, task class, reasoning effort, cost, latency, pass/fail, repair count,
#      reviewer findings
cd "$(dirname "$0")" && . ./lib.sh
machine mroute && seed_spec && seed_acceptance_test

echo "== M1  the four tiers exist as routing outcomes, not merely as policy text"
TIERS=""
for c in documentation implementation architecture; do
  TIERS="$TIERS $(ROLE=routine-documentation res route --class $c | python3 -c "import json,sys;print(json.load(sys.stdin)['minimum_tier'])")"
done
echo "   documentation/implementation/architecture at a low role ->$TIERS"
check "$(python3 -c "print(1 if '$TIERS'.split()==['T1','T2','T3'] else 0)")" "M1.1 lightweight (T1), strong-engineering (T2) and frontier (T3) are reachable routing outcomes" "$TIERS"
T0R="$(for c in $(python3 -c "
import yaml;print(' '.join(yaml.safe_load(open('$MROOT/governance/kernel/policies/MODEL_ROUTING_POLICY.yaml'))['task_class_minimum_tier']))"); do
  ROLE=routine-documentation res route --class "$c" | python3 -c "import json,sys;print(json.load(sys.stdin)['minimum_tier'])"; done | sort -u | tr '\n' ' ')"
echo "   every declared task class routes to one of: $T0R"
check "$(python3 -c "print(1 if 'T0' in '$T0R'.split() else 0)")" "M1.2 a deterministic / no-LLM (T0) route is reachable" "no task class routes to T0; reachable tiers were: $T0R"
# the deterministic surface the product does offer, exercised
INT="$(res intent 'show me the task dag' 2>/dev/null)"
echo "   NOTE gov intent (COMMAND_CONTRACT calls this the deterministic T0 routing surface): $(echo "$INT" | head -c 220)"

echo "== M1/M3  a project overlay may raise a floor, never lower it (POLICY_PRECEDENCE)"
python3 - "$MROOT" <<'PY'
import sys, yaml, os
p = os.path.join(sys.argv[1], "governance/project/MODEL_ROUTING_OVERRIDES.yaml")
d = yaml.safe_load(open(p)) or {}
d.setdefault("task_class_overrides", {})["security"] = "T1"          # a weakening: security is T3 in the kernel
d.setdefault("role_overrides", {})["orchestrator"] = {"default_reasoning": "low"}   # a weakening
d.setdefault("task_class_overrides", {})["documentation"] = "T3"     # a strengthening: allowed
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
g rebuild-memory --incremental >/dev/null 2>&1
SEC="$(res route --class security | python3 -c "import json,sys;print(json.load(sys.stdin)['minimum_tier'])")"
check_eq "$SEC" T3 "M1.3 an overlay that lowers the kernel tier floor for security does not take effect"
ORC="$(res route --class implementation | python3 -c "import json,sys;print(json.load(sys.stdin)['reasoning'])")"
check_eq "$ORC" high "M3.1 an overlay that lowers the orchestrator's reasoning default does not take effect"
DOC="$(ROLE=routine-documentation res route --class documentation | python3 -c "import json,sys;print(json.load(sys.stdin)['minimum_tier'])")"
check_eq "$DOC" T3 "M1.4 an overlay that raises a floor does take effect"
OV="$(res policy overrides 2>/dev/null)"
echo "   gov policy overrides: $(echo "$OV" | head -c 400)"
check "$(echo "$OV" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin));print(1 if 'security' in s and ('refus' in s.lower() or 'floor' in s.lower() or 'reject' in s.lower()) else 0)")" "M1.5 the refused weakening is reported, not silently ignored" "$(echo "$OV" | head -c 400)"

echo "== M2  a reasoning minimum can be declared on a task and is enforced upward"
TA="$(res task create --class documentation --objective "A task that declares an extra-high reasoning minimum" --status READY --allowed 'docs/**' --fields '{"role":"routine-documentation","minimum_reasoning":"extra_high","minimum_model_tier":"T3"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
RT="$(ROLE=routine-documentation res route --task "$TA" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['minimum_tier'],d['reasoning'])")"
echo "   routing for the declared task: $RT"
check_eq "$RT" "T3 extra_high" "M2.1 a declared minimum reasoning and tier are honoured"
TB="$(res task create --class documentation --objective "A task that declares a low reasoning minimum" --status READY --allowed 'docs/**' --fields '{"role":"orchestrator","minimum_reasoning":"low"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
RB="$(res route --task "$TB" | python3 -c "import json,sys;print(json.load(sys.stdin)['reasoning'])")"
check_eq "$RB" high "M2.2 a task cannot declare its way below its role's reasoning floor"

echo "== M3  provider names live only in the overlay; project state stays canonical"
CAND="$(res route --class implementation | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({'candidates':d['candidates'],'chosen':d['chosen'],'note':d.get('note')}))")"
echo "   candidates from the overlay: $(echo "$CAND" | head -c 300)"
python3 - "$MROOT" <<'PY'
import sys, yaml, os
p = os.path.join(sys.argv[1], "governance/project/MODEL_ROUTING_OVERRIDES.yaml")
d = yaml.safe_load(open(p)) or {}
d["providers"] = [{"name": "provider-alpha", "models": [
    {"id": "alpha-small", "tier": "T1", "max_reasoning": "medium", "cost_per_1k_in": 0.01, "cost_per_1k_out": 0.02},
    {"id": "alpha-large", "tier": "T3", "max_reasoning": "extra_high", "cost_per_1k_in": 0.5, "cost_per_1k_out": 1.0}]}]
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
g rebuild-memory --incremental >/dev/null 2>&1
CH="$(res route --class implementation | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d['chosen']))")"
echo "   chosen after mapping providers in the overlay: $CH"
check "$(echo "$CH" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d and d.get('provider')=='provider-alpha' else 0)")" "M3.2 provider/model names are mapped in the overlay and resolved by the router" "$CH"
GREP="$(grep -rl 'alpha-large' "$MROOT/spec" 2>/dev/null | head -3)"
check "$([ -z "$GREP" ] && echo 1 || echo 0)" "M3.3 mapping providers rewrites no project state (no provider name in spec/**)" "found in: $GREP"
for r in orchestrator memory-engineer independent-auditor; do
  TT="$(ROLE=$r res route --class implementation | python3 -c "import json,sys;print(json.load(sys.stdin)['minimum_tier'])")"
  check_eq "$TT" T3 "M3.4 the $r role defaults to a strong enough tier (T3)"
done

echo "== M4  telemetry can compare the eight dimensions"
REC() { # REC <model> <reasoning> <pass> <repairs> <findings> <cost> <latency>
  local f="$MROOT/.governance-runtime/route-$1-$2.json"
  python3 - "$f" "$@" <<'PY'
import json, sys
f, model, reasoning, passed, repairs, findings, cost, latency = sys.argv[1:9]
json.dump({"model": model, "provider": "provider-alpha", "task_class": "implementation",
           "reasoning_effort": reasoning, "cost": float(cost), "latency_ms": int(latency),
           "pass": passed == "true", "repair_count": int(repairs), "reviewer_findings": int(findings)}, open(f, "w"))
PY
  g route --record "$f" >/dev/null 2>&1
}
REC alpha-large extra_high true 0 0 0.90 4200
REC alpha-large low false 3 7 0.10 900
REC alpha-small medium true 1 2 0.05 500
RAW="$MROOT/.governance-runtime/routing/evidence.jsonl"
check "$([ -f "$RAW" ] && echo 1 || echo 0)" "M4.0 routing evidence is recorded"
for d in model provider task_class reasoning_effort cost latency_ms pass repair_count reviewer_findings; do
  check "$(python3 -c "print(1 if all('\"$d\"' in l for l in open('$RAW')) else 0)")" "M4.1 every recorded run carries '$d'" ""
done
MISS="$(code route --record "$(python3 -c "
import json;f='$MROOT/.governance-runtime/route-missing.json';json.dump({'model':'m','provider':'p','task_class':'implementation','cost':1.0,'latency_ms':1,'pass':True,'repair_count':0},open(f,'w'));print(f)")")"
check "$([ "$MISS" != OK ] && echo 1 || echo 0)" "M4.2 a run missing a declared evidence field is refused at record time" "returned $MISS"
REP="$(res route --report)"
echo "   gov route --report rows:"
echo "$REP" | python3 -c "import json,sys;[print('     ',json.dumps(r)) for r in json.load(sys.stdin)['rows']]"
COLS="$(echo "$REP" | python3 -c "import json,sys;r=json.load(sys.stdin)['rows'];print(','.join(sorted(r[0].keys())) if r else '')")"
echo "   report columns: $COLS"
for d in provider model task_class; do
  check "$(python3 -c "print(1 if '$d' in '$COLS'.split(',') else 0)")" "M4.3 the comparison can group by '$d'" "columns=$COLS"
done
for d in "pass_rate:pass/fail" "avg_cost:cost" "avg_latency_ms:latency" "avg_repairs:repair count"; do
  col="${d%%:*}"; name="${d#*:}"
  check "$(python3 -c "print(1 if '$col' in '$COLS'.split(',') else 0)")" "M4.4 the comparison reports $name" "columns=$COLS"
done
check "$(echo "$REP" | python3 -c "
import json,sys;rows=json.load(sys.stdin)['rows']
efforts={r.get('reasoning_effort') for r in rows}
print(1 if any('reasoning' in k for r in rows for k in r) or len(rows)>=4 else 0)")" "M4.5 the comparison can distinguish reasoning effort" "the report groups by provider|model|task_class only, so the two alpha-large runs at extra_high and low are merged into one row"
check "$(echo "$REP" | python3 -c "
import json,sys;rows=json.load(sys.stdin)['rows']
print(1 if any('reviewer' in k or 'finding' in k for r in rows for k in r) else 0)")" "M4.6 the comparison reports reviewer findings" "no reviewer-findings column in gov route --report"
TEL="$(res telemetry summary 2>/dev/null)"
MR="$(echo "$TEL" | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d.get('model_routing') or {}))")"
echo "   telemetry summary model_routing: $(echo "$MR" | head -c 500)"
check "$(echo "$MR" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin));print(1 if 'reasoning' in s and ('reviewer' in s or 'finding' in s) else 0)")" "M4.7 gov telemetry summary compares reasoning effort and reviewer findings" "$(echo "$MR" | head -c 400)"
echo "   NOTE the raw evidence keeps every dimension per run, so an offline comparison is possible:"
python3 -c "
import json
rows=[json.loads(l) for l in open('$RAW')]
print('     ', json.dumps(sorted({(r['model'], r['reasoning_effort'], r['pass'], r['reviewer_findings']) for r in rows})))"

summary
