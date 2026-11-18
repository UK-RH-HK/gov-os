"""success-2 (S2, Briefed automatically; DEC-1204 (5); P-GOLDEN-RULE-1 section 3 S2; the lead's interface items 1 and 2).

A fixture project (this tree's kernel templates and facts file, one READY ticket) with the skill installed: the kernel file
``template/governance/kernel/skills/judging-work/SKILL.md`` and the preloaded copy ``.claude/skills/judging-work/SKILL.md``
(the generated form). Each judging brief (``gov brief independent-auditor``, ``gov brief qa-engineer``, ``gov brief lead
--run review``) holds sections 1 to 3 of the kernel file as one contiguous byte-for-byte substring and one line holding both
``judging-work`` and ``version 1.1.0``; the engineer's and the test designer's briefs hold neither.
"""

from __future__ import annotations

import pytest

import w2_195_support as s


@pytest.mark.parametrize("which", list(s.JUDGING_BRIEFS))
def test_s2_a_judging_brief_holds_sections_1_to_3_byte_for_byte_and_names_the_version(tmp_path, which):
    """success-2: the brief holds the kernel file's sections 1 to 3 as one substring, and a line naming ``judging-work`` and
    ``version 1.1.0``."""
    project = s.BriefProject(tmp_path / "repo")
    brief = s.brief_text(project.brief(*s.JUDGING_BRIEFS[which]))
    want = s.sections(s.kernel_text())
    assert want in brief, f"the {which} brief does not hold sections 1 to 3 of the installed judging-work skill, byte for byte"
    assert s.version_lines(brief, s.VERSION), f"no line of the {which} brief names judging-work and 'version {s.VERSION}'"


def test_s2_in_an_adopted_tree_the_auditor_brief_reads_governance_kernel(tmp_path):
    """success-2 (interface item 1, the ``template/``-presence rule): in a tree with no ``template/`` (the kernel templates
    and the skill under ``governance/kernel/``), the independent auditor's brief holds the sections of
    ``governance/kernel/skills/judging-work/SKILL.md`` and names its version."""
    project = s.BriefProject(tmp_path / "repo", adopted=True)
    assert not (project.root / "template").exists(), "the plant: the adopted tree holds a template/ folder"
    brief = s.brief_text(project.brief(*s.JUDGING_BRIEFS["independent-auditor"]))
    assert s.sections(s.kernel_text()) in brief, "the auditor brief in an adopted tree does not hold sections 1 to 3"
    assert s.version_lines(brief, s.VERSION), f"no line of the auditor brief names judging-work and 'version {s.VERSION}'"


@pytest.mark.parametrize("which", list(s.NON_JUDGING_BRIEFS))
def test_s2_a_non_judging_brief_holds_neither_the_sections_nor_the_version_line(tmp_path, which):
    """success-2 (the contrast): on the same fixture, where the auditor's brief carries the sections (asserted first, so
    the absence below is not a broken fixture), the ``which`` brief holds no part of them (neither section 1's heading nor
    the sections) and no line naming ``judging-work`` and its version."""
    project = s.BriefProject(tmp_path / "repo")
    auditor = s.brief_text(project.brief(*s.JUDGING_BRIEFS["independent-auditor"]))
    want = s.sections(s.kernel_text())
    assert want in auditor, "the contrast: the auditor brief on this fixture does not hold the sections, so nothing is shown"
    brief = s.brief_text(project.brief(*s.NON_JUDGING_BRIEFS[which]))
    assert want not in brief and s.START.strip() not in brief, f"the {which} brief carries the judging-work sections"
    assert not s.version_lines(brief, s.VERSION), f"the {which} brief names judging-work's version"
