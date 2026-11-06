"""L5 in the score-once harness copy (DEC-1079 L5, DEC-1084): ``split`` and ``termmap`` ported from the research
harness (a5c0c34f, ``l5_check.py``'s checks ported here, its score log not). No model, no reranker, no store, no GPU,
no ``gov retrieve``; every question here is made up for the check, and no evaluation set is read.

    python3 test_rx_l5.py

1. **The pure functions** (``_split_parts``, ``_named_things``, ``_termmap_from``, ``_termmap_phrase``), taken from
   rx.py's source by name, with l5_check.py's cases.
2. **Only L5 changed:** ``rx.pre-l5.py`` is the reviewed copy the live window ran (its sha256 is LIVE-REVIEWED's
   rx.py line); every line the port removed from it is one of the four L5 needs to change.
3. **The no-op:** with both switches off, rx.py and rx.pre-l5.py, each imported (``GOV_RX_NO_MAIN=1``) in a child
   process with the same stand-ins for the store's routes and the reranker, driven through the clone's own
   ``retrieve`` order of calls: every search asked, every text given to the reranker (and to whom), the fused list
   and the final evidence equal, for the score-once variants (v456; with ``rq``; with ``lift_norm``; L2's
   ``routing`` sentinel and ``ahead_types``) and l5_check's others, on a tree with ``routing.phrasings`` on and off.
4. **L5 on:** the reranker's text equal to L5 off (with ``rq`` and without), the extras searched after the product's
   phrasings, the marker this question's alone and a union under nested calls, the term map's phrasing; the two
   refusals; the term map's cache by root and commit.
5. **Extend, then replay** (the extend window and replay.sh's form, on a socket stand-in for the trial service): a
   variant run in trial mode into a copy of a kept cache (scores and meta kept) scores only the texts the kept cache
   lacks; replayed with GOV_RX_COMBINE (``alone`` over that cache, the route answers copied with scores and meta
   removed) it gives the same evidence, with no reranker asked; for ``split`` and for ``depth`` 80.
"""
import ast
import difflib
import hashlib
import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
RX, BEFORE = HERE / "rx.py", HERE / "rx.pre-l5.py"
CLONE_SRC = Path.home() / "gov-os-runs/D4B/g1/repo/src"
V456 = {"sem_uncut": True, "sem_k": 60, "lex_k": 60, "depth": 40, "perfile": 2, "dedup": True}
V456RQ = {**V456, "rq": "question"}
L3 = {**V456RQ, "lift_norm": 0.0766}
RESULTS: list[bool] = []


def report(name: str, passed: bool, detail: str = "") -> None:
    RESULTS.append(bool(passed))
    print(f"{'ok  ' if passed else 'FAIL'} {name}{': ' + detail if detail and not passed else ''}")


# ---------------------------------------------------------------- 1. the pure functions, from rx.py's source
PURE = {"_STOP", "_ASK", "_ASK_AFTER", "_ENUM", "_ROMAN", "_ID", "_NAMED_CAND", "_ID_DOTTED", "_EXT", "_FRONTED",
        "_GLUE", "_TOKEN", "_HUMP", "_ACR_AFTER", "_ACR_BEFORE", "_named_thing", "_named_things", "_content",
        "_enumerated", "_split_parts", "_parts", "_fold", "_compound", "_acr_expansion", "_termmap_from",
        "_termmap_phrase"}


def pure_namespace(path: Path) -> dict:
    ns = {"re": re}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        names = ([node.name] if isinstance(node, ast.FunctionDef) else
                 [t.id for t in node.targets if isinstance(t, ast.Name)] if isinstance(node, ast.Assign) else [])
        if any(n in PURE for n in names):
            exec(compile(ast.Module([node], []), str(path), "exec"), ns)
    missing = PURE - set(ns)
    if missing:
        raise SystemExit(f"test_rx_l5: rx.py lacks {sorted(missing)}")
    return ns


