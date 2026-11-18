"""W2-197 S7 (DAEO-3d3o): ``gov adopt --facts`` writes the retrieve form with the question as text the session
replaces, never a ``{QUESTION}`` slot (audit 2 M3, R7)."""

from __future__ import annotations

import datetime

import yaml

from gov.adopt import facts


def test_the_written_retrieve_form_names_the_question_as_text(tmp_path):
    facts.write_default(tmp_path, datetime.date(2026, 11, 17))
    written = yaml.safe_load((tmp_path / "governance/project/facts.yaml").read_text(encoding="utf-8"))
    assert written["commands"]["retrieve"]["run"] == 'gov retrieve "<question>"'
    assert "{QUESTION}" not in (tmp_path / "governance/project/facts.yaml").read_text(encoding="utf-8")
