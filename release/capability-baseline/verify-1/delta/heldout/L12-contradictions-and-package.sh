#!/usr/bin/env bash
# P2-AR-0049 held-out probe — Gate L1/L2 (Contract v3:656-672)
#   L1 deterministic precedence first; agent resolution only where allowed; human escalation for consequential
#      uncertainty; rationale/evidence recorded
#   L2 the Human Decision Gate package: question, why now, current state, options, impact, reversibility,
#      cost/rework, recommendation, confidence, exact permitted next actions
cd "$(dirname "$0")" && . ./lib.sh
machine lgate && seed_spec && seed_acceptance_test

echo "== L1.b1  deterministic precedence resolves first: a superseded record is not a contradiction"
mkdir -p "$MROOT/spec/decisions"
cat > "$MROOT/spec/decisions/D-0100.yaml" <<'YML'
id: D-0100
type: decision
title: Use postgres for the ledger store
status: SUPERSEDED
state_class: HISTORICAL
superseded_by: D-0101
chosen_option: postgres
decision_key: ledger-store
affects: [F-0001]
YML
cat > "$MROOT/spec/decisions/D-0101.yaml" <<'YML'
id: D-0101
type: decision
title: Use mysql for the ledger store
status: ACTIVE
state_class: AUTHORITATIVE
supersedes: [D-0100]
chosen_option: mysql
decision_key: ledger-store
affects: [F-0001]
YML
git -C "$MROOT" add -A >/dev/null 2>&1; git -C "$MROOT" commit -qm decisions >/dev/null 2>&1
g rebuild-memory --incremental >/dev/null 2>&1
T1="$(res task create --class implementation --objective "Wire the ledger store" --feature F-0001 --status READY --allowed 'src/**' --fields '{"requirements":["REQ-0001"],"scenarios":["SCN-0001"],"decisions":["D-0100","D-0101"],"role":"backend-engineer"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
MAN="$(res context manifest "$T1" 2>/dev/null)"
echo "   manifest delivery_state: $(echo "$MAN" | python3 -c "import json,sys;print(json.load(sys.stdin)['delivery_state'])")"
check "$(echo "$MAN" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin));print(1 if 'SUPERSEDED' in s and 'CONTRADICTION' not in s else 0)")" "L1.1 a superseded input is resolved by precedence, not raised as a contradiction" "$(echo "$MAN" | head -c 400)"

echo "== L1.b3  a contradiction precedence cannot resolve is detected, blocks, and escalates"
cat > "$MROOT/spec/decisions/D-0102.yaml" <<'YML'
id: D-0102
type: decision
title: Use postgres for the ledger store
status: ACTIVE
state_class: AUTHORITATIVE
chosen_option: postgres
decision_key: ledger-store
affects: [F-0001]
YML
git -C "$MROOT" add -A >/dev/null 2>&1; git -C "$MROOT" commit -qm conflict >/dev/null 2>&1
g rebuild-memory --incremental >/dev/null 2>&1
T2="$(res task create --class implementation --objective "Wire the ledger store, conflicted" --feature F-0001 --status READY --allowed 'src/**' --fields '{"requirements":["REQ-0001"],"scenarios":["SCN-0001"],"decisions":["D-0101","D-0102"],"role":"backend-engineer"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
MAN2="$(res context manifest "$T2" 2>/dev/null)"
echo "   manifest: $(echo "$MAN2" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['delivery_state'], json.dumps(d['contradictions'])[:300])")"
check "$(echo "$MAN2" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin));print(1 if 'CONTRADICT' in s.upper() else 0)")" "L1.2 two current, contradictory decisions are detected as a contradiction" "$(echo "$MAN2" | head -c 400)"
check "$(echo "$MAN2" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d['delivery_state']=='BLOCKED' and any(c.get('blocks') for c in d['contradictions']) else 0)")" "L1.3 the contradiction blocks the task's input manifest: both sides are never delivered as authority" "$(echo "$MAN2" | head -c 300)"
check_eq "$(ROLE=backend-engineer code task claim "$T2")" TASK_NOT_RUNNABLE "L1.4 a task whose inputs contradict cannot be claimed"
ROUTED="$(res context compile "$T2" 2>/dev/null | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin).get('contradiction_routing')))")"
echo "   routing at dispatch: $(echo "$ROUTED" | head -c 300)"
CG="$(res gate list 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);gs=d if isinstance(d,list) else d.get('gates',[]);print(json.dumps([x for x in gs if x.get('trigger')=='contradiction']))")"
echo "   contradiction gate(s): $(echo "$CG" | head -c 300)"
check "$(echo "$CG" | python3 -c "import json,sys;print(1 if json.load(sys.stdin) else 0)")" "L1.5 the contradiction is escalated to a Human Decision Gate" "$CG"

