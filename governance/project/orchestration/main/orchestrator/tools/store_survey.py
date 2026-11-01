#!/usr/bin/env python3
"""Every store on the machine, read-only: the main tree's, the designers' (both copies) and each worktree's.
For each: when store.db was last written, the head its rebuild fingerprinted, how far that head is behind the tree's
own HEAD and behind w2/integrate, and what it holds: the record graph (records, commits, edges), the keyword index
(lexical files and chunks), the embeddings (vectors) and the code graph (code.db and its node count).
    python3 store_survey.py [--json]"""
import glob
import json
import os
import sqlite3
import subprocess
import sys
import time

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
WT = "/home/usain/gov-os-worktrees"


def git(root, *a):
    r = subprocess.run(["git", "-C", root, *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def count(c, table):
    try:
        return c.execute(f'select count(*) from "{table}"').fetchone()[0]
    except sqlite3.Error:
        return None


def survey(root):
    out = {"root": root, "head_now": git(root, "rev-parse", "--short=12", "HEAD"),
           "branch": git(root, "rev-parse", "--abbrev-ref", "HEAD")}
    db = os.path.join(root, ".gov-runtime/store.db")
    if not os.path.isfile(db):
        out["store"] = "none"
        return out
    out["built"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(db)))
    try:
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        fp = c.execute("select head from fingerprints").fetchone()
        built_on = fp[0] if fp else None
        out["built_on"] = built_on[:12] if built_on else None
        out["records"], out["commits"], out["edges"] = count(c, "records"), count(c, "commits"), count(c, "edges")
        out["lexical_files"], out["lexical_chunks"] = count(c, "lexical_file"), count(c, "lexical_chunk")
        out["vectors"] = count(c, "semantic_vector")
        c.close()
    except sqlite3.Error as e:
        out["store"] = f"unreadable: {e}"
        return out
    if built_on:
        out["behind_own_head"] = git(root, "rev-list", "--count", f"{built_on}..HEAD")
        out["behind_integrate"] = git(root, "rev-list", "--count", f"{built_on}..w2/integrate")
    cdb = os.path.join(root, ".gov-runtime/codeintel/home/code.db")
    if os.path.isfile(cdb):
        out["code_graph_built"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(cdb)))
        try:
            c = sqlite3.connect(f"file:{cdb}?mode=ro", uri=True)
            out["code_nodes"] = count(c, "nodes")
            out["code_edges"] = count(c, "edges")
            c.close()
        except sqlite3.Error as e:
            out["code_graph"] = f"unreadable: {e}"
    else:
        out["code_graph"] = "none"
    return out


def main():
    roots = [MAIN]
    link = os.path.join(WT, "W2-00-store")
    roots += sorted(p for p in glob.glob(os.path.join(WT, "*")) if os.path.isdir(p) and not os.path.islink(p))
    rows = [survey(r) for r in roots]
    live = os.path.realpath(link) if os.path.islink(link) else None
    for r in rows:
        r["designers_live"] = (r["root"] == live)
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=1))
        return
    for r in rows:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
