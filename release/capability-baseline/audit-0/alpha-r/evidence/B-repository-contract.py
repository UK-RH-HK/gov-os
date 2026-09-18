#!/usr/bin/env python3
"""B1 (standard repository contract), B2 bullet 1/5 on an initialised project (path classification from the contract),
B3 (authoritative vs derived state).

[K*] B1 boundaries explicit and enforced; native layout preserved and mapped without cosmetic refactoring;
     generated/runtime distinguished from authoritative tracked state
[P*] B2 every artefact of an initialised repo is classifiable (class/authority/namespace) by the machine contract
[D*] B3 records authoritative; indexes derived; deleting derived state cannot delete truth; derived provenance
Run: PROBE_TMP=<scratch> python3 B-repository-contract.py
"""
import os, sys, json, shutil, sqlite3, subprocess, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

native = {
    "README.md": "# native app\n",
    "pyproject.toml": "[project]\nname = 'nativeapp'\nversion = '0.1.0'\n",
    "src/nativeapp/__init__.py": "",
    "src/nativeapp/server.py": "from nativeapp.routes import register\n\ndef main():\n    return register()\n",
    "src/nativeapp/routes.py": "def register():\n    return ['/health']\n",
    "tests/test_server.py": "from nativeapp.server import main\n\ndef test_main():\n    assert main() == ['/health']\n",
    "web/package.json": '{"name": "web", "version": "1.0.0"}\n',
    "web/src/index.ts": "export const x = 1;\n",
}
sb = Sandbox("b")
p = sb.new_repo("native", native)
tree_before = {r: hashlib.sha256(open(os.path.join(p, r), "rb").read()).hexdigest() for r in native}
o = sb.gov("init", "--name", "native", "--alias", "nat", "--intent", "native layout probe", cwd=p, quiet=True)
print("## [K1] boundaries after gov init")
for d in ["governance/kernel", "governance/project", "governance/generated", "governance/framework.lock", ".governance-runtime", "spec", "archive", "product"]:
    print(f"[K1] {d:28s} exists={os.path.exists(os.path.join(p, d))}")
rc = yaml.safe_load(open(os.path.join(p, "governance/project/REPOSITORY_CONTRACT.yaml")))
for r in rc["paths"]:
    if r["pattern"].startswith(("governance/", ".governance-runtime", "src/", "tests/", "web/", "spec/**", "archive/")):
        print(f"[K1] contract rule {r['pattern']:28s} class={r.get('class'):14s} mutation={r.get('mutation', '-'):11s} owner={r.get('owner_role', '-')}")
print("[K1] .gitignore carries .governance-runtime/:", ".governance-runtime/" in open(os.path.join(p, ".gitignore")).read())
print("[K1] capability_roots:", rc.get("capability_roots"))

print("\n## [K2] native layout preserved / mapped, not refactored")
tree_after = {r: hashlib.sha256(open(os.path.join(p, r), "rb").read()).hexdigest() if os.path.exists(os.path.join(p, r)) else None for r in native}
print("[K2] every native file still at its path with identical bytes:", tree_after == tree_before)
print("[K2] git status of the native tree (excluding governance additions):", subprocess.run(["git", "status", "--porcelain", "--", "src", "tests", "web", "pyproject.toml"], cwd=p, capture_output=True, text=True).stdout.splitlines())
sb.gov("rebuild-memory", cwd=p, quiet=True)
db = sqlite3.connect(os.path.join(p, ".governance-runtime/state.db"))
rows = {r[0]: r[1:] for r in db.execute("SELECT path, path_class, namespace, sensitivity, code, default_retrieval FROM artifacts")}
for f in ["src/nativeapp/server.py", "tests/test_server.py", "web/src/index.ts", "pyproject.toml", "governance/kernel/KERNEL.yaml", "governance/project/PROJECT_POLICY.yaml", "spec/now/NOW.md"]:
    print(f"[K2]/[P1] {f:36s} -> (class, namespace, sensitivity, code_index, default_retrieval) = {rows.get(f)}")
syms = db.execute("SELECT name, kind, path FROM symbols WHERE path LIKE 'src/%' ORDER BY path, name").fetchall()
print("[K2] native code indexed in place (symbols):", syms[:6])
eco = sb.gov("capabilities", "ecosystems", cwd=p, quiet=True)["result"]
print("[K2] ecosystems detected over the native layout:", [(e.get("id"), e.get("dir")) for e in eco.get("ecosystems", [])][:6])