echo "== L1.b2/b4  agent resolution only where policy allows, on an assessment the resolver did not make alone"
GA="$(res gate create --question "Should the ledger cache be warmed on boot?" --fields '{"why_now":"the boot path is being finalised this week","current_state":"cold start takes 4s; no warm-up exists","options":[{"id":"A","description":"warm the cache on boot","authorises_blocked_work":true},{"id":"B","description":"leave the cold start","authorises_blocked_work":false}],"impact":"one module of the boot path","reversibility":"reversible: the warm-up is a single call that can be removed","cost_rework":"under an hour to remove","recommendation":"A","confidence":0.92,"trigger":"ux_direction","impact_radius":"R0"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
g gate present "$GA" >/dev/null
SELF="$(code decide "$GA" --option A --by orchestrator --rationale "low impact and reversible")"
echo "   the session that raised it resolving it itself -> $SELF"
check "$([ "$SELF" != OK ] && echo 1 || echo 0)" "L1.6 an agent may not resolve a gate on an assessment its own session declared" "decide returned $SELF"
OTHER="$(SESSION=other ROLE=change-controller code decide "$GA" --option A --by change-controller --rationale "low impact, reversible, high confidence; the boot path warm-up is a single call")"
echo "   another session resolving it within agent_resolvable_when -> $OTHER"
check_eq "$OTHER" OK "L1.7 another session's L3+ agent may resolve a low-impact, reversible, high-confidence gate"
DEC="$(res gate show "$GA" | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d))")"
check "$(echo "$DEC" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin));print(1 if 'single call' in s else 0)")" "L1.8 the resolution's rationale is recorded" "$(echo "$DEC" | head -c 300)"
NR="$(SESSION=other2 ROLE=change-controller code decide "$GA" --option A --by change-controller)"
echo "   (a second, rationale-less resolution attempt -> $NR)"

echo "== L1.b2  an unassessed or consequential gate is not agent-resolvable"
GU="$(res gate create --question "Should we drop the legacy ledger table?" --fields '{"why_now":"the migration window closes on Friday","current_state":"the legacy table still holds three years of rows","options":[{"id":"A","description":"drop the legacy table","authorises_blocked_work":true},{"id":"B","description":"keep it read-only","authorises_blocked_work":false}],"impact":"three years of historical ledger rows across every downstream report","reversibility":"irreversible: the rows cannot be reconstructed after the drop","cost_rework":"unrecoverable data loss if it is wrong","recommendation":"B","confidence":0.55,"trigger":"destructive_migration","impact_radius":"R4"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
g gate present "$GU" >/dev/null
AGENT="$(SESSION=other ROLE=change-controller code decide "$GU" --option A --by change-controller --rationale "it is fine")"
echo "   agent resolution of an irreversible R4 human-only gate -> $AGENT"
check "$([ "$AGENT" != OK ] && echo 1 || echo 0)" "L1.9 consequential/irreversible uncertainty is escalated to the human, not agent-resolved" "decide returned $AGENT"
check_eq "$(decide_human "$GU" B >/dev/null 2>&1; res gate show "$GU" | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d).count('human')>0)")" "True" "L1.10 the same gate is answerable through the owner-signed human channel"

echo "== L2  the decision package: every field is substantive, options are real, answers stay inside them"
BARE="$(emsg gate create --question "Do the thing?")"
echo "   a gate with only a question -> $(echo "$BARE" | python3 -c "import json,sys;print(json.load(sys.stdin).get('code'))")"
check "$(echo "$BARE" | python3 -c "import json,sys;print(1 if json.load(sys.stdin).get('code') else 0)")" "L2.1 a gate raised with only a question is refused"
for f in why_now current_state options impact reversibility cost_rework recommendation confidence; do
  FL="$(python3 - "$f" <<'PY'
import json, sys
d = {"why_now": "w", "current_state": "c",
     "options": [{"id": "A", "description": "do it", "authorises_blocked_work": True},
                 {"id": "B", "description": "do not", "authorises_blocked_work": False}],
     "impact": "i", "reversibility": "reversible: r", "cost_rework": "cr", "recommendation": "A", "confidence": 0.8,
     "trigger": "ux_direction", "impact_radius": "R0"}
d.pop(sys.argv[1]); print(json.dumps(d))
PY
)"
  C="$(code gate create --question "Probe for $f" --fields "$FL")"
  check "$([ "$C" != OK ] && echo 1 || echo 0)" "L2.2 a package missing '$f' is refused" "gate create returned $C"
