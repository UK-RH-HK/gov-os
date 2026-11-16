"""failure-1 (F1, the brief builder edits the skill's text; DEC-1204 (5); P-GOLDEN-RULE-1 section 3 F1; interface item 8).

The sha256 of the sections a judging brief carries equals that of the installed kernel file's sections 1 to 3: for the
approved 1.0.0 text, and for a 1.0.1 copy with one word of section 2 changed (installed as both the kernel file and the
preloaded copy), where the brief carries the changed text and its version, never the approved text: it follows the
installed file, not a hand copy.
"""

from __future__ import annotations

import pytest

import w2_195_support as s


def _carried(brief: str, want: str) -> str:
    """The bytes the brief carries from section 1's heading on, as long as the installed file's sections 1 to 3."""
    assert s.START in brief, "the brief carries no section 1 heading of judging-work"
    start = brief.index(s.START)
    return brief[start:start + len(want)]


@pytest.mark.parametrize("text_kind", ["approved-1.0.0", "changed-1.0.1"])
@pytest.mark.parametrize("which", list(s.JUDGING_BRIEFS))
def test_f1_the_sections_a_brief_carries_hash_as_the_installed_files_sections(tmp_path, which, text_kind):
    """failure-1: sha256(the sections the brief carries) == sha256(the installed kernel file's sections 1 to 3); with the
    changed 1.0.1 text, the brief names version 1.0.1 and does not hold the approved 1.0.0 sections."""
    approved = s.kernel_text()
    text = approved if text_kind == "approved-1.0.0" else s.variant(approved)
    version = s.VERSION if text_kind == "approved-1.0.0" else s.OTHER_VERSION
    project = s.BriefProject(tmp_path / "repo", kernel=text, copy=s.preloaded(text))
    want = s.sections(text)
    if text_kind == "approved-1.0.0":
        assert s.sha256(want) == s.SECTIONS_SHA256, "the plant: the approved sections' sha256 is not the lead's"
    brief = s.brief_text(project.brief(*s.JUDGING_BRIEFS[which]))
    carried = _carried(brief, want)
    assert s.sha256(carried) == s.sha256(want), (f"the {which} brief's sections hash {s.sha256(carried)[:12]}, the installed "
                                                 f"file's {s.sha256(want)[:12]}: the builder changed the text")
    assert s.version_lines(brief, version), f"no line of the {which} brief names judging-work and 'version {version}'"
    if text_kind == "changed-1.0.1":
        assert s.sections(approved) not in brief, f"the {which} brief carries the approved text, not the installed file's"
