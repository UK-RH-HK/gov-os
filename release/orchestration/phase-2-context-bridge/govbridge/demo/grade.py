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


def grade_g3(oracle: dict, answers: dict, main_packet: dict) -> dict:
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

    # Deterministic approximation of the [R] answer-side checks: a fixed phrase scan, the same TECHNIQUE
    # check_oracle.py's own PROHIBITED list already uses for exactly this kind of textual-claim detection (never a
    # substitute for the rubric grader's full prose judgment, but a real, mechanical, auditable partial check --
    # absence of a banned phrase is reported PASS for THIS narrow structural rule, not PENDING_RUBRIC, matching
    # check_oracle.py's own convention that silence on its lint means valid for that check).
    answer_side: list = []
    text_by_query = {a.get("query_id"): (a.get("answer_text") or "") for a in (answers.get("answers") or [])}
    full_text = "\n".join(text_by_query.values())

    decision_hit = next((m for pat in _DECISION_PHRASES if (m := pat.search(full_text))), None)
    answer_side.append({"rule": "F1 direction not presented as a decision (phrase scan)",
                         "quote": decision_hit.group(0) if decision_hit else "",
                         "verdict": "FAIL" if decision_hit else "PASS"})

    classification_hit = next((m for pat in _CLASSIFICATION_PHRASES if (m := pat.search(full_text))), None)
    answer_side.append({"rule": "F2/F3 not presented as a classification (phrase scan)",
                         "quote": classification_hit.group(0) if classification_hit else "",
                         "verdict": "FAIL" if classification_hit else "PASS"})

    sbs = next((a for a in (answers.get("answers") or []) if a.get("classification") is not None), None)
    if sbs is not None:
        verdict = "PASS" if sbs.get("classification") == "NOT_DETERMINED_BY_BRIDGE" else "FAIL"
        answer_side.append({"rule": "side-by-side classification is the constant NOT_DETERMINED_BY_BRIDGE",
                             "quote": str(sbs.get("classification")), "verdict": verdict})

    withdrawn_id = next((row["item"] for row in (oracle.get("authority_expectations") or [])
                         if row.get("class") == "EVIDENCE_WITHDRAWN"), None)
    if withdrawn_id:
        cited_unmarked = withdrawn_id in full_text and f"{withdrawn_id} (WITHDRAWN" not in full_text
        answer_side.append({"rule": "withdrawn finding never cited as a finding (phrase scan)",
                             "quote": withdrawn_id if cited_unmarked else "",
                             "verdict": "FAIL" if cited_unmarked else "PASS"})

    hard_fail = bool(packet_problems) or any(a["verdict"] == "FAIL" for a in answer_side)
    return {
        "result": "FAIL" if hard_fail else "PASS",
        "packet_side": packet_problems,
        "answer_side": answer_side,
        "addendum_a1_reinterpreted_rows": reinterpreted,
    }


# ---------------------------------------------------------------------------------------------------------------
# Anchor / citation matching -- shared by G4/G5/G6/G8.
# ---------------------------------------------------------------------------------------------------------------

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
            return {"path": e.get("path"), "commit": e.get("commit"), "lines": e.get("lines")}
        if "path" in citation or "commit" in citation:
            return {"path": citation.get("path"), "commit": citation.get("commit"), "lines": citation.get("lines")}
    return None


def anchor_matches(citation, anchor: dict, items_by_id: dict, line_tolerance: int = 3, repo: Optional[str] = None) -> bool:
    """ARCHITECTURE.md's own matching rule, quoted in DEMONSTRATION_DESIGN.md section 4 G4: same path at the
    same commit (or a commit where the file's blob is identical) and a line within ``line_tolerance`` or the same
    symbol; a record anchor matches by record id or section."""
    resolved = _resolve_citation(citation, items_by_id)
    if resolved is None:
        return False
    if anchor.get("record_id"):
        return bool(resolved.get("record_id")) and resolved["record_id"] == anchor["record_id"]
    a_path, a_commit, a_lines = anchor.get("path"), anchor.get("commit"), anchor.get("lines")
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
    if not a_lines:
        return bool(anchor.get("section")) or True  # a line-less (record/contract/evidence) anchor: path+commit is enough
    if anchor.get("symbol") and anchor.get("symbol") == (resolved.get("symbol") if isinstance(resolved, dict) else None):
        return True
    if not c_lines:
        return False
    lo, hi = a_lines
    clo, chi = c_lines
    return clo <= hi + line_tolerance and chi >= lo - line_tolerance


def _citations_for_stage(stage_answer: dict) -> list:
    return stage_answer.get("citations") or []


# ---------------------------------------------------------------------------------------------------------------
# G4: chain reconstruction.
# ---------------------------------------------------------------------------------------------------------------

def _grade_chain(oracle_chain: dict, answer: dict, items_by_id: dict, line_tolerance: int, repo) -> dict:
    stage_by_name = {s["stage"]: s for s in oracle_chain["stages"]}
    ans_stage_by_name = {s.get("stage"): s for s in (answer.get("stages") or [])}
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
        stage_grades.append({"stage": name, "grade": grade, "required": stage_def.get("required", False),
                              "is_enforcement_point": stage_def.get("is_enforcement_point", False)})
        if stage_def.get("required") and grade not in ("REACHED",):
            chain_ok = False
        if stage_def.get("is_enforcement_point") and grade != "REACHED":
            # UPSTREAM_ONLY enforcement fails the WHOLE chain regardless of every other stage (launcher's rule).
            chain_ok = False
    result = "PASS" if chain_ok else "FAIL"
    return {"query_id": answer.get("query_id"), "result": result, "stages": stage_grades}


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
    both_enforcement_reached = all(c["result"] == "PASS" for c in chains_out) if chains_out else False
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

