#!/usr/bin/env python3
"""REPAIR-1 node R1-GA3: helpers that let ``govbridge.compile.packet`` compile sections B-H from
``govbridge.gather.followup.gather_with_followup`` results (REPAIR_PLAN.md sections 2.8-2.10; RC-4, RC-5;
REPAIR_DAG.yaml node R1-GA3). Kept a separate, leaf module (imports nothing from ``govbridge.compile.packet``) so
``packet.py`` -- already large, and shared with RX/RM before this node -- stays the ONE place that decides section
placement/ordering; this module only ever computes DATA those decisions consume:

* **facet attribution** for one merged gather item, disclosed as an approximation where gather's own return shape
  does not itemise it (``govbridge.gather.followup``'s own module docstring and its ``failed_approaches``: calling
  the engine once per facet inside ``gather_with_followup`` itself was tried and reverted, because it would drop
  R1-GA1's tested cross-facet PARALLEL round property for every caller, including the CLI ``gather`` command --
  never this node's file to change. A caller with different needs, like a compiler that wants a defensible facet
  tag for round-robin quotas, recovers what it needs at ITS OWN layer instead);
* **content slicing** for a code/test/semantic item whose route only ever attached a pointer (a bare signature, an
  edge label, or no text at all -- RC-5), read fresh from Git at the item's own occurrence;
* **oversize mandatory-item section selection** by the gather facet vocabulary (BR-DAG-AMEND-R1-11), a PURE
  function of a document's own content and the versioned facet registry alone -- deliberately never of which
  facets any one task's queries happened to request (see ``select_oversize_facet_sections``'s own docstring for
  why: ``govbridge.compile.validate``'s independent re-derivation recomposes a mandatory item's body from nothing
  but ``(mi, dparts, repo, per_item_cap_bytes)``, so anything this module adds to that composition must be
  reproducible from the exact same inputs, never from a particular compile's task-specific facet selection);
* **overflow packaging** -- when a query's gathered evidence does not entirely fit the compiled packet, shaping the
  dropped remainder into an R1-RN hierarchical evidence note and an R1-RS supplementary packet, so nothing is
  silently discarded (REPAIR_PLAN.md section 2.8, OD-BR-06 section 4).
"""
from __future__ import annotations

from typing import Optional

from govbridge.core import gitobj
from govbridge.core.yamlutil import sha256_text
from govbridge.gather import facets as facetsmod
from govbridge.notes import build as notesbuildmod

# ---------------------------------------------------------------------------------------------------------------
# facet attribution (RC-4's "per-item facet tags")
# ---------------------------------------------------------------------------------------------------------------

#: the tag a base-round item (gather_with_followup's own disclosed gap: engine.gather's return shape does not
#: itemise which facet produced which hit) gets when NO requested facet's declared scope/route is even consistent
#: with it -- an honest "could not attribute", never a fabricated facet name.
UNATTRIBUTED_FACET = "unattributed"


def facet_tags_for_merged_item(item_dict: dict, requested_facets: dict) -> tuple:
    """``item_dict``: one row of ``gather_with_followup(...)["merged"]`` (a
    ``govbridge.gather.merge.MergedItem.to_dict()`` shape: ``provenance`` is a list of
    ``{route, facet, round, trigger}``). ``requested_facets``: ``{name: govbridge.gather.facets.Facet}``, the
    facets THIS query actually requested (``govbridge.gather.facets.facets_for_query``).

    Returns the tuple of facet names this item is tagged with, in a fixed, deterministic order:

    * a follow-up-round item (``provenance[*].facet == "followup:<kind>"``) is tagged with that exact trigger kind
      (precise -- the identifier that caused it to be fetched is known exactly, REPAIR_PLAN.md section 2.5's own
      "each follow-up item records its trigger");
    * a base-round item (every ``provenance[*].facet is None`` -- ``gather_with_followup``'s own disclosed
      boundary) is tagged with every REQUESTED facet whose declared ``routes`` include this item's own ``route``
      and whose ``scope_classes``/``lifecycle_scope`` (when declared) accept its ``authority_class``/``lifecycle``
      -- a defensible, disclosed SUPERSET, never a claim that this is the one facet call that actually produced it;
    * :data:`UNATTRIBUTED_FACET` when neither of the above yields anything (a route/class combination none of the
      requested facets declare -- honest, never silently dropped from quota bookkeeping)."""
    provenance = item_dict.get("provenance") or []
    followup_kinds = sorted({
        p["facet"].split(":", 1)[1] for p in provenance
        if isinstance(p.get("facet"), str) and p["facet"].startswith("followup:")
    })
    if followup_kinds:
        return tuple(f"followup:{k}" for k in followup_kinds)

    route = item_dict.get("route")
    cls = item_dict.get("authority_class")
    lifecycle = item_dict.get("lifecycle")
    matched = []
    for name, facet in sorted(requested_facets.items()):
        if facet.synthetic:
            continue
        if facet.routes and route not in facet.routes:
            continue
        if not facet.in_scope(cls, lifecycle):
            continue
        matched.append(name)
    return tuple(matched) if matched else (UNATTRIBUTED_FACET,)