def check_pure() -> None:
    ns = pure_namespace(RX)
    split, named = ns["_split_parts"], ns["_named_things"]
    cases = [
        ("Who decided DEC-820? What did it change?", ["Who decided DEC-820?", "What did it change? DEC-820"]),
        ("(1) what is CAP-33 (2) which skill covers audits", ["what is CAP-33", "which skill covers audits CAP-33"]),
        ("What does the guard refuse and which paths may a worker write?",
         ["What does the guard refuse", "which paths may a worker write?"]),
        ("In the guard, what is refused and what is allowed?",
         ["In the guard, what is refused?", "In the guard, what is allowed?"]),
        ("Which roles exist in W2-40, and also how are they launched?",
         ["Which roles exist in W2-40", "how are they launched? W2-40"]),
        ("List a) the ticket's allowed_paths b) the role's tools",
         ["List the ticket's allowed_paths", "List the role's tools allowed_paths"]),
        ("We moved the store. Where is it now? Who reads it?", ["We moved the store. Where is it now?",
                                                                "We moved the store. Who reads it?"]),
        ("(1) what is A-1 (2) what is B-2 (3) what is C-3 (4) what is D-4 (5) what is E-5",
         ["what is A-1 B-2 C-3 D-4 E-5", "what is B-2 A-1 C-3 D-4 E-5", "what is C-3 A-1 B-2 D-4 E-5",
          "what is D-4 A-1 B-2 C-3 E-5"]),
    ]
    bad = [(q, split(q)) for q, want in cases if split(q) != want]
    report(f"1 split: the parts of {len(cases)} two-ask questions", not bad, f"{bad}")
    ones = ("What does the guard refuse?", "Who wrote the register and why?",
            "What is the difference between tickets and waves?", "Does the guard allow read/write and/or installs?",
            "How? Why?", "(1) the guard")
    bad = [(q, split(q)) for q in ones if split(q) != []]
    report(f"1b split refuses {len(ones)} one-ask questions", not bad, f"{bad}")
    text = ("Use e.g. src/gov/retrieval/routing.py and/or `gov retrieve`, routing.phrasings, allowed_paths, DEC-820, "
            "CAP-24.b, i.e. docs/research and read/write, a/b/c")
    want = ["src/gov/retrieval/routing.py", "`gov retrieve`", "routing.phrasings", "allowed_paths", "DEC-820",
            "CAP-24.b", "a/b/c"]
    report("1c named things: ids, paths, dotted and snake_case names, quoted spans; not and/or, e.g., word pairs",
           named(text) == want, f"{named(text)}")
    swap = {"DEC-820": "ADR-7", "CAP-33": "RISK-12", "W2-40": "Q-9", "guard": "planner", "store": "index",
            "allowed_paths": "held_items"}
    same = True
    for q, _ in cases[:7]:
        q2 = q
        for a, b in swap.items():
            q2 = q2.replace(a, b)
        p1 = split(q)
        for a, b in swap.items():
            p1 = [p.replace(a, b) for p in p1]
        same &= p1 == split(q2)
    report("1d split is structural: other names in the same forms give the same parts", same)

    build, phrase = ns["_termmap_from"], ns["_termmap_phrase"]
    labels = ["The allowed_paths of a ticket", "Held-out material", "Long Form (LF) answers", "Re-rank budget",
              "The rerank pass", "Retrieval Augmented Generation (RAG)", "Random Access Generation (RAG)",
              "DEC-820 Reads are open", "Budget", "Command Line Interface (CLI)"]
    symbols = ["allowed_paths", "held_out", "ScoreLog", "score_log", "read_block"]
    tmap = build(labels, symbols)
    report("1e term map: compounds, one spelling per word sequence",
           tmap["compound"].get("allowedpath") == "allowed_paths" and tmap["compound"].get("heldout") == "Held-out"
           and tmap["compound"].get("scorelog") == "ScoreLog")
    report("1f term map refuses an ambiguous compound (re-rank and rerank)", "rerank" not in tmap["compound"])
    report("1g term map: an acronym defined in a label, both ways", tmap["acronym"].get("LF") == "Long Form"
           and tmap["expansion"].get("long form") == "LF" and tmap["acronym"].get("CLI") == "Command Line Interface")
    report("1h term map refuses an acronym with two expansions (RAG), never maps an id, is order-free",
           "RAG" not in tmap["acronym"] and not any(a == "RAG" for a in tmap["expansion"].values())
           and not any("820" in k for k in tmap["compound"])
           and build(list(reversed(labels)), list(reversed(symbols))) == tmap)
    mapped = [("Which allowed paths does a ticket hold?", "Which allowed_paths does a ticket hold?"),
              ("Who may read held out material?", "Who may read Held-out material?"),
              ("Where is the score log written?", "Where is the ScoreLog written?"),
              ("When is an LF answer required?", "When is an Long Form (LF) answer required?"),
              ("When is a long form answer required?", "When is a Long Form (LF) answer required?"),
              ("Which flags does the CLI take?", "Which flags does the Command Line Interface (CLI) take?")]
    bad = [(q, phrase(q, tmap)) for q, want in mapped if phrase(q, tmap) != want]
    report(f"1i term map phrases {len(mapped)} questions in the record's words", not bad, f"{bad}")
    alone = ("How deep is the re rank?", "What is RAG?", "What did DEC-820 decide?", "What does the budget hold?",
             "Which allowed_paths does a ticket hold?", "When is a Long Form (LF) answer required?")
    bad = [(q, phrase(q, tmap)) for q in alone if phrase(q, tmap) is not None]
    report(f"1j term map leaves {len(alone)} questions alone", not bad, f"{bad}")