print("\n## [K3] boundary enforcement")
kf = os.path.join(p, "governance/kernel/policies/TEST_POLICY.yaml"); korig = open(kf).read(); open(kf, "a").write("# edited in the consumer\n")
t = sb.gov("task", "create", "--objective", "after kernel edit", cwd=p, quiet=True); print("[K3] edit governance/kernel/** in the consumer -> next mutation:", "ok" if t["ok"] else f"REFUSED {err(t)}")
open(kf, "w").write(korig)
t = sb.gov("task", "create", "--objective", "touch kernel", "--allowed", "governance/kernel/**", cwd=p, quiet=True)
a = sb.gov("audit", "--no-persist", cwd=p, quiet=True); r_ = a.get("result") or (a.get("error") or {}).get("details") or {}
print("[K3] task whose allowed_paths include governance/kernel/** -> full governance suite:", r_.get("verdict"), [(f["severity"], f["family"], f["message"][:100]) for f in r_.get("findings", []) if "INV-007" in f["message"]][:2])
tk = yaml.safe_load(open(os.path.join(p, "spec/tasks", t["result"]["id"] + ".yaml"))) if t["ok"] else {}
print("[K3] the task record itself also carries forbidden_paths:", tk.get("forbidden_paths"))
gf = os.path.join(p, "governance/generated/adapter-manifest.json"); g0 = open(gf).read(); open(gf, "w").write(g0.replace('"overlay_hash"', '"overlay_hash_x"'))
d = sb.gov("doctor", cwd=p, quiet=True); r_ = d.get("result") or (d.get("error") or {}).get("details") or {}
print("[K3] hand-edited governance/generated/adapter-manifest.json -> doctor D020:", [(c["ok"], c["message"][:90]) for c in r_.get("checks", []) if c["id"] == "D020"])
sb.gov("adapters", "generate", cwd=p, quiet=True)
print("[K3] `gov adapters generate` regenerates it:", '"overlay_hash"' in open(gf).read())

print("\n## [D1] authoritative tracked state vs derived runtime")
sb.gov("task", "create", "--objective", "authoritative task", cwd=p, quiet=True)
os.makedirs(os.path.join(p, "spec/decisions"), exist_ok=True)
open(os.path.join(p, "spec/decisions/D-0001.yaml"), "w").write(yaml.safe_dump({"id": "D-0001", "type": "decision", "title": "use postgres", "status": "ACTIVE", "chosen_option": "postgres"}))
sb.gov("rebuild-memory", cwd=p, quiet=True)
sb.git(p, "add", "-A"); sb.git(p, "commit", "-q", "-m", "state")
st1 = sb.gov("status", cwd=p, quiet=True)["result"]
m1 = json.load(open(os.path.join(p, "governance/generated/index-manifest.json")))["manifest_hash"]
print("[D1] tracked by git:", subprocess.run(["git", "ls-files", "spec/decisions", "spec/tasks", "governance/framework.lock"], cwd=p, capture_output=True, text=True).stdout.split())
print("[D1] derived runtime tracked by git?", bool(subprocess.run(["git", "ls-files", ".governance-runtime"], cwd=p, capture_output=True, text=True).stdout.strip()))
tables = [r[0] for r in sqlite3.connect(os.path.join(p, ".governance-runtime/state.db")).execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("[D1] derived stores (state.db tables):", tables)
print("[D1] derived runtime dir contents:", sorted(os.listdir(os.path.join(p, ".governance-runtime"))))
print("\n## [D2] delete ALL derived state, rebuild")
shutil.rmtree(os.path.join(p, ".governance-runtime"))
print("[D2] after deleting .governance-runtime: git status of tracked truth =", subprocess.run(["git", "status", "--porcelain"], cwd=p, capture_output=True, text=True).stdout.splitlines())
st2 = sb.gov("status", cwd=p, quiet=True)["result"]
print("[D2] gov status still reconstructs truth: records", st1["records"], "->", st2["records"], "| task counts", st1["tasks"]["counts"], "->", st2["tasks"]["counts"])
r = sb.gov("rebuild-memory", cwd=p, quiet=True)["result"]
m2 = json.load(open(os.path.join(p, "governance/generated/index-manifest.json")))["manifest_hash"]
print("[D2] rebuild: manifest hash before delete", m1[:16], "after rebuild", m2[:16], "| identical:", m1 == m2)
print("[D2] tracked files changed by the rebuild:", subprocess.run(["git", "status", "--porcelain"], cwd=p, capture_output=True, text=True).stdout.splitlines())
print("\n## [D3] derived records carry provenance sufficient to reconstruct source hits")
db = sqlite3.connect(os.path.join(p, ".governance-runtime/state.db"))
cols = [r[1] for r in db.execute("PRAGMA table_info(artifacts)")]
print("[D3] artifacts columns:", cols)
ccols = [r[1] for r in db.execute("PRAGMA table_info(chunks)")]
print("[D3] chunks columns:", ccols)
row = db.execute("SELECT artifact_id, path, content_hash, repo_commit, index_version FROM artifacts WHERE path='spec/decisions/D-0001.yaml'").fetchone()
print("[D3] D-0001 artifact:", row)
print("[D3] content_hash == sha256(file bytes):", row and row[2] == hashlib.sha256(open(os.path.join(p, row[1]), "rb").read()).hexdigest(), "| repo_commit == HEAD:", row and row[3] == sb.git(p, "rev-parse", "HEAD")[1])
q = sb.gov("memory", "query", "use postgres", cwd=p, quiet=True)["result"]["hits"][0]
print("[D3] memory query hit carries:", {k: q.get(k) for k in ("artifact_id", "path", "section", "status", "state_class", "routes")}, "| excerpt found in source file:", (q.get("excerpt") or "").strip()[:30] in open(os.path.join(p, q["path"])).read())
print("\nDONE")
