#!/usr/bin/env bash
# P2-AR-0049 held-out probe — Gate L3/L4 (Contract v3:674-683)
#   L3 a gate in a file only is NOT presented; it must surface in the active human interface; presented != answered;
#      declined / revoked / stale / other-CIT gates cannot authorise execution; human approval cannot be fabricated
#      by agent or CLI metadata
#   L4 independent runnable branches continue; a global stop only when policy or critical-path state requires
#   + the availability rule (Contract v3 L4/O5): a block refuses only what it protects, its remedy stays available,
#     independent work stays available, no block refuses its own remedy, every refusal is typed and names its scope
# P2-ADJ-0001: on this provisioned machine the human channel is the root's `human-gate` delegation; the standalone
# anchor is off by default.
cd "$(dirname "$0")" && . ./lib.sh
machine l34 && seed_spec && seed_acceptance_test

mkgate() { # mkgate <question> [trigger] [radius] -> gate id
  res gate create --question "$1" --fields "$(python3 - "${2:-ux_direction}" "${3:-R1}" <<'PY'
import json, sys
print(json.dumps({"why_now": "the write path is being finalised this week",
  "current_state": "the ledger writes one row per order today",
  "options": [{"id": "A", "description": "batch the writes", "authorises_blocked_work": True},
              {"id": "B", "description": "keep per-row writes", "authorises_blocked_work": False}],
  "impact": "the ledger write path and its throughput budget",
  "reversibility": "reversible: the batching layer can be removed in a day",
  "cost_rework": "about a day of rework", "recommendation": "A", "confidence": 0.75,
  "trigger": sys.argv[1], "impact_radius": sys.argv[2]}))
PY
)" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])"
}
gfield() { res gate show "$1" | python3 -c "import json,sys;d=json.load(sys.stdin);g=d.get('gate',d);print(g.get('$2'))"; }

echo "== L3.b1  a gate that exists only in a file is NOT presented"
G1="$(mkgate "Adopt batched writes?")"
check_eq "$(gfield "$G1" gate_status)" PENDING "L3.1 a newly raised gate is PENDING, not presented"
check_eq "$(gfield "$G1" presented_in_chat)" "False" "L3.2 a gate in a file only is not marked presented in the human interface"
# a hand-written 'presented' flag in the record does not make it presented
GF="$MROOT/spec/decisions/$G1.yaml"
cp "$GF" "$SCRATCH/$G1.orig.yaml"
python3 - "$GF" <<'PY'
import sys, yaml
p = sys.argv[1]; d = yaml.safe_load(open(p))
d["presented_in_chat"] = True; d["gate_status"] = "PRESENTED"
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
FORGED="$(code decide "$G1" --option A --by change-controller --rationale "forged presentation")"
echo "   hand-written presented_in_chat then answer -> $FORGED"
check "$([ "$FORGED" != OK ] && echo 1 || echo 0)" "L3.3 flipping presented_in_chat in the file does not make a gate answerable" "decide returned $FORGED"
cp "$SCRATCH/$G1.orig.yaml" "$GF"