# ---------------------------------------------------------------- 2. only L5 changed
def check_diff() -> None:
    pin = (HERE / "LIVE-REVIEWED.sha256").read_text().splitlines()
    want = next((line.split()[0] for line in pin if line.endswith("/rx.py")), None)
    got = hashlib.sha256(BEFORE.read_bytes()).hexdigest()
    report("2 rx.pre-l5.py is the reviewed rx.py the live window ran (LIVE-REVIEWED.sha256)", got == want,
           f"{got[:12]} vs {str(want)[:12]}")
    old, new = BEFORE.read_text().splitlines(), RX.read_text().splitlines()
    removed = [line for line in difflib.ndiff(old, new) if line.startswith("- ")]
    allowed = {
        "-   any file, in each call (D4B-STRUCTURE E1: generated and copied texts take one place).",
        "-     return list(dict.fromkeys(p for p in out if p.strip()))",
        '-     STATE["query"], STATE["root"] = query, Path(root)',
        '- CUSTOM = bool(set(V) - {"exclude", "chars", "sem_k", "lex_k", "sem_uncut"}) or bool(EXCLUDE)',
    }
    report("2b the port removed only the four lines L5 changes (docstring, _phrasings, _lex, CUSTOM)",
           set(removed) <= allowed and len(removed) == 4, f"{removed}")
    added = [line[2:] for line in difflib.ndiff(old, new) if line.startswith("+ ")]
    code = [line for line in added if re.search(r"^\s*SCORELOG\s*=|_scorelog|os\.environ.*SCORELOG", line)]
    report("2c no score log ported (no SCORELOG setting, no score-log writer)", not code, f"{code}")


