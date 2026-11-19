"""Builder tests for the 4-characters-a-token counter at its new home, ``gov.util.tokens`` (W2-200 S1; DEC-1214 M1)."""
from __future__ import annotations

import pytest

from gov.util import tokens


@pytest.mark.parametrize("text, counted", [("", 0), ("a", 1), ("abcd", 1), ("abcde", 2), ("x" * 4000, 1000),
                                           ("x" * 4001, 1001)])
def test_a_token_is_four_characters_rounded_up(text, counted):
    assert tokens.TOKEN_CHARS == 4
    assert tokens._tokens(text) == counted


def test_the_four_helpers_take_the_counter_from_gov_util_tokens():
    from gov.check import skill_validator
    from gov.telemetry import counter, sessionlog

    assert counter._tokens is tokens._tokens and sessionlog._tokens is tokens._tokens
    assert skill_validator.TOKEN_CHARS is tokens.TOKEN_CHARS
    import inspect

    from gov.retrieval import supplementary
    assert "from gov.util.tokens import _tokens" in inspect.getsource(supplementary)
