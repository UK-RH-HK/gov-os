"""KPI success 1, its record half: "One helper does it, and the sweep record lists every call" [AR-2].

The ticket names the record (``docs/research/AR-2-git-sweep.md``) and the helper (``src/gov/util/gitenv.py``),
and says the sweep "names each file before it is changed" (its allowed paths). These cases hold the record to
that: it exists, it lists the calls in a table whose columns name at least the file and the call, and every
file of the Gov OS source that starts git is named in it. "Starts git" is read as a lower bound the tests can
see without reading the code: a file holding the string literal ``"git"`` (or ``'git'``), the program name an
argument list starts with. The record may list more (a git called by another name, a test helper elsewhere).

The behaviour of the calls is tested in ``test_w2_05_planted.py`` and ``test_w2_05_linked_worktree.py``.
"""

from __future__ import annotations

import subprocess
import sys

import w2_05_support as support

SWEEP = support.REPO_ROOT / support.SWEEP_REL


def _sweep_text():
    assert SWEEP.is_file(), f"the sweep record {support.SWEEP_REL} is absent (AR-2: the sweep is kept as a record)"
    return SWEEP.read_text(encoding="utf-8")


def test_the_sweep_record_lists_the_calls_in_a_table():
    text = _sweep_text()
    headers = support.table_headers(text)
    listing = [cells for cells in headers
               if any("file" in cell for cell in cells) and any("call" in cell for cell in cells)]
    assert listing, (f"{support.SWEEP_REL} holds no table of the calls whose columns name the file and the call; "
                     f"tables found: {headers}")


def test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep():
    text = _sweep_text()
    starting = support.files_that_start_git()
    assert starting, "no file of src/gov names git: the lower bound of the sweep is empty, the case is wrong"
    unnamed = [rel for rel in starting if not support.names_file(text, rel)]
    assert not unnamed, (f"{support.SWEEP_REL} does not name {len(unnamed)} of the {len(starting)} files of "
                         f"src/gov that start git: {unnamed}")


def test_the_one_helper_is_there_and_the_sweep_names_it(code_under_test):
    done = subprocess.run(
        [sys.executable, "-c", f"import {support.HELPER_MODULE} as m; print(m.__file__)"],
        capture_output=True, text=True, env={"PATH": support.SYSTEM_PATH, "PYTHONPATH": str(code_under_test),
                                             "PYTHONDONTWRITEBYTECODE": "1"},
        cwd=str(support.REPO_ROOT.parent), timeout=60)
    assert done.returncode == 0, (f"{support.HELPER_MODULE} cannot be imported from this worktree's src "
                                  f"(one helper clears the GIT_* variables, AR-2):\n{support.said(done)}")
    assert done.stdout.strip().startswith(str(code_under_test)), (
        f"{support.HELPER_MODULE} was imported from {done.stdout.strip()}, not from {code_under_test}")
    text = _sweep_text()
    assert support.names_file(text, support.HELPER_REL), (
        f"{support.SWEEP_REL} does not name the helper {support.HELPER_REL}")
