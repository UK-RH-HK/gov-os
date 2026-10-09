"""``gov context``: compiled, budgeted, hashed context packets (W1-24; CAP-15, CAP-01, CAP-38).

``context(root, ticket, *, brief=False, budget=None)`` resolves the ticket's
declared mandatory inputs from the record store, orders them by authority
precedence, adds supplementary context from retrieval when room allows, and
returns a deterministic packet with a sha256 hash.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from gov.cli.errors import GovError

PRECEDENCE = ("charter", "contract", "decision", "specification", "ticket")
PRECEDENCE_RANK = {kind: i for i, kind in enumerate(PRECEDENCE)}
DEFAULT_BUDGET = 6000
TOKEN_CHARS = 4
BRIEF_LIMIT = 2500
EXTERNAL_REFERENCES_REL = "governance/project/external-references.yaml"
_REGISTER_FORM = re.compile(r"DEC-\d+")  # DEC-473: the form of a register entry's id


def _tokens(text: str) -> int:
    return -(-len(text) // TOKEN_CHARS)


def _record_content(root: Path, record: dict) -> str:
    try:
        return (root / record["path"]).read_text(encoding="utf-8")
    except OSError:
        return ""


def _sha256_file(root: Path, record: dict) -> str:
    try:
        return hashlib.sha256((root / record["path"]).read_bytes()).hexdigest()
    except OSError:
        return hashlib.sha256(b"").hexdigest()


def _store_query(root: Path, sql: str, params: tuple = ()) -> list:
    from gov.store import connect
    conn = connect(root)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def _record_map(root: Path) -> dict:
    rows = _store_query(root, "SELECT id, type, status, path FROM records")
    return {r[0]: {"id": r[0], "type": r[1], "status": r[2], "path": r[3]} for r in rows}


def _supersedes_edges(root: Path) -> set:
    rows = _store_query(root, "SELECT source, target FROM edges WHERE type = 'SUPERSEDES'")
    return {(r[0], r[1]) for r in rows}



def _ticket_mandatory_ids(root: Path, ticket: str) -> list:
    from gov.tasks.tickets import frontmatter
    front = frontmatter(root / ".tickets" / f"{ticket}.md")
    if front is None:
        raise GovError("BLOCKED", f"ticket {ticket!r} not found", {"ticket": ticket})
    ids, seen = [], set()
    for field in ("sources", "depends_on", "deps"):
        for item in (front.get(field) or []):
            s = str(item)
            if s not in seen:
                ids.append(s)
                seen.add(s)
    return ids


def _ticket_source_ids(root: Path, ticket: str) -> list:
    """The ids the ticket declares as ``sources``, its dependencies left out (W1-41)."""
    from gov.tasks.tickets import frontmatter
    front = frontmatter(root / ".tickets" / f"{ticket}.md") or {}
    return [str(item) for item in (front.get("sources") or [])]


def external_references(root: Path) -> dict:
    """The sources the project lists as living outside the repository: id -> its entry (W1-41; DEC-520).

    A project without the file lists none. A file that is there and cannot be
    read, is not valid YAML or is not of the stated shape is BLOCKED and named,
    never taken for an empty list (DEC-449, DEC-454).
    """
    import yaml

    def defect(why: str, **more) -> GovError:
        return GovError("BLOCKED", f"{EXTERNAL_REFERENCES_REL}: {why}",
                        {"file": EXTERNAL_REFERENCES_REL, **more})

    try:
        text = (Path(root) / EXTERNAL_REFERENCES_REL).read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeDecodeError) as exc:
        raise defect(f"the file cannot be read: {exc}") from exc
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise defect(f"the file is not valid YAML: {exc}") from exc
    entries = document.get("references") if isinstance(document, dict) else None
    if not isinstance(entries, list):
        raise defect("the file is not a mapping with a list `references`")
    listed: dict = {}
    for number, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            raise defect(f"entry {number} is not a mapping")
        for key in ("id", "location", "reason"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                raise defect(f"entry {number} has no `{key}` that is text and not empty")
        rid = entry["id"]
        if rid in listed:
            raise defect(f"the id {rid!r} is listed twice", id=rid)
        if _REGISTER_FORM.fullmatch(rid):
            raise defect(f"{rid!r} is a decision of the register, which lives in the repository "
                         f"and is never an external reference", id=rid)
        listed[rid] = entry
    return listed


def _make_item(record: dict, sha: str, reason: str) -> dict:
    return {
        "id": record["id"],
        "sha256": sha,
        "authority": record["type"],
        "lifecycle": record["status"],
        "constraint": sha,
        "reason": reason,
    }


def _supplementary_query(root: Path, ticket: str) -> str:
    from gov.tasks.tickets import frontmatter
    front = frontmatter(root / ".tickets" / f"{ticket}.md")
    if not front:
        return ticket
    title = str(front.get("title", ""))
    words = [w for w in title.split() if len(w) > 2]
    if words:
        return words[0]
    return title or ticket


def _try_supplementary(root: Path, ticket: str, budget_remaining: int) -> tuple[list, list]:
    try:
        from gov.retrieval.retrieve import retrieve
        query = _supplementary_query(root, ticket)
        bundle = retrieve(root, query, ticket=ticket)
        evidence = bundle.get("evidence", [])
        if not evidence:
            return [], []
        supplementary, dropped = [], []
        for item in evidence:
            text = item.get("text", "")
            cost = _tokens(text)
            if budget_remaining >= cost:
                supplementary.append({
                    "id": item.get("id", item.get("chunk_id", "")),
                    "text": text,
                    "path": item.get("path", ""),
                    "tokens": cost,
                })
                budget_remaining -= cost
            else:
                dropped.append({
                    "id": item.get("id", item.get("chunk_id", "")),
                    "reason": "budget exceeded",
                })
        return supplementary, dropped
    except Exception:
        return [], [{"id": "supplementary", "reason": "index unavailable"}]


def context(root: Path, ticket: str, *, brief: bool = False, budget: int | None = None,
            dry_run: bool = False) -> dict:
    root = Path(root)
    limit = budget if budget is not None else DEFAULT_BUDGET

    declared_ids = _ticket_mandatory_ids(root, ticket)
    if not declared_ids:
        raise GovError("BLOCKED", f"ticket {ticket!r} declares no mandatory inputs",
                       {"ticket": ticket})

    records = _record_map(root)
    sup_edges = _supersedes_edges(root)
    listed = external_references(root)  # a defective file blocks every ticket's context
    # Step 3: resolve mandatory inputs; the store is asked first, the list never hides a record
    resolved = []
    external = []
    for rid in declared_ids:
        rec = records.get(rid)
        if rec is None and rid in listed:
            external.append({"id": rid, "location": listed[rid]["location"],
                             "reason": listed[rid]["reason"], "read": False})
            continue
        if rec is None:
            raise GovError("BLOCKED", f"mandatory input {rid!r} not found in the store",
                           {"ticket": ticket, "missing": rid})
        if rec["status"] == "SUPERSEDED":
            raise GovError("BLOCKED",
                           f"mandatory input {rid!r} is superseded and cannot satisfy a current requirement",
                           {"ticket": ticket, "superseded": rid})
        resolved.append(rec)
    # every source is external: no source was read, and a dependency that was read is not one (DEC-454, DEC-552);
    # a ticket that declares no source is judged on every id it declares, as before
    sources = _ticket_source_ids(root, ticket) or declared_ids
    if not any(rec["id"] in sources for rec in resolved):
        ids = [item["id"] for item in external]
        raise GovError("BLOCKED",
                       f"ticket {ticket!r}: every declared source is an external reference "
                       f"({', '.join(repr(i) for i in ids)}) and none was read",
                       {"ticket": ticket, "external": ids})

    # Step 4: check for conflicts at the same precedence level
    by_type: dict[str, list] = {}
    for rec in resolved:
        by_type.setdefault(rec["type"], []).append(rec)
    for rec_type, recs in by_type.items():
        if len(recs) < 2:
            continue
        for i, a in enumerate(recs):
            for b in recs[i + 1:]:
                a_sup_b = (a["id"], b["id"]) in sup_edges
                b_sup_a = (b["id"], a["id"]) in sup_edges
                if a_sup_b or b_sup_a:
                    superseded = b["id"] if a_sup_b else a["id"]
                    raise GovError("BLOCKED",
                                   f"mandatory input {superseded!r} is superseded at the same level "
                                   f"({rec_type}) and cannot satisfy a current requirement",
                                   {"ticket": ticket, "superseded": superseded})
                if a["status"] == "ACTIVE" and b["status"] == "ACTIVE":
                    raise GovError("CONTRADICTION",
                                   f"conflicting mandatory inputs at the same level "
                                   f"({rec_type}): {a['id']!r} and {b['id']!r}",
                                   {"ticket": ticket, "conflicting": [a["id"], b["id"]]})

    # Build mandatory items sorted by precedence
    mandatory_items = []
    for rec in resolved:
        sha = _sha256_file(root, rec)
        mandatory_items.append(_make_item(rec, sha, "declared in sources"))
    mandatory_items.sort(key=lambda item: PRECEDENCE_RANK.get(item["authority"], 999))

    # Step 6: authority block — exclude records superseded by another mandatory record
    authority_items = []
    for item in mandatory_items:
        superseded_by_another = any(
            (other["id"], item["id"]) in sup_edges
            for other in mandatory_items if other["id"] != item["id"]
        )
        if not superseded_by_another:
            authority_items.append(item)

    # Token counting for mandatory
    mandatory_tokens = 0
    for item in mandatory_items:
        content = _record_content(root, records[item["id"]])
        mandatory_tokens += _tokens(content)

    budget_remaining = limit - mandatory_tokens
    dropped: list[dict] = []

    # Supplementary context
    supplementary, supp_dropped = _try_supplementary(root, ticket, max(0, budget_remaining))
    dropped.extend(supp_dropped)

    supp_tokens = sum(item.get("tokens", 0) for item in supplementary)
    total_tokens = mandatory_tokens + supp_tokens
    budget_info = {"limit": limit, "used": total_tokens}

    # Deterministic hash of the packet content
    packet_for_hash = {
        "ticket": ticket,
        "authority": authority_items,
        "mandatory": mandatory_items,
        "supplementary": supplementary,
        "dropped": dropped,
        "tokens": total_tokens,
        "budget": budget_info,
    }
    if external:  # absent where the ticket declares none: the packet and its hash stay W1-24's
        packet_for_hash["external"] = external
    canonical =json.dumps(packet_for_hash, sort_keys=True, separators=(",", ":"))
    packet_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    packet = {
        "ticket": ticket,
        "authority": authority_items,
        "mandatory": mandatory_items,
        "supplementary": supplementary,
        "dropped": dropped,
        "hash": packet_hash,
        "tokens": total_tokens,
        "budget": budget_info,
    }
    if external:
        packet["external"] = external

    if brief:
        summary_parts = [f"Context for {ticket}:"]
        for item in mandatory_items:
            summary_parts.append(f"  {item['id']} ({item['authority']}, {item['lifecycle']})")
        for item in external:
            summary_parts.append(f"  {item['id']} (external, not read)")
        if supplementary:
            summary_parts.append(f"  + {len(supplementary)} supplementary items")
        if dropped:
            summary_parts.append(f"  - {len(dropped)} items dropped")
        summary = "\n".join(summary_parts)
        if _tokens(summary) > BRIEF_LIMIT:
            summary = summary[:BRIEF_LIMIT * TOKEN_CHARS]

        sanitized = ticket.replace("..", "_").replace("/", "_").replace("\\", "_")
        scratch = root / ".gov-runtime" / "scratch" / "context"
        brief_path = (scratch / f"{sanitized}.json").resolve()
        if not str(brief_path).startswith(str(scratch.resolve())):
            brief_path = scratch / "sanitized.json"

        if not dry_run:
            brief_path.parent.mkdir(parents=True, exist_ok=True)
            brief_path.write_text(json.dumps(packet, sort_keys=True, indent=2), encoding="utf-8")
            return {"path": str(brief_path), "summary": summary}
        return {"path": "", "summary": summary}

    return packet
