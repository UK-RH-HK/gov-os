"""W2-107: ``gov.secrets.scan_counts()`` says how many texts of each kind were scanned and how many were remembered.

KPI success 7's testable part (the rebuild's record says how many contents and names were scanned and how many were
answered from the cache; the record's line and the seconds before and after are measured by the lead) and failure 6's
(a second unchanged pass that scans everything again). ``scanned`` counts texts given to gitleaks, ``remembered`` texts
answered from the cache; a caller takes the difference around its own work. The counts agree with the stand-in's.
"""

from __future__ import annotations

import w2_107_support as support
from gov import secrets

pytestmark = support.needs_tools

FILES = {f"docs/page-{number}.md": f"W2-107: page {number}, ordinary text.\n" for number in range(3)}
NAMES = ["docs/an-ordinary-name.md", "notes/another-ordinary-name.txt"]
KINDS = ("content", "path")


def difference(before, after):
    return {kind: {key: after[kind][key] - before[kind][key] for key in ("scanned", "remembered")} for kind in KINDS}


def measured(engine, work):
    """``work()``'s result, the counts' difference around it, and the stand-in's scan calls during it."""
    before = secrets.scan_counts()
    result, calls = support.counted(engine, work)
    return result, difference(before, secrets.scan_counts()), calls


def tally(content, path):
    return {"content": dict(zip(("scanned", "remembered"), content)), "path": dict(zip(("scanned", "remembered"), path))}


def test_the_counts_have_their_form_and_each_call_gives_a_fresh_dict():
    first = secrets.scan_counts()
    assert set(first) == set(KINDS), "one entry a kind: content and path"
    for kind in KINDS:
        assert set(first[kind]) == {"scanned", "remembered"}
        assert all(isinstance(value, int) and value >= 0 for value in first[kind].values())
    first["content"]["scanned"] = -1
    first["path"] = None
    second = secrets.scan_counts()
    assert second is not first and second["content"]["scanned"] >= 0 and isinstance(second["path"], dict), \
        "a caller's change to one result is not seen in the next"


def test_the_counts_show_scanned_and_remembered_per_kind_and_agree_with_the_gitleaks_calls(
        project, engine, cache, per_text, monkeypatch):
    rels = support.put(project, FILES)
    secret = support.put(project, {"docs/planted.md": f"The value is {support.planted()} today.\n"})
    bad_name = f"docs/{support.planted()}/page.md"

    def judge(paths, names):
        return secrets.indexable(project, paths), [secrets.path_holds_secret(project, name) for name in names]

    _, counts, calls = measured(engine, lambda: judge(rels, NAMES))
    assert counts == tally((3, 0), (2, 0)) and calls == 5 * per_text, "the first pass scans every text"
    _, counts, calls = measured(engine, lambda: judge(rels, NAMES))
    assert counts == tally((0, 3), (0, 2)) and calls == 0, "the second pass remembers every text and scans none"
    support.write(project / rels[0], "W2-107: page 0, changed.\n")
    _, counts, calls = measured(engine, lambda: judge(rels + secret, NAMES + [bad_name]))
    assert counts == tally((2, 2), (1, 2)), "the changed file and the secrets are scanned, the rest remembered"
    findings = support.uncached(engine, lambda: judge(secret, [bad_name]))[1]
    assert calls == per_text + findings, "the stand-in saw the scans counted: the changed file's and the secrets'"
    monkeypatch.setenv("GOV_SECRETS_FULL_SCAN", "1")
    _, counts, calls = measured(engine, lambda: judge(rels, NAMES))
    assert counts == tally((3, 0), (2, 0)) and calls == 5 * per_text, "a full scan remembers nothing it answers"
    monkeypatch.delenv("GOV_SECRETS_FULL_SCAN")
    with support.cache_off():
        _, counts, calls = measured(engine, lambda: judge(rels, NAMES))
    assert counts == tally((3, 0), (2, 0)) and calls == 5 * per_text, "with no cache, every text counts as scanned"
