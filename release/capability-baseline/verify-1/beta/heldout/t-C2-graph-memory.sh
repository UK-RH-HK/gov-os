#!/usr/bin/env bash
# C2 — relationship/graph memory (Contract v3:230-232):
#   b1 typed relationships support the twenty listed types (or equivalent)
#   b2 graph integrity checks detect orphan / stale / reversed / invalid relationships
#   b3 impact traversal is executable
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus c2); gov "$ROOT" init --name c2probe >/dev/null 2>&1

# ---- b1: every one of the twenty types is storable and readable back through the graph -------------------------
# One record declares every type explicitly, so nothing depends on which convenience field happens to map to it.
cat > "$ROOT/spec/requirements/REQ-0090.yaml" <<'Y'
id: REQ-0090
type: requirement
title: Edge-type carrier
status: ACTIVE
kind: functional
relations:
  - {type: DEPENDS_ON, target: REQ-0001}
  - {type: BLOCKS, target: SCN-0001}
  - {type: IMPLEMENTS, target: F-0001}
  - {type: REALISES, target: F-0001}
  - {type: GOVERNED_BY, target: D-0001}
  - {type: CONSTRAINS, target: TST-0001}
  - {type: DERIVED_FROM, target: L-0001}
  - {type: SUPERSEDES, target: API-0001}
  - {type: VALIDATED_BY, target: TST-0001}
  - {type: TESTS, target: SCN-0001}
  - {type: USES, target: API-0001}
  - {type: PRODUCES, target: REL-0001}
  - {type: CONSUMES, target: PRJ-0001}
  - {type: AFFECTS, target: REL-0001}
  - {type: GENERATED_FROM, target: PRJ-0001}
  - {type: CALLS, target: 'file:src/app/orders.py'}
  - {type: IMPORTS, target: 'file:src/app/base.py'}
  - {type: OWNS, target: 'file:src/web/http.ts'}
  - {type: FAILED_BECAUSE, target: L-0001}
  - {type: LEARNED_FROM, target: L-0001}
Y
gov "$ROOT" rebuild-memory >/dev/null 2>&1
DB="$ROOT/.governance-runtime/state.db"
MISS=$(python3 - "$DB" <<'PY'
import sqlite3, sys
want = ["DEPENDS_ON","BLOCKS","IMPLEMENTS","REALISES","GOVERNED_BY","CONSTRAINS","DERIVED_FROM","SUPERSEDES",
        "VALIDATED_BY","TESTS","USES","PRODUCES","CONSUMES","AFFECTS","GENERATED_FROM","CALLS","IMPORTS","OWNS",
        "FAILED_BECAUSE","LEARNED_FROM"]
inv = {"CONSUMED_BY":"CONSUMES","PRODUCED_BY":"PRODUCES","BLOCKED_BY":"BLOCKS","SUPERSEDED_BY":"SUPERSEDES"}
c = sqlite3.connect(sys.argv[1])
have = set()
for (t,) in c.execute("select distinct type from edges"):
    have.add(inv.get(t, t))
print(",".join(w for w in want if w not in have))
PY
)
if [ -z "$MISS" ]; then pass C2-b1 "all twenty contract relationship types are stored and read back as typed edges"
else fail C2-b1 "relationship types not representable as edges: $MISS"; fi

# ---- b2: integrity detects orphan / stale / reversed / invalid ---------------------------------------------------
cat > "$ROOT/spec/requirements/REQ-0091.yaml" <<'Y'
id: REQ-0091
type: requirement
title: Orphan requirement
status: ACTIVE
kind: functional
Y
cat > "$ROOT/spec/requirements/REQ-0092.yaml" <<'Y'
id: REQ-0092
type: requirement
title: Dangling reference
status: ACTIVE
kind: functional
feature: F-0001
governed_by: [D-9999]
Y
cat > "$ROOT/spec/decisions/D-0090.yaml" <<'Y'
id: D-0090
type: decision
title: Retired decision
status: SUPERSEDED
decision: old
Y
cat > "$ROOT/spec/requirements/REQ-0093.yaml" <<'Y'
id: REQ-0093
type: requirement
title: In-force reference to a superseded decision
status: ACTIVE
kind: functional
feature: F-0001
governed_by: [D-0090]
Y
cat > "$ROOT/spec/decisions/D-0091.yaml" <<'Y'
id: D-0091
type: decision
title: Backwards and ill-typed edges
status: ACTIVE
decision: x
governed_by: [TST-0001]
tests: [REQ-0001]
Y
gov "$ROOT" rebuild-memory >/dev/null 2>&1
gov "$ROOT" memory integrity > "$BETA_SCRATCH/c2-integrity.json" 2>&1
for kind in orphan dangling stale reversed ill_typed; do
  python3 -c "
import json,sys
d=json.load(open(sys.argv[1])); r=d.get('result') or d.get('error',{}).get('details',{})
sys.exit(0 if (r.get('counts') or {}).get(sys.argv[2],0) > 0 else 1)" "$BETA_SCRATCH/c2-integrity.json" "$kind"
  chk "C2-b2-$kind" $? "graph integrity reports the planted $kind relationship" \
                       "graph integrity did not report the planted $kind relationship"
done

# ---- b3: impact traversal is executable -------------------------------------------------------------------------
gov "$ROOT" memory impact "REQ-0001" --depth 3 > "$BETA_SCRATCH/c2-impact.json" 2>&1
python3 -c "
import json,sys
d=json.load(open(sys.argv[1])); r=d.get('result') or {}
reach=json.dumps(r)
sys.exit(0 if d.get('ok') and 'F-0001' in reach else 1)" "$BETA_SCRATCH/c2-impact.json"
chk C2-b3-impact $? "gov memory impact traverses from REQ-0001 to the feature that depends on it" \
                    "impact traversal did not reach F-0001: $(head -c 250 "$BETA_SCRATCH/c2-impact.json")"

gov "$ROOT" artefact lineage REQ-0001 --direction up --depth 4 > "$BETA_SCRATCH/c2-lineage.json" 2>&1
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
sys.exit(0 if d.get('ok') and json.dumps(d['result']).count('-') > 0 else 1)" "$BETA_SCRATCH/c2-lineage.json"
chk C2-b3-lineage $? "reverse (upstream) lineage traversal executes over canonical edges" \
                     "reverse lineage did not execute"

summary
