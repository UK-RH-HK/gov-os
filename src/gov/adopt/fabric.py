"""A9 lite: the memory fabric of an adopted repository (W2-88 S3 to S6, S10, S11, S18 to S23; CAP-44.f by CIT-P note).

``a9(run)`` builds the stores with ``gov.rebuild.command.run`` in full (under W2-76's lock, so never two rebuilds at
once: a second one waits), judges every tracked file (indexed, or named with its reason), checks the four per-store
digests and the standard (S10), measures the scale and the questions it is given (no bar: a low figure is a named
residual), and writes the audit's records for the repository's owner (S18 to S23). It starts no audit, writes no
crontab line and applies no ACT; its one write in the repository is the stage's record, committed as every stage's is.

Not ok (a refusal that writes no record): ``FABRIC_INCOMPLETE`` (a tracked file in neither list of the store that
judges it, or a store the path map calls for not built), ``STANDARD_DEPARTURE`` (a setting differs from ``STANDARD``
and no ``--decision`` names it) and ``DIGESTS_INCOMPLETE`` (a rebuild record without its four digests).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import resource
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from gov.adopt import assess, memory_sets, project
from gov.cli.errors import GovError
from gov.memaudit import declare

GOV_OS = Path(__file__).resolve().parents[3]
RETRIEVE_BUDGET_MS = 2000  # proposed (W2-88-evidence.md, seams, item 1): the code states no budget for the vector scan
PLAIN_QUESTION = "where is the project's configuration defined"
DIGEST_KEYS = ("record", "lexical", "vectors", "codegraph_bytes")
JUDGING = ("lexical", "vectors", "codegraph")  # the stores whose lists cover the tracked files (the record store reports)
REASONS = ("secrets", "binary", "not-embedded", "unsupported-language", "over-limit", "not-indexed")
DECISION = re.compile(r"DEC-[0-9]+(?::[a-z_]+)?")
SETTINGS = ("reranker", "reranker_service", "pool", "bundle_tokens", "widen")


def _shipped_pool() -> dict:
    """The ``pool:`` block of ``governance/project/retrieval.yaml`` as Gov OS ships it."""
    try:
        block = yaml.safe_load((GOV_OS / "governance/project/retrieval.yaml").read_text(encoding="utf-8")).get("pool")
        if isinstance(block, dict):
            return block
    except (OSError, AttributeError, yaml.YAMLError):
        pass
    return {"meaning_uncut": True, "route_depth": 60, "rerank_depth": 40, "per_file_first10": 2, "drop_nested": True}


STANDARD = {"reranker": "Qwen3-Reranker-0.6B", "reranker_service": "shared", "pool": _shipped_pool(),
            "bundle_tokens": 6000, "widen": "sections"}


# ---- the standard (S10, F7)

def _code_settings() -> dict:
    """What the pinned gov's own code says: the reranker's model and the bundle's budget."""
    from gov.retrieval import rerank, retrieve

    return {"reranker": str(rerank.MODEL).rsplit("/", 1)[-1], "bundle_tokens": retrieve.BUNDLE_BUDGET}


def settings_of(doc: dict | None) -> dict:
    """The five settings in force: the file's keys where it names them (``rerank.model``, ``rerank.service``,
    ``bundle.tokens``, ``bundle.widen``, ``pool``), else the pin's code. The pool is its ``pool_on`` word and block."""
    code = _code_settings()
    doc = doc if isinstance(doc, dict) else {}
    rerank = doc.get("rerank") if isinstance(doc.get("rerank"), dict) else {}
    bundle = doc.get("bundle") if isinstance(doc.get("bundle"), dict) else {}
    pool = doc.get("pool") if declare.pool_on(doc) else False
    return {"reranker": str(rerank.get("model", code["reranker"])).rsplit("/", 1)[-1],
            "reranker_service": rerank.get("service", STANDARD["reranker_service"]),
            "pool": pool if pool is not False else False,
            "bundle_tokens": bundle.get("tokens", code["bundle_tokens"]),
            "widen": bundle.get("widen", STANDARD["widen"])}


