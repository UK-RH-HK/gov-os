"""KPI S6, F1 and F2: the kept register is rebuilt from the archive, and a register that lost or changed a kept
entry is named (EMERGENCY-2 11.3, DEC-1214 G4 (a)).

The builder, ``docs/emergency-2/audits/08-new-register.py`` of this tree, runs as a child process: on this tree
(nothing is written here: ``--out`` names a temporary file) and on a planted project with seven archive entries.
"""

from __future__ import annotations

import re

import pytest

import w2_203_support as s

MISSING, DIFFERS = "REGISTER_KEPT_MISSING", "REGISTER_ENTRY_DIFFERS"
APPENDED = "DEC-1217"  # the next id after the last of the base register
FAR, AFTER_THE_MOVE = "DEC-1299", "DEC-1300"


def _run(home, *argv: str):
    script = s.REPO / s.BUILDER_REL
    assert script.is_file(), f"{s.BUILDER_REL} is not a file of this tree"
    return s.child(s.src(), home, home / "builder", str(script), *argv)


def _lines(done) -> list[str]:
    """The failure lines of a ``--check``, wherever they were printed."""
    return [" ".join(line.split()[:2]) for line in (done.stdout + "\n" + done.stderr).splitlines()
            if re.match(rf"\s*({MISSING}|{DIFFERS})\b", line)]


def _ok(done) -> None:
    assert done.returncode == 0 and not _lines(done), f"exit {done.returncode}: {done.stdout[-600:]} {done.stderr[-600:]}"
    last = [line for line in done.stdout.splitlines() if line.strip()][-1:]
    assert last and last[0].startswith("ok"), f"the summary line: {last}"


def _late(record_id: str, word: str) -> str:
    return (f"### {record_id} — The {word} decision\n- **Status:** ACCEPTED (owner, 2026-11-19)\n"
            f"- **Decision:** the {word} is settled.\n- **Why:** it was asked.")


@pytest.fixture
def project(plant):
    return plant("builder", index=False, load=False).root


@pytest.fixture
def built(project, home, tmp_path):
    """The planted project's kept register as the builder writes it from the planted archive: ``(root, text)``."""
    out = tmp_path / "built.md"
    done = _run(home, "--root", str(project), "--out", str(out))
    assert done.returncode == 0 and out.is_file(), f"exit {done.returncode}: {done.stderr[-800:]}"
    return project, out.read_text(encoding="utf-8")


# ---------------------------------------------------------------- S6

def test_s6_rebuilding_from_the_archive_gives_the_committed_register_byte_for_byte(home, tmp_path):
    out = tmp_path / "rebuilt.md"
    done = _run(home, "--out", str(out))
    assert done.returncode == 0 and out.is_file(), f"exit {done.returncode}: {done.stderr[-800:]}"
    assert out.read_bytes() == (s.REPO / s.REGISTER_REL).read_bytes(), \
        f"the register rebuilt from the archive is not the committed {s.REGISTER_REL}"


def test_s6_the_archive_is_read_from_the_path_maps_key_and_the_kept_and_late_entries_are_written(built):
    _, text = built
    assert s.entries(text) == [(record_id, s.ENTRY[record_id]) for record_id in s.KEPT_IDS], \
        "the kept entries (one with its class on the status line's second line) and the late ones, verbatim, in order"
    assert not text.startswith(s.ARCHIVE_FIRST_LINE) and text.startswith("# "), "under a head of its own"


def test_s6_an_entry_appended_to_the_archive_is_in_the_output_whatever_its_id(project, home, tmp_path):
    for number, record_id in enumerate((APPENDED, FAR)):
        entry = _late(record_id, "wintergreen")
        archive, out = tmp_path / f"archive-{number}.md", tmp_path / f"out-{number}.md"
        archive.write_text(s.archive_text() + "\n" + entry + "\n", encoding="utf-8")
        done = _run(home, "--root", str(project), "--archive", str(archive), "--out", str(out))
        assert done.returncode == 0, done.stderr[-800:]
        assert s.entries(out.read_text(encoding="utf-8")) == \
            [(kept_id, s.ENTRY[kept_id]) for kept_id in s.KEPT_IDS] + [(record_id, entry)]