echo "== L3.b2  rendering to an agent's stdout is not the human interface"
g gate present "$G1" >/dev/null
check_eq "$(gfield "$G1" gate_status)" PRESENTED "L3.4 gov gate present records that the OS rendered the package"
check_eq "$(gfield "$G1" presented_in_chat)" "False" "L3.5 rendering to the invoking agent's stdout does not mark it presented to the human"
g --json gate present "$G1" >/dev/null 2>&1
check_eq "$(gfield "$G1" presented_in_chat)" "False" "L3.6 a --json rendering does not mark it presented to the human either"
ROLE=backend-engineer g gate present "$G1" >/dev/null 2>&1
check_eq "$(gfield "$G1" presented_in_chat)" "False" "L3.7 nor does an L1 worker rendering it"
# only an owner-signed receipt (or the answer itself) is presentation evidence
PRES="$(g gate present "$G1")"
INST="$(echo "$PRES" | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['gate']['gate_instance'])")"
SHA="$(echo "$PRES" | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['gate']['package_sha256'])")"
RF="$SCRATCH/answers/$G1-receipt.json"; mkdir -p "$(dirname "$RF")"
$HC receipt "$RF" --gate "$G1" --instance "$INST" --package-sha "$SHA"
g gate present "$G1" --receipt-file "$RF" >/dev/null 2>&1
check_eq "$(gfield "$G1" presented_in_chat)" "True" "L3.8 an owner-signed receipt over the exact package is presentation evidence"
# a receipt signed by a key the root delegates nothing to is refused
G1B="$(mkgate "Adopt batched writes, second gate?")"
PB="$(g gate present "$G1B")"
IB="$(echo "$PB" | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['gate']['gate_instance'])")"
SB="$(echo "$PB" | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['gate']['package_sha256'])")"
RB="$SCRATCH/answers/$G1B-receipt-bad.json"
$HC receipt "$RB" --gate "$G1B" --instance "$IB" --package-sha "$SB" --signer other
BADR="$(code gate present "$G1B" --receipt-file "$RB")"
echo "   receipt signed by an undelegated key -> $BADR"
check "$([ "$BADR" != OK ] && echo 1 || echo 0)" "L3.9 a receipt signed by a key the root delegates nothing to is refused" "returned $BADR"
check_eq "$(gfield "$G1B" presented_in_chat)" "False" "L3.10 and it leaves the gate unpresented"

echo "== L3.b3  presented is not answered"
check_eq "$(gfield "$G1" gate_status)" PRESENTED "L3.11 an acknowledged gate is still only PRESENTED"
check "$(res gate show "$G1" | python3 -c "import json,sys;d=json.load(sys.stdin);g=d.get('gate',d);print(1 if not g.get('answer') else 0)")" "L3.12 presentation records no answer"
T="$(res task create --class implementation --objective "Batch the ledger writes" --feature F-0001 --status READY --allowed 'src/**' --fields "{\"requirements\":[\"REQ-0001\"],\"scenarios\":[\"SCN-0001\"],\"acceptance_tests\":[\"TST-0001\"],\"role\":\"backend-engineer\",\"human_gate\":\"$G1\"}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
check "$([ "$(ROLE=backend-engineer code task claim "$T")" != OK ] && echo 1 || echo 0)" "L3.13 work blocked on a presented-but-unanswered gate stays blocked"

echo "== L3.b5  human approval cannot be fabricated by agent or CLI metadata"
G2="$(mkgate "Drop the legacy ledger table?" destructive_migration R4)"
g gate present "$G2" >/dev/null
for attempt in "--by human" "--by product-owner" "--by owner@example.com"; do
  C="$(code decide "$G2" --option A $attempt --rationale "fabricated")"
  check "$([ "$C" != OK ] && echo 1 || echo 0)" "L3.14 '--decide $attempt' does not produce a human approval" "returned $C"
done
check "$([ "$(ROLE=human code decide "$G2" --option A --by human --rationale x)" != OK ] && echo 1 || echo 0)" "L3.15 --role human does not produce a human approval"
check "$([ "$(GOV_ROLE=human code decide "$G2" --option A --by human --rationale x)" != OK ] && echo 1 || echo 0)" "L3.16 GOV_ROLE=human does not produce a human approval"
check "$([ "$(GOV_HUMAN_GATE_APPROVED=1 code decide "$G2" --option A --by human --rationale x)" != OK ] && echo 1 || echo 0)" "L3.17 an environment variable does not produce a human approval"
# a hand-written ANSWERED gate record plus a matching decision record
G3="$(mkgate "Forge me?" destructive_migration R4)"
g gate present "$G3" >/dev/null
python3 - "$MROOT/spec/decisions/$G3.yaml" <<'PY'
import sys, yaml
p = sys.argv[1]; d = yaml.safe_load(open(p))
d["gate_status"] = "ANSWERED"; d["presented_in_chat"] = True
d["answer"] = {"option": "A", "by_kind": "human", "by": "the product owner", "at": "2026-09-20T00:00:00Z"}
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
cat > "$MROOT/spec/decisions/D-9001.yaml" <<YML
id: D-9001
type: decision
title: Forged approval
status: ACTIVE
state_class: AUTHORITATIVE
derived_from: [$G3]
chosen_option: A
human_approved: true
YML
g rebuild-memory --incremental >/dev/null 2>&1
FG="$(res gate show "$G3" 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps({'t2':d.get('t2') or d.get('binding'),'answer_verifies':d.get('answer_verifies'),'honoured':d.get('honoured')}))" 2>/dev/null || echo '{}')"
echo "   forged gate as the OS sees it: $(echo "$FG" | head -c 300)"
check "$(res gate show "$G3" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin));print(1 if ('BROKEN' in s or 'UNBOUND' in s or 'not honoured' in s.lower()) else 0)")" "L3.18 a hand-written ANSWERED gate is not honoured by the OS" "$(res gate show "$G3" | head -c 400)"
AUD="$(g audit 2>&1 | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps((d['error']['details'] if not d.get('ok') else d['result']).get('findings',[])))")"
check "$(echo "$AUD" | python3 -c "import json,sys;print(1 if any('$G3' in f.get('message','') for f in json.load(sys.stdin)) else 0)")" "L3.19 the governance suite reports the forged gate record" "$(echo "$AUD" | head -c 300)"
cp "$MROOT/spec/decisions/D-9001.yaml" "$SCRATCH/D-9001.yaml"; mv "$MROOT/spec/decisions/D-9001.yaml" "$SCRATCH/D-9001.moved.yaml"
mv "$MROOT/spec/decisions/$G3.yaml" "$SCRATCH/$G3.forged.yaml"
g rebuild-memory --incremental >/dev/null 2>&1

