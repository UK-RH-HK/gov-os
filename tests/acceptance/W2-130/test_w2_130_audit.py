"""S3 and F3: before each marks commit an independent auditor checked every free-text mark and 20 labelled marks;
no wrong mark was committed and no free-text mark went unchecked (the check's dates and heads, its verdicts, the
comparison with each commit's diff).

A mark "derived from free text" is one ``gov links`` flags ``text: true`` on the commit's register with the marks it
appends taken off (``variant_findings``: the commit's own tool, its tree's ``src``, on the commit's own tree) or one the
audit lists in ``free_text``.
"""

from __future__ import annotations

import pytest

import w2_130_support as s


def _free_text_pairs(findings) -> set:
    return {key for key, finding in s.by_pair(findings).items() if finding.get("text")}


def _items(item) -> list:
    return s.audit_marks(item, "free_text") + s.audit_marks(item, "labelled")


def test_s3_every_marks_commit_has_one_audit_item_and_each_item_is_for_a_marks_commit(record):
    marks, audits = s.marks_commits(record), s.audits_by_commit(record)
    assert len(set(marks)) == len(marks), "commits.marks lists a commit twice"
    assert set(audits) == set(marks), f"audits and commits.marks differ: {sorted(set(audits) ^ set(marks))}"


def test_s3_each_audit_is_dated_before_its_commit_and_made_at_an_ancestor_head(record):
    audits, bad = s.audits_by_commit(record), []
    for commit in s.marks_commits(record):
        item = audits.get(commit)
        if item is None:
            bad.append((commit[:12], "no audits item"))
            continue
        when = s.parse_when(item.get("audit_date"))
        if when is None:
            bad.append((commit[:12], f"audit_date {item.get('audit_date')!r} is no ISO 8601 date with time and zone"))
        elif when >= s.committer_date(commit):
            bad.append((commit[:12], "audit_date is not before the commit's committer date"))
        try:
            if not s.is_ancestor(str(item.get("audit_head")), commit) or s.full(str(item["audit_head"])) == commit:
                bad.append((commit[:12], "audit_head is not an ancestor of the commit"))
        except (RuntimeError, KeyError):
            bad.append((commit[:12], "audit_head names no commit"))
        if not str(item.get("audit_source", "")).strip():
            bad.append((commit[:12], "audit_source names no place"))
    assert not bad, f"{bad}"


@pytest.mark.parametrize("commit", [s.FIRST, s.SECOND])
def test_s3_the_first_two_audits_were_made_at_the_heads_the_interface_names(record, commit):
    item = s.audits_by_commit(record).get(s.full(commit))
    assert item is not None, f"audits has no item for {commit}"
    assert s.full(str(item["audit_head"])) == s.full(s.AUDIT_HEADS[commit]), (
        f"{commit}: the audit is at {item['audit_head']}, the review was made at {s.AUDIT_HEADS[commit]}")


def test_s3_labelled_marks_are_twenty_drawn_by_a_seed_or_every_labelled_mark_when_twenty_or_fewer(record,
                                                                                                  variant_findings):
    audits, bad = s.audits_by_commit(record), []
    for commit in s.marks_commits(record):
        item = audits[commit]
        labelled = s.audit_marks(item, "labelled")
        keys = [(m["changed"], m["changer"]) for m in labelled]
        if len(set(keys)) != len(keys):
            bad.append((commit[:12], "labelled repeats a mark"))
        if isinstance(item.get("seed"), int) and not isinstance(item.get("seed"), bool):
            if len(labelled) != 20:
                bad.append((commit[:12], f"seed {item['seed']} draws 20, labelled holds {len(labelled)}"))
        elif item.get("seed") is None:
            text = _free_text_pairs(variant_findings(commit))
            labelled_committed = {k for k in s.committed_pairs(commit) if k not in text}
            if len(labelled) > 20 or not labelled_committed <= set(keys):
                bad.append((commit[:12], "seed null: labelled must hold every labelled mark the commit adds, 20 or fewer"))
        else:
            bad.append((commit[:12], f"seed {item.get('seed')!r} is neither an integer nor null"))
    assert not bad, f"{bad}"


