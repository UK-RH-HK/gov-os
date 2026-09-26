"""``govbridge.answers.lint`` (REPAIR_DAG.yaml node R1-RA). Hermetic, same fixture repo/store discipline as
``tests/answers/test_cite.py``. Uses ONLY the SCHEMA (``ARCHITECTURE/schemas/answers.yaml``) as a shape reference
-- no demonstration query text, no run-1 answer content -- and its own ``RA``-prefixed synthetic identifiers.

One fixture ``answers`` document (``ANSWERS_DOC`` below) exercises all four finding kinds in separate query_ids, so
each assertion is about ONE query_id and cannot be satisfied by a different kind's finding leaking across.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

FIXTURES_ANSWERS = Path(__file__).resolve().parents[1] / "fixtures" / "answers"
if str(FIXTURES_ANSWERS) not in sys.path:
    sys.path.insert(0, str(FIXTURES_ANSWERS))
import answers_repobuilder as repobuilder  # noqa: E402

from govbridge.answers import lint as lintmod  # noqa: E402
from govbridge.core import freshness as freshnessmod  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store-test-lint"))
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)


@pytest.fixture()
def built(tmp_path):
    repo = repobuilder.build(tmp_path)
    r = freshnessmod.run(view_path=repo.view_path, rules_path=repo.rules_path, repo=str(repo.root), from_clean=True)
    assert r["trigger"] == "FULL"
    return repo


def _answers_doc(commit: str) -> dict:
    return {
        "schema": "govbridge-answers/1",
        "run_id": "RA-TEST-RUN",
        "packets_used": ["deadbeef"],
        "answers": [
            {
                # REPAIR_DAG.yaml acceptance: "names three tests and cites one yields two NAMED_NOT_CITED".
                "query_id": "Q1",
                "status": "ANSWERED",
                "answer_text": ("The fix touches ra_unique_fn and is covered by test_ra_python_unique; "
                                 "RA-L-0001 records the decision."),
                "citations": [{"item_id": "ra_unique_fn"}],
            },
            {
                # a whole-document citation of a document that HAS a section map.
                "query_id": "Q2",
                "status": "ANSWERED",
                "answer_text": "See the sub detail section about ra_unique_fn.",
                # `ra_unique_fn` is ALSO cited here (its own item_id) so this answer stays clean under
                # NAMED_NOT_CITED -- this fixture is deliberately scoped to ONE finding kind per query_id.
                "citations": [{"exact": {"path": repobuilder.GUIDE_PATH, "commit": commit}},
                              {"item_id": "ra_unique_fn"}],
            },
            {
                # a claim that points to "another answer" instead of restating it (a generic outward phrase).
                "query_id": "Q3",
                "status": "PARTIAL",
                "answer_text": "See the answer to Q1 for the fix location.",
                "citations": [],
            },
            {
                # a claim that literally names another answer's own query_id, no restating phrase needed.
                "query_id": "Q4",
                "status": "PARTIAL",
                "answer_text": "The value equals what Q1 already established.",
                "citations": [],
            },
            {
                # NOT_SELF_CONTAINED: ANSWERED with zero citations anywhere in its own record.
                "query_id": "Q5",
                "status": "ANSWERED",
                "answer_text": "an ungrounded claim",
                "citations": [],
            },
            {
                # NOT_SELF_CONTAINED: PARTIAL/ANSWERED with an empty answer_text.
                "query_id": "Q6",
                "status": "PARTIAL",
                "answer_text": "",
                "citations": [],
            },
            {
                # NOT_SELF_CONTAINED: a chain stage whose claim carries no citations of its own, even though the
                # answer as a whole is not uncited (its own top-level citations list is non-empty).
                "query_id": "Q7",
                "status": "ANSWERED",
                "answer_text": "chain answer text",
                "citations": [{"item_id": "some-other-item"}],
                "stages": [
                    {"stage": 1, "claim": "first stage claim text", "citations": [], "is_enforcement_point": False},
                ],
            },
            {
                # a clean answer: fully self-contained, nothing named-but-uncited, no cross reference.
                "query_id": "Q8",
                "status": "ANSWERED",
                "answer_text": "a clean, self-contained answer citing its own claim",
                "citations": [{"item_id": "clean-item"}],
            },
        ],
    }


def _findings_of_kind(result: dict, kind: str) -> list:
    return [f for f in result["findings"] if f["kind"] == kind]


def _by_query(findings: list, query_id: str) -> list:
    return [f for f in findings if f["query_id"] == query_id]


def test_named_not_cited_two_of_three(built):
    result = lintmod.lint_answers(_answers_doc(built.commit), [], view_path=built.view_path, repo=str(built.root))
    named = _by_query(_findings_of_kind(result, lintmod.KIND_NAMED_NOT_CITED), "Q1")
    idents = {f["identifier"] for f in named}
    assert idents == {"test_ra_python_unique", "RA-L-0001"}
    assert "ra_unique_fn" not in idents  # it WAS cited


def test_named_not_cited_absent_for_clean_answer(built):
    result = lintmod.lint_answers(_answers_doc(built.commit), [], view_path=built.view_path, repo=str(built.root))
    assert _by_query(_findings_of_kind(result, lintmod.KIND_NAMED_NOT_CITED), "Q8") == []


def test_doc_level_citation_suggests_the_nested_section(built):
    result = lintmod.lint_answers(_answers_doc(built.commit), [], view_path=built.view_path, repo=str(built.root))
    findings = _by_query(_findings_of_kind(result, lintmod.KIND_DOC_LEVEL_CITATION), "Q2")
    assert len(findings) == 1
    f = findings[0]
    assert f["path"] == repobuilder.GUIDE_PATH
    assert f["suggested_anchor"]["title"].startswith("2.1")
    assert f["suggested_anchor"]["lines"][0] <= f["suggested_anchor"]["lines"][1]


def test_doc_level_citation_absent_when_lines_are_given(built):
    doc = _answers_doc(built.commit)
    doc["answers"][1]["citations"] = [{"exact": {"path": repobuilder.GUIDE_PATH, "lines": [3, 3]}}]
    result = lintmod.lint_answers(doc, [], view_path=built.view_path, repo=str(built.root))
    assert _by_query(_findings_of_kind(result, lintmod.KIND_DOC_LEVEL_CITATION), "Q2") == []


def test_doc_level_citation_via_item_id_manifest_lookup(tmp_path, built):
    """The OTHER schema-legal citation shape (``{item_id}``, resolved through a packet's own manifest.json) --
    a hand-built manifest row in the REAL shape ``govbridge.compile.render.item_manifest_row`` writes (``unit``,
    ``source: {path, commit, line_start, line_end}``), never a real compiler run (this is a pure-function unit
    test of the lookup, not a re-test of the compiler itself)."""
    packet_dir = tmp_path / "packet"
    packet_dir.mkdir()
    manifest = {
        "sections": {
            "H": {
                "items": [
                    {
                        "item_id": "h:1", "unit": {"kind": "occurrence", "id": repobuilder.GUIDE_PATH},
                        "source": {"ref": "records", "commit": built.commit, "path": repobuilder.GUIDE_PATH,
                                   "blob": None, "line_start": None, "line_end": None},
                    },
                ],
            },
        },
    }
    (packet_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    doc = _answers_doc(built.commit)
    doc["answers"][1]["citations"] = [{"item_id": "h:1"}]
    result = lintmod.lint_answers(doc, [str(packet_dir)], view_path=built.view_path, repo=str(built.root))
    findings = _by_query(_findings_of_kind(result, lintmod.KIND_DOC_LEVEL_CITATION), "Q2")
    assert len(findings) == 1
    assert findings[0]["path"] == repobuilder.GUIDE_PATH


def test_cross_answer_reference_phrase_and_literal_query_id(built):
    result = lintmod.lint_answers(_answers_doc(built.commit), [], view_path=built.view_path, repo=str(built.root))
    cross = _findings_of_kind(result, lintmod.KIND_CROSS_ANSWER_REFERENCE)
    assert _by_query(cross, "Q3"), "the 'see the answer to Q1' phrase was not flagged"
    assert _by_query(cross, "Q4"), "the literal mention of another answer's own query_id was not flagged"
    assert _by_query(cross, "Q8") == []


def test_cross_answer_reference_does_not_fire_on_a_compound_word(built):
    """Real-view regression (AGENT_RUNS/BR-AR-0027.check08-realview-answers-lint.out, first run): "See the
    answer-side aids section of REPAIR_PLAN.md for details." is NOT a pointer to another answer -- "answer-side"
    is a section name's own compound word, not the phrase "see the answer". A bare ``\\b`` after "answer" is also
    satisfied at a hyphen, so this must be checked with a real hyphenated word, not just asserted by inspection."""
    doc = {"schema": "govbridge-answers/1", "run_id": "RA-COMPOUND", "packets_used": [], "answers": [
        {"query_id": "QCOMP", "status": "ANSWERED",
         "answer_text": "See the answer-side aids section of REPAIR_PLAN.md for details.",
         "citations": [{"item_id": "x"}]},
    ]}
    result = lintmod.lint_answers(doc, [], view_path=built.view_path, repo=str(built.root))
    assert _findings_of_kind(result, lintmod.KIND_CROSS_ANSWER_REFERENCE) == []


def test_not_self_contained_three_shapes(built):
    result = lintmod.lint_answers(_answers_doc(built.commit), [], view_path=built.view_path, repo=str(built.root))
    nsc = _findings_of_kind(result, lintmod.KIND_NOT_SELF_CONTAINED)
    assert _by_query(nsc, "Q5"), "ANSWERED with zero citations anywhere was not flagged"
    assert _by_query(nsc, "Q6"), "empty answer_text was not flagged"
    q7 = _by_query(nsc, "Q7")
    assert q7 and q7[0]["context"] == "stage:1"
    assert _by_query(nsc, "Q8") == []


def test_status_and_exit_code_without_waivers(built):
    result = lintmod.lint_answers(_answers_doc(built.commit), [], view_path=built.view_path, repo=str(built.root))
    assert result["status"] == "FINDINGS"
    assert result["open_findings"] > 0
    assert all(f["waived"] is False for f in result["findings"])


def test_waivers_reduce_open_findings_but_keep_the_row(built):
    result = lintmod.lint_answers(_answers_doc(built.commit), [], view_path=built.view_path, repo=str(built.root),
                                   waivers=["NAMED_NOT_CITED:Q1", "DOC_LEVEL_CITATION:Q2", "CROSS_ANSWER_REFERENCE",
                                            "NOT_SELF_CONTAINED"])
    q1 = _by_query(_findings_of_kind(result, lintmod.KIND_NAMED_NOT_CITED), "Q1")
    assert q1 and all(f["waived"] for f in q1)
    assert result["open_findings"] == 0
    assert result["status"] == "PASS"
    # the waived rows are still REPORTED, never dropped silently.
    assert len(result["findings"]) >= 6


def test_clean_answers_document_passes(built):
    doc = {"schema": "govbridge-answers/1", "run_id": "RA-CLEAN", "packets_used": [], "answers": [
        {"query_id": "QC1", "status": "ANSWERED", "answer_text": "a clean answer", "citations": [{"item_id": "x"}]},
    ]}
    result = lintmod.lint_answers(doc, [], view_path=built.view_path, repo=str(built.root))
    assert result == {"findings": [], "open_findings": 0, "status": "PASS"}


def test_extract_candidate_identifiers_shapes():
    text = "see fn_one and mod_a::mod_b::fn and D-0001 and REPAIR_PLAN.md §7"
    found = lintmod._extract_candidate_identifiers(text)
    assert "fn_one" in found
    assert "mod_a::mod_b::fn" in found
    assert "D-0001" in found
    assert "REPAIR_PLAN.md §7" in found


def test_cli_lint_exit_codes(built, tmp_path, capsys):
    import yaml as pyyaml

    answers_path = tmp_path / "answers.yaml"
    answers_path.write_text(pyyaml.safe_dump(_answers_doc(built.commit), sort_keys=False), encoding="utf-8")
    packet_dir = tmp_path / "empty_packet"
    packet_dir.mkdir()
    (packet_dir / "manifest.json").write_text(json.dumps({"sections": {}}), encoding="utf-8")

    rc = lintmod.main([str(answers_path), "--packet", str(packet_dir), "--view", built.view_path,
                        "--repo", str(built.root)])
    assert rc == 1
    capsys.readouterr()

    clean_path = tmp_path / "clean.yaml"
    clean_doc = {"schema": "govbridge-answers/1", "run_id": "RA-CLEAN2", "packets_used": [], "answers": [
        {"query_id": "QC2", "status": "ANSWERED", "answer_text": "clean", "citations": [{"item_id": "x"}]},
    ]}
    clean_path.write_text(pyyaml.safe_dump(clean_doc, sort_keys=False), encoding="utf-8")
    rc = lintmod.main([str(clean_path), "--packet", str(packet_dir), "--view", built.view_path,
                        "--repo", str(built.root)])
    assert rc == 0
