"""The owner's answers to the CIT-P (DEC-741, 2026-10-17), on the public documents.

DEC-741 approves the CIT-P (apply now) and answers its questions as the CIT-P
recommended.  These tests add what the answers fix and the earlier tests could
not know:

- A (a1): a split item keeps its id for the lite Wave 2 part; new ids carry the
  Wave 3 rest (CAP-43.d, CAP-44.k, CAP-44.l); covers by wave W1 149 / W2 20 /
  W3 38 / NONE 7.
- B (i): lite CAP-43.b is the manifest and the file hashes only.
- C: the tests hold under both outcomes (the ten conditions listed in CAP-44.h,
  each marked W2 or W3; or the fallback, the lite conditions in the Contract's
  own terms and the ten with CAP-44.l).
- D (ii): CAP-45.a's Wave 2 wording (the signed tag with CAP-02.c in Wave 3).
- F (i): the three verdict rules; only the owner accepts an exception.
- G (i): three operational lite conditions.
- H (i): W2-52 (DAEO-siiz) builds the lite A7 and A10 stage records.
- K (1): every capability record cites version 4.2 (K (2), the rewritten
  records, is in ``test_w2_49_capability_records.py``, so it can be dropped
  alone).
- Row W2-L343: both Contract files state status ACCEPTED.

Every Contract test runs on both files and first checks the version, so none
passes on the unchanged 4.1 text by accident.

Revised for Contract 4.3 (W2-140; DEC-1093 (1), the approved W2-27-CIT-P):
the counts (covers W2 19 / W3 39; capabilities W2 6 / W3 12), D (ii) (CAP-45.a
is W3; its authenticated source names the signed tag and the manifest and file
hashes; no Wave 2 clause left), K (1) (the version in force, once), and
CAP-45 itself at W3. Each revised function carries its Rewrite-Reason.
"""

from __future__ import annotations

import re
import subprocess
from collections import Counter

import pytest

from w2_49_support import (
    BASE_COMMIT,
    CAP_43B_REST,
    CAPABILITIES,
    CIT_E,
    CIT_P,
    CONTRACT_MD,
    CONTRACT_YAML,
    MOVED_ITEMS,
    NEW_SPLIT_IDS,
    ROOT,
    _flatten,
    base_yaml_model,
    cap_wave_note,
    clauses,
    clean,
    contract_status,
    current_model,
    describe,
    gate,
    has,
    is_v42_or_later,
    load_yaml_text,
    md_model,
    read_base,
    read_doc,
    require_v42,
    together,
    verdict,
    wave_token,
)

SOURCES = ["yaml", "markdown"]

W2 = wave_token("W2")
W3 = wave_token("W3")


@pytest.fixture(scope="module", params=SOURCES)
def model(request):
    return current_model(request.param)


def _base(source: str):
    if source == "yaml":
        return base_yaml_model()
    return md_model(read_base(CONTRACT_MD))


def _item(model, cap_id):
    item = model.by_id().get(cap_id)
    assert item is not None, f"{model.source}: {cap_id} is missing\n{describe(model, cap_id.rsplit('.', 1)[0])}"
    return item


# --------------------------------------------------------------------------
# A (a1): the split form, the new ids and their waves


# The part each new id names (DEC-741 A): CAP-43.d the nine other release
# contents of CAP-43.b; CAP-44.k A9, A11, and A7 and A10 beyond their lite form;
# CAP-44.l the verdict with the ten ADOPTED_HEALTHY conditions.
NEW_ID_PARTS = {
    "CAP-43.d": dict(CAP_43B_REST),
    "CAP-44.k": {"A9": gate("A9"), "A11": gate("A11"), "A7": gate("A7"), "A10": gate("A10")},
    "CAP-44.l": {"the verdict": r"verdict|ADOPTED_HEALTHY", "the ten conditions": r"\bten\b[^;]*condition"},
}


