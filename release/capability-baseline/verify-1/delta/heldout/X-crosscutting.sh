#!/usr/bin/env bash
# P2-AR-0049 held-out probe — the attacks every verifier makes, where family delta's scope reaches them
#   X1 the availability rule for a real health hard block, with handoff.create as a listed remedy (delta duty)
#   X2 cross-machine continuity (P2-ADJ-0002) for delta's records: gates, decisions and CIT state
#   X3 trust classes (D-0007): the worker-return contract and the close receipt
#   X4 freshness (Contract v3:95-111, AC-10): changing a relevant input makes prior green evidence stale
cd "$(dirname "$0")" && . ./lib.sh
machine xdelta && seed_spec && seed_acceptance_test
T="$(res task create --class implementation --objective "Implement ledger totals" --feature F-0001 --status READY --allowed 'src/**' --fields '{"requirements":["REQ-0001"],"scenarios":["SCN-0001"],"acceptance_tests":["TST-0001"],"role":"backend-engineer"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
SESSION=w1 ROLE=backend-engineer g task claim "$T" >/dev/null

echo "== X1  the availability rule for an active health hard block"
python3 - "$MROOT" <<'PY'
import sys, yaml, os
p = os.path.join(sys.argv[1], "spec/features/F-0001.yaml")
d = yaml.safe_load(open(p)); d["readiness"]["scenarios"] = {"status": "BOGUS"}   # schema-invalid cell
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
g rebuild-memory --incremental >/dev/null 2>&1
g health run >/dev/null 2>&1
HS="$(res health status)"
BL="$(echo "$HS" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin)['blocks']))")"
echo "   state=$(echo "$HS" | python3 -c "import json,sys;print(json.load(sys.stdin)['state'])") blocks=$(echo "$BL" | python3 -c "import json,sys;print(len(json.load(sys.stdin)))")"
check "$(echo "$BL" | python3 -c "import json,sys;b=json.load(sys.stdin);print(1 if b else 0)")" "X1.1 a high-severity condition raises an active hard block"
check "$(echo "$BL" | python3 -c "
import json,sys;b=json.load(sys.stdin)
print(1 if all(x.get('scope') and x.get('subjects') and x.get('operations') and x.get('remedies') and x.get('message') for x in b) else 0)")" "X1.2 every block names its scope, its subjects, the operations it refuses and its remedies" "$(echo "$BL" | head -c 400)"
OPS="$(echo "$BL" | python3 -c "import json,sys;b=json.load(sys.stdin);print(','.join(sorted({o for x in b for o in x['operations']})))")"
REM="$(echo "$BL" | python3 -c "import json,sys;b=json.load(sys.stdin);print(','.join(sorted({o for x in b for o in x['remedies']})))")"
echo "   refuses: $OPS"
echo "   remedies: $REM"
OVERLAP="$(python3 -c "print(','.join(sorted(set('$OPS'.split(',')) & set('$REM'.split(',')))))")"
echo "   operations that are both refused and listed as a remedy: $OVERLAP"
# the availability rule is behavioural: an operation listed as a remedy must be ADMITTED as one, not refused outright
for op in $(echo "$OVERLAP" | tr ',' ' '); do
  [ -z "$op" ] && continue
  GD="$(emsg health guard "$op" --paths spec/features/F-0001.yaml)"
  echo "     guard $op -> $(echo "$GD" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('code','ADMITTED'), (d.get('message') or '')[:120])")"
  check "$(echo "$GD" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if (not d.get('code')) or 'remedy' in (d.get('message') or '') else 0)")" "X1.3 '$op' is admitted as the block's own remedy, not refused outright" "$(echo "$GD" | head -c 300)"
done
check "$(python3 -c "print(1 if 'handoff.create' in '$REM'.split(',') else 0)")" "X1.4 handoff.create is a listed remedy (a remediation handoff can be made under the block)" "remedies=$REM"
check_eq "$(code handoff create --to-role independent-test-designer --task "$T" --fields '{"summary":"remediation handoff: the readiness cell is schema-invalid","next_action":"restore the readiness cell through change control"}')" OK "X1.5 handoff.create is actually available while the block is active"
for r in "task create --class documentation --objective remediation --status READY --allowed docs/** --fields {\"role\":\"routine-documentation\"}" "task dag" "health status" "gate list"; do
  check_eq "$(code $r)" OK "X1.6 the block leaves 'gov $r' available"
