"""W2-93's acceptance tests for ``--sets-root``: S3 (the hidden half is found only under the hidden folder, and no
question or answer reaches an output, a log or a commit message) and S6 (the runner and the validator each find and read
the stand-in given only ``--sets-root``; a root without a hidden folder exits non-zero naming it).

Planted stand-ins only, in the cases' own temporary folders. Red today: the validator is absent and the runner does not
know ``--sets-root`` at the base.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest
import w2_93_standin as s

HIDDEN = "fixtures/evaluation/adoption-proving-ground/hidden"
VALIDATOR_NO_HIDDEN = f"refused: no hidden half under the sets root: {HIDDEN}"
RUNNER_NO_HIDDEN = f"refused: --sets-root holds no hidden half: {HIDDEN}"


def _move_half(valid, base, where):
    """A sets root with the stand-in's files at ``where`` (a path under the root) and no ``hidden/`` folder."""
    root = Path(base) / "sets-root"
    target = root / where
    target.mkdir(parents=True)
    for path in s.hidden_of(valid.root).iterdir():
        (target / path.name).write_bytes(path.read_bytes())
    return root


MISPLACED = {
    "beside-hidden": "fixtures/evaluation/adoption-proving-ground",
    "at-the-root-hidden": "hidden",
    "under-another-set": "fixtures/evaluation/another-set/hidden",
    "named-visible": "fixtures/evaluation/adoption-proving-ground/visible",
}


# --------------------------------------------------------------------------
# S3: the hidden files are found only under the hidden folder; nothing hidden leaks
# --------------------------------------------------------------------------

@pytest.mark.parametrize("where", list(MISPLACED), ids=list(MISPLACED))
def test_s3_a_stand_in_placed_elsewhere_under_the_root_is_not_found(tmp_path, valid, where):
    """S3: the stand-in beside `hidden/`, at `<root>/hidden/`, under another set or named visible, with no `hidden/`
    folder of the set: not found: exit 2 and the missing-folder line, nothing built."""
    root = _move_half(valid, tmp_path, MISPLACED[where])
    run = s.validate(root, tmp_path)
    assert run.code == 2, run.out[:300]
    assert VALIDATOR_NO_HIDDEN in run.lines, run.out[:300]
    assert "Traceback" not in run.out and s.WORD not in run.out and s.VWORD not in run.out
    assert not any(line.startswith("valid:") for line in run.lines)
    assert not list(run.tmpdir.iterdir()), "a built copy was made for a half that was not found"


def test_s3_a_hidden_path_that_is_a_file_is_not_a_folder_and_is_not_found(tmp_path):
    """S3: `hidden` present but not a folder: the same refusal."""
    root = tmp_path / "sets-root"
    (root / HIDDEN).parent.mkdir(parents=True)
    (root / HIDDEN).write_text(f"{s.WORD}\n", encoding="utf-8")
    run = s.validate(root, tmp_path)
    assert run.code == 2 and VALIDATOR_NO_HIDDEN in run.lines, run.out[:300]
    assert s.WORD not in run.out


def test_s3_the_planted_words_are_in_no_output_of_a_valid_run_and_nothing_is_written_beside_it(valid):
    """S3: on the valid stand-in the question word and the variant word are in neither stream, and the validator wrote
    nothing in the sets root, this repository or its TMPDIR (the built copy is removed)."""
    assert valid.run.code == 0, valid.run.out[:300]
    assert s.WORD not in valid.run.out and s.VWORD not in valid.run.out
    assert valid.root_after == valid.root_before, "the validator changed the sets root"
    assert valid.repo_after == valid.repo_before, "the validator changed this repository"
    assert not list(valid.run.tmpdir.iterdir()), "the validator left its built copy in TMPDIR"


def test_s3_no_commit_message_since_the_base_and_no_ticket_note_holds_the_planted_words():
    """S3: `git log --format=%B a7b36bcfd98a..HEAD` and the ticket file hold the planted question word 0 times (and the
    variant word, likewise)."""
    done = subprocess.run(["git", "-C", str(s.REPO_ROOT), "log", "--format=%B", f"{s.BASE_COMMIT}..HEAD"],
                          capture_output=True, text=True)
    assert done.returncode == 0, "git log failed"
    assert done.stdout.count(s.WORD) == 0 and done.stdout.count(s.VWORD) == 0, "a commit message holds a planted word"
    tickets = [p for p in s.TICKET_FILES if p.is_file()]
    assert tickets, "the ticket file DAEO-6y0x.md was not found to read"
    for ticket in tickets:
        text = ticket.read_text(encoding="utf-8")
        assert s.WORD not in text and s.VWORD not in text, f"{ticket.name} holds a planted word"


# --------------------------------------------------------------------------
# S6: the runner and the validator, each given only --sets-root
# --------------------------------------------------------------------------

