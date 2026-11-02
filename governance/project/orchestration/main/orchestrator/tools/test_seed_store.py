"""seed_store.py (DEC-1032 step (iv)): a seed applied; a seed refused leaves a normal rebuild, named; the vectors of
unchanged chunks kept on a planted repository (the real `gov rebuild` of this checkout's src/, embedding through a
stand-in Ollama on a private loopback port: the shared servers are never asked).

    python3 -m pytest -q -p no:cacheprovider .gov-runtime/scratch/orchestrator/tools/test_seed_store.py
    python3 .gov-runtime/scratch/orchestrator/tools/test_seed_store.py measure   # the planted measurement, printed
"""
import hashlib
import json
import os
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import seed_store as ss  # noqa: E402

REPO = HERE.parents[3]
SRC = Path(os.environ.get("SEED_TEST_GOV_SRC") or REPO / "src")


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                           "-c", "core.hooksPath=/dev/null", *a], capture_output=True, text=True, check=True).stdout.strip()


def write(p, text):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def plant_store(tree, vectors=("c1", "c2"), extra_table=True):
    """A store.db shaped like the product's: a lexical table, an FTS table, the vectors and their manifest."""
    db = Path(tree) / ss.STORE_REL
    db.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(db)
    c.executescript("CREATE TABLE lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT, path TEXT);"
                    "CREATE VIRTUAL TABLE lexical_fts USING fts5(text);"
                    "CREATE TABLE semantic_vector (chunk_id TEXT PRIMARY KEY, embedding BLOB NOT NULL);"
                    "CREATE TABLE semantic_manifest (embedder_model TEXT, embedder_revision TEXT, reranker_model TEXT,"
                    " reranker_revision TEXT);"
                    "INSERT INTO semantic_manifest VALUES ('m', 'r', 'x', 'y');")
    if extra_table:
        c.execute("CREATE TABLE records (id TEXT)")
    for v in vectors:
        c.execute("INSERT INTO lexical_chunk (chunk_id, path) VALUES (?, 'a.md')", (v,))
        c.execute("INSERT INTO lexical_fts (text) VALUES ('t')")
        c.execute("INSERT INTO semantic_vector VALUES (?, ?)", (v, struct.pack("2f", 1.0, 0.0)))
    c.commit()
    c.close()


def tables(db):
    c = sqlite3.connect(db)
    try:
        return sorted(n for (n,) in c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
                      if not n.startswith("sqlite_"))
    finally:
        c.close()


