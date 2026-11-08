"""The planted set: a synthetic sets root and clone in the fresh 80's file shape (the measure's loader and the tracked
visible fixtures' form; ACT-MSET-3 §4 item 4), built in a temporary folder. Nothing here reads ~/gov-os-eval.

- the clone: a git repository with docs/q/<id>.md per question ("# Topic <id>" and two lines), the path map's
  evaluation_families (contract 4, kernel 3, agents 2 members: item 5's line), retrieval.yaml's pool block, a branch
  w2/integrate, and .gov-runtime/store.db (ignored) with a lexical_chunk table;
- the sets root: its path map's evaluation_sets (no families, as the real one), memory-verdict-2/hidden/v01..v80
  (v80 the nonexistent-id question, naming DEC-99999), memory-retrieval/visible/c01..c40 (the control: 34 hit);
- a fake gov (``fake_gov.py``): a question with "[hit]" gets its gold file in the first five items; "again <id>"
  gets it too; DEC-99999 gets UNRESOLVED_IDS; switches by env for faults.
"""
import json
import os
import shutil
import sqlite3
import stat
import subprocess
import sys
from pathlib import Path

import pytest

PIN_SITE = Path.home() / ".local/share/gov-os/pin-bcea09060ebc/lib/python3.12/site-packages"
HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
for p in (str(TOOLS), str(PIN_SITE)):
    if p not in sys.path:
        sys.path.insert(0, p)

FAMILIES_MAP = """evaluation_families:
  contract: ["docs/contract/CONTRACT_v4.md", "docs/contract/contract.yaml",
             "docs/contract/capabilities/*.md", "docs/contract/master-rules/*.md"]
  kernel: ["template/governance/kernel/**", ".claude/**", ".rulesync/**"]
  agents: ["AGENTS.md", "CLAUDE.md"]
"""
POOL = """pool:
  meaning_uncut: true
  route_depth: 60
  rerank_depth: 40
  per_file_first10: 2
  drop_nested: true
"""
SETS_MAP = """evaluation_sets:
  memory-retrieval:
    visible: ["docs/assessment/2026-10/B-memory-retrieval.md"]
    hidden: ["fixtures/evaluation/memory-retrieval/hidden/**"]
    measures:
      roles: [engineer, research]
  memory-verdict-2:
    visible: []
    hidden: ["fixtures/evaluation/memory-verdict-2/hidden/**"]
    measures:
      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]
"""
MISS_IDS = {"v03", "v11", "v19", "v27", "v35", "v43", "v51", "v59", "v67", "v75"}  # 10 first-call misses of the 79
CONTROL_MISS = {"c05", "c10", "c15", "c20", "c25", "c30"}  # 34 of 40 hit

