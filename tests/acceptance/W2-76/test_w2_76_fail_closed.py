"""KPI success 4 (fail closed, DEC-866): a lock that cannot be created or taken is never ignored.

A lock that cannot be opened or created (its folder is missing, or cannot be written and the file is absent) refuses
the rebuild at once with ``REBUILD_FAILED``, naming the lock's path and the reason, and nothing is built: no store is
created or changed. An invalid ``governance/project/rebuild.yaml`` is refused the same way, naming the file and the
key (DEC-939 item 2, row W2-M408).
"""

from __future__ import annotations

import os

import pytest

import w2_76_support as support

pytestmark = support.needs_tools

# A refusal comes "at once": well before a rebuild of the tiny project would end on a loaded machine.
REFUSAL_BOUND_S = 30.0


def _assert_refused(run, *named):
    code, text = support.error_text(run)
    assert run.returncode not in (0, None) and run.envelope().get("ok") is False and code == "REBUILD_FAILED", \
        f"the rebuild was not refused with REBUILD_FAILED\n{run.describe()}"
    for name in named:
        assert name in text, f"the refusal does not name {name!r}: {text}"
    assert run.seconds < REFUSAL_BOUND_S, f"the refusal took {run.seconds:.1f} s: it waited or built first"


def _assert_nothing_built(project):
    assert support.store_snapshot(project) == {}, \
        f"the refused rebuild created stores: {sorted(support.store_snapshot(project))}"


def test_a_lock_whose_folder_is_missing_refuses_and_builds_nothing(box, env):
    lock = box.base / "no-such-folder" / "rebuild.lock"
    project = support.make_project(box, "project", lock)

    run = support.rebuild(project, env, "--no-embeddings")

    _assert_refused(run, str(lock))
    _assert_nothing_built(project)
    assert not lock.parent.exists(), "the rebuild made the lock's missing folder instead of refusing"


@pytest.mark.skipif(os.geteuid() == 0, reason="root writes into a folder of mode 0555")
def test_a_lock_in_an_unwritable_folder_refuses_and_builds_nothing(box, env):
    folder = box.base / "read-only-locks"
    folder.mkdir()
    lock = folder / "rebuild.lock"
    project = support.make_project(box, "project", lock)
    folder.chmod(0o555)
    try:
        run = support.rebuild(project, env, "--no-embeddings")
    finally:
        folder.chmod(0o755)

    _assert_refused(run, str(lock))
    _assert_nothing_built(project)
    assert not lock.exists()


def test_a_refused_rebuild_leaves_the_existing_stores_unchanged(box, lock, env):
    project = support.make_project(box, "project", lock)
    built = support.rebuild(project, env, "--no-embeddings")
    assert built.returncode == 0, built.describe()
    before = support.store_snapshot(project)
    assert before, "the first rebuild built no store to compare"
    bad = box.base / "gone" / "rebuild.lock"
    support.set_settings(project, support.settings_text(bad))

    run = support.rebuild(project, env, "--no-embeddings")

    _assert_refused(run, str(bad))
    assert support.store_snapshot(project) == before, "a refused rebuild changed the stores"


INVALID_SETTINGS = {
    "not-yaml": ("slow_after_s: [2\nlock: {unclosed\n", ()),
    "not-a-map": ("- slow_after_s\n- lock\n", ()),
    "threshold-zero": ("slow_after_s: 0\nlock: {lock}\n", ("slow_after_s",)),
    "threshold-not-a-number": ("slow_after_s: soon\nlock: {lock}\n", ("slow_after_s",)),
    "lock-relative": ("slow_after_s: 600\nlock: locks/rebuild.lock\n", ("lock",)),
    "lock-empty": ("slow_after_s: 600\nlock: ''\n", ("lock",)),
}


@pytest.mark.parametrize("case", sorted(INVALID_SETTINGS))
def test_an_invalid_rebuild_yaml_refuses_and_builds_nothing(box, lock, env, case):
    template, keys = INVALID_SETTINGS[case]
    text = template.replace("{lock}", '"' + str(lock) + '"') if "{lock}" in template else template
    project = support.make_project(box, "project", lock, settings=text)

    run = support.rebuild(project, env, "--no-embeddings", timeout=60)

    _assert_refused(run, "rebuild.yaml", *keys)
    _assert_nothing_built(project)
