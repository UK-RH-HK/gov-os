#!/usr/bin/env bash
# P2-AR-0049 held-out probe — Gate K, CIT-P and CIT-E end to end (Contract v3:622-636)
#   K1 deterministic traversal, semantic/lexical candidates, impact radius, human-readable consequences
#   K2 final decision, mutation manifest, authoritative updates, staleness/retest/rework propagation,
#      derived-view regeneration, memory/index refresh, verification, commit-or-rollback atomically
# Also delta's iteration-1 duties: sealed CIT state; a CIT declined inside another task's claim window.
cd "$(dirname "$0")" && . ./lib.sh
machine kcit && seed_spec && seed_acceptance_test

# --- a DONE implementation task against REQ-0001, so propagation has completed work to reach (K2 <-> W6)
IMPL="$(res task create --class implementation --objective "Implement ledger totals" --feature F-0001 --status READY --allowed 'src/**' --fields '{"requirements":["REQ-0001"],"scenarios":["SCN-0001"],"acceptance_tests":["TST-0001"],"role":"backend-engineer"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
SESSION=impl ROLE=backend-engineer g task claim "$IMPL" >/dev/null
echo 'pub fn total_cents(v: &[(i64,i64)]) -> i64 { v.iter().map(|(q,c)| q*c).sum() }  // implemented' > "$MROOT/src/lib.rs"
PKT="$(SESSION=impl ROLE=backend-engineer res context compile "$IMPL" | python3 -c "import json,sys;print(json.load(sys.stdin)['packet_hash'])")"
CKPT="$(res checkpoint create --next-action "continue after the implementation" --task "$IMPL" 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('id',''))")"
R="$(SESSION=impl ROLE=backend-engineer receipt "$IMPL" impl-close "implemented ledger totals" "src/lib.rs" not_applicable_with_reason "$NA_TESTS")"
check_eq "$(SESSION=impl ROLE=backend-engineer code task close "$IMPL" --report "$R")" OK "K2.0 baseline: an implementation task closes DONE against REQ-0001"
g rebuild-memory --incremental >/dev/null 2>&1

echo "== K1  a proposed material change is traversed deterministically"
cat > "$MROOT/.governance-runtime/mf-req.json" <<'JSON'
[{"op":"set_field","target":"REQ-0001","field":"acceptance_criteria","value":["total_cents sums quantity*unit_cents and rejects negative quantities"]}]
JSON
CIT="$(res cit propose --proposal "tighten the ledger acceptance criterion" --trigger editorial --title "ledger criterion" --manifest "$MROOT/.governance-runtime/mf-req.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
IMP="$(res cit show "$CIT" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin)['impact']))")"
echo "   radius=$(echo "$IMP" | python3 -c "import json,sys;print(json.load(sys.stdin)['radius'])") affected=$(echo "$IMP" | python3 -c "import json,sys;print(json.load(sys.stdin)['affected'])")"
check "$(echo "$IMP" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d['seeds']==['REQ-0001'] and d['affected'] else 0)")" "K1.1 the manifest's targets seed a graph traversal that reaches linked artefacts" "$IMP"
check "$(echo "$IMP" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d.get('completed_tasks_to_revalidate') else 0)")" "K1.2 the traversal reaches the completed task that implemented the seed" "$IMP"
check "$(echo "$IMP" | python3 -c "import json,sys;d=json.load(sys.stdin);c=d.get('semantic_candidates') or [];print(1 if c and all(x.get('routes') for x in c) else 0)")" "K1.3 semantic/lexical candidates supplement the deterministic set, each with its route" ""
check "$(echo "$IMP" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d['radius'] in ('R0','R1','R2','R3','R4','R5') else 0)")" "K1.4 an impact radius is produced"
check "$(echo "$IMP" | python3 -c "import json,sys;d=json.load(sys.stdin);c=d['consequences'];print(1 if len(c)>=5 and any('retest' in x for x in c) and any('rollback' in x for x in c) else 0)")" "K1.5 human-readable consequences are surfaced"
# determinism: re-simulating the same manifest over unchanged state gives the same impact digest
S1="$(res cit show "$CIT" | python3 -c "import json,sys;print(json.load(sys.stdin)['os_state']['impact_sha256'])")"
g cit simulate "$CIT" >/dev/null
S2="$(res cit show "$CIT" | python3 -c "import json,sys;print(json.load(sys.stdin)['os_state']['impact_sha256'])")"
check_eq "$S1" "$S2" "K1.6 re-simulating the same manifest over unchanged state is deterministic (same impact digest)"