done
for v in '""' '"not assessed"' '"tbd"'; do
  FL="$(python3 - "$v" <<'PY'
import json, sys
d = {"why_now": json.loads(sys.argv[1]), "current_state": "c",
     "options": [{"id": "A", "description": "do it", "authorises_blocked_work": True},
                 {"id": "B", "description": "do not", "authorises_blocked_work": False}],
     "impact": "i", "reversibility": "reversible: r", "cost_rework": "cr", "recommendation": "A", "confidence": 0.8,
     "trigger": "ux_direction", "impact_radius": "R0"}
print(json.dumps(d))
PY
)"
  C="$(code gate create --question "Probe for placeholder $v" --fields "$FL")"
  check "$([ "$C" != OK ] && echo 1 || echo 0)" "L2.3 a placeholder value ($v) is not substantive content" "gate create returned $C"
done
C="$(code gate create --question "No options" --fields '{"why_now":"w","current_state":"c","options":[],"impact":"i","reversibility":"reversible: r","cost_rework":"cr","recommendation":"A","confidence":0.8,"trigger":"ux_direction","impact_radius":"R0"}')"
check "$([ "$C" != OK ] && echo 1 || echo 0)" "L2.4 a gate with no options is refused" "gate create returned $C"

echo "== L2.b10  the permitted next actions are derived by the OS for this gate"
GP="$(res gate create --question "Adopt the batched ledger writer?" --fields '{"why_now":"the write path is being finalised","current_state":"writes are per-row today","options":[{"id":"A","description":"batch the writes","authorises_blocked_work":true},{"id":"B","description":"keep per-row writes","authorises_blocked_work":false}],"impact":"the ledger write path and its throughput budget","reversibility":"reversible: the batching layer can be removed in a day","cost_rework":"about a day","recommendation":"A","confidence":0.75,"trigger":"ux_direction","impact_radius":"R1"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
PN="$(res gate show "$GP" | python3 -c "import json,sys;d=json.load(sys.stdin);g=d.get('gate',d);print(json.dumps(g.get('permitted_next_actions')))")"
echo "   permitted_next_actions: $(echo "$PN" | head -c 400)"
check "$(echo "$PN" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin));print(1 if '$GP' in s and '<gate>' not in s else 0)")" "L2.5 the permitted next actions name this gate and carry no placeholder" "$PN"

echo "== L2  an answer outside the offered options is not a decision"
g gate present "$GP" >/dev/null
OUT="$(SESSION=other ROLE=change-controller code decide "$GP" --option Z --by change-controller --rationale "not an offered option")"
check "$([ "$OUT" != OK ] && echo 1 || echo 0)" "L2.6 an option the package does not offer is refused" "decide returned $OUT"
# an owner-signed answer for an option outside the package is refused too
PRES="$(g gate present "$GP")"
INST="$(echo "$PRES" | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['gate']['gate_instance'])")"
SHA="$(echo "$PRES" | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['gate']['package_sha256'])")"
AF="$SCRATCH/answers/$GP-Z.json"; mkdir -p "$(dirname "$AF")"
$HC answer "$AF" --gate "$GP" --instance "$INST" --package-sha "$SHA" --option Z
OUT2="$(code decide "$GP" --option Z --answer-file "$AF")"
check "$([ "$OUT2" != OK ] && echo 1 || echo 0)" "L2.7 even an owner-signed answer naming an option outside the package is refused" "decide returned $OUT2"

echo "== L2  a system-raised gate carries a complete package too"
SYS="$(res gate list 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin); gs=d if isinstance(d,list) else d.get('gates',[])
c=[x for x in gs if x.get('trigger')=='contradiction']
print(c[0]['id'] if c else '')")"
if [ -n "$SYS" ]; then
  SP="$(res gate show "$SYS" | python3 -c "
import json,sys
d=json.load(sys.stdin); g=d.get('gate',d)
bad=[f for f in ('why_now','current_state','options','impact','reversibility','cost_rework','recommendation','confidence','permitted_next_actions')
     if not g.get(f) or str(g.get(f)).strip().lower() in ('','not assessed','tbd','[]')]
print(json.dumps({'gate':g.get('id'),'missing_or_placeholder':bad,'options':[o.get('id') for o in (g.get('options') or [])]}))")"
  echo "   system-raised gate package: $SP"
  check "$(echo "$SP" | python3 -c "import json,sys;print(1 if not json.load(sys.stdin)['missing_or_placeholder'] else 0)")" "L2.8 a system-raised gate's package is complete and substantive" "$SP"
else
  bad "L2.8 a system-raised gate's package is complete and substantive  -- no system-raised gate was found to inspect"
fi

summary