def facet_min_shares(facets_path: Optional[str] = None) -> dict:
    """``{facet_name: min_share}`` for every registered facet (``config/facets.yaml``) -- the SAME registry
    ``govbridge.gather`` itself reads, never a second, diverging copy of the shares."""
    return {name: f.min_share for name, f in facetsmod.load_facets(facets_path).items()}


# ---------------------------------------------------------------------------------------------------------------
# content slices instead of pointers (RC-5)
# ---------------------------------------------------------------------------------------------------------------

def read_content_slice(path: Optional[str], commit: Optional[str], line_start: Optional[int],
                        line_end: Optional[int], repo: Optional[str], max_chars: Optional[int],
                        pad: int = 0) -> Optional[str]:
    """The exact text of ``path``@``commit``, or the ``[line_start-pad, line_end+pad]`` slice of it when a line
    range is given, capped to ``max_chars`` (a disclosed, marked truncation -- never a silent one: this is
    RETRIEVED/DERIVED evidence, not a mandatory item, so the per-item-cap discipline of
    ``govbridge.compile.packet._read_excerpt``/``Compiler._mandatory_text`` does not apply here, but a body must
    still never look complete when it was cut). ``None`` on any failure (an honest MISSING, never a crash) --
    the caller keeps whatever pointer text it already had."""
    if not path or not commit:
        return None
    try:
        raw = gitobj.read_path(commit, path, repo=repo)
    except gitobj.GitError:
        return None
    if raw is None:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if line_start is not None:
        lines = text.splitlines(keepends=True)
        l1 = max(1, line_start - pad)
        l2 = min(len(lines), (line_end or line_start) + pad)
        text = "".join(lines[l1 - 1:l2])
    if max_chars is not None and len(text.encode("utf-8")) > max_chars:
        # cut on a UTF-8-safe boundary (never split a multi-byte codepoint), then mark the cut -- a truncated
        # RETRIEVED slice must never read as if it were the whole thing.
        encoded = text.encode("utf-8")[:max_chars]
        text = encoded.decode("utf-8", errors="ignore") + f"\n... [content slice truncated at {max_chars} bytes]"
    return text


def needs_content_slice(unit_kind: str, route: Optional[str], text: Optional[str]) -> bool:
    """RC-5's exact three pointer shapes this node repairs at the compile layer (``real_routes.py`` -- not this
    node's file to edit -- still attaches only a bare signature/edge label for a code-route hit, and no text at
    all for a semantic hit):

    * a ``symbol`` unit from the code route (``_code_hit_from_definition``'s ``"{kind} {qualified_name}"``);
    * an ``occurrence`` unit from the code route (a CALLS/TESTS/READS_KEY/CITED edge's own one-line label);
    * a ``chunk`` unit from the semantic route with NO text at all (``semantic_route``'s ``text=None``).

    A lexical ``chunk`` (already real chunk text) or anything already carrying substantial text is left alone."""
    if route == "code" and unit_kind in ("symbol", "occurrence"):
        return True
    if route == "semantic" and unit_kind == "chunk" and not text:
        return True
    return False


# ---------------------------------------------------------------------------------------------------------------
# oversize mandatory-item section selection (BR-DAG-AMEND-R1-11)
# ---------------------------------------------------------------------------------------------------------------

