"""Every copy seeded from the warm integration store before its rebuild (owner, DEC-1032 step (iv)): no cold rebuild.

    python3 seed_store.py seed    <tree> [--base <dir>] [--mode auto|copy|product] [--vectors-only] [--replace]
                                         [--who <label>] [--json]
    python3 seed_store.py rebuild <tree> [the same options] [-- <more gov rebuild arguments>]
    python3 seed_store.py warm    <tree> [the same options]

The base (default ~/gov-os-worktrees/W2-00-store, the link to the ready half of the integration store) is only read.

- **product** (when the tree's own `gov rebuild --help` offers `--seed`, W2-122): nothing is copied here; the answer
  carries `--seed <base>` for the tree's rebuild, which seeds under its own lock and refuses, named in its `seed`
  answer, a base whose code, embedder or schema differs (it then runs cold).
- **copy** (otherwise, or `--mode copy`): the base's `store.db` copied through SQLite's backup (a consistent state even
  while it is read). When the base and the tree are at the same commit with no tracked change, the whole store is kept
  (and the query-vector cache): the rebuild re-chunks nothing and embeds nothing. Otherwise (`--vectors-only`, or
  another commit) only the vectors are kept (`semantic_vector`, `semantic_manifest`); every other table is dropped, so
  the record store, the lexical index and its secrets judgements are built by the tree's own code, and the semantic
  stage embeds only the chunks that have no vector: a chunk's id is the hash of its path, its file's blob and its
  lines (`gov.retrieval.chunking.make_id`), so an unchanged file keeps its vectors, and a vector of another embedder
  is dropped by the semantic stage itself (`semantic._build`). The vectors are only kept where the code that turns a
  chunk into the text it embeds is the base's (semantic.py, lexical.py, chunking.py: the same blobs); else refused.
  The code index is not copied: it holds its tree's absolute path and every rebuild makes it anew.
- **Fail closed:** a seed that cannot be applied (no base, the tree's own store present without `--replace`, the
  guard, a copy fault) leaves the tree as it was, says why, and the rebuild runs as it would have (cold for an empty
  tree). Nothing raises.

`seed` seeds (copy) or answers the product's arguments (product). `rebuild` seeds when the tree has no store (or with
`--replace`), then the rebuild in a heavy-job slot (rebuild_slot.sh, its output passed through), exit = the rebuild's.
`warm` seeds, and runs the rebuild only in product mode (where the seed happens inside it): new_worktree.sh.
Every seed and every rebuild is one line of SEED_LOG (default log/seed.jsonl): who, tree, mode, status, reason,
vectors kept, seconds, and for a rebuild its exit and the stage times (rebuild_counts.py reads it).
Tests only: SEED_REBUILD_CMD replaces `bash rebuild_slot.sh` (the tree and the arguments are appended).
"""
import argparse
import json
import os
import shlex
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORCH = HERE.parent
DEFAULT_BASE = Path.home() / "gov-os-worktrees/W2-00-store"
STORE_REL = ".gov-runtime/store.db"
QUERY_REL = ".gov-runtime/query-vector-cache.db"
STAGING_REL = ".gov-runtime/seed.tmp"
KEEP = ("semantic_vector", "semantic_manifest")  # what a vectors-only seed keeps
GUARD = ("src/gov/retrieval/semantic.py", "src/gov/retrieval/lexical.py", "src/gov/retrieval/chunking.py")
SIDECARS = ("-wal", "-shm", "-journal")


def log_path():
    return Path(os.environ.get("SEED_LOG") or ORCH / "log/seed.jsonl")


def record(entry):
    try:
        p = log_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(entry, at=time.strftime("%F %T")), sort_keys=True) + "\n")
    except OSError:
        pass  # the record never fails a seed


def git(where, *args):
    r = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def clean(where):
    """No tracked change in the working tree (staged or not): its tracked files are its HEAD's."""
    return subprocess.run(["git", "-C", str(where), "diff", "--quiet", "HEAD", "--"], capture_output=True).returncode == 0


def blob(where, rel):
    """The blob id of the working file `rel` (what the code that ran was), None when it is absent."""
    return git(where, "hash-object", "--", rel) if (Path(where) / rel).is_file() else None


def offers_seed(tree):
    """Whether the tree's own `gov rebuild --help` offers --seed (W2-122 landed in that tree's code)."""
    try:
        r = subprocess.run([sys.executable, "-m", "gov.cli.main", "rebuild", "--help"], cwd=tree, capture_output=True,
                           text=True, timeout=180,
                           env=dict(os.environ, PYTHONPATH=f"{tree}/src", PYTHONDONTWRITEBYTECODE="1"))
    except (OSError, subprocess.TimeoutExpired):
        return False
    return r.returncode == 0 and "--seed" in r.stdout


