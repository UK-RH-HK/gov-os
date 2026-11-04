"""``gov retrieve``: one cited evidence bundle with one stopping reason (W1-21; DEC-080, DEC-419, DEC-422–425).

``retrieve`` asks the lexical and the semantic route, closes over a ticket, ids or the records the question names
(``graph_route``) with ``gov.closure``, asks the code index for the symbols it names (``code_route``), merges them
by chunk hash, drops what the store says is superseded or must-not-cite (DEC-329, G-19, DEC-423), reranks
the rest once (DP-9) and expands a child hit to its parent within the bundle budget (DEC-091, DP-3). It only
reads (DEC-322).

Paging (DEC-422): batches beyond the first, rounds scaled by radius, a stateless continuation token.
Must-not-cite (DEC-423): DEPRECATED, REJECTED, WITHDRAWN; frontmatter check for files not in the store.
Failure/lesson ahead (DEC-424): failure and lesson records in the ticket's closure come ahead of other evidence.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
from pathlib import Path

import yaml

from gov import closure as closures
from gov import records
from gov.cli.errors import GovError
from gov.guard import role_paths
from gov.retrieval import authority, code_route, graph_route, lexical, routing, semantic
from gov.retrieval.fusion import RERANK_CHARS, rrf
from gov.retrieval.rerank import last_outcome, rerank
from gov.store import loader

CLOSURE = "closure"
SATURATED, BUDGET_EXHAUSTED = "SATURATED", "BUDGET_EXHAUSTED_WITH_GAPS"
SUPERSEDED, NOT_GATHERED = "SUPERSEDED", "NOT_GATHERED"
BUNDLE_BUDGET = 6000  # tokens: DEC-004's packet ceiling, until a decision gives another number (DP-3)
TOKEN_CHARS = 4
NO_CODE_INDEX = "the code index did not answer for an id that is no record"

ROUNDS_BY_RADIUS = {0: 1, 1: 1, 2: 3, 3: 8, 4: 8}
DEFAULT_BATCH_SIZE = 10
MUST_NOT_CITE_STATUSES = frozenset({"DEPRECATED", "REJECTED", "WITHDRAWN"})
AHEAD_TYPES = frozenset({"failure", "lesson"})
# What sqlite raises for a store that cannot be opened, holds no record graph or is no database; no fault of a query
STORE_FAULTS = (sqlite3.OperationalError, sqlite3.DatabaseError)
# W2-32 S7, DEC-1067: why a span is named in ``repeats`` and not sent
IN_EARLIER_PARENT = "SENT_IN_AN_EARLIER_PARENT"  # the chunk lies inside a parent an earlier call expanded
EARLIER_CHILD = "SENT_EARLIER_AS_A_CHILD"  # an earlier call sent these lines as a child: left out of a later parent
NO_RECORD_GRAPH = "the record graph is unreadable, so whether this record is current cannot be judged"  # DEC-1019


def _declares_record(root: Path, rel: str) -> str | None:
    """The id a file's front matter declares, read as the store's loader reads a record; None for no record."""
    try:
        front = loader._frontmatter((root / rel).read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return None
    return str(front["id"]) if isinstance(front, dict) and "id" in front else None


def _named_register(root: Path) -> str | None:
    """The register the path map names under the loader's key, read without the record graph; None for none."""
    try:
        named = yaml.safe_load((root / loader.PATH_MAP_REL).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    return named.get(loader.REGISTER_KEY) if isinstance(named, dict) else None


def _graph(root: Path) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """``path -> id`` of every record, ``id -> reason`` for not-current records (superseded or must-not-cite),
    and ``id -> type`` for every record. Raises what the store raises when it is missing or cannot be read."""
    known = records.records(root)
    superseded_edges = {edge["target"] for edge in records.edges(root, type="SUPERSEDES")}
    record_of = {record["path"]: record["id"] for record in known}
    not_current: dict[str, str] = {}
    for record in known:
        if record["status"] == SUPERSEDED or record["id"] in superseded_edges:
            not_current[record["id"]] = SUPERSEDED
        elif record["status"] in MUST_NOT_CITE_STATUSES:
            not_current[record["id"]] = record["status"]
    record_types = {record["id"]: record["type"] for record in known}
    return record_of, not_current, record_types


def _frontmatter_status(root: Path, rel: str) -> tuple[str | None, str | None]:
    """The (id, status) from a file's YAML frontmatter, or (None, None)."""
    try:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, None
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return None, None
    try:
        front = yaml.safe_load(text[4:text.index("\n---\n", 4)])
    except Exception:
        return None, None
    if not isinstance(front, dict):
        return None, None
    return front.get("id"), front.get("status")


def _tokens(text: str) -> int:
    return -(-len(text) // TOKEN_CHARS)


def _encode_continuation(query, ids, ticket, radius, batch_size, bundle_budget, offset, expanded=(), alone=()):
    """The stateless token of the next call; ``x`` carries the parents already expanded and ``c`` the spans already
    sent as a child on its own (``[path, first, last]``), so a later call sends neither again (W2-32 S7, DEC-1067)."""
    payload = json.dumps({"q": query, "i": sorted(ids), "t": ticket, "r": radius,
                          "bs": batch_size, "bb": bundle_budget, "o": offset, "x": sorted(expanded),
                          "c": sorted([list(item) for item in alone])},
                         separators=(",", ":"), sort_keys=True)
    return base64.urlsafe_b64encode(payload.encode()).decode()


def _expanded_of(payload: dict) -> set[str]:
    """The parents the earlier calls expanded (``x``); none for a token made before W2-32 S7."""
    named = payload.get("x", [])
    if not isinstance(named, list) or not all(isinstance(parent, str) for parent in named):
        raise GovError("CONTINUATION_INVALID", "the continuation is no token of an earlier bundle") from None
    return set(named)


def _alone_of(payload: dict) -> set[tuple[str, int, int, str]]:
    """The spans the earlier calls sent as a child on its own (``c``: path, first line, last line and the chunk; a
    token that names no chunk gives ""); none for a token made before DEC-1067."""
    named = payload.get("c", [])
    if not isinstance(named, list) or not all(
            isinstance(item, list) and len(item) in (3, 4) and isinstance(item[0], str)
            and all(isinstance(n, int) and not isinstance(n, bool) for n in item[1:3])
            and (len(item) == 3 or isinstance(item[3], str)) for item in named):
        raise GovError("CONTINUATION_INVALID", "the continuation is no token of an earlier bundle") from None
    return {(item[0], item[1], item[2], item[3] if len(item) == 4 else "") for item in named}


def _merged(spans) -> list[tuple[int, int]]:
    """``spans`` (first and last line, both inclusive, as a chunk's) in order, those that share a line made one, so
    each line is named once. Neighbouring chunks share their overlap lines (``chunking.OVERLAP_CHARS``); spans that
    only touch stay apart, as they were sent."""
    merged: list[list[int]] = []
    for first, last in sorted(spans):
        if merged and first <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], last)
        else:
            merged.append([first, last])
    return [(first, last) for first, last in merged]


