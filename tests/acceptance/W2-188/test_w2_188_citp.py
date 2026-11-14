"""W2-188, success 5 -- the CIT-P record `docs/changes/W2-188-CIT-P.md`.

Readings (also in the README):
* BEFORE: the full `16fd341f...0a0` on a line (or the line above it) that says "before"; also the sha256 of
  `git show 5336a6fca:<kernel skill>`, a fixed commit, so the pin never moves.
* AFTER: a different 64-hex value equal to the kernel skill's sha256 AS THIS TICKET LAST COMMITTED IT: the blob at the latest
  commit after the base that changes the kernel skill and carries `Task: DAEO-zlog` (W2-88a's reading: a later ticket's
  commit never moves it; an intermediate blob of this ticket is not the answer). The hash sits on a line (or under a line)
  that says "after".
* LINES: counts the record states (W2-88a's `stated_counts` forms) must include `git diff --numstat <base> <that commit>`'s
  two numbers, or every added and removed line of that diff is listed.
* TEXT: every non-blank removed line and every added line of that diff (a leading list number or bullet dropped,
  whitespace collapsed, markdown block-quote marks and backticks dropped) stands in the record, except the version line,
  for which `1.0.0` and `1.1.0` standing in the record is enough.
* IMPACT (re-baselined 2026-11-14, DEC-1157 (12), P-W2-188-S5 (a)): table rows say W2-11's body and version cases do not
  cover `adopt` (so they stay as they are); `adapter-portability` reports `GENERATED_DIFFERS` on
  `.claude/skills/adopt/SKILL.md` until the copies ACT; W2-88a's cases are `unchanged`.
* VERDICT: the record says an independent review was made and its last `verdict:` begins with PASS.
* OWNER: its own case: an `owner_approval:` line that names the after sha256 and says `approved`.
"""

from __future__ import annotations

import re

import pytest

import w2_188_support as support


def _record():
    return support.read(support.CITP_REL)


def _after_or_fail():
    after, commit = support.committed_after()
    if after is None:
        pytest.fail(f"no commit after {support.BASE[:9]} that changes {support.KERNEL_REL} carries `Task: {support.TICKET}`: "
                    "commit the skill with that trailer", pytrace=False)
    return after, commit


def _labelled(text, digest, label):
    return any(label in context for context in support.a88.hash_lines(text, digest))


def test_s5_the_record_holds_the_full_sha256_before_on_a_line_that_says_before():
    text = _record()
    assert support.BASE_SHA256 in text.lower(), f"{support.CITP_REL} does not hold the full before sha256"
    assert _labelled(text, support.BASE_SHA256, "before"), (
        f"{support.CITP_REL} holds {support.BASE_SHA256[:12]}... but not on a line that says `before`")


def test_s5_the_record_holds_the_sha256_after_as_the_kernel_skill_was_last_committed():
    text = _record()
    after, commit = _after_or_fail()
    assert after != support.BASE_SHA256, f"the kernel skill committed at {commit[:12]} is byte-equal to the base's"
    assert after in text.lower(), (f"{support.CITP_REL} does not hold the kernel skill's sha256 as committed at "
                                   f"{commit[:12]} ({after})")
    assert _labelled(text, after, "after"), f"{support.CITP_REL} holds {after[:12]}... but not on a line that says `after`"


def test_s5_the_record_gives_the_lines_added_and_removed_matching_the_diff_against_the_base():
    text = _record()
    _, commit = _after_or_fail()
    added, removed = support.numstat(commit)
    stated_added, stated_removed = support.stated_counts(text)
    if added in stated_added and removed in stated_removed:
        return
    removed_lines, added_lines = support.diff_changed_lines(commit)
    body = support.quote_free(text)
    if added_lines and all(support.flat(line) in body for line in removed_lines + added_lines):
        return
    pytest.fail(f"{support.CITP_REL} does not give the lines added and removed: `git diff --numstat` says {added} added and "
                f"{removed} removed; the record states added {sorted(stated_added) or 'nothing'} and removed "
                f"{sorted(stated_removed) or 'nothing'} and does not list the diff", pytrace=False)


def test_s5_the_record_gives_the_old_and_new_text_of_each_changed_place():
    text = _record()
    _, commit = _after_or_fail()
    removed, added = support.diff_changed_lines(commit)
    assert removed and added, "the committed kernel skill removes or adds no line against the base"
    body = support.quote_free(text)
    missing = []
    for kind, lines in (("old", removed), ("new", added)):
        for line in lines:
            if line.startswith("version:"):
                if not ("1.0.0" in body and "1.1.0" in body):
                    missing.append(f"{kind}: the version line (1.0.0 and 1.1.0)")
            elif support.flat(line) not in body:
                missing.append(f"{kind}: {line[:70]!r}")
    assert not missing, f"{support.CITP_REL} lacks the text of {len(missing)} changed line(s): {missing[:3]}"


def test_s5_the_impact_table_says_w2_11_does_not_cover_adopt_adapter_portability_differs_until_the_copies_act_and_w2_88a_unchanged():
    rows = [line for line in _record().splitlines() if line.lstrip().startswith("|")]
    flat_rows = [support.flat(row) for row in rows]
    problems = []
    if not any(re.search(r"w2-11(?!\d)", row) and "adopt" in row and "body" in row and "version" in row
               and re.search(r"(do(es)? not|don't|doesn't|never|neither|nor) (cover|include|reach)|not covered|no case covers", row)
               and re.search(r"stay|remain|unchanged|as they are|as is|not red|none red|no change|unaffected|not affected|"
                         r"still (pass|green)|green", row) for row in flat_rows):
        problems.append("no table row says W2-11's body and version cases do not cover `adopt` and so stay as they are")
    if not any("adapter-portability" in row and "generated_differs" in row and ".claude/skills/adopt/skill.md" in row
               and re.search(r"until|till|before", row) and re.search(r"\bact\b", row) for row in flat_rows):
        problems.append("no table row says `adapter-portability` reports `GENERATED_DIFFERS` on "
                        "`.claude/skills/adopt/SKILL.md` until the copies ACT")
    if not any("w2-88a" in row and "unchanged" in row for row in flat_rows):
        problems.append("no table row names W2-88a's cases with `unchanged`")
    assert not problems, f"{support.CITP_REL}'s impact table: {'; '.join(problems)}"


def test_s5_the_last_verdict_is_pass_after_an_independent_review():
    text = _record()
    low = text.lower()
    assert "independent" in low and re.search(r"review|auditor", low), f"{support.CITP_REL} does not record an independent review"
    stated = support.verdicts(text)
    assert stated, f"{support.CITP_REL} records no verdict (`verdict: PASS` or `FAIL`)"
    assert stated[-1].startswith("PASS"), f"the last verdict {support.CITP_REL} records is {stated[-1]!r}, not PASS (all: {stated})"


def test_s5_the_owner_approval_line_names_the_after_sha256():
    """Red until the owner's approval, by design: the owner writes it after the review, before the merge; the line reads
    `pending` (or has no hash) until then."""
    text = _record()
    after, _ = _after_or_fail()
    lines = [m.group(1) for m in re.finditer(r"(?mi)^\s*owner_approval:\s*(.*)$", text)]
    assert lines, f"{support.CITP_REL} has no `owner_approval:` line"
    value = lines[-1].strip().strip("'\"")
    assert after in value.lower(), f"the `owner_approval:` line does not name the after sha256 {after[:12]}...: {value[:80]!r}"
    assert "approved" in value.lower(), f"the `owner_approval:` line does not say `approved`: {value[:80]!r}"
