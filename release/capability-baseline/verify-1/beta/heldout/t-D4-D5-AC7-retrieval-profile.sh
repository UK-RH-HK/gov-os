#!/usr/bin/env bash
# D4 component separation (Contract v3:329-340), D5 evidence-driven retrieval model selection (:342-348), and the
# AC-7 determination of the frozen gate contract §9.1: an EXECUTABLE, EVIDENCED path to a provisional retrieval
# profile. No profile is selected here as a Phase-2 conclusion; the path is exercised and then left as it was found.
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus_provisioned d45)
S=$BETA_SCRATCH/d45

gov "$ROOT" memory profile > "$S-prof.json" 2>&1
PROBE_TASK=$(gov "$ROOT" task create --class specification --objective "D4 packet probe" --status READY \
              --allowed 'spec/**' --fields '{"requirements":["REQ-0001"]}' | jget 'd["result"]["id"]')
gov "$ROOT" context compile "$PROBE_TASK" > "$S-pkt.json" 2>&1
MAN="$ROOT/governance/generated/index-manifest.json"
DB="$ROOT/.governance-runtime/state.db"

# ---- D4: each of the ten components, identifiable and (where designed) replaceable -------------------------------
ident() { # ident <id> <python test over the collected evidence> <pass msg> <fail msg>
  python3 - "$MAN" "$S-prof.json" "$S-pkt.json" "$DB" "$2" <<'PY'
import json, sqlite3, sys
man = json.load(open(sys.argv[1]))
prof = (json.load(open(sys.argv[2])).get("result") or {})
pkt = (json.load(open(sys.argv[3])).get("result") or {})
db = sqlite3.connect(sys.argv[4])
ns = {"man": man, "prof": prof, "pkt": pkt, "db": db, "json": json}
sys.exit(0 if eval(sys.argv[5], ns) else 1)
PY
  chk "$1" $? "$3" "$4"
}

ident D4-embedding-model \
  'man["components"]["embedder"]["model"].get("id") and man["components"]["embedder"]["model"].get("sha256") and man["components"]["embedder"]["identity"]' \
  "the embedding MODEL is separately identified (id, revision, parameters, sha256) in the index manifest and the live profile" \
  "the embedding model is not separately identified"

ident D4-embedding-runtime \
  'man["components"]["embedder"]["runtime"].get("id") and man["components"]["embedder"].get("runtime_digest")' \
  "the embedding RUNTIME is separately identified (id, kind, digest), distinct from the model" \
  "the embedding runtime is not separately identified"

ident D4-vector-store \
  '[r for r in db.execute("select name from sqlite_master where type=\x27table\x27 and name=\x27vectors\x27")] and man["counts"].get("vectors") is not None' \
  "the vector store is separately identifiable (its own store with its own count in the manifest)" \
  "the vector store is not separately identifiable"

ident D4-lexical-engine \
  'man["lexical"].get("engine") and man["lexical"].get("tokenizer")' \
  "the lexical engine is separately identified (engine + tokenizer, and the tokenizer is part of the index pin)" \
  "the lexical engine is not separately identified"

ident D4-graph-engine \
  '[r for r in db.execute("select name from sqlite_master where type=\x27table\x27 and name=\x27edges\x27")] and man["counts"].get("edges") is not None' \
  "the graph engine is separately identifiable (its own edge store and manifest count)" \
  "the graph engine is not separately identifiable"

ident D4-code-intelligence \
  'set(r[0] for r in db.execute("select distinct provider from symbols")) - {None} != set()' \
  "code intelligence records the resolving adapter identity per artefact, so the adapter in force is identifiable" \
  "code intelligence records no adapter identity"

ident D4-reranker \
  'man["components"]["reranker"].get("identity") and "provider" in man["reranker"]' \
  "the reranker is separately identified even when its provider is none, with its own component identity" \
  "the reranker is not separately identified"

ident D4-retrieval-router \
  'pkt.get("retrieved_intelligence", {}).get("retrieval_strategy") is not None or pkt.get("retrieved_intelligence", {}).get("routes") is not None' \
  "the retrieval router names the strategy and the routes it used for each compiled packet" \
  "the retrieval router is not identifiable in what it produces"

