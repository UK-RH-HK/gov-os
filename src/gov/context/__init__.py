"""``gov context``: compiled, budgeted, hashed context packets (W1-24; CAP-15, CAP-01, CAP-38).

``context(root, ticket, *, brief=False, budget=None)`` reads the ticket's file once, resolves its declared mandatory
inputs from the record store (a register entry as its own span, W2-03), orders them by authority precedence, adds
supplementary context in batches when room allows (DEC-860), and returns a deterministic packet with a sha256 hash.
The ticket's own text and the mandatory inputs are never shortened: where they alone pass the ceiling the context
refuses (``CONTEXT_OVER_CEILING``, CAP-15.d, W2-04).
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path

from gov.cli.errors import GovError

PRECEDENCE = ("charter", "contract", "decision", "specification", "ticket")
PRECEDENCE_RANK = {kind: i for i, kind in enumerate(PRECEDENCE)}
DEFAULT_BUDGET = 6000
TOKEN_CHARS = 4
BRIEF_LIMIT = 2500
EXTERNAL_REFERENCES_REL = "governance/project/external-references.yaml"
TICKETS_REL = ".tickets"
NO_LONGER_STANDS = ("SUPERSEDED", "RETIRED", "REJECTED")  # DEC-568: only these say a record no longer stands
INDEX_UNAVAILABLE = "index unavailable"
OVER_CEILING = "CONTEXT_OVER_CEILING"
# id forms the repository itself holds, never an outside source's (DEC-551 P-12, DEC-552 finding 9): a decision of
# the register, a decision file, a capability and its items, a must rule, a lesson, a work-breakdown id
_HELD_FORM = re.compile(r"DEC-\d+|ADR-\d+|CAP-\d+(\.[a-z]+)?|MR-\d+|L-\d{4,}|W\d+-\d{2,}")


def _tokens(text: str) -> int:
    return -(-len(text) // TOKEN_CHARS)


def _read_record(root: Path, record: dict, ticket: str) -> tuple[str, str]:
    """The sha256 and the text of a mandatory record: a register entry's own span and ``content_hash`` (W2-03, AR-1),
    another record's file; BLOCKED where it cannot be read (never read as empty)."""
    if record.get("in_register"):
        if not record.get("span") or not record.get("content_hash"):
            raise GovError("BLOCKED", f"mandatory input {record['id']!r}: its span of the register {record['path']} "
                                      f"cannot be read (the store holds none)",
                           {"ticket": ticket, "unreadable": record["id"], "file": record["path"]})
        return record["content_hash"], record["span"]
    try:
        content = (root / record["path"]).read_bytes()
        return hashlib.sha256(content).hexdigest(), content.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        reason = getattr(exc, "strerror", None) or "it is not UTF-8 text"
        raise GovError("BLOCKED", f"mandatory input {record['id']!r}: its file {record['path']} cannot be read "
                                  f"({reason})", {"ticket": ticket, "unreadable": record["id"],
                                                "file": record["path"]}) from None


def _store_query(root: Path, sql: str, params: tuple = ()) -> list:
    from gov.store import connect
    conn = connect(root)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def _record_map(root: Path) -> dict:
    """id -> record of the store; an entry of the register carries ``in_register``, its span and its hash."""
    from gov import records
    from gov.retrieval.authority import register_path
    known = records.records(root)
    register = register_path(known)
    return {record["id"]: {**record, "in_register": register is not None and record["path"] == register}
            for record in known}


def _supersedes_edges(root: Path) -> set:
    rows = _store_query(root, "SELECT source, target FROM edges WHERE type = 'SUPERSEDES'")
    return {(r[0], r[1]) for r in rows}


def _read_ticket(root: Path, ticket: str) -> tuple[str, str, dict]:
    """The ticket file's path, its text and its frontmatter, from the one read of it the context makes (W2-L183)."""
    import yaml
    rel = f"{TICKETS_REL}/{ticket}.md"
    try:
        text = (root / rel).read_bytes().decode("utf-8")
        lines = [line.rstrip() for line in text.split("\n")]
        front = yaml.safe_load("\n".join(lines[1:lines.index("---", 1)])) if lines[0] == "---" else None
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError):
        front = None
    if not isinstance(front, dict):
        raise GovError("BLOCKED", f"ticket {ticket!r} not found", {"ticket": ticket})
    return rel, text, front


def _ticket_mandatory_ids(front: dict) -> list:
    ids, seen = [], set()
    for field in ("sources", "depends_on", "deps"):
        for item in (front.get(field) or []):
            s = str(item)
            if s not in seen:
                ids.append(s)
                seen.add(s)
    return ids