@pytest.mark.parametrize("cap_id", NEW_SPLIT_IDS)
def test_new_split_id_exists_in_wave_3_naming_its_part(model, cap_id):
    """A (a1): CAP-43.d, CAP-44.k and CAP-44.l carry the Wave 3 rest of the split items."""
    require_v42(model)
    item = _item(model, cap_id)
    parent = cap_id.rsplit(".", 1)[0]
    assert item.cap == parent, f"{model.source}: {cap_id} sits under {item.cap}, not {parent}"
    assert item.wave == "W3", f"{model.source}: {cap_id} is in {item.wave}, not W3"
    missing = [name for name, pattern in NEW_ID_PARTS[cap_id].items() if not has(pattern, item.text)]
    assert not missing, f"{model.source}: {cap_id} does not name {missing}: {item.text[:300]}"


@pytest.mark.parametrize("cap_id", MOVED_ITEMS)
def test_split_item_keeps_its_id_at_wave_2(model, cap_id):
    """A (a1): CAP-44.f, CAP-44.h and CAP-43.b keep their ids and become W2, lite."""
    require_v42(model)
    item = _item(model, cap_id)
    assert item.wave == "W2", f"{model.source}: {cap_id} is in {item.wave}, not W2 (DEC-741 A: the id keeps the lite part)"


def test_no_new_covers_id_but_cap_43d_44k_44l(model):
    """A (a1): the only new covers ids are CAP-43.d, CAP-44.k and CAP-44.l."""
    require_v42(model)
    old = {c.id for c in _base(model.source).covers}
    new = {c.id for c in model.covers} - old
    assert new == set(NEW_SPLIT_IDS), (
        f"{model.source}: new covers ids {sorted(new)}, expected exactly {sorted(NEW_SPLIT_IDS)}"
    )


def test_no_other_covers_item_of_cap_43_or_cap_44_changes_wave(model):
    """A (a1): in CAP-43 and CAP-44 only CAP-43.b, CAP-44.f and CAP-44.h change wave."""
    require_v42(model)
    now = model.by_id()
    wrong = [
        f"{old.id}: {old.wave} -> {now[old.id].wave if old.id in now else 'removed'}"
        for old in _base(model.source).covers
        if old.cap in ("CAP-43", "CAP-44")
        and old.id not in MOVED_ITEMS
        and (old.id not in now or now[old.id].wave != old.wave)
    ]
    assert not wrong, f"{model.source}: covers items of CAP-43/CAP-44 changed wave: {wrong}"


def test_covers_count_by_wave_is_w1_149_w2_19_w3_39_none_7(model):
    """CIT-P §6.3 under A (a1), then W2-27-CIT-P §5.5: 214 covers items, W1 149 / W2 19 / W3 39 / NONE 7; 62
    capabilities, W1 42 / W2 6 / W3 12 / NONE 2 (the markdown's §1 Counts says the same)."""
    # Rewrite-Reason: DEC-1093 (1) — CAP-45.a to W3: covers W2 20 -> 19, W3 38 -> 39 (214 kept); CAP-45 to W3 (A (i)):
    # capabilities W2 7 -> 6, W3 11 -> 12 (62 kept), counted from the capabilities and, in the markdown, §1 Counts.
    # Renamed: the old name stated W2 20 / W3 38.
    require_v42(model)
    counts = Counter(c.wave for c in model.covers)
    expected = {"W1": 149, "W2": 19, "W3": 39, "NONE": 7}
    assert dict(counts) == expected, f"{model.source}: covers by wave {dict(counts)}, expected {expected}"
    assert len(model.covers) == 214, f"{model.source}: {len(model.covers)} covers items, expected 214"
    caps = Counter(model.cap_waves.values())
    expected_caps = {"W1": 42, "W2": 6, "W3": 12, "NONE": 2}
    assert dict(caps) == expected_caps, f"{model.source}: capabilities by wave {dict(caps)}, expected {expected_caps}"
    assert len(model.cap_waves) == 62, f"{model.source}: {len(model.cap_waves)} capabilities, expected 62"
    if model.source == "markdown":
        table = {
            m.group(1): int(m.group(2))
            for m in re.finditer(r"^\|\s*(W1|W2|W3|NONE)\s*\|(?:\s*\d+\s*\|){3}\s*(\d+)\s*\|\s*$", read_doc(CONTRACT_MD), re.MULTILINE)
        }
        assert table == expected_caps, f"markdown: §1 Counts totals {table}, expected {expected_caps}"


