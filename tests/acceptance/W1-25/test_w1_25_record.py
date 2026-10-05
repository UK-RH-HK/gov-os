"""W1-25 -- the checkpoint record: where it is, what it conforms to, its inputs with their hashes.

- KPI success 1 [CAP-13.b, CAP-37.a]: "A checkpoint conforming to the carried
  schema is written ...".
- KPI failure 2: "A checkpoint references an input by id without its hash".

Recommended option of DP-2 (the schema, the frontmatter keys and the command's
arguments). Another answer to DP-2 changes this file and ``w1_25_support.py``.
The location assertions rest on the sources alone (DP-3 leaves only the
directory open, and no test names a directory): CAP-37.a "in the repository",
CAP-20.a (a fresh clone has the latest checkpoint, so git must be able to track
it) and DEC-176 (``.gov-runtime/`` outside ``scratch/`` is closed).
"""

from __future__ import annotations

import pytest

import w1_25_support as support

cli_support = support.cli_support


def test_a_checkpoint_is_a_file_git_can_track(project, checkpoint):
    """[CAP-37.a] "in the repository": inside the project, outside ``.gov-runtime/``, not ignored by git."""
    path = checkpoint(commit=False)
    rel = path.relative_to(project).as_posix()
    assert path.resolve().is_relative_to(project.resolve()), f"{rel} is outside the project"
    assert not rel.startswith(".gov-runtime/"), f"the checkpoint is derived state under .gov-runtime/: {rel}"
    status = cli_support.git(project, "status", "--porcelain", "--untracked-files=all")
    assert rel in status, f"git does not see the new checkpoint {rel} (is it ignored?):\n{status}"


def test_writing_a_checkpoint_changes_nothing_else(project, gov, interface):
    """An act command writes its record and nothing else in the tracked tree; it makes no commit."""
    before_files, _, before_git = support.state(project)
    result = support.succeeded(gov(*support.write_args()), interface)
    path = support.checkpoint_path(project, result)
    after_files, _, after_git = support.state(project)
    difference = cli_support.snapshot_difference(before_files, after_files)
    changed = [line for line in difference if not line.startswith("created: ")]
    created = [rel for rel in (line.split(": ", 1)[1] for line in difference if line.startswith("created: "))
               if after_files[rel] != "dir"]
    assert not changed, f"gov checkpoint changed or deleted existing files: {changed}"
    assert created == [path.relative_to(project).as_posix()], f"gov checkpoint created {created}"
    assert after_git == before_git, "gov checkpoint moved HEAD or a ref"


def test_the_checkpoint_conforms_to_the_kernel_schema(project, checkpoint, tmp_path):
    """KPI success 1: W1-08's ``checkpoint.schema.json`` (shared frontmatter, ``type: checkpoint``, the id grammar)."""
    document = support.frontmatter(checkpoint(inputs=(support.INPUT_REL,)))
    support.validate(project, document, tmp_path)
    assert document["type"] == "checkpoint"


def test_the_checkpoint_records_the_ticket_the_trigger_and_the_next_step(checkpoint):
    """[CAP-37.a] a structured checkpoint: the fields are frontmatter keys, not prose."""
    document = support.frontmatter(checkpoint(trigger="stop"))
    assert document.get(support.KEY_TICKET) == support.TICKET, document
    assert document.get(support.KEY_TRIGGER) == "stop", document
    assert document.get(support.KEY_NEXT) == support.NEXT_STEP, document
    assert document.get(support.KEY_CREATED), f"the checkpoint has no '{support.KEY_CREATED}' time: {document}"


def test_the_ticket_is_an_input_with_its_id_version_and_hash(project, checkpoint):
    """[CAP-37.a] "input ids/versions/hashes": the ticket file is always an input."""
    inputs = support.inputs_of(support.frontmatter(checkpoint()))
    digest = support.sha256(support.ticket_path(project))
    found = [item for item in inputs if digest in str(item.get("hash", ""))]
    assert found, f"no input carries the sha256 of the ticket file ({digest}): {inputs}"
    assert found[0].get("id") == support.TICKET, f"the ticket input's id is not the ticket's id: {found[0]}"


def test_a_named_input_is_recorded_with_its_hash(project, checkpoint):
    inputs = support.inputs_of(support.frontmatter(checkpoint(inputs=(support.INPUT_REL,))))
    digest = support.sha256(project / support.INPUT_REL)
    assert [item for item in inputs if digest in str(item.get("hash", ""))], \
        f"no input carries the sha256 of {support.INPUT_REL} ({digest}): {inputs}"


def test_every_input_has_an_id_a_version_and_a_hash(checkpoint):
    """KPI failure 2, on what the command writes: no input is named by id alone."""
    for item in support.inputs_of(support.frontmatter(checkpoint(inputs=(support.INPUT_REL,)))):
        for key in ("id", "version", "hash"):
            assert str(item.get(key) or "").strip(), f"an input lacks its {key}: {item}"


def test_an_input_that_cannot_be_hashed_is_refused_and_nothing_is_written(project, gov, interface):
    """KPI failure 2: an input that is not a file of the project has no hash; no checkpoint names it."""
    before = support.state(project)
    run = gov(*support.write_args(inputs=("docs/w1-25-no-such-input.md",)))
    support.refused(run, interface)
    assert support.state(project) == before, f"a checkpoint was written without its input's hash\n{run.describe()}"


@pytest.mark.parametrize("missing", ("--next", "--ticket", "--trigger"))
def test_a_checkpoint_without_its_ticket_trigger_or_next_step_is_refused(project, gov, interface, missing):
    """A governance error (exit code 1), not a usage error: W1-07 holds ``gov checkpoint`` to the envelope."""
    args = list(support.write_args())
    at = args.index(missing)
    del args[at:at + 2]
    before = support.state(project)
    run = gov(*args)
    support.refused(run, interface)
    assert support.state(project) == before, f"a checkpoint was written without {missing}\n{run.describe()}"


def test_a_checkpoint_for_an_unknown_ticket_is_refused(project, gov, interface):
    before = support.state(project)
    run = gov(*support.write_args(ticket="DAEO-zq99"))
    support.refused(run, interface)
    assert support.state(project) == before, run.describe()


def test_an_earlier_checkpoint_is_kept_when_a_later_one_is_written(checkpoint):
    """[CAP-13.b] episodic memory: each checkpoint is its own record, with its own id."""
    first = checkpoint(next_step="first step")
    second = checkpoint(next_step="second step")
    assert first != second and first.is_file() and second.is_file(), "the later checkpoint replaced the earlier one"
    assert support.frontmatter(first)["id"] != support.frontmatter(second)["id"]
    assert support.frontmatter(first)[support.KEY_NEXT] == "first step"


def test_checkpoints_are_kept_per_ticket(checkpoint):
    """[CAP-13.b] "per ticket": each record names its own ticket."""
    mine = checkpoint(ticket=support.TICKET)
    other = checkpoint(ticket=support.OTHER_TICKET)
    assert support.frontmatter(mine)[support.KEY_TICKET] == support.TICKET
    assert support.frontmatter(other)[support.KEY_TICKET] == support.OTHER_TICKET
