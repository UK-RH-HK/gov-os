"""success-1, I4: a vendored skill (openspec-*, superpowers/*) is named, ``code`` ``SKILL_VENDORED_KEY`` with file and key,
and the exit is unchanged (a named-only finding never changes it), until DEC-996 item 5 strips them.

The kernel skills root is given here (``--both-layouts template/governance/kernel/skills``): the openspec-* skills lie
only in the generated folders, so I4 is judged where the root is given (README, reading 2). The other skills of the
planted project are clean.
"""

from __future__ import annotations

import pytest

import w2_120_support as sup


def _named(run, tmp_path, planted, key):
    found = sup.about(run, tmp_path, planted, key)
    assert found, f"no finding names {planted.relative_to(tmp_path)} and key {key!r}: {run.out}"
    assert any(f.get("code") == sup.VENDORED_CODE for f in found), f"not named SKILL_VENDORED_KEY: {found}"
    for field in ("code", "file", "key", "message"):
        assert all(field in f for f in found), found


def _vendored_front(name, **extra):
    front = {"name": name, "description": sup.DESCRIPTION, "metadata": {"version": "1.0.0"}}
    return {**front, **extra}


def test_i4_a_vendored_kernel_superpowers_skill_with_allowed_tools_is_named_and_the_exit_stays_0(tmp_path):
    """I4 (a): ``superpowers/<y>`` in the kernel skills carries ``allowed-tools``: named ``SKILL_VENDORED_KEY``, exit 0."""
    sup.plant_clean(tmp_path, "alpha")
    planted = sup.write_skill(tmp_path, sup.KERNEL, "superpowers/gamma",
                              {**sup.kernel_front("gamma"), "allowed-tools": "Bash(git:*)"})
    run = sup.run_on_root(tmp_path)
    assert run.code == 0, run.text()
    _named(run, tmp_path, planted, "allowed-tools")
    assert not sup.refusing(run.findings), run.out


def test_i4_a_vendored_claude_openspec_skill_with_allowed_tools_and_license_is_named_and_the_exit_stays_0(tmp_path):
    """I4 (b): ``.claude/skills/openspec-<z>`` carries ``allowed-tools`` and ``license`` (as the live copies do): each
    named ``SKILL_VENDORED_KEY`` with the file, exit 0."""
    sup.plant_clean(tmp_path, "alpha")
    planted = sup.write_skill(tmp_path, sup.CLAUDE, "openspec-zeta",
                              _vendored_front("openspec-zeta", **{"allowed-tools": "Bash(openspec:*)", "license": "MIT"}))
    run = sup.run_on_root(tmp_path)
    assert run.code == 0, run.text()
    _named(run, tmp_path, planted, "allowed-tools")
    _named(run, tmp_path, planted, "license")
    assert not sup.refusing(run.findings), run.out


@pytest.mark.parametrize("folder", [sup.RULESYNC, sup.TEMPLATE_RULESYNC])
def test_i4_a_vendored_rulesync_openspec_skill_with_targets_is_named_and_the_exit_stays_0(tmp_path, folder):
    """I4 (c): ``.rulesync/skills/openspec-<z>`` (and the template's) carries ``targets``, as the live copies do:
    named ``SKILL_VENDORED_KEY`` with the file and the key, exit 0."""
    sup.plant_clean(tmp_path, "alpha")
    # a rulesync copy's own list holds version, so the planted copy is clean but for `targets` (no pinning of how a
    # vendored skill's missing fields are handled)
    planted = sup.write_skill(tmp_path, folder, "openspec-zeta",
                              _vendored_front("openspec-zeta", version="1.0.0", targets=["*"]))
    run = sup.run_on_root(tmp_path)
    assert run.code == 0, run.text()
    _named(run, tmp_path, planted, "targets")
    assert not sup.refusing(run.findings), run.out


def test_i4_a_vendored_named_finding_beside_a_refused_non_vendored_key_gives_exit_1_and_both_findings(tmp_path):
    """I1 and I4: a vendored ``allowed-tools`` is named and a non-vendored kernel skill's ``network`` is refused: exit 1
    from the refusal alone, and both findings are there."""
    sup.plant_clean(tmp_path, "alpha")
    vendored = sup.write_skill(tmp_path, sup.CLAUDE, "openspec-zeta",
                               _vendored_front("openspec-zeta", **{"allowed-tools": "Bash(openspec:*)"}))
    plain = sup.plant_with(tmp_path, sup.KERNEL, "alpha", {"network": "none"})
    run = sup.run_on_root(tmp_path)
    assert run.code == 1, run.text()
    _named(run, tmp_path, vendored, "allowed-tools")
    sup.assert_refused(run, tmp_path, plain, "network")


def test_i4_a_non_vendored_skill_with_allowed_tools_is_refused_not_merely_named(tmp_path):
    """I4: only openspec-* and superpowers/* are vendored: a kernel skill of another name with ``allowed-tools`` is
    refused (exit 1, a finding that is not ``SKILL_VENDORED_KEY``), with the root given."""
    sup.plant_clean(tmp_path, "alpha")
    plain = sup.plant_with(tmp_path, sup.KERNEL, "alpha", {"allowed-tools": "Bash(git:*)"})
    run = sup.run_on_root(tmp_path)
    sup.assert_refused(run, tmp_path, plain, "allowed-tools")