# ---------------------------------------------------------------- 3.-5. the harness in child processes
CHILD = r'''
import hashlib, importlib.util, json, os, sys
from pathlib import Path
rx_path, mode = sys.argv[1], sys.argv[2]
args = json.loads(sys.argv[3])
spec = importlib.util.spec_from_file_location("rx_l5", rx_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
from gov import records
from gov.retrieval import authority, graph_route, lexical, routing, semantic
from gov.retrieval import retrieve as rt
H = lambda s: hashlib.sha256(s.encode()).hexdigest()
N = args.get("n", 30)  # the extend checks widen the pool (more chunks, more hits a word) so depth 80 reaches past 40
SPREAD = args.get("spread", [0, 7])
CH = {}
for i in range(N):
    sub = "high" if i % 7 == 0 else "low"
    path = f"docs/{sub}/f{i // 3:02d}.md"
    start = 1 + (i % 3) * 4 if i % 3 != 2 else 2
    end = start + (3 if i % 3 != 2 else 1)
    CH[f"c{i:02d}"] = {"chunk_id": f"c{i:02d}", "path": path, "start_line": start, "end_line": end}
LOG = {"lex": [], "sem": [], "rr": []}
def hits_of(q, salt, top):
    out = []
    for w in sorted(set(q.lower().replace("?", " ").split())):
        for k in SPREAD:
            cid = f"c{(int(H(salt + w), 16) + k) % N:02d}"
            if cid not in out:
                out.append(cid)
    return out[:top]
def lex(root, q, refresh=True):
    LOG["lex"].append(q)
    hits = [{**CH[c], "bm25": -1.0 - r / 10} for r, c in enumerate(hits_of(q, "l", lexical.TOP_K))]
    return {"available": True, "reason": None, "hits": hits, "ranked": hits}
def sem(root, q, refresh=True):
    LOG["sem"].append(q)
    hits = [{**CH[c], "distance": 0.1 + r / 100} for r, c in enumerate(hits_of(q, "s", semantic.TOP_K))]
    return {"available": True, "reason": None, "hits": hits}
def start_ids(root, q, known):
    import re
    found = re.findall(r"\b[A-Z][A-Z0-9]*-\d+\b", q)
    return found + (["W2-99"] if "guard" in q.lower() else [])
def fake_scores(query, texts):
    LOG["rr"].append([query, [H(t) for t in texts]])
    return [int(H(query + "\x00" + t)[:8], 16) / 4e9 for t in texts]
mod._lex_memo, mod._sem_memo = lex, sem
if not args.get("real"):  # "real": rx.py's own scores() (the trial switch or GOV_RX_COMBINE), its GPU read replaced
    mod.scores = fake_scores
mod._gpu_used = lambda: 1000
mod._chunks_rt = lambda root, path=None: [dict(c) for c in CH.values()]
graph_route.start_ids = start_ids
records.records = lambda root, **kw: []
def drive(root, query, **kw):
    root = Path(root)
    settings = routing.settings(root)
    order = authority.order(root, [], [], lambda p, s: None)
    asked = [query]
    if settings["phrasings"]:
        asked = routing.phrasings(query, graph_route.start_ids(root, query, []))
    answers = {"lexical": rt._phrased(lexical.search, root, asked, "ranked"),
               "semantic": rt._phrased(semantic.search, root, asked, "hits", cut=semantic.TOP_K)}
    routes = {name: a.get("ranked", a["hits"]) for name, a in answers.items()}
    chunks = {c["chunk_id"]: c for c in lexical.chunks(root)}
    routes["closure"] = [dict(CH[c]) for c in ("c03", "c10", "c21")]
    fused = order.fused(rt.rrf(routes), chunks)
    page = []
    for h in fused[:20]:
        c = chunks[h["chunk_id"]]
        body = b"".join((root / c["path"]).read_bytes().splitlines(keepends=True)[c["start_line"] - 1:c["end_line"]])
        page.append({**c, "routes": h["routes"], "text": f"[path: {c['path']}]\n{body.decode()}"})
    ranked = order.reranked(rt.rerank(query, page, None))
    ranked, moved = routing.ahead(ranked, [routes["closure"][0]["chunk_id"]])
    return {"evidence": [{k: c[k] for k in ("chunk_id", "path", "start_line", "end_line", "text")} for c in ranked],
            "fused": [h["chunk_id"] for h in fused]}
mod._retrieve = drive
out = []
if mode == "flow":
    for q in args["questions"]:
        for k in LOG:
            LOG[k] = []
        bundle = rt.retrieve(args["root"], q)
        out.append({"lex": LOG["lex"], "sem": LOG["sem"], "rr": LOG["rr"], "fused": bundle["fused"],
                    "evidence": [e["chunk_id"] for e in bundle["evidence"]], "state_query": mod.STATE["query"],
                    "extra": sorted(mod.STATE.get("extra", ()))})
    if args.get("nested"):
        q = args["questions"][0]
        mod.STATE["extra"] = set()
        first = mod._extras(q, [q])
        mod._extras(first[0], [first[0]]) if first else None
        out.append({"nested_kept": all(p in mod.STATE["extra"] for p in first), "first": first})
elif mode == "termmap":
    calls = []
    real = mod._harvest
    def counted(root):
        calls.append(str(root))
        return real(root)
    mod._harvest = counted
    maps = {r: mod._termmap(Path(r)) for r in args["roots"]}
    again = {r: mod._termmap(Path(r)) for r in args["roots"]}
    out = {"harvests": len(calls), "acronyms": {r: sorted(m["acronym"]) for r, m in maps.items()},
           "same_again": all(maps[r] is again[r] for r in args["roots"])}
print(json.dumps(out))
'''