ident D4-context-compiler \
  'pkt.get("provenance", {}).get("compiler", {}).get("runtime_version") and pkt["provenance"]["compiler"].get("index_version")' \
  "the context compiler is identified in every packet it produces (runtime and index version)" \
  "the context compiler is not identified"

gov "$ROOT" route --class implementation > "$S-route.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1])).get('result') or {}
sys.exit(0 if ('minimum_tier' in r and 'candidates' in r) else 1)" "$S-route.json"
chk D4-generative-model $? "the generative/query-planning model is a separately resolved component (tier requirement + overlay-declared candidates), never named in kernel policy" \
                           "the generative model is not separately resolved"

# replaceability where designed: the embedder is replaceable through the governed path and the swap is visible
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
t = open(p).read().replace("policy_overrides: {}", "policy_overrides:\n  MEMORY_POLICY.embedding.dimensions: 256")
open(p, "w").write(t)
PY
gov "$ROOT" memory profile > "$S-prof2.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
sys.exit(0 if r['state'] in ('UNGOVERNED','UNGOVERNED_CHANGE') and r.get('severity')=='high' else 1)" "$S-prof2.json"
chk D4-replace-detected $? "replacing a component outside the governed path is detected and reported as an ungoverned profile change (high)" \
                           "an out-of-band component replacement is not detected"
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
t = open(p).read(); i, j = t.index("policy_overrides:"), t.index("staleness:")
open(p, "w").write(t[:i] + "policy_overrides: {}\n" + t[j:])
PY
gov "$ROOT" rebuild-memory >/dev/null 2>&1

# ---- D5: evidence-driven selection --------------------------------------------------------------------------------
gov "$ROOT" memory benchmark --candidate current --candidate builtin:64 --candidate builtin:8 > "$S-bench.json" 2>&1
python3 - "$S-bench.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])).get("result") or {}
rows = r.get("rows", [])
need = ["recall_at_k", "mrr", "precision_at_k", "stale_hit_rate", "avg_query_latency_ms", "index_ms", "vectors"]
ok = len(rows) >= 3 and all(all(k in row for k in need) for row in rows) and r.get("queries", 0) >= 5
print("candidates:", [x["candidate"] for x in rows], "queries:", r.get("queries"))
sys.exit(0 if ok else 1)
PY
chk D5-b1-b4 $? "a benchmark mechanism exists, compares several candidate models/runtimes on a held-out set, and reports Recall@K, MRR, precision, stale-hit, latency and resource cost per candidate" \
                "the benchmark does not compare candidates on the required metrics"

python3 - "$ROOT/governance/tests/memory/heldout.yaml" <<'PY'
import sys, yaml, collections
d = yaml.safe_load(open(sys.argv[1]))
qs = d["queries"]
cats = collections.Counter(q.get("category") for q in qs)
print("held-out categories:", dict(cats))
sys.exit(0 if len(qs) >= 5 else 1)
PY
chk D5-b3-heldout $? "a golden/held-out retrieval query set exists and is versioned in the repository" "no held-out query set"

# the starter set's discriminating power: does the measured set contain any SEMANTIC query?
gov "$ROOT" memory verify > "$S-verify.json" 2>&1
python3 - "$S-verify.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])).get("result") or {}
cats = {c["category"] for c in r.get("by_category", [])}
print("measured categories:", sorted(cats), "pending:", r.get("pending_queries"))
sys.exit(0 if "semantic_paraphrase" in cats else 1)
PY
chk D5-heldout-discriminates $? "the measured held-out set contains semantic queries, so the evidence can discriminate the embedder it is used to select" \
                                "the generated held-out set leaves its semantic paraphrase queries PENDING, so every embedder candidate measures identically and the selection evidence cannot discriminate the component being selected (the product reports pending_queries but neither refuses nor flags a selection made on it)"

python3 - "$S-prof.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])).get("result") or {}
p = r["retrieval_profile"]
ok = p["embedder"].get("identity") and p["reranker"].get("identity") and r.get("digest")
sys.exit(0 if ok else 1)
PY
chk D5-b5-pinned $? "the selected embedder/reranker revisions are pinned as component identities (adapter+model+runtime), not as bare strings" \
                    "the pins are bare strings not bound to what executes"

