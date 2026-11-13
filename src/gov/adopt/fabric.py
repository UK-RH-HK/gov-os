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
import os
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
REASONS = ("secrets", "binary", "not-embedded", "unsupported-language", "over-limit")
DECISION = re.compile(r"DEC-[0-9]+(?::[a-z_]+)?")
SETTINGS = ("reranker", "reranker_service", "pool", "bundle_tokens", "widen")
RETRIEVAL = "governance/project/retrieval.yaml"
# The kernel files A9 copies, byte for byte, as Gov OS ships them (S15, S10; B-1.1, B-1.3): (Gov OS folder or file,
# the adopted repository's). Nothing is re-worded per repository.
KERNEL_FOLDERS = (("template/governance/kernel/skills/retrieval", ".claude/skills/retrieval"),
                  ("template/governance/kernel/skills/discovery", ".claude/skills/discovery"))
KERNEL_FILES = (("template/governance/kernel/templates/brief.md", "governance/kernel/templates/brief.md"),
                ("template/governance/kernel/templates/role-cto.md", "governance/kernel/templates/role-cto.md"))


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

SHARED_SERVICE = (".cache/gov-os", "rerank.sock")  # the machine's one shared reranker service (``rerank.CACHE_REL``, ``SOCKET``)
PIN_ONLY_KEYS = ("rerank", "bundle")  # keys a retrieval.yaml may never carry: the reranker and the bundle are the pin's


def _code_settings() -> dict:
    """What the pinned gov's own code says (B-1.2): the reranker's model, the service it is reached by (``shared`` for
    the machine's one service, else its folder and socket) and the bundle's budget."""
    from gov.retrieval import rerank, retrieve

    shared = (rerank.CACHE_REL, rerank.SOCKET) == SHARED_SERVICE
    return {"reranker": str(rerank.MODEL).rsplit("/", 1)[-1],
            "reranker_service": STANDARD["reranker_service"] if shared else f"{rerank.CACHE_REL}/{rerank.SOCKET}",
            "bundle_tokens": retrieve.BUNDLE_BUDGET}


def settings_of(doc: dict | None) -> dict:
    """The five settings in force. The reranker, its service and the bundle's budget are the pin's constants
    (``rerank.MODEL``, ``rerank.CACHE_REL`` and ``SOCKET``, ``retrieve.BUNDLE_BUDGET``); a ``retrieval.yaml`` may not
    carry them (``check_keys``). Only the pool departs through the file: its whole block when the pool is on
    (``meaning_uncut: true``), else False. ``widen`` has no constant to depart from."""
    code = _code_settings()
    doc = doc if isinstance(doc, dict) else {}
    return {"reranker": code["reranker"], "reranker_service": code["reranker_service"],
            "pool": doc.get("pool") if declare.pool_on(doc) else False,
            "bundle_tokens": code["bundle_tokens"], "widen": STANDARD["widen"]}


def departures(doc: dict | None) -> list[dict]:
    """Every setting that differs from ``STANDARD``: ``[{setting, value}]``. The standard's pool is the whole ``pool:``
    block as Gov OS ships it: a block that differs in any key (a value, a missing or an added key), or none, departs."""
    held = settings_of(doc)
    return [{"setting": name, "value": held[name]} for name in SETTINGS if held[name] != STANDARD[name]]


def check_keys(doc: dict | None) -> None:
    """``CONFIG_INVALID`` (``details["keys"]``) for a ``retrieval.yaml`` that carries ``rerank`` or ``bundle`` (B-1.2:
    the reranker and the bundle are the pin's constants). A ``--decision`` does not make it ok."""
    keys = [key for key in PIN_ONLY_KEYS if isinstance(doc, dict) and key in doc]
    if keys:
        raise GovError("CONFIG_INVALID", "governance/project/retrieval.yaml: the key(s) " + ", ".join(keys) + " are not "
                       "allowed: the reranker and the bundle are the pin's constants (rerank.MODEL, "
                       "retrieve.BUNDLE_BUDGET), never a repository's setting", {"keys": keys})


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
    if raw is None:  # none tracked: the copy A9 installs (Gov OS's, as shipped) is the file in force (B-1.3)
        raw = (GOV_OS / RETRIEVAL).read_bytes()
        doc = yaml.safe_load(raw.decode("utf-8"))
    check_keys(doc)
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


