"""Premises (green on integrate): the planted repository, the stub's model of Claude Code, and failure line 10.

These hold the cases' own ground: if one goes red, the red cases elsewhere may be red for the wrong reason.
"""

from __future__ import annotations

import json
import os
import subprocess

import pytest

import w2_149_support as support


def test_s7_premise_the_planted_commits_are_one_change_each(world):
    tracked_b = set(world.tracked("B"))
    assert "docs/link.md" not in tracked_b
    mode = support.git(world.repo_path, "ls-tree", world.sha("L"), "docs/link.md").split()[0]
    assert mode == "120000", "L holds a symlink"
    for key in ["TB", "TK", "TS"] + [f"T-{n}" for n in support.TEMPLATE_FILES]:
        diff = support.git(world.repo_path, "diff", "--name-only", world.sha("B"), world.sha(key)).split()
        assert len(diff) == 1, (key, diff)
    for key in ["TB"] + [f"T-{n}" for n in support.TEMPLATE_FILES]:
        rel = support.git(world.repo_path, "diff", "--name-only", world.sha("B"), world.sha(key)).strip()
        a, b = world.blob("B", rel), world.blob(key, rel)
        assert len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1, key
    assert support.git(world.repo_path, "diff", "--name-only", world.sha("B"), world.sha("Z")).strip() == ""
    reach = subprocess.run(["git", "-C", str(world.repo_path), "merge-base", "--is-ancestor", world.sha("S"),
                            "w2/integrate"], env=support.GIT_ENV)
    assert reach.returncode == 1, "S is not reachable from w2/integrate"


def test_s5_premise_the_rule_s_inputs_are_planted(world):
    changed, sample = world.expected_selection(1, 5)
    assert changed == ["docs/d03.md", "docs/new.md", "src/pkg/m02.py"], changed
    assert len(sample) == 5
    ex = world.exclusions()
    diff = support.git(world.repo_path, "diff", "--name-only", world.sha("A"), world.sha("B")).split()
    assert any(support.excluded(p, ex) for p in diff), "an excluded path changed too"
    # the planted excluded paths are excluded under the path map's segment-wise globs as under fnmatch
    for p in world.tracked():
        seg = any(_segment_match(p, g) for g in ex)
        assert seg == support.excluded(p, ex), p


def _segment_match(path, glob):
    import re
    rx = ""
    i = 0
    while i < len(glob):
        if glob.startswith("**", i):
            rx += ".*"
            i += 2
        elif glob[i] == "*":
            rx += "[^/]*"
            i += 1
        else:
            rx += re.escape(glob[i])
            i += 1
    return re.fullmatch(rx, path) is not None


def test_s9_premise_the_stub_models_claude_code(world, tmp_path):
    """The stub's canary: restricted mode refuses a target outside every working folder even with no settings; with
    the target in an --add-dir folder, valid settings whose hook refuses it refuse it, invalid ones are ignored."""
    wall, tree, canary = tmp_path / "wall", tmp_path / "tree", tmp_path / "canary"
    for d in (wall / "out", tree, canary):
        d.mkdir(parents=True)
    target = canary / "target.txt"
    target.write_text("x\n")
    hook = support.TREE / support.TEMPLATE_REL / "wall_hook.py"
    good = {"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [
        {"type": "command", "command": f"python3 -I {hook} {wall} {tree}", "timeout": 20}]}]}}
    bad = {"hooks": {"PreToolUse": "not a list"}}
    (wall / "good.json").write_text(json.dumps(good))
    (wall / "bad.json").write_text(json.dumps(bad))
    world.write_stub()

    def canary_denied(settings, adds):
        argv = [str(world.bin / "claude"), "-p", "--restricted"] + (["--settings", settings] if settings else [])
        for d in adds:
            argv += ["--add-dir", str(d)]
        argv += ["--output-format", "json", f"Use the Read tool once on {target} and stop."]
        p = subprocess.run(argv, cwd=str(wall), capture_output=True, text=True, timeout=60,
                           env={"PATH": "/usr/bin:/bin", "HOME": str(world.home), "LANG": "C.UTF-8"})
        assert p.returncode == 0, p.stderr
        return bool(json.loads(p.stdout)["permission_denials"])

    assert canary_denied(None, [tree]) is True, "restricted mode alone refuses a target outside the folders"
    assert canary_denied(None, [tree, canary]) is False
    assert canary_denied("good.json", [tree, canary]) is True, "the wall's hook refuses it"
    assert canary_denied("bad.json", [tree, canary]) is False, "invalid settings are ignored"


def test_f10_every_launch_runs_on_planted_roots(world, monkeypatch):
    world.check_planted()
    monkeypatch.setattr(world, "home", support.Path(os.path.realpath(support.real_home())))
    with pytest.raises(AssertionError):
        world.check_planted()
    monkeypatch.undo()
    monkeypatch.setattr(world, "sr", support.Path(support.real_home()) / "gov-os-eval")
    with pytest.raises(AssertionError):
        world.check_planted()
