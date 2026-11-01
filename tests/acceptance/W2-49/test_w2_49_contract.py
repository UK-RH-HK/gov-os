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
    CAP_43B_REST,
    CONTRACT_MD,
    CONTRACT_YAML,
    MOVED_ITEMS,
    SPLIT_CAPABILITIES,
    VERDICTS,
    base_yaml_model,
    current_model,
    describe,
    gate,
    has,
    load_yaml_text,
    md_model,
    placements,
    read_base,
    read_doc,
    require_v42,
    verdict,
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


def test_yaml_version_is_4_2_with_a_change_log_entry_citing_dec_722():
    data = load_yaml_text(read_doc(CONTRACT_YAML))
    assert str(data.get("version")) == "4.2", f"contract.yaml is version {data.get('version')!r}, not 4.2"
    entries = [e for e in data.get("change_log", []) if str(e.get("version")) == "4.2"]
    assert len(entries) == 1, "contract.yaml's change_log has no single entry for version 4.2"
    assert has(r"DEC-722", str(entries[0].get("change", ""))), "the 4.2 change-log entry does not cite DEC-722"


def test_yaml_change_log_keeps_every_earlier_version_unchanged():
    """Every version of the specification is kept (CAP-33.e, DEC-105)."""
    before = load_yaml_text(read_base(CONTRACT_YAML))["change_log"]
    after = load_yaml_text(read_doc(CONTRACT_YAML)).get("change_log", [])
    assert str(load_yaml_text(read_doc(CONTRACT_YAML)).get("version")) == "4.2", "contract.yaml is not version 4.2"
    assert after[: len(before)] == before, "an earlier change-log entry of contract.yaml was changed or removed"


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
    """Only CAP-44.f, CAP-44.h and CAP-43.b may change wave in place, and only to W2."""
    require_v42(ymodel)
    now = ymodel.by_id()
    wrong = []
    for old in base.covers:
        new = now.get(old.id)
        if new is None or new.wave == old.wave:
            continue
        if old.id not in MOVED_ITEMS or new.wave != "W2":
            wrong.append(f"{old.id}: {old.wave} -> {new.wave}")
    assert not wrong, "covers items changed wave beyond DEC-722's parts: " + ", ".join(wrong)


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
    """The capability-level waves (and so §1 Counts) are unchanged; CAP-44 stays W3 because A11 stays."""
    require_v42(ymodel)
    assert ymodel.cap_waves == base.cap_waves, {
        k: (base.cap_waves.get(k), ymodel.cap_waves.get(k))
        for k in set(base.cap_waves) | set(ymodel.cap_waves)
        if base.cap_waves.get(k) != ymodel.cap_waves.get(k)
    }


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