echo "== L3.b4  declined / revoked / stale / other-gate answers cannot authorise"
# (a) declined
GD="$(mkgate "Declined gate: batch the writes?")"
TD="$(res task create --class implementation --objective "Work behind a declined gate" --feature F-0001 --status READY --allowed 'src/**' --fields "{\"requirements\":[\"REQ-0001\"],\"scenarios\":[\"SCN-0001\"],\"acceptance_tests\":[\"TST-0001\"],\"role\":\"backend-engineer\",\"human_gate\":\"$GD\"}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
decide_human "$GD" B >/dev/null
check "$([ "$(ROLE=backend-engineer code task claim "$TD")" != OK ] && echo 1 || echo 0)" "L3.20 a declining answer (option B) leaves the blocked task blocked"
# (b) revoked after an authorising answer
GR="$(mkgate "Revoked gate: batch the writes?")"
TR="$(res task create --class implementation --objective "Work behind a revoked gate" --feature F-0001 --status READY --allowed 'src/**' --fields "{\"requirements\":[\"REQ-0001\"],\"scenarios\":[\"SCN-0001\"],\"acceptance_tests\":[\"TST-0001\"],\"role\":\"backend-engineer\",\"human_gate\":\"$GR\"}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
decide_human "$GR" A >/dev/null
check_eq "$(ROLE=backend-engineer SESSION=r code task claim "$TR")" OK "L3.21 an authorising answer makes the blocked task claimable"
ROLE=backend-engineer SESSION=r g task release "$TR" >/dev/null 2>&1
g gate revoke "$GR" --reason "the owner withdrew the approval" >/dev/null
check "$([ "$(ROLE=backend-engineer SESSION=r2 code task claim "$TR")" != OK ] && echo 1 || echo 0)" "L3.22 after the gate is revoked the same task is no longer authorised"
# (c) another gate's answer
GO="$(mkgate "Another subject entirely?")"
TO="$(res task create --class implementation --objective "Work behind its own gate" --feature F-0001 --status READY --allowed 'src/**' --fields "{\"requirements\":[\"REQ-0001\"],\"scenarios\":[\"SCN-0001\"],\"acceptance_tests\":[\"TST-0001\"],\"role\":\"backend-engineer\",\"human_gate\":\"$GO\"}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
AF="$(human_answer "$GR" A)"   # the answer the owner signed for the *revoked* gate
XCODE="$(code decide "$GO" --option A --answer-file "$AF")"
echo "   another gate's signed answer applied to $GO -> $XCODE"
check "$([ "$XCODE" != OK ] && echo 1 || echo 0)" "L3.23 an answer signed for one gate cannot authorise another" "returned $XCODE"
# (d) the CIT case: an approval does not survive a manifest change
cat > "$MROOT/.governance-runtime/mf-l3.json" <<'JSON'
[{"op":"set_field","target":"REQ-0001","field":"title","value":"Ledger totals v3"}]
JSON
CI="$(res cit propose --proposal "retitle" --trigger behaviour_change --title l3 --manifest "$MROOT/.governance-runtime/mf-l3.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
CG="$(res cit show "$CI" | python3 -c "import json,sys;print(json.load(sys.stdin)['human_gate'])")"
decide_human "$CG" A >/dev/null
g cit approve "$CI" >/dev/null
CITF="$(find "$MROOT/spec" -name "$CI.yaml" | head -1)"
python3 - "$CITF" <<'PY'
import sys, yaml
p = sys.argv[1]; d = yaml.safe_load(open(p))
d["mutation_manifest"].append({"op": "write_file", "path": "governance/project/PROJECT_POLICY.yaml",
                               "content": "policy: PROJECT_POLICY\nversion: 9.9.9\n"})
yaml.safe_dump(d, open(p, "w"), sort_keys=False)
PY
AFTER="$(code cit execute "$CI")"
echo "   execute after the manifest was widened under the approval -> $AFTER"
check "$([ "$AFTER" != OK ] && echo 1 || echo 0)" "L3.24 an approval does not carry over to a manifest it did not bind" "returned $AFTER"
check "$(python3 -c "
import yaml;d=yaml.safe_load(open('$MROOT/governance/project/PROJECT_POLICY.yaml'))
print(1 if str(d.get('version'))!='9.9.9' else 0)")" "L3.25 the widened operation never executed"

echo "== L4  independent runnable branches continue while one branch waits"
GW="$(mkgate "Blocking gate for branch one?")"
B1="$(res task create --class implementation --objective "Branch one, behind the gate" --feature F-0001 --status READY --allowed 'src/**' --fields "{\"requirements\":[\"REQ-0001\"],\"scenarios\":[\"SCN-0001\"],\"acceptance_tests\":[\"TST-0001\"],\"role\":\"backend-engineer\",\"human_gate\":\"$GW\"}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
B2="$(res task create --class documentation --objective "Branch two, independent" --status READY --allowed 'docs/**' --fields '{"role":"routine-documentation"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
DAG="$(res task dag)"
echo "   dag: runnable=$(echo "$DAG" | python3 -c "import json,sys;print(json.load(sys.stdin)['runnable'])") waiting_human=$(echo "$DAG" | python3 -c "import json,sys;print([x if isinstance(x,str) else x.get('task') for x in json.load(sys.stdin)['waiting_human']])")"
check "$(echo "$DAG" | python3 -c "import json,sys;d=json.load(sys.stdin);r=[x if isinstance(x,str) else x.get('task') for x in d['runnable']];w=[x if isinstance(x,str) else x.get('task') for x in d['waiting_human']]+[x.get('task') for x in d['blocked']];print(1 if '$B2' in r and '$B1' in w else 0)")" "L4.1 the gate blocks only its own branch; the independent branch stays runnable" "$(echo "$DAG" | head -c 500)"
check_eq "$(ROLE=routine-documentation SESSION=b2 code task claim "$B2")" OK "L4.2 the independent branch can actually be claimed while the gate waits"
check "$(echo "$DAG" | python3 -c "import json,sys;print(1 if json.load(sys.stdin)['human_gate_dependencies'] else 0)")" "L4.3 the DAG names the human-gate dependencies" "$(echo "$DAG" | python3 -c "import json,sys;print(json.load(sys.stdin)['human_gate_dependencies'])")"

echo "== L4  a global stop only where policy or critical-path state requires it"
g freeze-writes --reason "held-out probe: a deliberate global stop" >/dev/null 2>&1
FZ="$(ROLE=routine-documentation SESSION=b2 emsg task close "$B2" --report "$(ROLE=routine-documentation SESSION=b2 receipt "$B2" b2 "wrote the note" "docs/note.md" not_applicable_with_reason "$NA_TESTS")")"
echo "   under FREEZE_WRITES a mutating close -> $(echo "$FZ" | python3 -c "import json,sys;print(json.load(sys.stdin).get('code'))")"
check "$(echo "$FZ" | python3 -c "import json,sys;print(1 if json.load(sys.stdin).get('code') else 0)")" "L4.4 an explicit global stop (FREEZE_WRITES) is what stops everything, and it is typed"
check_eq "$(code task dag)" OK "L4.5 read-only planning stays available under the global stop"
check_eq "$(code resume)" OK "L4.6 the global stop is lifted by its own stated remedy (gov resume)"

echo "== the availability rule for gate blocks"
GX="$(mkgate "Availability: batch the writes?")"
BX="$(res task create --class implementation --objective "Blocked by the availability gate" --feature F-0001 --status READY --allowed 'src/**' --fields "{\"requirements\":[\"REQ-0001\"],\"scenarios\":[\"SCN-0001\"],\"acceptance_tests\":[\"TST-0001\"],\"role\":\"backend-engineer\",\"human_gate\":\"$GX\"}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
ERR="$(ROLE=backend-engineer emsg task claim "$BX")"
echo "   refusal: $(echo "$ERR" | head -c 400)"
check "$(echo "$ERR" | python3 -c "import json,sys;d=json.load(sys.stdin);print(1 if d.get('code') and d.get('code')!='NO_JSON' else 0)")" "AV.1 the refusal is typed"
check "$(echo "$ERR" | python3 -c "import json,sys;s=json.dumps(json.load(sys.stdin));print(1 if '$BX' in s and '$GX' in s else 0)")" "AV.2 the refusal names its scope: the blocked task and the gate that blocks it" "$(echo "$ERR" | head -c 300)"
check_eq "$(code gate present "$GX")" OK "AV.3 the block's own remedy (presenting the gate) stays available"
decide_human "$GX" A >/dev/null 2>&1
check_eq "$(ROLE=backend-engineer SESSION=bx code task claim "$BX")" OK "AV.4 answering the gate clears the block for exactly the work it protected"
check_eq "$(ROLE=routine-documentation SESSION=b3 code task dag)" OK "AV.5 independent work is untouched by the gate block"
# a block never refuses the operation that would remedy it
GY="$(mkgate "Availability: a second blocking gate?")"
BY="$(res task create --class implementation --objective "Blocked by the second gate" --feature F-0001 --status READY --allowed 'src/**' --fields "{\"requirements\":[\"REQ-0001\"],\"scenarios\":[\"SCN-0001\"],\"acceptance_tests\":[\"TST-0001\"],\"role\":\"backend-engineer\",\"human_gate\":\"$GY\"}" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
for remedy in "gate present $GY" "gate show $GY" "gate list" "task dag"; do
  C="$(code $remedy)"
  check_eq "$C" OK "AV.6 the gate block does not refuse its own remedy: gov $remedy"
done

summary