FAKE_GOV = r'''#!/usr/bin/env python3
import json, os, re, sys
a = sys.argv[1:]
if a[:1] == ["--version"]:
    print("gov 0.0-fake"); sys.exit(0)
if a[:1] != ["retrieve"]:
    sys.exit(2)
a = a[1:]
words, i = [], 0
while i < len(a):
    if a[i] in ("--ticket", "--id", "--radius", "--batch-size", "--bundle-budget", "--continue"):
        i += 2; continue
    if a[i] == "--json":
        i += 1; continue
    words.append(a[i]); i += 1
q = " ".join(words)
m = re.search(r"\b([vc]\d\d)\b", q)
qid = m.group(1) if m else "none"
flag = os.environ.get("FAKE_FAIL_ONCE")
if flag and qid == "v05" and "planted question" in q and os.path.exists(flag):
    os.remove(flag); sys.exit(1)
if os.environ.get("FAKE_FAIL_ALWAYS") and qid == "v05" and "planted question" in q:
    sys.exit(1)
if os.environ.get("FAKE_TOUCH_STORE") and qid == "v10" and "planted question" in q:
    with open(os.environ["FAKE_TOUCH_STORE"], "ab") as f:
        f.write(b"x")
if os.environ.get("FAKE_SEARCH_FAIL") and q.startswith("again ") and qid in os.environ["FAKE_SEARCH_FAIL"].split(","):
    print("not json"); sys.exit(1)
OKF = {"lexical": {"available": True}, "semantic": {"available": True}}
SVC = {"by": "service", "device": "cuda:0", "reason": None}
deg = os.environ.get("FAKE_DEGRADE_ONCE")
rerank, facets = dict(SVC), dict(OKF)
if deg and qid == "v07" and "planted question" in q and os.path.exists(deg):
    os.remove(deg); rerank = {"by": "unavailable", "device": None, "reason": "no GPU slot"}
if os.environ.get("FAKE_DEGRADE_SEARCH") and q.startswith("again ") and qid in os.environ["FAKE_DEGRADE_SEARCH"].split(","):
    facets = {"lexical": {"available": True}, "semantic": {"available": False, "reason": "embedder down"}}
fill = [{"path": f"docs/fill{k}.md", "start_line": 1, "end_line": 2, "text": f"filler {k}", "chunk_id": f"fill{k}"}
        for k in range(1, 7)]
if "DEC-99999" in q:
    print(json.dumps({"ok": True, "result": {"stopping_reason": "UNRESOLVED_IDS", "evidence": [],
                      "gaps": [{"id": "DEC-99999", "reason": "UNRESOLVED"}], "facets": OKF, "continuation": None}}))
    sys.exit(0)
gold = {"path": f"docs/q/{qid}.md", "start_line": 1, "end_line": 3, "text": f"# Topic {qid}\nfact {qid}\nmore",
        "chunk_id": f"{qid}-1"}
hit = "[hit]" in q or q.startswith("again ")
ev = (fill[:2] + [gold] + fill[2:]) if hit else fill
print(json.dumps({"ok": True, "result": {"stopping_reason": "BUDGET", "evidence": ev, "rerank": rerank,
                                         "facets": facets, "continuation": None}}))
'''


def git(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True).stdout.strip()


