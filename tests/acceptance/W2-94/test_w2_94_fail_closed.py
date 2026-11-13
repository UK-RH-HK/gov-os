"""W2-94, fail closed -- what the program cannot read or parse is refused with a reason code and a non-zero exit, never
passed.

An unreadable or missing sets root, ``hidden/`` folder, copy or ``COPY-HEAD.txt``; a ``COPY-HEAD.txt`` that is not 40
hexadecimal digits; a commit the copy does not hold; an unparsable question file; a bad command line. A refusal prints
no ``n of N hold`` line (the set was not judged) and exits 2.
"""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_94_cases as c  # noqa: E402
import w2_94_support as s  # noqa: E402


@pytest.mark.parametrize("name", sorted(c.FAIL_CLOSED))
def test_what_cannot_be_read_or_parsed_is_refused(tmp_path, name):
    build_kwargs, case, rc = c.FAIL_CLOSED[name]
    world = s.build(tmp_path, count=10, **build_kwargs)
    expected, kwargs = case(world)
    run = s.run_check(world, **kwargs)
    assert run.returncode == rc and run.returncode != 0, f"{name}\n{run.describe()}"
    for words in expected:
        assert s.has(run, *words), f"{name}: no line begins {' '.join(words)}\n{run.describe()}"
    assert not any("hold" in line or "questions (" in line for line in run.lines), (
        f"{name}: a refused set was judged\n{run.describe()}")


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads any folder")
@pytest.mark.parametrize("which", ["hidden-folder", "development-half", "sets-root", "a-question-file"])
def test_a_folder_or_file_the_program_may_not_read_is_refused(tmp_path, which):
    world = s.build(tmp_path, count=10)
    target = {"hidden-folder": world.hidden_dir, "development-half": world.dev_dir, "sets-root": world.root,
              "a-question-file": world.qpath("q07")}[which]
    expected = {"hidden-folder": "HIDDEN_UNREADABLE", "development-half": "HIDDEN_VISIBLE_UNREADABLE",
                "sets-root": "SETS_ROOT_UNREADABLE", "a-question-file": "QUESTION_UNREADABLE"}[which]
    mode = target.stat().st_mode
    target.chmod(0)
    try:
        run = s.run_check(world)
    finally:
        target.chmod(stat.S_IMODE(mode))
    assert run.returncode == 2 and s.has(run, "REFUSED", expected), run.describe()
    assert s.shape_faults(run) == [] and s.planted_hits(run, world) == [], run.describe()


def test_a_copy_whose_git_folder_is_gone_is_refused(tmp_path):
    import shutil

    world = s.build(tmp_path, count=10)
    shutil.rmtree(world.copy / ".git")
    run = s.run_check(world)
    assert run.returncode == 2 and s.has(run, "REFUSED", "COPY_UNREADABLE"), run.describe()


def test_a_committed_copy_head_is_read_not_a_working_tree_file(tmp_path):
    """The launch clone's COPY-HEAD.txt is the committed one: an edited working-tree file does not change the commit
    every question is held to."""
    world = s.build(tmp_path, count=10)
    (world.copy / s.COPY_HEAD_REL).write_text("b" * 40 + "\n", encoding="utf-8")
    run = s.run_check(world)
    assert run.returncode == 0, run.describe()
    assert run.lines[1] == "10 of 10 hold", run.describe()