def backup(source, target):
    """The SQLite file `source`, read as one consistent state, into `target` (replaced whole)."""
    reading = sqlite3.connect(Path(source).resolve().as_uri() + "?mode=ro", uri=True, timeout=60.0)
    try:
        writing = sqlite3.connect(target, timeout=60.0)
        try:
            reading.backup(writing)
        finally:
            writing.close()
    finally:
        reading.close()


def vectors_in(db):
    c = sqlite3.connect(Path(db).resolve().as_uri() + "?mode=ro", uri=True, timeout=60.0)
    try:
        if c.execute("SELECT 1 FROM sqlite_master WHERE name = 'semantic_manifest'").fetchone() is None:
            return 0
        if c.execute("SELECT 1 FROM semantic_manifest").fetchone() is None:
            return 0
        return c.execute("SELECT count(*) FROM semantic_vector").fetchone()[0]
    finally:
        c.close()


def keep_vectors_only(db):
    """Every table of the copy but the vectors dropped (virtual tables first: their shadow tables go with them)."""
    c = sqlite3.connect(db, isolation_level=None)
    try:
        for virtual in (True, False):
            rows = c.execute("SELECT name, sql FROM sqlite_master WHERE type = 'table'").fetchall()
            for name, sql in rows:
                if name in KEEP or name.startswith("sqlite_"):
                    continue
                if virtual != (sql or "").upper().startswith("CREATE VIRTUAL"):
                    continue
                if c.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (name,)).fetchone():
                    c.execute(f'DROP TABLE "{name}"')
        c.execute("VACUUM")
    finally:
        c.close()


def answer(mode, status, reason, base=None, **more):
    return {"mode": mode, "status": status, "reason": reason, "base": None if base is None else str(base),
            "rebuild_args": [], **more}


def remove_store(tree):
    for suffix in ("",) + SIDECARS:
        (Path(tree) / (STORE_REL + suffix)).unlink(missing_ok=True)


def copy_seed(tree, base, vectors_only=False, replace=False):
    """The copy seed (module docstring). Returns the answer; never raises."""
    tree = Path(tree).resolve()
    if not (base / STORE_REL).is_file():
        return answer("copy", "none", f"no warm base at {base}: it holds no {STORE_REL}", base)
    if base == tree:
        return answer("copy", "none", f"the base {base} is this tree itself", base)
    if (tree / STORE_REL).exists() and not replace:
        return answer("copy", "none", "the tree has its own store: kept, not seeded", base)
    base_head, tree_head = git(base, "rev-parse", "HEAD"), git(tree, "rev-parse", "HEAD")
    if not base_head or not tree_head:
        return answer("copy", "refused", "the HEAD of the base or of the tree cannot be read", base)
    whole = not vectors_only and base_head == tree_head and clean(base) and clean(tree)
    if not whole:
        differs = [rel for rel in GUARD if blob(base, rel) != blob(tree, rel)]
        if differs:
            return answer("copy", "refused", "the code that turns a chunk into its text differs from the base's ("
                          + ", ".join(differs) + "): no vector is reused", base, base_head=base_head)
    t0 = time.time()
    staging = tree / STAGING_REL
    installed = False
    try:
        if vectors_in(base / STORE_REL) == 0:
            return answer("copy", "none", f"the base {base} holds no vectors", base, base_head=base_head)
        shutil.rmtree(staging, ignore_errors=True)
        staging.mkdir(parents=True)
        backup(base / STORE_REL, staging / "store.db")
        if not whole:
            keep_vectors_only(staging / "store.db")
        kept = vectors_in(staging / "store.db")
        if replace:
            remove_store(tree)
        elif (tree / STORE_REL).exists():
            return answer("copy", "none", "the tree's own store appeared while the base was copied: kept", base)
        installed = True
        os.replace(staging / "store.db", tree / STORE_REL)
        query = False
        if whole and (base / QUERY_REL).is_file() and (replace or not (tree / QUERY_REL).exists()):
            backup(base / QUERY_REL, staging / "query.db")
            for suffix in ("",) + SIDECARS:
                (tree / (QUERY_REL + suffix)).unlink(missing_ok=True)
            os.replace(staging / "query.db", tree / QUERY_REL)
            query = True
    except (OSError, sqlite3.Error) as exc:
        if installed:
            remove_store(tree)
        return answer("copy", "refused", f"the base could not be copied: {exc}", base)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return answer("copy", "seeded", None, base, kept="whole store" if whole else "vectors only", vectors=kept,
                  query_cache=query, base_head=base_head, tree_head=tree_head, seconds=round(time.time() - t0, 1))


