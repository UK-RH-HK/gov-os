#!/usr/bin/env python3
"""``govbridge demo grade`` -- the deterministic half of grading (DEMONSTRATION_DESIGN.md section 4): computes
every check marked **[D]** for gates G1-G8, against the schemas ``answers.yaml``/``receipt.yaml``/
``grading-report.yaml``. Checks marked **[R]** (rubric, prose judgment) are left for the SEPARATE fresh-opus rubric
grader (node GRADE, BR-AR-0012) to fill in -- this module reports them as ``PENDING_RUBRIC``, never guesses a
verdict for them, and never claims DEMONSTRATION_PASS on their behalf. Where a [D+R] check has a mechanical,
citation- or constant-level component (e.g. "cites none of the oracle's forbidden items", or the ``classification``/
``disposition`` field must be an exact constant), that mechanical component IS computed here -- generic
citation/anchor matching, never a special case for Review 8, F1-F6 or Phase 2 (OC-BR-02): every rule below reads
its subject (chain stages, query classes, anchors, forbidden lists) from the oracle and the public query set as
data.

Orchestrator Addendum A1 (GATES/BR-ARCH-RULING-1-...md): G3's packet-side check for section A does not fail a
lifecycle-UNKNOWN mandatory item that carries its banner and a matching J notice (BR-ARCH-RULING-1); an oracle
``authority_expectations`` row expecting an A-admissible item outside A is read as expecting A, and every such
reinterpreted row is listed in the grading report.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Optional

from govbridge.authority import classes as classesmod
from govbridge.core.yamlutil import load_yaml_file

PENDING_RUBRIC = "PENDING_RUBRIC"

# A-admissible ladder classes (ranks 1-6) -- BR-ARCH-RULING-1's own scope: "Every item the resolver returns whose
# class is admissible in A (ladder ranks 1-6) is placed in A... whatever its lifecycle."
_A_ADMISSIBLE_CLASSES = {c.name for c in classesmod.LADDER if c.admissible_in_a}


# ---------------------------------------------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------------------------------------------

def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_packet_dir(path: str) -> dict:
    d = Path(path)
    manifest = _load_json(str(d / "manifest.json"))
    task_spec = load_yaml_file(str(d / "task_spec.yaml"))
    meta = {}
    meta_path = d / "meta.json"
    if meta_path.exists():
        meta = _load_json(str(meta_path))
    return {"dir": str(d), "manifest": manifest, "task_spec": task_spec, "meta": meta}


def _manifest_items_by_id(manifest: dict) -> dict:
    """Keyed by BOTH the packet's hashed ``item_id`` (what ``schemas/answers.yaml`` literally names as a
    citation) AND the human-readable ``unit.id`` (the ONLY identifier actually printed in the rendered packet
    text -- ``_render_item_body`` in ``govbridge/compile/render.py`` shows ``unit: {kind}:{unit_id}``, never the
    hash). A worker can only cite what it can read, so this grader resolves a citation against either form."""
    out = {}

    def _index(row):
        out[row["item_id"]] = row
        uid = row.get("unit", {}).get("id")
        if uid:
            out.setdefault(uid, row)

    for letter, sec in manifest["sections"].items():
        if letter == "D":
            for sub in sec["subblocks"].values():
                for row in sub["items"]:
                    _index(row)
        else:
            for row in sec["items"]:
                _index(row)
    return out


def _every_section_ids(manifest: dict) -> dict:
    out = {}
    for letter, sec in manifest["sections"].items():
        if letter == "D":
            for sub, subsec in sec["subblocks"].items():
                out[sub] = [row["unit"]["id"] for row in subsec["items"]]
        else:
            out[letter] = [row["unit"]["id"] for row in sec["items"]]
    return out


# ---------------------------------------------------------------------------------------------------------------
# G1 / G2: packet validity, receipt -- thin wrappers over the existing, independent modules.
# ---------------------------------------------------------------------------------------------------------------

def grade_g1(packets: list, repo: Optional[str] = None) -> dict:
    from govbridge.compile import validate as validatemod
    results = []
    for p in packets:
        problems = validatemod.verify_packet(p["manifest"], p["task_spec"], repo=repo,
                                              registry_path=p["meta"].get("registry_path"))
        results.append({"packet_id": p["meta"].get("packet_id") or p["manifest"].get("packet_id"),
                         "verify": "PASS" if not problems else "FAIL", "problems": problems})
    result = "PASS" if all(r["verify"] == "PASS" for r in results) else "FAIL"
    return {"result": result, "packets": results}


def grade_g2(packets: list, receipt: dict, repo: Optional[str] = None) -> dict:
    from govbridge.compile import receipt as receiptmod
    results = []
    for p in packets:
        r = receiptmod.check(p["manifest"], receipt, p["task_spec"], repo=repo,
                              registry_path=p["meta"].get("registry_path"))
        results.append({"packet_id": p["meta"].get("packet_id") or p["manifest"].get("packet_id"), **r})
    result = "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL"
    return {"result": result, "reasons": [pr for r in results for pr in r.get("problems", [])]}


# ---------------------------------------------------------------------------------------------------------------
# G3: authority classes preserved (packet side [D]; answer side left [R]/PENDING_RUBRIC, with a mechanical
# approximation of the "presented as a decision/classification" and "cited as a finding" checks).
# ---------------------------------------------------------------------------------------------------------------

_DECISION_PHRASES = [
    re.compile(r"\bhas been (?:decided|authorised|approved)\b", re.I),
    re.compile(r"\bis (?:now )?(?:authoris|approv)ed\b", re.I),
    re.compile(r"\b(?:should|must|shall) be (?:deleted|simplified|repaired|narrowed|retained)\b", re.I),
    re.compile(r"\bdisposition\s*:\s*(?:DELETE|SIMPLIFY|REPAIR|NARROW|RETAIN)\b"),
]
_CLASSIFICATION_PHRASES = [
    re.compile(r"\bare (?:one|the same|a single) (?:deeper )?(?:defect )?class\b", re.I),
    re.compile(r"\bare (?:two )?(?:different|distinct|separate) (?:defect )?classes\b", re.I),
]
# GD-4: the withdrawn-finding marker, generic across spelling: `(WITHDRAWN)`, `[WITHDRAWN]`, `-- WITHDRAWN`,
# `: WITHDRAWN`, any case. The only fixed signal is the word itself -- never one literal bracket/phrase form.
_WITHDRAWN_MARKER_RE = re.compile(r"\bwithdrawn\b", re.I)


def _withdrawn_citation_line(item_id: str, text: str) -> tuple:
    """Follow-up to GD-4 (orchestrator finding on the quarantined run, 2026-09-26): a phrase/marker scan can tell
    whether ``item_id`` is cited, and whether a withdrawn marker shares its line, but it CANNOT tell whether that
    citation is offered "as a finding" (support for a claim) versus, say, listed among the packet's own mandatory
    inputs -- that is a prose judgement, [R], never a [D] certainty. Returns ``(quote, marker_present)`` for the
    FIRST line citing ``item_id`` (whichever form it takes), or ``(None, None)`` if it is never cited at all.
    ``marker_present`` is reported for the rubric grader's convenience; it never decides this check's verdict."""
    id_re = re.compile(re.escape(item_id))
    for line in text.splitlines():
        if id_re.search(line):
            return line.strip(), bool(_WITHDRAWN_MARKER_RE.search(line))
    return None, None


def _packet_side_authority_expectations(oracle: dict, main_by_section: dict, main_items_by_id: dict) -> tuple:
    """Returns (problems, reinterpreted_rows) -- BR-ARCH-RULING-1 Addendum A1's packet-side G3 check, evaluated
    against the MAIN packet's own section map. ``reinterpreted_rows`` lists every oracle row the addendum's
    A-admissible-implies-A reading affected, exactly as the addendum requires ("the grader must record, in the
    grading report, every oracle row that this reading affected")."""
    problems: list = []
    reinterpreted: list = []
    for row in oracle.get("authority_expectations") or []:
        item, expected_sections, cls = row.get("item"), row.get("sections") or [], row.get("class")
        expect_a = "A" in expected_sections
        if cls in _A_ADMISSIBLE_CLASSES and not expect_a:
            expected_sections = ["A"]
            expect_a = True
            reinterpreted.append({"item": item, "oracle_sections": row.get("sections"), "read_as": ["A"],
                                   "reason": "A-admissible mandatory class; Addendum A1"})
        actual_section = next((sec for sec, ids in main_by_section.items() if item in ids), None)
        if actual_section is None:
            problems.append(f"{item}: not found in any packet section (expected one of {expected_sections})")
            continue
        if actual_section not in expected_sections:
            problems.append(f"{item}: found in section {actual_section!r}, expected one of {expected_sections}")
            continue
        row_manifest = main_items_by_id.get(item)
        if row_manifest is not None and cls and row_manifest.get("authority_class") != cls:
            problems.append(f"{item}: class {row_manifest.get('cls')!r} != oracle class {cls!r}")
    return problems, reinterpreted


def grade_g3(oracle: dict, answers: dict, main_packet: dict, rubric: Optional[dict] = None) -> dict:
    manifest = main_packet["manifest"]
    by_section = _every_section_ids(manifest)
    items_by_id = _manifest_items_by_id(manifest)

    packet_problems, reinterpreted = _packet_side_authority_expectations(oracle, by_section, items_by_id)

    # Addendum A1, section A's own hard rule (independent of the oracle): every A row is either a non-ladder class
    # (fails), or a non-ACTIVE row without its banner/J-notice (fails); D.1 fails on non-ladder or non-ACTIVE.
    notices = manifest.get("notices") or []
    lifecycle_notice_ids = {n["id"] for n in notices if n.get("type") == "MANDATORY_LIFECYCLE_NOT_ACTIVE"}
    for row in manifest["sections"]["A"]["items"]:
        cls = row.get("authority_class")
        if cls not in _A_ADMISSIBLE_CLASSES:
            packet_problems.append(f"A/{row['unit']['id']}: class {cls!r} is not a ladder A-admissible class")
            continue
        if row.get("delivery") not in ("MANDATORY",):
            packet_problems.append(f"A/{row['unit']['id']}: delivery {row.get('delivery')!r} != MANDATORY "
                                    f"(only the resolver may place an item in A)")
        if row.get("lifecycle") != classesmod.LIFECYCLE_ACTIVE:
            if not row.get("banner"):
                packet_problems.append(f"A/{row['unit']['id']}: non-ACTIVE lifecycle {row.get('lifecycle')!r} "
                                        f"lacks its lifecycle banner")
            if row["unit"]["id"] not in lifecycle_notice_ids:
                packet_problems.append(f"A/{row['unit']['id']}: non-ACTIVE lifecycle with no "
                                        f"MANDATORY_LIFECYCLE_NOT_ACTIVE J notice")
    # D.1 lives at sections["D"]["subblocks"]["D.1"] in the rendered manifest.
    d1_items = (manifest["sections"].get("D", {}).get("subblocks", {}).get("D.1", {}) or {}).get("items", [])
    for row in d1_items:
        cls = row.get("authority_class")
        if cls not in ("OWNER_DECISION", "ARCHITECTURE_DECISION", "ORCHESTRATION_RECORD"):
            packet_problems.append(f"D.1/{row['unit']['id']}: class {cls!r} is not D.1-admissible")
        if row.get("lifecycle") != classesmod.LIFECYCLE_ACTIVE:
            packet_problems.append(f"D.1/{row['unit']['id']}: lifecycle {row.get('lifecycle')!r} != ACTIVE")

    # F1/F2/F3 packet-side placement (generic: only checked if the oracle names these items at all).
    for row in oracle.get("authority_expectations") or []:
        item = row.get("item")
        if row.get("class") == "OWNER_DIRECTION_TO_TEST":
            if item not in by_section.get("D.2", []):
                packet_problems.append(f"{item}: OWNER_DIRECTION_TO_TEST must be in D.2 only")
            for sec, ids in by_section.items():
                if sec != "D.2" and item in ids:
                    packet_problems.append(f"{item}: OWNER_DIRECTION_TO_TEST must never appear outside D.2 "
                                            f"(also found in {sec})")
        if row.get("class") == "HYPOTHESIS_TO_TEST":
            if item not in by_section.get("D.3", []):
                packet_problems.append(f"{item}: HYPOTHESIS_TO_TEST must be in D.3 only")

    # Answer-side [R] checks come in two, clearly separated kinds (orchestrator finding on the quarantined run,
    # 2026-09-26, over DEMONSTRATION_DESIGN.md section 4 G3's own "[D + R]" marking: "the deterministic part is
    # packet-side placement, and the answer-side judgement belongs to the rubric"):
    #
    # * a HEURISTIC TEXT SCAN (a phrase or marker match) can be a useful hint, but it is never "mechanically
    #   certain" -- it cannot tell a hypothetical or quoted mention from an assertion, or a citation "as a finding"
    #   from one inside a listing of mandatory inputs. Such a scan may report PASS when it finds nothing (silence
    #   on the scan is a reasonably safe negative, the same convention check_oracle.py's own PROHIBITED lint
    #   uses), but on a HIT it reports PENDING_RUBRIC, with the matched/cited text quoted for the rubric grader --
    #   never FAIL. (The original code FAILed on a phrase/marker hit; over the real run-1 answers this produced a
    #   hard G3 FAIL on a withdrawn-item citation the independent rubric grader judged a PASS, because the citation
    #   was inside a mandatory-inputs listing, not offered as a finding -- exactly the context judgement a phrase
    #   scan cannot make.)
    # * a MECHANICALLY CERTAIN check reads an exact CONSTANT field the answers schema itself defines (the
    #   side-by-side `classification`, the both-ways `disposition`) -- there is no prose judgement left once that
    #   field is read, so this kind alone may still report FAIL.
    answer_side: list = []
    text_by_query = {a.get("query_id"): (a.get("answer_text") or "") for a in (answers.get("answers") or [])}
    full_text = "\n".join(text_by_query.values())

    decision_hit = next((m for pat in _DECISION_PHRASES if (m := pat.search(full_text))), None)
    answer_side.append({"rule": "F1 direction not presented as a decision (phrase scan; heuristic)",
                         "quote": decision_hit.group(0) if decision_hit else "",
                         "verdict": PENDING_RUBRIC if decision_hit else "PASS"})

    classification_hit = next((m for pat in _CLASSIFICATION_PHRASES if (m := pat.search(full_text))), None)
    answer_side.append({"rule": "F2/F3 not presented as a classification (phrase scan; heuristic)",
                         "quote": classification_hit.group(0) if classification_hit else "",
                         "verdict": PENDING_RUBRIC if classification_hit else "PASS"})

    # Mechanically certain: the answers schema's own CONSTANT fields, read exactly, never scanned for phrasing.
    sbs = next((a for a in (answers.get("answers") or []) if a.get("classification") is not None), None)
    if sbs is not None:
        verdict = "PASS" if sbs.get("classification") == "NOT_DETERMINED_BY_BRIDGE" else "FAIL"
        answer_side.append({"rule": "side-by-side classification is the constant NOT_DETERMINED_BY_BRIDGE "
                                     "(certain)",
                             "quote": str(sbs.get("classification")), "verdict": verdict})

    bw = next((a for a in (answers.get("answers") or []) if a.get("disposition") is not None), None)
    if bw is not None:
        verdict = "PASS" if bw.get("disposition") == "NONE_STATED" else "FAIL"
        answer_side.append({"rule": "both-ways disposition is the constant NONE_STATED (certain)",
                             "quote": str(bw.get("disposition")), "verdict": verdict})

    # Heuristic: citing the withdrawn item at all is a hint worth the rubric grader's attention, marked or not --
    # whether it is offered "as a finding" is exactly the context judgement a marker scan cannot make (see above).
    withdrawn_id = next((row["item"] for row in (oracle.get("authority_expectations") or [])
                         if row.get("class") == "EVIDENCE_WITHDRAWN"), None)
    if withdrawn_id:
        quote, marker_present = _withdrawn_citation_line(withdrawn_id, full_text)
        answer_side.append({"rule": "withdrawn finding citation context (marker scan; heuristic)",
                             "quote": quote or "", "marker_present": marker_present,
                             "verdict": PENDING_RUBRIC if quote is not None else "PASS"})

    # GD-9/D-3 (BR-ARCH-RULING-2 D-3: "AUTH items are gated under G3 ... on the answers by the rubric, [which]
    # checks the answer side and quotes the text it judged"): every item the rubric names is ingested here as a
    # HARD G3 gate, generically -- this grader never hard-codes which items need answer-side authority gating
    # (OC-BR-02); it gates whatever the rubric file names, with whatever verdict the rubric grader recorded. Absent
    # a rubric (the default), nothing here changes G3's result -- matching every other [R] check's PENDING_RUBRIC
    # convention until the fresh rubric grader runs.
    for row in (rubric or {}).get("auth_gating") or []:
        verdict = row.get("verdict")
        answer_side.append({"rule": f"answer-side authority gating: {row.get('item')} (rubric)",
                             "quote": row.get("quote", ""),
                             "verdict": verdict if verdict in ("PASS", "FAIL") else PENDING_RUBRIC})

    # Aggregation: a packet-side problem or any CERTAIN answer-side FAIL is a hard G3 FAIL. Absent either, one or
    # more heuristic hits leave G3 PENDING_RUBRIC (never FAIL) until the rubric grader resolves them -- exactly the
    # verdict-logic convention every other [R]/PENDING_RUBRIC gate already uses (`grade()`'s own top-level verdict
    # already turns an all-PASS-except-PENDING_RUBRIC gate set into DEMONSTRATION_PENDING_RUBRIC, not
    # DEMONSTRATION_FAIL -- no change needed there).
    hard_fail = bool(packet_problems) or any(a["verdict"] == "FAIL" for a in answer_side)
    pending = any(a["verdict"] == PENDING_RUBRIC for a in answer_side)
    result = "FAIL" if hard_fail else (PENDING_RUBRIC if pending else "PASS")
    return {
        "result": result,
        "packet_side": packet_problems,
        "answer_side": answer_side,
        "addendum_a1_reinterpreted_rows": reinterpreted,
    }


# ---------------------------------------------------------------------------------------------------------------
# Anchor / citation matching -- shared by G4/G5/G6/G8.
# ---------------------------------------------------------------------------------------------------------------

def _normalise_lines(value):
    """GD-1: ``lines`` is accepted in every form a citation or anchor may reasonably carry, normalised to a
    ``[start, end]`` pair of ints -- never crashes on a well-formed value. Accepted forms: a two-element
    ``[start, end]`` (or ``(start, end)``) list/tuple; a one-element ``[n]`` list (a single line); a bare ``int``
    (a single line); a string ``"START-END"``; a string holding a single integer (``"12"``, a single line). Any
    other shape raises ``ValueError`` naming the offending value, rather than a bare ``unpack`` crash deep inside
    the matcher (GD-1's own defect: ``lines: "START-END"`` crashed ``anchor_matches`` with
    ``ValueError: too many values to unpack``, because a 2+ character string was unpacked as if it were a
    2-element sequence)."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        if len(value) == 1:
            return [int(value[0]), int(value[0])]
        if len(value) == 2:
            return [int(value[0]), int(value[1])]
        raise ValueError(f"lines: unrecognised sequence length {len(value)!r} in {value!r}")
    if isinstance(value, bool):
        raise ValueError(f"lines: unrecognised value {value!r}")
    if isinstance(value, int):
        return [value, value]
    if isinstance(value, str):
        s = value.strip()
        if "-" in s:
            a, b = s.split("-", 1)
            return [int(a.strip()), int(b.strip())]
        return [int(s), int(s)]
    raise ValueError(f"lines: unrecognised form {value!r}")


def _resolve_citation(citation, items_by_id: dict) -> Optional[dict]:
    if isinstance(citation, str):
        row = items_by_id.get(citation)
        if row is None:
            return None
        u = row["unit"]
        src = row.get("source") or {}
        lines = [src["line_start"], src["line_end"]] if src.get("line_start") is not None else None
        return {"path": src.get("path"), "commit": src.get("commit"), "lines": lines,
                "record_id": u.get("id") if u.get("kind") == "record" else None}
    if isinstance(citation, dict):
        if "exact" in citation:
            e = citation["exact"] or {}
            return {"path": e.get("path"), "commit": e.get("commit"), "lines": _normalise_lines(e.get("lines")),
                     "record_id": e.get("record_id"), "symbol": e.get("symbol")}
        if "path" in citation or "commit" in citation or "record_id" in citation:
            return {"path": citation.get("path"), "commit": citation.get("commit"),
                     "lines": _normalise_lines(citation.get("lines")), "record_id": citation.get("record_id"),
                     "symbol": citation.get("symbol")}
    return None


def _enclosing_symbol(path: Optional[str], commit: Optional[str], line: Optional[int],
                       repo: Optional[str]) -> Optional[str]:
    """GD-10: resolves the symbol (function/type) enclosing ``line`` in ``path`` at ``commit``, through the SAME
    code store the code route already builds (``govbridge.code.symbols``/``govbridge.code.store``) -- never a
    second, independent symbol table, and never a Review-8/Phase-2-specific one (OC-BR-02: this looks up whatever
    path/commit/line it is given, generically). Read-only from this module's point of view: it only ever looks up
    an already-parseable blob (lazily indexing it on first use, exactly like any other code-route query) and never
    writes anything this grader owns. Returns ``None`` (never raises) whenever the lookup cannot be completed --
    no repo, an unindexable path, a store error, no enclosing definition -- so a citation simply falls through to
    the ordinary line-range check below instead of crashing the grade."""
    if not (path and commit and line and repo):
        return None
    try:
        from govbridge.core import store as corestore, gitobj
        from govbridge.code import store as codestore, symbols as codesymbols
        blob_id = gitobj.blob_at(commit, path, repo=repo)
        if not blob_id:
            return None
        conn = corestore.open_db()
        codestore.ensure_schema(conn)
        codesymbols.ensure_indexed(conn, commit, repo=repo)
        rows = codestore.symbols_for_blobs(conn, [blob_id])
        candidates = [r for r in rows if r["start_line"] <= line <= r["end_line"]]
        if not candidates:
            return None
        best = min(candidates, key=lambda r: r["end_line"] - r["start_line"])
        return best["qualified_name"] or best["name"]
    except Exception:
        return None


def anchor_matches(citation, anchor: dict, items_by_id: dict, line_tolerance: int = 3, repo: Optional[str] = None) -> bool:
    """ARCHITECTURE.md's own matching rule, quoted in DEMONSTRATION_DESIGN.md section 4 G4: same path at the
    same commit (or a commit where the file's blob is identical) and a line within ``line_tolerance`` or the same
    symbol; a record anchor matches by record id or section.

    D-1/GD-3/GD-8 (BR-ARCH-RULING-2 D-1, "a record anchor matches by record id or section"): a citation carrying
    the SAME record id as the anchor matches -- a whole-document citation therefore matches a sectioned anchor of
    that record, whichever section the anchor targets. A citation that resolves to a DIFFERENT record's id never
    matches, even if a path/commit/line coincidence would otherwise suggest one (checked first, so it vetoes the
    section fallback below). When the record id does not settle it -- one side (or both) simply has none, most
    often because the anchor identifies a SECTION of a record by path/commit/line-range rather than by an id
    string -- the SAME path + blob-identical-commit + line-overlap rule already used for a code anchor decides it
    ("or section"). Previously, ANY anchor carrying a record_id short-circuited straight to an id-equality
    check and never fell through to this section rule, so a citation that named the record's path/lines correctly
    but not its id-string form could never match ("a record anchor matched by record id only", GD-3)."""
    resolved = _resolve_citation(citation, items_by_id)
    if resolved is None:
        return False

    anchor_record_id, resolved_record_id = anchor.get("record_id"), resolved.get("record_id")
    if anchor_record_id and resolved_record_id:
        return resolved_record_id == anchor_record_id

    a_path, a_commit, a_lines = anchor.get("path"), anchor.get("commit"), _normalise_lines(anchor.get("lines"))
    c_path, c_commit, c_lines = resolved.get("path"), resolved.get("commit"), resolved.get("lines")
    if not (a_path and c_path and a_path == c_path):
        return False
    commit_ok = a_commit == c_commit
    if not commit_ok and repo and a_commit and c_commit:
        try:
            from govbridge.core import gitobj
            b1, b2 = gitobj.blob_at(a_commit, a_path, repo=repo), gitobj.blob_at(c_commit, c_path, repo=repo)
            commit_ok = bool(b1) and b1 == b2
        except Exception:
            commit_ok = False
    if not commit_ok:
        return False
    if anchor.get("symbol"):
        # GD-10: a symbol-qualified anchor is matched not only by a citation that itself names the symbol, but by
        # ANY citation whose cited line resolves, through the code store at the cited commit, to that SAME
        # enclosing symbol -- so a plain line citation inside a function's body matches that function's anchor
        # even when its lines fall outside `line_tolerance` of whatever line the anchor happened to record.
        if resolved.get("symbol") and resolved["symbol"] == anchor["symbol"]:
            return True
        if c_lines and _enclosing_symbol(c_path, c_commit, c_lines[0], repo) == anchor["symbol"]:
            return True
        if not a_lines:
            # A symbol-qualified anchor with no line range of its own is scoped to that symbol specifically --
            # unlike a genuinely line-less record/contract/evidence anchor (below), it must NOT match every other
            # line in the same file just because path+commit agree.
            return False
    if not a_lines:
        return True  # a line-less (record/contract/evidence) anchor: path + (blob-identical) commit is enough
    if not c_lines:
        return False
    lo, hi = a_lines
    clo, chi = c_lines
    return clo <= hi + line_tolerance and chi >= lo - line_tolerance


def _citations_for_stage(stage_answer: dict) -> list:
    return stage_answer.get("citations") or []


# ---------------------------------------------------------------------------------------------------------------
# must_state format (follow-up, orchestrator, 2026-09-26; BR-ARCH-RULING-2 D-2): the run-2 oracle writes each
# must_state entry as ``{fact, binding}`` (``binding`` a chain-stage name, or the literal ``"query"``) as well as
# the run-1 plain string form (implicit binding: the stage listing it). This grader was told the exact grammar in
# plain English by the orchestrator's own dispatch message; per REPAIR-1 rule 1 it did NOT read
# ``DEMONSTRATION/oracle-tools/check_oracle.py`` (a ``DEMONSTRATION/oracle*`` path) to confirm it, since the
# dispatch message's description was itself sufficient to implement this from.
# ---------------------------------------------------------------------------------------------------------------

def _must_state_entries(raw_list) -> list:
    """Normalises a must_state list to ``[{"fact": str, "binding": Optional[str]}, ...]``. A plain string (the
    run-1 form) becomes ``binding: None`` -- "bound to the stage listing it", preserving run-1's own implicit
    behaviour exactly."""
    out = []
    for e in raw_list or []:
        if isinstance(e, str):
            out.append({"fact": e, "binding": None})
        elif isinstance(e, dict):
            out.append({"fact": e.get("fact"), "binding": e.get("binding")})
    return out


def _must_state_scope_text(binding: Optional[str], own_stage_name: str, stage_claims_by_name: dict,
                            query_full_text: str) -> str:
    """Resolves the text a must_state fact is judged against, per D-2: ``binding == "query"`` -> the query's WHOLE
    answer; ``binding`` naming a stage -> that stage's own claim (even one OTHER than the stage physically listing
    the fact, if the oracle ever rebinds one); missing/``None``, or the containing stage's own name -> the
    containing stage's claim (the run-1 plain-string form's own implicit behaviour)."""
    if binding == "query":
        return query_full_text
    if binding and binding in stage_claims_by_name:
        return stage_claims_by_name[binding]
    return stage_claims_by_name.get(own_stage_name, "")


def _must_state_present(fact: Optional[str], scope_text: str) -> bool:
    """A generic, HEURISTIC (never mechanically certain) case-insensitive substring check -- a real, auditable
    partial signal, exposed as data for the rubric grader. must_state facts are [R] (DEMONSTRATION_DESIGN.md
    section 4 G4: "[R] Each must_state fact is present in the stage's claim"); this never by itself turns a stage
    REACHED/MISSING or a gate PASS/FAIL -- ``must_state_ok`` stays PENDING_RUBRIC here, exactly like every other
    heuristic text scan in this module (the G3 follow-up's own discipline)."""
    if not fact:
        return False
    return fact.strip().lower() in (scope_text or "").lower()


# ---------------------------------------------------------------------------------------------------------------
# G4: chain reconstruction.
# ---------------------------------------------------------------------------------------------------------------

def _grade_chain(oracle_chain: dict, answer: dict, items_by_id: dict, line_tolerance: int, repo) -> dict:
    stage_by_name = {s["stage"]: s for s in oracle_chain["stages"]}
    ans_stage_by_name = {s.get("stage"): s for s in (answer.get("stages") or [])}
    # D-2 must_state scoping (see the module-level helpers above): the "stage claim" scope for a stage binding,
    # and the "whole answer" scope for a `query` binding -- every stage's claim, plus the query's own answer_text
    # if it carries one, concatenated. Computed ONCE per chain since a `query`-bound fact's scope never depends on
    # which stage lists it.
    stage_claims_by_name = {nm: (s.get("claim") or "") for nm, s in ans_stage_by_name.items()}
    query_full_text = "\n".join(filter(None, [answer.get("answer_text") or ""] + list(stage_claims_by_name.values())))
    stage_grades = []
    chain_ok = True
    for stage_def in oracle_chain["stages"]:
        name = stage_def["stage"]
        ans_stage = ans_stage_by_name.get(name)
        citations = _citations_for_stage(ans_stage) if ans_stage else []
        any_of = (stage_def["anchors"].get("any_of"))
        all_of = (stage_def["anchors"].get("all_of"))
        wrong_anchors = stage_def.get("wrong") or []
        trap_anchors = stage_def.get("traps") or []

        is_wrong = any(anchor_matches(c, w, items_by_id, line_tolerance, repo) for c in citations for w in wrong_anchors)
        matched_any = any_of and any(
            anchor_matches(c, a, items_by_id, line_tolerance, repo) for c in citations for a in any_of)
        matched_all = all_of and all(
            any(anchor_matches(c, a, items_by_id, line_tolerance, repo) for c in citations) for a in all_of)
        matched_real = bool(matched_any or matched_all)
        matched_trap_only = (not matched_real) and citations and all(
            any(anchor_matches(c, t, items_by_id, line_tolerance, repo) for t in trap_anchors) for c in citations)

        if is_wrong:
            grade = "WRONG"
        elif stage_def.get("is_enforcement_point") and matched_trap_only:
            grade = "UPSTREAM_ONLY"
        elif matched_real:
            grade = "REACHED"
        elif not citations:
            grade = "MISSING" if stage_def.get("required") else "MISSING"
        else:
            grade = "MISSING"
        must_state_results = []
        for entry in _must_state_entries(stage_def.get("must_state")):
            scope_text = _must_state_scope_text(entry["binding"], name, stage_claims_by_name, query_full_text)
            must_state_results.append({
                "fact": entry["fact"], "binding": entry["binding"] or name,
                "present": _must_state_present(entry["fact"], scope_text), "must_state_ok": PENDING_RUBRIC,
            })
        stage_grades.append({"stage": name, "grade": grade, "required": stage_def.get("required", False),
                              "is_enforcement_point": stage_def.get("is_enforcement_point", False),
                              "must_state": must_state_results})
        if stage_def.get("required") and grade not in ("REACHED",):
            chain_ok = False
        if stage_def.get("is_enforcement_point") and grade != "REACHED":
            # UPSTREAM_ONLY enforcement fails the WHOLE chain regardless of every other stage (launcher's rule).
            chain_ok = False
    result = "PASS" if chain_ok else "FAIL"
    # GD-5: the enforcement stage's OWN grade, tracked independently of the chain's overall result -- a chain can
    # fail (a required, non-enforcement stage MISSING or WRONG) while its enforcement point was still REACHED.
    # `grade_g4`'s side-by-side check needs exactly this narrower fact (DEMONSTRATION_DESIGN.md section 4: "passes
    # when both enforcement points are reached"), not "both whole chains passed".
    enforcement_reached = any(
        s["is_enforcement_point"] and s["grade"] == "REACHED" for s in stage_grades
    ) if any(s["is_enforcement_point"] for s in stage_grades) else False
    return {"query_id": answer.get("query_id"), "result": result, "stages": stage_grades,
            "enforcement_reached": enforcement_reached}


def grade_g4(oracle: dict, answers: dict, items_by_id: dict, line_tolerance: int, repo=None) -> dict:
    answers_by_id = {a.get("query_id"): a for a in (answers.get("answers") or [])}
    chains_out = []
    for oc in oracle.get("chains") or []:
        qid = oc["query_id"]
        ans = answers_by_id.get(qid) or {"query_id": qid, "stages": []}
        chains_out.append(_grade_chain(oc, ans, items_by_id, line_tolerance, repo))
    sbs_oracle = oracle.get("side_by_side") or {}
    sbs_answer = next((a for a in (answers.get("answers") or []) if a.get("shared_points") is not None
                        or a.get("differing_points") is not None), {})
    shared_req = sbs_oracle.get("shared_points") or []
    differing_req = sbs_oracle.get("differing_points") or []
    shared_recall = _recall(sbs_answer.get("shared_points") or [], shared_req, items_by_id, line_tolerance, repo)
    differing_recall = _recall(sbs_answer.get("differing_points") or [], differing_req, items_by_id, line_tolerance, repo)
    # GD-5: side-by-side requires both ENFORCEMENT POINTS reached, not both whole chains PASS
    # (DEMONSTRATION_DESIGN.md section 4 G4: "passes when both enforcement points are reached, the shared and
    # differing code locations match ... at recall >= 0.8"). The old `all(c["result"] == "PASS" ...)` condition
    # additionally demanded every OTHER required stage of both chains also reach REACHED, so a chain that failed
    # on an unrelated stage silently failed the side-by-side too, even though its enforcement point (and every
    # side-by-side recall figure) was fine.
    both_enforcement_reached = bool(chains_out) and all(c["enforcement_reached"] for c in chains_out)
    side_by_side = {
        "result": "PASS" if (both_enforcement_reached and shared_recall >= 0.8 and differing_recall >= 0.8) else "FAIL",
        "shared_recall": shared_recall, "differing_recall": differing_recall,
    }
    overall = "PASS" if (all(c["result"] == "PASS" for c in chains_out) and side_by_side["result"] == "PASS") else "FAIL"
    return {"result": overall, "chains": chains_out, "side_by_side": side_by_side}


def _recall(citations: list, required: list, items_by_id: dict, line_tolerance: int, repo) -> float:
    if not required:
        return 1.0
    hit = 0
    for req in required:
        if any(anchor_matches(c, req if isinstance(req, dict) else {"record_id": req}, items_by_id, line_tolerance, repo)
               for c in citations):
            hit += 1
    return hit / len(required)


# ---------------------------------------------------------------------------------------------------------------
# G5 / G8: query classes / controls.
# ---------------------------------------------------------------------------------------------------------------

def _grade_one_query(oracle_row: dict, answer: dict, items_by_id: dict, line_tolerance: int, repo,
                      rubric: Optional[dict] = None) -> dict:
    citations = list(answer.get("citations") or [])
    required = oracle_row.get("required") or []
    forbidden = oracle_row.get("forbidden") or []
    recall = _recall(citations, required, items_by_id, line_tolerance, repo)
    forbidden_hits = [f for f in forbidden if any(
        anchor_matches(c, f if isinstance(f, dict) else {"record_id": f}, items_by_id, line_tolerance, repo)
        for c in citations)]
    # GD-9/D-3: ingest the rubric's [R] `must_state` verdict for THIS query, when one was supplied, instead of
    # always reporting PENDING_RUBRIC and never letting it affect the result -- "[R] results not ingested per
    # query" was GD-9's own defect. Absent a rubric (the default), behaviour is unchanged: PENDING_RUBRIC, and it
    # never blocks `ok` (a genuinely pending item is not yet known to have failed).
    qid = oracle_row.get("query_id")
    must_state_row = (rubric or {}).get("must_state", {}).get(qid) if rubric else None
    must_state_ok = bool(must_state_row.get("ok")) if must_state_row is not None else PENDING_RUBRIC
    ok = recall >= 0.8 and not forbidden_hits and must_state_ok is not False
    return {"query_id": qid, "recall": recall, "forbidden_hits": len(forbidden_hits),
            "must_state_ok": must_state_ok, "result": "PASS" if ok else "FAIL"}


def grade_g5(oracle: dict, answers: dict, queries_meta: dict, items_by_id: dict, line_tolerance: int, repo=None,
             rubric: Optional[dict] = None) -> dict:
    answers_by_id = {a.get("query_id"): a for a in (answers.get("answers") or [])}
    per_query = []
    for row in oracle.get("queries") or []:
        qid = row.get("query_id")
        meta = queries_meta.get(qid) or {}
        if meta.get("kind") not in ("query_class",):
            continue
        ans = answers_by_id.get(qid) or {"query_id": qid}
        per_query.append({**_grade_one_query(row, ans, items_by_id, line_tolerance, repo, rubric=rubric),
                           "class": meta.get("class"), "subject": meta.get("subject")})
    per_class: dict = {}
    for row in per_query:
        c = row.get("class")
        if not c:
            continue
        per_class.setdefault(c, []).append(row["result"] == "PASS")
    class_verdict = {}
    for c, results in per_class.items():
        passed = sum(1 for r in results if r)
        if c == "QC9":
            class_verdict[c] = "PASS" if passed == len(results) else "FAIL"
        else:
            class_verdict[c] = "PASS" if passed >= 2 else "FAIL"
    # "the overall threshold is 10/10 classes" (DEMONSTRATION_DESIGN.md section 4 G5) is a property of the REAL
    # Review-8 oracle's ten defined query classes (QC1-QC10), not a number this generic grader may hard-code
    # (OC-BR-02); the generic rule it implements is "every class the oracle actually defines must pass" -- which
    # equals 10/10 whenever the oracle covers all ten, and scales to whatever a differently-shaped oracle covers.
    overall = "PASS" if per_class and all(v == "PASS" for v in class_verdict.values()) else "FAIL"
    return {"result": overall, "per_query": per_query, "per_class": class_verdict}


def grade_g8(oracle: dict, answers: dict, queries_meta: dict, items_by_id: dict, line_tolerance: int, repo=None,
             rubric: Optional[dict] = None) -> dict:
    answers_by_id = {a.get("query_id"): a for a in (answers.get("answers") or [])}
    per_query = []
    for row in oracle.get("controls") or []:
        qid = row.get("query_id")
        ans = answers_by_id.get(qid) or {"query_id": qid}
        per_query.append(_grade_one_query(row, ans, items_by_id, line_tolerance, repo, rubric=rubric))
    result = "PASS" if per_query and all(r["result"] == "PASS" for r in per_query) else ("FAIL" if per_query else PENDING_RUBRIC)
    return {"result": result, "per_query": per_query}


# ---------------------------------------------------------------------------------------------------------------
# G6: F1 evidence both ways.
# ---------------------------------------------------------------------------------------------------------------

def grade_g6(oracle: dict, answers: dict, items_by_id: dict, line_tolerance: int, repo=None) -> dict:
    bw_oracle = oracle.get("f1_both_ways") or {}
    # GD-2: select the both-ways answer by the oracle's OWN `query_id`, never "whichever answer happens to be
    # first with an evidence_for/evidence_against/disposition field" -- the run's answer set can carry several
    # such shaped answers (e.g. a side-by-side or a chain answer that also states a disposition), and grading the
    # wrong one silently graded the wrong query ("G6 grades the first answer with evidence_for").
    bw_qid = bw_oracle.get("query_id")
    bw_answer = next((a for a in (answers.get("answers") or []) if a.get("query_id") == bw_qid), {})
    all_citations = []
    for block in ("evidence_for", "evidence_against"):
        for row in bw_answer.get(block) or []:
            all_citations.extend(row.get("citations") or [])
    all_citations.extend(bw_answer.get("citations") or [])
    purpose_hit = any(
        anchor_matches(c, a, items_by_id, line_tolerance, repo)
        for c in all_citations for a in (bw_oracle.get("purpose_anchors") or []))
    consumer_anchors = bw_oracle.get("consumer_anchors") or []
    consumer_recall = _recall(all_citations, consumer_anchors, items_by_id, line_tolerance, repo)
    disposition_stated = bw_answer.get("disposition") not in (None, "NONE_STATED")
    result = "PASS" if (purpose_hit and consumer_recall >= 1.0 and not disposition_stated) else "FAIL"
    return {"result": result, "purpose_hit": purpose_hit, "consumer_recall": consumer_recall,
            "decision_stated": disposition_stated}


# ---------------------------------------------------------------------------------------------------------------
# G7: no whole-repository dumping.
# ---------------------------------------------------------------------------------------------------------------

SWEEP_PATTERNS = [
    re.compile(r"\bgrep\s+-r\b"), re.compile(r"\brg\s+(?!--)[^|]*(?<!\S)\.(?!\S)"),
    re.compile(r"\bfind\s+\.\s"), re.compile(r"\bls\s+-R\b"),
    re.compile(r"\bgit\s+ls-tree\s+-r\b(?!.*--)"), re.compile(r"\bgit\s+grep\b(?!.*--\s)"),
]

# D-4 (BR-ARCH-RULING-2): a read under the run's OWN directory is not a corpus read -- it is the task's own input
# or the orchestrator's protocol material. Generic: matches any `run-<n>/` path segment, never one particular run.
_RUN_DIR_RE = re.compile(r"(^|/)run-\d+(/|$)")


def _window_bytes(raw: bytes, lines) -> int:
    """GD-7/D-5: the byte count of a DECLARED window (a 1-indexed, inclusive ``[start, end]`` line range) within
    ``raw``, not the whole blob's size."""
    parts = raw.split(b"\n")
    lo = max((lines[0] or 1) - 1, 0)
    hi = min(lines[1] or len(parts), len(parts))
    return sum(len(p) + 1 for p in parts[lo:hi])


def _supplied_paths(packets: list, receipt: dict) -> set:
    """GD-6/D-4: paths already SUPPLIED to the agent -- through a compiled packet (any section, main or
    supplementary), through the task spec's own declared inputs, or as the receipt's own declared
    ``outputs_produced``/``inputs_consumed`` -- so re-reading one from disk is not a NEW, undeclared acquisition
    (REPAIR_PLAN.md section 8.2 GD-6: "exclude supplied inputs, the agent's own outputs and scratch")."""
    supplied: set = set()
    for p in packets:
        manifest = p.get("manifest") or {}
        for letter, sec in (manifest.get("sections") or {}).items():
            rows = []
            if letter == "D":
                for sub in (sec.get("subblocks") or {}).values():
                    rows.extend(sub.get("items") or [])
            else:
                rows.extend(sec.get("items") or [])
            for row in rows:
                path = (row.get("source") or {}).get("path")
                if path:
                    supplied.add(path)
        for inp in (p.get("task_spec") or {}).get("required_inputs") or []:
            if isinstance(inp, dict) and inp.get("path"):
                supplied.add(inp["path"])
    for key in ("outputs_produced", "inputs_consumed"):
        for entry in receipt.get(key) or []:
            if isinstance(entry, dict) and entry.get("path"):
                supplied.add(entry["path"])
    return supplied


def grade_g7(packets: list, receipt: dict, corpus_bytes: Optional[int], budget_bytes: Optional[int],
             reads: Optional[dict], repo: Optional[str] = None) -> dict:
    packet_bytes = sum(len((p.get("rendered") or "").encode("utf-8")) if p.get("rendered") is not None
                        else Path(p["dir"], "packet.md").stat().st_size for p in packets)
    ext = receipt.get("external_reads") or []
    external_read_files = len({e.get("path") for e in ext})
    external_read_bytes = 0
    for e in ext:
        path, commit = e.get("path"), e.get("commit")
        if path and commit and repo:
            try:
                from govbridge.core import gitobj
                blob = gitobj.blob_at(commit, path, repo=repo)
                raw = gitobj.read_blob(blob, repo=repo) if blob else None
                if raw is None:
                    continue
                # GD-7/D-5: "count declared windows, or only direct reads" -- an external_reads entry that
                # declares a line range (however the receipt spells it: `lines`, or `line_start`/`line_end`) is a
                # WINDOWED read; only that window's bytes are charged, never the whole blob it came from ("external
                # bytes counted as whole blobs when the content came through govbridge", GD-7's own defect). A
                # receipt entry with no window at all is a genuine direct/whole-file read, counted in full.
                window = None
                if e.get("lines") is not None:
                    window = _normalise_lines(e.get("lines"))
                elif e.get("line_start") is not None:
                    window = _normalise_lines([e.get("line_start"), e.get("line_end")])
                external_read_bytes += _window_bytes(raw, window) if window else len(raw)
            except Exception:
                pass

    undeclared = []
    sweep_commands = []
    if reads:
        declared = {(e.get("path"), e.get("commit")) for e in ext}
        supplied = _supplied_paths(packets, receipt)
        for r in reads.get("reads") or []:
            path = r.get("path")
            if not path:
                continue
            key = (path, r.get("commit"))
            if key in declared or any(k[0] == path for k in declared):
                continue
            if path in supplied or _RUN_DIR_RE.search(path):
                continue
            undeclared.append(r)
        sweep_commands = reads.get("sweep_commands") or []

    problems = []
    # OBS-BR-05: this check must always run when `corpus_bytes` is known -- the ORIGINAL code additionally
    # required a truthy `budget_bytes`, which `grade()` always passed as `None`, so "packet bytes <= 1% of corpus"
    # was silently never enforced. `budget_bytes`, when a caller DOES supply it (the sum of the budget profiles
    # actually used), is now a genuinely separate, additional check, per DEMONSTRATION_DESIGN.md section 4 G7:
    # "exceed 1% of corpus, OR the sum of the budget profiles used".
    if corpus_bytes and packet_bytes > 0.01 * corpus_bytes:
        problems.append(f"packet_bytes {packet_bytes} exceeds 1% of corpus ({corpus_bytes}) (OBS-BR-05)")
    if budget_bytes and packet_bytes > budget_bytes:
        problems.append(f"packet_bytes {packet_bytes} exceeds the sum of budget profiles used ({budget_bytes})")
    if external_read_files > 25:
        problems.append(f"external_read_files {external_read_files} exceeds 25")
    if corpus_bytes and external_read_bytes > 0.005 * corpus_bytes:
        problems.append(f"external_read_bytes {external_read_bytes} exceeds 0.5% of corpus ({corpus_bytes})")
    if undeclared:
        problems.append(f"{len(undeclared)} undeclared read(s) found in the transcript extraction")
    if sweep_commands:
        problems.append(f"{len(sweep_commands)} whole-tree sweep command(s) found in the transcript")

    context_efficiency = ((packet_bytes + external_read_bytes) / corpus_bytes) if corpus_bytes else None
    return {
        "result": "FAIL" if problems else "PASS",
        "corpus_bytes": corpus_bytes, "packet_bytes": packet_bytes,
        "external_read_files": external_read_files, "external_read_bytes": external_read_bytes,
        "undeclared_reads": undeclared, "sweep_commands": sweep_commands,
        "context_efficiency": context_efficiency, "problems": problems,
    }


# ---------------------------------------------------------------------------------------------------------------
# Top level
# ---------------------------------------------------------------------------------------------------------------

def grade(oracle_path: str, answers_path: str, receipt_path: Optional[str], packet_dirs: list,
          queries_path: Optional[str] = None, reads_path: Optional[str] = None,
          corpus_bytes: Optional[int] = None, repo: Optional[str] = None, budget_bytes: Optional[int] = None,
          rubric_path: Optional[str] = None) -> dict:
    from govbridge import GOV_BRIDGE_DOMAIN
    import os

    oracle = load_yaml_file(oracle_path)
    answers = load_yaml_file(answers_path)
    receipt = load_yaml_file(receipt_path) if receipt_path else {}
    packets = [_load_packet_dir(p) for p in packet_dirs]
    queries_path = queries_path or os.path.join(GOV_BRIDGE_DOMAIN, "ARCHITECTURE", "demonstration-queries.yaml")
    queries_doc = load_yaml_file(queries_path)
    queries_meta = {q["id"]: q for q in queries_doc.get("queries") or []}
    line_tolerance = int(oracle.get("line_tolerance") or 3)
    reads = _load_json(reads_path) if reads_path and Path(reads_path).exists() else None
    # GD-9/D-3: the fresh-opus rubric grader's [R] results (must_state per query, and any answer-side authority
    # gating such as AUTH items), ingested here so they change G3/G5/G8's actual result instead of only ever
    # reporting PENDING_RUBRIC ("[R] results not ingested per query", GD-9's own defect). Optional and generic:
    # absent (the default), nothing here changes -- this grader still computes every [D] check on its own.
    rubric = load_yaml_file(rubric_path) if rubric_path else None

    main_packet = packets[0] if packets else {"manifest": {"sections": {}, "notices": []}, "task_spec": {}, "meta": {}}
    items_by_id = _manifest_items_by_id(main_packet["manifest"]) if packets else {}

    g1 = grade_g1(packets, repo=repo) if packets else {"result": PENDING_RUBRIC, "packets": []}
    g2 = grade_g2(packets, receipt, repo=repo) if packets else {"result": PENDING_RUBRIC, "reasons": []}
    g3 = grade_g3(oracle, answers, main_packet, rubric=rubric) if packets else {"result": PENDING_RUBRIC}
    g4 = grade_g4(oracle, answers, items_by_id, line_tolerance, repo)
    g5 = grade_g5(oracle, answers, queries_meta, items_by_id, line_tolerance, repo, rubric=rubric)
    g6 = grade_g6(oracle, answers, items_by_id, line_tolerance, repo)
    g7 = grade_g7(packets, receipt, corpus_bytes, budget_bytes, reads, repo=repo) if packets else \
        {"result": PENDING_RUBRIC, "problems": []}
    g8 = grade_g8(oracle, answers, queries_meta, items_by_id, line_tolerance, repo, rubric=rubric)

    gates = {"G1_packet_validity": g1, "G2_receipt": g2, "G3_authority_classes": g3, "G4_chains": g4,
             "G5_query_classes": g5, "G6_f1_both_ways": g6, "G7_no_dumping": g7, "G8_controls": g8}
    hard_fail = any(g.get("result") == "FAIL" for g in gates.values())
    verdict = "DEMONSTRATION_FAIL" if hard_fail else (
        "DEMONSTRATION_PASS" if all(g.get("result") == "PASS" for g in gates.values()) else "DEMONSTRATION_PENDING_RUBRIC")

    return {
        "run_id": answers.get("run_id"),
        "oracle": {"path": oracle_path, "oracle_id": oracle.get("oracle_id")},
        "deterministic_grader": {"command": "govbridge demo grade"},
        "gates": gates,
        "verdict": verdict,
        "note": "builder-level evidence toward P2_CONTEXT_RETRIEVAL_BRIDGE_BUILT; never the acceptance token. "
                "PENDING_RUBRIC items require the separate fresh-opus rubric grader (node GRADE).",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.demo.grade")
    p.add_argument("--oracle", required=True)
    p.add_argument("--answers", required=True)
    p.add_argument("--receipt")
    p.add_argument("--packet", action="append", default=[], help="a directory written by `govbridge compile --out "
                                                                    "DIR`; repeatable (main packet first, then "
                                                                    "supplementary packets)")
    p.add_argument("--queries")
    p.add_argument("--reads")
    p.add_argument("--corpus-bytes", type=int)
    p.add_argument("--budget-bytes", type=int, help="the sum of the budget profiles used (DEMONSTRATION_DESIGN.md "
                                                       "section 4 G7's second, alternative bound; optional)")
    p.add_argument("--rubric", help="the fresh rubric grader's [R] results (govbridge-rubric-results/1: must_state "
                                     "per query, and any answer-side authority gating), ingested into G3/G5/G8 "
                                     "(D-3/GD-9); optional")
    p.add_argument("--repo")
    args = p.parse_args(argv)

    result = grade(args.oracle, args.answers, args.receipt, args.packet, queries_path=args.queries,
                    reads_path=args.reads, corpus_bytes=args.corpus_bytes, repo=args.repo,
                    budget_bytes=args.budget_bytes, rubric_path=args.rubric)
    print(json.dumps(result, indent=1, sort_keys=True, default=str))
    return 0 if result["verdict"] == "DEMONSTRATION_PASS" else (
        1 if result["verdict"] == "DEMONSTRATION_FAIL" else 3)


if __name__ == "__main__":
    import sys
    sys.exit(main())
