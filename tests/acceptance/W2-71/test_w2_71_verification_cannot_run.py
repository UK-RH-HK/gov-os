"""KPI 3 (DEC-911 item 4, DEC-298): a match whose verification cannot run fails closed. Each project quotes, after
the rule's keywords, a commit hash its repository has (or had), in a file and in a stored value; the check and the
pre-index filter run where the verification cannot:

- ``no-git``: no git on ``PATH`` (``PATH`` holds python3 and gitleaks only);
- ``not-a-repository``: the project's ``.git`` moved away after the commit, and git never looks above the sandbox;
- ``git-fails``: a git first on ``PATH`` that answers every call with exit 128 and a fatal line (and ``commit`` on
  standard output);
- ``git-hangs``: a git first on ``PATH`` that does not answer (it sleeps far beyond the check's declared limit).

Fails closed: the check ends within its declared limit (900 s) with a non-zero exit, naming the file or naming none
of the case's files (undecided); the filter ends within the same limit and does not return the path.

Guards, green today: today's check never runs git and finds each. They must stay green.
"""

from __future__ import annotations

import functools
import os
import shutil
import subprocess

import pytest

import w2_71_support as support

pytestmark = [support.needs_gitleaks, support.needs_git, pytest.mark.local_only]

ENVIRONMENTS = ["no-git", "not-a-repository", "git-fails", "git-hangs"]
PLACES = [("file", "vendor-keyword"), ("file", "prefix-keyword"), ("store", "vendor-keyword"),
          ("store", "prefix-keyword")]
IDS = [f"{form}-{name}" for form, name in PLACES]
KEYWORDS = {"vendor-keyword": support.VENDOR, "prefix-keyword": support.PREFIX}


class Case:
    def __init__(self, sandbox, environment):
        self.sandbox = sandbox
        self.repo = support.make_repo(sandbox, environment, label=environment)
        root = self.repo.root
        self.check_rels, self.filter_rels = {}, {}
        for form, name in PLACES:
            line = support.vendor_line(KEYWORDS[name], self.repo.head)
            check_rel = (f".gov-runtime/scratch/{name}.log" if form == "file"
                         else f".gov-runtime/stores/{name}.db")
            filter_rel = f"docs/{name}.md" if form == "file" else f"docs/{name}.db"
            self.check_rels[(form, name)], self.filter_rels[(form, name)] = check_rel, filter_rel
            for rel in (check_rel, filter_rel):
                if form == "file":
                    support.write(root / rel, "a log\n" + line)
                else:
                    support.sqlite_store(root / rel, ["a log", line])
        env = support.base_environment(sandbox)
        if environment == "no-git":
            env = support.base_environment(sandbox, path=str(support.bin_without_git(sandbox)))
        elif environment == "not-a-repository":
            shutil.move(str(root / ".git"), str(sandbox.elsewhere / f"{environment}.git-moved"))
        elif environment == "git-fails":
            env = support.base_environment(sandbox, path=f"{support.git_that_fails(sandbox)}{os.pathsep}{env['PATH']}")
        elif environment == "git-hangs":
            env = support.base_environment(sandbox, path=f"{support.git_that_hangs(sandbox)}{os.pathsep}{env['PATH']}")
        self.env = env
        self.check = support.run_check(sandbox, root, env=env)
        self.filter = support.run_filter(sandbox, root, sorted(self.filter_rels.values()), env=env)


class Cases:
    """Each environment's project, built and judged the first time a case asks for it."""

    def __init__(self, sandbox):
        self.sandbox = sandbox

    @functools.cache
    def __getitem__(self, environment):
        return Case(self.sandbox, environment)


@pytest.fixture(scope="module")
def cases(module_sandbox):
    return Cases(module_sandbox)


# ---- premises ----------------------------------------------------------------------------------------------------

def test_premise_no_git_is_on_the_path_of_the_no_git_case(sandbox):
    folder = support.bin_without_git(sandbox)
    found = shutil.which("git", path=str(folder))
    runs = [shutil.which(name, path=str(folder)) is not None for name in ("python3", "gitleaks")]
    assert found is None and all(runs), f"the no-git PATH finds git: {found is not None}; python3, gitleaks: {runs}"


def test_premise_the_project_without_its_git_folder_is_no_repository_even_unbounded(cases):
    case = cases["not-a-repository"]
    env = {key: value for key, value in case.env.items() if key != "GIT_CEILING_DIRECTORIES"}
    done = subprocess.run([support.REAL_GIT, "-C", str(case.repo.root), "rev-parse", "--git-dir"],
                                  capture_output=True, env=env, timeout=60)
    assert done.returncode != 0, "a repository is found at or above the project once its .git is moved away"


def test_premise_the_failing_git_answers_with_an_error(sandbox):
    folder = support.git_that_fails(sandbox)
    done = subprocess.run([str(folder / "git"), "cat-file", "-e", "0" * 40 + "^{commit}"],
                                  capture_output=True, text=True, timeout=60)
    assert done.returncode == 128 and done.stdout.strip() == "commit", "the failing stand-in does not answer as said"


# ---- the check and the filter ------------------------------------------------------------------------------------

@pytest.mark.parametrize("place", PLACES, ids=IDS)
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_the_check_fails_closed_when_the_verification_cannot_run(cases, environment, place):
    case = cases[environment]
    rel = case.check_rels[place]
    assert case.check.ended, (f"{environment}: the check did not end within its declared limit "
                              f"({support.declared_limit_s()} s)\n{case.check.describe()}")
    closed = support.check_fails_closed(case.check, rel, list(case.check_rels.values()))
    assert closed, (f"{environment}: the check passes {rel} (an unverified commit hash after the rule's keyword) as "
                    f"clean\n{case.check.describe()}")


@pytest.mark.parametrize("place", PLACES, ids=IDS)
@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_the_filter_fails_closed_when_the_verification_cannot_run(cases, environment, place):
    case = cases[environment]
    rel = case.filter_rels[place]
    assert case.filter.ended, (f"{environment}: the filter did not end within {support.declared_limit_s()} s\n"
                               f"{case.filter.describe()}")
    passes = case.filter.passes(rel)
    assert not passes, (f"{environment}: the filter lets {rel} (an unverified commit hash after the rule's keyword) "
                        f"through\n{case.filter.describe()}")
