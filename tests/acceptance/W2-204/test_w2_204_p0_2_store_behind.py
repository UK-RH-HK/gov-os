"""W2-204 fix P0-2 (plan item 0-2; DAEO-ma4q "Fix: the pre-flight refuses a store behind HEAD"): ``gov memaudit
preflight`` exits with ``STORE_BEHIND``, naming the store's commit and HEAD, when the integration store's commit is not
the repository's HEAD, and writes no declaration. README: "P0-2".

The planted store is the one W2-116 keeps: ``integration_store`` of the repository's ``governance/project/rebuild.yaml``
is a link to a detached worktree of the repository, and the worktree's ``.gov-runtime/store.db`` has a ``fingerprints``
row (as ``rebuild_stub.py`` writes it) for the commit the worktree is at. Both name the same commit, so whichever of the
two the pre-flight reads gives the same answer. The repository carries the file as a commit of its own (HEAD).
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import w2_204_support as K
from w2_204_support import HIDDEN, VISIBLE, W171

SETTINGS_REL = "governance/project/rebuild.yaml"
OK_LINE = "PRE-FLIGHT: every check as expected"


def _git(world, *args):
    return W171.git(world.repo, *args, home=world.home).strip()


def _head(world):
    return _git(world, "rev-parse", "HEAD")


def _delivered(world):
    """A delivered, noted hidden half (and the visible one): a set whose pre-flight passes."""
    world.make_step_store()
    for audit in (VISIBLE, HIDDEN):
        world.write_half(audit, K.clean_specs())
        world.write_notes(audit)
    world.install_plans()


def _configured(world):
    """The repository names its integration store (a link outside it); HEAD is the commit that adds the file. Returns
    the link."""
    link = world.base / "integration"
    (world.repo / SETTINGS_REL).parent.mkdir(parents=True, exist_ok=True)
    (world.repo / SETTINGS_REL).write_text(f"slow_after_s: 600\nintegration_store: {link}\n", encoding="utf-8")
    _git(world, "add", "-f", SETTINGS_REL)
    _git(world, "commit", "-q", "-m", "P0-2: the integration store's place", "--", SETTINGS_REL)
    return link


def _store_at(world, link, commit):
    """The store at ``commit``: a detached worktree there, its store file naming the commit, the link to it."""
    half = world.base / f"store-{commit[:8]}"
    if not half.exists():
        _git(world, "worktree", "add", "-q", "--detach", str(half), commit)
        store = half / ".gov-runtime" / "store.db"
        store.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(store)
        connection.execute("CREATE TABLE fingerprints (head TEXT NOT NULL, code TEXT, records TEXT, kind TEXT NOT NULL)")
        connection.execute("INSERT INTO fingerprints VALUES (?, ?, ?, ?)", (commit, "c0de", "rec0", "rebuild"))
        connection.commit()
        connection.close()
    if os.path.lexists(link):
        os.unlink(link)
    os.symlink(half, link)


def _commit_something(world, name):
    (world.repo / "records" / name).write_text("A record written after the store was built.\n", encoding="utf-8")
    _git(world, "add", f"records/{name}")
    _git(world, "commit", "-q", "-m", f"P0-2: {name}", "--", f"records/{name}")
    return _head(world)


def _no_declaration(world):
    found = [str(p) for p in world.base.rglob("DECLARATION.json")]
    assert not found, f"a declaration was written while the store is behind HEAD: {found}"


def test_p0_2_preflight_refuses_store_behind_naming_both_commits_and_writes_no_declaration(world):
    _delivered(world)
    link = _configured(world)
    head = _head(world)
    behind_at = world.later_commit                     # the commit before the settings file: one behind HEAD
    assert behind_at != head
    _store_at(world, link, behind_at)
    run = world.step("preflight", HIDDEN)
    assert run.code != 0 and "STORE_BEHIND" in run.text, f"the pre-flight did not refuse STORE_BEHIND\n{run!r}"
    assert behind_at[:12] in run.text and head[:12] in run.text, (
        f"the refusal does not name the store's commit {behind_at[:12]} and HEAD {head[:12]}\n{run!r}")
    assert OK_LINE not in run.lines, f"the pre-flight said everything was as expected\n{run!r}"
    _no_declaration(world)


def test_p0_2_a_store_at_head_passes_and_the_next_commit_makes_it_behind(world):
    _delivered(world)
    link = _configured(world)
    head = _head(world)
    _store_at(world, link, head)
    ok = world.step("preflight", HIDDEN)
    assert ok.code == 0 and ok.last == OK_LINE and "STORE_BEHIND" not in ok.text, f"a store at HEAD did not pass\n{ok!r}"
    newer = _commit_something(world, "after-the-store.md")
    run = world.step("preflight", HIDDEN)
    assert run.code != 0 and "STORE_BEHIND" in run.text, f"after a commit the pre-flight did not refuse\n{run!r}"
    assert head[:12] in run.text and newer[:12] in run.text, (
        f"the refusal does not name the store's commit {head[:12]} and HEAD {newer[:12]}\n{run!r}")
    _no_declaration(world)
