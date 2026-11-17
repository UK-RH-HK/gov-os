"""Success 5 [CAP-43]: two repositories on the machine run two different releases side by side."""

from __future__ import annotations

import sys

import pytest

import w2_18_support as s


@pytest.mark.parametrize("folder", ["top", "subfolder"])
@pytest.mark.parametrize("launcher", ["console-script", "python-m"])
def test_the_same_gov_runs_each_repository_s_pinned_release(planted_a, planted_b, launcher, folder, sandbox):
    script = s.gov_console_script(sandbox)

    def version(cwd, **extra):
        if launcher == "console-script":
            env = s.base_env(sandbox, path=f"{script.parent}:{s.SYSTEM_PATH}", **extra)
            return s.run(("gov", "--version"), cwd, env)
        env = s.base_env(sandbox, PYTHONPATH=s.SRC, **extra)
        return s.run((sys.executable, "-m", "gov.cli.main", "--version"), cwd, env)

    own = version(sandbox.elsewhere)  # outside every repository: the launcher's own gov ("gov <version> (commit …)")
    assert own.returncode == 0 and len(own.stdout.split()) >= 2, f"the gov launcher does not run\n{own.describe()}"
    assert not any(s.prints_version(own.stdout, release) for release in (s.VERSION_A, s.VERSION_B)), \
        f"the launcher's own gov prints a fixture release's version: the case cannot tell them apart\n{own.describe()}"
    trees = {s.VERSION_A: planted_a, s.VERSION_B: planted_b}
    before = {release: s.working_tree_state(tree) for release, tree in trees.items()}
    for release, tree in trees.items():
        cwd = tree if folder == "top" else tree / "governance"
        done = version(cwd)
        assert done.returncode == 0 and s.prints_version(done.stdout, release), (
            f"`gov --version` in a repository pinned to release {release} ({cwd}) does not print {release}\n"
            f"{done.describe()}")
        off = version(cwd, GOV_PIN="off")
        assert off.returncode == 0 and off.stdout.split()[:2] == own.stdout.split()[:2], (
            f"with GOV_PIN=off `gov --version` in {cwd} does not run the launcher's own gov ({own.stdout.strip()})\n"
            f"{off.describe()}")
    for release, tree in trees.items():
        assert s.working_tree_state(tree) == before[release], f"the repository pinned to {release} changed"