def build(base: Path) -> dict:
    clone, root = base / "clone", base / "sets"
    (clone / "docs/q").mkdir(parents=True)
    (clone / "governance/project").mkdir(parents=True)
    ids = [f"v{i:02d}" for i in range(1, 81)] + [f"c{i:02d}" for i in range(1, 41)]
    for qid in ids:
        (clone / f"docs/q/{qid}.md").write_text(f"# Topic {qid}\nfact {qid}\nmore\n")
    for k in range(1, 7):
        (clone / f"docs/fill{k}.md").write_text(f"filler {k}\nline\n")
    (clone / "governance/project/path-map.yaml").write_text(FAMILIES_MAP)
    (clone / "governance/project/retrieval.yaml").write_text(POOL)
    (clone / ".gitignore").write_text(".gov-runtime/\n")
    git(base, "init", "-q", str(clone))
    git(clone, "config", "user.email", "t@t")
    git(clone, "config", "user.name", "t")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "planted")
    git(clone, "branch", "w2/integrate")
    head = git(clone, "rev-parse", "HEAD")
    (clone / ".gov-runtime").mkdir()
    db = sqlite3.connect(clone / ".gov-runtime/store.db")
    db.execute("CREATE TABLE lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT, path TEXT, start_line INTEGER, "
               "end_line INTEGER, parent_id TEXT)")
    db.executemany("INSERT INTO lexical_chunk (chunk_id, path, start_line, end_line, parent_id) VALUES (?,?,?,?,?)",
                   [(f"{q}-1", f"docs/q/{q}.md", 1, 3, q) for q in ids])
    db.commit()
    db.close()
    (root / "governance/project").mkdir(parents=True)
    (root / "governance/project/path-map.yaml").write_text(SETS_MAP)
    hid = root / "fixtures/evaluation/memory-verdict-2/hidden"
    vis = root / "fixtures/evaluation/memory-retrieval/visible"
    hid.mkdir(parents=True)
    vis.mkdir(parents=True)
    for i in range(1, 81):
        qid = f"v{i:02d}"
        if qid == "v80":
            cat, text = "nonexistent-id", "planted question v80: where is DEC-99999 recorded?"
        else:
            cat = "decision"
            text = f"planted question {qid} {'[miss]' if qid in MISS_IDS else '[hit]'}"
        doc = {"id": qid, "category": cat, "commit": head[:12], "question": text, "gold_answer": f"gold {qid}",
               "sources": [{"path": f"docs/q/{qid}.md", "heading": f"# Topic {qid}", "lines": [1, 3]}]}
        (hid / f"{qid}.yaml").write_text("# DEC-1074 (3), the verdict set of 80\n" + json.dumps(doc))
    for i in range(1, 41):
        qid = f"c{i:02d}"
        doc = {"id": qid, "category": "decision", "commit": head[:12],
               "question": f"control {qid} {'[miss]' if qid in CONTROL_MISS else '[hit]'}", "gold_answer": "x",
               "sources": [{"path": f"docs/q/{qid}.md", "heading": f"# Topic {qid}", "lines": [1, 3]}]}
        (vis / f"{qid}.yaml").write_text(json.dumps(doc))
    os.chmod(hid, 0o700)
    old = 1761955200  # 2025-11-01: before DEC-1078's close
    for f in hid.glob("*.yaml"):
        os.utime(f, (old, old))
    # the main tree (ACT-GUARD-SETS-1 applied, the declaration's home): a git repository with w2/integrate
    main = base / "main"
    (main / "governance/project").mkdir(parents=True)
    (main / ".claude/hooks").mkdir(parents=True)
    (main / "governance/project/orchestration/packages/LIFT-1").mkdir(parents=True)
    (main / "governance/project/path-map.yaml").write_text(act_block(root))
    (main / ".claude/hooks/pretooluse.py").write_text(
        'SETS_BLOCK = "sets_root_hidden"\n\n\ndef sets_root_rule(main):\n    return None\n')
    git(base, "init", "-q", str(main))
    git(main, "config", "user.email", "t@t")
    git(main, "config", "user.name", "t")
    git(main, "add", "-A")
    git(main, "commit", "-q", "-m", "act applied")
    git(main, "branch", "w2/integrate")
    gov = base / "fake_gov.py"
    gov.write_text(FAKE_GOV)
    gov.chmod(gov.stat().st_mode | stat.S_IEXEC)
    return {"base": base, "clone": clone, "root": root, "head": head, "gov": gov, "hidden": hid, "main": main}


def act_block(root) -> str:
    return (f'sets_root_hidden:\n  root: "{root}"\n'
            '  hidden: ["fixtures/evaluation/memory-retrieval/hidden/**", "fixtures/evaluation/memory-verdict/**",\n'
            '           "fixtures/evaluation/memory-verdict-2/**", "transcripts/**", "runs/fresh-80/**"]\n'
            '  refused_roles: [orchestrator, engineer, research, product-spec, independent-test-designer, '
            'independent-auditor]\n')


DECL = "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md"


def declare(planted, digest=None, blanks=False, commit=True):
    """The declaration in the planted main tree, its digest filled (the set's now unless given), committed."""
    import f80lib as L
    d = digest or L.set_digest(planted["root"])
    text = f"# The fresh 80, declared\n- **Its digest** (item 1): `{d}`.\n- ACT applied at `abc`.\n"
    if blanks:
        text += "- the interval: ____\n"
    f = planted["main"] / DECL
    f.write_text(text)
    if commit:
        git(planted["main"], "add", "-A")
        git(planted["main"], "commit", "-q", "-m", "declared")


@pytest.fixture(scope="session")
def template(tmp_path_factory):
    return build(tmp_path_factory.mktemp("planted-template"))


@pytest.fixture
def planted(template, tmp_path):
    base = tmp_path / "p"
    shutil.copytree(template["base"], base, symlinks=True)
    out = {k: (base / Path(v).relative_to(template["base"]) if isinstance(v, Path) else v) for k, v in template.items()}
    out["base"] = base
    # the copy's own sets root in the main tree's ACT block
    (out["main"] / "governance/project/path-map.yaml").write_text(act_block(out["root"]))
    git(out["main"], "commit", "-q", "-am", "the copy's root")
    return out
