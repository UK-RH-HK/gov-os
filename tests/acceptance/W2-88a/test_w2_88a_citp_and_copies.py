"""W2-88a, success 3 -- the CIT-P record and the copies.

KPI line: "The CIT-P record (docs/changes/W2-88a-CIT-P.md) gives the kernel skill's sha256 before and after, the lines
added or removed, the independent review and the owner's approval of the bytes before the merge; the two .rulesync
copies equal the kernel copy in the changed sections. Verify: the record holds both hashes and the review's verdict; a
diff of the three files shows the same changed sections."

Readings (also in the README):
* BEFORE: the record holds 641a347b...102d, which is also the sha256 of `git show ba27e4c0d:<kernel skill>`, a fixed
  commit, so the check never moves. The hash must sit on a line (or the line above it) that says "before".
* AFTER: a different 64-hex value, equal to the kernel skill's sha256 AS THIS TICKET LAST COMMITTED IT: the blob at the
  latest commit after the base that changes the kernel skill and carries `Task: DAEO-pg6i`. Why not the file in the
  working tree or at HEAD: after the merge into w2/integrate a later ticket may change the skill, and the record is
  history, so a HEAD-based check would turn red then. Why not "any commit's blob": an intermediate blob of this
  ticket's own would pass, and the owner approves one set of bytes. A later ticket's commit carries another Task and
  never moves this value. A record naming a stale blob (the skill committed again after the record) fails.
  The hash must sit on a line (or the line above it) that says "after".
* LINES: counts (or the diff). The record's stated numbers of lines added and removed (forms read: "15 lines added",
  "added: 15", "none removed", "+15 -0", git's "15 insertions(+), 0 deletions(-)", a `--numstat` row) must include
  `git diff --numstat <base> <after commit> -- <kernel skill>`'s two numbers; or the record lists the diff: every added
  line (and every removed line) of that diff appears in it.
* REVIEW: the record says an independent review was made (the words "independent" and "review" or "auditor") and
  states a verdict (`verdict: PASS`...). The last verdict stated must begin with PASS (a recorded FAIL, or only a
  placeholder, fails). So this line passes only after the independent review is in the record.
* OWNER: a place for the owner's approval of the bytes (a line with "owner" and "approv...", and within it or the next
  lines "bytes", "sha256", "hash", "skill" or "file"). NOT required to be filled in: the owner approves after this
  run's review, before the merge.
* COPIES: the three files are byte-equal (the strong form; they are one generated source, so a weaker form has no
  reason), and, so that the test is red until the text exists, each block of lines the kernel skill adds to the base
  appears verbatim in both `.rulesync` copies (and the kernel skill must have changed at all).
"""

from __future__ import annotations

import difflib
import re

import pytest

import w2_88a_support as support


def _record():
    return support.read(support.CITP_REL)


def _after_or_fail():
    after, commit = support.committed_after_hash()
    if after is None:
        pytest.fail(f"no commit after {support.BASE_COMMIT} that changes {support.KERNEL_REL} carries "
                    f"`Task: {support.TICKET}`: commit the skill with that trailer", pytrace=False)
    return after, commit


def _labelled(text, digest, label):
    return any(label in context for context in support.hash_lines(text, digest))


def test_s3_the_before_hash_is_the_sha256_of_the_skill_at_the_base_commit():
    """Guard (holds on the base): the pinned value is the sha256 of `git show ba27e4c0d:<kernel skill>`."""
    assert support.sha256_of(support.base_blob()) == support.BASE_SHA256


def test_s3_the_record_holds_the_kernel_skills_sha256_before():
    """The record gives the sha256 of the skill before the change: 641a347b...102d, on a line that says "before"."""
    text = _record()
    assert support.BASE_SHA256 in text.lower(), (
        f"{support.CITP_REL} does not hold the kernel skill's sha256 before the change ({support.BASE_SHA256})")
    assert _labelled(text, support.BASE_SHA256, "before"), (
        f"{support.CITP_REL} holds {support.BASE_SHA256[:12]}... but not on a line that says it is the hash "
        "`before`")


