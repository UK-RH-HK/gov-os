"""KPI failure 1: RETR-A-04's bundle is unchanged (citations, three parent expansions, stopping reason).

Two parts:

- **On the fixture, no model:** the bundle keeps its form (W1-21's keys, an evidence item's keys, an expansion's
  keys, the fixed list of stopping reasons, each citation's sha256 and text against the bytes), and a child hit in a
  long section is still cited as its parent and named as an expansion (DEC-091, W1-21's case), now that the lexical
  route ranks. These pass on the base: they guard against a regression.
- **On the a-dev tier, with the real models (``needs("ollama", "reranker")``, ``local_only``):** RETR-A-04 as the
  Wave 1 exit run asked it (``gov retrieve "Which files implement the leapfrog integrator?" --radius 1``; EXIT-REPORT
  "Retrieval"): both implementation files cited by id and sha256, at least three named parent expansions, and the
  stopping reason ``BUDGET_EXHAUSTED_WITH_GAPS`` with its gaps named and a continuation, as recorded then. The exact
  count of expansions depends on which chunks the run cites, so the case holds the recorded three as a floor.
"""

from __future__ import annotations

import pytest

import w2_13_support as support

pytestmark = pytest.mark.needs("git", "gitleaks", "sqlite_vec")


def test_the_bundle_keeps_its_form(box, built, ollama):
    bundle = box.retrieve(built, support.EXPANSION_PHRASE, "--bundle-budget", str(support.BUDGET_LARGE),
                          host=ollama.host).result()
    support.check_bundle(bundle, root=built)
    assert bundle[support.K_EVIDENCE] and bundle[support.K_EXPANSIONS], "premise: nothing is cited or expanded"
    assert isinstance(bundle[support.K_MERGE].get("reranked"), bool)
    for part in ("rounds", "bundle"):
        assert isinstance(bundle[support.K_BUDGET].get(part), dict), f"`budget.{part}` is lost: {bundle['budget']!r}"


def test_a_child_hit_is_still_cited_as_its_parent_and_named_as_an_expansion(box, built, ollama):
    hits = box.search(built, support.EXPANSION_PHRASE)["hits"]
    chunk_ids = {hit["chunk_id"] for hit in hits if support.EXPANSION_PHRASE in hit["text"]}
    assert len(chunk_ids) == 1 and all(hit["path"] == support.MANUAL for hit in hits if hit["chunk_id"] in chunk_ids), \
        f"premise: the phrase is not in one chunk of {support.MANUAL}: {hits!r}"
    chunk_id = chunk_ids.pop()
    chunk = next(record for record in box.run([(support.LEXICAL, "chunks", [support.path_arg(built)],
                                                {"path": support.MANUAL})]).value() if record["chunk_id"] == chunk_id)
    parent = box.run([(support.LEXICAL, "parent", [support.path_arg(built), chunk["parent_id"]], {})]).value()
    assert parent["kind"] == "section" and (parent["start_line"], parent["end_line"]) != \
        (chunk["start_line"], chunk["end_line"]), f"premise: the chunk is not a child of a longer section: {parent!r}"
    bundle = support.check_bundle(box.retrieve(built, support.EXPANSION_PHRASE, "--bundle-budget",
                                               str(support.BUDGET_LARGE), host=ollama.host).result(), root=built)
    items = [item for item in bundle[support.K_EVIDENCE] if item["chunk_id"] == chunk_id]
    assert len(items) == 1, f"the chunk that holds the phrase is cited {len(items)} times"
    assert (items[0]["path"], items[0]["start_line"], items[0]["end_line"]) == \
        (support.MANUAL, parent["start_line"], parent["end_line"]), \
        f"the hit is not cited as its parent section (lines {parent['start_line']}-{parent['end_line']}): " \
        f"{items[0]['start_line']}-{items[0]['end_line']}"
    named = [entry for entry in bundle[support.K_EXPANSIONS] if entry["chunk_id"] == chunk_id]
    assert len(named) == 1 and all(named[0][key] == parent[key] for key in ("parent_id", "path", "start_line",
                                                                            "end_line")), \
        f"the expansion is not named with its parent {parent!r}: {named!r}"


@pytest.mark.local_only
@pytest.mark.needs("ollama", "reranker")
def test_retr_a_04_cites_both_files_with_three_named_expansions_and_its_stopping_reason(box, real_tiers):
    root = real_tiers["A"]
    run = box.retrieve(root, support.RETR_A_04_QUESTION, "--radius", "1", env=box.real_env(),
                       timeout=support.MEASURE_TIMEOUT_S)
    bundle = support.check_bundle(run.result(), root=root)
    missing = set(support.RETR_A_04_EXPECTED) - set(support.cited_paths(bundle))
    assert not missing, f"RETR-A-04 does not cite {sorted(missing)}; cited: {support.cited_paths(bundle)[:12]}"
    expansions = bundle[support.K_EXPANSIONS]
    assert len(expansions) >= support.RETR_A_04_EXPANSIONS, \
        f"RETR-A-04 names {len(expansions)} parent expansions, fewer than the {support.RETR_A_04_EXPANSIONS} recorded"
    for entry in expansions:
        assert entry["parent_id"] and entry["path"] and 1 <= entry["start_line"] <= entry["end_line"], \
            f"an expansion does not name its parent: {entry!r}"
    assert bundle[support.K_REASON] == support.BUDGET_EXHAUSTED, \
        f"RETR-A-04 stops with {bundle[support.K_REASON]}, not BUDGET_EXHAUSTED_WITH_GAPS as recorded"
    assert bundle[support.K_GAPS] and bundle[support.K_CONTINUATION], "the budget's gaps or its continuation are lost"
