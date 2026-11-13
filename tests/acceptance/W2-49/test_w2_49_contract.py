"""KPI success line 2: Contract v4.2 (``docs/contract/contract.yaml`` and ``CONTRACT_v4.md``).

"Contract v4.2 moves exactly those parts to Wave 2. CAP-02.c, A9, A11, the
qualification certificate and the rest of CAP-43.b stay in Wave 3."

"Those parts" (KPI line 1, DEC-722): CAP-44.h, lite (the verdict); the A7 and
A10 gates of CAP-44.f, lite; CAP-43.b, lite (the manifest and file hashes).

No source fixes how the Contract shows an item split between waves.  These
tests accept three forms, on the covers items themselves (see ``placements``
in ``w2_49_support.py`` and the README):
  1. a split into separate covers items, each with its own ``wave``;
  2. the item moved whole to W2, with a note naming what stays in W3;
  3. the item kept in W3, with a note naming what moves to W2.
"Exactly" is checked on the ``wave`` fields against the base (a02e3485).
Every placement test runs on both files, so the two agree on the moved and
the kept parts.
"""

from __future__ import annotations

import re

import pytest

from w2_49_support import (
    APPROVED_ON,
    CAP_43B_REST,
    CAPABILITIES_MOVED_BY_DEC_1093,
    CONTRACT_MD,
    CONTRACT_YAML,
    COVERS_MOVED_BY_DEC_1093,
    MOVED_ITEMS,
    SPLIT_CAPABILITIES,
    V42_COMMIT,
    V43_CITES,
    VERDICTS,
    base_yaml_model,
    current_model,
    describe,
    frontmatter,
    gate,
    has,
    is_v42_or_later,
    iso_date_on_or_after,
    load_yaml_text,
    md_model,
    placements,
    read_at,
    read_base,
    read_doc,
    require_v42,
    verdict,
    version_key,
)

SOURCES = ["yaml", "markdown"]


@pytest.fixture(scope="module", params=SOURCES)
def model(request):
    return current_model(request.param)


@pytest.fixture(scope="module")
def ymodel():
    return current_model("yaml")


@pytest.fixture(scope="module")
def base():
    return base_yaml_model()


# --------------------------------------------------------------------------
# The version and its change log


def test_yaml_version_is_4_2_or_later_with_the_4_2_entry_citing_dec_722_unchanged():
    """contract.yaml is version 4.2 or later; its one 4.2 change-log entry cites DEC-722, as W2-49 wrote it."""
    # Rewrite-Reason: DEC-1093 (1) — Contract 4.3 (V (i)): the version is "4.2 or later", not "4.2"; the 4.2 entry
    # must still be there, unchanged from W2-49's apply (V42_COMMIT), and still cite DEC-722. Renamed: the old name
    # said "version is 4.2". The 4.3 entry is test_yaml_change_log_has_a_4_3_entry_….
    data = load_yaml_text(read_doc(CONTRACT_YAML))
    assert is_v42_or_later(data.get("version")), f"contract.yaml is version {data.get('version')!r}, not 4.2 or later"
    entries = [e for e in data.get("change_log", []) if str(e.get("version")) == "4.2"]
    assert len(entries) == 1, "contract.yaml's change_log has no single entry for version 4.2"
    assert has(r"DEC-722", str(entries[0].get("change", ""))), "the 4.2 change-log entry does not cite DEC-722"
    v42 = [e for e in load_yaml_text(read_at(V42_COMMIT, CONTRACT_YAML))["change_log"] if str(e.get("version")) == "4.2"]
    assert entries == v42, f"the 4.2 change-log entry differs from Contract 4.2 as applied ({V42_COMMIT})"


