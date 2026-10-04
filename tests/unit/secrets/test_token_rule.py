"""Builder tests for the repaired token rule (W1-16; DEC-324, DEC-325).

Regression evidence only (DEC-136). The rule is written as three expressions
without look-ahead. They are held here against the requirement written with
look-ahead, which gitleaks cannot run, over generated bodies around the floor
of 16 characters: the same strings are flagged, and the match is the whole
token. The two gitleaks files hold the same rules. No binary is run.
"""
from __future__ import annotations

import itertools
import random
import re
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FILES = (".gitleaks.toml", "template/.gitleaks.toml")
# DEC-325: a digit, or both cases, in a body of 16 characters or more that begins with a letter or a digit.
REQUIREMENT = re.compile(r"\b(?:sk|pk|rk|tok)[_-](?=[\w-]*\d|[\w-]*[a-z][\w-]*[A-Z]|[\w-]*[A-Z][\w-]*[a-z])"
                         r"[A-Za-z0-9][\w-]{15,}")


def _rules(rel):
    return tomllib.loads((REPO / rel).read_text(encoding="utf-8"))["rules"]


def _token_rules(rel):
    return [re.compile(rule["regex"]) for rule in _rules(rel) if rule["id"].startswith("gov-token")]


def test_the_two_files_hold_the_same_rules():
    assert _rules(FILES[0]) == _rules(FILES[1])


def test_the_three_expressions_flag_what_the_requirement_flags():
    rules = _token_rules(FILES[0])
    assert len(rules) == 3
    chooser = random.Random(116)
    bodies = ["".join(chooser.choice(alphabet) for _ in range(length))
              for alphabet in ("ab_-", "AB_-", "abAB_-", "ab7_-", "AB7_-", "aB7_-")
              for length in range(13, 20) for _ in range(200)]
    # One character of another kind at every place of a body of exactly 16 and of 15 characters.
    bodies += [("a" * length)[:place] + other + ("a" * length)[place + 1:]
               for length in (15, 16) for place in range(length) for other in "A7_"]
    bodies += [("A" * length)[:place] + other + ("A" * length)[place + 1:]
               for length in (15, 16) for place in range(length) for other in "a7-"]
    wrong = []
    for prefix, separator, body in itertools.product(("sk", "tok"), "_-", bodies):
        text = f"The value is {prefix}{separator}{body} today."
        # The whole token is the match: an allowlist expression of a project is compared with it.
        found = {match.group() for rule in rules if (match := rule.search(text))}
        if found != {match.group() for match in [REQUIREMENT.search(text)] if match}:
            wrong.append(text)
    assert not wrong, wrong[:10]