def test_s6_real_a_late_entry_appended_to_this_archive_is_in_the_output_and_the_rest_is_unchanged(home, tmp_path):
    committed = s.entries((s.REPO / s.REGISTER_REL).read_text(encoding="utf-8"))
    archive_file = s.REPO / s.ARCHIVE_REL
    assert archive_file.is_file(), f"{s.ARCHIVE_REL} is not a file of this tree"
    last = max(s.number_of(record_id) for record_id, _ in committed)
    entry = _late(f"DEC-{last + 1}", "wintergreen")
    archive, out = tmp_path / "archive.md", tmp_path / "out.md"
    archive.write_text(archive_file.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + entry + "\n", encoding="utf-8")
    done = _run(home, "--archive", str(archive), "--out", str(out))
    assert done.returncode == 0, done.stderr[-800:]
    written = out.read_text(encoding="utf-8")
    assert entry in written, "the appended entry is not in the output verbatim"
    assert s.entries(written) == committed + [(f"DEC-{last + 1}", entry)], "the existing entries changed"


# ---------------------------------------------------------------- F1

def test_f1_real_the_committed_register_and_archive_check_clean(home):
    _ok(_run(home, "--check"))


@pytest.mark.parametrize("lost", [s.K_SECOND, s.K_LATER])
def test_f1_a_register_that_lacks_a_kept_or_late_entry_is_named(built, home, tmp_path, lost):
    root, text = built
    register = tmp_path / "register.md"
    register.write_text(text, encoding="utf-8")
    _ok(_run(home, "--root", str(root), "--register", str(register), "--check"))
    register.write_text(s.without_entry(text, lost), encoding="utf-8")
    done = _run(home, "--root", str(root), "--register", str(register), "--check")
    assert _lines(done) == [f"{MISSING} {lost}"] and done.returncode == 1, \
        f"exit {done.returncode}: {done.stdout[-600:]} {done.stderr[-600:]}"


def test_f1_the_check_reads_the_projects_own_register_by_default(built, home):
    root, text = built
    s.write(root, s.REGISTER_REL, s.without_entry(s.without_entry(text, s.K_FIRST), s.K_LATE))
    done = _run(home, "--root", str(root), "--check")
    assert sorted(_lines(done)) == sorted(f"{MISSING} {lost}" for lost in (s.K_FIRST, s.K_LATE))
    assert done.returncode == 1


def test_f1_a_decision_made_after_the_move_is_no_failure(built, home, tmp_path):
    root, text = built
    register = tmp_path / "register.md"
    register.write_text(text.rstrip("\n") + "\n\n" + _late(AFTER_THE_MOVE, "foxglove") + "\n", encoding="utf-8")
    _ok(_run(home, "--root", str(root), "--register", str(register), "--check"))


# ---------------------------------------------------------------- F2

@pytest.mark.parametrize("changed", [s.K_FIRST, s.K_LATE])
def test_f2_an_entry_whose_text_differs_by_one_character_is_named(built, home, tmp_path, changed):
    root, text = built
    last = s.ENTRY[changed].split("\n")[-1]
    assert text.count(last) == 1, "premise: the entry's last line stands once in the built register"
    register = tmp_path / "register.md"
    register.write_text(text.replace(last, last[:-2] + "x" + last[-1]), encoding="utf-8")
    done = _run(home, "--root", str(root), "--register", str(register), "--check")
    assert _lines(done) == [f"{DIFFERS} {changed}"] and done.returncode == 1, \
        f"exit {done.returncode}: {done.stdout[-600:]} {done.stderr[-600:]}"