def test_s3_the_record_holds_the_kernel_skills_sha256_after_as_committed():
    """The record gives a different sha256 for the skill after the change: the blob this ticket last committed."""
    text = _record()
    after, commit = _after_or_fail()
    assert after != support.BASE_SHA256, (
        f"the kernel skill committed at {commit[:12]} is byte-equal to the base's: nothing changed")
    assert after in text.lower(), (
        f"{support.CITP_REL} does not hold the kernel skill's sha256 after the change as committed at "
        f"{commit[:12]} ({after})")
    assert _labelled(text, after, "after"), (
        f"{support.CITP_REL} holds {after[:12]}... but not on a line that says it is the hash `after`")


def test_s3_the_record_gives_the_lines_added_or_removed():
    """Counts (or the diff) of the lines the change added to or removed from the kernel skill."""
    text = _record()
    _, commit = _after_or_fail()
    added, removed = support.actual_numstat(commit)
    stated_added, stated_removed = support.stated_counts(text)
    if added in stated_added and removed in stated_removed:
        return
    diff_added, diff_removed = support.actual_diff_lines(commit)
    body = support.flat(text)
    if diff_added and all(support.flat(line) in body for line in diff_added + diff_removed):
        return
    pytest.fail(f"{support.CITP_REL} does not give the lines added or removed: `git diff --numstat` says {added} "
                f"added and {removed} removed; the record states added {sorted(stated_added) or 'nothing'} and "
                f"removed {sorted(stated_removed) or 'nothing'} and does not list the diff", pytrace=False)


def test_s3_the_record_gives_the_independent_review_with_its_pass_verdict():
    """The independent review is recorded with its verdict (the last one stated begins with PASS)."""
    text = _record()
    low = text.lower()
    assert "independent" in low and re.search(r"review|auditor", low), (
        f"{support.CITP_REL} does not record an independent review")
    stated = support.verdicts(text)
    assert stated, f"{support.CITP_REL} records no verdict of the independent review (`verdict: PASS` or `FAIL`)"
    assert stated[-1].startswith("PASS"), (
        f"the last verdict {support.CITP_REL} records is {stated[-1]!r}, not PASS (all stated: {stated})")


def test_s3_the_record_has_a_place_for_the_owners_approval_of_the_bytes():
    """A line for the owner's approval of the bytes (not required to be filled in)."""
    places = support.owner_approval_lines(_record())
    assert places, f"{support.CITP_REL} has no place for the owner's approval (a line with `owner` and `approv...`)"
    assert any(re.search(r"\bbytes?\b|sha-?256|\bhash\b|\bskill\b|\bfiles?\b", context) for _, context in places), (
        f"{support.CITP_REL}'s place for the owner's approval does not say it is the approval of the bytes "
        "(no `bytes`, `sha256`, `hash`, `skill` or `file` with it)")


def test_s3_the_three_files_are_byte_equal():
    """Guard (holds on the base): the kernel copy and the two generated-source copies are one text."""
    kernel = support.read_bytes(support.KERNEL_REL)
    differing = [rel for rel in support.COPIES_REL if support.read_bytes(rel) != kernel]
    assert not differing, (f"{' and '.join(differing)} differ from {support.KERNEL_REL} "
                           f"(sha256 {support.sha256_of(kernel)[:12]}...)")


def test_s3_the_changed_sections_reach_both_generated_source_copies():
    """Every block the kernel skill adds to the base's text appears verbatim in each `.rulesync` copy; the kernel
    skill has changed from the base at all."""
    base = support.base_blob().decode("utf-8").splitlines()
    kernel_text = support.read(support.KERNEL_REL)
    blocks, current = [], []
    for line in difflib.unified_diff(base, kernel_text.splitlines(), lineterm="", n=0):
        if line.startswith(("+++", "---", "@@")):
            if current:
                blocks.append("\n".join(current))
                current = []
            continue
        if line.startswith("+"):
            current.append(line[1:])
        elif current:
            blocks.append("\n".join(current))
            current = []
    if current:
        blocks.append("\n".join(current))
    blocks = [block for block in blocks if block.strip()]
    assert blocks, (f"{support.KERNEL_REL} is unchanged from the base ({support.BASE_COMMIT}): there are no changed "
                    "sections to carry into the copies")
    for rel in support.COPIES_REL:
        copy = support.read(rel)
        missing = [block for block in blocks if block not in copy]
        assert not missing, (f"{rel} lacks {len(missing)} of {len(blocks)} changed block(s) of the kernel skill; "
                             f"first: {missing[0][:100]!r}")
