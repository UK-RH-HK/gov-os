"""S2 and S3 through the batch's route: ``python3 -m gov.close.batch run <ticket>`` reaches the nightly (its full
regression is ``gov.close.nightly.night``), so W2-68's batch is switched on only after this fix (DEC-939 item 5,
P-W2-68-PRUNE (b), DEC-803).

The project is W2-68's (``w2_68_support.Project``, imported, never copied): ticket A with its work and its checkpoint
committed. As in W2-68's reviewer's F1, a second worktree of the project's repository, holding a staged change, has
its folder moved aside for the whole batch, then put back: it keeps its registration, its administrative folder and
its staged index. A second batch, whose full regression locks the clone it runs in (a probe planted in a suite no
ticket of the batch owns), carries the failed removal in the batch's record (the night's ``cleanup`` key).

Red reasons on the base (README): the night's repo-wide ``git worktree prune`` drops the hidden worktree; the batch's
record has no ``cleanup`` key.
"""

import sys
from pathlib import Path

_W2_68 = str(Path(__file__).resolve().parents[1] / "W2-68")
if _W2_68 not in sys.path:
    sys.path.insert(0, _W2_68)

import w2_68_support as batch_support  # noqa: E402

import w2_77_support as support  # noqa: E402

STAGED = {"staged-change.txt": "a change staged in the second worktree, not committed\n"}
PROBE_REL = "tests/acceptance/W2-zz/test_zz_w2_77_probe.py"


def _ready_project(base, plant=None):
    sandbox = batch_support.make_sandbox(base)
    env = batch_support.env_without_endpoint(sandbox)
    project = batch_support.Project(base / "project", base / "told")
    if plant:
        project.based(plant, "a probe in a suite no ticket of the batch owns")
    project.work({batch_support.WIDGET: "# the widget, changed\n"}, ticket=batch_support.A)
    project.ready(sandbox, ticket=batch_support.A)
    return project, env


def test_the_batch_keeps_a_hidden_worktree_s_registration_admin_folder_and_staged_index(tmp_path):
    project, env = _ready_project(tmp_path)
    second = support.add_worktree(project.root, tmp_path / "second", staged=STAGED)
    support.assert_kept(project, second, "before the batch (the fixture)")
    with support.moved_aside(second.path):
        answer = batch_support.batch(project, env, batch_support.A)
    records = batch_support.batch_records(project)
    assert records, f"the fixture: the batch wrote no run record, so it did not reach the nightly\n{answer.describe()}"
    support.assert_kept(project, second, "the second worktree, moved aside while the batch ran")


def test_the_batch_s_record_carries_the_night_s_cleanup_when_the_clone_s_removal_fails(tmp_path):
    told_clone = tmp_path / "probe" / "clone"
    told_clone.parent.mkdir(parents=True)
    project, env = _ready_project(tmp_path, plant={PROBE_REL: support.probe_test(told_clone, lock=True)})
    answer = batch_support.batch(project, env, batch_support.A)
    rel, record, _ = batch_support.the_batch_record(project)
    assert told_clone.is_file(), f"the fixture: the batch's regression did not run the probe\n{answer.describe()}"
    clone = Path(told_clone.read_text(encoding="utf-8").splitlines()[0].split("\t")[0])
    cleanup = record.get(support.CLEANUP_KEY)
    assert isinstance(cleanup, dict) and cleanup.get("ok") is False, \
        (f"the clone's removal failed (its worktree was locked) and the batch's record {rel} does not carry the "
         f"night's {support.CLEANUP_KEY!r} key (record keys: {sorted(record)})")
    assert isinstance(cleanup.get("clone"), str) and support.same_path(cleanup["clone"], clone), \
        f"the batch record's cleanup does not name the clone {clone}: {cleanup}"