def seed(tree, base=None, mode="auto", vectors_only=False, replace=False, who=None):
    """Seed `tree` from `base` (module docstring); the answer, also recorded in SEED_LOG. Never raises."""
    tree = Path(tree).resolve()
    given = Path(base).expanduser() if base else DEFAULT_BASE
    try:
        resolved = given.resolve()  # a link followed once: the ready half, read from here on
        if mode == "auto" and not vectors_only:
            mode = "product" if offers_seed(tree) else "copy"
        if mode == "product":
            if (tree / STORE_REL).exists() and not replace:
                ans = answer("product", "none", "the tree has its own store: kept, not seeded", resolved)
            elif not (resolved / STORE_REL).is_file():
                ans = answer("product", "none", f"no warm base at {resolved}: it holds no {STORE_REL}", resolved)
            else:
                ans = answer("product", "deferred", None, resolved, rebuild_args=["--seed", str(resolved)])
        else:
            ans = copy_seed(tree, resolved, vectors_only=vectors_only, replace=replace)
    except Exception as exc:  # fail closed: a seed that cannot be worked out is no seed
        ans = answer(mode, "refused", f"the seed could not be worked out: {exc.__class__.__name__}: {exc}", given)
    record(dict(ans, kind="seed", tree=str(tree), who=who))
    return ans


def summary(ans):
    what = {"seeded": f"{ans.get('kept')}, {ans.get('vectors')} vectors from {ans.get('base')} at "
                      f"{(ans.get('base_head') or '')[:12]} in {ans.get('seconds')} s",
            "deferred": f"gov rebuild {' '.join(ans['rebuild_args'])}"}.get(ans["status"], ans.get("reason"))
    return f"seed: {ans['status']} ({ans['mode']}): {what}"


def envelope(text):
    """The rebuild's JSON envelope in its output (the last line that parses as an object), or None."""
    for line in reversed((text or "").splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                doc = json.loads(line)
            except ValueError:
                continue
            if isinstance(doc, dict):
                return doc
    return None


def rebuild(tree, ans, extra, who):
    """The rebuild in a heavy-job slot, its output passed through; the record of it; its exit code."""
    tree = Path(tree).resolve()
    prefix = shlex.split(os.environ["SEED_REBUILD_CMD"]) if os.environ.get("SEED_REBUILD_CMD") else \
        ["bash", str(HERE / "rebuild_slot.sh")]
    env = dict(os.environ, PYTHONPATH=f"{tree}/src",
               GOV_REBUILD_PYTHON=os.environ.get("GOV_REBUILD_PYTHON") or sys.executable)
    t0 = time.time()
    r = subprocess.run(prefix + [str(tree), *ans.get("rebuild_args", []), *extra], cwd=tree, env=env,
                       stdout=subprocess.PIPE, text=True)
    sys.stdout.write(r.stdout)
    sys.stdout.flush()
    doc = envelope(r.stdout) or {}
    res = doc.get("result") or {}
    record({"kind": "rebuild", "tree": str(tree), "who": who, "rc": r.returncode,
            "seconds": round(time.time() - t0, 1), "timing": res.get("timing"),
            "semantic": ((res.get("stores") or {}).get("semantic") or {}).get("status"),
            "seed": {k: ans.get(k) for k in ("mode", "status", "reason", "kept", "vectors")},
            "product_seed": res.get("seed")})
    if res.get("seed") and res["seed"].get("status") != "seeded":
        print(f"seed_store: the product refused the seed, the rebuild ran cold: {res['seed'].get('reason')}",
              file=sys.stderr)
    return r.returncode


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("action", choices=("seed", "rebuild", "warm"))
    ap.add_argument("tree")
    ap.add_argument("--base")
    ap.add_argument("--mode", choices=("auto", "copy", "product"), default="auto")
    ap.add_argument("--vectors-only", action="store_true")
    ap.add_argument("--replace", action="store_true", help="seed over the tree's own store")
    ap.add_argument("--who", default=None, help="a label for the record (lead W2-xx, queue merged, close, nightly)")
    ap.add_argument("--json", action="store_true")
    argv = list(sys.argv[1:] if argv is None else argv)
    extra = argv[argv.index("--") + 1:] if "--" in argv else []
    a = ap.parse_args(argv[:argv.index("--")] if "--" in argv else argv)
    tree = Path(a.tree)
    if not (tree / ".git").exists():
        print(f"seed_store: {a.tree} is not a git tree", file=sys.stderr)
        return 2
    if a.action == "rebuild" and (tree / STORE_REL).exists() and not a.replace:
        ans = answer("none", "none", "the tree has its own store: an incremental rebuild")
    else:
        ans = seed(tree, a.base, a.mode, a.vectors_only, a.replace, a.who)
    if a.action == "seed" or (a.action == "warm" and not ans["rebuild_args"]):
        print(json.dumps(ans) if a.json else summary(ans), flush=True)
        return 0
    print(summary(ans), file=sys.stderr, flush=True)
    return rebuild(tree, ans, extra, a.who)


if __name__ == "__main__":
    sys.exit(main())
