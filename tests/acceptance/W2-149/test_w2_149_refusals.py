"""S1, S2, S3, S6 (the seed refused), code 14 (failure line 2), and reading 3: the refusals before anything is built.

Each code refuses on its own: in the same planted set-up every other check passes (the default launch builds, as
``assert_good_launch`` shows after each refusal). Nothing is built: the kind's wall listing, the trees folder and the
seed ledger are unchanged and no ``claude`` is started. Then a second, good launch for the same kind and set builds
(failure line 2: no half-built wall left to build into).
"""

from __future__ import annotations

import pytest

import w2_149_support as support
from w2_149_support import assert_good_launch, assert_nothing_built, assert_refused


# -- S1: the brief is the approved one (code 10) ------------------------------------------------------------------

def test_s1_a_brief_byte_altered_at_the_commit_refuses_10(world):
    """TB holds writer.md with one byte changed; --brief-sha256 and APPROVED hold B's bytes' hash."""
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", commit="TB"))
    assert_refused(world, run, 10)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


def test_s1_a_wrong_hash_argument_refuses_10(world):
    good = world.brief_sha("writer")
    wrong = good[:-1] + ("0" if good[-1] != "0" else "1")
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", sha=wrong))
    assert_refused(world, run, 10)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


def test_s1_the_approved_line_removed_refuses_10(world):
    world.approve(drop_kind="writer")
    before = world.built_state("writer")
    run = world.launch(*world.args("writer"))
    assert_refused(world, run, 10)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


def test_s1_a_brief_whose_front_matter_names_another_kind_refuses_10(world):
    """APPROVED lists checker.md as a writer's brief (its bytes and hash agree), but its front matter says checker."""
    extra = [f"{world.brief_sha('checker')}  brief writer {support.BRIEFS_REL}/checker.md"]
    world.approve(extra=extra)
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", brief="checker"))
    assert_refused(world, run, 10)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


# -- S2: the template is the approved one (code 11) ---------------------------------------------------------------

@pytest.mark.parametrize("name", support.TEMPLATE_FILES)
def test_s2_one_changed_byte_in_a_template_file_refuses_11(world, name):
    """T-<file> holds B's tree with one byte of that file changed; APPROVED holds B's hashes."""
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", commit=f"T-{name}"))
    assert_refused(world, run, 11)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


def test_s2_the_bytes_come_from_the_commit_not_the_working_tree(world, tmp_path):
    """Reading 3: a clone whose working tree holds an uncommitted change to a template file and to the brief still
    builds at B (the bytes are read with git at --commit); its tree carries the commit's bytes."""
    repo = support.clone_repo(world.repo, tmp_path / "clone")
    world.attach(repo)
    for rel in (f"{support.TEMPLATE_REL}/settings.json.tmpl", f"{support.BRIEFS_REL}/writer.md"):
        p = world.repo_path / rel
        p.write_bytes(support.flip_last_letter(p.read_bytes()))
    run = world.launch(*world.args("writer", dry=True))
    assert run.code == 0, run.why()
    line = run.line
    assert (world.wall(line) / "brief.md").read_bytes() == world.blob("B", f"{support.BRIEFS_REL}/writer.md")
    assert world.tree_problems(world.tree(line)) == []


# -- S3: a wall is built only into nothing (code 12) --------------------------------------------------------------

def test_s3_a_wall_holding_an_entry_refuses_12_and_leaves_it_untouched(world):
    """The test hook, at ``before_wall`` (the run's id chosen, nothing written), plants one file in the wall."""
    hook = world.write_hook({"before_wall": [{"op": "write", "where": "wall", "rel": "planted.txt",
                                              "text": "planted before the build\n"}]})
    ledger = world.built_state("writer")[2]
    run = world.launch(*world.args("writer", dry=True), env=hook)
    assert "before_wall" in world.hook_points(), "the test hook's point before_wall was not run"
    assert_refused(world, run, 12)
    wall, tree = world.wall(run.line), world.tree(run.line)
    assert sorted(p.name for p in wall.iterdir()) == ["planted.txt"]
    assert support.sha_file(wall / "planted.txt") == support.sha256(b"planted before the build\n")
    assert not tree.exists(), "a tree was built"
    assert world.built_state("writer")[2] == ledger, "a SEEDS.log line was written"
    assert world.calls() == []
    assert_good_launch(world, "writer")


def test_s3_an_existing_tree_folder_refuses_12_and_leaves_it_untouched(world):
    hook = world.write_hook({"before_wall": [{"op": "write", "where": "tree", "rel": "planted.txt",
                                              "text": "a planted tree\n"}]})
    ledger = world.built_state("writer")[2]
    run = world.launch(*world.args("writer", dry=True), env=hook)
    assert "before_wall" in world.hook_points(), "the test hook's point before_wall was not run"
    assert_refused(world, run, 12)
    wall, tree = world.wall(run.line), world.tree(run.line)
    assert sorted(p.name for p in tree.iterdir()) == ["planted.txt"]
    assert support.sha_file(tree / "planted.txt") == support.sha256(b"a planted tree\n")
    assert not wall.exists() or not any(wall.iterdir()), "a wall was built"
    assert world.built_state("writer")[2] == ledger, "a SEEDS.log line was written"
    assert world.calls() == []
    assert_good_launch(world, "writer")


# -- S6: the caller cannot choose the seed (code 17) --------------------------------------------------------------

def test_s6_a_given_seed_without_dry_refuses_17(world):
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", seed=5))
    assert_refused(world, run, 17)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


# -- failure line 2, code 14: the commit -------------------------------------------------------------------------

def test_f2_a_commit_that_does_not_resolve_refuses_14(world):
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", commit="0123456789abcdef0123456789abcdef01234567"))
    assert_refused(world, run, 14)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")


def test_f2_a_commit_not_reachable_from_the_main_line_refuses_14(world):
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", commit="S"))
    assert_refused(world, run, 14)
    assert_nothing_built(world, "writer", before)
    assert_good_launch(world, "writer")