def departures(doc: dict | None) -> list[dict]:
    """Every setting that differs from ``STANDARD``: ``[{setting, value}]``. The pool differs only when it is off."""
    held = settings_of(doc)
    out = []
    for name in SETTINGS:
        standard, value = STANDARD[name], held[name]
        if (name == "pool" and value is False) or (name != "pool" and value != standard):
            out.append({"setting": name, "value": value})
    return out


def _covered(found: list[dict], decisions: list[str]) -> list[dict]:
    """``found`` with the decision that names each (``DEC-n`` names every departure, ``DEC-n:setting`` that one)."""
    out = []
    for item in found:
        named = next((d for d in decisions if d.partition(":")[0] and d.partition(":")[2] in ("", item["setting"])), None)
        out.append({**item, "decision": named.partition(":")[0] if named else None})
    return out


def read_standard(root: Path, decisions: list[str]) -> dict:
    """The record's ``standard`` block for the repository at ``root``; ``STANDARD_DEPARTURE`` where a setting differs
    and no decision names it. The file is read as ``gov.memaudit.declare`` reads it (``pool_on``, ``retrieval``)."""
    for each in decisions:
        if not DECISION.fullmatch(each):
            raise project.refuse("BAD_DECISION", f"--decision {each!r} is not a decision id (DEC-n or DEC-n:setting)")
    head = project.resolve(root, "HEAD")
    raw, doc = declare.retrieval(root, head)
    found = _covered(departures(doc), decisions)
    unnamed = [item["setting"] for item in found if item["decision"] is None]
    if unnamed:
        raise GovError("STANDARD_DEPARTURE", "the store would be served with " + ", ".join(unnamed) + " other than "
                       "Gov OS's standard and no --decision names it: the stage is not ok (a setting of the standard "
                       "changes only by the owner's decision)", {"settings": unnamed, "standard": {
                           key: STANDARD[key] for key in unnamed}})
    pin = declare.gov_pin(shutil.which("gov") or sys.argv[0] or "gov")
    try:
        from gov.retrieval import semantic
        embedder = (semantic.manifest(root) or {}).get("embedder")
    except Exception:  # noqa: BLE001 - no vector index here: the record says none
        embedder = None
    return {**settings_of(doc), "gov_pin": pin, "embedder": embedder,
            "retrieval_yaml_sha256": hashlib.sha256(raw).hexdigest() if raw else None, "departures": found}


# ---- the checks that refuse (F2, F3)

def check_digests(record: dict) -> None:
    """``DIGESTS_INCOMPLETE`` when any of the four per-store digests is absent from the rebuild ``record``."""
    held = record.get("digests") if isinstance(record.get("digests"), dict) else record
    missing = [key for key in DIGEST_KEYS if key not in held or held[key] is None]
    if missing:
        raise GovError("DIGESTS_INCOMPLETE", "the rebuild record lacks the per-store digest(s) " + ", ".join(missing)
                       + ": a record whose only digest is the record graph's is refused", {"missing": missing})


def check_coverage(record: dict, tracked) -> None:
    """``FABRIC_INCOMPLETE`` (``details["missing"]``: the sorted paths) for a tracked file in neither the indexed list
    nor the refused list of the store that judges it. The lexical store judges every tracked file; the vector store
    and the code graph judge theirs, and name their own lists (a store whose ``judged`` is more than its two lists hold
    leaves files unnamed)."""
    stores = record.get("stores") if isinstance(record.get("stores"), dict) else {}
    tracked, missing, short = set(tracked), set(), []
    for name in JUDGING:
        store = stores.get(name)
        if not isinstance(store, dict) or store.get("requested") is False:
            continue
        named = set(store.get("indexed") or []) | {item.get("path") for item in store.get("refused") or []
                                                  if isinstance(item, dict)}
        if name == "lexical":
            missing |= tracked - named
        else:
            gap = (store.get("judged") or 0) - len(named)
            if gap > 0:
                short.append(f"{name}: {gap} file(s) judged and in neither list")
    if missing or short:
        said = ([f"{len(missing)} tracked file(s) are in neither the indexed list nor the refused list of the store "
                 "that judges them"] if missing else []) + short
        raise GovError("FABRIC_INCOMPLETE", "; ".join(said), {"missing": sorted(missing), "short": short})