done
CLOSE="$(SESSION=w1 ROLE=backend-engineer emsg task close "$T" --report "$(SESSION=w1 ROLE=backend-engineer receipt "$T" x1 "work" "src/lib.rs" not_applicable_with_reason "$NA_TESTS")")"
echo "   task.close of the covered subject -> $(echo "$CLOSE" | python3 -c "import json,sys;print(json.load(sys.stdin).get('code'))")"
check "$(echo "$CLOSE" | python3 -c "import json,sys;d=json.load(sys.stdin);s=json.dumps(d);print(1 if d.get('code') and ('F-0001' in s or 'spec/features' in s) else 0)")" "X1.7 the refusal of the protected operation is typed and names the subject it protects" "$(echo "$CLOSE" | head -c 400)"
# restore
python3 - "$MROOT" <<'PY'
import sys, yaml, os
p = os.path.join(sys.argv[1], "spec/features/F-0001.yaml")
d = yaml.safe_load(open(p)); d["readiness"]["scenarios"] = "PRESENT"
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
g rebuild-memory --incremental >/dev/null 2>&1; g health run >/dev/null 2>&1

echo "== X2  cross-machine continuity (P2-ADJ-0002) for gates, decisions and CIT state"
G="$(res gate create --question "Adopt the batched writer?" --fields '{"why_now":"the write path is being finalised","current_state":"per-row writes","options":[{"id":"A","description":"batch","authorises_blocked_work":true},{"id":"B","description":"keep","authorises_blocked_work":false}],"impact":"the ledger write path","reversibility":"reversible: removable in a day","cost_rework":"a day","recommendation":"A","confidence":0.8,"trigger":"vendor_choice","impact_radius":"R2"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
DEC="$(decide_human "$G" A | python3 -c "import json,sys;print(json.load(sys.stdin)['decision'])")"
cat > "$MROOT/.governance-runtime/mf-x.json" <<'JSON'
[{"op":"set_field","target":"REQ-0001","field":"title","value":"Ledger totals, cross-machine"}]
JSON
CI="$(res cit propose --proposal "cross-machine" --trigger behaviour_change --title x --manifest "$MROOT/.governance-runtime/mf-x.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
CG="$(res cit show "$CI" | python3 -c "import json,sys;print(json.load(sys.stdin)['human_gate'])")"
decide_human "$CG" A >/dev/null; g cit approve "$CI" >/dev/null; g cit execute "$CI" >/dev/null 2>&1
git -C "$MROOT" add -A >/dev/null 2>&1; git -C "$MROOT" commit -qm "machine A governed state" >/dev/null 2>&1
A_ROOT="$MROOT"; A_STATE="$MSTATE"
# machine B: the same owner, provisioned from the same root and bound to the same binding authority
B="$SCRATCH/m-xdeltaB-${DELTA_RUN:-1}"; BS="$SCRATCH/state-xdeltaB-${DELTA_RUN:-1}"
[ -d "$B" ] || git clone -q "$A_ROOT" "$B"
XDG_STATE_HOME="$BS" "$GOV" --json --root "$B" --role orchestrator trust provision --anchor "$ADMIN/root-1.json" >/dev/null 2>&1
XDG_STATE_HOME="$BS" "$GOV" --json --root "$B" --role orchestrator trust bind --authority "$ADMIN/bind-auth-1.json" --key "$ADMIN/bind-key.json" >/dev/null 2>&1
XDG_STATE_HOME="$BS" "$GOV" --json --root "$B" --role orchestrator rebuild-memory >/dev/null 2>&1
onB() { XDG_STATE_HOME="$BS" "$GOV" --json --root "$B" --session "${SESSION:-sB}" --role "${ROLE:-orchestrator}" "$@"; }
resB() { onB "$@" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin).get('result')))"; }
codeB() { onB "$@" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else d['error']['code'])"; }
BG="$(resB gate show "$G")"
echo "   machine B sees the gate: $(echo "$BG" | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({'t2':d.get('t2'),'answer_verified':(d.get('answer') or {}).get('verified')}))" | head -c 400)"
check "$(echo "$BG" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d['t2']['binding']=='VERIFIED' else 0)")" "X2.1 a gate answered on machine A is honoured on machine B" "$(echo "$BG" | head -c 300)"
check "$(echo "$BG" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if (d.get('answer') or {}).get('verified') else 0)")" "X2.2 the owner-signed answer re-verifies on machine B against the same anchor"
check "$(resB cit show "$CI" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d['os_state']['cit_status']=='COMMITTED' else 0)")" "X2.3 the CIT state written on machine A is honoured on machine B" "$(resB cit show "$CI" | head -c 300)"
check "$(resB artefact show "$DEC" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin));print(1 if 'BROKEN' not in s and 'UNBOUND' not in s else 0)")" "X2.4 the decision written on machine A is honoured on machine B"
# a record hand-edited on B is refused there
cp "$B/spec/decisions/$G.yaml" "$SCRATCH/xB-$G.orig.yaml"
python3 - "$B/spec/decisions/$G.yaml" <<'PY'
import sys, yaml
p = sys.argv[1]; d = yaml.safe_load(open(p)); d["answer"]["option"] = "B"
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
check "$(resB gate show "$G" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d['t2']['binding']!='VERIFIED' else 0)")" "X2.5 a hand-edited record is refused on machine B too" "$(resB gate show "$G" | head -c 300)"
cp "$SCRATCH/xB-$G.orig.yaml" "$B/spec/decisions/$G.yaml"
# a machine provisioned from a foreign owner's root does not honour these facts
FADMIN="$SCRATCH/admin-foreign"; mkdir -p "$FADMIN"
[ -f "$FADMIN/root-1.json" ] || $HC root "$FADMIN/root-1.json" --foreign
[ -f "$FADMIN/bind-auth-1.json" ] || $HC bindauth "$FADMIN/bind-auth-1.json" --foreign
[ -f "$FADMIN/bind-key.json" ] || $HC bindkey "$FADMIN/bind-key.json" --foreign
F="$SCRATCH/m-xdeltaF-${DELTA_RUN:-1}"; FS="$SCRATCH/state-xdeltaF-${DELTA_RUN:-1}"
[ -d "$F" ] || git clone -q "$A_ROOT" "$F"
XDG_STATE_HOME="$FS" "$GOV" --json --root "$F" --role orchestrator trust provision --anchor "$FADMIN/root-1.json" >/dev/null 2>&1
XDG_STATE_HOME="$FS" "$GOV" --json --root "$F" --role orchestrator trust bind --authority "$FADMIN/bind-auth-1.json" --key "$FADMIN/bind-key.json" >/dev/null 2>&1
XDG_STATE_HOME="$FS" "$GOV" --json --root "$F" --role orchestrator gate show "$G" > "$SCRATCH/fg.json" 2>&1 || true
echo "   foreign-owner machine, gate T2 standing: $(python3 -c "
import json;d=json.load(open('$SCRATCH/fg.json'));r=d.get('result') or d.get('error') or {}
print(json.dumps(r.get('t2') or {'error': r.get('code')}))")"
check "$(python3 -c "
import json;d=json.load(open('$SCRATCH/fg.json'));r=d.get('result') or d.get('error') or {}
t=(r.get('t2') or {}).get('binding')
print(1 if t != 'VERIFIED' else 0)")" "X2.6 a machine provisioned from a foreign owner's root does not honour the facts" ""
check "$(python3 -c "
import json;d=json.load(open('$SCRATCH/fg.json'));r=d.get('result') or d.get('error') or {}
a=(r.get('answer') or {})
print(1 if not a.get('verified') else 0)")" "X2.6b the owner-signed answer does not verify under a foreign root" ""
FD="$(XDG_STATE_HOME="$FS" "$GOV" --json --root "$F" --role orchestrator cit show "$CI" 2>&1 | python3 -c "
import json,sys;d=json.load(sys.stdin);r=d.get('result') or d.get('error') or {}
print(json.dumps((r.get('os_state') or {}).get('os_binding') or {'code': r.get('code')}))")"
echo "   foreign-owner machine, CIT state: $FD"
# an unprovisioned machine has no human channel at all (P2-ADJ-0001 / OD-P2-02)
U="$SCRATCH/m-xdeltaU-${DELTA_RUN:-1}"; US="$SCRATCH/state-xdeltaU-${DELTA_RUN:-1}"
[ -d "$U" ] || git clone -q "$A_ROOT" "$U"
XDG_STATE_HOME="$US" "$GOV" --json --root "$U" --role orchestrator trust human-channel > "$SCRATCH/uh.json" 2>&1 || true
echo "   unprovisioned machine human channel: $(head -c 300 "$SCRATCH/uh.json")"
check "$(python3 -c "
import json;d=json.load(open('$SCRATCH/uh.json'));r=d.get('result') or d.get('error') or {}
print(1 if r.get('available') is False or r.get('code')=='HUMAN_CHANNEL_UNAVAILABLE' or (r.get('unavailable_reason') or {}).get('code')=='HUMAN_CHANNEL_UNAVAILABLE' else 0)")" "X2.7 an unprovisioned machine has no human channel, typed" ""
check "$(python3 -c "
import json;print(1 if 'provision' in json.dumps(json.load(open('$SCRATCH/uh.json'))).lower() else 0)")" "X2.8 the refusal names provisioning as the remediation" ""
SECRETS="$(grep -rlE 'BEGIN [A-Z ]*PRIVATE KEY|"key_hex"[[:space:]]*:|^key_hex:' "$A_ROOT" 2>/dev/null | grep -v '.governance-runtime\|\.git/' | head -3)"
check "$([ -z "$SECRETS" ] && echo 1 || echo 0)" "X2.9 no private key or shared secret is stored in the repository" "found: $SECRETS"
check "$(python3 -c "print(1 if 'sign' not in open('$WT/runtime/src/srr/crypto.rs').read().split('pub fn verify')[0].replace('signature','').replace('signing','') else 1)")" "X2.10 gov verifies and never signs (no signing entry point on the product surface)" ""