def child(rx: Path, mode: str, args: dict, variant: dict, home: Path, cache: Path, extra_env: dict | None = None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
    env.update({"HOME": str(home), "GOV_RX_NO_MAIN": "1", "GOV_RX": json.dumps(variant), "GOV_RX_CACHE": str(cache),
                "PYTHONPATH": str(CLONE_SRC), **(extra_env or {})})
    got = subprocess.run([sys.executable, "-c", CHILD, str(rx), mode, json.dumps(args)], env=env,
                         capture_output=True, text=True, timeout=300)
    if got.returncode != 0:
        return None, got
    return json.loads(got.stdout.strip().splitlines()[-1]), got


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=l5", "-c", "user.email=l5@check", "-c",
                           "commit.gpgsign=false", *a], capture_output=True, text=True, check=True)


def tree(base: Path, phrasings: bool) -> Path:
    """A made-up tree: the routing setting, an authority block, 20 files (some texts copied), one heading that
    defines an acronym; the tree with phrasings on is a git repository (so the term map harvests it)."""
    root = base / ("root-on" if phrasings else "root-off")
    (root / "governance/project").mkdir(parents=True)
    (root / "governance/project/retrieval.yaml").write_text(f"routing:\n  phrasings: {str(phrasings).lower()}\n")
    (root / "governance/project/path-map.yaml").write_text(
        "retrieval_authority:\n  lift: {fused: 0.004, rerank: 1.0}\n  default: plain\n  tiers:\n"
        "    - name: high\n      paths: ['docs/high/**']\n    - name: plain\n")
    for sub in ("high", "low"):
        (root / "docs" / sub).mkdir(parents=True)
        for f in range(40):  # chunk i lies in file i // 3: 40 files hold the extend checks' 120 chunks
            same ="The same paragraph, copied into several files, word for word, so its text repeats here." * 2
            lines = [same if (f % 4 == 0 and n < 4) else f"{sub} file {f} line {n} " + "w" * (n * 7 % 50)
                     for n in range(1, 13)]
            if sub == "low" and f == 9:
                lines[0] = "# Long Form (LF) answers"
            (root / "docs" / sub / f"f{f:02d}.md").write_text("\n".join(lines) + "\n")
    if phrasings:
        git(root, "init", "-q")
        git(root, "add", "docs", "governance")
        git(root, "commit", "-q", "-m", "l5 check tree")
    return root


QUESTIONS = ["Who decided DEC-820? What did it change?",
             "What does the guard refuse and which allowed paths may a worker write?",
             "How is the long form answer scored?",
             "(1) what is CAP-33 (2) which skill covers audits",
             "Where is the score log written?"]
KEYS = ("lex", "sem", "rr", "fused", "evidence", "state_query")