def _facet_terms(facets_path: Optional[str] = None) -> tuple:
    """Every generic term the gather facet registry declares -- each facet's own NAME (split on ``_``) plus its
    ``extra_terms`` (``config/facets.yaml``: "every extra_terms entry is a generic English word... never a path, a
    file name, a Review-8 item"). A PURE function of the (versioned, sha256'd) config file alone -- the SAME set
    for every caller and every compile of the same commit, so a mandatory item's oversize section selection is
    reproducible by anyone who calls it with the SAME (default) ``facets_path``, including
    ``govbridge.compile.validate``'s blind re-derivation (``_composition_context_class``), which supplies no task,
    no query set and no per-task facet list at all -- see this module's own top docstring."""
    terms = set()
    for name, facet in facetsmod.load_facets(facets_path).items():
        terms.update(name.split("_"))
        terms.update(t.lower() for t in facet.extra_terms)
    return tuple(sorted(terms))


def _section_score(name: str, terms: tuple) -> int:
    """A section's own NAME (a Markdown heading title or a YAML key -- never its body text, which is free-form
    prose and far too likely to contain an incidental match against a generic English word like "must" or "test")
    scored by how many distinct gather-facet terms it contains, case-insensitively, as whole words. Zero unless at
    least one whole-word match is found."""
    lowered = f" {name.lower()} "
    score = 0
    for term in terms:
        needle = f" {term} "
        if needle in lowered or lowered.startswith(f"{term} ") or lowered.endswith(f" {term}") or lowered.strip() == term:
            score += 1
    return score


def select_oversize_facet_sections(disclosure_map: tuple, max_sections: int = 6, max_extra_bytes: int = 49152,
                                    facets_path: Optional[str] = None) -> tuple:
    """``(selected, remaining)`` -- both lists of ``oversize_disclosure_map`` rows (``{path, commit, line_start,
    line_end, name, sha256, bytes}``). ``selected`` is chosen by scoring every section's own NAME against the
    gather facet registry's generic terms (:func:`_facet_terms`), highest first, ties by document order
    (``line_start``), taking sections while a score > 0 remains AND both ``max_sections`` and ``max_extra_bytes``
    still have room -- REPAIR_PLAN.md section 3 rule 1 ("plus the sections selected by the task's facets"),
    BR-DAG-AMEND-R1-11. Zero-scoring sections, and anything past either cap, land in ``remaining`` (still fully
    disclosed by reference, exactly as before this amendment -- "nothing is ever removed from A"). Deterministic:
    the SAME ``disclosure_map`` and the SAME (default) facet registry always select the SAME sections, which is
    what lets ``govbridge.compile.validate``'s blind re-derivation reproduce this exactly (see this module's own
    top docstring)."""
    terms = _facet_terms(facets_path)
    scored = [(row, _section_score(row["name"], terms)) for row in disclosure_map]
    ranked = sorted(
        (r for r in scored if r[1] > 0),
        key=lambda r: (-r[1], r[0]["line_start"] if r[0]["line_start"] is not None else 0),
    )
    selected_names: set = set()
    used_bytes = 0
    for row, _score in ranked:
        if len(selected_names) >= max_sections:
            break
        b = row.get("bytes") or 0
        if used_bytes + b > max_extra_bytes:
            continue
        selected_names.add(row["name"])
        used_bytes += b
    selected = [row for row in disclosure_map if row["name"] in selected_names]
    remaining = [row for row in disclosure_map if row["name"] not in selected_names]
    return selected, remaining


# ---------------------------------------------------------------------------------------------------------------
# gather-merged-item <-> RouteHit-dict adapter (so R1-RS's supplementary-packet builder, written against
# engine.gather's plain RouteHit-shaped "merged" list, also accepts gather_with_followup's richer
# MergedItem-shaped one)
# ---------------------------------------------------------------------------------------------------------------

