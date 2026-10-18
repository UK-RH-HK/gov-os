"""KPI success line 4 [DEC-730]: the ``wbs_id`` grammar accepts an id with one lower-case letter suffix
(``W2-15a``) and still refuses any other form. Its one definition is
``template/governance/kernel/schemas/common.schema.json``.

The KPI line lists ``W2-15`` among the refused forms. DEC-730's own grammar (``^W[0-9]+-[0-9]{2,}[a-z]?$``)
accepts it, every ticket's ``wbs_id`` here has that form, and W1-08's acceptance test holds ``W1-08`` as a real
id. That form is package P-1 and no case here holds it either way; see the README.

The pattern is read from the file and applied as a regular expression, as W1-08's and W1-30's suites do.
"""

from __future__ import annotations

import re

import pytest

import w2_02_support as support

ACCEPTED = ("W2-15a", "W2-15b", "W10-123z")
REFUSED = ("W2-15ab", "W2-15A", "W2-1", "W2-1a", "W2-15-a", "w2-15a", "W2-15a ", "W2-")


def _pattern():
    shape = support.common_schema()["$defs"].get("wbs_id") or {}
    pattern = shape.get("pattern")
    assert isinstance(pattern, str), f"{support.COMMON_SCHEMA} defines no `wbs_id` pattern"
    return pattern


@pytest.mark.parametrize("wbs_id", ACCEPTED)
def test_the_wbs_id_grammar_accepts_one_lower_case_letter_suffix(wbs_id):
    """Red today: ``^W[0-9]+-[0-9]{2,}$`` refuses the suffix."""
    assert re.search(_pattern(), wbs_id), f"the wbs_id grammar {_pattern()} refuses {wbs_id!r}"


@pytest.mark.parametrize("wbs_id", REFUSED)
def test_the_wbs_id_grammar_still_refuses_every_other_form(wbs_id):
    """Two letters, an upper-case letter, a one-digit number (with or without a letter), a dash before the
    letter, a lower-case ``w``, a trailing blank, no number. Passes today ("still"); held so the widening stays
    one lower-case letter."""
    assert not re.search(_pattern(), wbs_id), f"the wbs_id grammar {_pattern()} accepts {wbs_id!r}"


def test_the_ticket_schema_takes_its_wbs_id_grammar_from_the_one_definition():
    """``ticket.schema.json`` refers to ``common.schema.json#/$defs/wbs_id`` and writes no wbs pattern of its own;
    no other kernel schema file, nor any file under ``schemas/``, writes a ``wbs_id`` pattern. Passes today; held
    so the widening is made in the one place."""
    ticket = support.kernel_schema_files()["ticket.schema.json"]
    assert (ticket.get("properties") or {}).get("wbs_id") == {"$ref": "common.schema.json#/$defs/wbs_id"}
    common = support.REPO_ROOT / support.KERNEL_SCHEMAS_REL / support.COMMON_SCHEMA
    others = sorted((support.REPO_ROOT / support.KERNEL_SCHEMAS_REL).glob("*.json")) + \
        sorted((support.REPO_ROOT / "schemas").rglob("*.json"))
    own = [str(path.relative_to(support.REPO_ROOT)) for path in others if path != common
           and re.search(r'"wbs[_a-z]*"\s*:\s*\{[^{}]*"pattern"', path.read_text(encoding="utf-8"))]
    assert not own, f"files that write a wbs_id pattern of their own: {own}"
