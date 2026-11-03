"""The supplementary block of a context packet: ranked, taken in batches, stacked (W2-04; DEC-860, CAP-15.d).

The evidence comes from the lexical facet alone, so that the block, and the packet's hash, are the same whether or not
the semantic index answers (AR-9, W2-M239): the query's words are searched one by one, a chunk is ranked by the sum
over the words it holds of one over the number of chunks that hold the word (a rarer word weighs more), and equal
ranks are ordered by path, then id, then the first line a word was found on. The ranked chunks are read a batch at a
time and stacked in rank order into the room the packet leaves; the stack stops at the first chunk that does not fit,
and the chunks of its batch from it on are named as left for a further batch. Where the room ends exactly on a stacked
chunk, or is none at all, the next ranked chunks, one batch at most, are named instead (DEC-1025 item 2).

Role separation (W2-13 S5, DEC-1065 (2)): a chunk the caller's role may not be handed (``GOV_ROLE``, ``GOV_TICKET``,
the main tree's ``role_paths:``; ``gov.guard.role_paths``) is never ranked; where a filter applies, the block's
``role_filter`` counts what was withheld by rule, and one entry of ``dropped`` (id ``role_filter``) says it in a line,
so the packet names it. Role paths that cannot be read raise: the packet's block is then empty and names why.
"""

from __future__ import annotations

import re
from pathlib import Path

BATCH_SIZE = 10
MAX_TERMS = 12  # each word is one search of the index: the longest words of the query, this many (W2-M126)
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9_-]*[A-Za-z0-9]")
_COMMON = frozenset("""
about above after again against also always among another before being below between both cannot could does doing
down during each either even ever every from have having here into itself just like many more most must never none
only other over same shall should since some such than that their them then there these they this those through under
until upon very were what whatever when where whether which while whose will with within without would your
""".split())
NOT_STANDING = frozenset({"SUPERSEDED", "RETIRED", "REJECTED", "DEPRECATED", "WITHDRAWN"})  # DEC-568, DEC-423


class Unavailable(Exception):
    """The lexical index did not answer; its reason is the index's own (missing, stale or empty)."""


def query(title: str, kpis: list[str]) -> str:
    """The supplementary query: the ticket's title and its KPI lines, one to a line (W2-M126)."""
    return "\n".join(line for line in [title, *kpis] if line)


def terms(text: str) -> list[str]:
    """The words of ``text`` that are searched: four letters or more, not a common word, as written, the longest
    first (then in alphabetical order), ``MAX_TERMS`` at most."""
    words = {word for word in _WORD.findall(text) if len(word) >= 4 and word.lower() not in _COMMON}
    return sorted(words, key=lambda word: (-len(word), word))[:MAX_TERMS]


def _ranked(root: Path, words: list[str], skip_paths: set, skip_entries: set,
            withhold=None) -> tuple[list[dict], dict | None]:
    """Every chunk that holds a word, in rank order, without the chunks of ``skip_paths``, of a path the caller's
    role may not be handed (``withhold``, which counts them), of a record that no longer stands, or of a register
    entry that is in ``skip_entries`` or is not current; and W2-55's ``left_out``."""
    from gov import records
    from gov.decisions.register import leave_out
    from gov.retrieval import authority, lexical

    holders: dict[str, set] = {}
    where: dict[str, tuple] = {}  # chunk id -> its path and the first line a word was found on
    for word in words:
        answer = lexical.search(root, word, refresh=False)
        if not answer["available"]:
            raise Unavailable(f"the lexical index is {answer['reason']}")
        for hit in answer["hits"]:
            holders.setdefault(word, set()).add(hit["chunk_id"])
            path, line = where.get(hit["chunk_id"], (hit["path"], hit["line"]))
            where[hit["chunk_id"]] = (path, min(line, hit["line"]))
    score: dict[str, float] = {}
    for word in sorted(holders):  # one order of the sums: equal word sets give equal scores, in every process
        weight = 1.0 / len(holders[word])
        for chunk_id in holders[word]:
            score[chunk_id] = score.get(chunk_id, 0.0) + weight

    known = records.records(root)
    edges = records.edges(root, type=authority.SUPERSEDES)
    superseded = {edge["target"] for edge in edges}
    record_of = {record["path"]: record for record in known if record.get("span") is None}
    register = authority.register_path(known)
    entry_of = authority.register_entries_of(known, edges, root)
    own = {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root, register)} \
        if register and any(path == register for path, _ in where.values()) else {}
    items = []
    for chunk_id, (path, line) in where.items():
        if path in skip_paths:
            continue
        if withhold is not None and not withhold.keep([{"path": path, "chunk_id": chunk_id}]):
            continue  # W2-13 S5 (DEC-1065 (2)): withheld from the caller's role, and counted
        item = {"path": path, "chunk_id": chunk_id, "_line": line, "_score": score[chunk_id], "_standing": True}
        if path == register:
            chunk = own.get(chunk_id)
            if chunk is None:
                continue
            entry = entry_of(path, chunk["start_line"])
            item.update(id=entry["id"] if entry else chunk_id, start_line=chunk["start_line"],
                        end_line=chunk["end_line"],
                        _standing=entry is None or (entry["id"] not in skip_entries and entry["current"]))
        else:
            record = record_of.get(path)
            if record is not None and (record["status"] in NOT_STANDING or record["id"] in superseded):
                continue
            item["id"] = record["id"] if record else chunk_id
        items.append(item)
    items.sort(key=lambda item: (-item["_score"], item["path"], item["id"], item["_line"], item["chunk_id"]))
    kept, left_out = leave_out(root, items)  # the register's superseded and done entries first (W2-55, DEC-791 item 1)
    return [{key: value for key, value in item.items() if not key.startswith("_")}
            for item in kept if item["_standing"]], left_out