echo "== delta duty: CIT state is sealed (T2), and a hand-edited CIT is not honoured"
check_eq "$(res cit show "$CIT" | python3 -c "import json,sys;print(json.load(sys.stdin)['os_state']['os_binding']['alg'])")" "hmac-sha256/t2-v2" "K2.1 CIT state carries an OS seal"
cp "$MROOT/spec/decisions/$CIT.yaml" "$SCRATCH/$CIT.orig.yaml" 2>/dev/null || cp "$(g cit show "$CIT" >/dev/null; find "$MROOT/spec" -name "$CIT.yaml")" "$SCRATCH/$CIT.orig.yaml"
CITF="$(find "$MROOT/spec" -name "$CIT.yaml" | head -1)"
python3 - "$CITF" <<'PY'
import sys, yaml
p = sys.argv[1]; d = yaml.safe_load(open(p))
d["cit_status"] = "APPROVED"                      # a hand-written approval
d["os_state"]["cit_status"] = "APPROVED"
d["os_state"]["human_gate"] = None
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
FORGED="$(code cit execute "$CIT")"
echo "   hand-edited CIT execute -> $FORGED"
check_eq "$FORGED" T2_UNBOUND "K2.2 a hand-edited CIT record is refused: its OS seal no longer verifies"
AUD="$(g audit 2>&1 | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps((d['error']['details'] if not d.get('ok') else d['result']).get('findings',[])))")"
check "$(echo "$AUD" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if any(f.get('family')=='os_binding_integrity' and f.get('severity')=='high' and '$CIT' in f.get('message','') for f in d) else 0)")" "K2.2b the governance suite reports the tampered CIT state at high severity" "$(echo "$AUD" | head -c 300)"
cp "$SCRATCH/$CIT.orig.yaml" "$CITF"

echo "== K2  the gate decides; execution without an honoured answer is refused"
GATE="$(res cit show "$CIT" | python3 -c "import json,sys;print(json.load(sys.stdin)['human_gate'])")"
check "$([ -n "$GATE" ] && [ "$GATE" != None ] && echo 1 || echo 0)" "K2.3 a material change raises its human gate" "gate=$GATE"
check "$([ "$(code cit execute "$CIT")" != OK ] && echo 1 || echo 0)" "K2.4 execution before the gate is answered is refused"
decide_human "$GATE" A >/dev/null
check_eq "$(code cit approve "$CIT")" OK "K2.5 the CIT is approved once the owner's signed answer is honoured"
BEFORE_IDX="$(python3 -c "import json;print(json.load(open('$MROOT/governance/generated/index-manifest.json'))['manifest_hash'])" 2>/dev/null || echo none)"
EXEC="$(res cit execute "$CIT")"
check "$(echo "$EXEC" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d.get('cit_status')=='COMMITTED' or d.get('status')=='COMMITTED' else 0)")" "K2.6 an approved CIT commits" "$(echo "$EXEC" | head -c 400)"

