"""F1: AS writes nothing outside ``governance/adoption/``, changes no spec and no code, and closes no gap: every gap's
``answer`` is empty after AS and stays empty when A3 reads the record. The owner's route that writes an answer is not
stated, so no case writes one (see the README's ``unresolved``)."""

from __future__ import annotations

import w2_192_support as support

base = support.base


def test_f1_as_changes_no_byte_outside_the_adoption_folder(audited):
    support.audit_ok(audited)
    root = audited.root
    moved = support.drift(audited.snapshot_before, support.snapshot(root))
    assert not moved, f"AS changed files outside {support.FOLDER}/ (working tree, tracked or not): {moved}"
    tracked = support.drift(audited.tracked_before, support.tracked_outside(root))
    assert not tracked, f"AS changed files outside {support.FOLDER}/ at HEAD: {tracked}"
    changed = base.git(root, "diff", "--name-only", f"{audited.head_before}..HEAD").split()
    assert support.AS_RECORD in changed, f"AS committed no record: {changed}"
    outside = [rel for rel in changed if not rel.startswith(support.FOLDER + "/")]
    assert not outside, f"AS's commits touch files outside {support.FOLDER}/: {outside}"
    assert not base.porcelain(root), f"AS left the tree dirty:\n{base.porcelain(root)}"


def test_f1_the_specs_and_the_code_are_byte_for_byte_as_planted(audited):
    support.audit_ok(audited)
    root = audited.root
    planted = {**{path: support.spec_text(path) for path in support.SPECS}, **support.CODE}
    for rel, text in planted.items():
        assert (root / rel).read_bytes() == text.encode("utf-8"), f"{rel} changed in the working tree"
        assert (base.at_head(root, rel) or b"") == text.encode("utf-8"), f"{rel} changed at HEAD"
    assert not (root / support.BETA_EXTRA_PY).exists() and not (root / support.OMEGA_PY).exists(), \
        "AS created code a spec names"


def test_f1_every_gap_answer_is_empty_after_as(audited):
    support.audit_ok(audited)
    gaps = support.as_front(audited.root).get("gaps")
    assert isinstance(gaps, list) and len(gaps) == len(support.GAPS), f"gaps: {gaps!r}"
    for gap in gaps:
        assert gap.get("answer") in (None, ""), f"{gap.get('subject')}: AS closed the gap itself, answer {gap.get('answer')!r}"


def test_f1_a3_reading_the_record_leaves_it_and_its_gap_answers_as_they_were(after_as):
    support.as_ran(after_as)
    before = base.at_head(after_as.root, support.AS_RECORD)
    assert before is not None, f"HEAD holds no {support.AS_RECORD}"
    base.succeeded(support.a3_keep_all(after_as))
    assert base.at_head(after_as.root, support.AS_RECORD) == before, "A3 changed the committed AS record"
    assert (after_as.root / support.AS_RECORD).read_bytes() == before, "A3 changed the AS record in the working tree"
    for gap in support.as_front(after_as.root).get("gaps") or []:
        assert gap.get("answer") in (None, ""), f"{gap.get('subject')}: a gap was closed, answer {gap.get('answer')!r}"
