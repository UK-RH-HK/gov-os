"""C5 Code-structural memory (Contract v3 lines 251-259).

Multi-language synthetic repo (Python, TypeScript, Rust, Go). Each facet is checked against what the product actually
stores (symbols / symbol_refs / edges tables) and what an agent can ask for through `gov memory query`.
b1 AST/LSP/SCIP or equivalent: builtin generic extractor vs the shipped python-ast plugin wired through the registry,
   with a fidelity trap (a `class`/`def` line inside a string literal).
b8 language adapters via the capability registry: python-ast resolved for .py only, builtin for others, and a failing
   adapter degrades (recorded) rather than crashing.
"""
import json
import shutil
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from govprobe import *  # noqa
from synth import build_rich  # noqa

TRAP = '''"""Module whose docstring mentions code.

Example in prose:
class NotARealClass:
    pass
def not_a_real_function():
    pass
"""


def real_function(x):
    return x + 1
'''
root, g = build_rich("c5", extra_files={"src/app/trap.py": TRAP,
                                        "src/app/test_colocated.py": "from app.models import compute_total\n\n\ndef test_colocated():\n    assert compute_total(1, 1) == 1\n",
                                        "tests/format.test.ts": "import { formatCents } from \"../src/web/format\";\n\ntest(\"formats\", () => {\n  expect(formatCents(150)).toBe(\"1.50\");\n});\n"})
g.ok("rebuild-memory")


def syms(path_like):
    return q(root, "SELECT path, name, qualname, kind, lineno, end_lineno, parent, provider FROM symbols WHERE path LIKE ? ORDER BY path, lineno", (path_like,))


section("C5-b1 AST/LSP/SCIP or equivalent — builtin extractor")
for r in syms("src/%"):
    log("  ", r)
trap_builtin = [r[1] for r in syms("src/app/trap.py")]
log("builtin symbols in trap.py:", trap_builtin)
providers = sorted({r[0] for r in q(root, "SELECT DISTINCT provider FROM symbols")})
log("providers:", providers)

section("C5-b8 language-appropriate adapter via capability registry: shipped python-ast plugin")
dst = root / "tools/pyplug"
shutil.copytree(WT / "capabilities/python/govos_capabilities", dst / "govos_capabilities")
write(root, "governance/project/plugins/python-ast.yaml", yaml.safe_dump({
    "plugin_id": "python-ast", "capability": "code_intel", "version": "1.0.0", "languages": ["python"],
    "command": ["python3", "-m", "govos_capabilities.code_intel_python_ast"], "cwd": "tools/pyplug"}, sort_keys=False))
commit_all(root, "python-ast adapter")
cp = g.ok("capabilities", "plugins")
log("gov capabilities plugins:", [(x.get("plugin_id"), x.get("capability"), x.get("status"), x.get("languages")) for x in cp])
rb = g.ok("rebuild-memory")
log("rebuild degradations:", rb["degradations"])
prov = q(root, "SELECT path, provider, COUNT(*) FROM symbols WHERE path LIKE 'src/%' GROUP BY path, provider ORDER BY path")
log("provider per file:", prov)
trap_ast = [r[1] for r in syms("src/app/trap.py")]
log("python-ast symbols in trap.py:", trap_ast)
cap_meta = q(root, "SELECT value FROM meta WHERE key='capability.plugins'")
log("capability memory (meta capability.plugins):", cap_meta)
py_ast = {p for (_, p, _) in prov if _.endswith(".py")} if False else {r[1] for r in prov if r[0].endswith(".py")}
other = {r[1] for r in prov if not r[0].endswith(".py")}
check("C5-b1", "NotARealClass" in trap_builtin and "NotARealClass" not in trap_ast and "real_function" in trap_ast,
      "builtin extractor is heuristic (reads a class inside a docstring as a symbol); the AST adapter is exact for Python")
check("C5-b8", py_ast == {"python-ast"} and other == {"builtin-generic"},
      "python files resolved to the python-ast adapter through the plugin registry; other languages to the builtin")
# failing adapter degrades and is recorded
(dst / "govos_capabilities/code_intel_python_ast.py").write_text("import sys\nsys.exit(3)\n")
commit_all(root, "break adapter")
rb2 = g.run("rebuild-memory")
log("rebuild with a broken python adapter:", rb2.get("ok"), (rb2.get("error") or {}).get("code"), "degradations:", (rb2.get("result") or {}).get("degradations", [])[:3])
check("C5-b8-degrade", rb2.get("ok") and any("python-ast" in d for d in rb2["result"]["degradations"]),
      "a failing code_intel adapter degrades to the builtin and the degradation is recorded (D-0005)")
(root / "governance/project/plugins/python-ast.yaml").unlink()
shutil.rmtree(dst)
commit_all(root, "remove adapter")
g.ok("rebuild-memory")

section("C5-b2 symbols / definitions / references")
r = g.ok("memory", "query", "compute_total", "--k", "10")
hits = [(h["artifact_id"], h["section"], h["routes"]) for h in r["hits"]]
log("gov memory query compute_total ->", r["routes"], hits)
refs = q(root, "SELECT path, name, kind, target FROM symbol_refs WHERE name='compute_total'")
log("symbol_refs for compute_total:", refs)
defn = q(root, "SELECT path, qualname, kind, lineno, end_lineno, signature FROM symbols WHERE name='compute_total'")
log("definition rows:", defn)
check("C5-b2", defn and defn[0][3] == 24 and any(x[0] == "src/app/api.py" for x in refs)
      and any(h[0] == "file:src/app/api.py" for h in hits) and any(h[1] == "compute_total" for h in hits),
      "definitions (with line spans) and call references are stored and retrievable through the symbol route")