def test_yaml_change_log_keeps_every_earlier_version_unchanged():
    """Every version of the specification is kept (CAP-33.e, DEC-105): 4.0, 4.1 and 4.2 as they were written."""
    # Rewrite-Reason: DEC-1093 (1) — Contract 4.3 (V (i)): the version is "4.2 or later", not "4.2"; the entries
    # kept are 4.0 and 4.1 as at the base and, now, 4.2 as at W2-49's apply (V42_COMMIT), in that order, first.
    before = load_yaml_text(read_base(CONTRACT_YAML))["change_log"]
    v42 = load_yaml_text(read_at(V42_COMMIT, CONTRACT_YAML))["change_log"]
    data = load_yaml_text(read_doc(CONTRACT_YAML))
    after = data.get("change_log", [])
    assert is_v42_or_later(data.get("version")), f"contract.yaml is version {data.get('version')!r}, not 4.2 or later"
    assert v42[: len(before)] == before, f"the premise fails: {V42_COMMIT} does not keep the base's change log"
    assert [str(e.get("version")) for e in v42] == ["4.0", "4.1", "4.2"], f"the premise fails: {V42_COMMIT} is not 4.2"
    assert after[: len(before)] == before, "an earlier change-log entry of contract.yaml was changed or removed"
    assert after[: len(v42)] == v42, "the 4.0, 4.1 or 4.2 change-log entry of contract.yaml was changed or removed"


def test_yaml_change_log_has_a_4_3_entry_citing_w2_27_cit_p_dec_1093_dec_1089_dec_1090():
    """Contract 4.3 (W2-27-CIT-P §5.1): one change-log entry 4.3, after the 4.2 entry, citing the note, the owner's
    approval (DEC-1093) and the decisions it carries (DEC-1089, DEC-1090), dated on or after the approval."""
    # Added-For: DEC-1093 (1) — V (i), the 4.3 entry (the note's §5.1); APPLY_DATE asked only as a date >= 2026-11-07.
    data = load_yaml_text(read_doc(CONTRACT_YAML))
    log = data.get("change_log", [])
    versions = [str(e.get("version")) for e in log]
    assert versions.count("4.3") == 1, f"contract.yaml's change_log has no single entry for version 4.3: {versions}"
    assert versions.index("4.3") == versions.index("4.2") + 1, f"the 4.3 entry does not follow the 4.2 entry: {versions}"
    entry = log[versions.index("4.3")]
    change = str(entry.get("change", ""))
    missing = [name for name, pattern in V43_CITES.items() if not has(pattern, change)]
    assert not missing, f"the 4.3 change-log entry does not cite {missing}: {change[:300]}"
    assert iso_date_on_or_after(entry.get("date")), f"the 4.3 entry's date {entry.get('date')!r} is not on or after {APPROVED_ON}"
    assert version_key(data.get("version")) >= (4, 3), f"contract.yaml is version {data.get('version')!r}, not 4.3 or later"
    assert iso_date_on_or_after(data.get("revised")), f"contract.yaml's revised {data.get('revised')!r} is not on or after {APPROVED_ON}"


def _md_change_rows(text: str) -> dict[str, str]:
    return {m.group(1): m.group(0) for m in re.finditer(r"^\|\s*(\d+\.\d+)\s*\|.*$", text, re.MULTILINE)}


def test_markdown_version_is_4_2_with_a_change_row_citing_dec_722():
    text = read_doc(CONTRACT_MD)
    model = md_model(text)
    require_v42(model)
    rows = _md_change_rows(text)
    assert "4.2" in rows, "CONTRACT_v4.md's version table has no row for 4.2"
    assert has(r"DEC-722", rows["4.2"]), "the 4.2 row of CONTRACT_v4.md does not cite DEC-722"
    before = _md_change_rows(read_base(CONTRACT_MD))
    for version, row in before.items():
        assert rows.get(version) == row, f"the {version} row of CONTRACT_v4.md was changed or removed"