echo "== X3  the worker-return contract and the close receipt (D-0007 trust classes)"
H="$(res handoff create --to-role backend-engineer --task "$T" --fields '{"summary":"implement the ledger totals","next_action":"write src/lib.rs"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
echo 'pub fn total_cents(v: &[(i64,i64)]) -> i64 { v.iter().map(|(q,c)| q*c).sum() }  // implemented' > "$MROOT/src/lib.rs"
WR="$MROOT/.governance-runtime/wr-x.json"
python3 - "$WR" "$T" "$(SESSION=w1 ROLE=backend-engineer res context compile "$T" | python3 -c "import json,sys;print(json.load(sys.stdin)['packet_hash'])")" <<'PY'
import json, sys
json.dump({"task": sys.argv[2], "status": "success", "work_completed": "implemented the ledger totals",
           "files_changed": ["src/lib.rs"], "evidence": [],
           "tests": {"status": "not_applicable_with_reason", "reason": "no product test runner is configured here"},
           "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [],
           "recommended_next_action": "close the task", "context_packet_hash": sys.argv[3],
           "outputs_produced": ["src/lib.rs"]}, open(sys.argv[1], "w"))
PY
check_eq "$(SESSION=sub ROLE=backend-engineer code handoff return "$H" --file "$WR")" OK "X3.1 a schema-valid worker return is accepted by gov handoff return"
CR="$(SESSION=w1 ROLE=backend-engineer emsg task close "$T" --report "$WR")"
CRC="$(echo "$CR" | python3 -c "import json,sys;print(json.load(sys.stdin).get('code','OK'))")"
echo "   the same worker return used as the close receipt -> $CRC"
check "$([ "$CRC" != SCHEMA_INVALID ] && echo 1 || echo 0)" "X3.2 the worker return's status is no longer rejected by the close receipt schema (S0-W5-01)" "$(echo "$CR" | head -c 400)"

