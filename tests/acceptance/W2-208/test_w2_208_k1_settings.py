"""K1: after adoption and after ``gov adapters generate`` the settings hold exactly the two deny lines and no allow line
the kit wrote; the kit's own sources say the same; the owner's hand-written lines are kept (EMERGENCY-2 2.4, 2.7;
DEC-1217 (6))."""

from __future__ import annotations

import json

import pytest

import w2_208_support as support


def test_k1_the_permission_source_holds_the_two_deny_lines_under_bash_and_nothing_else():
    path = support.TEMPLATE / support.PERMS_REL
    assert path.is_file(), f"template/{support.PERMS_REL} is absent"
    data = support.jsonc(path.read_text(encoding="utf-8"))
    rules = {key: value for key, value in data.items() if key != "$schema"}
    assert rules == {"permission": {"bash": {"git push *": "deny", "sudo *": "deny"}}}, (
        f"template/{support.PERMS_REL} is not exactly `git push *` and `sudo *` denied under `bash`: "
        f"{json.dumps(data)}")


def test_k1_the_kernel_settings_hold_no_allow_and_no_deny_but_the_two():
    path = support.TEMPLATE / support.KERNEL_SETTINGS_REL
    assert path.is_file(), f"template/{support.KERNEL_SETTINGS_REL} is absent"
    settings = json.loads(path.read_text(encoding="utf-8"))
    deny, allow = support.permission_lines(settings)
    assert allow == [], f"template/{support.KERNEL_SETTINGS_REL} holds allow lines: {allow}"
    assert "allow" not in settings, f"template/{support.KERNEL_SETTINGS_REL} holds a top-level allow key"
    extra = [line for line in deny if line not in support.TWO]
    assert not extra and len(deny) == len(set(deny)), (
        f"template/{support.KERNEL_SETTINGS_REL} denies more than the two lines: {deny}")


@pytest.mark.parametrize("held_out", [False, True], ids=["no-held-out-file", "held-out-file-of-two-paths"])
def test_k1_a_project_adopted_from_the_kit_holds_exactly_the_two_deny_lines(tmp_path, sandbox, held_out):
    project = support.template_project(tmp_path / "product", held_out=held_out)
    done = support.generate(project, sandbox)
    assert done.returncode == 0, f"`gov adapters generate` failed in the adopted project\n{done.describe()}"
    settings = support.read_settings(project)
    deny, allow = support.permission_lines(settings)
    assert not support.read_lines_starting_read(settings), (
        f"a `Read(` line is in {support.SETTINGS_REL}: {support.read_lines_starting_read(settings)}")
    support.assert_exact_lines(deny, support.TWO, f"permissions.deny of {support.SETTINGS_REL}")
    assert allow == [], f"permissions.allow of {support.SETTINGS_REL} holds lines the kit wrote: {allow}"


def test_k1_lines_the_owner_wrote_by_hand_are_kept_beside_the_two_by_a_second_generate(tmp_path, sandbox):
    project = support.template_project(tmp_path / "product", held_out=True)
    first = support.generate(project, sandbox)
    assert first.returncode == 0, f"the first `gov adapters generate` failed\n{first.describe()}"
    support.add_lines(project, deny=(support.OWNER_DENY,), allow=(support.OWNER_ALLOW,))
    second = support.generate(project, sandbox)
    assert second.returncode == 0, f"the second `gov adapters generate` failed\n{second.describe()}"
    deny, allow = support.permission_lines(support.read_settings(project))
    support.assert_exact_lines(deny, (*support.TWO, support.OWNER_DENY), "permissions.deny after the second generate")
    assert allow == [support.OWNER_ALLOW], (
        f"permissions.allow after the second generate is {allow}, not the owner's line alone")


def test_k1_a_project_adopted_by_copier_at_release_b_holds_exactly_the_two_deny_lines(adopted_at_b):
    settings = support.read_settings(adopted_at_b)
    deny, allow = support.permission_lines(settings)
    assert not support.read_lines_starting_read(settings), "a `Read(` line is in the adopted project's settings"
    support.assert_exact_lines(deny, support.TWO, "permissions.deny of the project adopted at B")
    assert allow == [], f"permissions.allow of the project adopted at B holds lines the kit wrote: {allow}"
