"""KPI success 1 and 2: each register entry is a record of its own, with its own sha256 over its own span, and a
decision id resolves to its entry, not to the register [AR-1, F-M5].

"The store loads each ``### DEC-nnn`` entry of the register as a record of its own, with its own sha256 over its
own span; two decisions never share a hash." / "A decision id resolves to its entry, not to the register."

Reading R1 (README): the store's record of an entry carries ``span``, the entry's own text in the register from its
heading (register-entry.schema.json: "the entry's own text in the register, from its heading to the next"), and
``content_hash``, the sha256 in lower-case hex of that text's UTF-8 bytes (DEC-012's computed ``content_hash``;
W2-L031). Where an entry ends before the next heading (blank lines, a part heading, a version table) is the
store's; the cases hold only that the span starts at the entry's heading, holds the entry's own lines, is text of
the register, and does not reach into the next entry.
"""

from __future__ import annotations

import pytest

import w2_03_support as support

REGISTER = """\
# Decisions

## 1. The first part

### DEC-101 — The parser reads both forms
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER
- **Decision:** The parser reads both forms of a record.

### DEC-102: The writer keeps its order
- **Status:** PROPOSED · **Basis:** a report
- **Decision:** The writer keeps the order it was given.
- **Why:** A second line of the entry.

### DEC-103 - Same words
- **Status:** ACCEPTED (owner, 2026-10-02)
- **Decision:** These words are the same in two entries.

### DEC-104 - Same words
- **Status:** ACCEPTED (owner, 2026-10-02)
- **Decision:** These words are the same in two entries.

## 2. The second part

### DEC-105 — The last decision
- **Status:** SUPERSEDED by DEC-106 · **Basis:** OWNER
- **Decision:** The last entry of the file.

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-02 | DEC-101 to DEC-105. |
"""

# id -> (heading line, lines of its own the span must hold)
ENTRIES = {
    "DEC-101": ("### DEC-101 — The parser reads both forms",
                ["- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER",
                 "- **Decision:** The parser reads both forms of a record."]),
    "DEC-102": ("### DEC-102: The writer keeps its order",
                ["- **Status:** PROPOSED · **Basis:** a report",
                 "- **Decision:** The writer keeps the order it was given.",
                 "- **Why:** A second line of the entry."]),
    "DEC-103": ("### DEC-103 - Same words",
                ["- **Status:** ACCEPTED (owner, 2026-10-02)",
                 "- **Decision:** These words are the same in two entries."]),
    "DEC-104": ("### DEC-104 - Same words",
                ["- **Status:** ACCEPTED (owner, 2026-10-02)",
                 "- **Decision:** These words are the same in two entries."]),
    "DEC-105": ("### DEC-105 — The last decision",
                ["- **Status:** SUPERSEDED by DEC-106 · **Basis:** OWNER",
                 "- **Decision:** The last entry of the file."]),
}
ORDER = list(ENTRIES)


@pytest.fixture(scope="module")
def loaded(api, tmp_path_factory):
    project = support.project_with_register(tmp_path_factory.mktemp("w2-03-entries") / "project", REGISTER)
    summary, records = api.load_and_records(project.root)
    return summary, support.register_records(records)


def _hash_and_span(record_id, record):
    assert support.HASH_KEY in record and support.SPAN_KEY in record, \
        f"{record_id}'s record carries no `{support.HASH_KEY}` and `{support.SPAN_KEY}`: keys {sorted(record)}"
    return record[support.HASH_KEY], record[support.SPAN_KEY]


# ---- KPI success 1

def test_each_entry_is_one_record_of_its_own(loaded):
    """Five entries, five records placed in the register file, nothing of the register invalid. Green where the
    store already loads entries (W1-10's follow-up), so the cases below are about the hash and the span."""
    summary, entries = loaded
    assert sorted(entries) == sorted(ENTRIES), f"the register's records are {sorted(entries)}"
    assert support.invalid_naming(summary, "DEC-101") == [], summary["invalid"]


