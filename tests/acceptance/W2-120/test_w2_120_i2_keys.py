"""success-1, I1 and I2: a skill whose front matter carries a key outside the skill template's list is refused, naming the
file and the key; a clean skill passes; a missing ``output`` is not refused (the deferred half).

Each case plants a project in ``tmp_path`` (the skill clean in the kernel folder and the three generated folders, then
one copy changed) and runs the check as ``skill-regression-a`` runs it, a process from the project's root (README).
"""

from __future__ import annotations

import pytest

import w2_120_support as sup


@pytest.mark.parametrize("key", list(sup.PERMISSION_KEYS))
def test_i2_a_kernel_skill_with_a_listed_permission_key_is_refused_naming_file_and_key(tmp_path, key):
    """I2 (permission keys) and I1 (four fields, exit 1): one planted kernel skill per listed key."""
    copies = sup.plant_clean(tmp_path, "alpha")
    planted = sup.plant_with(tmp_path, sup.KERNEL, "alpha", {key: sup.PERMISSION_KEYS[key]})
    assert planted == copies[sup.KERNEL]
    run = sup.run_on(tmp_path, "alpha")
    finding = sup.assert_refused(run, tmp_path, planted, key)
    assert finding["code"] != sup.VENDORED_CODE, "a non-vendored skill is refused, not merely named (I4)"


@pytest.mark.parametrize("key", ["license", "colour"])
def test_i2_a_kernel_skill_with_any_other_key_is_refused_naming_file_and_key(tmp_path, key):
    """I2 (any key outside the template's list): ``license`` and a made-up key."""
    sup.plant_clean(tmp_path, "alpha")
    planted = sup.plant_with(tmp_path, sup.KERNEL, "alpha", {key: "x"})
    run = sup.run_on(tmp_path, "alpha")
    sup.assert_refused(run, tmp_path, planted, key)


def test_i2_two_refused_keys_in_one_skill_are_each_named(tmp_path):
    """I1 and I2: one finding names each refused key of the file (naming the file and the key)."""
    sup.plant_clean(tmp_path, "alpha")
    planted = sup.plant_with(tmp_path, sup.KERNEL, "alpha", {"model": "opus", "effort": "high"})
    run = sup.run_on(tmp_path, "alpha")
    sup.assert_refused(run, tmp_path, planted, "model")
    sup.assert_refused(run, tmp_path, planted, "effort")


def test_i2_a_clean_kernel_skill_passes_with_no_findings(tmp_path):
    """I2 and I1: name, version, description, output and metadata.version only: exit 0, ``{"findings": []}``."""
    sup.plant_clean(tmp_path, "alpha")
    run = sup.run_on(tmp_path, "alpha")
    sup.assert_passes(run)
    assert run.data == {"findings": []}, run.out


def test_deferred_a_skill_with_no_output_key_is_not_refused(tmp_path):
    """The ticket's "Deferred" line: a missing ``output`` is not refused by this ticket. KPI success-1's "one with no
    output class" is tested as: such a skill, otherwise clean, gives no refusing finding and exit 0."""
    sup.plant_clean(tmp_path, "alpha")
    front = sup.kernel_front("alpha")
    del front["output"]
    sup.write_skill(tmp_path, sup.KERNEL, "alpha", front)
    run = sup.run_on(tmp_path, "alpha")
    assert run.code == 0, run.text()
    assert not sup.refusing(run.findings), run.out


def test_i1_every_finding_carries_code_file_key_and_message(tmp_path):
    """I1: each finding, key-related or not, has ``code``, ``file``, ``key`` and ``message`` (a value for ``key`` that
    is no key is not pinned); here a skill with no description plus one with a refused key."""
    sup.plant_clean(tmp_path, "alpha")
    sup.plant_clean(tmp_path, "beta")
    front = sup.kernel_front("alpha")
    del front["description"]
    broken = sup.write_skill(tmp_path, sup.KERNEL, "alpha", front)
    sup.plant_with(tmp_path, sup.KERNEL, "beta", {"permissions": ["read"]})
    run = sup.run_on(tmp_path, "alpha", "beta")
    assert run.code == 1, run.text()
    assert len(run.findings) >= 2, run.out
    for finding in run.findings:
        for field in ("code", "file", "key", "message"):
            assert field in finding, f"finding lacks {field!r}: {finding}"
    assert sup.about(run, tmp_path, broken), f"no finding names {broken}: {run.out}"


def test_i2_a_generated_claude_copy_of_name_description_and_metadata_passes(tmp_path):
    """I2 (``.claude/skills/``: name, description and metadata): a copy with no top-level ``version`` or ``output`` is
    clean (rulesync drops them), so the live generated copies are not refused for what the generator drops."""
    sup.plant_clean(tmp_path, "alpha")
    run = sup.run_on(tmp_path, "alpha")
    sup.assert_passes(run)
    assert (tmp_path / sup.CLAUDE / "alpha" / "SKILL.md").is_file()


@pytest.mark.parametrize("key,value", [("version", "1.0.0"), ("output", "none")])
def test_i2_a_generated_claude_copy_with_a_kernel_only_key_is_refused(tmp_path, key, value):
    """I2: for ``.claude/skills/`` the list is name, description and metadata, so a copy that also carries the
    kernel's ``version`` or ``output`` is refused, naming the ``.claude`` file and the key (README, reading 1)."""
    sup.plant_clean(tmp_path, "alpha")
    planted = sup.plant_with(tmp_path, sup.CLAUDE, "alpha", {key: value})
    run = sup.run_on(tmp_path, "alpha")
    sup.assert_refused(run, tmp_path, planted, key)
    assert sup.files_named(run, tmp_path) == {planted.resolve()}, run.out
