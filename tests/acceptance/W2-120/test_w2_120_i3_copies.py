"""success-1, I3: from the kernel skill folder it is given (``--both-layouts``), the validator itself reads the kernel
source and every generated copy (``.rulesync/skills/``, ``template/.rulesync/skills/``, ``.claude/skills/``), so
``gov check`` reads them with no edit to the three skill-regression check files.

The command a check file runs is read from the file and run from a planted project's root (README, "How a refusal is
judged"). Paths are compared as paths, never searched as text (DEC-1155).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest
import yaml

import w2_120_support as sup


def test_i3_the_three_check_files_still_run_the_validator_over_kernel_skill_folders():
    """I3: nothing is edited in the three skill-regression check files, so each still runs the validator in its
    ``--both-layouts`` form over folders of the kernel skills (the validator finds the copies itself)."""
    folder = re.compile(r"template/governance/kernel/skills/[a-z][a-z0-9-]*")
    for check_id in sup.CHECK_IDS:
        words = sup.check_command(check_id)
        assert words[:4] == sup.CHECK_HEAD, (check_id, words)
        assert len(words) > 4 and all(folder.fullmatch(word) for word in words[4:]), (check_id, words)


@pytest.mark.parametrize("folder", sup.GENERATED)
def test_i3_a_refused_key_in_a_generated_copy_is_read_and_names_the_generated_file(tmp_path, folder):
    """I3 (a), (b), (c): the kernel copy is clean; the same skill under ``.rulesync/skills/``,
    ``template/.rulesync/skills/`` or ``.claude/skills/`` carries ``allowed-tools``: refused, the finding naming the
    generated file and not the kernel one."""
    copies = sup.plant_clean(tmp_path, "alpha")
    planted = sup.plant_with(tmp_path, folder, "alpha", {"allowed-tools": "Bash(git:*)"})
    run = sup.run_on(tmp_path, "alpha")
    sup.assert_refused(run, tmp_path, planted, "allowed-tools")
    assert sup.files_named(run, tmp_path) == {planted.resolve()}, f"only the generated file is named: {run.out}"
    assert not sup.about(run, tmp_path, copies[sup.KERNEL]), "the clean kernel copy is not named"


@pytest.mark.parametrize("folder", sup.GENERATED)
def test_i3_kernel_and_a_generated_copy_both_carrying_the_key_are_both_named(tmp_path, folder):
    """I3 and I2: the kernel copy and one generated copy carry ``model``: a finding for each file."""
    sup.plant_clean(tmp_path, "alpha")
    kernel = sup.plant_with(tmp_path, sup.KERNEL, "alpha", {"model": "opus"})
    generated = sup.plant_with(tmp_path, folder, "alpha", {"model": "opus"})
    run = sup.run_on(tmp_path, "alpha")
    sup.assert_refused(run, tmp_path, kernel, "model")
    sup.assert_refused(run, tmp_path, generated, "model")


def test_i3_every_copy_carrying_a_key_is_named_once_each(tmp_path):
    """I3: the kernel copy and all three generated copies carry ``effort``: four files named, each with the key."""
    sup.plant_clean(tmp_path, "alpha")
    planted = [sup.plant_with(tmp_path, folder, "alpha", {"effort": "high"})
               for folder in (sup.KERNEL, *sup.GENERATED)]
    run = sup.run_on(tmp_path, "alpha")
    assert run.code == 1, run.text()
    for path in planted:
        sup.assert_refused(run, tmp_path, path, "effort")


def test_i3_the_installed_twin_of_the_kernel_folder_is_read_too(tmp_path):
    """I2 on every copy read, with ``--both-layouts`` mapping ``template/<path>`` to its installed twin: a skill
    under ``governance/kernel/skills/`` that carries ``network`` is refused naming that file."""
    sup.plant_clean(tmp_path, "alpha")
    twin = sup.write_skill(tmp_path, "governance/kernel/skills", "alpha", {**sup.kernel_front("alpha"), "network": "none"})
    run = sup.run_on(tmp_path, "alpha")
    sup.assert_refused(run, tmp_path, twin, "network")


def test_i3_gov_check_runs_the_check_file_and_refuses_the_planted_key(tmp_path):
    """I1 and I3 through ``gov check`` itself: a planted project holding ``skill-regression-a.yaml`` as the kernel
    ships it, its folder list swapped for the planted skill's, and a generated copy with ``allowed-tools``: the
    check's entry is red and its findings name the generated file and the key. Judged on the real validator only
    (``gov check`` runs ``python3 -m gov.check.skill_validator`` as the file says, so a stand-in is not reachable).

    ``gov check --json`` ends with 3 when a hard-block check is red; its envelope is then ``ok: false`` with
    ``result: {}`` and the per-check entries under ``error.details.checks`` (on success under ``result.checks``).
    So the entry is looked for anywhere in the payload, and its status is spelled ``RED`` (``GREEN``, ``YELLOW``)."""
    if not sup.REAL:
        pytest.skip("gov check runs the real validator named in the check file; a stand-in switch is set")
    copies = sup.plant_clean(tmp_path, "alpha")
    planted = sup.plant_with(tmp_path, sup.CLAUDE, "alpha", {"allowed-tools": "Bash(git:*)"})
    declared = yaml.safe_load((sup.CHECKS / "skill-regression-a.yaml").read_text(encoding="utf-8"))
    declared["command"] = f"python3 -m gov.check.skill_validator --both-layouts {sup.KERNEL}/alpha"
    checks = tmp_path / "template" / "governance" / "kernel" / "checks"
    checks.mkdir(parents=True)
    (checks / "skill-regression-a.yaml").write_text(yaml.safe_dump(declared, sort_keys=False), encoding="utf-8")
    env = sup.env_for()
    done = subprocess.run([sys.executable, "-P", "-m", "gov.cli.main", "check", "--json"], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=300, check=False)
    assert done.returncode == 3, f"gov check ends with 3 on a red hard-block check: {done.returncode} {done.stderr[:300]}"
    payload = json.loads(done.stdout)
    entries = [entry for entry in _walk(payload) if entry.get("id") == "skill-regression-a"]
    assert entries, f"gov check printed no entry for skill-regression-a: {done.stdout[:600]} {done.stderr[:300]}"
    entry = entries[0]
    assert str(entry.get("status")).upper() == "RED", entry
    findings = [f for f in entry.get("findings", []) if isinstance(f, dict)]
    assert any(sup.same_file(tmp_path, f.get("file"), planted) and f.get("key") == "allowed-tools"
               for f in findings), f"no finding names the file and key: {findings}"
    assert not any(sup.same_file(tmp_path, f.get("file"), copies[sup.KERNEL]) for f in findings), findings
    assert os.path.exists(planted)


def _walk(node):
    """Every mapping in a parsed JSON document, depth first."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)