echo "== K2  authoritative updates, propagation, derived views, index refresh"
check "$(python3 -c "
import yaml;d=yaml.safe_load(open('$MROOT/spec/requirements/REQ-0001.yaml'))
print(1 if 'negative quantities' in str(d['acceptance_criteria']) else 0)")" "K2.7 the authoritative record carries the change the manifest declared"
T="$(res task show "$IMPL")"
check "$(echo "$T" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d.get('revalidation') or d.get('retest_required') else 0)")" "K2.8 the DONE task that implemented the seed is marked for revalidation/retest" "$(echo "$T" | python3 -c "import json,sys;d=json.load(sys.stdin);print({k:v for k,v in d.items() if 'reval' in k or 'retest' in k or 'stale' in k})")"
GEN="$(res task generate --dry-run 2>/dev/null)"
ALLT="$(res task list | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin)))")"
check "$(echo "$ALLT" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin)).lower();print(1 if 'revalidat' in s else 0)")" "K2.9 a revalidation task is generated for the completed work" "$(echo "$ALLT" | head -c 400)"
TST="$(python3 -c "import yaml;d=yaml.safe_load(open('$MROOT/spec/tasks/TST-0001.yaml'));print(1 if d.get('staleness') else 0)")"
check "$TST" "K2.10 the acceptance obligation within the radius is marked stale"
CK="$(res checkpoint freshness 2>/dev/null)"
check "$(echo "$CK" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin)).lower();print(1 if ('stale' in s and 'true' in s) or 'STALE' in s.upper() else 0)")" "K2.11 the checkpoint that captured the pre-change state is reported stale" "$(echo "$CK" | head -c 500)"
AFTER_IDX="$(python3 -c "import json;print(json.load(open('$MROOT/governance/generated/index-manifest.json'))['manifest_hash'])" 2>/dev/null || echo none)"
check "$([ "$BEFORE_IDX" != "$AFTER_IDX" ] && echo 1 || echo 0)" "K2.12 CIT-E refreshes the index (manifest hash changed)" "before=$BEFORE_IDX after=$AFTER_IDX"
check "$(res cit show "$CIT" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d['os_state'].get('writes_sha256') else 0)")" "K2.13 the executed writes are bound in the CIT's sealed state"

echo "== K2  derived-view regeneration (the derived views are rebuilt from authoritative state by CIT-E)"
REG="$MROOT/governance/generated/tool-registry.json"; ADP="$MROOT/governance/generated/adapter-manifest.json"
cp "$REG" "$SCRATCH/reg.before.json"; cp "$ADP" "$SCRATCH/adp.before.json"
echo '{"tools": [], "damaged_by": "P2-AR-0049 held-out probe"}' > "$REG"
echo '{"adapters": [], "damaged_by": "P2-AR-0049 held-out probe"}' > "$ADP"
cat > "$MROOT/.governance-runtime/mf-view.json" <<'JSON'
[{"op":"set_field","target":"REQ-0001","field":"title","value":"Ledger totals are exact integer cents (v2)"}]
JSON
VC="$(res cit propose --proposal "retitle the ledger requirement" --trigger behaviour_change --title "retitle" --manifest "$MROOT/.governance-runtime/mf-view.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
VG="$(res cit show "$VC" | python3 -c "import json,sys;print(json.load(sys.stdin).get('human_gate'))")"
[ "$VG" != None ] && [ -n "$VG" ] && decide_human "$VG" A >/dev/null 2>&1
g cit approve "$VC" >/dev/null 2>&1
VOUT="$(code cit execute "$VC")"
RD="$(python3 -c "import json;print(0 if 'damaged_by' in open('$REG').read() else 1)")"
AD="$(python3 -c "import json;print(0 if 'damaged_by' in open('$ADP').read() else 1)")"
echo "   execute -> $VOUT ; tool registry rebuilt=$RD ; adapter manifest rebuilt=$AD"
check "$([ "$VOUT" = OK ] && [ "$RD" = 1 ] && [ "$AD" = 1 ] && echo 1 || echo 0)" "K2.13b CIT-E regenerates the derived views from the committed authoritative state" "execute=$VOUT registry=$RD adapters=$AD"

echo "== K2  verification and atomic rollback of a failed transaction"
cat > "$MROOT/.governance-runtime/mf-bad.json" <<'JSON'
[{"op":"set_field","target":"REQ-0001","field":"governed_by","value":["D-9999"]},
 {"op":"write_file","path":"src/extra.rs","content":"pub fn extra() {}\n"}]