def test_s6_the_validator_given_only_sets_root_finds_and_reads_the_stand_in(tmp_path, valid):
    """S6: the validator, given only `--sets-root`, finds and reads the stand-in: exit 0 and 60 questions, 13 variants."""
    run = s.validate(valid.root, tmp_path)
    assert run.code == 0, run.out[:400]
    assert re.search(rf"^valid: 60 hidden questions in 6 repositories, {s.VARIANT_COUNT} hidden variants \(seed \d+\)$",
                     run.out, re.M), run.out[-300:]


def test_s6_the_runner_given_only_sets_root_finds_and_reads_the_stand_in(tmp_path, valid):
    """S6: the runner (`--mode build --folder <tmp> --sets-root <root> --large-size 4096`) finds and reads the stand-in:
    its build records the stand-in's variant count, and the planted words are in none of its output or run files
    (the built repositories and manifests hold the variants' own files by design, so only the run's own files are read)."""
    run = s.runner_build(valid.root, tmp_path)
    assert run.code == 0, run.out[:400]
    assert re.search(r"^BUILT \(seed \d+\)$", run.out, re.M), run.out[:300]
    record = json.loads((run.folder / "run.json").read_text(encoding="utf-8"))
    assert record["hidden_variants"] == s.VARIANT_COUNT, "the build did not read the stand-in's variants"
    hidden = {}
    for name in s.REPOS:
        manifest = json.loads((run.folder / "manifests" / f"{name}.json").read_text(encoding="utf-8"))
        hidden[name] = sorted(e["kind"] for e in manifest["planted"] if e.get("hidden"))
    assert {name: kinds for name, kinds in hidden.items() if kinds} == {
        name: sorted(kinds) for name, kinds in s.PLAN.items()}, "the manifests do not hold the stand-in's variants"
    for rel, text in s.texts_under(run.folder, skip=("repos", "manifests")):
        assert s.WORD not in text and s.VWORD not in text, f"a planted word is in the run's own file {rel}"
    assert s.WORD not in run.out and s.VWORD not in run.out
    for rel, text in s.texts_under(run.folder, skip=("repos",)):
        assert s.WORD not in text, f"a stand-in question or answer is in {rel}"


def test_s6_the_runner_and_the_validator_find_the_same_variants(tmp_path, valid):
    """S6: the one hidden folder serves both: the validator's total of variants is the build's record."""
    built = s.runner_build(valid.root, tmp_path / "a")
    checked = s.validate(valid.root, tmp_path / "b")
    assert built.code == 0 and checked.code == 0, (built.out[:200], checked.out[:200])
    record = json.loads((built.folder / "run.json").read_text(encoding="utf-8"))
    found = re.search(r"hidden variants \(seed", checked.out)
    assert found and f"{record['hidden_variants']} hidden variants (seed" in checked.out


def test_s6_a_root_without_the_hidden_folder_is_refused_by_the_validator_naming_it(tmp_path):
    """S6: a root without the hidden folder: the validator exits non-zero naming it."""
    root = tmp_path / "empty-root"
    root.mkdir()
    run = s.validate(root, tmp_path)
    assert run.code == 2 and VALIDATOR_NO_HIDDEN in run.lines, run.out[:300]
    assert "Traceback" not in run.out


@pytest.mark.parametrize("mode", ["build", "run", "read"])
def test_s6_a_root_without_the_hidden_folder_is_refused_by_the_runner_naming_it_before_anything_is_built(
        tmp_path, mode):
    """S6: a root without the hidden folder: the runner exits 2 naming `fixtures/evaluation/adoption-proving-ground/
    hidden`, in every mode, before anything is built (the run folder is never made)."""
    root = tmp_path / "empty-root"
    root.mkdir()
    folder = tmp_path / "run"
    run = s.run_script(s.RUNNER, ["--mode", mode, "--folder", folder, "--sets-root", root, "--large-size", s.LARGE],
                       tmp_path)
    assert run.code == 2, run.out[:300]
    assert RUNNER_NO_HIDDEN in run.lines, run.out[:300]
    assert "Traceback" not in run.out
    assert not folder.exists(), "something was built before the refusal"


def test_s6_sets_root_and_hidden_together_are_refused_by_the_runner(tmp_path, valid):
    """S6 (interface item 8): `--sets-root` and `--hidden` together: refused, exit 2, nothing built."""
    folder = tmp_path / "run"
    run = s.run_script(s.RUNNER, ["--mode", "build", "--folder", folder, "--sets-root", valid.root, "--hidden",
                                  s.hidden_of(valid.root), "--large-size", s.LARGE], tmp_path)
    assert run.code == 2, run.out[:300]
    assert [line for line in run.lines if line.startswith("refused: ")], run.out[:300]
    assert "Traceback" not in run.out and not folder.exists()


def test_s6_hidden_stays_for_a_direct_call(tmp_path, valid):
    """S6: the runner's `--hidden <folder>` stays for a direct call: it reads the same stand-in and records its variants."""
    folder = tmp_path / "run"
    run = s.run_script(s.RUNNER, ["--mode", "build", "--folder", folder, "--hidden", s.hidden_of(valid.root),
                                  "--large-size", s.LARGE], tmp_path)
    assert run.code == 0, run.out[:400]
    record = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    assert record["hidden_variants"] == s.VARIANT_COUNT
