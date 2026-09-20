#!/usr/bin/env bash
# C9 — working memory / context packet (Contract v3:285-292).
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus c9); gov "$ROOT" init --name c9probe >/dev/null 2>&1
S=$BETA_SCRATCH/c9

TID=$(gov "$ROOT" task create --class implementation --objective "implement exact ledger totals" --feature F-0001 \
      --status READY --allowed 'src/**' \
      --fields '{"requirements":["REQ-0001"],"decisions":["D-0001"],"interfaces":["API-0001"],"scenarios":["SCN-0001"],"role":"backend-engineer","required_inputs":[{"id":"RES-0100","required":true,"reason":"benchmark evidence"}]}' \
      | jget 'd["result"]["id"]')
gov "$ROOT" context compile "$TID" > "$S-p1.json" 2>&1
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
sys.exit(0 if d.get('ok') else 1)" "$S-p1.json" || { fail C9-compile "context compile failed: $(head -c 300 "$S-p1.json")"; summary; exit 1; }

# b2 deterministic authority block, carrying the normative CONTENT (not only ids) and a content hash per input
python3 - "$S-p1.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
da = r["deterministic_authority"]
reqs = da["governing_requirements"]; decs = da["active_decisions"]; ifaces = da["interfaces"]
ok = (reqs and decs and ifaces
      and all(x.get("content") and x.get("content_hash") for x in reqs + decs + ifaces)
      and any("NEEDLEACCEPT4417" in json.dumps(x["content"]) for x in reqs)
      and any("NEEDLEOPTION8823" in json.dumps(x["content"]) for x in decs)
      and any("NEEDLEIFACE9034" in json.dumps(x["content"]) for x in ifaces))
print("requirements:", len(reqs), "decisions:", len(decs), "interfaces:", len(ifaces))
sys.exit(0 if ok else 1)
PY
chk C9-b2-authority $? "the deterministic authority block delivers each governing record's full normative content with its content hash, not a field whitelist of ids" \
                       "the deterministic block does not carry the normative statements of its inputs"

# b1 reproducible: the same inputs recompile to the same deterministic hash; a changed normative statement changes it
gov "$ROOT" context compile "$TID" > "$S-p2.json" 2>&1
H1=$(jget 'd["result"]["deterministic_hash"]' < "$S-p1.json"); H2=$(jget 'd["result"]["deterministic_hash"]' < "$S-p2.json")
[ "$H1" = "$H2" ] && [ -n "$H1" ]
chk C9-b1-reproducible $? "recompiling the same task reproduces the same deterministic hash ($H1)" "the deterministic block is not reproducible"

sed -i 's/rounding is prohibited at every step/rounding is prohibited except at the final boundary/' "$ROOT/spec/requirements/REQ-0001.yaml"
gov "$ROOT" rebuild-memory --incremental >/dev/null 2>&1
gov "$ROOT" context compile "$TID" > "$S-p3.json" 2>&1
H3=$(jget 'd["result"]["deterministic_hash"]' < "$S-p3.json")
[ "$H3" != "$H1" ] && [ -n "$H3" ]
chk C9-b1-sensitive $? "changing one word of a governing requirement's normative text changes the deterministic hash ($H1 -> $H3)" \
                       "the deterministic hash is insensitive to the normative text it delivers"

# b3 retrieved supplementary intelligence, separated from the authority block
python3 - "$S-p3.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
ri = r["retrieved_intelligence"]
need = ["query", "retrieval_strategy", "index_snapshot", "ranked_evidence", "semantic_candidates",
        "lessons_failures", "code_references", "declared_supplementary"]
missing = [k for k in need if k not in ri]
print("missing supplementary fields:", missing)
sys.exit(0 if not missing and r["supplementary_state"] else 1)
PY
chk C9-b3-supplementary $? "the packet carries every CONTEXT_POLICY retrieved field (including semantic_candidates) in a block separate from the authority block" \
                           "supplementary intelligence fields are missing"