# ---- the copy step (S15, S10; B-1.1, B-1.3)

def _sources() -> list[tuple[str, str]]:
    """``(from, to)`` for every kernel file A9 installs: the files of the two skill folders (same relative names) and
    the two templates. A source Gov OS does not ship is a refusal, never a skipped file."""
    found = []
    for source, target in KERNEL_FOLDERS:
        base = GOV_OS / source
        files = sorted(path for path in base.rglob("*") if path.is_file()) if base.is_dir() else []
        if not files:
            raise GovError("KERNEL_SOURCE_MISSING", f"{source}: Gov OS ships no file there: nothing is installed",
                           {"source": source})
        found += [(path.relative_to(GOV_OS).as_posix(), f"{target}/{path.relative_to(base).as_posix()}") for path in files]
    for source, target in KERNEL_FILES:
        if not (GOV_OS / source).is_file():
            raise GovError("KERNEL_SOURCE_MISSING", f"{source}: Gov OS ships no such file: nothing is installed",
                           {"source": source})
        found.append((source, target))
    return found


def install(run, head: str) -> dict:
    """Write, byte for byte, the kernel files Gov OS ships into the adopted repository and stage them (the stage's one
    commit takes them with its record): the retrieval and discovery skills to ``.claude/skills/``, T-0 and T-8 to
    ``governance/kernel/templates/``, and Gov OS's ``retrieval.yaml`` only where the repository tracks none (its own is
    kept, and judged). ``{installed: [{path, sha256, from}], kept: [{path, sha256}], written, dirs, staged, replaced}``:
    what A9 wrote, the folders it made, the index entry ``(mode, blob)`` it staged per path and the blob of each path the
    start commit tracked: what ``undo`` judges by. The copies join ``run.tracked`` (the stores judge them like any
    file). An untracked file at a destination is never overwritten (refused, naming it)."""
    root, tracked = run.root, run.tracked
    wanted, kept = _sources(), []
    if RETRIEVAL in tracked:
        kept.append({"path": RETRIEVAL, "sha256": hashlib.sha256(project.blob(root, tracked[RETRIEVAL])).hexdigest()})
    elif (GOV_OS / RETRIEVAL).is_file():
        wanted.append((RETRIEVAL, RETRIEVAL))
    else:
        raise GovError("KERNEL_SOURCE_MISSING", f"{RETRIEVAL}: Gov OS ships no such file", {"source": RETRIEVAL})
    taken = [target for _, target in wanted if os.path.lexists(root / target) and target not in tracked]
    if taken:
        raise project.refuse("WOULD_OVERWRITE", "an untracked file stands at " + ", ".join(taken) + ": the tool writes "
                             "nothing over a file it did not write", paths=taken)
    copies = {"installed": [], "kept": kept, "written": [], "dirs": [], "staged": {},
              "replaced": {target: tracked[target] for _, target in wanted if target in tracked}}
    try:
        for source, target in wanted:
            data, place = (GOV_OS / source).read_bytes(), root / target
            walk = place.parent
            while not walk.exists():
                copies["dirs"].append(walk)
                walk = walk.parent
            place.parent.mkdir(parents=True, exist_ok=True)
            real = place.parent.resolve()
            if place.is_symlink() or not (real == root.resolve() or root.resolve() in real.parents):
                raise project.refuse("INSTALL_PATH_UNSAFE", f"{target} would be written through a link or outside the "
                                                            "project: nothing is installed", path=target)
            place.write_bytes(data)
            copies["written"].append(target)
            copies["installed"].append({"path": target, "sha256": hashlib.sha256(data).hexdigest(), "from": source})
        project.git(root, "--literal-pathspecs", "add", "--", *copies["written"])
        for entry in project.git(root, "--literal-pathspecs", "ls-files", "-s", "-z", "--", *copies["written"]).split("\0"):
            meta, _, rel = entry.partition("\t")
            if rel:  # the copies are tracked files of the project from here on: judged like every other
                mode, blob_id = meta.split()[:2]
                copies["staged"][rel] = (mode, blob_id)
                run.tracked[rel] = blob_id
    except BaseException as exc:
        undone(root, head, copies, exc)
        raise
    return copies