section("C5-b3 inheritance / interfaces")
ifaces = q(root, "SELECT path, name, kind FROM symbols WHERE kind IN ('interface','trait')")
log("interface/trait symbols:", ifaces)
inh_refs = q(root, "SELECT path, name, kind, target FROM symbol_refs WHERE kind NOT IN ('import','call')")
inh_edges = q(root, "SELECT src, type, dst FROM edges WHERE type NOT IN ('IMPORTS','CALLS','TESTS') AND src LIKE 'file:%'")
log("non-import/call symbol references (inheritance/implementation):", inh_refs)
log("code edges other than IMPORTS/CALLS/TESTS:", inh_edges)
for qq in ["what implements OrderRepository", "classes that extend SqlOrderRepository", "who implements trait Ledger", "subclasses of AuditedEntity"]:
    rr = g.ok("memory", "query", qq, "--k", "6", show=False)
    log(f"query {qq!r}: routes={rr['routes']} hits={[h['artifact_id'] + '#' + h['section'] for h in rr['hits']]}")
check("C5-b3-interfaces", len(ifaces) >= 2, "interface/trait declarations are captured as symbols")
check("C5-b3-inheritance", bool(inh_refs) or bool(inh_edges),
      "inheritance/implementation relationships (Order(Base, AuditedEntity); SqlOrderRepository implements OrderRepository; "
      "CachedOrderRepository extends SqlOrderRepository; impl Ledger for MemoryLedger) are represented")

section("C5-b4 calls / imports")
calls = q(root, "SELECT path, name, target FROM symbol_refs WHERE kind='call' AND path LIKE 'src/%' ORDER BY path")
imps = q(root, "SELECT path, name, target FROM symbol_refs WHERE kind='import' ORDER BY path")
edges = q(root, "SELECT src, type, dst FROM edges WHERE type IN ('CALLS','IMPORTS') ORDER BY type, src")
log("call refs:", calls)
log("import refs:", imps)
log("CALLS/IMPORTS edges:", edges)
unres = [i for i in imps if i[2].startswith("module:") and i[1].startswith("app.")]
log("first-party imports left unresolved (module:*):", unres)
check("C5-b4", ("file:src/app/api.py", "IMPORTS", "file:src/app/models.py") in edges and ("file:src/web/api.ts", "IMPORTS", "file:src/web/format.ts") in edges
      and ("file:src/app/api.py", "CALLS", "file:src/app/models.py") in edges, "calls and imports are extracted and materialised as CALLS/IMPORTS edges")

section("C5-b5 route registrations")
route_like = q(root, "SELECT path, name, kind FROM symbols WHERE kind LIKE '%route%' OR name LIKE '/%'")
route_refs = q(root, "SELECT path, name, kind, target FROM symbol_refs WHERE kind NOT IN ('import') AND (name LIKE '/%' OR kind LIKE '%route%')")
log("route symbols:", route_like, "route refs:", route_refs)
for qq in ["which handler serves GET /orders/<int:order_id>", "route registration for /ping", "routes registered in api.ts"]:
    rr = g.ok("memory", "query", qq, "--k", "5", show=False)
    log(f"query {qq!r}: routes={rr['routes']} hits={[h['artifact_id'] + '#' + h['section'] for h in rr['hits']]}")
check("C5-b5", bool(route_like) or bool(route_refs), "HTTP route registrations (Flask @app.route/@app.post, express router.get, Go http.HandleFunc) are represented structurally")

section("C5-b6 DB models")
dbm = q(root, "SELECT path, name, kind FROM symbols WHERE kind IN ('model','db_model','table','entity')")
log("DB-model symbols:", dbm)
log("Order symbol row:", q(root, "SELECT path, name, kind, signature FROM symbols WHERE name='Order'"))
rr = g.ok("memory", "query", "which model maps the orders table", "--k", "5", show=False)
log("query 'which model maps the orders table':", [h["artifact_id"] + "#" + h["section"] for h in rr["hits"]])
check("C5-b6", bool(dbm), "database models (SQLAlchemy `class Order(Base)` with __tablename__) are represented as DB models")

section("C5-b7 test-coverage relationships")
tests_e = q(root, "SELECT src, type, dst FROM edges WHERE type='TESTS' AND src LIKE 'file:%'")
log("file-level TESTS edges:", tests_e)
log("tests/test_models.py import refs:", q(root, "SELECT name, target FROM symbol_refs WHERE path='tests/test_models.py' AND kind='import'"))
log("src/app/test_colocated.py path class:", q(root, "SELECT path_class FROM artifacts WHERE path='src/app/test_colocated.py'"))
imp = g.ok("memory", "impact", "file:src/app/models.py", "--depth", "1", show=False)
log("impact of models.py:", [(x["node"], x["via"]) for x in imp])
check("C5-b7-tests-dir", ("file:tests/test_models.py", "TESTS", "file:src/app/models.py") in tests_e,
      "a test in tests/ exercising src/app/models.py yields a TESTS relationship")
check("C5-b7-relative", ("file:tests/format.test.ts", "TESTS", "file:src/web/format.ts") in tests_e,
      "a test whose import is a relative path (../src/web/format) yields a TESTS relationship")
summary()