# b4 bounded size
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
b=r['budget']
sys.exit(0 if r['chars'] <= b['max_packet_chars'] and 'over_budget' in b else 1)" "$S-p3.json"
chk C9-b4-bounded $? "the packet is bounded by CONTEXT_POLICY.max_packet_chars and reports its budget" "the packet is unbounded"

# b5 provenance / citations
python3 - "$S-p3.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
prov = r["provenance"]; ri = r["retrieved_intelligence"]
cited = all(("path" in e or "artifact_id" in e) for e in ri.get("ranked_evidence", []))
ok = prov.get("repo_commit") and prov.get("compiler") and r.get("packet_hash") and cited
print("repo_commit:", bool(prov.get("repo_commit")), "ranked_evidence:", len(ri.get("ranked_evidence", [])))
sys.exit(0 if ok else 1)
PY
chk C9-b5-provenance $? "the packet records the repository commit, the compiler identity, its own hash, and cites the source of every retrieved slice" \
                        "the packet lacks provenance or citations"

# b6 duplicate suppression: a verbatim copy of an indexed file must not be delivered twice
cp "$ROOT/src/app/orders.py" "$ROOT/src/app/orders_copy.py"
commit_all "$ROOT" "verbatim copy"
gov "$ROOT" rebuild-memory >/dev/null 2>&1
gov "$ROOT" memory query "pyfindbysku_marker_0042" --k 8 > "$S-dup.json" 2>&1
python3 - "$S-dup.json" <<'PY'
import json, sys, hashlib
r = json.load(open(sys.argv[1]))["result"]
seen, dups = {}, []
for h in r["hits"]:
    k = hashlib.sha256(h["excerpt"].encode()).hexdigest()
    if k in seen: dups.append((seen[k], h["path"], h["section"]))
    seen[k] = h["path"]
print("suppressed:", r.get("duplicates_suppressed"), "delivered duplicates:", dups)
sys.exit(0 if not dups else 1)
PY
chk C9-b6-duplicates $? "byte-identical content from two different artefacts is not delivered twice" \
                        "the same text is delivered twice from two artefacts (per-artefact cap only)"

# b7 active vs historical separation
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/spec/decisions/D-0001.yaml"
s = open(p).read().replace("status: ACTIVE", "status: SUPERSEDED")
open(p, "w").write(s)
open(sys.argv[1] + "/spec/decisions/D-0900.yaml", "w").write(
    "id: D-0900\ntype: decision\ntitle: Current money decision\nstatus: ACTIVE\n"
    "decision: store money as integer cents\nsupersedes: [D-0001]\nrationale: exactness\n")
PY
commit_all "$ROOT" "supersede D-0001"
gov "$ROOT" rebuild-memory >/dev/null 2>&1
gov "$ROOT" context compile "$TID" > "$S-p4.json" 2>&1
python3 - "$S-p4.json" <<'PYX'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
da = r["deterministic_authority"]
active = json.dumps(da["active_decisions"])
conflicting = json.dumps(da.get("conflicting_decisions") or [])
# the superseded record must not be delivered as current authority ...
not_active = "D-0001" not in active
# ... it must be delivered explicitly as historical/conflicting, flagged as such ...
flagged = ("D-0001" in conflicting and "SUPERSEDED" in conflicting)
# ... the manifest must block on it and name the remedy ...
mf = json.dumps(r["input_manifest"])
blocked = (r["input_manifest"]["delivery_state"] == "BLOCKED" and "SUPERSEDED" in mf and "D-0900" in mf)
# ... and no retrieved slice may deliver its content as if it were current
slices = [e for e in r["retrieved_intelligence"].get("ranked_evidence", [])
          if e.get("artifact_id") == "D-0001" or "NEEDLEOPTION8823" in json.dumps(e.get("excerpt"))]
print("active-excluded:", not_active, "flagged-historical:", flagged, "manifest-blocked:", blocked,
      "superseded slices delivered:", len(slices))
sys.exit(0 if (not_active and flagged and blocked and not slices) else 1)
PYX
chk C9-b7-active-historical $? "a superseded decision is delivered in neither the authority block nor the retrieved slices of a current task" \
                               "superseded material reached a current task's packet"

summary