def test_s3_verdicts_and_fates_agree_with_what_each_commit_committed(record):
    audits, bad = s.audits_by_commit(record), []
    for commit in s.marks_commits(record):
        committed = s.committed_pairs(commit)
        tails = {}
        for mark in s.added_marks(commit):
            tails.setdefault(mark["changed"], set()).add(mark["changer"])
        for mark in _items(audits[commit]):
            key = (mark["changed"], mark["changer"])
            verdict, fate = mark["verdict"], mark["fate"]
            if verdict not in ("right", "wrong") or fate not in ("committed", "dropped", "corrected"):
                bad.append((commit[:12], key, "verdict or fate outside the words of the interface"))
            elif verdict == "right" and fate != "committed":
                bad.append((commit[:12], key, "a right mark must be committed"))
            elif verdict == "wrong" and fate == "committed":
                bad.append((commit[:12], key, "a wrong mark was committed"))
            elif fate == "dropped" and key in committed:
                bad.append((commit[:12], key, "dropped, yet the commit appends it"))
            elif fate == "committed" and key not in committed:
                bad.append((commit[:12], key, "committed, yet the commit does not append it"))
            elif fate == "corrected":
                fixed = s.ids_in(str(mark.get("committed_mark", "")))
                if not fixed or not set(fixed) <= tails.get(mark["changed"], set()):
                    bad.append((commit[:12], key, "corrected: the commit does not append the committed_mark"))
    assert not bad, f"{bad[:6]}"


def test_f3_every_free_text_mark_a_commit_adds_is_in_the_audit_with_a_verdict_of_right(record, variant_findings):
    audits, bad = s.audits_by_commit(record), []
    for commit in s.marks_commits(record):
        listed = {(m["changed"], m["changer"]): m for m in s.audit_marks(audits[commit], "free_text")}
        for key in sorted(s.committed_pairs(commit) & _free_text_pairs(variant_findings(commit))):
            if key not in listed:
                bad.append((commit[:12], key, "free-text mark committed unchecked"))
            elif listed[key]["verdict"] != "right":
                bad.append((commit[:12], key, "free-text mark committed with a verdict of " + listed[key]["verdict"]))
    assert not bad, f"{len(bad)}: {bad[:6]}"


def test_f3_no_committed_mark_is_one_any_audit_judged_wrong(record):
    audits = s.audits_by_commit(record)
    dropped = {(m["changed"], m["changer"]) for commit in s.marks_commits(record) for m in _items(audits[commit])
               if m["verdict"] == "wrong" and m["fate"] == "dropped"}
    bad = [(commit[:12], key) for commit in s.marks_commits(record) for key in sorted(s.committed_pairs(commit))
           if key in dropped]
    assert not bad, f"marks an audit judged wrong and dropped, yet committed: {bad[:6]}"


def test_f3_the_comparison_shows_no_unchecked_and_no_wrong_mark_and_my_comparison_agrees(record, variant_findings):
    audits, comparison = s.audits_by_commit(record), record.data("comparison")
    assert isinstance(comparison, dict), "w2-130:comparison is not a mapping commit -> {unchecked, wrong}"
    by_commit = {s.need_hash(key, "comparison key"): value for key, value in comparison.items()}
    bad = []
    for commit in s.marks_commits(record):
        recorded = by_commit.get(commit)
        if not isinstance(recorded, dict) or recorded.get("unchecked") != 0 or recorded.get("wrong") != 0:
            bad.append((commit[:12], "the record's comparison is not unchecked 0, wrong 0", recorded))
        committed = s.committed_pairs(commit)
        listed = {(m["changed"], m["changer"]) for m in s.audit_marks(audits[commit], "free_text")}
        judged_wrong = {(m["changed"], m["changer"]) for m in _items(audits[commit])
                        if m["verdict"] == "wrong" and m["fate"] == "dropped"}
        unchecked = (committed & _free_text_pairs(variant_findings(commit))) - listed
        if unchecked or committed & judged_wrong:
            bad.append((commit[:12], "my comparison finds unchecked", sorted(unchecked)[:3],
                        "wrong", sorted(committed & judged_wrong)[:3]))
    assert not bad, f"{bad}"
