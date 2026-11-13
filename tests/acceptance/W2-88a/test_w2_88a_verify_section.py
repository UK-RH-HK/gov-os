"""W2-88a, success 2 -- the adopt skill states the Verify pass (W2-174's skill line, moved word for word).

KPI line: "The adopt skill, in the kernel copy and the two generated-source copies, states the pass: when it runs (for a
ticket about to launch, not for the whole tracker), who writes the clauses (a product-spec session), what checks them
(the tool, the ticket's test designer, the auditor's sample), and that the owner approves the rule once. Verify: the
three files carry the section `Verify clauses for adopted tickets` with the four statements, and the three copies are
equal in that section."

Readings (also in the README):
* The heading's level is not stated: `##` or `###` is accepted; the section runs to the next heading of the same or a
  higher level (deeper headings belong to it). The title is the KPI's, case-insensitive, an optional trailing colon.
  The section appears exactly once in each file.
* The four statements are looked for in the section's own words (flattened, lower-cased):
  - when: a ticket "about to launch" (or about to start) AND a negation of the whole tracker (not / never ... the whole,
    entire or every tracker, backlog or tickets);
  - who writes: one sentence or list item with "product-spec", a form of "write" and "clauses";
  - what checks them: within a stretch around a "check/verify/review" word, ALL THREE: the tool, the test designer,
    the auditor's sample;
  - owner: one sentence or item with "owner", "approve..." and "once".
* The section's bytes (heading line to the line before the next same-or-higher heading) are equal in the three files.
"""

from __future__ import annotations

import re

import pytest

import w2_88a_support as support


def _sections():
    """``{path: [section, ...]}`` for the three files."""
    return {rel: support.verify_sections(support.read(rel)) for rel in support.ALL_REL}


def _the_section(rel):
    found = support.verify_sections(support.read(rel))
    if len(found) != 1:
        pytest.fail(f"{rel} has {len(found)} sections headed `{support.VERIFY_HEADING}` (## or ###); expected one",
                    pytrace=False)
    return found[0]


def test_s2_each_of_the_three_files_carries_the_section_once():
    """The kernel copy and the two generated-source copies each carry one section headed
    `Verify clauses for adopted tickets`."""
    counts = {rel: len(found) for rel, found in _sections().items()}
    bad = {rel: n for rel, n in counts.items() if n != 1}
    assert not bad, f"each file must carry the section `{support.VERIFY_HEADING}` exactly once; found {bad}"


def test_s2_the_section_says_when_the_pass_runs():
    """For a ticket about to launch, not for the whole tracker (all three files)."""
    for rel in support.ALL_REL:
        text = support.flat(_the_section(rel))
        missing = []
        if not any(re.search(pattern, text) for pattern in support.WHEN_ABOUT_TO_LAUNCH):
            missing.append("that it runs for a ticket about to launch")
        if not any(re.search(pattern, text) for pattern in support.WHEN_NOT_WHOLE_TRACKER):
            missing.append("that it does not run for the whole tracker")
        assert not missing, f"the section of {rel} does not state {' or '.join(missing)}"


def test_s2_the_section_says_a_product_spec_session_writes_the_clauses():
    """Who writes the clauses: a product-spec session (all three files)."""
    for rel in support.ALL_REL:
        found = support.sentence_with(_the_section(rel), support.WHO_WRITES)
        assert found, (f"the section of {rel} does not state that a product-spec session writes the clauses "
                       "(no sentence or item holds `product-spec`, a form of `write` and `clauses`)")


def test_s2_the_section_says_the_tool_the_test_designer_and_the_auditors_sample_check_them():
    """What checks the clauses: the tool, the ticket's test designer and the auditor's sample: all three (all three
    files)."""
    for rel in support.ALL_REL:
        found, missing = support.window_hits(_the_section(rel), support.WHAT_CHECKS_TRIGGER, support.WHAT_CHECKS_TERMS)
        assert not missing, (f"the section of {rel} does not state, where it says what checks the clauses, "
                             f"{' and '.join(missing)} (all three of the tool, the ticket's test designer and the "
                             f"auditor's sample are required)")


def test_s2_the_section_says_the_owner_approves_the_rule_once():
    """The owner approves the rule once (all three files)."""
    for rel in support.ALL_REL:
        found = support.sentence_with(_the_section(rel), support.OWNER_APPROVES_ONCE)
        assert found, (f"the section of {rel} does not state that the owner approves the rule once "
                       "(no sentence or item holds `owner`, `approve...` and `once`)")


def test_s2_the_three_copies_are_equal_in_that_section():
    """The section's bytes are equal in the kernel copy and in each generated-source copy."""
    kernel = _the_section(support.KERNEL_REL).encode("utf-8")
    for rel in support.COPIES_REL:
        other = _the_section(rel).encode("utf-8")
        if other != kernel:
            kernel_lines, other_lines = kernel.decode().splitlines(), other.decode().splitlines()
            first = next((i for i in range(max(len(kernel_lines), len(other_lines)))
                          if (kernel_lines[i] if i < len(kernel_lines) else None)
                          != (other_lines[i] if i < len(other_lines) else None)), 0)
            pytest.fail(f"the section `{support.VERIFY_HEADING}` of {rel} differs from the kernel copy's, first at "
                        f"its line {first + 1}: kernel "
                        f"{(kernel_lines[first] if first < len(kernel_lines) else '<none>')[:80]!r}, copy "
                        f"{(other_lines[first] if first < len(other_lines) else '<none>')[:80]!r}", pytrace=False)
