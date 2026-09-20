#!/usr/bin/env bash
# D1 — incremental indexing / freshness (Contract v3:307-313), including the iteration-0 mechanisms of BC-P2-29
# (stale edges owned by unchanged files; a path-map reclassification never reaching unchanged files while freshness
# still reports fresh) and of BC-P2-03 (green memory/index evidence not invalidated by the inputs that change it).
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus d1); gov "$ROOT" init --name d1probe >/dev/null 2>&1
S=$BETA_SCRATCH/d1
DB="$ROOT/.governance-runtime/state.db"
sq() { python3 -c "
import sqlite3,sys
c=sqlite3.connect(sys.argv[1])
print('|'.join(str(x) for r in c.execute(sys.argv[2]) for x in r))" "$DB" "$1"; }
fresh() { gov "$ROOT" memory freshness > "$S-fresh.json" 2>&1; jget 'json.dumps(d.get("result") or d.get("error",{}).get("details",{}))' < "$S-fresh.json"; }

# ---- b1 content-hash / repo-commit invalidation ------------------------------------------------------------------
echo "# appended by the D1 probe" >> "$ROOT/src/app/orders.py"
F=$(fresh)
echo "$F" | python3 -c "
import sys,json;r=json.loads(sys.stdin.read())
sys.exit(0 if r.get('fresh') is False and any('orders.py' in s for s in r.get('stale',[])) else 1)"
chk D1-b1-content-hash $? "an edited file is reported stale by content hash before any rebuild" "an edited file is still reported fresh"

gov "$ROOT" rebuild-memory --incremental >/dev/null 2>&1
echo "$(fresh)" | python3 -c "
import sys,json;r=json.loads(sys.stdin.read()); sys.exit(0 if r.get('fresh') else 1)"
chk D1-b1-restored $? "after an incremental rebuild the index is fresh again" "the index is still stale after an incremental rebuild"

# ---- b2 changed artefacts invalidate affected chunks / symbols / nodes --------------------------------------------
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/src/app/orders.py"
s = open(p).read().replace("def find_by_sku(self, sku):", "def find_by_barcode(self, barcode):")
s = s.replace("pyfindbysku_marker_0042", "pyfindbybarcode_marker_9099")
open(p, "w").write(s)
PY
gov "$ROOT" rebuild-memory --incremental >/dev/null 2>&1
[ -z "$(sq "select name from symbols where qualname='OrderRepository.find_by_sku'")" ] && \
[ -n "$(sq "select name from symbols where qualname='OrderRepository.find_by_barcode'")" ] && \
[ -z "$(sq "select chunk_id from chunks where text like '%pyfindbysku_marker_0042%'")" ] && \
[ -n "$(sq "select chunk_id from chunks where text like '%pyfindbybarcode_marker_9099%'")" ]
chk D1-b2-affected $? "renaming a method inside a changed file removes the old symbol and chunk and adds the new ones" \
                      "stale symbols or chunks survive an incremental rebuild of the changed file"

# ---- BC-P2-29: an edge OWNED BY AN UNCHANGED FILE whose target disappears -----------------------------------------
# src/web/client.ts imports src/web/http.ts. Remove http.ts without touching client.ts and rebuild incrementally.
[ -n "$(sq "select src from edges where type='IMPORTS' and src='file:src/web/client.ts'")" ] || \
  fail D1-precondition "the IMPORTS edge under test does not exist"
aside "$ROOT/src/web/http.ts"
gov "$ROOT" rebuild-memory --incremental > "$S-inc.json" 2>&1
LEFT=$(sq "select dst from edges where type='IMPORTS' and src='file:src/web/client.ts'")
gov "$ROOT" memory integrity > "$S-int.json" 2>&1
DANG=$(jget 'json.dumps((d.get("result") or {}).get("counts",{}).get("dangling",0))' < "$S-int.json")
if [ -z "$LEFT" ] || [ "$DANG" != "0" ]; then
  pass D1-b2-stale-edges "an edge owned by an unchanged file is either removed or reported dangling after its target is deleted (remaining=[$LEFT], dangling=$DANG)"
else
  fail D1-b2-stale-edges "the edge file:src/web/client.ts -IMPORTS-> $LEFT survives its target's deletion and is not reported dangling"
fi

# ---- b3 rename / move / delete+add --------------------------------------------------------------------------------
( cd "$ROOT" && git add -A && git commit -q -m pre-rename && git mv src/app/base.py src/app/bases.py ) >/dev/null 2>&1
gov "$ROOT" rebuild-memory --incremental >/dev/null 2>&1
[ -z "$(sq "select path from artifacts where path='src/app/base.py'")" ] && \
[ -n "$(sq "select path from artifacts where path='src/app/bases.py'")" ] && \
[ "$(sq "select count(*) from artifacts where path like 'src/app/base%'")" = "1" ]
chk D1-b3-rename $? "a renamed file is not duplicated: the old path is gone and only the new one is indexed" \
                    "a rename left the old path indexed or duplicated the artefact"

# ---- b4 embedder / dimension change invalidates incompatible semantic state ---------------------------------------
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
t = open(p).read().replace("policy_overrides: {}", "policy_overrides:\n  MEMORY_POLICY.embedding.dimensions: 128")
open(p, "w").write(t)
PY
echo "$(fresh)" | python3 -c "
import sys,json;r=json.loads(sys.stdin.read())
sys.exit(0 if r.get('fresh') is False and r.get('pin_mismatch') else 1)"
chk D1-b4-embedder $? "changing the embedding dimension makes the live index incompatible (pin mismatch), not merely out of date" \
                      "an embedder/dimension change left the index reported fresh"
gov "$ROOT" memory query "integer cents" --k 3 > "$S-q.json" 2>&1
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
r=d.get('result') or {}
# either the query refuses, or it must not answer from vectors of the incompatible profile
hits=[h for h in r.get('hits',[]) if 'semantic' in h.get('routes',[])]
sys.exit(0 if (not d.get('ok')) or not hits else 1)" "$S-q.json"
chk D1-b4-no-mixed $? "an incompatible semantic state is not silently queried under the new pin" \
                      "semantic hits are still served from vectors built under the previous embedder pin"
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/PROJECT_POLICY.yaml"
t = open(p).read()
i, j = t.index("policy_overrides:"), t.index("staleness:")
open(p, "w").write(t[:i] + "policy_overrides: {}\n" + t[j:])
PY
gov "$ROOT" rebuild-memory >/dev/null 2>&1

# ---- b5 index manifest records compatible component identity ------------------------------------------------------
python3 - "$ROOT/governance/generated/index-manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
emb = m["embedder"]
ok = (emb.get("identity") and emb.get("adapter") and emb.get("model") and emb.get("runtime")
      and m.get("chunking", {}).get("chunker") and m.get("lexical", {}).get("tokenizer")
      and m.get("index_version") and m.get("repo_commit") and m.get("manifest_hash"))
print("components:", sorted(m.get("components", {}).keys()) or "(none)")
sys.exit(0 if ok else 1)
PY
chk D1-b5-manifest $? "the index manifest records the embedder's adapter/model/runtime identity, the chunker, the lexical tokenizer, the index version and the repository commit" \
                      "the index manifest does not record compatible component identity"

# ---- BC-P2-29: a path-map reclassification must reach UNCHANGED files ----------------------------------------------
# Reclassify src/** as historical/archive namespace without touching a single source file.
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/REPOSITORY_CONTRACT.yaml"
t = open(p).read().replace(
    "- pattern: src/**\n  class: source\n  owner_role: backend-engineer\n  semantic_index: true\n  lexical_index: true\n  graph_index: true\n  code_index: true\n  namespace: product",
    "- pattern: src/**\n  class: historical\n  owner_role: backend-engineer\n  semantic_index: false\n  lexical_index: true\n  graph_index: false\n  code_index: false\n  default_retrieval: false\n  namespace: archive")
open(p, "w").write(t)
PY
FR=$(fresh)
echo "$FR" | python3 -c "
import sys,json;r=json.loads(sys.stdin.read())
sys.exit(0 if r.get('fresh') is False or r.get('reclassified') else 1)"
chk D1-reclass-detected $? "a path-map reclassification of unchanged files is detected by freshness (reclassified=$(echo "$FR" | python3 -c 'import sys,json;print(json.loads(sys.stdin.read()).get("reclassified"))'))" \
                           "freshness still reports fresh after the path map reclassified unchanged files"
gov "$ROOT" rebuild-memory --incremental >/dev/null 2>&1
NS=$(sq "select distinct namespace from artifacts where path like 'src/%'")
DR=$(sq "select distinct default_retrieval from artifacts where path like 'src/%'")
[ "$NS" = "archive" ] && [ "$DR" = "0" ]
chk D1-reclass-applied $? "an INCREMENTAL rebuild applies the reclassification to the unchanged files (namespace=$NS, default_retrieval=$DR)" \
                          "an incremental rebuild left unchanged files in their old class (namespace=$NS, default_retrieval=$DR): archive is still indexed as current"
gov "$ROOT" memory query "pyfindbybarcode_marker_9099" --k 5 > "$S-arch.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1])).get('result') or {}
sys.exit(0 if not any(h['path'].startswith('src/') for h in r.get('hits',[])) else 1)" "$S-arch.json"
chk D1-reclass-retrieval $? "after the reclassification the archived source is out of default retrieval" \
                            "reclassified-as-archive source is still returned by default retrieval"

summary