# --------------------------------------------------------------------------
# B (i): lite CAP-43.b is the manifest and the file hashes only


def test_lite_cap_43b_names_none_of_the_nine_other_release_contents(model):
    """B (i): CAP-43.b (W2) holds the manifest and file hashes, and none of the nine other contents.

    A clause that names CAP-43.d or Wave 3 is a note on what is excluded, and is
    not read as part of the lite item.
    """
    require_v42(model)
    item = _item(model, "CAP-43.b")
    assert has(r"manifest", item.text) and has(r"hash", item.text), (
        f"{model.source}: CAP-43.b does not name the manifest and file hashes: {item.text}"
    )
    own = [c for c in clauses(item.text) if not (has(r"CAP-43\.d", c) or W3.search(c))]
    named = sorted(part for part, pattern in CAP_43B_REST.items() if any(has(pattern, c) for c in own))
    assert not named, f"{model.source}: lite CAP-43.b names other release contents as its own: {named}"


def test_cap_43_wave_note_names_cap_43d_and_no_ticket(model):
    """B (i): what is built before Wave 3 is ahead of its wave, in CAP-43's wave note naming CAP-43.d, no ticket."""
    require_v42(model)
    note = cap_wave_note(model.source, "CAP-43")
    assert has(r"CAP-43\.d", note), f"{model.source}: CAP-43's wave note does not name CAP-43.d: {note}"
    tickets = re.findall(r"(?<![\w-])W\d-\d+(?![\w])", note)
    assert not tickets, f"{model.source}: CAP-43's wave note names tickets {tickets}"


# --------------------------------------------------------------------------
# D (ii): CAP-45.a's Wave 2 wording


AUTH_SOURCE_PARTS = {
    "the signed tag": r"\bsign\w*\b[^;]*\btag",
    "CAP-02.c": r"CAP-02\.c(?![\w])",
    "the manifest": r"manifest",
    "the file hashes": r"\bhash",
    "CAP-43.b": r"CAP-43\.b(?![\w])",
}


def test_cap_45a_moves_to_w3_with_the_signed_tag_and_the_manifest_and_hashes_as_its_authenticated_source(model):
    """D (ii) as DEC-1093 (1) changes it (A (i), C (i)): CAP-45.a is W3, and one clause names, as its authenticated
    source, the signed tag (CAP-02.c) and the release's manifest and file hashes (CAP-43.b); it cites DEC-722 and
    DEC-1090 (W2-27-CIT-P §5.1, §5.2)."""
    # Rewrite-Reason: DEC-1093 (1) — CAP-45.a moves W2 -> W3 and C (i) withdraws the "in Wave 2" clause, keeping the
    # manifest and file hashes beside the signed tag: W2 becomes W3, and the Wave 2 source clause becomes one
    # authenticated-source clause naming both; DEC-722 still cited, DEC-1090 added. Renamed: the old name said
    # "stays W2".
    require_v42(model)
    item = _item(model, "CAP-45.a")
    assert item.wave == "W3", f"{model.source}: CAP-45.a is in {item.wave}, not W3 (DEC-1093 moves it)"
    sources = [c for c in clauses(item.text) if has(r"authenticated source", c)]
    assert sources, f"{model.source}: CAP-45.a names no authenticated source: {item.text}"
    whole = [c for c in sources if all(has(p, c) for p in AUTH_SOURCE_PARTS.values())]
    assert whole, (
        f"{model.source}: no clause of CAP-45.a names, as its authenticated source, "
        f"{[n for n, p in AUTH_SOURCE_PARTS.items() if not any(has(p, c) for c in sources)] or list(AUTH_SOURCE_PARTS)} "
        f"together: {item.text}"
    )
    assert has(r"DEC-722(?!\d)", item.text), f"{model.source}: CAP-45.a does not cite DEC-722"
    assert has(r"DEC-1090(?!\d)", item.text), f"{model.source}: CAP-45.a does not cite DEC-1090"


