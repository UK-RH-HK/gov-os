"""The brief's memory block (W2-197 S1, S2, F1; EMERGENCY-2 5.4): the ticket's retrieval, put into T-0's
``{MEMORY_BLOCK}`` by ``gov brief``.

The retrieval is ``gov.retrieval.retrieve.retrieve(<store>, <query>, ticket=<id>, role=<the brief's role>)``, run as
the role's own session would run it: ``GOV_ROLE`` is the brief's role and ``GOV_TICKET`` the ticket while it runs, so
the path map's role filter withholds what that role may not be handed (DEC-1065 (2)); both are restored after. The
query is the ticket's ``title``, else its body's first ``# `` heading, else its id; the store is ``--store``, else
``GOV_STORE``, else facts.yaml's ``paths.store_tree`` filled, else the root.

A store that is missing or cannot be read, or any fault of the search, never refuses a brief: the block says
``Memory not reached: <CODE> <detail>.`` and the brief gets the warning ``MEMORY_UNAVAILABLE`` (F1), as it does for
a bundle that was not reranked. Nothing here writes; the command logs the retrieval (``gov.memory_use``).
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

WARNING = "MEMORY_UNAVAILABLE"
FIRST_LINE = 100  # characters of an item's first non-empty line in the index
HEADING = re.compile(r"^# (.+?)\s*$", re.MULTILINE)


def query_of(front: dict, body: str, ticket_id: str) -> str:
    """The ticket's ``title``, else its body's first ``# `` heading, else its id."""
    title = front.get("title")
    if isinstance(title, str) and title.strip():
        return " ".join(title.split())
    heading = HEADING.search(body or "")
    return " ".join(heading.group(1).split()) if heading else str(ticket_id)


def store_root(root: Path, flag: str | None, store_tree: str | None) -> Path:
    """``--store``, else ``GOV_STORE`` (its link followed once), else facts.yaml's ``paths.store_tree`` as filled
    (one with a key left unfilled is none), else the root; a relative store_tree is the root's."""
    if flag:
        return Path(flag)
    named = os.environ.get("GOV_STORE")
    if named:
        from gov.launch.store import StoreSettingError, session_root

        try:
            return session_root(named)
        except StoreSettingError:
            return Path(named)  # not absolute: the search names it as STORE_MISSING or reads it, never a refusal
    if store_tree and "{" not in store_tree:
        return Path(store_tree) if os.path.isabs(store_tree) else Path(root) / store_tree
    return Path(root)


def _first_line(text: str) -> str:
    return next((line.strip() for line in str(text).splitlines() if line.strip()), "")[:FIRST_LINE]


def gather(store: Path, query: str, ticket: str, role: str) -> dict:
    """The retrieval as the role's own session runs it: ``{store, commit, query, stop_reason, reranked, refusal,
    detail, rerank_reason, items, characters, latency_ms}``, each item ``{rank, path, start_line, end_line, id,
    line}``; a fault is ``refusal`` (its code) and ``detail``, never raised."""
    import sqlite3

    from gov.cli.errors import GovError
    from gov.retrieval.retrieve import resolved, retrieve, store_of

    folder = resolved(store)
    found = {"store": str(folder), "commit": None, "query": query, "stop_reason": None, "reranked": False,
             "refusal": None, "detail": None, "rerank_reason": None, "items": [], "characters": 0, "latency_ms": 0,
             "head": None}
    saved = {name: os.environ.get(name) for name in ("GOV_ROLE", "GOV_TICKET")}
    started = time.monotonic()
    try:
        os.environ["GOV_ROLE"], os.environ["GOV_TICKET"] = role, ticket
        store_named = store_of(folder, role)  # W2-138 S1: the commit the store was built at, as gov retrieve names it
        bundle = retrieve(folder, query, ticket=ticket, role=role, store=store_named)
    except GovError as error:
        found["refusal"], found["detail"] = error.code, error.message
    except sqlite3.DatabaseError as error:
        found["refusal"], found["detail"] = "STORE_UNREADABLE", f"the store at {folder} cannot be read: {error}"
    except Exception as error:  # noqa: BLE001 - F1: memory never refuses a brief
        found["refusal"], found["detail"] = "RETRIEVE_FAILED", f"{type(error).__name__}: {error}"
    else:
        evidence = bundle.get("evidence") or []
        found.update({
            "commit": store_named.get("commit"), "head": store_named.get("head"),
            "stop_reason": bundle.get("stopping_reason"),
            "reranked": bool((bundle.get("merge") or {}).get("reranked")),
            "rerank_reason": (bundle.get("rerank") or {}).get("reason"),
            "items": [{"rank": rank, "path": item.get("path"), "start_line": item.get("start_line"),
                       "end_line": item.get("end_line"), "id": item.get("id"), "line": _first_line(item.get("text"))}
                      for rank, item in enumerate(evidence, 1)],
            "characters": sum(len(str(item.get("text", ""))) for item in evidence),
        })
    finally:
        found["latency_ms"] = int((time.monotonic() - started) * 1000)
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    return found


