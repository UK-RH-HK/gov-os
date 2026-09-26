#!/usr/bin/env python3
"""``govbridge answers lint <answers> --packet DIR [--supplementary DIR...]`` (REPAIR_DAG.yaml node R1-RA,
REPAIR_PLAN.md section 7, RC-11). Advisory for the demonstration agent (never a grader, never touching any oracle
or sealed path): reports four kinds of finding over one ``schemas/answers.yaml``-shaped document, machine-readable,
exit 1 on any open (non-waived) finding.

* **NAMED_NOT_CITED** -- an identifier named in a claim's own free text that :mod:`govbridge.answers.cite` resolves
  in the index, yet is absent from that SAME claim's own citation list.
* **DOC_LEVEL_CITATION** -- a citation of a WHOLE document (no line range, whether given as ``{exact: {path,
  commit}}`` with no ``lines``, or as an ``item_id`` whose packet-manifest row records no ``line_start``) for a
  document that has a section map (R1-RM's ``govbridge.compile.sectionmap``, at least one heading/key). The
  suggested anchor is the section whose title shares the most words with the claim text (deterministic tie-break:
  document order), never a guess at "the right" section without evidence.
* **CROSS_ANSWER_REFERENCE** -- a claim that POINTS to another answer instead of restating it: a generic outward-
  pointer phrase ("see the answer...", "as stated in..."), or a literal mention of another answer's own
  ``query_id`` within this claim's text.
* **NOT_SELF_CONTAINED** -- per-query self-containment, checked on the answer record's own fields, independent of
  any other answer: an ``ANSWERED``/``PARTIAL`` answer with empty ``answer_text``; an ``ANSWERED`` answer carrying
  no citation anywhere in its own record; or a chain stage whose ``claim`` is non-empty but whose own ``citations``
  are empty.

A finding is WAIVED when a caller-supplied waiver string is a prefix of (or exactly equals) its own
``"{kind}:{query_id}:{extra}"`` key -- the run-2 protocol's own "a clean lint or a justified waiver per finding"
(REPAIR_PLAN.md section 7).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

from govbridge.answers import cite as citemod

KIND_NAMED_NOT_CITED = "NAMED_NOT_CITED"
KIND_DOC_LEVEL_CITATION = "DOC_LEVEL_CITATION"
KIND_CROSS_ANSWER_REFERENCE = "CROSS_ANSWER_REFERENCE"
KIND_NOT_SELF_CONTAINED = "NOT_SELF_CONTAINED"

_SNAKE_RE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
_RUST_PATH_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*(?:::[a-zA-Z_][a-zA-Z0-9_]*)+\b")
_DOC_ANCHOR_SCAN_RE = re.compile(r"\S+\s+§\s*\d+(?:\.\d+)*")
_WORD_RE = re.compile(r"[a-zA-Z0-9]+")

#: "answer(?!-)": excludes a compound word like "answer-side" (as in "the answer-side aids section") -- a bare
#: `\b` alone is satisfied at a hyphen too (a word/non-word boundary), so without this the phrase scan would
#: mistake a section NAME for a pointer to another answer. Found empirically on the real view (CONTROL-A,
#: AGENT_RUNS/BR-AR-0027.check08-realview-answers-lint.out first run): "See the answer-side aids section of
#: REPAIR_PLAN.md" matched "see (the )?answer" before this fix.
_CROSS_REF_PHRASES_RE = re.compile(
    r"\b(see (the )?(other )?answer(?!-)|as (stated|noted|shown|answered) (in|for|above)"
    r"|refer(?:s)? to (the )?(other )?answer(?!-)|per (the )?(other )?answer(?!-)"
    r"|stated in (another|the other) answer(?!-)"
    r"|already (stated|answered) (in|for) (another|the other) (query|answer(?!-)))\b",
    re.IGNORECASE,
)


def _extract_candidate_identifiers(text: str) -> set:
    out: set = set()
    if not text:
        return out
    for m in _RUST_PATH_RE.finditer(text):
        out.add(m.group(0))
    for m in _SNAKE_RE.finditer(text):
        out.add(m.group(0))
    for m in citemod.id_token_re().finditer(text):
        out.add(m.group(0))
    for m in _DOC_ANCHOR_SCAN_RE.finditer(text):
        out.add(m.group(0))
    return out


def _is_cited(identifier: str, citations: list) -> bool:
    for c in citations or []:
        if not isinstance(c, dict):
            continue
        if c.get("item_id") == identifier:
            return True
        ex = c.get("exact")
        if isinstance(ex, dict):
            path = ex.get("path") or ""
            stem = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            if stem == identifier or (identifier and identifier in path):
                return True
    return False


def _claim_contexts(answer: dict) -> list:
    """[(claim_text, citations, context_label)] for every free-text/citation pairing ``schemas/answers.yaml``
    defines on one answer record -- generic across every answer shape (plain, chain, side-by-side, both-ways):
    a field this particular answer does not carry is simply absent from the result, never an error."""
    out = [(answer.get("answer_text") or "", answer.get("citations") or [], "answer_text")]
    for stage in answer.get("stages") or []:
        if isinstance(stage, dict):
            out.append((stage.get("claim") or "", stage.get("citations") or [],
                        f"stage:{stage.get('stage')}"))
    for label in ("evidence_for", "evidence_against"):
        for ev in answer.get(label) or []:
            if isinstance(ev, dict):
                out.append((ev.get("claim") or "", ev.get("citations") or [], label))
    return out


def _find_manifest_item(packet_dirs: list, item_id: str) -> Optional[dict]:
    for pd in packet_dirs:
        manifest_path = Path(pd) / "manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for letter, sec in (manifest.get("sections") or {}).items():
            rows = sec.get("items") or []
            if letter == "D":
                rows = [r for sub in (sec.get("subblocks") or {}).values() for r in (sub.get("items") or [])]
            for row in rows:
                if row.get("item_id") == item_id:
                    return row
    return None


def _citation_source(citation: dict, packet_dirs: list) -> Optional[dict]:
    if not isinstance(citation, dict):
        return None
    if "exact" in citation:
        ex = citation.get("exact") or {}
        return {"path": ex.get("path"), "commit": ex.get("commit"), "has_lines": bool(ex.get("lines"))}
    item_id = citation.get("item_id")
    if item_id is None:
        return None
    row = _find_manifest_item(packet_dirs, item_id)
    if row is None:
        return None
    src = row.get("source") or {}
    return {"path": src.get("path"), "commit": src.get("commit"),
            "has_lines": src.get("line_start") is not None, "item_id": item_id}


def _suggest_anchor(sections: list, claim_text: str):
    claim_words = {w.lower() for w in _WORD_RE.findall(claim_text or "") if len(w) > 2}
    best = sections[0]
    best_score = -1
    for s in sections:
        title_words = {w.lower() for w in _WORD_RE.findall(s.name) if len(w) > 2}
        score = len(claim_words & title_words)
        if score > best_score:
            best_score = score
            best = s
    return best


def _check_doc_level(citation: dict, packet_dirs: list, claim_text: str, repo: Optional[str],
                      query_id, label: str) -> Optional[dict]:
    from govbridge.compile import sectionmap as sectionmapmod
    from govbridge.core import gitobj

    src = _citation_source(citation, packet_dirs)
    if not src or src["has_lines"] or not src.get("path") or not src.get("commit"):
        return None
    path, commit = src["path"], src["commit"]
    try:
        raw = gitobj.read_path(commit, path, repo=repo)
    except Exception:
        raw = None
    if raw is None:
        return None
    text = raw.decode("utf-8", "replace")
    try:
        sections = sectionmapmod.flat_tiling(text, path)
    except Exception:
        sections = []
    if len(sections) <= 1:
        return None  # no meaningful section map to suggest an anchor from
    suggested = _suggest_anchor(sections, claim_text)
    return {
        "kind": KIND_DOC_LEVEL_CITATION, "query_id": query_id, "context": label, "path": path, "commit": commit,
        "suggested_anchor": {"title": suggested.name, "lines": [suggested.line_start, suggested.line_end]},
        "detail": f"whole-document citation of {path!r} ({len(sections)} section(s) in its section map)",
    }


def _mentions_other_query_id(text: str, own_query_id, all_query_ids: list) -> Optional[str]:
    if not text:
        return None
    for qid in all_query_ids:
        if not qid or qid == own_query_id:
            continue
        if re.search(rf"\b{re.escape(str(qid))}\b", text):
            return qid
    return None


def _check_self_contained(answer: dict, total_citations: int) -> list:
    out = []
    query_id = answer.get("query_id")
    status = answer.get("status")
    answer_text = (answer.get("answer_text") or "").strip()
    if status in ("ANSWERED", "PARTIAL") and not answer_text:
        out.append({"kind": KIND_NOT_SELF_CONTAINED, "query_id": query_id, "context": "answer_text",
                     "detail": f"status={status} but answer_text is empty"})
    if status == "ANSWERED" and total_citations == 0:
        out.append({"kind": KIND_NOT_SELF_CONTAINED, "query_id": query_id, "context": "answer",
                     "detail": "status=ANSWERED but the answer carries no citation anywhere in its own record"})
    for stage in answer.get("stages") or []:
        if not isinstance(stage, dict):
            continue
        claim = (stage.get("claim") or "").strip()
        cites = stage.get("citations") or []
        if claim and not cites:
            out.append({"kind": KIND_NOT_SELF_CONTAINED, "query_id": query_id,
                         "context": f"stage:{stage.get('stage')}",
                         "detail": "stage claim has no citations of its own"})
    return out


def _finding_key(f: dict) -> str:
    extra = f.get("identifier") or f.get("path") or f.get("context") or ""
    return f"{f['kind']}:{f.get('query_id')}:{extra}"


def lint_answers(answers_doc: dict, packet_dirs: list, *, commit: Optional[str] = None,
                  view_path: Optional[str] = None, repo: Optional[str] = None,
                  registry_path: Optional[str] = None, waivers: Optional[list] = None) -> dict:
    # BR-DAG-AMEND-R1-23 (ONE RESOLVED VIEW PER OPERATION): a lint run used to make one INDEPENDENT
    # config/canonical-view.yaml resolution per uncited identifier, per claim, per answer (each of citemod.
    # cite_identifier's own calls below, previously never given a resolved_view). One "answers lint" invocation
    # now resolves ONCE, here, and threads the SAME view through every cite_identifier call in this run.
    from govbridge.core import view as viewmod
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    vp = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    resolved_view = viewmod.resolve_view(viewmod.load_view(vp), repo=repo)

    findings: list = []
    answers = answers_doc.get("answers") or []
    all_query_ids = [a.get("query_id") for a in answers]

    for answer in answers:
        if not isinstance(answer, dict):
            continue
        query_id = answer.get("query_id")
        contexts = _claim_contexts(answer)
        total_citations = 0

        for claim_text, citations, label in contexts:
            total_citations += len(citations or [])

            for ident in sorted(_extract_candidate_identifiers(claim_text)):
                if _is_cited(ident, citations):
                    continue
                res = citemod.cite_identifier(ident, commit=commit, view_path=view_path, repo=repo,
                                               registry_path=registry_path, resolved_view=resolved_view)
                if res["status"] in (citemod.STATUS_RESOLVED, citemod.STATUS_AMBIGUOUS):
                    findings.append({
                        "kind": KIND_NAMED_NOT_CITED, "query_id": query_id, "context": label, "identifier": ident,
                        "resolution": res["status"],
                        "detail": f"{ident!r} resolves in the index ({res['status']}) but is not cited in {label}",
                    })

            for c in citations or []:
                f = _check_doc_level(c, packet_dirs, claim_text, repo, query_id, label)
                if f is not None:
                    findings.append(f)

            m = _CROSS_REF_PHRASES_RE.search(claim_text or "")
            if m:
                findings.append({
                    "kind": KIND_CROSS_ANSWER_REFERENCE, "query_id": query_id, "context": label,
                    "detail": f"claim text points to another answer ({m.group(0)!r}) instead of restating it",
                })
            other_qid = _mentions_other_query_id(claim_text, query_id, all_query_ids)
            if other_qid:
                findings.append({
                    "kind": KIND_CROSS_ANSWER_REFERENCE, "query_id": query_id, "context": label,
                    "detail": f"claim text references {other_qid!r} instead of restating the fact",
                })

        findings.extend(_check_self_contained(answer, total_citations))

    waivers = waivers or []
    out_findings = []
    open_count = 0
    for f in findings:
        key = _finding_key(f)
        waived = any(key == w or key.startswith(w) for w in waivers)
        row = dict(f)
        row["waived"] = waived
        out_findings.append(row)
        if not waived:
            open_count += 1

    # BR-DAG-AMEND-R1-23 requirement 1: the recorded view in this output must equal the commits actually used.
    return {"findings": out_findings, "open_findings": open_count,
            "status": "PASS" if open_count == 0 else "FINDINGS", "resolved_refs": resolved_view.pinned_refs()}


def main(argv=None) -> int:
    from govbridge.core.yamlutil import load_yaml_file

    p = argparse.ArgumentParser(prog="govbridge answers lint")
    p.add_argument("answers")
    p.add_argument("--packet", required=True, help="the main packet directory this run's answers were built from")
    p.add_argument("--supplementary", action="append", default=[], metavar="DIR",
                    help="repeatable: a further supplementary packet directory this run also wrote")
    p.add_argument("--commit")
    p.add_argument("--view")
    p.add_argument("--repo")
    p.add_argument("--registry")
    p.add_argument("--waive", action="append", default=[], metavar="KIND:QUERY_ID[:DETAIL]")
    args = p.parse_args(argv)

    answers_doc = load_yaml_file(args.answers)
    packet_dirs = [args.packet, *args.supplementary]
    result = lint_answers(answers_doc, packet_dirs, commit=args.commit, view_path=args.view, repo=args.repo,
                           registry_path=args.registry, waivers=args.waive)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