def test_cap_45a_names_no_signed_tag_as_a_wave_2_requirement(model):
    """D (ii), failure, as DEC-1093 (1) changes it (C (i)): no clause of CAP-45.a names Wave 2 at all, so neither
    the signed tag nor anything else is a Wave 2 requirement, and the withdrawn clause is gone."""
    # Rewrite-Reason: DEC-1093 (1) — C (i) withdraws "in Wave 2 the authenticated source is …" and CAP-45.a is W3:
    # "every signed-tag mention carries a W3 qualifier" becomes "no clause of CAP-45.a names W2 or Wave 2".
    require_v42(model)
    item = _item(model, "CAP-45.a")
    wave_2 = [c.strip() for c in clauses(item.text) if W2.search(c)]
    assert not wave_2, f"{model.source}: CAP-45.a still has a Wave 2 clause: {wave_2}"
    assert not has(r"in\s+Wave\s+2\s+the\s+authenticated\s+source", item.text), (
        f"{model.source}: CAP-45.a keeps the withdrawn Wave 2 clause: {item.text}"
    )


def _cap_45_fields(source: str) -> tuple[str, list[str], list[str]]:
    """CAP-45's wave note, provider entries and sources, as each file states them."""
    if source == "yaml":
        caps = {c["id"]: c for c in load_yaml_text(read_doc(CONTRACT_YAML)).get("capabilities", [])}
        cap = caps.get("CAP-45") or {}
        return _flatten(cap.get("wave_note")), [str(p) for p in cap.get("provider") or []], [str(s) for s in cap.get("sources") or []]
    lines, inside = {}, False
    for line in read_doc(CONTRACT_MD).splitlines():
        if line.startswith("### "):
            inside = line.startswith("### CAP-45 ")
            continue
        m = re.match(r"^- \*\*(Wave|Provider|Sources):\*\*\s*(.*)$", line)
        if inside and m and m.group(1) not in lines:
            lines[m.group(1)] = m.group(2)
    split = lambda text, sep: [s.strip() for s in text.split(sep) if s.strip()]  # noqa: E731
    return lines.get("Wave", ""), split(lines.get("Provider", ""), ","), split(lines.get("Sources", ""), ";")


def test_cap_45_moves_to_w3_with_its_wave_note_provider_and_sources(model):
    """A (i) (W2-27-CIT-P §5.1, §5.2): CAP-45 is W3 in both files; its wave note puts gov update and the first real
    `copier update` in W3 (DEC-1089, DEC-1090) beside the pending-update report (DEC-165), with no W2 left; its
    provider reads `W3: gov update --check` and names nothing W2; its sources keep the five and add DEC-1090;
    CAP-45.b stays W3."""
    # Added-For: DEC-1093 (1) — A (i), CAP-45's wave, wave note, provider and sources in both forms (the note's §5).
    require_v42(model)
    assert model.cap_waves.get("CAP-45") == "W3", f"{model.source}: CAP-45 is {model.cap_waves.get('CAP-45')}, not W3"
    note, provider, sources = _cap_45_fields(model.source)
    assert not W2.search(note), f"{model.source}: CAP-45's wave note still names W2: {note}"
    for what, pattern in (("gov update", r"gov update"), ("copier update", r"copier update"), ("DEC-1089", r"DEC-1089(?!\d)"),
                          ("DEC-1090", r"DEC-1090(?!\d)"), ("DEC-165", r"DEC-165(?!\d)"), ("W3", W3.pattern)):
        assert has(pattern, note), f"{model.source}: CAP-45's wave note does not name {what}: {note}"
    assert any(re.fullmatch(r"W3:\s*gov update --check", p) for p in provider), (
        f"{model.source}: CAP-45's provider has no 'W3: gov update --check': {provider}"
    )
    assert not [p for p in provider if W2.search(p)], f"{model.source}: CAP-45's provider still names W2: {provider}"
    kept = ["Contract v3 Gate S5", "Framework v4.1.2 §82", "Distribution Protocol v1.2 §12", "DEC-023", "DEC-165", "DEC-1090"]
    missing = [s for s in kept if s not in sources]
    assert not missing, f"{model.source}: CAP-45's sources lack {missing}: {sources}"
    assert _item(model, "CAP-45.b").wave == "W3", f"{model.source}: CAP-45.b is no longer W3"


