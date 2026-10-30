"""Builder tests of the nightly's clean-up (W2-77; DEC-939 item 5, row W2-M406): only the clone, by its exact path,
its own entry alone when that fails, and never a prune."""
from __future__ import annotations

import inspect
import shutil

from gov.close import nightly

from .conftest import Repo


def _add(repo: Repo, path) -> None:
    repo.git("worktree", "add", "--detach", "--force", str(path), "HEAD")


def _registered(repo: Repo) -> list[str]:
    return [line.split(" ", 1)[1] for line in repo.git("worktree", "list", "--porcelain").splitlines()
            if line.startswith("worktree ")]


def test_the_clone_goes_by_its_exact_path_and_a_stale_registration_stays(repo: Repo, tmp_path):
    repo.commit("one")
    stale = tmp_path / "stale"
    _add(repo, stale)
    shutil.rmtree(stale)
    clone = tmp_path / "work" / "tree"
    _add(repo, clone)
    entry = nightly._entry_of(clone)
    assert entry is not None and entry.is_dir()
    assert nightly._remove_clone(repo.root, clone, entry) is None
    assert not clone.exists() and not entry.exists()
    assert str(stale) in _registered(repo)


def test_a_failed_removal_takes_only_the_clone_s_own_entry_and_says_so(repo: Repo, tmp_path, capsys):
    repo.commit("one")
    other = tmp_path / "elsewhere" / "tree"
    _add(repo, other)
    clone = tmp_path / "work" / "tree"
    _add(repo, clone)
    entry = nightly._entry_of(clone)
    assert entry.name != "tree"  # read from the clone's .git, never guessed from its folder's name
    repo.git("worktree", "lock", str(clone))
    cleanup = nightly._remove_clone(repo.root, clone, entry)
    assert cleanup["ok"] is False and cleanup["entry_removed"] is True
    assert cleanup["clone"] == str(clone) and cleanup["entry"] == str(entry) and cleanup["error"]
    assert not entry.exists()
    assert (repo.root / ".git" / "worktrees" / "tree").is_dir() and str(other) in _registered(repo)
    assert str(clone) in capsys.readouterr().err


def test_an_entry_not_confirmed_as_the_clone_s_is_left_and_reported(repo: Repo, tmp_path):
    repo.commit("one")
    clone = tmp_path / "work" / "tree"
    _add(repo, clone)
    entry = nightly._entry_of(clone)
    repo.git("worktree", "lock", str(clone))
    (entry / "gitdir").write_text(str(tmp_path / "someone-else" / ".git") + "\n", encoding="utf-8")
    cleanup = nightly._remove_clone(repo.root, clone, entry)
    assert cleanup["entry_removed"] is False and entry.is_dir()


def test_the_night_has_no_worktree_prune():
    assert '"prune"' not in inspect.getsource(nightly)