# ---- the stores' lists, read from the stores the rebuild built

def _peak() -> int:
    return max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss) * 1024


def _namespaces(run) -> dict[str, str | None]:
    try:
        return project.classify(run.config, run.tracked)
    except GovError:  # no path map: no namespace holds anything
        return {rel: None for rel in run.tracked if not rel.startswith(project.FOLDER + "/")}


def _policy(config: dict, space: str | None) -> str | None:
    spaces = (config.get("path-map.yaml") or {}).get("namespaces") if isinstance(config.get("path-map.yaml"), dict) else {}
    value = spaces.get(space) if isinstance(spaces, dict) else None
    return value.get("embedding_policy") if isinstance(value, dict) else None


def _stores(run, result: dict) -> dict:
    """Per store ``{judged, indexed[], refused[{path, reason}], chunks, vectors, nodes, edges, seconds,
    peak_rss_bytes}``. The peak is the stage's whole process (one rebuild, not one per store)."""
    from gov import codeintel
    from gov.store import STORE_REL

    namespaces, timing, peak = _namespaces(run), result.get("timing") or {}, _peak()
    base = {"chunks": 0, "vectors": 0, "nodes": 0, "edges": 0, "peak_rss_bytes": peak}
    paths = sorted(namespaces)
    db = sqlite3.connect((run.root / STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        def rows(sql):
            try:
                return db.execute(sql).fetchall()
            except sqlite3.Error:
                return []

        verdicts = {rel: state for rel, state in rows("SELECT path, indexed FROM lexical_file")}
        chunked = {path: count for path, count in rows("SELECT path, count(*) FROM lexical_chunk GROUP BY path")}
        vectored = {path for (path,) in rows("SELECT DISTINCT c.path FROM lexical_chunk c JOIN semantic_vector v "
                                             "ON v.chunk_id = c.chunk_id")}
        records = {path for (path,) in rows("SELECT DISTINCT path FROM records")}
        n_chunks, n_vectors = sum(chunked.values()), (rows("SELECT count(*) FROM semantic_vector") or [(0,)])[0][0]
    finally:
        db.close()
    lexical_i, lexical_r = [], []
    for rel in paths:
        state = verdicts.get(rel)
        if state is None:
            continue  # the keyword index holds no verdict on it: it is in neither list, and check_coverage says so
        if state == 1:
            lexical_i.append(rel)
        elif state == 2:
            lexical_r.append({"path": rel, "reason": "not-indexed"})
        else:
            try:
                binary = b"\0" in project.blob(run.root, run.tracked[rel])[:8000]
            except GovError:
                binary = False
            lexical_r.append({"path": rel, "reason": "binary" if binary else "secrets"})
    vec_i = [rel for rel in lexical_i if rel in vectored]
    vec_r = [{"path": rel, "reason": "not-embedded"} for rel in lexical_i
             if rel in chunked and rel not in vectored and _policy(run.config, namespaces[rel]) != "embedded"]
    code = [rel for rel in paths if Path(rel).suffix.lower() in assess.CODE_GRAPH_SUFFIXES | assess.OTHER_CODE_SUFFIXES]
    called_for = project.code_intelligence(run.config)
    code_i, code_r = [], []
    for rel in code if called_for else ():
        if (run.root / codeintel.BASE_REL / "files" / rel).is_file():
            code_i.append(rel)
        elif Path(rel).suffix.lower() in assess.OTHER_CODE_SUFFIXES:
            code_r.append({"path": rel, "reason": "unsupported-language"})
        else:
            code_r.append({"path": rel, "reason": "secrets" if verdicts.get(rel) == 0 else "not-indexed"})
    nodes = edges = 0
    if called_for and (code_i or code_r):
        try:
            graph, users = codeintel._graph(run.root)
            nodes, edges = len(graph), sum(len(each) for each in users.values())
        except Exception:  # noqa: BLE001 - the tool is not here: nodes and edges are asked of it, never invented
            nodes = edges = 0
    markdown = [rel for rel in paths if rel.endswith(".md")]
    return {
        "record": {**base, "judged": len(markdown), "indexed": sorted(records & set(markdown)), "refused": [],
                   "seconds": timing.get("record_s", 0.0)},
        "lexical": {**base, "judged": len(paths), "indexed": lexical_i, "refused": lexical_r, "chunks": n_chunks,
                    "seconds": timing.get("lexical_s", 0.0)},
        "vectors": {**base, "judged": len([rel for rel in lexical_i if rel in chunked]), "indexed": vec_i, "refused": vec_r, "chunks": n_chunks,
                    "vectors": n_vectors, "seconds": timing.get("semantic_s", 0.0)},
        "codegraph": {**base, "judged": len(code_i) + len(code_r), "indexed": code_i, "refused": code_r, "nodes": nodes,
                      "edges": edges, "seconds": timing.get("codeintel_s", 0.0),
                      **({} if called_for else {"requested": False})},
    }


# ---- scale and measure (S5, S6)

def search(root: Path, question: str) -> dict:  # the seam a test replaces with a stand-in
    from gov.retrieval import retrieve

    return retrieve.retrieve(root, question)


def _timed(call) -> float | None:
    start = time.perf_counter()
    try:
        call()
    except Exception:  # noqa: BLE001 - a route that cannot answer has no time: the record names it
        return None
    return round((time.perf_counter() - start) * 1000, 1)


def scale(root: Path, nodes: int, edges: int, budget_ms: int) -> dict:
    """The query time of one plain question on each route and the vector scan's time against the budget."""
    from gov.retrieval import lexical, semantic

    routes = {"lexical": _timed(lambda: lexical.search(root, PLAIN_QUESTION, refresh=False)),
              "semantic": _timed(lambda: semantic.search(root, PLAIN_QUESTION, refresh=False)),
              "retrieve": _timed(lambda: search(root, PLAIN_QUESTION))}
    return {"routes": routes, "vector_scan_ms": routes["semantic"], "budget_ms": budget_ms,
            "envelope": {**assess.ENVELOPE, "nodes_found": nodes, "edges_found": edges, "peak_rss_bytes_found": _peak()}}


def over(found_scale: dict) -> list[str]:
    """What the scale record shows over the budget or over DEC-078's envelope."""
    said, env = [], found_scale["envelope"]
    scan = found_scale.get("vector_scan_ms")
    if scan is not None and scan > found_scale["budget_ms"]:
        said.append(f"the vector scan took {scan} ms against a budget of {found_scale['budget_ms']} ms")
    for name, found in (("nodes", env["nodes_found"]), ("edges", env["edges_found"]),
                        ("peak_rss_bytes", env["peak_rss_bytes_found"])):
        if found > env[name]:
            said.append(f"{name} {found} is over DEC-078's envelope {env[name]}")
    return said


def proposal(out: Path, said: list[str], found_scale: dict) -> None:
    """``<out>/SCALE-PROPOSAL.md`` (a CIT-P form) for the owner; it changes no store file."""
    (Path(out) / "SCALE-PROPOSAL.md").write_text(
        "---\nid: SCALE-PROPOSAL\ntype: proposal\nstatus: PROPOSED\nstate_class: AUTHORITATIVE\n---\n\n"
        "# Scale proposal (CIT-P form): a figure is over the budget or the envelope\n\n"
        "## Evidence\n\n" + "\n".join(f"- {line}" for line in said) + "\n\nFigures: `" + json.dumps(found_scale, sort_keys=True)
        + "`\n\n## Corroboration\n\nTo be added by the owner's reviewer from a second measure.\n\n"
        "## Proposal\n\nThe owner chooses: (a) accept the figure as a named residual, (b) a ticket for an indexed "
        "vector store, (c) a larger budget by a decision. No store file is changed by this proposal.\n\n"
        "## Independent review\n\npending\n\n## Owner approval\n\npending\n", encoding="utf-8")


def load_questions(file: str | None) -> tuple[list[dict], str | None]:
    """The questions of ``--questions`` (``form: w2-88-questions/1``) and the cause where there are none."""
    if not file:
        return [], "no question set was given (--questions)"
    try:
        text = Path(file).read_text(encoding="utf-8")
        data = yaml.safe_load(text)  # JSON is YAML
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return [], "the question set cannot be read"
    listed = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(listed, list) or not all(isinstance(q, dict) and isinstance(q.get("id"), str)
                                              and isinstance(q.get("question"), str) and q.get("gold") for q in listed):
        return [], "the question set is not of the form w2-88-questions/1 (id, question, gold)"
    return listed, None


def measure(root: Path, questions: list[dict], cause: str | None) -> dict:
    """right_e2e, wrong_claims and hit_at_5 over ``questions`` (evidence side only: no reader model runs here)."""
    standing = {"name": "reader", "cause": "no reader model runs in A9: right_e2e is the evidence side (every gold "
                                          "path stacked, no forbidden path in the first five); the reader's grade is "
                                          "the first full run's (W2-27)"}
    if not questions:
        return {"right_e2e": None, "wrong_claims": None, "hit_at_5": None,
                "residuals": [{"name": "questions", "cause": cause or "no questions"}, standing]}
    hits = right = wrong = 0
    residuals = [standing]
    for question in questions:
        gold, forbidden = list(question["gold"]), set(question.get("forbidden") or [])
        try:
            items = [item.get("path") for item in search(root, question["question"]).get("evidence") or []]
        except Exception as exc:  # noqa: BLE001 - a search that fails is a miss with its cause, never a stop
            residuals.append({"name": question["id"], "cause": f"the search failed ({type(exc).__name__})"})
            continue
        top = items[:5]
        bad = any(path in forbidden for path in top)
        hit = any(path in top for path in gold) and not bad
        full = all(path in items for path in gold) and not bad
        hits, right, wrong = hits + hit, right + full, wrong + bad
        if not hit:
            residuals.append({"name": question["id"], "cause": "forbidden path in the first five" if bad
                              else "no gold path among the first five items"})
    n = len(questions)
    return {"right_e2e": round(100 * right / n, 1), "wrong_claims": wrong, "hit_at_5": round(100 * hits / n, 1),
            "questions": n, "residuals": residuals}


# ---- the stage

def _out(args, root: Path) -> Path:
    given = getattr(args, "out", None)
    if not given:
        raise project.refuse("NO_OUT", "stage A9 needs --out <folder>: where its scale proposal and the audit's "
                                       "records are written (a folder outside the project)")
    out = Path(given).resolve()
    if out == root or root in out.parents:
        raise GovError("OUT_INSIDE_PROJECT", f"{out} lies inside the project {root}", {"out": str(out)})
    out.mkdir(parents=True, exist_ok=True)
    return out


def _domains(config: dict) -> tuple[dict[str, str], list[str]]:
    """The twelve categories mapped to the path map's namespaces by name; a category with none is dropped."""
    keys = {"decision": ("decision", "adr"), "contract": ("contract", "spec"), "plan": ("plan", "roadmap"),
            "ticket": ("ticket", "task", "issue"), "callers": ("code", "src", "source"),
            "code-paraphrase": ("code", "src", "source"), "exact-string": ("code", "src", "source", "doc"),
            "multi-file": ("code", "src", "source", "doc"), "kernel-template": ("kernel", "template"),
            "failure-memory": ("lesson", "failure", "postmortem")}
    spaces = (config.get("path-map.yaml") or {}).get("namespaces") if isinstance(config.get("path-map.yaml"), dict) else {}
    names = list(spaces) if isinstance(spaces, dict) else []
    found = {category: next((name for name in names if any(word in name.lower() for word in words)), None)
             for category, words in keys.items()}
    found = {category: name for category, name in found.items() if name}
    found.update({"history": "the repository's git history", "nonexistent-id": "the repository's records"})
    return found, [c for c in memory_sets.CATEGORIES if c not in found]


def a9(run) -> dict:
    """Stage A9 lite (see the module's text). ``run`` is ``gov.adopt.stages.Run``."""
    from gov.rebuild import command as rebuild

    root, args = run.root, run.args
    out = _out(args, root)
    decisions = list(getattr(args, "decision", None) or [])
    budget = getattr(args, "budget_ms", None) or RETRIEVE_BUDGET_MS
    standard = read_standard(root, decisions)  # STANDARD_DEPARTURE refuses before any store is built
    built = rebuild.run(root, argparse.Namespace(no_embeddings=False, seed=None, integration=None), run.config)
    check_digests(built)
    stores = _stores(run, built)
    tracked = [rel for rel in run.tracked if not rel.startswith(project.FOLDER + "/")]
    record = {"stores": stores}
    not_built = [item["store"] for item in built.get("not_built") or []]
    try:
        check_coverage(record, tracked)
    except GovError as exc:
        raise GovError("FABRIC_INCOMPLETE", exc.message + (f"; stores not built: {not_built}" if not_built else ""),
                       {**exc.details, "not_built": not_built}) from None
    if not_built:
        raise GovError("FABRIC_INCOMPLETE", "a store the path map calls for was not built: " + ", ".join(not_built),
                       {"missing": [], "not_built": not_built, "reasons": built.get("not_built")})
    questions, cause = load_questions(getattr(args, "questions", None))
    found_scale = scale(root, stores["codegraph"]["nodes"], stores["codegraph"]["edges"], budget)
    said = over(found_scale)
    if said:
        proposal(out, said, found_scale)
    domains, dropped = _domains(run.config)
    blind = [project.FOLDER + "/**", memory_sets.WALLS + "/**", "memory-audit/**"]
    made = memory_sets.variants(GOV_OS / memory_sets.BRIEFS, domains, blind, dropped)
    audit = f"memory-audit-{datetime.now(timezone.utc):%Y%m%d}"
    sets_root = str(Path.home() / f"{root.name}-memory-sets")
    memory = memory_sets.audit_record(out, sets_root=sets_root, audits=[audit], made=made)
    memory_sets.walls_act(out, sets_root=sets_root, audit=audit, made=made, blind=blind)
    price = memory_sets.cost(memory_sets.COST_BASIS_N)
    (out / "memory-audit" / "COST.json").write_text(json.dumps(price, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "memory-audit" / "briefs").mkdir(exist_ok=True)
    for kind, item in made.items():
        (out / "memory-audit" / "briefs" / f"{kind}.md").write_text(item["text"], encoding="utf-8")
    data = {"commit": project.resolve(root, "HEAD"), "stores": stores, "digests": built["digests"], "standard": standard,
            "scale": found_scale, "measure": measure(root, questions, cause),
            "refresh": {"command": memory_sets.REFRESH, "hook": "installed by the owner's operator through "
                                                                 "memory-audit/ACT-WALLS, never by this tool"},
            "audit": {"record": "memory-audit/AUDIT-RECORD.json", "due": memory["due"], "variants": memory["variants"],
                      "dropped_categories": dropped}, "cost": price}
    if built.get("layout"):
        data["layout"] = built["layout"]
    return run.finish(data, None, ok=True, digests=built["digests"], over=said, out=str(out))