def _entries(listing: str, blob_at: int) -> dict[str, tuple[str, str]]:
    """Path -> ``(mode, blob)`` from a ``-z`` listing of ``ls-files -s`` (blob at field 1) or ``ls-tree`` (field 2)."""
    found = {}
    for entry in listing.split("\0"):
        meta, _, rel = entry.partition("\t")
        if rel:
            fields = meta.split()
            found[rel] = (fields[0], fields[blob_at])
    return found


def undo(root: Path, head: str, copies: dict) -> str | None:
    """Undo only what A9 did (RV2-1), judged against the commit HEAD names now: never ``git reset --hard``, never a
    checkout, never a move of the branch. In the index, a path A9 staged is unstaged (put back to the commit's entry
    where the commit tracks it) only where its entry is still the blob A9 staged; in the tree, a file A9 wrote is
    deleted (or, where the commit tracks the path, or the start commit did, given back that content) only where its
    bytes are still A9's; then the folders A9 made, each only when empty. A copy the commit itself holds (committed
    during the run) is left as it is, and so is every other path: a tracked file edited, a file staged or made during
    the run. Returns the commit HEAD names now where it is not ``head`` (the caller refuses ``HEAD_MOVED``), else
    None."""
    written = list(copies["written"])
    now = project.resolve(root, "HEAD")
    if written:
        index = _entries(project.git(root, "--literal-pathspecs", "ls-files", "-s", "-z", "--", *written), 1)
        held = _entries(project.git(root, "--literal-pathspecs", "ls-tree", "-r", "-z", now, "--", *written), 2) \
            if now else {}
        sums = {item["path"]: item["sha256"] for item in copies["installed"]}
        staged, lines = copies.get("staged") or {}, []
        for rel in written:
            mine = staged.get(rel)
            if mine is None or index.get(rel) != mine or held.get(rel, (None, None))[1] == mine[1]:
                continue  # not staged by A9, re-staged by someone, or the commit holds A9's copy: left as it is
            if rel in held:
                lines.append(f"{held[rel][0]} {held[rel][1]}\t{rel}\0")
            else:
                lines.append(f"0 {'0' * len(mine[1])}\t{rel}\0")
        if lines:
            project._run(root, ("update-index", "-z", "--index-info"), (0,), "".join(lines).encode("utf-8", "surrogateescape"))
        for rel in written:
            place = root / rel
            if place.is_symlink() or not place.is_file():
                continue
            if hashlib.sha256(place.read_bytes()).hexdigest() != sums.get(rel):
                continue  # changed during the run: the bytes are someone else's now
            if rel in held and held[rel][1] == staged.get(rel, (None, None))[1]:
                continue  # the commit holds A9's copy (committed during the run)
            back = held.get(rel, (None, None))[1] or (copies.get("replaced") or {}).get(rel)
            if back:  # a file the commit (or the start commit) tracks: its content is put back, never deleted
                place.write_bytes(project.blob(root, back))
            else:
                place.unlink()
    for folder in sorted(copies["dirs"], key=lambda each: len(each.parts), reverse=True):
        try:
            folder.rmdir()
        except OSError:
            pass
    return now if now != head else None


