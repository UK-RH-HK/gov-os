"""KPI success 3: registers the index-freshness family check: the index digest matches the tracked blobs, and a
stale index is reported [CAP-38.b].

The ticket registers the check as a declaration under ``template/governance/kernel/checks/``, so
``gov check --list --json`` lists it. Running checks through ``gov check`` is W1-26; until then the tests run the
declared ``command`` themselves, by ``sh -c`` in the root of a project, and read its exit code (DEC-285): 0 when
the index is up to date with the tracked files, another code when it is not.
"""

from __future__ import annotations

import pytest

import w1_17_support as support


def test_the_check_is_registered_in_the_kernel_template(family_check):
    """One listed check of the family, with the five fields of a declaration and a command to run."""
    for field in support.CHECK_FIELDS:
        assert isinstance(family_check.get(field), str) and family_check[field].strip(), \
            f"the listed index-freshness check has no {field}: {family_check!r}"
    assert family_check["severity"] in ("hard-block", "warning"), family_check


def test_the_check_is_green_on_an_index_that_matches_the_tracked_blobs(api, family_check, repo):
    """The tree holds a product-data file and a file with a canary: neither is in the index, and neither makes
    it stale."""
    support.write(repo, "notes/planted.md", f"# Notes\n\n{support.CANARY}\n")
    support.commit(repo, "a file with a canary")
    api.refresh(repo)
    run = support.run_check(family_check, repo, api)
    assert run.returncode == 0, f"the index is up to date and the check is not green\n{run.describe()}"


def _an_edit(repo):
    return support.write(repo, support.RUNBOOK, support.RUNBOOK_TEXT.replace("drains", "empties"))


def _a_new_file(repo):
    return support.write(repo, "notes/added.md", "# Added\n\nA new note.\n")


def _a_removed_file(repo):
    support.git(repo, "rm", "-q", support.CLIENT)
    return support.CLIENT


@pytest.mark.parametrize("change", [_an_edit, _a_new_file, _a_removed_file],
                         ids=["a file is edited", "a file is added", "a file is removed"])
def test_the_check_is_not_green_on_a_stale_index_and_names_the_file(api, family_check, repo, change):
    before = api.refresh(repo)["digest"]
    rel = change(repo)
    support.commit(repo, "the tracked content changes")
    run = support.run_check(family_check, repo, api)
    assert run.returncode != 0, f"the index is stale and the check is green\n{run.describe()}"
    assert rel in run.output, f"the check does not say which file is stale ({rel})\n{run.describe()}"
    assert "Traceback" not in run.output, f"the check reports a stale index with a traceback\n{run.describe()}"
    assert api.digest(repo) == before, "the check changed the index: a check reports, it does not repair"


def test_the_check_is_green_again_once_the_index_is_refreshed(api, family_check, repo):
    api.refresh(repo)
    _an_edit(repo)
    support.commit(repo, "the tracked content changes")
    assert support.run_check(family_check, repo, api).returncode != 0
    api.refresh(repo)
    run = support.run_check(family_check, repo, api)
    assert run.returncode == 0, run.describe()


def test_the_check_is_not_green_when_there_is_no_index(api, family_check, repo):
    """Package DP-5, the recommended option: no index matches no tracked blob. The check says so and writes
    nothing."""
    run = support.run_check(family_check, repo, api)
    assert run.returncode != 0, f"there is no index and the check is green\n{run.describe()}"
    assert "Traceback" not in run.output, f"the check reports a missing index with a traceback\n{run.describe()}"
    assert not (repo / support.RUNTIME_REL).exists(), "the check wrote .gov-runtime/"
