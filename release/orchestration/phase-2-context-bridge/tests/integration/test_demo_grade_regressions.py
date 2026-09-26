"""REPAIR-1 node R1-RG: one regression test per grader defect GD-1..GD-10 and OBS-BR-05
(``ARCHITECTURE/REPAIR-1/REPAIR_PLAN.md`` section 8.2), implementing BR-ARCH-RULING-2's D-1..D-5 exactly as ruled.

Every fixture here is synthetic (``T-*``/``CX-*`` ids, never Review-8/Phase-2 content -- OC-BR-02) and every
acceptance check is proved against a fixture oracle/answers/receipt/transcript this run wrote itself, never the
held-out oracle or the run-1 answers (REPAIR-1 rule 2). Each test below is written to FAIL against the pre-repair
``govbridge/demo/grade.py``/``extract_reads.py`` (confirmed empirically while diagnosing each defect) and PASS
after the fix in this same commit -- the acceptance check `REPAIR_DAG.yaml` node R1-RG names.

Two fixtures live under ``tests/fixtures/demo/`` (this node's own scope) because they are genuinely file-shaped:
a transcript (GD-6, ``extract_reads.extract`` reads a real JSONL) and a rubric-results file (GD-9, ``grade()``'s
``--rubric``). Every other defect is a property of a single grading function on a small, literal, self-documenting
fixture -- calling `anchor_matches`/`grade_gN` directly, rather than a full compiled-packet fixture apiece, keeps
each regression test precise (it pins exactly the one behaviour the defect describes) and fast; GD-10 alone needs
a real, git-backed repo (the code store it queries is commit-addressed), so it reuses the existing, generic
``tests/fixtures/compile/compile_repobuilder.py`` fixture that ``tests/integration/test_demo_grade.py`` already
depends on.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

FIXTURES_COMPILE = Path(__file__).resolve().parents[1] / "fixtures" / "compile"
sys.path.insert(0, str(FIXTURES_COMPILE))
import compile_repobuilder as repobuilder  # noqa: E402

from govbridge.compile import packet as packetmod
from govbridge.core.yamlutil import load_yaml_file
from govbridge.demo import extract_reads as ermod
from govbridge.demo import grade as g
from govbridge.route.router import FAKE_ROUTES

FIXTURES_INTEGRATION = Path(__file__).resolve().parents[1] / "fixtures" / "integration"
FIXTURES_DEMO = Path(__file__).resolve().parents[1] / "fixtures" / "demo"
ORACLE_PATH = str(FIXTURES_INTEGRATION / "oracle-synthetic.yaml")
QUERIES_PATH = str(FIXTURES_INTEGRATION / "demo-queries-synthetic.yaml")
ANSWERS_PASSING_PATH = str(FIXTURES_INTEGRATION / "answers-passing.yaml")
RUBRIC_GD9_PATH = str(FIXTURES_DEMO / "rubric-gd9.yaml")
TRANSCRIPT_GD6_PATH = str(FIXTURES_DEMO / "transcript-gd6.jsonl")


@pytest.fixture(autouse=True)
def _no_env_leak(monkeypatch):
    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)


# ---------------------------------------------------------------------------------------------------------------
# GD-1: crash on `lines: "START-END"` (and other accepted forms).
# ---------------------------------------------------------------------------------------------------------------

def test_gd1_string_and_single_line_forms_grade_without_error():
    items_by_id = {}
    anchor = {"path": "a/b.py", "commit": "c1", "lines": [12, 15]}
    # a "START-END" string -- the pre-repair code unpacked this 5-character STRING as if it were a 2-element
    # sequence (`clo, chi = c_lines`) and crashed with `ValueError: too many values to unpack`.
    assert g.anchor_matches({"path": "a/b.py", "commit": "c1", "lines": "12-15"}, anchor, items_by_id) is True
    # a single bare int (one line) -- the pre-repair code crashed with `TypeError: cannot unpack non-iterable int`.
    assert g.anchor_matches({"path": "a/b.py", "commit": "c1", "lines": 13}, anchor, items_by_id) is True
    # a single-element list -- also previously unhandled.
    assert g.anchor_matches({"path": "a/b.py", "commit": "c1", "lines": [13]}, anchor, items_by_id) is True
    # the ordinary [start, end] list form must keep working.
    assert g.anchor_matches({"path": "a/b.py", "commit": "c1", "lines": [12, 15]}, anchor, items_by_id) is True
    # a citation outside the anchor's line range must still correctly NOT match.
    assert g.anchor_matches({"path": "a/b.py", "commit": "c1", "lines": "100-105"}, anchor, items_by_id) is False


# ---------------------------------------------------------------------------------------------------------------
# GD-2: G6 grades the first answer with `evidence_for`, not the oracle's own both-ways query id.
# ---------------------------------------------------------------------------------------------------------------

def test_gd2_g6_selects_the_both_ways_answer_by_query_id():
    oracle = {"f1_both_ways": {"query_id": "T-BOTHWAYS", "purpose_anchors": [{"path": "n.md", "commit": "c1"}],
                                "consumer_anchors": [{"path": "n.md", "commit": "c1"}]}}
    answers = {"answers": [
        # a DIFFERENT answer, listed FIRST, that also happens to carry evidence_for -- the pre-repair code graded
        # this one (`next(... a.get("evidence_for") is not None ...)`), regardless of its query_id.
        {"query_id": "T-OTHER", "evidence_for": [{"claim": "wrong", "citations": []}]},
        {"query_id": "T-BOTHWAYS",
         "evidence_for": [{"claim": "purpose", "citations": [{"path": "n.md", "commit": "c1"}]}],
         "evidence_against": [{"claim": "consumer", "citations": [{"path": "n.md", "commit": "c1"}]}]},
    ]}
    result = g.grade_g6(oracle, answers, {}, 3, None)
    assert result["result"] == "PASS", result
    assert result["purpose_hit"] is True
    assert result["consumer_recall"] == 1.0


# ---------------------------------------------------------------------------------------------------------------
# GD-3: a record anchor matched by record id only -- it must ALSO match "by section" (path, blob-identical
# commit, line overlap) when the anchor or the citation carries no record id string.
# ---------------------------------------------------------------------------------------------------------------

def test_gd3_a_record_section_anchor_matches_a_line_citation_in_that_section():
    # the anchor identifies a SECTION of record T-REC-1 by path/commit/line-range (not by a bare id-string
    # citation); the citation is a plain line citation into that same section -- the pre-repair code's record
    # branch (`if anchor.get("record_id"): return resolved.get("record_id") == anchor["record_id"]`) returned
    # False here unconditionally, because a raw path/commit/lines citation never carries a `record_id` at all, and
    # never fell through to the section (path/commit/line-overlap) rule it uses for every other anchor kind.
    anchor = {"kind": "record", "record_id": "T-REC-1", "path": "notes.md", "commit": "c1", "lines": [45, 50]}
    citation = {"path": "notes.md", "commit": "c1", "lines": [46, 48]}
    assert g.anchor_matches(citation, anchor, {}) is True
    # a citation to an unrelated section of a DIFFERENT file must still not match.
    other = {"path": "other.md", "commit": "c1", "lines": [46, 48]}
    assert g.anchor_matches(other, anchor, {}) is False


# ---------------------------------------------------------------------------------------------------------------
# GD-4: the withdrawn-finding check was one literal phrase ("{id} (WITHDRAWN"); it must recognise the marker
# generically, wherever it appears on the SAME line as the citation.
# ---------------------------------------------------------------------------------------------------------------

def _g3_withdrawn_verdict(answer_text: str) -> str:
    oracle = {"authority_expectations": [{"item": "T-REC-W1", "class": "EVIDENCE_WITHDRAWN"}]}
    main_packet = {"manifest": {"sections": {"A": {"items": []}, "D": {"subblocks": {"D.1": {"items": []}}}},
                                 "notices": []}}
    answers = {"answers": [{"query_id": "Q1", "answer_text": answer_text}]}
    result = g.grade_g3(oracle, answers, main_packet)
    row = next(r for r in result["answer_side"] if "withdrawn" in r["rule"])
    return row["verdict"]


@pytest.mark.parametrize("spelling", [
    "See T-REC-W1 (WITHDRAWN) for background.",
    "See T-REC-W1 [WITHDRAWN] for background.",
    "See T-REC-W1 (withdrawn) for background.",  # lower case
    "T-REC-W1 -- WITHDRAWN, not used as a finding.",  # dash form
    "T-REC-W1: WITHDRAWN. Not cited as support.",  # colon form
])
def test_gd4_several_withdrawn_marker_spellings_pass(spelling):
    assert _g3_withdrawn_verdict(spelling) == "PASS", spelling


def test_gd4_an_unmarked_withdrawn_citation_fails():
    assert _g3_withdrawn_verdict("T-REC-W1 shows the defect clearly.") == "FAIL"


# ---------------------------------------------------------------------------------------------------------------
# GD-5: side-by-side required BOTH WHOLE CHAINS to PASS; it must require only both ENFORCEMENT POINTS reached.
# ---------------------------------------------------------------------------------------------------------------

def test_gd5_side_by_side_passes_when_chains_fail_elsewhere_but_enforcement_is_reached():
    def chain(qid):
        return {"query_id": qid, "stages": [
            {"stage": "s1", "required": True, "is_enforcement_point": True,
             "anchors": {"any_of": [{"path": "x.py", "commit": "c1", "lines": [1, 2]}]}},
            # a SECOND required, non-enforcement stage that will grade MISSING -- the whole chain fails, but the
            # enforcement stage (s1) was correctly reached.
            {"stage": "s2", "required": True, "is_enforcement_point": False,
             "anchors": {"any_of": [{"path": "y.py", "commit": "c1", "lines": [1, 2]}]}},
        ]}

    oracle = {"chains": [chain("T-A"), chain("T-B")],
              "side_by_side": {"query_id": "T-SBS",
                                "shared_points": [{"path": "x.py", "commit": "c1", "lines": [1, 2]}],
                                "differing_points": []}}
    answers = {"answers": [
        {"query_id": "T-A", "stages": [{"stage": "s1", "citations": [{"path": "x.py", "commit": "c1",
                                                                       "lines": [1, 2]}]}]},
        {"query_id": "T-B", "stages": [{"stage": "s1", "citations": [{"path": "x.py", "commit": "c1",
                                                                       "lines": [1, 2]}]}]},
        {"query_id": "T-SBS", "shared_points": [{"path": "x.py", "commit": "c1", "lines": [1, 2]}],
         "differing_points": []},
    ]}
    result = g.grade_g4(oracle, answers, {}, 3, None)
    assert [c["result"] for c in result["chains"]] == ["FAIL", "FAIL"]  # the chains DO fail elsewhere
    assert result["side_by_side"]["result"] == "PASS", result["side_by_side"]  # yet side-by-side passes


# ---------------------------------------------------------------------------------------------------------------
# GD-6/D-4: undeclared-read false positives on a govbridge selector argument and the agent's own output; a
# genuinely undeclared read must still be caught.
# ---------------------------------------------------------------------------------------------------------------

def test_gd6_selector_and_own_output_are_not_read_false_positives():
    result = ermod.extract(TRANSCRIPT_GD6_PATH)
    # the selector's embedded path ("fixtures/demo/T-CODE-1.rs:1-5") and the agent's own redirected/re-read output
    # (run-1/supplementary/queries/01-exact.json) must NOT appear as reads.
    read_paths = {r["path"] for r in result["reads"]}
    assert "fixtures/demo/T-CODE-1.rs" not in read_paths
    assert "run-1/supplementary/queries/01-exact.json" not in read_paths
    assert result["excluded_selectors"], result
    # the one GENUINE, undeclared read must still be found.
    assert read_paths == {"fixtures/demo/T-UNDECLARED.rs"}


def test_gd6_zero_true_undeclared_reads_gives_zero():
    reads = ermod.extract(TRANSCRIPT_GD6_PATH)
    packets = [{"rendered": "x", "manifest": {}, "task_spec": {}, "meta": {}, "dir": "/nowhere"}]
    # declare the one genuine read in the receipt -- a fixture transcript with 0 TRUE undeclared reads must give 0.
    receipt = {"external_reads": [{"path": "fixtures/demo/T-UNDECLARED.rs", "commit": "0" * 40}]}
    result = g.grade_g7(packets, receipt, corpus_bytes=None, budget_bytes=None, reads=reads, repo=None)
    assert result["undeclared_reads"] == []


# ---------------------------------------------------------------------------------------------------------------
# GD-7/D-5: external bytes counted as whole blobs when the receipt declared a WINDOW.
# ---------------------------------------------------------------------------------------------------------------

def test_gd7_a_declared_window_is_counted_as_a_window(tmp_path):
    import subprocess

    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "a@b.c"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "a"], cwd=repo, check=True)
    big_content = "\n".join(f"line {i}" for i in range(1000)) + "\n"
    (repo / "big.txt").write_text(big_content, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True,
                             check=True).stdout.strip()

    receipt = {"external_reads": [{"path": "big.txt", "commit": commit, "line_start": 1, "line_end": 5}]}
    result = g.grade_g7([], receipt, corpus_bytes=1_000_000, budget_bytes=None, reads=None, repo=str(repo))
    # 5 lines of "line N\n" is a few dozen bytes -- nowhere near the whole ~8.9 KB file the pre-repair code
    # charged (it always read and counted the FULL blob, regardless of a declared window).
    assert result["external_read_bytes"] < 100, result
    assert result["external_read_bytes"] > 0


# ---------------------------------------------------------------------------------------------------------------
# GD-8/D-1: a whole-document citation (by record id) matches a sectioned anchor of the SAME record, whichever
# section it targets; a citation resolving to a DIFFERENT record's id never matches.
# ---------------------------------------------------------------------------------------------------------------

def test_gd8_whole_document_citation_matches_same_record_any_section():
    # a "whole-document" citation -- a raw citation OBJECT naming only the record's id, no path/commit/lines at
    # all (the shape a worker citing "the whole record", rather than a packet item_id string, would naturally
    # produce). The pre-repair `_resolve_citation` only ever read a `record_id` off a STRING citation (looked up in
    # `items_by_id`); its dict branch required "path" or "commit" to be present and otherwise returned `None` --
    # so this exact citation shape could never resolve, and NEVER matched anything, however the anchor was framed
    # ("whole-document versus sectioned anchor undefined", GD-8). The anchor here targets a specific section of
    # T-REC-1; the whole-document citation matches it, by record id, REGARDLESS of section (BR-ARCH-RULING-2 D-1 --
    # not the analyst's rejected "delivered coverage" alternative).
    anchor_section = {"kind": "record", "record_id": "T-REC-1", "path": "notes.md", "commit": "c1",
                       "lines": [45, 50]}
    whole_doc_citation = {"record_id": "T-REC-1"}
    assert g.anchor_matches(whole_doc_citation, anchor_section, {}) is True


def test_gd8_a_citation_to_a_different_record_does_not_match():
    anchor_other_record = {"kind": "record", "record_id": "T-REC-2", "path": "notes.md", "commit": "c1"}
    whole_doc_citation = {"record_id": "T-REC-1"}
    assert g.anchor_matches(whole_doc_citation, anchor_other_record, {}) is False


# ---------------------------------------------------------------------------------------------------------------
# GD-9/D-3: [R] results (must_state per query; AUTH-style answer-side gating) must be ingested when a rubric file
# is supplied, changing G5/G3's actual result -- not only ever reported PENDING_RUBRIC.
# ---------------------------------------------------------------------------------------------------------------

def _compile_fixture_packet(tmp_path):
    fixture_repo = repobuilder.build(tmp_path / "repo")
    view_path = tmp_path / "canonical-view.yaml"
    repobuilder.write_canonical_view(view_path, fixture_repo)
    registry_path = tmp_path / "authority-registry.yaml"
    repobuilder.write_registry(registry_path)
    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-DEMO-GRADE-REGRESSIONS", "role": "test",
        "objective": "demo grade regression fixture",
        "view": str(view_path),
        "required_inputs": [{"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"}],
        "seeds": [], "queries": [],
        "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED"], "budget_profile": "bounded-builder",
    }
    result = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=str(fixture_repo.root),
                                       registry_path=str(registry_path))
    assert result["status"] == packetmod.STATUS_OK
    return result, task_spec, str(fixture_repo.root)


def _write_packet_dir(tmp_path, name, result, task_spec):
    import yaml
    d = tmp_path / name
    d.mkdir()
    (d / "packet.md").write_text(result["rendered"], encoding="utf-8")
    (d / "manifest.json").write_text(json.dumps(result["manifest"], indent=1, sort_keys=True), encoding="utf-8")
    (d / "task_spec.yaml").write_text(yaml.safe_dump(task_spec, sort_keys=False), encoding="utf-8")
    meta = {"status": result["status"], "packet_id": result.get("packet_id"),
             "packet_sha256": result.get("packet_sha256"), "manifest_sha256": result.get("manifest_sha256"),
             "registry_path": result.get("registry_path")}
    (d / "meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True), encoding="utf-8")
    return str(d)


def _valid_receipt(manifest: dict, packet_sha256: str) -> dict:
    import hashlib
    m_sha = manifest["manifest_sha256"]
    read_tokens = {letter: hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12] for letter in "ABCDEFGHIJ"}
    a_rows = manifest["sections"]["A"]["items"]
    inputs_consumed = [f"{r['unit']['id']}@{r['content_sha256']}" for r in a_rows]
    items_relied_on = [r["item_id"] for r in a_rows[:1]]
    return {
        "context_packet_hash": [packet_sha256], "manifest_sha256": [m_sha], "read_tokens": read_tokens,
        "inputs_consumed": inputs_consumed, "items_relied_on": items_relied_on, "external_reads": [],
        "outputs_produced": [], "decisions_applied": [], "acceptance_evidence": [], "deviations": [],
        "unresolved": [],
    }


def _write_yaml(path: Path, doc: dict) -> str:
    import yaml
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return str(path)


def test_gd9_rubric_flips_the_passing_fixture_to_fail(tmp_path):
    result, task_spec, repo_root = _compile_fixture_packet(tmp_path)
    packet_dir = _write_packet_dir(tmp_path, "main", result, task_spec)
    receipt_path = _write_yaml(tmp_path / "receipt.yaml", _valid_receipt(result["manifest"], result["packet_sha256"]))

    # without a rubric, the fixture (checked in test_demo_grade.py) grades DEMONSTRATION_PASS.
    baseline = g.grade(oracle_path=ORACLE_PATH, answers_path=ANSWERS_PASSING_PATH, receipt_path=receipt_path,
                        packet_dirs=[packet_dir], queries_path=QUERIES_PATH, corpus_bytes=10_000_000,
                        repo=repo_root)
    assert baseline["verdict"] == "DEMONSTRATION_PASS", json.dumps(baseline, indent=1, default=str)

    # WITH the rubric fixture (must_state fails 2 of QC1's 3 subjects; an AUTH item is gated FAIL under G3), the
    # SAME packet/answers must now grade DEMONSTRATION_FAIL -- the pre-repair code reported PENDING_RUBRIC forever
    # and never let a rubric change the result ("[R] results not ingested per query", GD-9).
    with_rubric = g.grade(oracle_path=ORACLE_PATH, answers_path=ANSWERS_PASSING_PATH, receipt_path=receipt_path,
                           packet_dirs=[packet_dir], queries_path=QUERIES_PATH, corpus_bytes=10_000_000,
                           repo=repo_root, rubric_path=RUBRIC_GD9_PATH)
    assert with_rubric["verdict"] == "DEMONSTRATION_FAIL", json.dumps(with_rubric, indent=1, default=str)
    assert with_rubric["gates"]["G5_query_classes"]["result"] == "FAIL"
    assert with_rubric["gates"]["G5_query_classes"]["per_class"]["QC1"] == "FAIL"
    assert with_rubric["gates"]["G3_authority_classes"]["result"] == "FAIL"


# ---------------------------------------------------------------------------------------------------------------
# GD-10: a symbol-qualified anchor is never matched by an exact line citation inside that symbol.
# ---------------------------------------------------------------------------------------------------------------

def test_gd10_a_line_citation_inside_a_function_matches_that_functions_symbol_anchor(tmp_path):
    fixture_repo = repobuilder.build(tmp_path / "repo")
    # `runtime/src/cx_module.rs`'s `cx_rule` function spans lines 2-4 (compile_repobuilder.py's own CODE_TEXT).
    anchor = {"path": "runtime/src/cx_module.rs", "commit": fixture_repo.c2, "symbol": "cx_rule"}
    inside = {"path": "runtime/src/cx_module.rs", "commit": fixture_repo.c2, "lines": [3, 3]}
    assert g.anchor_matches(inside, anchor, {}, repo=str(fixture_repo.root)) is True
    # a citation to the comment line ABOVE the function (not inside its body) must not match the symbol anchor.
    outside = {"path": "runtime/src/cx_module.rs", "commit": fixture_repo.c2, "lines": [1, 1]}
    assert g.anchor_matches(outside, anchor, {}, repo=str(fixture_repo.root)) is False


# ---------------------------------------------------------------------------------------------------------------
# OBS-BR-05: the 1%-of-corpus packet-bytes check must always apply, over main plus supplementary packets.
# ---------------------------------------------------------------------------------------------------------------

def test_obs_br_05_the_1pct_check_fires_without_a_budget_bytes_argument():
    # the pre-repair `grade()` ALWAYS called `grade_g7(..., budget_bytes=None, ...)`, and `grade_g7` required a
    # truthy `budget_bytes` before ever comparing packet_bytes against 1% of corpus -- so the check never fired,
    # for any run. Calling `grade_g7` exactly as `grade()` now does (no `budget_bytes`) must still catch an
    # oversize packet.
    packets = [{"rendered": "x" * 200_000, "manifest": {}, "task_spec": {}, "meta": {}, "dir": "/nowhere"}]
    result = g.grade_g7(packets, {}, corpus_bytes=1_000_000, budget_bytes=None, reads=None, repo=None)
    assert result["result"] == "FAIL", result
    assert any("OBS-BR-05" in p for p in result["problems"]), result
