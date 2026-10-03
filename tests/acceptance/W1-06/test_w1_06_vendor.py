"""W1-06 — the Superpowers v6.4.2 source in the repository: three skills and the licence, nothing else.

KPI success 2, first half: "The Superpowers v6.4.2 source is available for
vendoring".

DEC-194 (DP-3): "Only the three skill folders (test-driven-development,
systematic-debugging, verification-before-completion) and the upstream licence
are committed, unchanged, under ``template/governance/kernel/vendor/superpowers/``.
The plugin, its hook and every other skill never enter the repository. The
scratch clone is deleted afterwards." (DEC-074 Q5, DEC-076:
subagent-driven-development is excluded.)

The tests read the working tree and ask git what it tracks. They do not fix
whether a skill folder sits directly in the vendor folder or under ``skills/``
as upstream has it. "Unchanged" cannot be compared with upstream without a
download; what is checked is that each ``SKILL.md`` still declares its own
skill.
"""

from __future__ import annotations

import re

import pytest

import w1_06_support as support

ROOT = support.REPO_ROOT / support.VENDOR_REL

PLUGIN_FILES = ("plugin.json", "marketplace.json")
HOOK_FILES = ("hooks.json",)
EXCLUDED_SKILL = "subagent-driven-development"


def _skill_files(vendor, skill):
    """The ``SKILL.md`` files that sit directly in a folder named ``skill``."""
    return [rel for rel in vendor if rel.split("/")[-2:] == [skill, "SKILL.md"]]


def _parts(rel):
    return [part.lower() for part in rel.split("/")]


def test_the_vendor_folder_is_committed(vendor):
    assert vendor, f"{support.VENDOR_REL}/ holds no file"
    tracked = set(support.tracked_files(support.VENDOR_REL))
    untracked = [rel for rel in vendor if f"{support.VENDOR_REL}/{rel}" not in tracked]
    assert untracked == [], f"files under {support.VENDOR_REL}/ that git does not track: {untracked}"
    assert support.is_committed_unchanged(support.VENDOR_REL), (
        f"{support.VENDOR_REL}/ differs from the committed folder: the source of record is the committed one"
    )


@pytest.mark.parametrize("skill", support.SKILLS)
def test_a_skill_folder_is_there_with_its_skill_md(vendor, skill):
    found = _skill_files(vendor, skill)
    assert found, f"{support.VENDOR_REL}/ has no {skill}/SKILL.md (files: {vendor})"
    assert len(found) == 1, f"{support.VENDOR_REL}/ holds {skill}/SKILL.md {len(found)} times: {found}"
    assert (ROOT / found[0]).read_text(encoding="utf-8").strip(), f"{support.VENDOR_REL}/{found[0]} is empty"


@pytest.mark.parametrize("skill", support.SKILLS)
def test_a_skill_md_declares_the_skill_of_its_folder(vendor, skill):
    """An unchanged upstream ``SKILL.md`` opens with frontmatter whose ``name`` is the folder's name."""
    found = _skill_files(vendor, skill)
    assert found, f"{support.VENDOR_REL}/ has no {skill}/SKILL.md"
    text = (ROOT / found[0]).read_text(encoding="utf-8")
    frontmatter = re.match(r"---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    assert frontmatter, f"{support.VENDOR_REL}/{found[0]} does not open with frontmatter"
    name = re.search(r"^name:\s*[\"']?([^\"'\r\n]+?)[\"']?\s*$", frontmatter.group(1), re.MULTILINE)
    assert name and name.group(1) == skill, (
        f"{support.VENDOR_REL}/{found[0]} declares the skill {name.group(1) if name else None!r}, not {skill!r}"
    )


def test_the_upstream_licence_is_there(vendor):
    licences = [rel for rel in vendor if support.is_licence(rel)]
    assert licences, (
        f"{support.VENDOR_REL}/ holds no licence file (LICENSE, LICENCE or COPYING) outside the skill folders: "
        f"{vendor}"
    )
    for rel in licences:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "copyright" in text.lower(), f"{support.VENDOR_REL}/{rel} does not read as a licence text"


def test_no_other_skill_is_there(vendor):
    others = [rel for rel in vendor
              if rel.split("/")[-1].lower() == "skill.md" and "/".join(rel.split("/")[-2:-1]) not in support.SKILLS]
    assert others == [], f"{support.VENDOR_REL}/ holds a skill that is not one of the three: {others}"
    excluded = [rel for rel in vendor if EXCLUDED_SKILL in _parts(rel)]
    assert excluded == [], f"{support.VENDOR_REL}/ holds {EXCLUDED_SKILL} (excluded by DEC-074 Q5): {excluded}"


def test_no_plugin_is_there(vendor):
    plugin = [rel for rel in vendor
              if _parts(rel)[-1] in PLUGIN_FILES or any("plugin" in part for part in _parts(rel)[:-1])]
    assert plugin == [], f"{support.VENDOR_REL}/ holds plugin files (DEC-194: the plugin never enters): {plugin}"


def test_no_hook_is_there(vendor):
    hooks = [rel for rel in vendor
             if "hooks" in _parts(rel)[:-1] or _parts(rel)[-1] in HOOK_FILES
             or _parts(rel)[-1].startswith(("session-start", "sessionstart"))]
    assert hooks == [], f"{support.VENDOR_REL}/ holds hook files (DEC-194: the hook never enters): {hooks}"


def test_nothing_but_the_three_skills_and_the_licence_is_there(vendor):
    """DEC-194: "Only the three skill folders … and the upstream licence are committed"."""
    other = [rel for rel in vendor if support.skill_of(rel) is None and not support.is_licence(rel)]
    assert other == [], (
        f"files under {support.VENDOR_REL}/ that are neither in one of the three skill folders nor the licence: "
        f"{other}"
    )


def test_the_excluded_parts_are_nowhere_in_the_repository(vendor):
    """DEC-194: "The plugin, its hook and every other skill never enter the repository"."""
    found = [path for path in support.tracked_files()
             if EXCLUDED_SKILL in _parts(path) or ".claude-plugin" in _parts(path)]
    assert found == [], f"the repository tracks parts of Superpowers that DEC-194 keeps out: {found}"


@pytest.mark.local_only
def test_the_scratch_clone_is_deleted(vendor):
    """DEC-194: "The scratch clone is deleted afterwards" (DEC-193 names the folder). Only its presence is asked."""
    clone = support.REPO_ROOT / support.SCRATCH_CLONE_REL
    assert not clone.exists(), f"{support.SCRATCH_CLONE_REL}/ is still there after the source was committed"
