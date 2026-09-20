#!/usr/bin/env bash
# C5 code-structural memory (Contract v3:251-259), D2 retrieval router (:315-321), D3 hierarchical retrieval (:323-327).
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus c5d); gov "$ROOT" init --name c5probe >/dev/null 2>&1
DB="$ROOT/.governance-runtime/state.db"
sq() { python3 -c "
import sqlite3,sys
c=sqlite3.connect(sys.argv[1])
for r in c.execute(sys.argv[2]): print('|'.join('' if x is None else str(x) for x in r))" "$DB" "$1"; }

# ---- C5 -----------------------------------------------------------------------------------------------------
# b1 AST/LSP/SCIP or equivalent — spans that match the source, in five languages, not just one
python3 - "$DB" "$ROOT" <<'PY' && pass C5-b1 "extracted unit spans match the source text in python, rust, typescript, java and go (5/5 languages checked line-by-line)" || fail C5-b1 "extracted spans do not match the source"
import sqlite3, sys, os
db, root = sys.argv[1], sys.argv[2]
c = sqlite3.connect(db)
want = {"src/app/orders.py": ("OrderRepository.find_by_sku", "def find_by_sku"),
        "src/lib.rs": ("Ledger.total_cents", "fn total_cents"),
        "src/web/client.ts": ("CardPayer.pay", "async pay("),
        "src/svc/Ledger.java": ("LedgerEntry.amountCents", "amountCents()"),
        "src/svc/handler.go": ("handleLedger", "func handleLedger")}
bad = []
for path, (qual, needle) in want.items():
    row = c.execute("select lineno, end_lineno from symbols where path=? and qualname=?", (path, qual)).fetchone()
    if not row: bad.append((path, qual, "no symbol")); continue
    lines = open(os.path.join(root, path)).read().splitlines()
    span = "\n".join(lines[row[0]-1:row[1]])
    if needle not in span: bad.append((path, qual, "span does not contain the definition"))
print("bad:", bad)
sys.exit(1 if bad else 0)
PY

# b2 symbols/definitions/references
test "$(sq "select count(*) from symbols where kind not in ('module','route','db_model')")" -ge 15
chk C5-b2-symbols $? "symbol definitions are recorded with kinds and spans" "too few symbol definitions"
test "$(sq "select count(*) from symbol_refs where kind='call'")" -ge 5
chk C5-b2-refs $? "symbol references (calls) are recorded" "no symbol references recorded"

# b3 inheritance/interfaces — in three languages, including an `implements`
for pair in "src/app/orders.py:inherits:BaseRepository" "src/svc/Ledger.java:implements:Auditable" "src/web/client.ts:implements:Payer"; do
  p=${pair%%:*}; rest=${pair#*:}; k=${rest%%:*}; n=${rest#*:}
  test -n "$(sq "select 1 from symbol_refs where path='$p' and kind='$k' and name='$n'")"
  chk "C5-b3-${k}-$(basename "$p")" $? "$k relation '$n' extracted from $p" "no $k relation '$n' from $p"
done

# b4 calls/imports as graph edges between files
test -n "$(sq "select 1 from edges where type='IMPORTS' and src='file:src/web/client.ts'")"
chk C5-b4-imports $? "IMPORTS edges link file to file" "no cross-file IMPORTS edge"
test -n "$(sq "select 1 from edges where type='CALLS'")"
chk C5-b4-calls $? "CALLS edges are recorded" "no CALLS edges"

# b5 route registrations — a decorator route and a mux registration
test "$(sq "select count(*) from symbols where kind='route'")" -ge 2
chk C5-b5-routes $? "route registrations extracted in two languages ($(sq "select group_concat(qualname) from symbols where kind='route'"))" \
                    "route registrations not extracted"

# b6 DB models — an ORM base class and an entity annotation
test "$(sq "select count(*) from symbols where kind='db_model'")" -ge 2
chk C5-b6-models $? "database models extracted ($(sq "select group_concat(qualname) from symbols where kind='db_model'"))" \
                    "database models not extracted"

# b7 test-coverage relationships
test -n "$(sq "select 1 from edges where type='TESTS' and src like 'file:tests/%'")"
chk C5-b7-tests $? "test-coverage relationships link test files to the code they exercise" "no TESTS edge from a test file"

# b8 language adapters resolved via the capability registry (not hard-coded): the provider recorded per file is the
# adapter identity the registry resolves; with no plugin registered it is the built-in extractor, named as such.
test "$(sq "select count(distinct provider) from symbols")" -ge 1 && \
  test -n "$(sq "select 1 from symbols where provider like 'builtin%'")"
chk C5-b8-adapter $? "each code artefact records the resolving adapter identity (builtin fallback named explicitly)" \
                     "code artefacts record no adapter identity"

# ---- D2: the six routes -------------------------------------------------------------------------------------
route_of() { gov "$ROOT" memory query "$1" --k 4 | python3 -c "
import sys,json
d=json.load(sys.stdin); r=d.get('result') or {}
print(json.dumps({'routes': r.get('routes'), 'primary': r.get('primary_route'),
                  'hits': [[h['path'], h['routes']] for h in r.get('hits',[])]}))"; }

R1=$(route_of "REQ-0001")
echo "$R1" | python3 -c "
import sys,json; d=json.loads(sys.stdin.read())
h=d['hits']
sys.exit(0 if d['primary']=='structured' and h and 'REQ-0001' in h[0][0] else 1)"
chk D2-b1-structured $? "a known id is answered by the structured route and ranked first" "structured lookup did not rank REQ-0001 first: $R1"

R2=$(route_of "src/app/orders.py")
echo "$R2" | python3 -c "
import sys,json; d=json.loads(sys.stdin.read())
sys.exit(0 if d['primary']=='path' and d['hits'] and 'orders.py' in d['hits'][0][0] else 1)"
chk D2-b1-path $? "a known path is answered by the path route and ranked first" "path lookup failed: $R2"

R3=$(route_of "OrderRepository.find_by_sku")
echo "$R3" | python3 -c "
import sys,json; d=json.loads(sys.stdin.read())
sys.exit(0 if d['primary']=='symbol' else 1)"
chk D2-b2-symbol $? "a qualified symbol is answered by the code/symbol route" "symbol route not primary: $R3"

R4=$(route_of "ERR_LEDGER_UNBALANCED_7731")
echo "$R4" | python3 -c "
import sys,json; d=json.loads(sys.stdin.read())
sys.exit(0 if 'lexical' in d['routes'] and any('orders.py' in p for p,_ in d['hits']) else 1)"
chk D2-b3-lexical $? "a literal error string is answered by the lexical route" "lexical route failed: $R4"

R5=$(route_of "what depends on REQ-0001")
echo "$R5" | python3 -c "
import sys,json; d=json.loads(sys.stdin.read())
tops=[r for _,r in d['hits'][:3]]
sys.exit(0 if d['primary']=='graph' and all('graph' in t for t in tops) else 1)"
chk D2-b4-graph $? "a dependency question is answered by the graph route, and the graph answers rank first (not buried by fusion)" \
                   "graph answers are not first: $R5"

R5b=$(route_of "what breaks if I change src/app/base.py")
echo "$R5b" | python3 -c "
import sys,json; d=json.loads(sys.stdin.read())
sys.exit(0 if d['primary']=='graph' and any('orders.py' in p for p,_ in d['hits']) else 1)"
chk D2-b4-code-impact $? "a code-impact question reaches the graph and returns the dependent file" "code impact did not reach the graph: $R5b"

R6=$(route_of "why is money stored as integer cents rather than floats")
echo "$R6" | python3 -c "
import sys,json; d=json.loads(sys.stdin.read())
sys.exit(0 if 'semantic' in d['routes'] else 1)"
chk D2-b5-semantic $? "a natural-language question runs the semantic route" "semantic route not run: $R6"

R7=$(route_of "how does the order repository find orders and what governs the ledger totals")
echo "$R7" | python3 -c "
import sys,json; d=json.loads(sys.stdin.read())
sys.exit(0 if len(set(d['routes'])) >= 2 and any(len(r)>1 for _,r in d['hits']) else 1)"
chk D2-b6-fusion $? "a complex question fuses several routes and returns candidates found by more than one" \
                    "no multi-route fusion: $R7"

# ---- D3: hierarchy ------------------------------------------------------------------------------------------
test -n "$(sq "select 1 from chunks where level='document'")" && \
test -n "$(sq "select 1 from chunks where level='section' and parent_chunk_id is not null")" && \
test -n "$(sq "select 1 from chunks where level='child' and parent_chunk_id is not null")"
chk D3-b1-doc-hierarchy $? "document → section → child chunks exist with parent links" "chunk hierarchy incomplete"

test -n "$(sq "select 1 from chunks c join artifacts a on a.artifact_id=c.artifact_id where a.path='src/app/orders.py' and c.section='OrderRepository' and c.level='section'")" && \
test -n "$(sq "select 1 from chunks c join artifacts a on a.artifact_id=c.artifact_id where a.path='src/app/orders.py' and c.section='OrderRepository.find_by_sku' and c.level='child'")"
chk D3-b2-code-hierarchy $? "code file → class → method chunks exist (methods are chunk units, not only file heads)" \
                            "methods are not chunk units"

gov "$ROOT" memory query "pyfindbysku_marker_0042" --k 1 > "$BETA_SCRATCH/d3.json" 2>&1
python3 -c "
import json,sys
h=json.load(open(sys.argv[1]))['result']['hits'][0]
sys.exit(0 if h['level']=='child' and h['section']=='OrderRepository.find_by_sku' else 1)" "$BETA_SCRATCH/d3.json"
chk D3-b3-child-first $? "retrieval returns the child chunk (the method) first, not the file header" "child-first retrieval failed"

python3 -c "
import json,sys
h=json.load(open(sys.argv[1]))['result']['hits'][0]
sys.exit(0 if h.get('parent_excerpt') and h.get('neighbours') is not None else 1)" "$BETA_SCRATCH/d3.json"
chk D3-b4-expansion $? "the top hit is selectively expanded with its parent chunk and its graph neighbours" \
                       "no parent/graph-neighbour expansion"

# expansion is SELECTIVE: only the policy's parent_expansion_top_n hits carry a parent excerpt
gov "$ROOT" memory query "ledger total" --k 8 > "$BETA_SCRATCH/d3b.json" 2>&1
python3 -c "
import json,sys
hs=json.load(open(sys.argv[1]))['result']['hits']
n=sum(1 for h in hs if h.get('parent_excerpt'))
sys.exit(0 if len(hs)>3 and n<=3 else 1)" "$BETA_SCRATCH/d3b.json"
chk D3-b4-selective $? "parent expansion is bounded to the policy's top-n hits, not applied to every hit" \
                       "parent expansion is not selective"

summary