JSON
BAD="$(res cit propose --proposal "introduce a dangling reference" --trigger behaviour_change --title bad --manifest "$MROOT/.governance-runtime/mf-bad.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
BG="$(res cit show "$BAD" | python3 -c "import json,sys;print(json.load(sys.stdin).get('human_gate'))")"
[ "$BG" != None ] && [ -n "$BG" ] && decide_human "$BG" A >/dev/null 2>&1
g cit approve "$BAD" >/dev/null 2>&1
BADOUT="$(g cit execute "$BAD" 2>&1)"
BADCODE="$(echo "$BADOUT" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else d['error']['code'])")"
echo "   bad CIT execute -> $BADCODE"
ST="$(res cit show "$BAD" | python3 -c "import json,sys;print(json.load(sys.stdin)['os_state']['cit_status'])")"
check "$([ "$ST" = ROLLED_BACK ] && echo 1 || echo 0)" "K2.14 a transaction that fails verification is rolled back, not half-applied" "status=$ST code=$BADCODE"
check "$([ ! -f "$MROOT/src/extra.rs" ] && echo 1 || echo 0)" "K2.15 the rollback restores every file the failed transaction wrote"
check "$(python3 -c "
import yaml;d=yaml.safe_load(open('$MROOT/spec/requirements/REQ-0001.yaml'))
print(1 if 'D-9999' not in str(d.get('governed_by','')) else 0)")" "K2.16 the rollback restores the authoritative record"

echo "== delta duty: a CIT declined inside another task's claim window"
W="$(res task create --class implementation --objective "Widen the ledger API" --feature F-0001 --status READY --allowed 'src/**' --fields '{"requirements":["REQ-0001"],"scenarios":["SCN-0001"],"acceptance_tests":["TST-0001"],"role":"backend-engineer"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
SESSION=w ROLE=backend-engineer g task claim "$W" >/dev/null 2>&1
cat > "$MROOT/.governance-runtime/mf-decl.json" <<'JSON'
[{"op":"set_field","target":"REQ-0001","field":"title","value":"Ledger totals are decimal"}]
JSON
DC="$(res cit propose --proposal "switch the ledger to decimals" --trigger behaviour_change --title "decline me" --manifest "$MROOT/.governance-runtime/mf-decl.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
DG="$(res cit show "$DC" | python3 -c "import json,sys;print(json.load(sys.stdin).get('human_gate'))")"
echo "   declined CIT=$DC gate=$DG (raised while $W is claimed by session w)"
if [ "$DG" != None ] && [ -n "$DG" ]; then decide_human "$DG" B >/dev/null; fi
check "$([ "$(code cit approve "$DC")" != OK ] && echo 1 || echo 0)" "K2.17 a declined gate does not approve its CIT"
check "$([ "$(code cit execute "$DC")" != OK ] && echo 1 || echo 0)" "K2.18 a declined CIT cannot execute"
check "$(python3 -c "
import yaml;d=yaml.safe_load(open('$MROOT/spec/requirements/REQ-0001.yaml'))
print(1 if d['title'] != 'Ledger totals are decimal' else 0)")" "K2.19 the declined change never reached the authoritative record"
# the claim window itself survives the decline: the other task's work is unaffected and it still closes
echo 'pub fn total_cents(v: &[(i64,i64)]) -> i64 { v.iter().map(|(q,c)| q*c).sum() }  // widened' > "$MROOT/src/lib.rs"
g rebuild-memory --incremental >/dev/null 2>&1
RW="$(SESSION=w ROLE=backend-engineer receipt "$W" w-close "widened the ledger API" "src/lib.rs" not_applicable_with_reason "$NA_TESTS")"
CW="$(SESSION=w ROLE=backend-engineer code task close "$W" --report "$RW")"
echo "   the claimed task's close after the decline -> $CW"
check "$([ "$CW" != "CIT_"* ] && [ "$CW" != GATE_NOT_AUTHORISED ] && echo 1 || echo 0)" "K2.20 the declined CIT does not block the unrelated claimed task's own close path" "close=$CW"

summary
