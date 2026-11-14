"""W2-101: the generated copies match the template's source: success-6, failure-5 (DEC-616, DEC-645).

The comparison rule, as the adapter check (``gov.adapters.portability``) applies it:

* ``.rulesync/skills/<skill>/`` and ``template/.rulesync/skills/<skill>/`` hold the same files as the kernel source,
  byte-equal (``diff -r`` finds no difference); the adapter check names no ``SOURCE_*`` finding for the skill.
* ``.claude/skills/<skill>/`` (what rulesync generates) holds the same files; ``SKILL.md`` has the same body, the same
  name and description (whitespace collapsed), only keys rulesync writes, the version under ``metadata.version``; every
  other file is byte-equal. The adapter check names a drifted generated file ``GENERATED_DIFFERS``.

KNOWN RED UNTIL THE COPIES ACT (DEC-1112 (3)): the ``.claude/skills/`` cases of the real tree. A launched session cannot
write that folder (DEC-315); the CTO's copies ACT generates it after the owner's yes. They compare the copy when it is
present and fail, naming the folder, when it is not: a merged-but-unplaced copy is not a pass of the ``.claude`` half.
They are neither skipped nor xfail.

DRIFT reads as the adapter check's ``SOURCE_DIFFERS`` and ``GENERATED_DIFFERS``, each naming the file. The planted hand
edits run in a minimal tree in ``tmp_path`` (a few named files, never the repository).
"""
from __future__ import annotations

import functools
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import w2_101_support as s

SKILLS = pytest.mark.parametrize("skill", s.SKILLS)
CLAUDE_KEYS = {"name", "description", "when_to_use", "allowed-tools", "disallowed-tools", "model", "effort",
               "argument-hint", "context", "agent", "shell", "background", "arguments", "hooks",
               "disable-model-invocation", "user-invocable", "paths", "license", "compatibility", "metadata"}


def _collapse(text):
    return " ".join(str(text).split())


def differences(source, copy, generated):
    """What differs between a copy folder and the source folder, as a list of messages (empty: no difference)."""
    source, copy = Path(source), Path(copy)
    if not copy.is_dir():
        return [f"{copy} does not exist"]
    found = []
    src, cpy = s.skill_files(source), s.skill_files(copy)
    found += [f"{copy}/{f} is missing" for f in src if f not in cpy]
    found += [f"{copy}/{f} has no source" for f in cpy if f not in src]
    for rel in (f for f in src if f in cpy):
        a, b = source / rel, copy / rel
        if rel.name != "SKILL.md" or len(rel.parts) != 1:
            if a.read_bytes() != b.read_bytes():
                found.append(f"{copy}/{rel} differs from {a}")
            continue
        (fa, ba), (fb, bb) = (s.split_frontmatter(p.read_text(encoding="utf-8")) for p in (a, b))
        if ba != bb:
            found.append(f"{copy}/SKILL.md: the body differs from {a}")
        if fa is None or fb is None:
            found.append(f"{copy}/SKILL.md or its source has no front matter")
        elif not generated:
            if fa != fb:
                found.append(f"{copy}/SKILL.md: the front matter differs from {a}")
        else:
            extra = set(fb) - CLAUDE_KEYS
            version = str(fa.get("version") or (fa.get("metadata") or {}).get("version"))
            if extra:
                found.append(f"{copy}/SKILL.md: keys rulesync does not write: {sorted(extra)}")
            if fb.get("name") != fa.get("name") or _collapse(fb.get("description")) != _collapse(fa.get("description")):
                found.append(f"{copy}/SKILL.md: name or description differs from {a}")
            if str((fb.get("metadata") or {}).get("version")) != version:
                found.append(f"{copy}/SKILL.md: metadata.version is not {version}")
    return found


def _source(skill):
    return s.need(s.skill_dir(skill) / "SKILL.md").parent


# success-6 and failure-5 on the real tree (repository-state) ---------------------------------------------------------------

@SKILLS
@pytest.mark.parametrize("root", [".rulesync/skills", "template/.rulesync/skills"])
def test_the_rulesync_copy_matches_the_kernel_source(skill, root):
    found = differences(_source(skill), s.REPO_ROOT / root / skill, generated=False)
    assert not found, f"{root}/{skill} differs from the kernel source: {found}"


@SKILLS
@pytest.mark.parametrize("root", [".rulesync/skills", "template/.rulesync/skills"])
def test_diff_r_of_the_rulesync_copy_against_the_source_is_empty(skill, root):
    source = _source(skill)
    copy = s.REPO_ROOT / root / skill
    assert copy.is_dir(), f"{copy} does not exist"
    done = subprocess.run(["diff", "-r", str(source), str(copy)], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=60)
    assert done.returncode == 0, f"diff -r finds a difference in {root}/{skill}: {done.stdout[-600:]}{done.stderr[-300:]}"


