"""Builder tests for the register's entries as records of their own (W2-03, AR-1).

Regression evidence only (DEC-136). They cover what the acceptance tests leave to the builder: where a span ends
(the blank lines before the next heading, a fenced block inside the entry), a comment opened and closed on one
line, the reason given for a heading outside the grammar, and the citations check's rule for a decision file.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check.citations import _decision  # noqa: E402
from gov.store.loader import register_entries  # noqa: E402

REGISTER = """\
# Decisions

### DEC-101 — One
- **Status:** ACCEPTED (owner, 2026-10-01)
- **Decision:** A body with a block:

```
# not a heading
### DEC-109 — not an entry
```

<!-- a note on one line -->
### DEC-102 — Two
- **Status:** PROPOSED

## A part
"""


def test_a_span_holds_its_fenced_block_and_ends_before_the_blank_lines_and_the_next_heading():
    live, refused = register_entries(REGISTER)
    assert refused == []
    one, two = live
    assert (one["id"], one["line"], two["id"], two["line"]) == ("DEC-101", 3, "DEC-102", 13)
    assert one["span"].endswith("<!-- a note on one line -->")
    assert "### DEC-109 — not an entry" in one["span"] and "### DEC-102" not in one["span"]
    assert two["span"] == "### DEC-102 — Two\n- **Status:** PROPOSED"
    assert two["content_hash"] == hashlib.sha256(two["span"].encode("utf-8")).hexdigest()


def test_a_heading_outside_the_grammar_and_a_duplicate_are_named_with_their_lines():
    text = ("### DEC-13 — Short\n- **Status:** ACCEPTED\n\n### DEC-200 — A\n- **Status:** ACCEPTED\n\n"
            "### DEC-200 — B\n- **Status:** ACCEPTED\n")
    live, refused = register_entries(text)
    assert live == []
    assert refused[0].startswith("DEC-13 at line 1 is no id of the decision_id grammar")
    assert "DEC-200 stands under 2 headings of the register, at lines 4 and 7" in refused[1]


def test_only_a_schema_valid_decision_file_records_its_id_for_a_citation():
    valid = {"id": "DEC-120", "type": "decision", "status": "ACTIVE", "state_class": "AUTHORITATIVE"}
    assert _decision(valid) == "DEC-120"
    for change in ({"id": "dec-120"}, {"id": 120}, {"type": "note"}, {"status": ""}, {"state_class": "OTHER"}):
        assert _decision({**valid, **change}) == "", change