def undone(root: Path, head: str, copies: dict, exc: BaseException) -> None:
    """``undo``, then ``HEAD_MOVED`` (chained from ``exc``) where HEAD no longer names ``head``: nothing was reset and
    the branch stays where it is. Where HEAD did not move, the caller re-raises ``exc`` as it was."""
    now = undo(root, head, copies)
    if now is None:
        return
    cause = exc.code if isinstance(exc, GovError) else type(exc).__name__
    raise GovError("HEAD_MOVED", f"A9 stopped ({cause}) after HEAD moved from {head} (the commit A9 started on) to "
                   f"{now}: nothing was reset and the branch stays at {now}; only A9's own copies (still as A9 wrote "
                   "and staged them, and not held by the new commit) were removed",
                   {"started": head, "now": now, "cause": cause}) from exc


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
    tracked, missing, short, not_built, errors = set(tracked), set(), [], [], []
    for name in JUDGING:
        store = stores.get(name)
        if isinstance(store, dict) and store.get("requested") is False:
            continue  # the path map did not call for it
        if not isinstance(store, dict) or store.get("built") is False \
                or store.get("status") in ("not_recreated", "not_built"):
            not_built.append(name)  # a store the path map calls for, absent or not built
            if isinstance(store, dict) and store.get("error"):
                errors.append(f"{name}: {store['error']}")
            continue
        named = set(store.get("indexed") or []) | {item.get("path") for item in store.get("refused") or []
                                                  if isinstance(item, dict)}
        if name == "lexical":
            missing |= tracked - named
        else:
            gap = (store.get("judged") or 0) - len(named)
            if gap > 0:
                short.append(f"{name}: {gap} file(s) judged and in neither list")
    if missing or short or not_built:
        said = ([f"{len(missing)} tracked file(s) are in neither the indexed list nor the refused list of the store "
                 "that judges them"] if missing else []) + short \
            + ([f"a store the path map calls for was not built: {', '.join(not_built)}"
                + (f" ({'; '.join(errors)})" if errors else "")] if not_built else [])
        raise GovError("FABRIC_INCOMPLETE", "; ".join(said),
                       {"missing": sorted(missing), "short": short, "not_built": not_built})


# ---- the stores' lists, read from the stores the rebuild built

def _peak() -> int:
    """The stage's process's own peak (``VmHWM``), or a child's (the scanner, the code graph) where that is more."""
    return max(assess.peak_rss(), resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)


def _namespaces(run) -> dict[str, str | None]:
    try:
        return project.classify(run.config, run.tracked)
    except GovError:  # no path map: no namespace holds anything
        return {rel: None for rel in run.tracked if not rel.startswith(project.FOLDER + "/")}


def _policy(config: dict, space: str | None) -> str | None:
    spaces = (config.get("path-map.yaml") or {}).get("namespaces") if isinstance(config.get("path-map.yaml"), dict) else {}
    value = spaces.get(space) if isinstance(spaces, dict) else None
    return value.get("embedding_policy") if isinstance(value, dict) else None


def _binary(run, paths: list[str]) -> set[str]:
    """The files of ``paths`` whose first 8,000 bytes hold a zero byte (git's own test), read by one ``cat-file``."""
    found, blobs = set(), assess._Blobs(run.root)
    try:
        for rel in paths:
            head, _size = blobs.read(run.tracked[rel], 8000)
            if b"\0" in head:
                found.add(rel)
    finally:
        blobs.close()
    return found


