"""K3 (measured on this repository, the engineer's evidence) [DEC-1014, DEC-996 item 3 A].

No test runs the measurement. One case holds that ``docs/changes/W2-122-evidence.md`` exists in the tree under test
and names what K3 asks for: the semantic stage's seconds and the embedding requests sent, a seeded first rebuild
against a cold one, alone and with two others running.
"""

from __future__ import annotations

import re

import w2_122_support as support


def test_the_evidence_file_names_the_measurement():
    path = support.REPO_ROOT / support.EVIDENCE_REL
    assert path.is_file(), f"no evidence file at {support.EVIDENCE_REL}"
    text = path.read_text(encoding="utf-8").lower()

    for words, what in ((("seeded", "seed"), "the seeded rebuild"), (("cold",), "the cold rebuild"),
                        (("semantic",), "the semantic stage"), (("second", " s ", "s)", "_s"), "its seconds"),
                        (("request",), "the embedding requests sent"), (("alone",), "the rebuild alone"),
                        (("two others", "two other", "three at once", "three rebuilds"), "with two others running")):
        assert any(word in text for word in words), f"the evidence file does not name {what} ({words})"
    assert re.search(r"\d", text), "the evidence file gives no figure"