def merged_items_as_hit_dicts(merged: list) -> list:
    """``gather_with_followup(...)["merged"]`` is a list of ``MergedItem.to_dict()`` rows (one ``occurrence`` dict
    plus a ``ref_summary`` and ``provenance``) -- a DIFFERENT shape from ``engine.gather(...)["merged"]``'s plain
    ``RouteHit.to_dict()`` rows (an ``occurrences`` LIST) that ``govbridge.compile.supplementary.extract_items``
    was written against (R1-RS ran in the same parallel group as R1-GA2, REPAIR_DAG.yaml's R1-PG3, each unaware of
    the other's exact return shape). This adapter reconciles the two, losslessly for every field
    ``extract_items``'s own ``_items_from_route_hits`` actually reads (``unit_kind``, ``unit_id``, ``route``,
    ``text``, ``authority_class``, ``lifecycle``, ``occurrences``)."""
    out = []
    for md in merged:
        occ = md.get("occurrence")
        out.append({
            "unit_id": md.get("unit_id"), "unit_kind": md.get("unit_kind"), "route": md.get("route"),
            "rank": None, "delivery": md.get("delivery"), "text": md.get("text"),
            "authority_class": md.get("authority_class"), "lifecycle": md.get("lifecycle"),
            "occurrences": [occ] if occ else [], "edge_path": [], "tier": md.get("tier"),
            "resolution": md.get("resolution"),
        })
    return out


# ---------------------------------------------------------------------------------------------------------------
# overflow -> hierarchical evidence note + supplementary packet (REPAIR_PLAN.md sections 2.8-2.10)
# ---------------------------------------------------------------------------------------------------------------

def _claim_from_overflow_item(query_id: str, index: int, item_dict: dict, repo: Optional[str]) -> Optional[dict]:
    """One R1-RN claim, grounded in exactly one source (``config/notes-schema.yaml``'s ``source_fields``: item_id,
    path, commit, blob, lines, content_sha256 -- every one required, every one independently re-verified by
    ``govbridge.notes.validate.resolve_source``). ``None`` when this item carries no concrete, groundable line
    range or its blob cannot be resolved -- an honest inability to ground it, surfaced by the caller in the note's
    own ``unresolved`` list rather than fabricated here."""
    occ = item_dict.get("occurrence") or {}
    path, commit = occ.get("path"), occ.get("commit")
    l1, l2 = occ.get("line_start"), occ.get("line_end")
    if not path or not commit or l1 is None:
        return None
    l2 = l2 or l1
    try:
        blob = gitobj.blob_at(commit, path, repo=repo)
    except Exception:
        blob = None
    if not blob:
        return None
    try:
        raw = gitobj.read_path(commit, path, repo=repo)
    except gitobj.GitError:
        raw = None
    if raw is None:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    file_lines = text.splitlines()
    if not (1 <= l1 <= l2 <= len(file_lines)):
        return None
    slice_text = "\n".join(file_lines[l1 - 1:l2])
    content_sha256 = sha256_text(slice_text)
    snippet = (item_dict.get("text") or "").strip().splitlines()
    snippet_text = snippet[0][:240] if snippet else f"{item_dict.get('unit_kind')}:{item_dict.get('unit_id')}"
    return {
        "claim_id": f"{query_id}-overflow-{index}",
        "text": f"additional evidence for query {query_id!r}, item {item_dict.get('unit_kind')}:"
                f"{item_dict.get('unit_id')}: {snippet_text}",
        "sources": [{
            "item_id": item_dict.get("unit_id"), "path": path, "commit": commit, "blob": blob,
            "lines": [l1, l2], "content_sha256": content_sha256,
        }],
    }


def build_overflow_note(query_id: str, overflow_items: list, repo: Optional[str] = None) -> Optional[dict]:
    """A ``govbridge.notes`` DERIVED_NOTE (built, not yet validated -- the caller runs
    ``govbridge.notes.validate.validate_note`` before trusting it) summarising evidence that gather retrieved for
    ``query_id`` but the compiled packet could not fit. ``None`` when ``overflow_items`` is empty (no note is
    built for a query with nothing left over). Every item that cannot be grounded in an exact, reconfirmable
    Git line range (REPAIR_PLAN.md section 2.10's schema) is listed in the note's own ``unresolved`` instead of a
    fabricated claim -- OD-BR-06 section 4: "disclose unresolved evidence"."""
    if not overflow_items:
        return None
    claims: list = []
    unresolved: list = []
    for i, item_dict in enumerate(overflow_items):
        claim = _claim_from_overflow_item(query_id, i, item_dict, repo)
        if claim is not None:
            claims.append(claim)
        else:
            unresolved.append({"unit_kind": item_dict.get("unit_kind"), "unit_id": item_dict.get("unit_id"),
                                "reason": "no groundable (path, commit, concrete line range, resolvable blob)"})
    if not claims and not unresolved:
        return None
    return notesbuildmod.build_note(note_id=f"overflow-{query_id}", claims=claims, unresolved=unresolved)