def _memory_class(config: dict, space: str | None) -> str | None:
    spaces = (config.get("path-map.yaml") or {}).get("namespaces") if isinstance(config.get("path-map.yaml"), dict) else {}
    value = spaces.get(space) if isinstance(spaces, dict) else None
    return value.get("memory_class") if isinstance(value, dict) else None


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
        n_records = (rows("SELECT count(*) FROM records") or [(0,)])[0][0]
        n_edges = (rows("SELECT count(*) FROM edges") or [(0,)])[0][0]
    finally:
        db.close()
    lexical_i, lexical_r = [], []
    binary_files = _binary(run, [rel for rel in paths if verdicts.get(rel) == 1])
    for rel in paths:
        state = verdicts.get(rel)
        if state is None:
            continue  # the keyword index holds no verdict on it: it is in neither list, and check_coverage says so
        if state == 1:  # a binary the index chunked is held by the store: indexed, and named in ``binary_held`` (RV1-4)
            lexical_i.append(rel)
        elif state == 2:
            lexical_r.append({"path": rel, "reason": "not-embedded"})
        elif _memory_class(run.config, namespaces[rel]) != "governance":
            # ``gov.secrets.indexable`` lets through only a namespace whose memory_class is governance
            lexical_r.append({"path": rel, "reason": "not-embedded"})
        else:
            try:
                binary = b"\0" in project.blob(run.root, run.tracked[rel])[:8000]
            except GovError:
                binary = False
            lexical_r.append({"path": rel, "reason": "binary" if binary else "secrets"})  # a binary the store did not take
    for rel in sorted(set(verdicts) - set(paths)):  # held by the store, outside the path map (the adoption's records)
        state = verdicts[rel]
        if state == 1:
            lexical_i.append(rel)
        else:
            lexical_r.append({"path": rel, "reason": "not-embedded" if state == 2 else "secrets"})
    vec_i = [rel for rel in lexical_i if rel in vectored]
    vec_r = [{"path": rel, "reason": "not-embedded"} for rel in lexical_i
             if rel in chunked and rel not in vectored and _policy(run.config, namespaces.get(rel)) != "embedded"]
    code = [rel for rel in paths if Path(rel).suffix.lower() in assess.CODE_GRAPH_SUFFIXES | assess.OTHER_CODE_SUFFIXES]
    called_for = project.code_intelligence(run.config)
    code_i, code_r = [], []
    for rel in code if called_for else ():
        if Path(rel).suffix.lower() not in assess.CODE_GRAPH_SUFFIXES:
            code_r.append({"path": rel, "reason": "unsupported-language"})  # never indexed by the graph (RV1-5)
        elif (run.root / codeintel.BASE_REL / "files" / rel).is_file():
            code_i.append(rel)
        else:
            code_r.append({"path": rel, "reason": "secrets" if verdicts.get(rel) == 0 else "not-embedded"})
    nodes = edges = 0
    unreadable = None
    if called_for and code_i:
        try:
            graph, users = codeintel._graph(run.root)
            nodes, edges = len(graph), sum(len(each) for each in users.values())
        except Exception as exc:  # noqa: BLE001 - a graph that cannot be read is named, never shown as 0 nodes and edges
            unreadable = f"{type(exc).__name__}: {' '.join(str(exc).split())}"
    held = sorted(records & set(paths))  # the record store judges the files that carry records (a plain file is none)
    return {
        "record": {**base, "judged": len(held), "indexed": held, "nodes": n_records, "edges": n_edges, "refused": [],
                   "seconds": timing.get("record_s", 0.0)},
        "lexical": {**base, "judged": len(lexical_i) + len(lexical_r), "indexed": lexical_i, "refused": lexical_r, "chunks": n_chunks,
                    "binary_held": [rel for rel in lexical_i if rel in binary_files], "seconds": timing.get("lexical_s", 0.0)},
        "vectors": {**base, "judged": len([rel for rel in lexical_i if rel in chunked]), "indexed": vec_i, "refused": vec_r,
                    "chunks": n_chunks, "vectors": n_vectors, "binary_held": [rel for rel in vec_i if rel in binary_files],
                    "seconds": timing.get("semantic_s", 0.0)},
        "codegraph": {**base, "judged": len(code_i) + len(code_r), "indexed": code_i, "refused": code_r, "nodes": nodes,
                      "edges": edges, "seconds": timing.get("codeintel_s", 0.0),
                      **({} if called_for else {"requested": False}),
                      **({"built": False, "error": unreadable} if unreadable else {})},
    }


# ---- scale and measure (S5, S6)

def search(root: Path, question: str) -> dict:  # the seam a test replaces with a stand-in
    from gov.retrieval import retrieve

    return retrieve.retrieve(root, question)


def vector_scan(root: Path, question: str) -> dict:  # the seam a test replaces with a stand-in (RV1-2)
    """The semantic route's reply: ``available`` (a scan ran) and ``reason`` (why not)."""
    from gov.retrieval import semantic

    return semantic.search(root, question, refresh=False)


def _timed(call) -> float | None:
    start = time.perf_counter()
    try:
        call()
    except Exception:  # noqa: BLE001 - a route that cannot answer has no time: the record names it
        return None
    return round((time.perf_counter() - start) * 1000, 1)


def _scan(root: Path) -> tuple[float | None, float | None, str | None]:
    """``(route time, vector scan ms, reason)``. The scan is a figure only where the semantic route answered
    ``available: true``; an unavailable answer or an error gives None and the reason (the route's, or the error's name):
    a reply that scanned nothing is never a scan time, and is never compared with the budget (RV1-2)."""
    start = time.perf_counter()
    try:
        reply = vector_scan(root, PLAIN_QUESTION)
    except Exception as exc:  # noqa: BLE001 - a route that raised ran no scan: the record names the error
        return round((time.perf_counter() - start) * 1000, 1), None, type(exc).__name__
    took = round((time.perf_counter() - start) * 1000, 1)
    if isinstance(reply, dict) and reply.get("available") is True:
        return took, took, None
    why = reply.get("reason") or reply.get("error") if isinstance(reply, dict) else None
    return took, None, str(why or "the semantic route answered unavailable")