# --------------------------------------------------------------------------
# F (i): the three verdict rules; only the owner accepts an exception

ACCEPT = r"(?<![\w])accept(?!ance)"
AUDITOR_ACCEPTS_NONE = (
    r"auditor\W+(?:\w+\W+){0,3}?(?:accepts?\s+(?:no|none|nothing)\b"
    r"|(?:does\s+not|doesn't|never|cannot|can't|may\s+not)\s+accept)"
    r"|\b(?:no|none|nothing)\b[^;]{0,40}accepted\s+by\s+the\s+(?:\w+\s+)?auditor"
)
OTHER_ACCEPTER = r"\b(?:auditor|orchestrator|lead|engineer|agent|reviewer|worker|designer)s?\b"


def test_cap_44h_states_the_three_verdict_rules(model):
    """F (i): ADOPTED_HEALTHY when every lite condition is met; WITH_ACCEPTED_EXCEPTIONS when each unmet one is
    accepted by name in an owner decision; otherwise NOT_ADOPTED_HEALTHY."""
    require_v42(model)
    parts = clauses(_item(model, "CAP-44.h").text)
    healthy = [c for c in parts if has(verdict("ADOPTED_HEALTHY"), c) and has(r"\b(?:every|all)\b", c) and has(r"\bmet\b", c)]
    excepted = [
        c
        for c in parts
        if has(verdict("ADOPTED_WITH_ACCEPTED_EXCEPTIONS"), c)
        and has(ACCEPT, c)
        and has(r"\bowner\b", c)
        and has(r"\bname", c)
        and has(r"\bdecision\b", c)
    ]
    not_healthy = [c for c in parts if has(verdict("NOT_ADOPTED_HEALTHY"), c) and has(r"\botherwise\b|\bnot\s+(?:met|accepted)\b|\bany\b", c)]
    missing = [n for n, hits in (("ADOPTED_HEALTHY", healthy), ("ADOPTED_WITH_ACCEPTED_EXCEPTIONS", excepted), ("NOT_ADOPTED_HEALTHY", not_healthy)) if not hits]
    assert not missing, f"{model.source}: CAP-44.h states no rule for {missing}"


def test_cap_44h_says_the_auditor_accepts_no_exception(model):
    """F (i): only the owner accepts an exception; the auditor accepts nothing."""
    require_v42(model)
    text = _item(model, "CAP-44.h").text
    assert any(has(AUDITOR_ACCEPTS_NONE, c) for c in clauses(text)), (
        f"{model.source}: CAP-44.h does not say that the auditor accepts no exception"
    )


def test_cap_44h_lets_no_one_but_the_owner_accept_an_exception(model):
    """F (i), failure: no clause of CAP-44.h lets the auditor, or anyone but the owner, accept an exception."""
    require_v42(model)
    wrong = []
    for c in clauses(_item(model, "CAP-44.h").text):
        if not has(ACCEPT, c) or has(AUDITOR_ACCEPTS_NONE, c):
            continue
        if has(OTHER_ACCEPTER, c) or not has(r"\bowner\b", c):
            wrong.append(c.strip())
    assert not wrong, f"{model.source}: CAP-44.h lets someone other than the owner accept an exception: {wrong}"


