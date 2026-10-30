"""W2-69, added after implementation from the review (DEC-136), behaviour 2: a full-text index's stored terms raise
no chance red.

KPI 2 (W2-M404), success: "An embedded fragment of a longer identifier is not
flagged: a token-shaped string inside a word, placed at every offset relative to
wherever the check or gitleaks begins a read, is not a finding, for every rule
with a leading word boundary." Failure: "A word-internal fragment flagged at a
read edge (the chance red of W2-62's queue, 2026-10-22)."

The setting: a full-text index built with the lexical index's own tokenizer
(``porter unicode61 tokenchars '_'``: an underscore stays inside a word). It holds
identifiers, words that keep underscores inside them and hold a token-shaped
string inside the word, after word characters; and, for each, a neighbouring term
that sorts just before it and shares its whole head up to that string. The index
stores the identifier as that string after the shared prefix: its stored text
begins inside the word. Such an index is no finding, as written (several segments)
and after the rebuild's compaction (optimised, then vacuumed), and through
``gov rebuild --json`` in a project whose sources hold such identifiers. A real
token at a word boundary in such an index's documents is still found (the control).

The project's four rules, each with a string that is a finding alone and none
inside its word (checked first by the real gitleaks). The index stores its terms
in lower case: the digit and lower-case strings as written; the upper-case
string's stored form is a ``gov-token-lower`` finding alone; the canary's stored
form is a finding by no rule (gov-canary asks for upper case), so its index is no
chance red today either and its case guards the change.

Today the check is red on the index: its stored text begins inside the word.
"""

from __future__ import annotations

import importlib.util

import pytest

import w2_69_review_support as review
import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
RULES = ("gov-canary", "gov-token-digit", "gov-token-lower", "gov-token-upper")
STATES = ("as-written", "optimised-and-vacuumed")
STORED_FINDING = {"gov-token-digit": "gov-token-digit", "gov-token-lower": "gov-token-lower",
                  "gov-token-upper": "gov-token-lower", "gov-canary": None}

needs_vectors = pytest.mark.skipif(importlib.util.find_spec("sqlite_vec") is None,
                                   reason="sqlite_vec is not installed: the semantic index cannot be built")


@pytest.mark.parametrize("rule", RULES)
def test_premise_the_string_is_a_finding_alone_and_none_inside_its_identifier(rule):
    sep, token = review.review_k2_strings()[rule]
    for name, config in support.rule_sets().items():
        assert rule in support.gitleaks_finds(f" {token} \n", config), f"premise: {rule}'s string alone ({name})"
        assert support.gitleaks_finds(f" zqrv000{sep}a7 zqrv000{sep}{token} \n", config) == [], (
            f"premise: {rule}'s identifier and its neighbour are a finding ({name})")
        stored = support.gitleaks_finds(f" {token.lower()} \n", config)
        expected = STORED_FINDING[rule]
        assert (expected in stored) if expected else stored == [], (
            f"premise: the stored (lower-case) form of {rule}'s string alone: {stored} ({name})")


def _stores(project, state, extra=None):
    """One index per rule under ``.gov-runtime/``; returns their relative paths."""
    rels = {}
    for rule in RULES:
        rel = f"{R}/fts/{rule}.db"
        documents = [extra(rule)] if extra else []
        path = review.fts_identifier_store(project / rel, rule, documents)
        if state == "optimised-and-vacuumed":
            review.optimise_and_vacuum(path)
            assert support.free_pages(path) == 0, "premise: the store is compacted"
        _sep, token = review.review_k2_strings()[rule]
        assert review.stored_as_a_suffix(path.read_bytes(), token), (
            f"premise: {rule}'s index stores the identifier as its string after the shared prefix ({state})")
        rels[rule] = rel
    return rels


@pytest.mark.parametrize("state", STATES)
def test_a_full_text_index_storing_identifiers_after_a_shared_prefix_is_no_finding(sandbox, project, state):
    rels = _stores(project, state)
    run = support.run_check(sandbox, project)
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    tokens = [token for _sep, token in review.review_k2_strings().values()]
    assert not any(t in run.stdout + run.stderr or t.lower() in run.stdout + run.stderr for t in tokens), (
        "the check printed a token-shaped string")
    named = [rule for rule, rel in rels.items() if run.names(rel)]
    assert not named, (
        f"{state}: the check flagged the full-text index of {named}: it holds token-shaped strings only inside "
        f"identifiers (stored after the prefix a neighbouring term shares)\n{run.describe(800)}")
    assert run.returncode == 0, f"{state}: the check is not green and names no index\n{run.describe()}"


def _real_token(rule):
    """A document holding the rule's string alone, at a word boundary: a real token."""
    _sep, token = review.review_k2_strings()[rule]
    return f"{support.prose(120, 'control')} the value {token} stands alone here\n"


@pytest.mark.parametrize("state", STATES)
def test_control_a_real_token_at_a_word_boundary_in_such_an_index_is_found(sandbox, project, state):
    rels = _stores(project, state, extra=_real_token)
    run = support.run_check(sandbox, project)
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    tokens = [token for _sep, token in review.review_k2_strings().values()]
    assert not any(t in run.stdout + run.stderr for t in tokens), "the check printed a token"
    missed = [rule for rule, rel in rels.items() if not run.names(rel)]
    assert not missed, (f"{state}: a real token at a word boundary in a full-text index's documents was not found: "
                        f"{missed}\n{run.describe(800)}")
    assert run.returncode == support.FINDING_EXIT


@pytest.fixture()
def embedder():
    stand_in = support.EmbedderStandIn()
    yield stand_in
    stand_in.close()


@needs_vectors
def test_a_rebuilt_lexical_index_storing_identifiers_after_a_shared_prefix_is_no_finding(sandbox, embedder):
    """``gov rebuild --json`` (full, the semantic index against the stand-in embedder; the code-graph tool hidden, so
    no daemon starts) in a project whose sources hold the identifiers and their neighbours; then the check."""
    files = {f"docs/ids-{rule}.md": f"# {rule}\n\n" + "".join(review.identifier_lines(rule, 120)) for rule in RULES}
    files["docs/intro.md"] = "# Intro\n\n" + support.prose(2000, "intro")
    project = support.make_rebuild_project(sandbox, files)
    env = support.rebuild_environment(sandbox, embedder, with_code_tool=False)
    run = support.rebuild(project, env)
    assert support.store_status(run, "lexical") == "recreated", f"premise: the lexical index\n{run.describe()}"
    data = b"".join(path.read_bytes() for path in support.sqlite_files(project / R))
    stored = {rule: review.stored_as_a_suffix(data, review.review_k2_strings()[rule][1]) for rule in RULES}
    assert all(stored.values()), (
        f"premise: the rebuilt index stores each identifier as its string after the shared prefix: {stored}")
    check = support.run_check(sandbox, project, env=support.base_environment(sandbox))
    assert check.returncode is not None, f"the check did not end within its declared limit\n{check.describe()}"
    tokens = [token for _sep, token in review.review_k2_strings().values()]
    assert not any(t in check.stdout + check.stderr or t.lower() in check.stdout + check.stderr for t in tokens), (
        "the check printed a token-shaped string")
    assert check.returncode == 0 and not check.stdout.strip(), (
        f"after a full rebuild of sources holding token-shaped strings only inside identifiers, the check is red on "
        f"the stores the rebuild wrote (the lexical index stores each identifier after the prefix its neighbour "
        f"shares)\n{check.describe(800)}")
