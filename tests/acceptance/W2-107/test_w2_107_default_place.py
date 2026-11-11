"""W2-107: where the cache is, by default and by setting.

KPI success 1's place (one machine-wide cache at ``~/.cache/gov-os/secrets-scan.sqlite``, outside every repository, its
folder made owner-only if missing); the design's settings: ``GOV_SECRETS_CACHE`` set to the empty string uses no cache
at all; under pytest (``PYTEST_CURRENT_TEST``) with no cache named, none is used. Each pass is a child process with
``HOME`` set to a folder of the case, so the real ``~/.cache/gov-os/`` is never touched.
"""

from __future__ import annotations

import stat

import w2_107_support as support

pytestmark = support.needs_tools

FILES = {
    "docs/alpha.md": "W2-107: the alpha page, ordinary text.\n",
    "docs/beta.md": "W2-107: the beta page, ordinary text.\n",
}
NAME = "docs/an-ordinary-name.md"
OUTSIDE_PYTEST = ("GOV_SECRETS_CACHE", "PYTEST_CURRENT_TEST", "XDG_CACHE_HOME", "GOV_SECRETS_FULL_SCAN")


def passes(project, engine, env, count=2):
    """``count`` passes in child processes; the scan calls of each."""
    rels = list(FILES)
    out = []
    for _ in range(count):
        run, calls = support.counted(engine, lambda: support.run_child(project, rels, [NAME], env))
        assert run.error is None and run.indexable == rels and run.names == [False], "the verdicts are right"
        out.append(calls)
    return out


def test_with_no_cache_named_outside_pytest_the_cache_is_made_in_the_home_folder(tmp_path, project, engine, per_text):
    support.put(project, FILES)
    home = tmp_path / "child-home"
    home.mkdir()
    before = support.files_under(project)
    env = support.child_env(engine, None, home=home, drop=OUTSIDE_PYTEST)
    calls = passes(project, engine, env)
    made = home / ".cache" / "gov-os" / support.CACHE_NAME
    assert made.is_file(), "the cache is made at <HOME>/.cache/gov-os/secrets-scan.sqlite"
    assert stat.S_IMODE(made.parent.stat().st_mode) & 0o077 == 0, "its folder is the owner's only"
    assert calls == [3 * per_text, 0], "the second process is answered from the cache in the home folder"
    assert support.files_under(project) == before, "nothing is written in the repository"


def test_an_empty_cache_setting_uses_no_cache_at_all(tmp_path, project, engine, per_text):
    """A guard: the base code uses no cache either."""
    support.put(project, FILES)
    home, temp = tmp_path / "child-home", tmp_path / "child-tmp"
    home.mkdir()
    temp.mkdir()
    before = support.files_under(project)
    env = support.child_env(engine, "", home=home, extra={"TMPDIR": str(temp)},
                            drop=("PYTEST_CURRENT_TEST", "XDG_CACHE_HOME", "GOV_SECRETS_FULL_SCAN"))
    assert passes(project, engine, env) == [3 * per_text, 3 * per_text], "every call scans every text"
    assert support.files_under(home) == [] and support.files_under(temp) == [], "no cache file is made anywhere"
    assert support.files_under(project) == before, "nor in the repository"


def test_under_pytest_with_no_cache_named_no_cache_is_used(tmp_path, project, engine, per_text):
    """A guard: while a test runs (``PYTEST_CURRENT_TEST``) and names no cache, every scan happens as before."""
    support.put(project, FILES)
    home = tmp_path / "child-home"
    home.mkdir()
    env = support.child_env(engine, None, home=home, extra={"PYTEST_CURRENT_TEST": "test_w2_107_example (call)"},
                            drop=("GOV_SECRETS_CACHE", "XDG_CACHE_HOME", "GOV_SECRETS_FULL_SCAN"))
    assert passes(project, engine, env) == [3 * per_text, 3 * per_text], "every call scans every text"
    assert support.files_under(home) == [], "no cache is made in the home folder"