# --------------------------------------------------------------------------
# G (i), under either outcome of C: the lite conditions

EXIT_0 = r"exit(?:s|ing)?\s*(?:code\s*|status\s*)?(?:0|zero)(?!\d)"
LITE_CONDITIONS = {
    "gov doctor green (exit 0)": [rf"`?gov doctor`?[^,;()]{{0,25}}?(?:\bgreen\b|{EXIT_0})"],
    "gov check with no RED family": [r"`?gov check`?[^;()]{0,40}?\b(?:no|without|not)\s+(?:a\s+|any\s+)?RED\b"],
    "a first ticket closed by gov close at exit 0": [
        rf"`?gov close`?[^;]{{0,40}}?{EXIT_0}|{EXIT_0}[^;]{{0,40}}?`?gov close",
        r"\bticket",
        r"\btest",
    ],
}


@pytest.mark.parametrize("condition", sorted(LITE_CONDITIONS))
def test_cap_44h_names_the_operational_lite_condition(model, condition):
    """G (i): `gov doctor` green; `gov check` with no RED family; a first `gov close` at exit 0 with the
    repository's own test command."""
    require_v42(model)
    text = _item(model, "CAP-44.h").text
    assert any(all(has(p, c) for p in LITE_CONDITIONS[condition]) for c in clauses(text)), (
        f"{model.source}: CAP-44.h does not name the lite condition '{condition}': {text[:400]}"
    )


def _numbered_entries(text: str) -> list[str] | None:
    """The ten entries of a list numbered 1 to 10 ("(1)", "1.", "1)" or "C1"), or None."""
    for pattern in (r"\((\d{1,2})\)", r"(?<![\w.§-])(\d{1,2})[.)](?=\s)", r"(?<![\w-])C(\d{1,2})(?![\w])"):
        marks = [(int(m.group(1)), m.start(), m.end()) for m in re.finditer(pattern, text)]
        found, pos = [], 0
        for n in range(1, 11):
            hit = next(((s, e) for k, s, e in marks if k == n and s >= pos), None)
            if hit is None:
                break
            found.append(hit)
            pos = hit[1]
        if len(found) == 10:
            entries = []
            for i, (start, end) in enumerate(found):
                stop = found[i + 1][0] if i < 9 else (text.find(";", end) if ";" in text[end:] else len(text))
                entries.append(text[end:stop])
            return entries
    return None


def test_cap_44h_names_its_lite_conditions_and_marks_each_of_the_ten_if_it_lists_them(model):
    """C, either outcome: CAP-44.h states lite conditions; if it lists the ten ADOPTED_HEALTHY conditions,
    each is marked lite W2 or W3 (C (i)); otherwise the ten stay with CAP-44.l in W3 (C (ii))."""
    require_v42(model)
    text = _item(model, "CAP-44.h").text
    assert has(r"\blite\b", text) and has(r"condition", text), f"{model.source}: CAP-44.h states no lite conditions"
    entries = _numbered_entries(text)
    if entries is None:
        return
    unmarked = [e.strip()[:80] for e in entries if not (W2.search(e) or W3.search(e))]
    assert not unmarked, f"{model.source}: CAP-44.h lists the ten conditions but these are not marked W2 or W3: {unmarked}"


# --------------------------------------------------------------------------
# H (i): W2-52 builds the lite A7 and A10 stage records

W2_52 = r"(?<![\w-])W2-52(?![\w])"


def test_cit_e_names_w2_52_as_the_builder_of_the_lite_a7_and_a10_stage_records():
    """H (i): the CIT-E records W2-52 (DAEO-siiz) as the ticket that builds the lite A7 and A10 stage records."""
    cit_e = read_doc(CIT_E)
    assert together(cit_e, W2_52, gate("A7"), gate("A10")), (
        "the CIT-E does not name W2-52 with the lite A7 and A10 stage records"
    )