def scale(root: Path, nodes: int, edges: int, budget_ms: int) -> dict:
    """The query time of one plain question on each route, and the vector scan's time against the budget (``None``
    with ``vector_scan_reason`` where the scan did not run). Only the vector scan is compared with the budget."""
    from gov.retrieval import lexical

    semantic_ms, scan_ms, why = _scan(root)
    routes = {"lexical": _timed(lambda: lexical.search(root, PLAIN_QUESTION, refresh=False)),
              "semantic": semantic_ms, "retrieve": _timed(lambda: search(root, PLAIN_QUESTION))}
    return {"routes": routes, "vector_scan_ms": scan_ms, "vector_scan_reason": why, "budget_ms": budget_ms,
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
    """Stage A9 lite (see the module's text). ``run`` is ``gov.adopt.stages.Run``. The standard is judged first (a
    refusal there writes nothing); then the kernel files are installed and staged, the stores built and the record
    committed with them in one commit. A refusal or an interrupt after the copies undoes only what A9 did (``undo``:
    its copies still as it wrote and staged them, and the folders it made when empty; every other edit, staged file or
    commit made during the run stays) and keeps its own code, or is ``HEAD_MOVED`` where HEAD moved meanwhile."""
    root, args = run.root, run.args
    out = _out(args, root)
    decisions = list(getattr(args, "decision", None) or [])
    standard = read_standard(root, decisions)  # CONFIG_INVALID, STANDARD_DEPARTURE: before any copy and any store
    head = project.resolve(root, "HEAD")
    copies = install(run, head)
    try:
        return _stage(run, out, standard, copies)
    except BaseException as exc:
        undone(root, head, copies, exc)
        raise


def _stage(run, out: Path, standard: dict, copies: dict) -> dict:
    from gov.rebuild import command as rebuild

    root, args = run.root, run.args
    budget = getattr(args, "budget_ms", None) or RETRIEVE_BUDGET_MS
    built = rebuild.run(root, argparse.Namespace(no_embeddings=False, seed=None, integration=None), run.config)
    check_digests(built)
    stores = _stores(run, built)
    tracked = [rel for rel in run.tracked if not rel.startswith(project.FOLDER + "/")]
    record = {"stores": stores}
    not_built = [item["store"] for item in built.get("not_built") or []]
    try:
        check_coverage(record, tracked)
    except GovError as exc:
        raise GovError("FABRIC_INCOMPLETE", exc.message + (f"; the rebuild says not built: {not_built}" if not_built else ""),
                       {**exc.details, "not_built": sorted({*exc.details["not_built"], *not_built})}) from None
    if not_built:
        raise GovError("FABRIC_INCOMPLETE", "a store the path map calls for was not built: " + ", ".join(not_built),
                       {"missing": [], "not_built": not_built, "reasons": built.get("not_built")})
    questions, cause = load_questions(getattr(args, "questions", None))
    found_scale = scale(root, stores["codegraph"]["nodes"], stores["codegraph"]["edges"], budget)
    said = over(found_scale)
    if said:
        proposal(out, said, found_scale)
    else:  # this run's record decides: a proposal an earlier run left in the folder is not this run's
        (out / "SCALE-PROPOSAL.md").unlink(missing_ok=True)
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
    data = {"commit": project.resolve(root, "HEAD"), "installed": copies["installed"], "kept": copies["kept"],
            "stores": stores, "digests": built["digests"], "standard": standard,
            "scale": found_scale, "measure": measure(root, questions, cause),
            "refresh": {"command": memory_sets.REFRESH, "hook": "installed by the owner's operator through "
                                                                 "memory-audit/ACT-WALLS, never by this tool"},
            "audit": {"record": "memory-audit/AUDIT-RECORD.json", "due": memory["due"], "variants": memory["variants"],
                      "dropped_categories": dropped}, "cost": price}
    if built.get("layout"):
        data["layout"] = built["layout"]
    return run.finish(data, None, ok=True, digests=built["digests"], over=said, out=str(out),
                      installed=copies["installed"], kept=copies["kept"])