@pytest.mark.parametrize("record_id", ORDER)
def test_each_entry_carries_the_sha256_of_its_own_span(loaded, record_id):
    """``content_hash`` is a sha256 in hex, and it is the sha256 of the record's ``span``."""
    _, entries = loaded
    content_hash, span = _hash_and_span(record_id, entries[record_id])
    assert support.is_sha256(content_hash), f"{record_id}'s {support.HASH_KEY} is no sha256: {content_hash!r}"
    assert isinstance(span, str), f"{record_id}'s {support.SPAN_KEY} is not the entry's text: {span!r}"
    assert content_hash == support.sha256_hex(span), \
        f"{record_id}'s {support.HASH_KEY} is not the sha256 of its own span"


@pytest.mark.parametrize("record_id", ORDER)
def test_the_span_is_the_entrys_own_text_in_the_register(loaded, record_id):
    """The span starts at the entry's heading, holds the entry's own lines, is text of the register as written,
    and holds no other entry's heading."""
    _, entries = loaded
    heading, own_lines = ENTRIES[record_id]
    _, span = _hash_and_span(record_id, entries[record_id])
    assert isinstance(span, str) and span.startswith(heading), \
        f"{record_id}'s span does not start at its heading: {span!r}"
    missing = [line for line in own_lines if line not in span.split("\n")]
    assert not missing, f"{record_id}'s span lacks lines of its own entry: {missing}"
    assert span in REGISTER, f"{record_id}'s span is not text of the register as written: {span!r}"
    others = [other for other, (line, _) in ENTRIES.items() if other != record_id and line in span]
    assert not others, f"{record_id}'s span reaches into the entries of {others}"


def test_two_decisions_never_share_a_hash(loaded):
    """Five entries, five hashes; DEC-103 and DEC-104 differ only in their ids."""
    _, entries = loaded
    hashes = {record_id: _hash_and_span(record_id, entries[record_id])[0] for record_id in ORDER}
    assert len(set(hashes.values())) == len(hashes), f"two decisions share a hash: {hashes}"


def test_every_entry_of_this_repositorys_register_has_its_own_hash(api, tmp_path):
    """The worked example (DEC-746 item 5): the text of this checkout's ``docs/DECISION_REGISTER.md``, read in
    place and committed into a temporary project as its named register. Every entry the store loads from it
    carries the sha256 of its own span, the span is text of the register starting at the entry's heading, and no
    two entries share a hash."""
    text = support.OWN_REGISTER.read_text(encoding="utf-8")
    project = support.project_with_register(tmp_path / "project", text)
    _, records = api.load_and_records(project.root)
    entries = support.register_records(records)
    assert len(entries) > 500, f"the fixture is wrong: {len(entries)} entries loaded from the register"
    wrong, hashes = [], {}
    for record_id, record in sorted(entries.items()):
        content_hash, span = record.get(support.HASH_KEY), record.get(support.SPAN_KEY)
        if not (isinstance(span, str) and support.is_sha256(content_hash)
                and content_hash == support.sha256_hex(span)
                and span.startswith(f"### {record_id}") and span in text):
            wrong.append(record_id)
        hashes.setdefault(content_hash, []).append(record_id)
    assert not wrong, f"{len(wrong)} entries without the sha256 of a span of their own, e.g. {wrong[:10]}"
    shared = [ids for ids in hashes.values() if len(ids) > 1]
    assert not shared, f"entries share a hash: {shared[:5]}"


# ---- KPI success 2

def test_a_decision_id_resolves_to_its_entry_not_to_the_register(loaded):
    """What the store answers for DEC-102 is its entry: a span shorter than the register, and a hash that is not
    the register file's."""
    _, entries = loaded
    register_hash = support.sha256_hex(REGISTER)
    content_hash, span = _hash_and_span("DEC-102", entries["DEC-102"])
    assert content_hash != register_hash, "DEC-102 resolves to the register file's hash, not to its entry's"
    assert isinstance(span, str) and len(span) < len(REGISTER) // 2, \
        f"DEC-102 resolves to the register, not to its entry: a span of {len(span or '')} characters"


def test_the_decision_citations_check_resolves_a_cited_id_to_its_entry(tmp_path):
    """The check counts DEC-101, an entry of the named register, as recorded: a commit that cites it and DEC-900,
    which no entry records, is flagged for DEC-900 alone. Green where the check reads the register (W1-26); the
    cases of ``test_w2_03_not_records.py`` hold what does not resolve."""
    project = support.project_with_register(tmp_path / "project", REGISTER)
    commit = project.commit("Change the parser (DEC-101, DEC-900)")
    support.assert_flagged(support.run_citations(project.root), [(commit, "DEC-900")])
