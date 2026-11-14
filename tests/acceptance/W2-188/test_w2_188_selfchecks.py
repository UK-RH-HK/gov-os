"""The readers' own checks on made-up texts (green now, by design): they guard the tolerance and the strictness of the
folder's matchers; they read no repository file."""

from __future__ import annotations

import w2_188_support as support


def test_selfcheck_a_step_6_stretch_runs_from_the_6_line_to_the_7_line():
    text = "5. five\n6. Declare and\n   measure.\n7. Record every method.\n"
    assert support.stretch_between(text, 6, 7) == "6. Declare and\n   measure."
    assert support.stretch_between("5. five\n6. six\n", 6, 7) is None


def test_selfcheck_the_permission_reader_names_an_unnegated_statement_and_passes_a_negated_one():
    assert support.permission_violations("The standing set may choose a fix when it misses.")
    assert support.permission_violations("The standing set is used to adopt or reject a fix.")
    assert support.permission_violations("Choose a fix on the standing set.")
    assert not support.permission_violations("The standing set never chooses or judges a fix.")
    assert not support.permission_violations("The standing set may not choose a fix; fixes are chosen on the tuning set.")
    assert not support.permission_violations("Fixes are chosen only on the tuning set, never on the standing set.")
    assert not support.permission_violations("Fixes are chosen on the tuning set and the fresh sets' misses; the standing set only counts.")


def test_selfcheck_the_second_reranker_reader_names_an_unrefused_mention_only():
    assert support.second_reranker_misuse("The reader is a second reranking model.")
    assert not support.second_reranker_misuse("W2-88 S10's second reranking model stays forbidden.")
    assert not support.second_reranker_misuse("The reader is not a second reranking model.")
    assert support.second_reranker_misuse("A miss is never re-scored. The reader is a second reranking model.")


def test_selfcheck_the_hunk_parser_reads_lengths_and_the_omitted_length_of_one():
    diff = "@@ -4 +4 @@\n-a\n+b\n@@ -59,0 +60,2 @@\n+x\n+y\n@@ -74,1 +76 @@\n-c\n+d\n"
    assert support.parse_hunks(diff) == [(4, 1, 4, 1), (59, 0, 60, 2), (74, 1, 76, 1)]


def test_selfcheck_a_wrapped_text_equals_its_one_line_form_and_the_5_point_rules_are_counted():
    wrapped = "- **Below 95 %:** the package's\n  §5.1 rules R1 to R9 (a miss\n  recorded)."
    assert support.collapse(wrapped) == "- **Below 95 %:** the package's §5.1 rules R1 to R9 (a miss recorded)."
    assert support.five_point_count("within 5 points of the standing set; or 5 points below it; a 5-point fall") == 3
    assert support.five_point_count("15 points; 50 points") == 0