def test_cit_p_records_the_owner_answer_naming_w2_52():
    """H (i): the approved CIT-P records the owner's answers (DEC-741), with W2-52 for the A7 and A10 records."""
    cit_p = read_doc(CIT_P)
    assert has(r"DEC-741", cit_p), "the CIT-P does not record the owner's answers (DEC-741)"
    assert together(cit_p, W2_52, gate("A7"), gate("A10")), (
        "the CIT-P does not name W2-52 with the lite A7 and A10 stage records"
    )
    assert together(cit_p, W2_52, r"DEC-741|\bowner"), "the CIT-P names W2-52 outside its record of the owner's answers"


# --------------------------------------------------------------------------
# K (1): the version line in every capability record (independent of K (2))

V41 =r"version\s+4\.1(?![\d])"


def _base_record_names() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-tree", "--name-only", f"{BASE_COMMIT}:{CAPABILITIES}"], cwd=ROOT, capture_output=True, text=True
    )
    if proc.returncode != 0:
        pytest.fail(f"cannot list {CAPABILITIES} at the base {BASE_COMMIT}: {proc.stderr.strip()}")
    return [n for n in proc.stdout.split() if n.endswith(".md")]


def _records() -> dict[str, str]:
    folder = ROOT / CAPABILITIES
    found = {p.name: p.read_text(encoding="utf-8") for p in sorted(folder.glob("*.md"))}
    missing = sorted(set(_base_record_names()) - set(found))
    assert not missing, f"capability records removed: {missing[:10]}"
    return found


CITED_VERSION = re.compile(r"Contract v4,?\s+version\s+(\d+(?:\.\d+)+)(?![\d])")


def test_every_capability_record_cites_the_contract_version_in_force_once():
    """K (1): every record under docs/contract/capabilities/ cites "Contract v4, version <the version in force>",
    read from contract.yaml (4.2 or later), exactly once, and no other Contract version. The six master-rule
    records (docs/contract/master-rules/) are not capability records and are not read (W2-27-CIT-P §4 row 6)."""
    # Rewrite-Reason: DEC-1093 (1) — V (i): the records cite 4.3 after the apply, so "cites version 4.2" becomes
    # "cites the version in force, read from contract.yaml, exactly once, and no other" (the note's §5.3 and §8
    # step 2); the version in force must still be 4.2 or later. Renamed: the old name said "version 4.2".
    version = str(load_yaml_text(read_doc(CONTRACT_YAML)).get("version"))
    assert is_v42_or_later(version), f"contract.yaml is version {version!r}, not 4.2 or later"
    records = _records()
    wrong = {}
    for name, text in records.items():
        cited = CITED_VERSION.findall(clean(text))
        if cited != [version]:
            wrong[name] = cited
    assert not wrong, (
        f"{len(wrong)} of {len(records)} capability records do not cite Contract v4, version {version} exactly once "
        f"(and no other version): {dict(list(wrong.items())[:10])}"
    )


def test_no_capability_record_cites_contract_version_4_1():
    """K (1), failure: no record still cites version 4.1."""
    records = _records()
    old = sorted(name for name, text in records.items() if has(V41, text))
    assert not old, f"{len(old)} of {len(records)} capability records still cite version 4.1: {old[:10]}"


# --------------------------------------------------------------------------
# Row W2-L343: one status in both Contract files


def test_both_contract_files_state_status_accepted_for_v4_2():
    """W2-L343: contract.yaml and CONTRACT_v4.md state the same status, ACCEPTED (DEC-741), for v4.2."""
    statuses = {source: contract_status(source) for source in SOURCES}
    assert statuses["yaml"] == statuses["markdown"], f"the two Contract files state different statuses: {statuses}"
    assert statuses == {"yaml": "ACCEPTED", "markdown": "ACCEPTED"}, f"the Contract's status is not ACCEPTED: {statuses}"
    for source in SOURCES:
        require_v42(current_model(source))