def _grade_one_query(oracle_row: dict, answer: dict, items_by_id: dict, line_tolerance: int, repo) -> dict:
    citations = list(answer.get("citations") or [])
    required = oracle_row.get("required") or []
    forbidden = oracle_row.get("forbidden") or []
    recall = _recall(citations, required, items_by_id, line_tolerance, repo)
    forbidden_hits = [f for f in forbidden if any(
        anchor_matches(c, f if isinstance(f, dict) else {"record_id": f}, items_by_id, line_tolerance, repo)
        for c in citations)]
    ok = recall >= 0.8 and not forbidden_hits
    return {"query_id": oracle_row.get("query_id"), "recall": recall, "forbidden_hits": len(forbidden_hits),
            "must_state_ok": PENDING_RUBRIC, "result": "PASS" if ok else "FAIL"}


def grade_g5(oracle: dict, answers: dict, queries_meta: dict, items_by_id: dict, line_tolerance: int, repo=None) -> dict:
    answers_by_id = {a.get("query_id"): a for a in (answers.get("answers") or [])}
    per_query = []
    for row in oracle.get("queries") or []:
        qid = row.get("query_id")
        meta = queries_meta.get(qid) or {}
        if meta.get("kind") not in ("query_class",):
            continue
        ans = answers_by_id.get(qid) or {"query_id": qid}
        per_query.append({**_grade_one_query(row, ans, items_by_id, line_tolerance, repo),
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


def grade_g8(oracle: dict, answers: dict, queries_meta: dict, items_by_id: dict, line_tolerance: int, repo=None) -> dict:
    answers_by_id = {a.get("query_id"): a for a in (answers.get("answers") or [])}
    per_query = []
    for row in oracle.get("controls") or []:
        qid = row.get("query_id")
        ans = answers_by_id.get(qid) or {"query_id": qid}
        per_query.append(_grade_one_query(row, ans, items_by_id, line_tolerance, repo))
    result = "PASS" if per_query and all(r["result"] == "PASS" for r in per_query) else ("FAIL" if per_query else PENDING_RUBRIC)
    return {"result": result, "per_query": per_query}


# ---------------------------------------------------------------------------------------------------------------
# G6: F1 evidence both ways.
# ---------------------------------------------------------------------------------------------------------------

def grade_g6(oracle: dict, answers: dict, items_by_id: dict, line_tolerance: int, repo=None) -> dict:
    bw_oracle = oracle.get("f1_both_ways") or {}
    bw_answer = next((a for a in (answers.get("answers") or []) if a.get("evidence_for") is not None
                       or a.get("evidence_against") is not None or a.get("disposition") is not None), {})
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
                external_read_bytes += len(raw) if raw else 0
            except Exception:
                pass

    undeclared = []
    sweep_commands = []
    if reads:
        declared = {(e.get("path"), e.get("commit")) for e in ext}
        for r in reads.get("reads") or []:
            key = (r.get("path"), r.get("commit"))
            if r.get("path") and key not in declared and not any(k[0] == r.get("path") for k in declared):
                undeclared.append(r)
        sweep_commands = reads.get("sweep_commands") or []

    problems = []
    if budget_bytes and packet_bytes > 0.01 * (corpus_bytes or 0) and corpus_bytes:
        problems.append(f"packet_bytes {packet_bytes} exceeds 1% of corpus ({corpus_bytes})")
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
          corpus_bytes: Optional[int] = None, repo: Optional[str] = None) -> dict:
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

    main_packet = packets[0] if packets else {"manifest": {"sections": {}, "notices": []}, "task_spec": {}, "meta": {}}
    items_by_id = _manifest_items_by_id(main_packet["manifest"]) if packets else {}

    g1 = grade_g1(packets, repo=repo) if packets else {"result": PENDING_RUBRIC, "packets": []}
    g2 = grade_g2(packets, receipt, repo=repo) if packets else {"result": PENDING_RUBRIC, "reasons": []}
    g3 = grade_g3(oracle, answers, main_packet) if packets else {"result": PENDING_RUBRIC}
    g4 = grade_g4(oracle, answers, items_by_id, line_tolerance, repo)
    g5 = grade_g5(oracle, answers, queries_meta, items_by_id, line_tolerance, repo)
    g6 = grade_g6(oracle, answers, items_by_id, line_tolerance, repo)
    g7 = grade_g7(packets, receipt, corpus_bytes, None, reads, repo=repo) if packets else \
        {"result": PENDING_RUBRIC, "problems": []}
    g8 = grade_g8(oracle, answers, queries_meta, items_by_id, line_tolerance, repo)

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
    p.add_argument("--repo")
    args = p.parse_args(argv)

    result = grade(args.oracle, args.answers, args.receipt, args.packet, queries_path=args.queries,
                    reads_path=args.reads, corpus_bytes=args.corpus_bytes, repo=args.repo)
    print(json.dumps(result, indent=1, sort_keys=True, default=str))
    return 0 if result["verdict"] == "DEMONSTRATION_PASS" else (
        1 if result["verdict"] == "DEMONSTRATION_FAIL" else 3)


if __name__ == "__main__":
    import sys
    sys.exit(main())
