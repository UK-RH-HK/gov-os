"""KPI success 4: a question about an id that exists nowhere stops with a named reason and no unrelated items: the
stated gap (RETR-X-02, DEC-900, AR-9) [W2-M296].

``DEC-9999`` is held by no file of the fixture and no record. Asked through ``gov retrieve --json`` as the question
alone (no ``--id``), and with ``--id`` as W1-21 asks it, the bundle:

- names the id among its gaps;
- stops: its reason is one that names the gap (``UNRESOLVED_IDS``, or ``FACET_UNAVAILABLE`` where a facet the bundle
  reports says it could not answer), never ``CLOSURE_COMPLETE``, ``SATURATED`` or ``BUDGET_EXHAUSTED_WITH_GAPS``,
  and it carries no continuation;
- carries no evidence: nothing in the corpus is about the id, so every item would be unrelated. The fixture holds a
  line with the question's other words ("What does ... decide?") on purpose, as the dev tiers do.

The semantic route answers (the stand-in endpoint): a gap is never explained away by a route that is down. A
question naming an id that exists is answered as before, with no gap for that id.
"""

from __future__ import annotations

import pytest

import w2_13_support as support

pytestmark = pytest.mark.needs("git", "gitleaks", "sqlite_vec")

ALONE = {"the id alone": support.GAP_QUESTIONS[0], "a question naming the id": support.GAP_QUESTIONS[1]}


def stated_gap(bundle, where):
    assert support.MISSING_ID in support.gap_names(bundle), \
        f"{where}: {support.MISSING_ID} is not named among the gaps: {bundle[support.K_GAPS]!r}"
    reason = bundle[support.K_REASON]
    assert reason not in support.NOT_A_STATED_GAP and reason in support.STATED_GAP, \
        f"{where}: the bundle stops with {reason}, not a reason that names the gap ({support.STATED_GAP})"
    assert bundle[support.K_CONTINUATION] is None, f"{where}: the bundle does not stop: it carries a continuation"
    assert bundle[support.K_EVIDENCE] == [], \
        f"{where}: {len(bundle[support.K_EVIDENCE])} unrelated items are cited: {support.cited_paths(bundle)[:10]}"


def test_premise_no_file_of_the_fixture_holds_the_missing_id(base):
    assert not any(support.MISSING_ID in text for text in support.corpus().values())
    assert support.MISSING_ID not in (base / support.PATH_MAP_REL).read_text(encoding="utf-8")


@pytest.mark.parametrize("asked", list(ALONE), ids=list(ALONE))
def test_an_id_that_exists_nowhere_asked_alone_is_a_stated_gap(box, built, ollama, asked):
    bundle = support.check_bundle(box.retrieve(built, ALONE[asked], host=ollama.host).result(), root=built)
    assert bundle[support.K_FACETS][support.ROUTE_SEMANTIC]["available"] is True, "premise: the semantic route is down"
    stated_gap(bundle, f"{ALONE[asked]!r} with no --id")


def test_an_id_that_exists_nowhere_given_with_its_id_is_a_stated_gap(box, built, ollama):
    question = support.GAP_QUESTIONS[1]
    bundle = support.check_bundle(box.retrieve(built, question, "--id", support.MISSING_ID, host=ollama.host).result(),
                                  root=built)
    stated_gap(bundle, f"{question!r} --id {support.MISSING_ID}")


@pytest.mark.parametrize("question", [support.RECORD_ID, f"What does {support.RECORD_ID} decide?"],
                         ids=["the id alone", "a question naming the id"])
def test_a_question_naming_an_id_that_exists_is_answered_with_no_gap_for_it(box, built, ollama, question):
    bundle = support.check_bundle(box.retrieve(built, question, host=ollama.host).result(), root=built)
    assert support.RECORD_FILE in support.cited_paths(bundle), \
        f"{question!r}: the record {support.RECORD_ID} ({support.RECORD_FILE}) is not cited: {support.cited_paths(bundle)}"
    assert support.RECORD_ID not in support.gap_names(bundle), f"{question!r}: a false gap: {bundle[support.K_GAPS]!r}"
    assert bundle[support.K_REASON] != support.UNRESOLVED_IDS, f"{question!r}: stops with UNRESOLVED_IDS"


@pytest.mark.local_only
@pytest.mark.parametrize("programme", sorted(support.TIERS))
def test_retr_x_02_on_a_dev_tier_asked_with_no_id_is_a_stated_gap(box, ollama, tmp_path_factory, programme):
    """W2-M296 where it was seen: each dev tier, rebuilt through the stand-in endpoint (no model runs), asked
    RETR-X-02's question with no ``--id``."""
    tier = support.TIERS[programme]
    root = support.clone_tier(tier, tmp_path_factory.mktemp(f"w2-13-gap-{tier}") / tier)
    if root is None:
        pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
    box.rebuild(root, host=ollama.host)
    question = support.GAP_QUESTIONS[1]
    bundle = support.check_bundle(box.retrieve(root, question, "--radius", "1", host=ollama.host).result(), root=root)
    stated_gap(bundle, f"{tier}: {question!r} with no --id")
