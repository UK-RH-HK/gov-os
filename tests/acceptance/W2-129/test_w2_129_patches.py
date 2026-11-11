"""W2-129 S12: --propose-marks and --propose-sources print patches that ``git apply`` accepts and that mend what
they name; neither writes a file (the mark aside). Each case works on its own copy of repository A."""

from __future__ import annotations

import subprocess

import pytest
import yaml
import w2_129_support as support
from w2_129_support import REGISTER

T001 = ".tickets/DAEO-t001.md"
UNMARKED = (("DEC-101", "DEC-102"), ("DEC-103", "DEC-104"), ("DEC-109", "DEC-110"), ("DEC-111", "DEC-112"),
            ("DEC-130", "DEC-131"))


def propose(shas: dict, flag: str, tmp_path) -> tuple:
    """The patch ``flag`` prints (with --all), written outside the repository, and whether the run wrote nothing."""
    repo = shas["repo"]
    files, state = support.tree_digest(repo), support.git_state(repo)
    done = support.run_links(repo, "--all", flag)
    assert done.returncode in (0, 1), done
    patch = tmp_path / f"{flag.strip('-')}.patch"
    patch.write_text(done.stdout)
    return patch, support.tree_digest(repo) == files and support.git_state(repo) == state


def git_apply(repo, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "apply", *args], cwd=repo, capture_output=True, text=True, env=support.git_env())


@pytest.mark.parametrize("flag", ["--propose-marks", "--propose-sources"])
def test_s12_the_patch_applies_with_git_apply_check_and_nothing_is_written(fresh, tmp_path, flag):
    patch, untouched = propose(fresh, flag, tmp_path)
    assert untouched, "the run changed a file other than its mark"
    checked = git_apply(fresh["repo"], "--check", str(patch))
    assert checked.returncode == 0, (checked.stderr, patch.read_text())


def test_s12_propose_marks_adds_changed_by_or_superseded_by_to_each_status_line(fresh, tmp_path):
    repo = fresh["repo"]
    patch, _ = propose(fresh, "--propose-marks", tmp_path)
    applied = git_apply(repo, str(patch))
    assert applied.returncode == 0, applied.stderr
    text = (repo / REGISTER).read_text()
    assert "SUPERSEDED by DEC-102" in support.status_line(text, "DEC-101"), support.status_line(text, "DEC-101")
    for changed, changer in (("DEC-103", "DEC-104"), ("DEC-109", "DEC-110")):
        line = support.status_line(text, changed)
        assert "**Changed by:**" in line and changer in line, line
    for changed, changer in (("DEC-111", "DEC-112"), ("DEC-130", "DEC-131")):
        assert changer in support.status_line(text, changed), support.status_line(text, changed)


def test_s12_after_the_marks_patch_no_unmarked_change_is_left(fresh, tmp_path):
    repo = fresh["repo"]
    patch, _ = propose(fresh, "--propose-marks", tmp_path)
    assert git_apply(repo, str(patch)).returncode == 0
    support.commit(repo, "the marks", {"Task": "decision-record", "Implements": "DEC-100", "Role": "orchestrator"},
                   10, [REGISTER])
    out = support.links(repo, "--all")
    assert out.findings, out.text()
    assert not [pair for pair in UNMARKED if out.of("UNMARKED_CHANGE", *pair)], out.text()


def test_s12_propose_sources_adds_each_unlinked_id_to_its_ticket_s_sources(fresh, tmp_path):
    repo = fresh["repo"]
    patch, _ = propose(fresh, "--propose-sources", tmp_path)
    assert git_apply(repo, str(patch)).returncode == 0
    front = yaml.safe_load((repo / T001).read_text().split("---\n")[1])
    assert {"DEC-104", "DEC-105", "DEC-121"} <= set(front["sources"]), front["sources"]
    support.commit(repo, "the sources", {"Task": "DAEO-t001", "Implements": "DEC-100", "Role": "orchestrator"}, 10,
                   [T001])
    out = support.links(repo, "--all")
    assert not [f for f in out.of("UNLINKED_ID") if f.path == T001 or "DAEO-t001" in f.raw], out.text()
