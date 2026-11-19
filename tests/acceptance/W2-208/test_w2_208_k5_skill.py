"""K5: the ``judging-work`` skill is shipped to every adopted repository and its text agrees with the head; its two
copies stay byte-equal; its version is raised (DEC-1217 (7); EMERGENCY-2 3.7)."""

from __future__ import annotations

import w2_208_support as support


def _missing_phrases(text, phrases):
    found = support.normalise(text).lower()
    return [phrase for phrase in phrases if phrase not in found]


def assert_carries_the_rules(text, what):
    missing = _missing_phrases(text, (*support.SKILL_PHRASES, *support.VALUE_FIRST))
    assert not missing, f"{what} lacks the head's key phrases {missing}"


def test_k5_the_two_copies_are_byte_equal_shipped_carry_the_rules_and_raise_the_version():
    rulesync, kernel = support.TEMPLATE / support.SKILL_RULESYNC_REL, support.TEMPLATE / support.SKILL_KERNEL_REL
    assert rulesync.read_bytes() == kernel.read_bytes(), (
        f"template/{support.SKILL_RULESYNC_REL} and template/{support.SKILL_KERNEL_REL} are not byte-equal")
    pyproject = (support.REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f"template/{support.SKILL_KERNEL_REL}" in pyproject, "the skill is not in the wheel's shipped list"
    text = kernel.read_text(encoding="utf-8")
    assert_carries_the_rules(text, "the judging-work skill")
    front, _body = support.split_front(text)
    versions = [front.get("version")]
    if isinstance(front.get("metadata"), dict) and "version" in front["metadata"]:
        versions.append(front["metadata"]["version"])
    parsed = [support.version_tuple(item) for item in versions]
    assert all(item is not None and item > support.BASE_SKILL_VERSION for item in parsed), (
        f"the skill's version {versions} is not raised above "
        f"{'.'.join(map(str, support.BASE_SKILL_VERSION))}")


def test_k5_the_skill_and_the_head_share_the_key_phrase_of_each_of_the_four_rules():
    head = (support.TEMPLATE / support.HEAD_REL).read_text(encoding="utf-8")
    skill = (support.TEMPLATE / support.SKILL_KERNEL_REL).read_text(encoding="utf-8")
    phrases = (*support.SKILL_PHRASES, support.VALUE_FIRST[0])
    in_head, in_skill = _missing_phrases(head, phrases), _missing_phrases(skill, phrases)
    assert not in_head and not in_skill, (
        f"key phrases missing from the head: {in_head}; from the skill: {in_skill}")


def _assert_generated_skill(project, what):
    path = project / support.SKILL_GENERATED_REL
    assert path.is_file(), f"{support.SKILL_GENERATED_REL} is absent ({what})"
    source = (support.TEMPLATE / support.SKILL_RULESYNC_REL).read_text(encoding="utf-8")
    generated = path.read_text(encoding="utf-8")
    assert support.split_front(generated)[1] == support.split_front(source)[1], (
        f"{support.SKILL_GENERATED_REL} is not the template's skill ({what})")
    assert_carries_the_rules(generated, f"{support.SKILL_GENERATED_REL} ({what})")


def test_k5_after_adoption_the_generated_skill_is_the_templates(tmp_path, sandbox, adopted_at_b):
    project = support.template_project(tmp_path / "product")
    done = support.generate(project, sandbox)
    assert done.returncode == 0, f"`gov adapters generate` failed\n{done.describe()}"
    _assert_generated_skill(project, "adopted from the kit")
    _assert_generated_skill(adopted_at_b, "adopted by copier at B")


def test_k5_after_the_update_the_generated_skill_is_the_templates(updated_013):
    done = updated_013["run"]
    assert done.returncode == 0, f"`gov update {support.B} --json` did not exit 0\n{done.describe()}"
    _assert_generated_skill(updated_013["project"], "after the update to B")
