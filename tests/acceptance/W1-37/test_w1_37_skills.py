"""W1-37 — the three Superpowers skills copied into ``skills/superpowers/``, with their record.

One test per KPI line of ticket ``DAEO-yvzh`` (profile LITE, DEC-221), read with
DEC-244 (the copy and its only source), DEC-245 (the namespace is the folder,
the files are byte-identical), DEC-246 (the record file) and DEC-247 (the
sizes). The README states the record file's contract.

The tests read the working tree. Nothing is installed, downloaded or run.
No test asserts whether a ``SKILL.md`` carries a version in its frontmatter:
DEC-245 leaves that with the owner.
"""

from __future__ import annotations

import w1_37_support as support


def test_the_three_skills_are_copied_from_v6_4_2_into_the_namespace_with_the_source_hash_recorded(
        vendor, copy, record):
    """Success 1: "… copied from v6.4.2, namespaced, with source hash recorded"."""
    links = support.symlinks(support.COPY_REL)
    assert links == [], f"{support.COPY_REL}/ holds symbolic links, not copies: {links}"

    for skill in support.SKILLS:
        source = support.under(vendor, f"skills/{skill}")
        target = support.under(copy, skill)
        assert source, f"{support.VENDOR_SKILLS_REL}/{skill}/ holds no file: the source of {skill} is missing"
        assert sorted(target) == sorted(source), (
            f"{support.COPY_REL}/{skill}/ does not hold the files of {support.VENDOR_SKILLS_REL}/{skill}/: "
            f"missing {sorted(set(source) - set(target))}, extra {sorted(set(target) - set(source))}"
        )
        changed = sorted(rel for rel in source if target[rel] != source[rel])
        assert changed == [], (
            f"files under {support.COPY_REL}/{skill}/ that are not byte-identical to the vendor copy (DEC-245): "
            f"{changed}"
        )

    assert support.norm_version(record.get("version", "")) == support.VERSION, (
        f"{support.RECORD_REL}: `version` is {record.get('version')!r}, the source version is v{support.VERSION}"
    )
    expected = support.folder_digest(vendor)
    recorded = support.recorded_sha256(record, "source_sha256")
    assert recorded == expected, (
        f"{support.RECORD_REL} records source_sha256 {recorded}; the digest of the {len(vendor)} files under "
        f"{support.VENDOR_REL}/ by the DEC-199 rule is {expected}"
    )


def test_the_token_sizes_are_measured_and_within_the_figures_and_no_plugin_hook_or_excluded_skill_is_there(
        copy, record):
    """Success 2: "Token sizes measured and within the I-09 figures; no plugin, no SessionStart hook, no
    subagent-driven-development"."""
    measured = {}
    for skill, ceiling in support.CEILINGS.items():
        rel = f"{skill}/SKILL.md"
        assert rel in copy, f"{support.COPY_REL}/{rel} does not exist"
        measured[skill] = support.token_size(copy[rel])
        assert measured[skill] <= ceiling, (
            f"{support.COPY_REL}/{rel} measures {measured[skill]} tokens (floor(characters / 4), DEC-247); "
            f"the figure is {ceiling}, with no tolerance"
        )
    sizes = record.get("token_sizes")
    assert isinstance(sizes, dict) and all(type(value) is int for value in sizes.values()), (
        f"{support.RECORD_REL}: `token_sizes` must map each skill to an integer, got {sizes!r}"
    )
    assert sizes == measured, (
        f"{support.RECORD_REL} records token_sizes {sizes}; the sizes measured on the copy are {measured}"
    )

    plugin = sorted(rel for rel in copy if support.is_plugin(rel))
    assert plugin == [], f"{support.COPY_REL}/ holds plugin files: {plugin}"
    hooks = sorted(rel for rel in copy if support.is_hook(rel))
    assert hooks == [], f"{support.COPY_REL}/ holds hook files (no SessionStart hook): {hooks}"
    excluded = sorted(rel for rel in copy if support.EXCLUDED_SKILL in support.parts(rel))
    assert excluded == [], f"{support.COPY_REL}/ holds {support.EXCLUDED_SKILL} (DEC-074 Q5, DEC-076): {excluded}"


def test_no_other_superpowers_skill_or_hook_is_present(vendor, copy):
    """Failure 1: "Any other Superpowers skill or hook is present"."""
    for skill in support.SKILLS:
        assert f"{skill}/SKILL.md" in copy, f"{support.COPY_REL}/{skill}/SKILL.md does not exist"

    other_skills = sorted(rel for rel in copy
                          if rel.split("/")[-1].lower() == "skill.md"
                          and rel not in {f"{skill}/SKILL.md" for skill in support.SKILLS})
    assert other_skills == [], f"{support.COPY_REL}/ holds a skill that is not one of the three: {other_skills}"
    hooks = sorted(rel for rel in copy if support.is_hook(rel))
    assert hooks == [], f"{support.COPY_REL}/ holds hook files: {hooks}"

    allowed_at_top = {support.RECORD_NAME, support.LICENCE_NAME}
    other = sorted(rel for rel in copy if rel.split("/")[0] not in support.SKILLS and rel not in allowed_at_top)
    assert other == [], (
        f"files under {support.COPY_REL}/ that are neither in one of the three skill folders, nor the record "
        f"file, nor the upstream licence: {other}"
    )
    if support.LICENCE_NAME in copy:
        assert copy[support.LICENCE_NAME] == vendor.get(support.LICENCE_NAME), (
            f"{support.COPY_REL}/{support.LICENCE_NAME} is not byte-identical to the vendor folder's licence"
        )


def test_no_vendored_file_differs_from_its_recorded_hash(copy, record):
    """Failure 2: "A vendored file differs from its recorded hash"."""
    files = support.copied(copy)
    assert files, f"{support.COPY_REL}/ holds no file but the record"
    expected = support.folder_digest(files)
    recorded = support.recorded_sha256(record, "sha256")
    assert recorded == expected, (
        f"{support.RECORD_REL} records sha256 {recorded}; the digest of the {len(files)} files under "
        f"{support.COPY_REL}/ ({support.RECORD_NAME} left out) by the DEC-199 rule is {expected}: "
        f"a vendored file differs from its recorded hash"
    )
    # The recorded hash catches a change to any single file.
    undetected = sorted(rel for rel, content in files.items()
                        if support.folder_digest({**files, rel: content + b"\n"}) == recorded)
    assert undetected == [], f"a change to these files would leave the recorded sha256 matching: {undetected}"