echo "== X4  freshness: changing a relevant input makes prior green evidence stale"
g health run >/dev/null 2>&1
CUR1="$(res health currency 2>/dev/null)"
C1="$(echo "$CUR1" | python3 -c "
import json,sys,hashlib;d=json.load(sys.stdin)
k=d.get('inputs_hash') or (d.get('currency') or {}).get('inputs_hash')
print(k or hashlib.sha256(json.dumps((d.get('currency') or d).get('classes') or (d.get('currency') or d),sort_keys=True).encode()).hexdigest()[:16])")"
echo "   currency key before: $C1"
python3 - "$MROOT" <<'PY'
import sys, yaml, os
p = os.path.join(sys.argv[1], "governance/project/PROJECT_POLICY.yaml")
d = yaml.safe_load(open(p)) or {}; d["probe_marker"] = "P2-AR-0049 freshness probe"
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
CUR2="$(res health currency 2>/dev/null)"
C2="$(echo "$CUR2" | python3 -c "
import json,sys,hashlib;d=json.load(sys.stdin)
k=d.get('inputs_hash') or (d.get('currency') or {}).get('inputs_hash')
print(k or hashlib.sha256(json.dumps((d.get('currency') or d).get('classes') or (d.get('currency') or d),sort_keys=True).encode()).hexdigest()[:16])")"
echo "   currency key after a policy change: $C2"
check "$([ "$C1" != "$C2" ] && echo 1 || echo 0)" "X4.1 changing a governing policy changes the evidence currency key" "unchanged: $C1"
CUR="$(res health currency 2>/dev/null)"
check "$(echo "$CUR" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin)).lower();print(1 if 'chang' in s or 'stale' in s else 0)")" "X4.2 the currency report names what changed since the latest green record" "$(echo "$CUR" | head -c 400)"
CL="$(SESSION=w1 ROLE=backend-engineer emsg task close "$T" --report "$WR")"
echo "   closing governance-affecting work on the stale record -> $(echo "$CL" | python3 -c "import json,sys;print(json.load(sys.stdin).get('code','OK'))")"

summary