def _ticket_source_ids(front: dict) -> list:
    """The ids the ticket declares as ``sources``, its dependencies left out (W1-41)."""
    return [str(item) for item in (front.get("sources") or [])]


def _kpi_lines(front: dict) -> list:
    """The ticket's KPI lines, success then failure, as its frontmatter states them."""
    kpis = front.get("kpis")
    if isinstance(kpis, list):
        return [str(line) for line in kpis]
    if not isinstance(kpis, dict):
        return []
    return [str(line) for kind in ("success", "failure") for line in (kpis.get(kind) or [])]


def external_references(root: Path) -> dict:
    """The sources the project lists as living outside the repository: id -> its entry (W1-41; DEC-520).

    The file is the one ``HEAD`` holds, never the working tree's or the index's
    (DEC-552, finding 9): a change that is in no commit lists nothing. A project
    whose commit has no such file lists none. A file that is there and cannot be
    read, is not valid YAML or is not of the stated shape is BLOCKED and named,
    never taken for an empty list (DEC-449, DEC-454).
    """
    import yaml
    from gov.store.loader import _file, _tree

    def defect(why: str, **more) -> GovError:
        return GovError("BLOCKED", f"{EXTERNAL_REFERENCES_REL}: {why}",
                        {"file": EXTERNAL_REFERENCES_REL, **more})

    try:
        tree = _tree(Path(root))
    except GovError as exc:
        raise defect(f"the commit that holds the file cannot be read: {exc.message}") from None
    if EXTERNAL_REFERENCES_REL not in tree:
        return {}
    text = _file(Path(root), tree, EXTERNAL_REFERENCES_REL)
    if text is None:
        raise defect("the file cannot be read: the commit does not hold it as a file of UTF-8 text")
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
        if _HELD_FORM.fullmatch(rid):
            raise defect(f"{rid!r} has the form of an id the repository itself holds (a decision, a capability, "
                         f"a must rule, a lesson, a work-breakdown id) and is never an external reference", id=rid)
        listed[rid] = entry
    return listed


def _make_item(record: dict, sha: str, reason: str, tokens: int) -> dict:
    return {
        "id": record["id"],
        "sha256": sha,
        "authority": record["type"],
        "lifecycle": record["status"],
        "constraint": sha,
        "reason": reason,
        "tokens": tokens,
    }


def _try_supplementary(root: Path, title: str, kpis: list, room: int, skip_paths: set, skip_entries: set) -> dict:
    """The supplementary block (``gov.retrieval.supplementary.stack``) for ``room`` tokens; a failed lookup is one
    entry of ``dropped``, named by its kind (W2-L180), and the block empty."""
    from gov.retrieval import supplementary
    try:
        return supplementary.stack(root, title, kpis, room, skip_paths=skip_paths, skip_entries=skip_entries)
    except Exception as exc:
        reason = str(exc) if isinstance(exc, supplementary.Unavailable) else _lookup_failure(root, exc)
        return {"query": supplementary.query(title, kpis), "supplementary": [], "further_batch": [],
                "dropped": [{"id": "supplementary", "reason": reason}], "left_out": None}


def _synthesis(root: Path) -> dict | None:
    """Whether the project's synthesis notes pass their validator, and the failure codes; None without notes (W2-M134,
    CAP-15.f)."""
    from gov.retrieval.synthesis import NOTES_REL, validate_notes
    if not (root / NOTES_REL).exists():
        return None
    try:
        result = validate_notes(root)
    except Exception as exc:  # notes that cannot be read are never valid
        return {"valid": False, "codes": ["NOTES_UNREADABLE"], "reason": " ".join(str(exc).split())}
    return {"valid": bool(result["valid"]), "codes": sorted({error["code"] for error in result["errors"]})}


def _lookup_failure(root: Path, exc: Exception) -> str:
    """What failed in the supplementary lookup, in the failure's own words; the index only where it is the index."""
    if isinstance(exc, sqlite3.Error) or (isinstance(exc, GovError) and exc.code == "STORE_MISSING"):
        return INDEX_UNAVAILABLE
    if isinstance(exc, OSError) and exc.filename:
        name = Path(exc.filename)
        rel = name.relative_to(root) if name.is_relative_to(root) else name
        return f"the lookup could not read {rel}: {exc.strerror}"
    return f"the lookup failed: {' '.join(str(exc).split()) or type(exc).__name__}"


