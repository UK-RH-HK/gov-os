"""W2-59 KPI success 5: ``gov --version`` names the version and the commit.

It prints the package's version, as ``pyproject.toml`` states it, and the commit of the code that runs, and exits 0,
with no command and outside any project. From this worktree's code in a git repository, the commit is that
repository's ``HEAD``, whatever the working folder. Never a wrong commit: run inside another git repository, the
answer never names that repository's commit.

From an installed wheel (the stand-in, built like the owner's pin from a tree that the installed package keeps no
git metadata of): the version, exit 0, and never a wrong commit. Whether the installed pin must also name its
commit is package P-W2-59-2 (README); no case here requires it.
"""

from __future__ import annotations

import w2_59_support as support


def _worktree_code_version(cwd, tmp_path):
    env = support.worktree_code_env(tmp_path / "home")
    (tmp_path / "home").mkdir(exist_ok=True)
    return support.run([support.REAL_PYTHON, "-m", "gov.cli.main", "--version"], cwd=cwd, env=env)


def _assert_names_only(done, head, other=None):
    named = support.named_commits(done.stdout)
    assert named, f"gov --version names no commit\n{done.describe()}"
    wrong = [commit for commit in named if not head.startswith(commit)]
    assert not wrong, f"gov --version names {wrong}, not the commit of the code that runs ({head})\n{done.describe()}"
    if other is not None:
        assert not any(other.startswith(commit) for commit in named), (
            f"gov --version names the commit of the working folder's repository ({other})\n{done.describe()}")


def test_from_this_worktree_s_code_outside_any_project_it_names_the_version_and_head(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    done = _worktree_code_version(outside, tmp_path)
    assert done.returncode == 0, f"gov --version, with no command and outside any project, failed\n{done.describe()}"
    assert support.names_version(done.stdout, support.package_version()), (
        f"gov --version does not name the version {support.package_version()} of pyproject.toml\n{done.describe()}")
    _assert_names_only(done, support.worktree_head())


def test_inside_another_git_repository_it_names_the_code_s_commit_not_that_repository_s(tmp_path):
    other = support.make_repository(tmp_path / "other")
    other_head = support.git(other, "rev-parse", "HEAD")
    done = _worktree_code_version(other, tmp_path)
    assert done.returncode == 0, done.describe()
    _assert_names_only(done, support.worktree_head(), other_head)


def test_the_installed_pin_names_its_version_and_never_a_wrong_commit(stand_in, tmp_path):
    other = support.make_repository(tmp_path / "other")
    other_head = support.git(other, "rev-parse", "HEAD")
    box = support.make_box(tmp_path / "box", stand_in)
    env = support.base_env(box.home, f"{box.local_bin}:{support.SYSTEM_PATH}")
    done = support.run([box.local_bin / "gov", "--version"], cwd=other, env=env)
    assert done.returncode == 0, f"the installed gov --version failed\n{done.describe()}"
    assert support.names_version(done.stdout, support.package_version()), (
        f"the installed gov --version does not name the version {support.package_version()}\n{done.describe()}")
    named = support.named_commits(done.stdout)
    head = support.worktree_head()
    wrong = [commit for commit in named if not head.startswith(commit)]
    assert not wrong, (
        f"the installed gov --version names {wrong}: not the commit its wheel was built from ({head})"
        f"{' and the working folder repository is ' + other_head if any(other_head.startswith(c) for c in named) else ''}"
        f"\n{done.describe()}")