def test_markdown_has_a_4_3_change_row_citing_w2_27_cit_p_dec_1093_dec_1089_dec_1090():
    """Contract 4.3 (W2-27-CIT-P §5.2): a `| 4.3 |` row after the 4.2 row, citing the note, DEC-1093, DEC-1089 and
    DEC-1090; the 4.2 row as W2-49 applied it; the frontmatter, title and version line state one version, the
    YAML's, and the frontmatter `decisions` gain DEC-1089 and DEC-1090."""
    # Added-For: DEC-1093 (1) — V (i), the 4.3 row and version lines (the note's §5.2).
    text = read_doc(CONTRACT_MD)
    rows = _md_change_rows(text)
    assert "4.3" in rows, "CONTRACT_v4.md's version table has no row for 4.3"
    order = list(rows)
    assert order.index("4.3") == order.index("4.2") + 1, f"the 4.3 row does not follow the 4.2 row: {order}"
    missing = [name for name, pattern in V43_CITES.items() if not has(pattern, rows["4.3"])]
    assert not missing, f"the 4.3 row of CONTRACT_v4.md does not cite {missing}: {rows['4.3'][:300]}"
    cells = [c.strip() for c in rows["4.3"].strip().strip("|").split("|")]
    assert len(cells) >= 2 and iso_date_on_or_after(cells[1]), f"the 4.3 row's date {cells[1:2]} is not on or after {APPROVED_ON}"
    v42 = _md_change_rows(read_at(V42_COMMIT, CONTRACT_MD))
    assert rows.get("4.2") == v42.get("4.2"), f"the 4.2 row of CONTRACT_v4.md differs from Contract 4.2 as applied ({V42_COMMIT})"
    meta, _ = frontmatter(text)
    version = str(meta.get("version"))
    assert version == str(load_yaml_text(read_doc(CONTRACT_YAML)).get("version")), (
        f"CONTRACT_v4.md is version {version!r}, contract.yaml {load_yaml_text(read_doc(CONTRACT_YAML)).get('version')!r}"
    )
    assert version_key(version) is not None and version_key(version) >= (4, 3), f"CONTRACT_v4.md is version {version!r}, not 4.3 or later"
    assert iso_date_on_or_after(meta.get("revised")), f"CONTRACT_v4.md's revised {meta.get('revised')!r} is not on or after {APPROVED_ON}"
    v = re.escape(version)
    assert re.search(rf"^# .*Contract v4 \(version {v}\)\s*$", text, re.MULTILINE), f"the title does not state version {version}"
    assert re.search(rf"^\*\*Version {v}\*\* \(", text, re.MULTILINE), f"the version line does not state version {version}"
    decisions = [str(d) for d in meta.get("decisions") or []]
    assert {"DEC-722", "DEC-1089", "DEC-1090"} <= set(decisions), f"the frontmatter decisions lack DEC-1089 or DEC-1090: {decisions[-5:]}"


# --------------------------------------------------------------------------
# What moves to Wave 2, lite (both files)


def _assert_lite_and_sourced(hits, what):
    assert any(has(r"\blite\b", item.text) for item, _ in hits), (
        f"{what} is placed in W2 but no covers item carrying it says it is lite (DEC-722)"
    )
    assert any(has(r"DEC-722", item.text) for item, _ in hits), (
        f"{what} is placed in W2 but no covers item carrying it cites DEC-722"
    )


def test_cap_44h_verdict_moves_to_wave_2_lite(model):
    """CAP-44.h, lite: the three verdicts ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY."""
    require_v42(model)
    hits = [
        (item, text)
        for item, text in placements(model, "CAP-44", "W2", r"verdict|ADOPTED_HEALTHY")
        if item.id == "CAP-44.h" or all(has(verdict(v), text) for v in VERDICTS)
    ]
    assert hits, f"{model.source}: CAP-44.h's verdict is not placed in W2\n{describe(model, 'CAP-44')}"
    _assert_lite_and_sourced(hits, f"{model.source}: the CAP-44.h verdict")