def context(root: Path, ticket: str, *, brief: bool = False, budget: int | None = None,
            dry_run: bool = False) -> dict:
    root = Path(root)
    limit = budget if budget is not None else DEFAULT_BUDGET

    ticket_rel, ticket_text, front = _read_ticket(root, ticket)  # the one read of the ticket (W2-L183)
    declared_ids = _ticket_mandatory_ids(front)
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
                           f"mandatory input {rid!r} is SUPERSEDED and cannot satisfy a current requirement",
                           {"ticket": ticket, "superseded": rid, "status": rec["status"]})
        if rec["status"] in NO_LONGER_STANDS:  # DEC-552 finding 10: only a record that stands satisfies
            raise GovError("BLOCKED",
                           f"mandatory input {rid!r} is {rec['status']}: it no longer stands and cannot satisfy "
                           f"a current requirement", {"ticket": ticket, "no_longer_stands": rid,
                                                      "status": rec["status"]})
        resolved.append(rec)
    # every source is external: no source was read, and a dependency that was read is not one (DEC-454, DEC-552);
    # a ticket that declares no source is judged on every id it declares, as before
    sources = _ticket_source_ids(front) or declared_ids
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
    mandatory_tokens = _tokens(ticket_text)  # the ticket's own text is never dropped (CAP-15.d)
    for rec in resolved:
        sha, content = _read_record(root, rec, ticket)
        mandatory_tokens += _tokens(content)
        mandatory_items.append(_make_item(rec, sha, "declared in sources", _tokens(content)))
    mandatory_items.sort(key=lambda item: PRECEDENCE_RANK.get(item["authority"], 999))
    if mandatory_tokens > limit:  # nothing of it is shortened: the context refuses (AR-1, F-M5)
        raise GovError(OVER_CEILING, f"ticket {ticket!r}: its own text and its mandatory inputs come to "
                                     f"{mandatory_tokens} tokens, over the packet's ceiling of {limit} tokens",
                       {"ticket": ticket, "limit": limit, "mandatory_tokens": mandatory_tokens})

    # Step 6: authority block — exclude records superseded by another mandatory record
    authority_items = []
    for item in mandatory_items:
        superseded_by_another = any(
            (other["id"], item["id"]) in sup_edges
            for other in mandatory_items if other["id"] != item["id"]
        )
        if not superseded_by_another:
            authority_items.append(item)

    # Supplementary context: in batches, ranked and stacked into the room the mandatory part leaves (DEC-860)
    skip_paths = {ticket_rel} | {rec["path"] for rec in resolved if not rec.get("in_register")}
    skip_entries = {rec["id"] for rec in resolved if rec.get("in_register")}
    block = _try_supplementary(root, str(front.get("title", "")), _kpi_lines(front), limit - mandatory_tokens,
                               skip_paths, skip_entries)
    supplementary, left_out = block["supplementary"], block["left_out"]
    # one order whatever order the retrieval returned its items in (DEC-768): an entry is its id and its reason,
    # so the two decide every pair that differ; what is kept still follows the retrieval's rank
    dropped = sorted(block["dropped"], key=lambda entry: (entry["id"], entry["reason"]))

    total_tokens = mandatory_tokens + sum(item["tokens"] for item in supplementary)
    if total_tokens > limit:  # never ok over the budget, whatever a lookup returned (AR-1)
        raise GovError(OVER_CEILING, f"ticket {ticket!r}: the packet comes to {total_tokens} tokens, over its "
                                     f"ceiling of {limit} tokens",
                       {"ticket": ticket, "limit": limit, "mandatory_tokens": mandatory_tokens})

    packet = {
        "ticket": ticket,
        "ticket_text": ticket_text,
        "authority": authority_items,
        "mandatory": mandatory_items,
        "supplementary": supplementary,
        "supplementary_query": block["query"],
        "further_batch": block["further_batch"],
        "dropped": dropped,
        "tokens": total_tokens,
        "budget": {"limit": limit, "used": total_tokens},
    }
    if external:  # absent where the ticket declares none (W1-41)
        packet["external"] = external
    if left_out:  # absent where nothing was left out (W2-55)
        packet["left_out"] = left_out
    synthesis = _synthesis(root)
    if synthesis is not None:  # absent where the project holds no synthesis notes (W2-M134)
        packet["synthesis"] = synthesis
    # Deterministic hash of the packet content, the hash itself left out
    canonical = json.dumps(packet, sort_keys=True, separators=(",", ":"))
    packet["hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

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
        if left_out:
            summary_parts.append(f"  - {left_out['count']} superseded or done register entries left out")
        if synthesis is not None:
            summary_parts.append("  synthesis notes: " + ("valid" if synthesis["valid"]
                                                          else "INVALID (" + ", ".join(synthesis["codes"]) + ")"))
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
