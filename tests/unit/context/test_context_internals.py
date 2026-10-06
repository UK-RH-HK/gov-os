"""Unit tests for gov.context internal helpers."""

from __future__ import annotations

from gov.context import _tokens, PRECEDENCE_RANK, TOKEN_CHARS


def test_tokens_empty():
    assert _tokens("") == 0


def test_tokens_exact_multiple():
    assert _tokens("abcd") == 1
    assert _tokens("abcdefgh") == 2


def test_tokens_rounds_up():
    assert _tokens("a") == 1
    assert _tokens("ab") == 1
    assert _tokens("abc") == 1
    assert _tokens("abcde") == 2


def test_tokens_matches_ceil_rule():
    for length in range(0, 50):
        text = "x" * length
        expected = -(-length // TOKEN_CHARS)
        assert _tokens(text) == expected, f"length {length}"


def test_precedence_order():
    order = sorted(PRECEDENCE_RANK, key=PRECEDENCE_RANK.get)
    assert order == ["charter", "contract", "decision", "specification", "ticket"]
