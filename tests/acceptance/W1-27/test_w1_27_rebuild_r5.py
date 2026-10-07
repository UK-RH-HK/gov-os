"""Round 5: rebuild on a project with no path map, and an owner that raises
unexpectedly (DEC-440).

DEC-440 says rebuild recreates every derived store by the code that owns it.
The lexical index's owner calls the secrets filter, which reads the path map
to classify files.  On a project with no path map, nothing is classified as
indexable and the lexical index must not be built.  The rebuild must still
return the envelope with exit 0, name the outcome, and give the record
store its own outcome.

W1-07's rule (DEC-185): a missing path map is not an error; every command
returns the envelope.

An owner that raises unexpectedly (for example a store file that is not a
database) must give an error envelope with a code and a non-zero exit, never
a traceback and never a rebuild reported as complete.

Predecessor analysis
--------------------
Rounds 1-4 test rebuild only on projects with a valid path map.  No existing
case covers the missing-path-map scenario.  The bug (``KeyError`` in the
secrets filter when the path map is absent) is invisible from those tests.

Red reasons
-----------
- No-path-map cases: ``rebuild`` calls the lexical index's owner, which
  calls the secrets filter, which reads
  ``load_config(root)["path-map.yaml"]["namespaces"]`` and raises
  ``KeyError``; exit 1 with a traceback, no envelope.
- Owner-raises cases: ``rebuild`` does not wrap the store loader or the
  lexical refresh in a handler; an unexpected error crashes the command
  with a traceback, no envelope.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w1_27_support as support


# =========================================================================== #
# Fixtures for the no-path-map and owner-raises scenarios
# =========================================================================== #

@pytest.fixture()
def no_pm_project(cli, tmp_path):
    """A tiny project with no path-map.yaml.  Has a tracked file so rebuild
    exercises the indexer path."""
    project = support.make_rebuild_project_no_path_map(cli, tmp_path / "no_pm")
    py_file = project / "hello.py"
    py_file.write_text("x = 1\n", encoding="utf-8")
    support.commit_all(project, "add a tracked file")
    return project


@pytest.fixture()
def no_pm_gov(cli, no_pm_project, sandbox):
    """``no_pm_gov(*args)`` runs gov on the no-path-map project."""
    def _gov(*args, cwd=None):
        return support.run_gov_with_code(cli, no_pm_project, sandbox, *args, cwd=cwd)
    return _gov


# =========================================================================== #
# No path map: the envelope, the outcome, the digest
# =========================================================================== #

def test_rebuild_no_path_map_returns_envelope(no_pm_gov, interface):
    """On a project with no path map, ``gov rebuild --json`` returns the
    API-0002 envelope with exit 0.

    W1-07 rule: a missing path map is not an error.
    DEC-440: rebuild returns the envelope.

    Currently fails: ``rebuild`` crashes with a ``KeyError`` traceback
    and exit 1; no envelope is printed.
    """
    run = no_pm_gov("rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert envelope["ok"] is True, (
        f"rebuild on a project with no path map is not ok\n{run.describe()}"
    )
    assert run.returncode == 0, (
        f"rebuild on a project with no path map exits {run.returncode}\n"
        f"{run.describe()}"
    )


def test_rebuild_no_path_map_lexical_not_built(no_pm_gov, interface):
    """The result names the lexical index as not built, with a reason that
    mentions the path map or the absence of indexable content.

    DEC-440: the result names the outcome of each store.

    Currently fails: traceback, no envelope.
    """
    run = no_pm_gov("rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    result = envelope.get("result") or {}
    stores = result.get("stores") or result.get("derived_stores") or {}
    lexical = stores.get("lexical") or {}

    assert lexical.get("status") != "recreated", (
        f"the lexical index should not be 'recreated' without a path map; "
        f"nothing is classified as indexable\nlexical: {lexical}\n{run.describe()}"
    )
    assert lexical.get("status") == "not_recreated", (
        f"the lexical index should be 'not_recreated' without a path map, "
        f"but got status={lexical.get('status')!r}\n"
        f"lexical: {lexical}\n{run.describe()}"
    )
    reason = str(lexical.get("reason", "")).lower()
    assert "path" in reason or "indexable" in reason or "classif" in reason, (
        f"the reason should mention the path map or indexable content, "
        f"but is: {lexical.get('reason')!r}\n{run.describe()}"
    )


def test_rebuild_no_path_map_no_traceback(no_pm_gov):
    """Rebuild on a project with no path map must never print a Python
    traceback on standard error.

    Currently fails: the ``KeyError`` in the secrets filter produces a
    full traceback.
    """
    run = no_pm_gov("rebuild", "--json")
    assert "Traceback" not in run.stderr, (
        f"rebuild printed a traceback on stderr:\n{run.stderr}"
    )


def test_rebuild_no_path_map_record_store_outcome(no_pm_gov, interface):
    """The record store has its own outcome: the result carries a digest
    from the store loader.

    DEC-440: the record store is independent of the path map.

    Currently fails: traceback, no envelope.
    """
    run = no_pm_gov("rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert run.returncode == 0, f"rebuild failed\n{run.describe()}"

    result = envelope.get("result") or {}
    digest = result.get("digest")
    assert isinstance(digest, str) and len(digest) > 0, (
        f"the result should carry a digest from the record store, "
        f"but got digest={digest!r}\nresult: {result}\n{run.describe()}"
    )


def test_rebuild_no_path_map_idempotent_digest(no_pm_gov, interface):
    """Two rebuilds on a project with no path map give the same digest.

    Currently fails: traceback, no envelope.
    """
    run1 = no_pm_gov("rebuild", "--json")
    env1 = support.assert_envelope(run1, interface, command="rebuild")
    assert run1.returncode == 0, f"first rebuild failed\n{run1.describe()}"
    digest1 = (env1.get("result") or {}).get("digest")

    run2 = no_pm_gov("rebuild", "--json")
    env2 = support.assert_envelope(run2, interface, command="rebuild")
    assert run2.returncode == 0, f"second rebuild failed\n{run2.describe()}"
    digest2 = (env2.get("result") or {}).get("digest")

    assert digest1 is not None and digest2 is not None, (
        f"rebuild has no digest\nrun 1 result: {env1.get('result')}\n"
        f"run 2 result: {env2.get('result')}"
    )
    assert digest1 == digest2, (
        f"two rebuilds on a project with no path map give different digests: "
        f"{digest1} vs {digest2}\n"
        f"run 1:\n{run1.describe()}\nrun 2:\n{run2.describe()}"
    )


def test_rebuild_no_path_map_writes_only_act_paths(no_pm_gov, no_pm_project, sandbox, interface):
    """Rebuild on a project with no path map writes nothing outside
    ``.gov-runtime/``."""
    before_tree = support.snapshot(no_pm_project)
    before_home = support.snapshot(sandbox.home, skip=())
    before_elsewhere = support.snapshot(sandbox.elsewhere, skip=())

    run = no_pm_gov("rebuild", "--json")
    assert run.returncode in interface.exit_codes, run.describe()

    changed = support.snapshot_difference(before_tree, support.snapshot(no_pm_project))
    assert not changed, (
        f"rebuild on a project with no path map wrote outside "
        f".gov-runtime: {changed}\n{run.describe()}"
    )
    changed = support.snapshot_difference(before_home, support.snapshot(sandbox.home, skip=()))
    assert not changed, (
        f"rebuild wrote outside the project (home): {changed}\n{run.describe()}"
    )
    changed = support.snapshot_difference(before_elsewhere, support.snapshot(sandbox.elsewhere, skip=()))
    assert not changed, (
        f"rebuild wrote outside the project (elsewhere): {changed}\n{run.describe()}"
    )


# =========================================================================== #
# An owner that raises unexpectedly
# =========================================================================== #

@pytest.fixture()
def corrupt_store_project(cli, tmp_path):
    """A project with a valid path map but a pre-existing ``.gov-runtime/store.db``
    that is not a SQLite database.  When rebuild's store loader opens it,
    the first SQL operation raises ``DatabaseError``."""
    project = support.make_rebuild_project(cli, tmp_path / "corrupt")
    store_dir = project / ".gov-runtime"
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / "store.db").write_text(
        "this file is not a SQLite database\n", encoding="utf-8",
    )
    return project


@pytest.fixture()
def corrupt_gov(cli, corrupt_store_project, sandbox):
    def _gov(*args, cwd=None):
        return support.run_gov_with_code(
            cli, corrupt_store_project, sandbox, *args, cwd=cwd,
        )
    return _gov


def test_rebuild_owner_raises_gives_error_envelope(corrupt_gov, interface):
    """When an owner raises unexpectedly (a store file that is not a database),
    rebuild returns an error envelope with a code and a non-zero exit.

    Currently fails: the unhandled ``DatabaseError`` produces a traceback
    and no envelope.
    """
    run = corrupt_gov("rebuild", "--json")
    envelope = support.assert_envelope(run, interface, command="rebuild")
    assert envelope["ok"] is False, (
        f"rebuild should not be ok when an owner raises\n{run.describe()}"
    )
    assert run.returncode != 0, (
        f"rebuild should exit non-zero when an owner raises\n{run.describe()}"
    )
    error = envelope.get("error") or {}
    assert isinstance(error.get("code"), str) and error["code"], (
        f"the error envelope should carry a code\nerror: {error}\n{run.describe()}"
    )


def test_rebuild_owner_raises_no_traceback(corrupt_gov):
    """Rebuild must never print a Python traceback when an owner raises."""
    run = corrupt_gov("rebuild", "--json")
    assert "Traceback" not in run.stderr, (
        f"rebuild printed a traceback on stderr:\n{run.stderr}"
    )


def test_rebuild_owner_raises_not_complete(corrupt_gov, interface):
    """A rebuild that hit an owner error is never reported as complete
    (``ok: true``)."""
    run = corrupt_gov("rebuild", "--json")
    try:
        envelope = run.envelope()
    except AssertionError:
        return
    assert envelope.get("ok") is not True, (
        f"rebuild reported ok=true despite an owner error\n{run.describe()}"
    )


def test_rebuild_owner_raises_writes_only_act_paths(corrupt_gov, corrupt_store_project, sandbox, interface):
    """Rebuild with a corrupt store writes nothing outside ``.gov-runtime/``."""
    before_tree = support.snapshot(corrupt_store_project)
    before_home = support.snapshot(sandbox.home, skip=())
    before_elsewhere = support.snapshot(sandbox.elsewhere, skip=())

    run = corrupt_gov("rebuild", "--json")
    assert run.returncode in interface.exit_codes, run.describe()

    changed = support.snapshot_difference(before_tree, support.snapshot(corrupt_store_project))
    assert not changed, (
        f"rebuild with a corrupt store wrote outside .gov-runtime: "
        f"{changed}\n{run.describe()}"
    )
    changed = support.snapshot_difference(before_home, support.snapshot(sandbox.home, skip=()))
    assert not changed, (
        f"rebuild wrote outside the project (home): {changed}\n{run.describe()}"
    )
    changed = support.snapshot_difference(before_elsewhere, support.snapshot(sandbox.elsewhere, skip=()))
    assert not changed, (
        f"rebuild wrote outside the project (elsewhere): {changed}\n{run.describe()}"
    )
