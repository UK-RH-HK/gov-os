"""W2-107: with ``GOV_SECRETS_FULL_SCAN`` set, nothing is read from the cache and every clean verdict is written fresh.

KPI success 6 (a full scan reads nothing from the cache, and refreshes it, when ``GOV_SECRETS_FULL_SCAN=1`` is set; any
value other than empty or ``0`` counts the same); failure 5 (the full-scan setting answered from the cache).
"""

from __future__ import annotations

import pytest

import w2_107_support as support
from gov import secrets

pytestmark = support.needs_tools

FILES = {
    "docs/alpha.md": "W2-107: the alpha page, ordinary text.\n",
    "docs/beta.md": "W2-107: the beta page, ordinary text.\n",
}
NAME = "docs/an-ordinary-name.md"


def judge(root, rels):
    return secrets.indexable(root, rels), secrets.path_holds_secret(root, NAME)


@pytest.mark.parametrize("value", ["1", "yes"])
def test_a_full_scan_reads_nothing_from_the_cache_and_refreshes_it(project, engine, cache, per_text, monkeypatch, value):
    rels = support.put(project, FILES)
    texts = len(rels) + 1
    monkeypatch.setenv("GOV_SECRETS_FULL_SCAN", value)
    for label in ("a full scan on an empty cache", "a full scan of texts remembered"):
        verdicts, calls = support.counted(engine, lambda: judge(project, rels))
        assert verdicts == (rels, False) and calls == texts * per_text, f"{label}: every text is scanned"
    monkeypatch.delenv("GOV_SECRETS_FULL_SCAN")
    verdicts, calls = support.counted(engine, lambda: judge(project, rels))
    assert verdicts == (rels, False) and calls == 0, "after it, an ordinary call is answered from what it wrote"


@pytest.mark.parametrize("value", ["0", ""])
def test_the_setting_empty_or_zero_is_an_ordinary_call(project, engine, cache, per_text, monkeypatch, value):
    rels = support.put(project, FILES)
    judge(project, rels)
    monkeypatch.setenv("GOV_SECRETS_FULL_SCAN", value)
    verdicts, calls = support.counted(engine, lambda: judge(project, rels))
    assert verdicts == (rels, False) and calls == 0, f"{value!r} is no full scan: the call is answered from the cache"