@pytest.mark.parametrize("name", ["A7", "A10"])
def test_cap_44f_gate_moves_to_wave_2_lite(model, name):
    """CAP-44.f, lite: the A7 and A10 gates move to Wave 2."""
    require_v42(model)
    hits = placements(model, "CAP-44", "W2", gate(name))
    assert hits, f"{model.source}: the {name} gate of CAP-44.f is not placed in W2\n{describe(model, 'CAP-44')}"
    _assert_lite_and_sourced(hits, f"{model.source}: the {name} gate")


def test_cap_43b_manifest_and_file_hashes_move_to_wave_2_lite(model):
    """CAP-43.b, lite: the manifest and file hashes."""
    require_v42(model)
    hits = [(i, t) for i, t in placements(model, "CAP-43", "W2", r"manifest") if has(r"hash", t)]
    assert hits, (
        f"{model.source}: CAP-43.b's manifest and file hashes are not placed in W2\n{describe(model, 'CAP-43')}"
    )
    _assert_lite_and_sourced(hits, f"{model.source}: CAP-43.b's manifest and file hashes")


# --------------------------------------------------------------------------
# What stays in Wave 3 (both files)


@pytest.mark.parametrize("name", ["A9", "A11"])
def test_cap_44f_gate_stays_in_wave_3(model, name):
    """CAP-44.f: A9 (new knowledge fabric) and A11 (full audit) stay in Wave 3."""
    require_v42(model)
    assert placements(model, "CAP-44", "W3", gate(name)), (
        f"{model.source}: {name} is no longer placed in W3\n{describe(model, 'CAP-44')}"
    )


@pytest.mark.parametrize("part", sorted(CAP_43B_REST))
def test_rest_of_cap_43b_stays_in_wave_3(model, part):
    """CAP-43.b: every release content but the manifest and file hashes stays in Wave 3."""
    require_v42(model)
    assert placements(model, "CAP-43", "W3", CAP_43B_REST[part]), (
        f"{model.source}: CAP-43.b's '{part}' is no longer placed in W3\n{describe(model, 'CAP-43')}"
    )


def test_cap_02c_signed_release_tag_stays_in_wave_3(model):
    """CAP-02.c (SSH-signed release tag) stays in Wave 3 (DEC-722 item 2)."""
    require_v42(model)
    item = model.by_id().get("CAP-02.c")
    assert item is not None, f"{model.source}: CAP-02.c is missing"
    assert item.wave == "W3", f"{model.source}: CAP-02.c is in {item.wave}, not W3"
    assert has(r"sign", item.text) and has(r"tag", item.text), f"{model.source}: CAP-02.c no longer states the signed tag"


def test_qualification_certificate_cap_43c_stays_in_wave_3(model):
    """The qualification certificate (CAP-43.c, release certification by qualification) stays in Wave 3."""
    require_v42(model)
    item = model.by_id().get("CAP-43.c")
    assert item is not None, f"{model.source}: CAP-43.c is missing"
    assert item.wave == "W3", f"{model.source}: CAP-43.c is in {item.wave}, not W3"
    assert has(r"certif", item.text), f"{model.source}: CAP-43.c no longer states the certification by qualification"


# --------------------------------------------------------------------------
# "Exactly": nothing else changes wave (contract.yaml against the base)


def test_no_other_covers_item_changes_wave(ymodel, base):
    """Only CAP-44.f, CAP-44.h and CAP-43.b may change wave in place, and only to W2 (DEC-722); and CAP-45.a moves
    W2 -> W3 (DEC-1093). Nothing else moves."""
    # Rewrite-Reason: DEC-1093 (1) — A (i): against the same base, CAP-45.a's move W2 -> W3 is required, named as
    # DEC-1093's; W2-49's own moves (CAP-44.f, CAP-44.h, CAP-43.b, to W2 only) are allowed as before; any other
    # change of wave still fails.
    require_v42(ymodel)
    now = ymodel.by_id()
    wrong = []
    for old in base.covers:
        new = now.get(old.id)
        if new is None or new.wave == old.wave:
            continue
        if old.id in MOVED_ITEMS and new.wave == "W2":
            continue
        if COVERS_MOVED_BY_DEC_1093.get(old.id) == (old.wave, new.wave):
            continue
        wrong.append(f"{old.id}: {old.wave} -> {new.wave}")
    assert not wrong, "covers items changed wave beyond DEC-722's parts and DEC-1093's move: " + ", ".join(wrong)
    unmoved = [
        f"{cid}: {now[cid].wave if cid in now else 'removed'} (DEC-1093 moves it {a} -> {b})"
        for cid, (a, b) in COVERS_MOVED_BY_DEC_1093.items()
        if base.by_id()[cid].wave != a or cid not in now or now[cid].wave != b
    ]
    assert not unmoved, "covers items DEC-1093 moves have not moved: " + ", ".join(unmoved)


