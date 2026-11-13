"""The predicates of KPI success 2, held on sample texts: they are narrow enough that a true refusal passes and the
old words fail. These cases judge the suite's own helpers, not the code under test; they are green before and after."""

from __future__ import annotations

import w2_113_support as support

# The refusal of the base (``gov.guard.install.cto_install`` before W2-113), for a project with no roster key.
OLD = ("installs are refused in every session: the project's coordination ticket is not set (governance/project/"
       "roster.yaml has no text value for the top-level key 'coordination_ticket'). Set the top-level key "
       "'coordination_ticket' in governance/project/roster.yaml to the id or WBS id of the coordination ticket in "
       ".tickets/ (set at adoption); until then raise the install as a P1 escalation to the CTO, who asks the owner "
       "(DEC-957)")
# A true text: it names GOV_TICKET, says where and how to set the key, and claims nothing.
TRUE = ("installs are refused in every session: the project's coordination ticket is not set "
        "(governance/project/roster.yaml has no text value for the top-level key 'coordination_ticket'). The CTO's "
        "session is the orchestrator whose GOV_TICKET is that ticket: set the top-level key 'coordination_ticket' in "
        "governance/project/roster.yaml to its id or WBS id (gov adopt --lite --stage A0 writes it; it is to be set "
        "at adoption); until then raise the install as a P1 escalation to the CTO, who asks the owner (DEC-957)")
LYING = (TRUE + " The key names the coordination ticket.")


def test_the_old_words_claim_a_key_was_set_and_do_not_name_the_variable():
    assert support.claims_a_key_was_set(OLD, key_exists=False) == ["set at adoption"]
    assert not support.names_the_variable(OLD)
    assert support.says_how_to_set_the_key(OLD)


def test_a_true_text_passes_every_predicate():
    assert support.claims_a_key_was_set(TRUE, key_exists=False) == []
    assert support.claims_a_key_was_set(TRUE, key_exists=True) == []
    assert support.names_the_variable(TRUE) and support.says_how_to_set_the_key(TRUE)


def test_a_text_that_speaks_of_the_value_of_a_key_that_is_not_there_is_caught():
    assert support.claims_a_key_was_set(LYING, key_exists=False)
    assert support.claims_a_key_was_set(LYING, key_exists=True) == []   # where a key exists, "names" may be true


def test_other_false_claims_are_caught():
    for text in ("the key was set at the last adoption", "the key has been set by adoption", "the key is already set",
                 "the key was written by adoption", "(set at adoption)"):
        assert support.claims_a_key_was_set(text, key_exists=True), text
    for text in ("the key is not set", "no key has been set", "no key was written", "adoption writes the key",
                 "set it by hand", "the key should be set at adoption", "it must be set at adoption",
                 "the key is not already set"):
        assert support.claims_a_key_was_set(text, key_exists=False) == [], text
