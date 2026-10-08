"""The pre-commit hook: G1-G2 and both gitleaks scans (KPI S1 first clause, S3) [CAP-39.a].

Every commit here is a plain ``git commit`` in a temporary repository where ``lefthook install`` put the hooks
of the repository's ``lefthook.yml``. A commit is refused when HEAD does not move.
"""

from __future__ import annotations

import pytest

import w1_40_support as support


def test_a_clean_commit_passes_and_runs_the_g1_and_g2_checks(project, machine):
    done, moved = project.commit(machine())
    assert moved, f"a commit with every check passing and no secret was refused:\n{support.said(done)}"
    assert project.ran("G1") >= 1, f"the project's G1 check did not run at commit:\n{support.said(done)}"
    assert project.ran("G2") >= 1, f"the project's G2 check did not run at commit:\n{support.said(done)}"


@pytest.mark.parametrize("tier", ["G1", "G2"])
def test_a_failing_hard_block_check_stops_the_commit(project, machine, tier):
    project.fail(tier)
    done, moved = project.commit(machine())
    assert project.ran(tier) >= 1, f"the {tier} check did not run at commit:\n{support.said(done)}"
    assert not moved, f"a failing {tier} hard-block check did not stop the commit:\n{support.said(done)}"
    assert done.returncode != 0


def test_the_commit_passes_again_once_the_check_passes(project, machine):
    """The refusal is the check's verdict, not a state the hook keeps."""
    dev = machine()
    project.fail("G1")
    _, moved = project.commit(dev)
    assert not moved
    project.fail("G1", failing=False)
    done, moved = project.commit(dev)
    assert moved, f"the commit stayed refused after the check passed:\n{support.said(done)}"


def test_the_g3_check_does_not_run_at_commit(project, machine):
    """G3 is the pre-push gate (DEC-075): a commit neither runs it nor is stopped by it."""
    project.fail("G3")
    done, moved = project.commit(machine())
    assert moved, f"a failing G3 check stopped a commit: G3 belongs to pre-push:\n{support.said(done)}"
    assert project.ran("G3") == 0, "the G3 check ran at commit"


def test_a_staged_secret_stops_the_commit(project, machine):
    dev = machine()
    assert support.single_scan_finds(support.PLAIN, dev), "the fixture value is not a secret by the project's file"
    done, moved = project.commit(dev, "app/settings.py", f'KEY = "{support.PLAIN}"\n')
    assert not moved, f"a staged secret did not stop the commit:\n{support.said(done)}"
    assert support.PLAIN not in done.stdout + done.stderr, "the hook printed the secret"


@pytest.mark.parametrize("shelter", sorted(support.SHELTERED))
def test_a_staged_secret_that_the_builtin_allowlist_shelters_stops_the_commit(project, machine, shelter):
    """DEC-347, DEC-369: the second scan, with the project's rules alone, runs at commit."""
    dev = machine()
    value = support.SHELTERED[shelter]
    assert not support.single_scan_finds(value, dev), (
        "the fixture value is no longer sheltered by gitleaks' built-in allowlist: this case would not show "
        "the second scan")
    done, moved = project.commit(dev, "app/settings.py", f'KEY = "{value}"\n')
    assert not moved, (
        f"a staged secret by the project's rules, sheltered by gitleaks' built-in allowlist ({shelter}), "
        f"did not stop the commit:\n{support.said(done)}")


def test_the_sheltering_words_alone_do_not_stop_a_commit(project, machine):
    """The second scan has the project's rules, not a ban on words."""
    text = f'LETTERS = "{support._RUN}"\nSTRICT = False\nVALUE = None  # null\n'
    done, moved = project.commit(machine(), "app/letters.py", text)
    assert moved, f"ordinary code with the sheltering words was refused:\n{support.said(done)}"


def test_a_secret_staged_beside_a_clean_working_copy_is_what_counts(project, machine):
    """The hook judges what is staged: the secret is staged, then the file is cleaned without staging again."""
    dev = machine()
    path = project.write("app/settings.py", f'KEY = "{support.SHELTERED["alphabet"]}"\n')
    support.sh(["git", "add", "--", "app/settings.py"], project.root, dev.env(), check=True)
    path.write_text('KEY = ""\n', encoding="utf-8")
    before = project.head()
    done = support.sh(["git", "commit", "-m", "settings"], project.root, dev.env())
    assert project.head() == before, f"a staged secret passed because the working copy was clean:\n{support.said(done)}"


@pytest.mark.parametrize("missing", ["gitleaks", "gov"])
def test_a_missing_tool_stops_the_commit(project, machine, missing):
    """DEC-449, DEC-454: what was not measured is refused. A tool the hook names and cannot run is a failure."""
    done, moved = project.commit(machine(**{missing: False}))
    assert not moved, f"the commit passed although {missing} could not run:\n{support.said(done)}"