def test_no_covers_item_is_removed(ymodel, base):
    """Covers ids are cited by tickets and tests; a split keeps the original id."""
    require_v42(ymodel)
    missing = sorted({c.id for c in base.covers} - {c.id for c in ymodel.covers})
    assert not missing, f"covers items removed in v4.2: {missing}"


def test_new_covers_items_are_only_splits_of_cap_43_and_cap_44(ymodel, base):
    """A split may add covers items to CAP-43 and CAP-44 only, each in W2 or W3."""
    require_v42(ymodel)
    old_ids = {c.id for c in base.covers}
    wrong = [
        f"{c.id} ({c.cap}, {c.wave})"
        for c in ymodel.covers
        if c.id not in old_ids and (c.cap not in SPLIT_CAPABILITIES or c.wave not in ("W2", "W3"))
    ]
    assert not wrong, f"new covers items outside a split of CAP-43 or CAP-44: {wrong}"


def test_no_capability_is_added_removed_or_changes_wave(ymodel, base):
    """No capability is added or removed; the only capability-level change of wave is CAP-45's, W2 -> W3
    (DEC-1093); CAP-44 stays W3 because A11 stays."""
    # Rewrite-Reason: DEC-1093 (1) — A (i): against the same base, exactly one capability changes wave, CAP-45,
    # W2 -> W3, named as DEC-1093's (W2-49 moved none); no capability added or removed; CAP-44 still W3.
    require_v42(ymodel)
    assert set(ymodel.cap_waves) == set(base.cap_waves), {
        "added": sorted(set(ymodel.cap_waves) - set(base.cap_waves)),
        "removed": sorted(set(base.cap_waves) - set(ymodel.cap_waves)),
    }
    changed = {k: (base.cap_waves[k], ymodel.cap_waves[k]) for k in base.cap_waves if base.cap_waves[k] != ymodel.cap_waves[k]}
    assert changed == CAPABILITIES_MOVED_BY_DEC_1093, (
        f"capability waves changed {changed}; expected exactly DEC-1093's {CAPABILITIES_MOVED_BY_DEC_1093}"
    )
    assert ymodel.cap_waves.get("CAP-44") == "W3", f"CAP-44 is {ymodel.cap_waves.get('CAP-44')}, not W3 (A11 stays)"


# --------------------------------------------------------------------------
# The two files agree


def test_yaml_and_markdown_agree_on_every_covers_item_and_wave():
    """contract.yaml and CONTRACT_v4.md hold the same covers items in the same waves."""
    y, m = current_model("yaml"), current_model("markdown")
    require_v42(y)
    require_v42(m)
    ywaves = {c.id: c.wave for c in y.covers}
    mwaves = {c.id: c.wave for c in m.covers}
    diff = {k: (ywaves.get(k), mwaves.get(k)) for k in set(ywaves) | set(mwaves) if ywaves.get(k) != mwaves.get(k)}
    assert not diff, f"covers items that differ between contract.yaml and CONTRACT_v4.md (yaml, md): {diff}"
    assert y.cap_waves == m.cap_waves, "capability waves differ between contract.yaml and CONTRACT_v4.md"
