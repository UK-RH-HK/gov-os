"""W2-107: only a clean verdict is remembered; a finding of any kind is scanned again on every call.

KPI success 2 (no finding is remembered, row W2-L423's exempt commit hash included; a secret's content is never answered
clean from the cache); failure 1 (a secret's content answered clean from the cache, or a finding remembered). Each case
also judges a clean neighbour, which is answered from the cache, so the cache is shown in use while the finding is not.
"""

from __future__ import annotations

import w2_107_support as support
from gov import secrets

pytestmark = support.needs_tools

CALLS = 3  # each case judges the same texts on three calls


def test_a_file_holding_the_secret_is_dropped_and_scanned_on_every_call(project, engine, cache, per_text):
    secret = support.put(project, {"docs/planted.md": f"The value is {support.planted()} today.\n"})
    clean = support.put(project, {"docs/neighbour.md": "W2-107: an ordinary neighbour.\n"})
    kept, alone = support.uncached(engine, lambda: secrets.indexable(project, secret))
    assert kept == [] and alone >= 1, "premise: gitleaks finds the planted secret"
    for number in range(CALLS):
        kept, calls = support.counted(engine, lambda: secrets.indexable(project, secret + clean))
        assert kept == clean, f"call {number + 1}: the file holding the secret is dropped"
        assert calls == alone + (per_text if number == 0 else 0), \
            f"call {number + 1}: the secret is scanned in full again, the clean neighbour only the first time"


def test_a_path_whose_name_holds_the_secret_is_judged_and_scanned_on_every_call(project, engine, cache, per_text):
    names = [f"docs/{support.planted()}/page.md", f"notes/{support.planted()}.txt"]
    clean = "docs/an-ordinary-name.md"
    verdicts, alone = support.uncached(engine, lambda: [secrets.path_holds_secret(project, name) for name in names])
    assert verdicts == [True, True] and alone >= 2, "premise: gitleaks finds the secret in each name"
    for number in range(CALLS):
        verdicts, calls = support.counted(
            engine, lambda: [secrets.path_holds_secret(project, name) for name in [*names, clean]])
        assert verdicts == [True, True, False], f"call {number + 1}: each name holding the secret holds a secret"
        assert calls == alone + (per_text if number == 0 else 0), \
            f"call {number + 1}: the names holding the secret are scanned again, the clean one only the first time"


def test_a_commit_of_the_repository_after_the_rules_keyword_is_let_through_and_scanned_on_every_call(
        tmp_path, engine, cache, per_text):
    """Row W2-L423's rule matches a bare 40-hex string after its keyword; the filter exempts a match that is a commit
    of the repository (DEC-911 item 4). That depends on the repository, so it is judged afresh on every call."""
    root = tmp_path / "repository"
    commit = support.make_repository(root)
    exempt = support.put(root, {"docs/review.md": support.review_line(commit)})
    other = support.put(root, {"docs/other.md": support.review_line(support.hex_of("no object"))})
    clean = support.put(root, {"docs/neighbour.md": "W2-107: an ordinary neighbour.\n"})
    kept, dropped = support.uncached(engine, lambda: secrets.indexable(root, other))
    assert kept == [] and dropped >= 1, "premise: the rule finds a 40-hex string after its keyword, not a commit"
    kept, alone = support.uncached(engine, lambda: secrets.indexable(root, exempt))
    assert kept == exempt and alone >= 1, "premise: a commit of the repository there is exempt and let through"
    for number in range(CALLS):
        kept, calls = support.counted(engine, lambda: secrets.indexable(root, exempt + other + clean))
        assert kept == exempt + clean, f"call {number + 1}: the commit is let through, the other string dropped"
        assert calls == alone + dropped + (per_text if number == 0 else 0), \
            f"call {number + 1}: the exempt match and the finding are scanned again, the clean neighbour only once"