def strip(rows):
    return [{k: r[k] for k in KEYS} for r in rows]


def check_harness(base: Path) -> None:
    home = base / "home"
    home.mkdir()  # no reranker venv under it: rx.py's default_reranker() is None, nothing is contacted
    on, off = tree(base, True), tree(base, False)
    n = [0]

    def run(rx, mode, args, variant, extra_env=None):
        n[0] += 1
        return child(rx, mode, args, variant, home, base / f"cache-{n[0]}", extra_env)

    variants = [("shipped", {}, on), ("shipped", {}, off), ("v456", V456, on), ("v456", V456, off),
                ("v456 rq", V456RQ, on), ("v456 rq lift_norm (L3)", L3, on), ("v456 rq lift_norm (L3)", L3, off),
                ("L2's routing sentinel and ahead types", {**L3, "routing": {"code_first": 0, "named_first": 0},
                                                           "ahead_types": []}, on),
                ("v456+rinstr", {**V456, "rinstr": True}, on), ("harness phrasings", {"phrasings": True}, off),
                ("both phrasings layers", {"phrasings": True, "depth": 10}, on),
                ("expand", {"phrasings": True, "expand": "both", "depth": 10}, off),
                ("blend/pin/front/perfile", {"rinstr": True, "blend": {"w": 0.5, "k": 10}, "pin": ["lexical"],
                                             "front": {"semantic": 1}, "perfile": 1}, on),
                ("dedup_text+decorate", {"dedup_text": True, "decorate": True, "depth": 15}, on),
                ("minmax+quota", {"fuse": "minmax", "quota": 2, "depth": 12}, on),
                ("switches present but false", {**L3, "split": False, "termmap": False}, on)]
    flows, bad = {}, []
    for name, variant, root in variants:
        args = {"root": str(root), "questions": QUESTIONS}
        old, p_old = run(BEFORE, "flow", args, {k: v for k, v in variant.items() if k not in ("split", "termmap")})
        new, p_new = run(RX, "flow", args, variant)
        if old is None or new is None:
            bad.append(f"{name} at {root.name}: child failed: {(p_old.stderr or p_new.stderr)[-300:]}")
            continue
        if strip(old) != strip(new):
            bad.append(f"{name} at {root.name}")
        flows[(name, root.name)] = new
    report(f"3 no-op: L5 off equals the reviewed copy for {len(variants)} variant-tree pairs (searches, reranker "
           f"texts, fused lists, evidence)", not bad, f"{bad}")

    for name, variant, root, off_key in [
            ("split on L3", {**L3, "split": True}, on, ("v456 rq lift_norm (L3)", "root-on")),
            ("termmap on L3", {**L3, "termmap": True}, on, ("v456 rq lift_norm (L3)", "root-on")),
            ("split+termmap on L3", {**L3, "split": True, "termmap": True}, on, ("v456 rq lift_norm (L3)", "root-on")),
            ("split on v456 (no rq)", {**V456, "split": True}, on, ("v456", "root-on")),
            ("split on the harness phrasings", {"phrasings": True, "split": True}, off, ("harness phrasings", "root-off")),
            ("split on the shipped path", {"split": True}, on, ("shipped", "root-on"))]:
        off_rows = flows.get(off_key)
        got, proc = run(RX, "flow", {"root": str(root), "questions": QUESTIONS, "nested": True}, variant)
        if got is None or off_rows is None:
            report(f"4 L5 {name}", False, f"child failed: {proc.stderr[-400:]}")
            continue
        nested, rows = got[-1], got[:-1]
        report(f"4 L5 {name}: the reranker's text is the one L5 off gives",
               [[q for q, _ in r["rr"]] for r in rows] == [[q for q, _ in r["rr"]] for r in off_rows])
        appended = all(r["lex"][:len(o["lex"])] == o["lex"] and r["sem"][:len(o["sem"])] == o["sem"]
                       for r, o in zip(rows, off_rows))
        extras = [r["extra"] for r in rows]
        own = all(set(e) <= set(r["lex"]) and set(e) <= set(r["sem"]) for e, r in zip(extras, rows))
        report(f"4 L5 {name}: extras searched after L5 off's phrasings (both routes), the marker this question's, "
               f"the run distinguishable from L5 off", appended and own and any(extras) and strip(rows) != strip(off_rows),
               f"extras per question {[len(e) for e in extras]}")
        report(f"4 L5 {name}: a nested phrasing call keeps the question's marks (union)", nested["nested_kept"])
        if variant.get("termmap"):
            want = "How is the Long Form (LF) answer scored?"
            report(f"4 L5 {name}: the term map's phrasing, from the tree's own heading, searched", want in extras[2],
                   f"{extras[2]}")

    for name, variant, root, word in [("neither phrasings layer", {**L3, "split": True}, off, "it would measure nothing"),
                                      ("both phrasings layers", {**L3, "split": True, "phrasings": True}, on,
                                       "phrased again")]:
        got, proc = run(RX, "flow", {"root": str(root), "questions": QUESTIONS[:1]}, variant)
        report(f"4 L5 refuses {name}", got is None and proc.returncode != 0 and word in proc.stderr,
               (proc.stderr.strip().splitlines() or [""])[-1][:200])

    repos = []
    for name, heading in (("repo-a", "# Long Form (LF) answers\n"), ("repo-b", "# Command Line Interface (CLI)\n")):
        repo = base / name
        (repo / "docs").mkdir(parents=True)
        (repo / "docs/a.md").write_text(heading)
        git(repo, "init", "-q")
        git(repo, "add", "docs/a.md")
        git(repo, "commit", "-q", "-m", "l5 check")
        repos.append(str(repo))
    cache = base / "cache-termmap"
    tm = lambda roots: child(RX, "termmap", {"roots": roots}, {"split": False, "termmap": True}, home, cache)
    one, p1 = tm(repos)
    report("4 term map per root: two maps, each built once in a process", one is not None and one["harvests"] == 2
           and one["acronyms"] == {repos[0]: ["LF"], repos[1]: ["CLI"]} and one["same_again"],
           f"{one if one else p1.stderr[-300:]}")
    two, _ = tm(repos)
    report("4 term map cached by root and commit across processes", two is not None and two["harvests"] == 0)
    Path(repos[0], "docs/b.md").write_text("# Data Retention Policy (DRP)\n")
    git(repos[0], "add", "docs/b.md")
    git(repos[0], "commit", "-q", "-m", "l5 check 2")
    three, _ = tm([repos[0]])
    report("4 term map rebuilt for a new commit", three is not None and three["harvests"] == 1
           and three["acronyms"][repos[0]] == ["DRP", "LF"], f"{three}")
    Path(repos[1], "docs/a.md").write_text("# Command Line Interface (CLI)\n# Unit Test Plan (UTP)\n")
    four, _ = tm([repos[1]])
    five, _ = tm([repos[1]])
    report("4 term map of a tree with changed tracked files: built afresh, never persisted", four is not None
           and five is not None and four["harvests"] == 1 and five["harvests"] == 1)
    check_extend(base, on)