@SKILLS
def test_the_claude_copy_matches_the_kernel_source(skill):
    """KNOWN RED until the CTO's copies ACT (DEC-1112 (3)): .claude/skills/ is generated by it, not by this ticket."""
    found = differences(_source(skill), s.REPO_ROOT / ".claude/skills" / skill, generated=True)
    assert not found, f".claude/skills/{skill} differs from the kernel source: {found}"


def _adapter(cwd):
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(s.SRC), os.environ.get("PYTHONPATH", "")])}
    done = subprocess.run([sys.executable, "-m", "gov.adapters.portability"], capture_output=True, text=True,
                          cwd=str(cwd), env=env, timeout=120, stdin=subprocess.DEVNULL)
    return done.returncode, json.loads(done.stdout)["findings"]


def _naming(findings, skill):
    return [f for f in findings if skill in f.get("file", "") or skill in f.get("message", "")]


@functools.lru_cache(maxsize=1)
def _real_findings():
    """The adapter check's findings on the real tree (one run for the module)."""
    return _adapter(s.REPO_ROOT)[1]


@SKILLS
def test_the_adapter_check_finds_no_source_drift_in_the_real_skill(skill):
    _source(skill)
    drift = [f for f in _naming(_real_findings(), skill) if f["code"].startswith("SOURCE_")]
    assert not drift, f"the adapter check names {skill}'s rulesync sources: {drift}"


@SKILLS
def test_the_adapter_check_finds_no_generated_drift_in_the_real_skill(skill):
    """KNOWN RED until the CTO's copies ACT (DEC-1112 (3)): the .claude/skills/ copy is generated by it."""
    if shutil.which("rulesync") is None and not os.environ.get("RULESYNC_BIN"):
        pytest.skip("rulesync is not installed: the adapter check cannot compare the generated copy")
    _source(skill)
    drift = [f for f in _naming(_real_findings(), skill) if f["code"].startswith("GENERATED_")]
    assert not drift, f"the adapter check names {skill}'s generated copy: {drift}"
    assert (s.REPO_ROOT / ".claude/skills" / skill / "SKILL.md").is_file(), \
        f".claude/skills/{skill} is not placed (the copies ACT has not run): the .claude half is not passed"


# the planted hand edits: a minimal tree in tmp_path -----------------------------------------------------------------------------

def _plant_tree(tmp_path, skill):
    """A minimal repository: the skill's files under the kernel's skills folder and byte copies in .rulesync."""
    source = _source(skill)
    kernel = tmp_path / s.KERNEL_SKILLS / skill
    mirror = tmp_path / ".rulesync/skills" / skill
    for folder in (kernel, mirror):
        folder.mkdir(parents=True)
        for rel in s.skill_files(source):
            (folder / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / rel, folder / rel)
    return kernel, mirror


@SKILLS
@pytest.mark.parametrize("name", ["SKILL.md", s.CHECK_NAME, s.SCENARIOS_FILE])
def test_a_hand_edit_in_the_rulesync_copy_is_named_by_the_adapter_check(skill, name, tmp_path):
    kernel, mirror = _plant_tree(tmp_path, skill)
    _, before = _adapter(tmp_path)
    assert not [f for f in before if f["code"] == "SOURCE_DIFFERS"], f"the untouched copy already differs: {before}"
    target = mirror / name
    target.write_text(target.read_text(encoding="utf-8") + "\nA line added by hand.\n", encoding="utf-8")
    code, findings = _adapter(tmp_path)
    expected = f".rulesync/skills/{skill}/{name}"
    named = [f for f in findings if f["code"] == "SOURCE_DIFFERS" and f.get("file") == expected]
    assert code == 1 and named, f"the adapter check does not name {expected} with SOURCE_DIFFERS: {findings}"


@SKILLS
def test_a_planted_hand_edit_makes_diff_r_find_a_difference(skill, tmp_path):
    """The test's own comparison, shown on planted copies: untouched is empty, an edit and an extra file are found."""
    kernel, mirror = _plant_tree(tmp_path, skill)
    assert differences(kernel, mirror, generated=False) == []
    done = subprocess.run(["diff", "-r", str(kernel), str(mirror)], capture_output=True, text=True, timeout=60)
    assert done.returncode == 0
    (mirror / "SKILL.md").write_text((mirror / "SKILL.md").read_text(encoding="utf-8") + "\nedit\n", encoding="utf-8")
    assert any("SKILL.md" in d for d in differences(kernel, mirror, generated=False))
    done = subprocess.run(["diff", "-r", str(kernel), str(mirror)], capture_output=True, text=True, timeout=60)
    assert done.returncode == 1, "diff -r does not find the planted edit"
    shutil.copyfile(kernel / "SKILL.md", mirror / "SKILL.md")
    (mirror / "extra.md").write_text("x", encoding="utf-8")
    assert any("extra.md" in d for d in differences(kernel, mirror, generated=False))