@pytest.fixture
def w(tmp_path, monkeypatch):
    monkeypatch.setenv("SEED_LOG", str(tmp_path / "seed.jsonl"))
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    for rel in ss.GUARD:
        write(repo / rel, f"# {rel}\n")
    write(repo / "docs/a.md", "a\n")
    write(repo / ".gitignore", ".gov-runtime/\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "one")
    base = tmp_path / "base"
    git(tmp_path, "clone", "-q", str(repo), str(base))
    plant_store(base)
    link = tmp_path / "store"
    link.symlink_to(base)
    tree = tmp_path / "tree"
    git(tmp_path, "clone", "-q", str(repo), str(tree))
    return type("W", (), {"tmp": tmp_path, "repo": repo, "base": base, "link": link, "tree": tree})


def log(w):
    return [json.loads(line) for line in (w.tmp / "seed.jsonl").read_text().splitlines()]


def test_same_commit_keeps_the_whole_store(w):
    ans = ss.seed(w.tree, w.link, mode="copy", who="t")
    assert ans["status"] == "seeded" and ans["kept"] == "whole store" and ans["vectors"] == 2, ans
    assert ans["base"] == str(w.base.resolve())  # the link followed once
    assert "records" in tables(w.tree / ss.STORE_REL)
    assert log(w)[-1]["kind"] == "seed" and log(w)[-1]["who"] == "t"


def test_another_commit_keeps_the_vectors_only(w):
    write(w.tree / "docs/b.md", "b\n")
    git(w.tree, "add", "-A")
    git(w.tree, "commit", "-q", "-m", "two")
    ans = ss.seed(w.tree, w.link, mode="copy")
    assert ans["status"] == "seeded" and ans["kept"] == "vectors only" and ans["vectors"] == 2, ans
    assert tables(w.tree / ss.STORE_REL) == ["semantic_manifest", "semantic_vector"]
    assert not (w.tree / ss.STAGING_REL).exists()


def test_vectors_only_is_forced_for_the_nightly(w):
    ans = ss.seed(w.tree, w.link, vectors_only=True)
    assert ans["mode"] == "copy" and ans["kept"] == "vectors only"


def test_the_guard_refuses_when_the_chunk_text_code_differs_and_leaves_the_tree(w):
    write(w.tree / "src/gov/retrieval/semantic.py", "EMBED_CHARS = 1024\n")
    git(w.tree, "commit", "-qam", "code")
    ans = ss.seed(w.tree, w.link, mode="copy")
    assert ans["status"] == "refused" and "semantic.py" in ans["reason"] and not (w.tree / ss.STORE_REL).exists()


def test_no_base_a_tree_with_its_store_and_a_broken_base_are_named_and_change_nothing(w):
    assert ss.seed(w.tree, w.tmp / "nowhere", mode="copy")["status"] == "none"
    plant_store(w.tree, vectors=("own",))
    ans = ss.seed(w.tree, w.link, mode="copy")
    assert ans["status"] == "none" and "own store" in ans["reason"]
    c = sqlite3.connect(w.tree / ss.STORE_REL)
    assert [r[0] for r in c.execute("SELECT chunk_id FROM semantic_vector")] == ["own"]
    c.close()
    other = w.tmp / "other"
    git(w.tmp, "clone", "-q", str(w.repo), str(other))
    (w.base / ss.STORE_REL).write_bytes(b"not a database at all" * 10)
    ans = ss.seed(other, w.link, mode="copy")
    assert ans["status"] == "refused" and not (other / ss.STORE_REL).exists(), ans


def test_replace_seeds_over_the_trees_store(w):
    plant_store(w.tree, vectors=("own",))
    ans = ss.seed(w.tree, w.link, mode="copy", replace=True)
    assert ans["status"] == "seeded" and ans["vectors"] == 2


STUB = ("import json, os, sys\n"
        "open(os.environ['STUB_ARGS'], 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "print(json.dumps({'ok': True, 'result': {'stores': {'semantic': {'status': 'recreated'}},"
        " 'timing': {'semantic_s': 1.5, 'total_s': 3.0}}}))\n"
        "sys.exit(int(os.environ.get('STUB_RC', '0')))\n")


def run_tool(w, *args, env=None):
    stub = w.tmp / "stub.py"
    stub.write_text(STUB)
    e = dict(os.environ, SEED_REBUILD_CMD=f"{sys.executable} {stub}", STUB_ARGS=str(w.tmp / "args.jsonl"),
             SEED_LOG=str(w.tmp / "seed.jsonl"), **(env or {}))
    return subprocess.run([sys.executable, str(HERE / "seed_store.py"), *map(str, args)], capture_output=True,
                          text=True, env=e)


def test_rebuild_after_a_refused_seed_is_the_normal_rebuild_and_says_why(w):
    write(w.tree / "src/gov/retrieval/chunking.py", "CHUNKER_VERSION = 9\n")
    git(w.tree, "commit", "-qam", "code")
    r = run_tool(w, "rebuild", w.tree, "--base", w.link, "--mode", "copy", "--who", "close")
    assert r.returncode == 0, r.stderr
    assert "seed: refused (copy)" in r.stderr and "chunking.py" in r.stderr
    assert json.loads((w.tmp / "args.jsonl").read_text().splitlines()[-1]) == [str(w.tree.resolve())]
    rows = log(w)
    assert [x["kind"] for x in rows] == ["seed", "rebuild"] and rows[-1]["seed"]["status"] == "refused"
    assert rows[-1]["timing"]["semantic_s"] == 1.5 and rows[-1]["who"] == "close"


def test_rebuild_of_a_tree_with_its_store_seeds_nothing(w):
    plant_store(w.tree, vectors=("own",))
    r = run_tool(w, "rebuild", w.tree, "--base", w.link)
    assert r.returncode == 0 and "incremental rebuild" in r.stderr
    assert [x["kind"] for x in log(w)] == ["rebuild"]


def test_product_mode_passes_seed_to_the_rebuild_when_the_trees_gov_offers_it(w):
    write(w.tree / "src/gov/__init__.py", "")
    write(w.tree / "src/gov/cli/__init__.py", "")
    write(w.tree / "src/gov/cli/main.py", "import sys\nprint('usage: gov rebuild [--json] [--seed [FOLDER]]')\n")
    r = run_tool(w, "rebuild", w.tree, "--base", w.link)
    assert r.returncode == 0, r.stderr
    assert json.loads((w.tmp / "args.jsonl").read_text().splitlines()[-1]) == \
        [str(w.tree.resolve()), "--seed", str(w.base.resolve())]
    assert not (w.tree / ss.STORE_REL).exists()  # nothing copied here: the product seeds under its own lock
    r = run_tool(w, "warm", w.tree, "--base", w.link)
    assert r.returncode == 0 and "seed: deferred (product)" in r.stderr


def test_warm_in_copy_mode_seeds_without_a_rebuild(w):
    r = run_tool(w, "warm", w.tree, "--base", w.link, "--mode", "copy")
    assert r.returncode == 0 and "seed: seeded (copy)" in r.stdout and not (w.tmp / "args.jsonl").exists()


def test_new_worktree_adds_the_worktree_and_seeds_it(w):
    env = dict(os.environ, NEW_WORKTREE_REPO=str(w.repo), NEW_WORKTREE_ROOT=str(w.tmp / "wts"),
               NEW_WORKTREE_BASE=str(w.link), SEED_LOG=str(w.tmp / "seed.jsonl"))
    (w.tmp / "wts").mkdir()
    r = subprocess.run(["bash", str(HERE / "new_worktree.sh"), "W2-9", "main"], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    tree = w.tmp / "wts/W2-9"
    assert git(tree, "rev-parse", "--abbrev-ref", "HEAD") == "w2/W2-9" and (tree / ss.STORE_REL).is_file()
    assert "seed: seeded (copy): whole store" in r.stdout and log(w)[-1]["who"] == "lead W2-9"
    again = subprocess.run(["bash", str(HERE / "new_worktree.sh"), "W2-9", "main"], capture_output=True, text=True,
                           env=env)
    assert again.returncode == 2 and "exists" in again.stderr
    assert subprocess.run(["bash", str(HERE / "new_worktree.sh"), "../x"], capture_output=True, env=env).returncode == 2


def refresh_env(w, **more):
    for half in ("a", "b"):
        git(w.repo, "worktree", "add", "-q", "--detach", str(w.tmp / f"st-{half}"), "main")
    (w.tmp / "st").symlink_to(w.tmp / "st-a")
    plant_store(w.tmp / "st-a")
    stub = w.tmp / "stub.py"
    stub.write_text(STUB)
    return dict(os.environ, GOV_STORE_LINK=str(w.tmp / "st"), GOV_STORE_REPO=str(w.repo), GOV_STORE_REF="main",
                GOV_STORE_LOG=str(w.tmp / "store.log"), SEED_LOG=str(w.tmp / "seed.jsonl"),
                SEED_REBUILD_CMD=f"{sys.executable} {stub}", STUB_ARGS=str(w.tmp / "args.jsonl"), **more)


def test_the_refresh_builds_the_standby_half_seeded_and_moves_the_link_under_the_stores_lock(w):
    env = refresh_env(w)
    fresh = subprocess.run(["bash", str(HERE / "refresh_integration_store.sh")], capture_output=True, text=True, env=env)
    assert fresh.returncode == 0 and "fresh at" in fresh.stdout  # already at the ref: nothing built
    write(w.repo / "docs/b.md", "b\n")
    git(w.repo, "add", "-A")
    git(w.repo, "commit", "-q", "-m", "two")
    r = subprocess.run(["bash", str(HERE / "refresh_integration_store.sh")], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (w.tmp / "st").resolve() == (w.tmp / "st-b").resolve()
    assert git(w.tmp / "st-b", "rev-parse", "HEAD") == git(w.repo, "rev-parse", "main")
    assert json.loads((w.tmp / "args.jsonl").read_text().splitlines()[-1]) == [str((w.tmp / "st-b").resolve())]
    seeds = [x for x in log(w) if x["kind"] == "seed"]
    assert seeds[-1]["status"] == "seeded" and seeds[-1]["kept"] == "vectors only" and seeds[-1]["who"] == "refresh st-b"


def test_a_failed_refresh_or_a_held_lock_leaves_the_link(w):
    import fcntl
    env = refresh_env(w, STUB_RC="75")
    write(w.repo / "docs/b.md", "b\n")
    git(w.repo, "add", "-A")
    git(w.repo, "commit", "-q", "-m", "two")
    r = subprocess.run(["bash", str(HERE / "refresh_integration_store.sh")], capture_output=True, text=True, env=env)
    assert r.returncode == 75 and (w.tmp / "st").resolve() == (w.tmp / "st-a").resolve()
    with open(str(w.tmp / "st") + ".lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)  # a queue's re-run in the ready half
        r = subprocess.run(["bash", str(HERE / "refresh_integration_store.sh")], capture_output=True, text=True,
                           env=dict(env, GOV_STORE_LOCK_WAIT="1", STUB_RC="0"))
    assert r.returncode == 3 and "lock" in r.stdout and (w.tmp / "st").resolve() == (w.tmp / "st-a").resolve()


# ---- the planted repository: the real rebuild, a stand-in embedder that counts what it is asked -------------------

class StandIn:
    """Ollama's interface on a private loopback port: a model list, and vectors that are a hash of the text."""

    def __init__(self):
        self.texts, outer = [], self
        entry = {"name": "qwen3-embedding:0.6b", "model": "qwen3-embedding:0.6b", "digest": "ac6da0dfba84" + "0" * 52}

        class H(BaseHTTPRequestHandler):
            def answer(self):
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n) or b"{}") if n else {}
                route = self.path.split("?")[0].rstrip("/")
                reply = {"version": "0.35.0"} if route == "/api/version" else {"models": [entry]} \
                    if route == "/api/tags" else {"models": [dict(entry, size=1, size_vram=0)]} if route == "/api/ps" \
                    else None
                if route == "/api/embed":
                    texts = body.get("input") or []
                    texts = [texts] if isinstance(texts, str) else texts
                    outer.texts.extend(texts)
                    reply = {"embeddings": [[b / 255 for b in hashlib.sha256(t.encode()).digest()[:16]] for t in texts]}
                data = json.dumps(reply or {}).encode()
                self.send_response(200 if reply is not None else 404)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            do_GET = do_POST = answer

            def log_message(self, *a):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()


def lacking():
    import importlib.util
    if not shutil.which("gitleaks"):
        return "no gitleaks"
    if importlib.util.find_spec("sqlite_vec") is None:
        return "no sqlite_vec"
    if not (SRC / "gov/rebuild/command.py").is_file():
        return f"no gov code at {SRC}"
    return None


def note(word, n=6):
    return f"# The {word} note\n\n" + "".join(f"The {word} ledger line {i} is kept beside the harbour.\n\n"
                                              for i in range(n))


def gov_rebuild(tree, env):
    t0 = time.time()
    r = subprocess.run([sys.executable, "-m", "gov.cli.main", "rebuild", "--json"], cwd=tree, env=env,
                       capture_output=True, text=True, timeout=900)
    doc = ss.envelope(r.stdout) or {}
    return r.returncode, doc.get("result") or {}, round(time.time() - t0, 1), r.stderr[-800:]


def vectors(tree):
    c = sqlite3.connect(Path(tree) / ss.STORE_REL)
    try:
        return dict(c.execute("SELECT chunk_id, embedding FROM semantic_vector"))
    finally:
        c.close()


def planted(tmp):
    """Base at commit 1 (four notes), a tree at commit 2 (one note changed, one removed, one added). Returns the
    measurement: texts embedded by the base's cold build, the tree's seeded build and the tree's cold build."""
    tmp = Path(tmp)
    tools = tmp / "tools"
    tools.mkdir()
    (tools / "gitleaks").symlink_to(shutil.which("gitleaks"))
    emb = StandIn()
    env = {"PATH": f"{tools}:{Path(sys.executable).parent}:/usr/bin:/bin", "HOME": str(tmp / "home"),
           "TMPDIR": str(tmp), "PYTHONPATH": str(SRC), "PYTHONDONTWRITEBYTECODE": "1", "OLLAMA_HOST": emb.host,
           "GOV_QUERY_OLLAMA_HOST": emb.host, "GOV_OLLAMA_BIN": str(tmp / "no-ollama"), "GOV_SECRETS_CACHE": "",
           "GOV_REBUILD_LOCK": str(tmp / "rebuild.lock"), "GIT_CONFIG_GLOBAL": os.devnull, "LANG": "C.UTF-8",
           "GIT_CONFIG_SYSTEM": os.devnull, "PYTHONUSERBASE": __import__("site").getuserbase()}
    (tmp / "home").mkdir()
    try:
        import yaml
        pm = yaml.safe_load((REPO / "template/governance/project/path-map.yaml").read_text())
        pm.setdefault("namespaces", {})["docs"] = {
            "paths": ["docs/**"], "memory_class": "governance", "sensitivity": "internal",
            "permitted_roles": ["engineer", "orchestrator"], "retention": "git", "export_policy": "allowed",
            "embedding_policy": "embedded", "provenance": "planted", "deletion_rebuild": "from git"}
        base = tmp / "base"
        write(base / "governance/project/path-map.yaml", yaml.safe_dump(pm, sort_keys=False))
        shutil.copy(REPO / "template/.gitleaks.toml", base / ".gitleaks.toml")
        write(base / ".gitignore", ".gov-runtime/\n__pycache__/\n")
        for rel in ss.GUARD:  # the guard compares these with the tree's: the same code on both sides
            write(base / rel, (SRC.parent / rel).read_text())
        words = ["quillwort", "marjoram", "bergamot", "sorrel"]
        for word in words:
            write(base / f"docs/{word}.md", note(word))
        git(base, "init", "-q", "-b", "main")
        git(base, "add", "-A")
        git(base, "commit", "-q", "-m", "one")
        rc, res, s_base, err = gov_rebuild(base, env)
        assert rc == 0 and res["stores"]["semantic"]["status"] == "recreated", (rc, res, err)
        base_texts = len(emb.texts)
        tree = tmp / "tree"
        git(tmp, "clone", "-q", str(base), str(tree))
        write(tree / "docs/bergamot.md", note("bergamot") + "The tamarind entry was added later.\n")
        (tree / "docs/sorrel.md").unlink()
        write(tree / "docs/fenugreek.md", note("fenugreek"))
        git(tree, "add", "-A")
        git(tree, "commit", "-q", "-m", "two")
        cold = tmp / "cold"
        git(tmp, "clone", "-q", str(tree), str(cold))
        same = tmp / "same"  # a copy at the base's own commit (a new worktree at the head; the promotion)
        git(tmp, "clone", "-q", str(base), str(same))
        os.environ["SEED_LOG"] = str(tmp / "seed.jsonl")
        whole = ss.seed(same, base, mode="copy", who="planted same")
        assert whole["status"] == "seeded" and whole["kept"] == "whole store", whole
        emb.texts.clear()
        rc, res, s_same, err = gov_rebuild(same, env)
        assert rc == 0 and res["stores"]["semantic"]["status"] == "recreated", (rc, res, err)
        same_texts, same_timing = len(emb.texts), res.get("timing")
        os.environ["SEED_LOG"] = str(tmp / "seed.jsonl")
        ans = ss.seed(tree, base, mode="copy", who="planted")
        assert ans["status"] == "seeded" and ans["kept"] == "vectors only", ans
        emb.texts.clear()
        rc, res, s_seeded, err = gov_rebuild(tree, env)
        assert rc == 0 and res["stores"]["semantic"]["status"] == "recreated", (rc, res, err)
        seeded_texts, sent = len(emb.texts), list(emb.texts)
        seeded_timing = res.get("timing")
        emb.texts.clear()
        rc, res, s_cold, err = gov_rebuild(cold, env)
        assert rc == 0, err
        cold_texts = len(emb.texts)
        same = vectors(tree) == vectors(cold)
        return {"base_cold_texts": base_texts, "tree_seeded_texts": seeded_texts, "tree_cold_texts": cold_texts,
                "same_commit_seeded_texts": same_texts, "same_commit_timing": same_timing,
                "seeded_equals_cold": same, "seeded_sent": sent, "seed": ans, "seconds": {
                    "base_cold": s_base, "tree_seeded": s_seeded, "tree_cold": s_cold},
                "seeded_timing": seeded_timing, "cold_timing": res.get("timing")}
    finally:
        emb.close()


@pytest.mark.skipif(lacking() is not None, reason=str(lacking()))
def test_a_seeded_rebuild_embeds_only_the_changed_chunks_and_equals_a_cold_one(tmp_path, monkeypatch):
    monkeypatch.setenv("SEED_LOG", str(tmp_path / "seed.jsonl"))
    m = planted(tmp_path)
    assert m["seeded_equals_cold"], "the seeded tree's vectors are not the cold tree's"
    assert m["same_commit_seeded_texts"] == 0, m  # the whole store at the same commit: nothing to embed
    assert 0 < m["tree_seeded_texts"] < m["tree_cold_texts"], m
    joined = "\n".join(m["seeded_sent"])
    assert "fenugreek" in joined or "tamarind" in joined  # the added and changed notes were embedded
    assert "quillwort" not in joined and "marjoram" not in joined  # the unchanged notes kept their vectors


if __name__ == "__main__" and sys.argv[1:] == ["measure"]:
    with tempfile.TemporaryDirectory() as d:
        out = planted(d)
        out.pop("seeded_sent")
        print(json.dumps(out, indent=1))
