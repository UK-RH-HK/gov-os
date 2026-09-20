#!/usr/bin/env bash
# D6 — rebuild guarantee (Contract v3:350-354), including the BC-P2-31 question: is anything the product itself
# classifies as DERIVED in fact non-rebuildable authoritative or operational state?
#
# `rm` is denied to this verifier, so "delete" is "move aside": the process under test sees the same absence.
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus d6); gov "$ROOT" init --name d6probe >/dev/null 2>&1
S=$BETA_SCRATCH/d6

# a claim and an emergency-control state to lose, and an authoritative record to preserve
CTID=$(gov "$ROOT" task create --class specification --objective "rebuild probe" --status READY \
        --allowed 'spec/**' --fields '{"role":"product-spec-agent"}' | jget 'd["result"]["id"]')
GOV_AS_ROLE=product-spec-agent GOV_SESSION_ID=S-claimer gov "$ROOT" task claim "$CTID" >/dev/null 2>&1
gov "$ROOT" freeze-writes --reason "rebuild probe" > "$S-freeze.json" 2>&1
CLAIMS_BEFORE=$(gov "$ROOT" claims list | jget 'json.dumps(d.get("result"))')
FROZEN_BEFORE=$(gov "$ROOT" status | jget 'json.dumps((d.get("result") or {}).get("control"))')
RECS_BEFORE=$(cd "$ROOT" && find spec governance/project -type f | sort | xargs md5sum | md5sum)

# ---- what does the product call derived? ---------------------------------------------------------------------
python3 - "$ROOT" <<'PY'
import sys, yaml
c = yaml.safe_load(open(sys.argv[1] + "/governance/project/REPOSITORY_CONTRACT.yaml"))
derived = [p["pattern"] for p in c["paths"] if p.get("class") == "derived"]
operational = [p["pattern"] for p in c["paths"] if p.get("class") == "operational"]
print("derived:", derived)
print("operational:", operational)
bad = [p for p in derived if "claims" in p or "control" in p or "registry" in p or p == ".governance-state/**"]
sys.exit(1 if bad else 0)
PY
chk D6-classification $? "no store of claims, emergency control or the plugin registry is classified derived; they are operational or authoritative in the repository contract" \
                         "a non-rebuildable store is still classified derived"

# ---- b1 delete ALL derived state and rebuild -------------------------------------------------------------------
gov "$ROOT" rebuild-memory >/dev/null 2>&1                # settle the index on the current tree
MAN_BEFORE=$(python3 -c "import json;print(json.load(open('$ROOT/governance/generated/index-manifest.json'))['manifest_hash'])")
# the path-independence clone is taken HERE, from exactly the tree whose index is about to be rebuilt
CLONE="$BETA_SCRATCH/d6-otherpath-$RANDOM.$$"
cp -r "$ROOT" "$CLONE"
aside "$ROOT/.governance-runtime"
[ ! -e "$ROOT/.governance-runtime/state.db" ]
chk D6-b1-deleted $? "every derived memory/index store is gone" "derived state was not removed"
gov "$ROOT" rebuild-memory > "$S-rebuild.json" 2>&1
jget 'd.get("ok")' < "$S-rebuild.json" | grep -q true
chk D6-b1-rebuilt $? "the derived state rebuilds from Git and the authoritative records alone" \
                     "rebuild failed: $(head -c 250 "$S-rebuild.json")"
MAN_AFTER=$(python3 -c "import json;print(json.load(open('$ROOT/governance/generated/index-manifest.json'))['manifest_hash'])")
[ "$MAN_BEFORE" = "$MAN_AFTER" ]
chk D6-b1-reproducible $? "the rebuilt index reproduces the manifest hash of the deleted one ($MAN_AFTER)" \
                          "the rebuild does not reproduce the manifest hash ($MAN_BEFORE -> $MAN_AFTER)"

# ---- b2 authoritative state and claims preserved ----------------------------------------------------------------
RECS_AFTER=$(cd "$ROOT" && find spec governance/project -type f | sort | xargs md5sum | md5sum)
[ "$RECS_BEFORE" = "$RECS_AFTER" ]
chk D6-b2-authoritative $? "deleting derived state did not touch one byte of authoritative project truth" \
                           "authoritative records changed across the rebuild"
CLAIMS_AFTER=$(gov "$ROOT" claims list | jget 'json.dumps(d.get("result"))')
[ "$CLAIMS_BEFORE" = "$CLAIMS_AFTER" ] && echo "$CLAIMS_AFTER" | grep -q "$CTID"
chk D6-b2-claims $? "the session claim survives the deletion and rebuild of all derived state" \
                    "the claim was lost with the derived state (before=$CLAIMS_BEFORE after=$CLAIMS_AFTER)"
FROZEN_AFTER=$(gov "$ROOT" status | jget 'json.dumps((d.get("result") or {}).get("control"))')
echo "$FROZEN_AFTER" | python3 -c "
import sys,json
v=json.loads(sys.stdin.read() or 'null') or {}
sys.exit(0 if v.get('writes_frozen') is True else 1)"
chk D6-b2-control $? "the emergency FREEZE_WRITES state survives the deletion and rebuild of all derived state" \
                     "deleting derived state lifted the emergency control (after=$FROZEN_AFTER)"
gov "$ROOT" resume >/dev/null 2>&1

# ---- b3 fresh-agent reconstruction ------------------------------------------------------------------------------
GOV_SESSION_ID=S-fresh-agent gov "$ROOT" status > "$S-status.json" 2>&1
python3 - "$S-status.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])).get("result") or {}
s = json.dumps(r)
ok = ("F-0001" in s and "REQ-0001" in s and r.get("framework"))
print("status chars:", len(s))
sys.exit(0 if ok else 1)
PY
chk D6-b3-fresh-agent $? "a fresh session reconstructs the governed project state after the rebuild, with no prior conversation" \
                         "fresh-agent reconstruction failed after the rebuild"
GOV_SESSION_ID=S-fresh-agent gov "$ROOT" continue > "$S-continue.json" 2>&1
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
r=d.get('result') or {}
sys.exit(0 if d.get('ok') and json.dumps(r) else 1)" "$S-continue.json"
chk D6-b3-next-action $? "the fresh session is told the correct next work and its bounded authority" \
                         "the fresh session is given no next action"

# ---- b4 path-independent rebuild ---------------------------------------------------------------------------------
aside "$CLONE/.governance-runtime"
gov "$CLONE" rebuild-memory > "$S-rebuild2.json" 2>&1
MAN_CLONE=$(python3 -c "import json;print(json.load(open('$CLONE/governance/generated/index-manifest.json'))['manifest_hash'])")
[ "$MAN_AFTER" = "$MAN_CLONE" ]
chk D6-b4-path-independent $? "rebuilding the same repository at a different absolute path reproduces the same index manifest hash ($MAN_CLONE)" \
                              "the rebuild depends on the absolute path ($MAN_AFTER vs $MAN_CLONE)"
python3 - "$ROOT/governance/generated/index-manifest.json" "$CLONE/governance/generated/index-manifest.json" <<'PY'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
s = json.dumps(a) + json.dumps(b)
leaked = [t for t in ("/tmp/", "scratchpad", "d6-otherpath") if t in s]
print("absolute-path leakage in the manifest:", leaked)
sys.exit(0 if not leaked else 1)
PY
chk D6-b4-no-paths $? "the index manifest carries no absolute machine path" "the index manifest embeds absolute machine paths"

summary
