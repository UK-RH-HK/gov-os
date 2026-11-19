"""The 4-characters-a-token counter (W2-200; DEC-1214 M1): moved from the retired ``gov.context``, counting as before.

An estimate by length, never a tokenizer's count: the telemetry counter, the session-log reader, the skill validator
and the supplementary block size a text with it.
"""

from __future__ import annotations

TOKEN_CHARS = 4


def _tokens(text: str) -> int:
    """``text``'s size in tokens: its characters divided by ``TOKEN_CHARS``, rounded up."""
    return -(-len(text) // TOKEN_CHARS)