# ---------------------------------------------------------------- 5. extend, then replay
class StandIn:
    """The trial service's socket: one request at a time; scores by a digest of (query, text); counts texts."""

    def __init__(self, path: Path):
        self.texts = 0
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(str(path))
        self.sock.listen(16)
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            with conn:
                q, texts = json.loads(conn.makefile("rb").readline())
                self.texts += len(texts)
                scores = [int(hashlib.sha256((q + "\x00" + t).encode()).hexdigest()[:8], 16) / 4e9 for t in texts]
                conn.sendall((json.dumps({"scores": scores, "device": "cpu"}) + "\n").encode())


def count(db: Path) -> int:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return con.execute("SELECT COUNT(*) FROM score").fetchone()[0]
    finally:
        con.close()


def copy_kept(src: Path, dst: Path, keep_scores: bool) -> None:
    """The extend window's copy (scores and meta kept) or replay.sh's (both removed), by sqlite's backup."""
    dst.mkdir(parents=True)
    a, b = sqlite3.connect(src / "cache.db"), sqlite3.connect(dst / "cache.db")
    a.backup(b)
    if not keep_scores:
        b.execute("DELETE FROM score")
        b.execute("DELETE FROM meta")
        b.commit()
    a.close()
    b.close()


def check_extend(base: Path, root: Path) -> None:
    home = base / "home-trial"  # the product client's interpreter check needs a file there; nothing runs it
    (home / ".local/share/gov-os/reranker-venv/bin").mkdir(parents=True)
    (home / ".local/share/gov-os/reranker-venv/bin/python").write_text("")
    svc = base / "svc"
    svc.mkdir()
    stand = StandIn(svc / "rerank.sock")
    model = "Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473"
    trial = {"GOV_RX_RERANK_DIR": str(svc), "GOV_RX_RERANK_MODEL": model, "GOV_RX_GPU_LIMIT_MIB": "14255"}
    args = {"root": str(root), "questions": QUESTIONS, "real": True, "n": 120, "spread": [0, 7, 13, 19, 29, 37]}
    kept = base / "kept-q06"
    got, proc = child(RX, "flow", args, L3, home, kept, trial)
    report("5 the kept cache: L3 run in trial mode against the stand-in", got is not None and count(kept / "cache.db")
           == stand.texts > 0, proc.stderr[-300:])
    for name, variant in (("split", {**L3, "split": True}), ("depth 80", {**L3, "depth": 80}),
                          ("split+termmap", {**L3, "split": True, "termmap": True})):
        ext = base / f"extend-{name.replace(' ', '-').replace('+', '-')}"
        copy_kept(kept, ext, keep_scores=True)
        before, asked = count(ext / "cache.db"), stand.texts
        window, proc = child(RX, "flow", args, variant, home, ext, trial)
        new = count(ext / "cache.db") - before
        report(f"5 extend {name}: only the texts the kept cache lacks are scored", window is not None and new > 0
               and stand.texts - asked == new, f"new {new}, asked {stand.texts - asked}; {proc.stderr[-300:]}")
        routes = base / f"replay-{ext.name}"
        copy_kept(ext, routes, keep_scores=False)
        combine = {"GOV_RX_COMBINE": json.dumps({"models": {"q06": model}, "caches": {"q06": str(ext)},
                                                 "rule": {"kind": "alone", "m": "q06"}})}
        asked = stand.texts
        replay, proc = child(RX, "flow", args, variant, home, routes, combine)
        report(f"5 replay {name}: alone q06 over the extended cache gives the window's evidence, no reranker asked",
               replay is not None and window is not None and [r["evidence"] for r in replay]
               == [r["evidence"] for r in window] and [r["fused"] for r in replay] == [r["fused"] for r in window]
               and stand.texts == asked, proc.stderr[-300:])
    combine = {"GOV_RX_COMBINE": json.dumps({"models": {"q06": model}, "caches": {"q06": str(kept)},
                                             "rule": {"kind": "alone", "m": "q06"}})}
    routes = base / "replay-kept-depth80"
    copy_kept(kept, routes, keep_scores=False)
    got, proc = child(RX, "flow", args, {**L3, "depth": 80}, home, routes, combine)
    report("5 a replay of depth 80 over the 40-candidate kept cache stops (texts not scored): the extension is needed",
           got is None and "were not scored by q06 in the window" in proc.stderr, proc.stderr[-200:])


def main() -> int:
    check_pure()
    check_diff()
    with tempfile.TemporaryDirectory(prefix="rxl5-") as tmp:
        check_harness(Path(tmp))
    print(f"{sum(RESULTS)} of {len(RESULTS)} passed")
    return 0 if all(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
