"""KPI success 1: tk v0.3.2 is vendored with sha256 408f2c11..., verified by gov doctor.

The vendored copy is ``template/governance/kernel/bin/tk`` (DEC-074 T3, ADR-0002
section 3). These tests check the file against the pin. ``gov doctor`` is built
by W1-27 and stays reserved; its check of the vendored copy is that ticket's.
"""

from __future__ import annotations

import os
import stat
import subprocess

import w1_09_support as support


def test_the_ticket_script_is_vendored_into_the_kernel_template(vendored):
    assert not vendored.is_symlink(), f"{support.VENDORED_REL} is a link, not the vendored script itself"
    assert stat.S_ISREG(vendored.stat().st_mode), f"{support.VENDORED_REL} is not a regular file"


def test_the_vendored_script_has_the_pinned_sha256(vendored):
    found = support.sha256(vendored)
    assert support.TK_SHA256.startswith("408f2c11")
    assert found == support.TK_SHA256, \
        f"{support.VENDORED_REL} has sha256 {found}, not the pinned {support.TK_SHA256} of ticket {support.TK_VERSION}"


def test_the_vendored_script_matches_the_tool_registry(vendored):
    """The registry records ticket v0.3.2 with its sha256; the vendored copy is that script."""
    entry = support.registry_entry("ticket")
    assert entry.get("version") == support.TK_VERSION, f"the registry records ticket {entry.get('version')!r}"
    assert entry.get("sha256") == support.sha256(vendored), \
        f"{support.VENDORED_REL} is not the script the tool registry records (sha256 {entry.get('sha256')})"


def test_the_vendored_script_is_executable(vendored):
    assert os.access(vendored, os.X_OK), f"{support.VENDORED_REL} is not executable"
    tracked = support.git(support.REPO_ROOT, "ls-files", "-s", "--", support.VENDORED_REL).split()
    assert tracked and tracked[0] == "100755", \
        f"{support.VENDORED_REL} is not tracked by git as an executable file: {tracked[:1]}"


def test_the_vendored_script_works_without_the_installed_one(vendored, tmp_path):
    """Run from the template, with no ``tk`` on ``PATH``: it creates a ticket and lists it as ready."""
    project = tmp_path / "project"
    project.mkdir()
    env = {"PATH": support.path_without_tk(), "HOME": str(tmp_path), "LC_ALL": "C.UTF-8"}

    def tk(*args):
        done = subprocess.run([str(vendored), *args], cwd=str(project), env=env, capture_output=True, text=True,
                              timeout=60)
        assert done.returncode == 0, f"tk {' '.join(args)} failed (exit code {done.returncode}):\n{done.stderr}"
        return done.stdout

    ticket = tk("create", "A first ticket").strip()
    assert (project / ".tickets" / f"{ticket}.md").is_file(), f"tk create printed {ticket!r} and wrote no ticket"
    assert ticket in tk("ready"), f"tk ready does not list the new ticket {ticket}"
