"""S7 (the plain, read-only tree), S8 (the wall's settings are the template's), S11 (the built wall's own hook holds).

S8 re-expresses the rehearsal's built-wall checks (``walls_check.py wall``, its F class) on a wall the script builds;
S11's deterministic case drives the hook command the built settings name, as Claude Code runs a command hook, with a
Read of each of the ten outside targets of the rehearsal's live step.
"""

from __future__ import annotations

import json
import os
import subprocess

import w2_149_support as support
from w2_149_support import assert_good_launch, assert_nothing_built, assert_refused

OLD = "20260101T000000Z-memory-verdict-3-r1"


def plant_older_walls(world):
    """A writer wall and a checker wall present at build time (with a marker each), and the checker's tree."""
    for kind in ("writer", "checker"):
        support.write_file(world.walls, f"{kind}/{OLD}/brief.md", f"DUMMY MARK-OUTSIDE-01 an older {kind} wall\n")
    support.write_file(world.trees, f"checker-{OLD}/README.md", "DUMMY MARK-OUTSIDE-02 another wall's tree\n")


# -- S7 -------------------------------------------------------------------------------------------------------------

def test_s7_the_tree_is_the_archive_at_the_commit_less_the_exclusions_plain_and_read_only(world):
    run = world.launch(*world.args("writer", dry=True))
    assert run.code == 0, run.why()
    tree = world.tree(run.line)
    assert tree.is_dir()
    assert world.tree_problems(tree) == []
    assert not str(tree).startswith(str(world.sr) + "/"), "the tree lies under the sets root"
    assert not str(tree).startswith(str(world.wall(run.line)) + "/")
    exe = tree / "tools/run.sh"
    assert exe.is_file() and oct(os.stat(exe).st_mode & 0o777) == oct(0o444), "an executable file is not 0444"


def test_s7_a_commit_holding_a_symlink_refuses_14_before_anything_is_built(world):
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", commit="L"))
    assert_refused(world, run, 14)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


def test_s7_a_trees_folder_under_the_sets_root_refuses_17(world):
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", dry=True), env={"GOV_INDEP_TREES_DIR": str(world.sr / "trees")})
    assert_refused(world, run, 17)
    assert_nothing_built(world, "writer", before)
    assert not (world.sr / "trees").exists()
    assert_good_launch(world, "writer")


# -- S8 -------------------------------------------------------------------------------------------------------------

def test_s8_the_built_wall_passes_the_rehearsal_s_f_checks(world):
    plant_older_walls(world)
    run = world.launch(*world.args("writer", dry=True))
    assert run.code == 0, run.why()
    assert world.f_checks(world.wall(run.line), "writer") == []


def test_s8_the_settings_are_the_template_filled_for_this_wall(world):
    plant_older_walls(world)
    run = world.launch(*world.args("writer", dry=True))
    assert run.code == 0, run.why()
    wall, tree = world.wall(run.line), world.tree(run.line)
    built = json.loads((wall / ".claude/settings.json").read_text())
    want = world.expected_settings(wall, tree)
    deny = built["permissions"]["deny"]
    extras = [x for x in deny if x not in want["permissions"]["deny"]]
    assert [x for x in deny if x not in extras] == want["permissions"]["deny"], "the template's deny entries differ"
    walls = str(world.walls)
    need = [f"Read(/{walls}/{k}/**)" for k in support.KINDS if k != "writer"] + [f"Read(/{walls}/writer/{OLD}/**)"]
    assert set(need) <= set(extras), f"the other walls' entries missing: {sorted(set(need) - set(extras))}"
    assert all(x.startswith(f"Read(/{walls}/") for x in extras), f"entries beyond the template's: {extras}"
    built["permissions"]["deny"] = want["permissions"]["deny"]
    assert built == want, "the settings differ from the template filled for this wall"


def test_s8_the_manifest_and_the_standing_note_name_this_wall(world):
    run = world.launch(*world.args("writer", dry=True))
    assert run.code == 0, run.why()
    line = run.line
    wall, tree = world.wall(line), world.tree(line)
    assert (wall / "CLAUDE.md").read_text() == world.expected_claude_md(line)
    m = json.loads((wall / "WALL.json").read_text())
    assert support.WALL_KEYS <= set(m), f"WALL.json lacks {sorted(support.WALL_KEYS - set(m))}"
    assert (m["kind"], m["run"], m["set"], m["round"]) == ("writer", line["run"], "memory-verdict-4", 1)
    assert m["commit"] == world.sha("B") and m["repo"] == os.path.realpath(world.repo_path)
    assert m["tree"] == str(tree) and m["runs"] == str(world.runs_root) and m["home"] == str(world.home)
    assert m["sets_root"] == str(world.sr)
    assert m["template_sha256"] == {n: support.sha256(world.blob("B", f"{support.TEMPLATE_REL}/{n}"))
                                    for n in support.TEMPLATE_FILES}
    assert m["approved_sha256"] == world.approved_sha() == line["approved_sha256"]
    assert m["hook_sha256"] == support.sha_file(wall / ".claude/wall_hook.py")
    assert m["brief_sha256"] == world.brief_sha("writer") == line["brief_sha256"]
    assert m["runs_override"] is False and m["trees_override"] is False and line["override"] is False
    assert line["template_ok"] is True


# -- S11 (deterministic) --------------------------------------------------------------------------------------------

def test_s11_the_built_wall_s_hook_refuses_each_outside_target_and_allows_its_brief_and_tree(world):
    plant_older_walls(world)
    run = world.launch(*world.args("writer", dry=True))
    assert run.code == 0, run.why()
    wall, tree = world.wall(run.line), world.tree(run.line)
    settings = json.loads((wall / ".claude/settings.json").read_text())
    (entry,) = settings["hooks"]["PreToolUse"]
    command = entry["hooks"][0]["command"]
    sr = world.sr
    outside = [world.walls / f"checker/{OLD}/brief.md", world.trees / f"checker-{OLD}/README.md",
               world.walls / "APPROVED", sr / "fixtures/evaluation/memory-verdict-2/hidden/p01.yaml",
               sr / support.SEALED / "corpus/zz-marker.jsonl", sr / "runs/e0/counts.txt", sr / "transcripts/t01.md",
               world.ledger, world.repo_path / ".gov-runtime/notes.md", world.repo_path / "CLAUDE.md"]
    assert all(p.exists() for p in outside), "premise: every target exists"

    def decide(path):
        event = {"session_id": "w2-149", "transcript_path": "", "cwd": str(wall), "hook_event_name": "PreToolUse",
                 "tool_name": "Read", "tool_input": {"file_path": str(path)}}
        p = subprocess.run(["/bin/sh", "-c", command], input=json.dumps(event), capture_output=True, text=True,
                           cwd=str(wall), env={"PATH": "/usr/bin:/bin", "HOME": str(world.home)}, timeout=30)
        if p.returncode == 2:
            return "deny"
        if p.returncode == 0 and p.stdout.strip():
            return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"]
        return "allow" if p.returncode == 0 else f"error {p.returncode}"

    got = {str(p): decide(p) for p in outside}
    assert all(v == "deny" for v in got.values()), got
    assert decide(wall / "brief.md") == "allow"
    assert decide(tree / "README.md") == "allow"