def _quoted(text: str) -> str:
    """``text`` in double quotes, so a shell passes it whole: a backslash, quote, dollar or backtick escaped."""
    return '"' + re.sub(r'([\\"$`])', r"\\\1", text) + '"'


def _one_line(text) -> str:
    return " ".join(str(text or "").split())


def block(found: dict, ticket: str) -> str:
    """T-0's ``{MEMORY_BLOCK}``: the store, query, count, stop reason and rerank on one line, one index line per item
    in a fenced block, and the two commands; for a refusal, the not-reached line and the two commands."""
    store = found["store"]
    commands = [f"The whole bundle: `gov retrieve --root {store} --ticket {ticket} {_quoted(found['query'])}`.",
                f"Search again in your own words: `gov retrieve --root {store} \"<your question>\"`."]
    if found.get("refusal"):
        return "\n".join([f"Memory not reached: {found['refusal']} {_one_line(found.get('detail'))}.", *commands])
    commit = str(found["commit"])[:12] if found.get("commit") else "unknown"
    head = (f"Store {commit} ({store}); query {_quoted(found['query'])}; {len(found['items'])} items; "
            f"stop {found['stop_reason']}; reranked {'true' if found['reranked'] else 'false'}.")
    index = [f"{item['rank']}. {item['path']}:{item['start_line']}-{item['end_line']} {item['id']} {item['line']}"
             .rstrip() for item in found["items"]]
    moved = found.get("head")
    if moved and found.get("commit") and moved != found["commit"]:  # P0-1: the brief says a store is behind HEAD
        head += f" This is a store behind HEAD: the store is at {commit}, HEAD is {str(moved)[:12]}."
    return "\n".join([head, "```", *index, "```", *commands])


def public(found: dict) -> dict:
    """``result.memory`` of ``--json``: store, commit, query, stop_reason, reranked, refusal, items."""
    keys = ("rank", "path", "start_line", "end_line", "id")
    return {"store": found["store"], "commit": found["commit"], "query": found["query"],
            "stop_reason": found["stop_reason"], "reranked": found["reranked"], "refusal": found["refusal"],
            "items": [{key: item[key] for key in keys} for item in found["items"]]}


def warning(found: dict) -> dict | None:
    """``MEMORY_UNAVAILABLE`` for a refusal or a bundle not reranked; None otherwise."""
    if found.get("refusal"):
        return {"code": WARNING, "detail": f"{found['refusal']} {_one_line(found.get('detail'))}"}
    if not found.get("reranked"):
        reason = _one_line(found.get("rerank_reason"))
        return {"code": WARNING, "detail": "the bundle is not reranked" + (f" ({reason})" if reason else "")}
    return None


def record(found: dict, role: str, ticket: str, session: str | None, latency_ms: int = 0) -> dict:
    """The memory-use line of the brief's retrieval (W2-197 S8)."""
    from gov.memory_use import query_hash

    return {"command": "brief", "role": role, "ticket": ticket, "session": session or None,
            "query_sha256": query_hash(found["query"]), "stop_reason": found["stop_reason"],
            "items": len(found["items"]), "characters": found["characters"], "latency_ms": int(latency_ms),
            "refusal": found["refusal"], "store_commit": found["commit"], "reranked": found["reranked"]}
