"""BR-DAG-AMEND-R1-6 regression test.

``govbridge.core.gitobj.repo_root()`` used to be ``functools.lru_cache``'d directly on the function, keyed on its
argument verbatim. Every BARE call (``repo or repo_root()``, throughout this package) passes exactly ``None``, so
the cache's one ``None`` slot was won by the FIRST bare caller's current working directory, for the rest of the
process -- a later ``os.chdir`` was invisible to it. This test builds two separate, unrelated git repositories,
``os.chdir``s into the first, resolves ``repo_root()`` (bare, no argument), then ``os.chdir``s into the second and
resolves it again: before the fix the second call still returns the FIRST repo's root; after the fix it correctly
returns the second repo's own root. ``monkeypatch.chdir`` restores the original working directory automatically
(hermetic: this test never leaves the process cwd changed for a later test, and never depends on cwd on entry).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from govbridge.core import gitobj


def _clear_repo_root_cache() -> None:
    """Isolates this test's cache from whatever an earlier test already resolved. Tries the FIXED module's own
    ``_repo_root_cached`` (the actual lru_cache target after BR-DAG-AMEND-R1-6) first, and falls back to clearing
    ``repo_root`` itself -- the PRE-fix shape, where ``repo_root`` was directly ``functools.lru_cache``'d -- so this
    test demonstrates the real caching bug (the first chdir's cwd winning) against the unfixed module too, rather
    than failing on an incidental ``AttributeError``."""
    clearer = getattr(gitobj, "_repo_root_cached", None) or gitobj.repo_root
    clearer.cache_clear()


def _init_repo(root: Path) -> str:
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(root), check=True)
    (root / "marker.txt").write_text("hello\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(root), check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "c1"],
        cwd=str(root), check=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=str(root), capture_output=True, text=True, check=True
    ).stdout.strip()


def test_two_chdirs_in_one_process_resolve_two_repositories(tmp_path, monkeypatch):
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    root_a = _init_repo(repo_a)
    root_b = _init_repo(repo_b)
    assert root_a != root_b

    _clear_repo_root_cache()

    monkeypatch.chdir(repo_a)
    resolved_a = gitobj.repo_root()
    assert resolved_a == root_a

    monkeypatch.chdir(repo_b)
    resolved_b = gitobj.repo_root()
    assert resolved_b == root_b, (
        "repo_root() returned the FIRST chdir's repo after a second chdir -- the process-lifetime cache is still "
        "keyed on the bare call, not on the resolved starting directory"
    )

    # a third chdir back to the first repo resolves it again too -- not merely "the second call always wins".
    monkeypatch.chdir(repo_a)
    assert gitobj.repo_root() == root_a


def test_explicit_start_argument_still_resolves_and_caches_independently_of_cwd(tmp_path, monkeypatch):
    repo_a = tmp_path / "repo_c"
    root_a = _init_repo(repo_a)
    _clear_repo_root_cache()

    monkeypatch.chdir(tmp_path)  # cwd is NOT a git repo at all
    assert gitobj.repo_root(str(repo_a)) == root_a
    # a relative start path resolves to the same absolute key as the already-absolute one above (Path.resolve()),
    # so this is a cache HIT on the same underlying repository, not a second, divergent entry.
    monkeypatch.chdir(repo_a)
    assert gitobj.repo_root(".") == root_a