def _text(root: Path, item: dict, files: dict) -> str:
    """The text of the item's chunk, its lines looked up when the item's batch is taken."""
    from gov.retrieval import lexical
    rel = item["path"]
    if rel not in files:
        files[rel] = ((Path(root) / rel).read_bytes().splitlines(keepends=True),
                      {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root, rel)})
    lines, chunks = files[rel]
    chunk = item if "start_line" in item else chunks.get(item["chunk_id"])
    if chunk is None:
        raise LookupError(f"the lexical index holds no chunk {item['chunk_id']} of {rel}")
    return b"".join(lines[chunk["start_line"] - 1:chunk["end_line"]]).decode("utf-8", "replace")


def stack(root: Path, title: str, kpis: list[str], room: int, *, skip_paths=(), skip_entries=(), role=None,
          ticket=None) -> dict:
    """The supplementary block for ``room`` tokens: ``{"query", "supplementary", "dropped", "further_batch",
    "supplementary_batches", "left_out"}``, each batch the ranked items it read and its limit, in the order taken.
    ``Unavailable`` where the lexical index does not answer."""
    from gov.context import _tokens
    from gov.guard import role_paths

    asked = query(title, kpis)
    # W2-13 S5: GOV_ROLE, a --role beside it (``role``: adds, never lifts) and GOV_TICKET; RolePathsError when unreadable
    # review S5-F1: the packet's own ``ticket`` judged beside GOV_TICKET (the union: it only adds)
    withhold = role_paths.caller(root, role, also=(ticket,) if ticket else ())
    ranked, left_out = _ranked(Path(root), terms(asked), set(skip_paths), set(skip_entries), withhold)
    files: dict[str, tuple] = {}
    supplementary, dropped, batches = [], [], []
    taken, left_from = 0, None
    while room > 0:
        limit = min(BATCH_SIZE, room)  # never more chunks than the room has tokens
        batch = ranked[taken:taken + limit]
        batches.append({"items": [{"id": item["id"], "path": item["path"]} for item in batch], "limit": limit})
        for place, item in enumerate(batch):
            text = _text(root, item, files)
            cost = _tokens(text)
            if cost > room:
                left_from = taken + place
                dropped = [{"id": left["id"], "reason": "budget exceeded"} for left in batch[place:]]
                room = -1
                break
            supplementary.append({"id": item["id"], "path": item["path"], "text": text, "tokens": cost})
            room -= cost
        taken += len(batch)
        if len(batch) < limit:  # the evidence ended: this batch holds fewer items than its limit
            break
    if left_from is not None:  # what is left is the last batch's items from the first that did not fit (S7a)
        further = ranked[left_from:taken]
    elif room == 0 and taken < len(ranked):
        # the room ended exactly on a stacked item, or there was none (DEC-1025 item 2): the next items in rank order,
        # one batch at most (the largest limit taken, or a batch's size where none was taken), no batch taken for them
        size = max((batch["limit"] for batch in batches), default=BATCH_SIZE)
        further = ranked[taken:taken + size]
        dropped = [{"id": left["id"], "reason": "budget exceeded"} for left in further]
    else:  # no item was left unstacked
        further = []
    block = {"query": asked, "supplementary": supplementary, "dropped": dropped,
             "further_batch": [{"id": item["id"], "path": item["path"]} for item in further],
             "supplementary_batches": batches, "left_out": left_out}
    if withhold is not None:  # DEC-1065 (2): named, never silent; the packet carries it as one entry of dropped
        block["role_filter"] = shown = withhold.summary()
        block["dropped"] = [*dropped, {"id": ROLE_FILTER_ID, "reason": withheld_reason(shown)}]
    return block


ROLE_FILTER_ID = "role_filter"


def withheld_reason(shown: dict) -> str:
    """The filter's count and rules in one line: how many paths and chunks were withheld, by which rule."""
    rules = "; ".join(f"{b['paths']} by role_paths.{b['role']}.reads_denied {b['rule']} ({b['glob']})"
                      for b in shown["by"]) or "none matched"
    return (f"withheld from {', '.join(shown['roles'])} (ticket {shown['ticket']}): {shown['withheld']['paths']} "
            f"paths, {shown['withheld']['chunks']} chunks; {rules} (DEC-1065 (2))")