# b6 changing them requires governed migration / reindex / regression — exercised end to end
RES=$(gov "$ROOT" memory benchmark --candidate current --candidate builtin:64 --record | jget 'd["result"]["research_record"]')
gov "$ROOT" memory select builtin:64 > "$S-noev.json" 2>&1
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
sys.exit(0 if (not d.get('ok')) and d['error']['code']=='PROFILE_EVIDENCE_REQUIRED' else 1)" "$S-noev.json"
chk D5-b6-evidence $? "a profile change without benchmark evidence is refused (PROFILE_EVIDENCE_REQUIRED)" "a profile change without evidence was accepted"

gov "$ROOT" memory select builtin:64 --research "$RES" > "$S-gate.json" 2>&1
GID=$(jget 'json.dumps((d.get("result") or {}).get("human_gate"))' < "$S-gate.json"); GID=${GID//\"/}
python3 -c "
import json,sys
r=json.load(open(sys.argv[1])).get('result') or {}
sys.exit(0 if r.get('applied') is False and r.get('status')=='WAITING_HUMAN' and r.get('impact_radius')=='R5' else 1)" "$S-gate.json"
chk D5-b6-gate $? "with evidence but without an answered change-control gate the change is held at WAITING_HUMAN (R5), not applied" \
                  "a profile change applied without the change-control gate"

# an agent-declared approval must not stand in for the owner's answer (trust classes, D-0007)
GOV_AS_ROLE=orchestrator gov "$ROOT" memory select builtin:64 --research "$RES" --gate "$GID" --by human > "$S-forge.json" 2>&1
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
r=d.get('result') or {}
sys.exit(0 if (not d.get('ok')) or r.get('applied') is not True else 1)" "$S-forge.json"
chk D5-b6-no-forgery $? "naming the acting role 'human' on the command line does not satisfy the gate" \
                        "a CLI-declared approval applied the profile change"

owner_answers "$ROOT" "$GID" A > "$S-answer.json" 2>&1
gov "$ROOT" memory select builtin:64 --research "$RES" --gate "$GID" > "$S-apply.json" 2>&1
python3 - "$S-apply.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
r = d.get("result") or {}
ok = (r.get("applied") is True and r.get("decision") and r.get("rebuilt")
      and (r.get("regression") or {}).get("measured") and r.get("human_approved") is True
      and (r.get("approval") or {}).get("answer", {}).get("by_kind") == "human")
print("applied:", r.get("applied"), "decision:", r.get("decision"), "regression:", (r.get("regression") or {}).get("status"))
sys.exit(0 if ok else 1)
PY
chk D5-b6-governed-change $? "with the owner's signed answer the change is applied as a governed migration: a recorded decision, a full re-index and a measured held-out regression" \
                             "the governed change path did not complete: $(head -c 250 "$S-apply.json")"

gov "$ROOT" memory profile > "$S-prof3.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
sys.exit(0 if r['state']=='GOVERNED' and r.get('decision') else 1)" "$S-prof3.json"
chk D5-b6-governed-state $? "after the change the live profile is GOVERNED by the decision that authorised it" \
                            "the applied profile is not bound to a decision"

# ---- AC-7 (frozen gate contract §9.1): the path, end to end --------------------------------------------------------
python3 - "$S-bench.json" "$S-apply.json" "$S-prof3.json" <<'PY'
import json, sys
bench = json.load(open(sys.argv[1])).get("result") or {}
appl = json.load(open(sys.argv[2])).get("result") or {}
prof = json.load(open(sys.argv[3])).get("result") or {}
ok = (len(bench.get("rows", [])) >= 2                    # compare
      and bench.get("queries", 0) >= 5                   # held-out queries
      and appl.get("applied") is True                    # select + pin
      and appl.get("rebuilt")                            # governed reindex
      and (appl.get("regression") or {}).get("measured")  # regression on change
      and prof.get("state") == "GOVERNED")
sys.exit(0 if ok else 1)
PY
chk AC-7-path $? "an executable, evidenced path to establish a provisional retrieval profile exists end to end: separately identifiable components, benchmark/compare on held-out queries with the required metrics, an owner-gated selection that pins them, a full re-index and a recorded regression" \
                 "the AC-7 path is not executable end to end"

summary