def _without(first: int, last: int, sent: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """The runs of lines ``first`` to ``last`` that none of the ``sent`` spans holds, in order."""
    runs, at = [], first
    for start, end in sorted(sent):
        if start > at:
            runs.append((at, min(start - 1, last)))
        at = max(at, end + 1)
    if at <= last:
        runs.append((at, last))
    return [(a, b) for a, b in runs if a <= b]


def _decode_continuation(token, query, ids, ticket, radius, batch_size, bundle_budget, expanded=None, alone=None):
    """The offset of the next call; with ``expanded`` (a set), the parents the earlier calls expanded are added, and
    with ``alone`` (a set), the spans they sent as a child on its own."""
    try:
        payload = json.loads(base64.urlsafe_b64decode(token))
    except Exception:
        raise GovError("CONTINUATION_INVALID", "the continuation is no token of an earlier bundle") from None
    expected = {"q": query, "i": sorted(ids), "t": ticket, "r": radius, "bs": batch_size, "bb": bundle_budget}
    for key in expected:
        if payload.get(key) != expected[key]:
            raise GovError("CONTINUATION_INVALID",
                           "the continuation belongs to a different question or arguments") from None
    offset = payload.get("o")
    if not isinstance(offset, int) or offset < 0:
        raise GovError("CONTINUATION_INVALID", "the continuation is no token of an earlier bundle") from None
    if expanded is not None:
        expanded |= _expanded_of(payload)
    if alone is not None:
        alone |= _alone_of(payload)
    return offset


def _by_cosine(root: Path, query: str, chunk_ids: list[str]) -> list[str]:
    """``chunk_ids`` ranked by their stored vectors' cosine to the question's, those with no vector last and ties in
    the order given; as given when no vector can be compared (W2-32 S8)."""
    distance = semantic.distances(root, query, chunk_ids)
    if not distance:
        return list(chunk_ids)
    return sorted(chunk_ids, key=lambda chunk_id: distance.get(chunk_id, float("inf")))


def role_filter(root, role=None):
    """W2-13 S5 (DEC-1065 (2)): what the caller (``GOV_ROLE``, ``role`` beside it, ``GOV_TICKET``) may not be handed,
    by the main tree's ``role_paths:``; None for no filter. One that cannot be worked out stops the search."""
    try:
        return role_paths.caller(root, role)
    except role_paths.RolePathsError as error:
        raise GovError("ROLE_PATHS_UNREADABLE", f"what the caller's role may be handed cannot be worked out: {error}",
                       {"root": str(root)}) from None


def retrieve(root, query, *, ids=(), ticket=None, radius=0, batch_size=None, bundle_budget=None, continuation=None,
             reranker=None, role=None) -> dict:
    """The evidence bundle for ``query``; ``ticket`` and ``ids`` are closed over to the depth of ``radius``. Every
    route's hits are filtered by the caller's role paths (``role_filter``; ``role`` is a ``--role`` given), and what
    is withheld is counted in the bundle's ``role_filter``."""
    if batch_size is None:
        batch_size = DEFAULT_BATCH_SIZE
    limit = BUNDLE_BUDGET if bundle_budget is None else bundle_budget

    offset, earlier, alone = 0, set(), set()  # the parents the earlier calls expanded, the children they sent alone
    if continuation is not None:
        offset = _decode_continuation(continuation, query, tuple(ids), ticket, radius, batch_size, bundle_budget,
                                      earlier, alone)
    sent_alone = set(alone)  # W2-32 S7, DEC-1067: and this call's, for the next

    withhold = role_filter(root, role)
    # W2-32 S8: the routing settings read first, so an invalid file is refused before any search work (S8-F4)
    route_settings, routed = routing.settings(root), {}
    root = Path(root)
    unread = None  # W2-92: a store whose record graph is missing or unreadable fails the record and closure routes
    try:
        record_of, not_current, record_types = _graph(root)
        # W2-87: a register chunk is the entry whose span holds it, never the register's last entry (DEC-952)
        known, edges = records.records(root), records.edges(root, type=authority.SUPERSEDES)
    except sqlite3.DatabaseError as error:  # no store file at all stays connect's STORE_MISSING: no route answers
        if type(error) not in STORE_FAULTS:
            raise  # a fault that is not the store's is no unavailable route
        missing = str(error).startswith("no such table")
        unread = (f"the record store is {'missing' if missing else 'unreadable'}: {error}; no record route or closure;"
                  " record files are left out, as their currency cannot be judged without the record graph")
        record_of, not_current, record_types, known, edges = {}, {}, {}, [], []
    register, entry_of = authority.register_path(known), authority.register_entries_of(known, edges, root)
    if unread is not None:
        register = _named_register(root)  # DEC-1019: the register, known without the graph, is left out too
    order = (authority.order(root, known, edges, entry_of) if unread is None  # DEC-952 item 1: retrieval_authority
             else authority.Order(None, known, edges, entry_of))  # no record graph: no authority order (DEC-1006)
    answers = {lexical.FACET: lexical.search(root, query, refresh=False),
               semantic.FACET: semantic.search(root, query, refresh=False)}
    facets = {name: {"available": answer["available"], "reason": answer["reason"]} for name, answer in answers.items()}
    routes = {name: answer.get("ranked", answer["hits"]) for name, answer in answers.items()}  # W2-13: ranked lexical
    chunks = {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root)} if facets[lexical.FACET]["available"] else {}
    closure_gaps, start = [], [*([ticket] if ticket else []), *ids]
    depth = closures.depth_of_radius(radius if start else min(radius, 1))  # W2-92: a question's records at R0 or R1
    start += [rid for rid in graph_route.start_ids(root, query, known) if rid not in start]  # W2-92: the record route
    reached = set()
    if unread is not None:
        facets[CLOSURE] = {"available": False, "reason": unread}
    elif start:
        closed = closures.closure(root, start, depth)
        reached = {item["id"] for item in closed["closure"]}
        routes[CLOSURE] = [chunk for chunk in chunks.values()
                           if (record_of.get(chunk["path"]) if chunk["path"] != register
                               else (entry_of(chunk["path"], chunk["start_line"]) or {}).get("id")) in reached]
        answered = closed["facets"]["code"] != "unavailable"
        facets[CLOSURE] = {"available": answered, "reason": None if answered else NO_CODE_INDEX}
        closure_gaps += closed["gaps"]
    coded = code_route.route(root, query, chunks)  # W2-92: the code route; None when the question names no symbol
    if coded is not None:
        routes[code_route.FACET], facets[code_route.FACET] = coded
        if route_settings["code_first"] and routes[code_route.FACET]:  # S8-F1: as r01, ranked before the fusion
            by_id = {hit["chunk_id"]: hit for hit in routes[code_route.FACET]}
            ordered = _by_cosine(root, query, list(by_id))
            routes[code_route.FACET] = [by_id[chunk_id] for chunk_id in ordered]
    if withhold is not None:  # W2-13 S5: every route's hits, before the fusion, so a withheld one takes no rank
        routes = {name: withhold.keep(hits) for name, hits in routes.items()}

    fused = rrf(routes)
    fused = order.fused(fused, chunks)  # W2-87: lifted by authority before the cut (DEC-952, DEC-860)

    # DEC-424: move failure/lesson records ahead so they're gathered even in small batches
    ahead_paths: set[str] = set()
    if ticket and reached:
        ahead_ids = {rid for rid in reached if record_types.get(rid) in AHEAD_TYPES and rid not in not_current}
        ahead_paths = {path for path, rid in record_of.items() if rid in ahead_ids}
        if ahead_paths:
            ahead_fused = [hit for hit in fused if hit["path"] in ahead_paths]
            rest_fused = [hit for hit in fused if hit["path"] not in ahead_paths]
            fused = ahead_fused + rest_fused

    # DEC-422: paging with rounds budget
    rounds_limit = ROUNDS_BY_RADIUS.get(radius, ROUNDS_BY_RADIUS[4])
    total_slots = (rounds_limit + 1) * batch_size
    gathering = fused[offset:offset + total_slots]
    remaining = fused[offset + total_slots:]

    batches_list: list[dict] = []
    batch_assignments: dict[str, int] = {}
    for i in range(rounds_limit + 1):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, len(gathering))
        batch_chunk = gathering[start_idx:end_idx]
        if not batch_chunk and i > 0:
            break
        batches_list.append({"size": len(batch_chunk)})
        for hit in batch_chunk:
            batch_assignments[hit["chunk_id"]] = i + 1

    rounds_used = min(rounds_limit, max(0, len(batches_list) - 1))

    gaps = list(closure_gaps)
    gaps += [{"path": hit["path"], "chunk_id": hit["chunk_id"], "reason": NOT_GATHERED} for hit in remaining]

    files: dict[str, list[bytes]] = {}

    def span(rel: str, first: int, last: int) -> bytes:
        if rel not in files:
            files[rel] = (root / rel).read_bytes().splitlines(keepends=True)
        return b"".join(files[rel][first - 1:last])

    dropped: dict[str, dict] = {}
    candidates = []
    frontmatter_cache: dict[str, tuple[str | None, str | None]] = {}

    for hit in gathering:
        if hit["chunk_id"] not in chunks:  # W2-13 R4: a hit whose chunk the lexical index does not hold is skipped
            continue
        chunk = chunks[hit["chunk_id"]]
        record_id = record_of.get(chunk["path"])

        # W2-87: a register chunk is never dropped for another entry's status, and its own entry's drops nothing
        # new here: leaving entries out is W2-55's (DEC-791 item 1)
        in_register = chunk["path"] == register

        # DEC-1019: without the record graph no record is judged current, so no record file is cited at all
        if unread is not None:
            declared = None if in_register else _declares_record(root, chunk["path"])
            if in_register or declared is not None:
                dropped.setdefault(chunk["path"], {"path": chunk["path"], "id": declared or chunk["path"],
                                                   "reason": NO_RECORD_GRAPH})
                continue

        # DEC-329, G-19: superseded records
        if not in_register and record_id is not None and record_id in not_current:
            if chunk["path"] not in dropped:
                dropped[chunk["path"]] = {"path": chunk["path"], "id": record_id, "reason": not_current[record_id]}
            continue

        # DEC-423: files the store could not load — read frontmatter
        if record_id is None:
            rel = chunk["path"]
            if rel not in frontmatter_cache:
                frontmatter_cache[rel] = _frontmatter_status(root, rel)
            fm_id, fm_status = frontmatter_cache[rel]
            if fm_status in ({SUPERSEDED} | MUST_NOT_CITE_STATUSES):
                if rel not in dropped:
                    dropped[rel] = {"path": rel, "id": fm_id or rel, "reason": fm_status}
                continue

        body = span(chunk["path"], chunk["start_line"], chunk["end_line"])
        candidates.append({**chunk, "routes": hit["routes"], "body": body,
                           "text": f"[path: {chunk['path']}]\n{body.decode('utf-8', 'replace')[:RERANK_CHARS]}",
                           "_batch": batch_assignments[hit["chunk_id"]]})

    try:
        ranked, reranked_by = rerank(query, candidates, reranker), last_outcome()
    except (OSError, RuntimeError, ValueError) as error:
        ranked = candidates
        reranked_by = {"by": "unavailable", "device": None, "reason": f"{type(error).__name__}: {error}"}
    ranked = order.reranked(ranked)  # W2-87: the rerank does not undo the authority order (DEC-952)

    # W2-32 S8 (DEC-1067 (a)): routing by question type, each half behind its own setting (off: today's order)
    if route_settings["named_first"] and start and routes.get(CLOSURE):
        named_ids = set(start)
        own = [chunk for chunk in routes[CLOSURE]
               if (record_of.get(chunk["path"]) if chunk["path"] != register
                   else (entry_of(chunk["path"], chunk["start_line"]) or {}).get("id")) in named_ids]
        # P-W2-32-9: the scores the pool's rerank already gave (the chunks put ahead are on the page, so scored);
        # no request of its own, so the rerank stays one of the merged set in full requests of 16
        own_ids = {chunk["chunk_id"] for chunk in own}
        mine = [(position, candidate) for position, candidate in enumerate(ranked) if candidate["chunk_id"] in own_ids]
        if mine:
            if all("rerank_score" in candidate for _, candidate in mine):
                best = [candidate["chunk_id"] for _, candidate in
                        sorted(mine, key=lambda pair: (-pair[1]["rerank_score"], pair[0]))]
            else:  # no reranker scored the page: by the stored vectors' cosine, else the page's order
                best = _by_cosine(root, query, [candidate["chunk_id"] for _, candidate in mine])
            ranked, routed[routing.NAMED] = routing.ahead(ranked, routing.firsts(best, route_settings["named_first"]))
    if route_settings["code_first"] and coded is not None and routes.get(code_route.FACET):
        best = [hit["chunk_id"] for hit in routes[code_route.FACET]]  # already by cosine, before the fusion
        ranked, routed[routing.CODE] = routing.ahead(ranked, routing.firsts(best, route_settings["code_first"]))

    # DEC-424: sort failure/lesson records ahead of other evidence after reranking
    if ahead_paths:
        ahead_ranked = [c for c in ranked if c["path"] in ahead_paths]
        rest_ranked = [c for c in ranked if c["path"] not in ahead_paths]
        ranked = ahead_ranked + rest_ranked

    # W2-32 S7: a chunk whose parent an earlier call expanded lies inside a span already sent: it is not sent again,
    # and is named in ``repeats`` (within one call a parent's other children are still sent, DP-3). The converse
    # (DEC-1067): lines an earlier call sent as a child on its own are left out of a parent expanded later, and each
    # such child's span is named in ``repeats`` the same way, with its own reason.
    repeats = [{**{key: candidate[key] for key in ("chunk_id", "path", "start_line", "end_line", "parent_id")},
                "reason": IN_EARLIER_PARENT} for candidate in ranked if candidate["parent_id"] in earlier]
    ranked = [candidate for candidate in ranked if candidate["parent_id"] not in earlier]
    used = sum(_tokens(candidate["body"].decode("utf-8", "replace")) for candidate in ranked)
    evidence, expansions, expanded = [], [], set(earlier)  # W2-32 S7: never a parent an earlier call sent

    def item(candidate, rel, first, last, body):
        return {"id": record_of.get(rel, candidate["chunk_id"]), "sha256": hashlib.sha256(body).hexdigest(),
                "path": rel, "start_line": first, "end_line": last, "text": body.decode("utf-8", "replace"),
                "chunk_id": candidate["chunk_id"], "routes": candidate["routes"], "batch": candidate["_batch"]}

    for candidate in ranked:
        rel, first, last, body = candidate["path"], candidate["start_line"], candidate["end_line"], candidate["body"]
        parent = lexical.parent(root, candidate["parent_id"])
        if parent and (parent["start_line"], parent["end_line"]) != (first, last) and parent["parent_id"] not in expanded:
            top, bottom = parent["start_line"], parent["end_line"]
            # DEC-1067 (review F-5): the lines an earlier call sent as a child on its own are left out of the parent
            children = sorted(child for child in alone if child[0] == rel and top <= child[1] and child[2] <= bottom)
            held = _merged((a, b) for _, a, b, _ in children)
            runs = _without(top, bottom, held)
            pieces = [(a, b, span(rel, a, b)) for a, b in runs]
            cost = sum(_tokens(piece.decode("utf-8", "replace")) for *_, piece in pieces) \
                - _tokens(body.decode("utf-8", "replace"))
            if used + cost <= limit:
                used = used + cost
                expanded.add(parent["parent_id"])
                expansions.append({"chunk_id": candidate["chunk_id"], "parent_id": parent["parent_id"], "path": rel,
                                   "start_line": top, "end_line": bottom,
                                   **({"left_out": [list(span_) for span_ in held]} if held else {})})
                repeats.extend({"chunk_id": chunk_id, "path": path, "start_line": a, "end_line": b,
                                "parent_id": parent["parent_id"], "reason": EARLIER_CHILD}
                               for path, a, b, chunk_id in children)  # each span sent earlier, as it was sent
                if not pieces:  # the whole parent was sent before, child by child: nothing of it again
                    repeats.append({**{key: candidate[key]
                                       for key in ("chunk_id", "path", "start_line", "end_line", "parent_id")},
                                    "reason": EARLIER_CHILD})
                evidence.extend(item(candidate, rel, a, b, piece) for a, b, piece in pieces)
                continue
        sent_alone.add((rel, first, last, candidate["chunk_id"]))
        evidence.append(item(candidate, rel, first, last, body))

    reasons = {gap["reason"] for gap in gaps}
    if not all(facet["available"] for facet in facets.values()):
        stopping = closures.FACET_UNAVAILABLE
    elif remaining:
        stopping = BUDGET_EXHAUSTED
    elif closures.DEPTH_LIMIT in reasons:
        stopping = closures.DEPTH_LIMIT
    elif closures.UNRESOLVED in reasons:
        stopping = closures.UNRESOLVED_ALONE
    else:
        stopping = closures.COMPLETE if start else SATURATED

    new_offset = offset + len(gathering)
    if remaining:
        token = _encode_continuation(query, tuple(ids), ticket, radius, batch_size, bundle_budget, new_offset,
                                     expanded, sent_alone)
    else:
        token = None

    bundle = {"stopping_reason": stopping, "evidence": evidence, "batches": batches_list,
              "merge": {"candidates": len(gathering), "duplicates": sum(map(len, routes.values())) - len(fused),
                        "dropped": [dropped[rel] for rel in sorted(dropped)],
                        "reranked": any("rerank_score" in candidate for candidate in ranked)},
              "rerank": reranked_by,  # W2-112: who scored (service, private) and on which device, or unavailable
              "expansions": expansions, "repeats": repeats, "gaps": gaps, "facets": facets,
              "budget": {"bundle": {"limit": limit, "used": used},
                         "rounds": {"limit": rounds_limit, "used": rounds_used}},
              "continuation": token}
    if any(route_settings.values()):  # W2-32 S8: what the routing moved ahead, per half that is on
        bundle["routing"] = {**{half: [] for half, key in ((routing.CODE, "code_first"), (routing.NAMED, "named_first"))
                                if route_settings[key]}, **routed}
    if withhold is not None:
        bundle["role_filter"] = withhold.summary()  # DEC-1065 (2): what was withheld, how many and by which rule
    return bundle
