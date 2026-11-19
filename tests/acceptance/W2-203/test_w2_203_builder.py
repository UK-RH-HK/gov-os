"""KPI S6, F1 and F2: the kept register is rebuilt from the archive, and a register that lost or changed a kept
entry is named (EMERGENCY-2 11.3, DEC-1214 G4 (a)).

The builder, ``docs/emergency-2/audits/08-new-register.py`` of this tree, runs as a child process: on this tree
(nothing is written here: ``--out`` names a temporary file) and on a planted project with seven archive entries.

S6, F1 and F2 as the CTO amended them (2026-11-19): the register in force is live from DEC-1211 on (DEC-1215 (2)
orders its revert recorded in its entry). ``--out`` is a first build: the archive's kept entries, then every entry
from DEC-1211 on as the archive has it. Only the kept part of the committed register is that build's, byte for byte.
``--check`` names a kept entry (below DEC-1211) that the register lacks or holds with another text; an entry from
DEC-1211 on that differs from the archive's copy, or that the archive lacks, is no failure.
"""

from __future__ import annotations

import re

import pytest

import w2_203_support as s

MISSING, DIFFERS = "REGISTER_KEPT_MISSING", "REGISTER_ENTRY_DIFFERS"
APPENDED = "DEC-1217"  # the next id after the last of the base register
FAR, AFTER_THE_MOVE = "DEC-1299", "DEC-1300"
LAST_CLASSED = "DEC-1210"  # the last id audit 8 classed: the highest id a kept entry has


def _kept_part(text: str) -> str:
    """A register's text from its first entry's heading to the heading of its first entry from DEC-1211 on (to its
    end where it holds none): the part that is the archive's."""
    first = re.search(r"^### DEC-[0-9]+", text, re.MULTILINE)
    assert first, "the text holds no entry"
    late = next((found for found in re.finditer(r"^### (DEC-[0-9]+)", text, re.MULTILINE)
                 if s.live(found.group(1))), None)
    return text[first.start():late.start() if late else len(text)]


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

def test_s6_rebuilding_from_the_archive_gives_the_committed_registers_kept_part_byte_for_byte(home, tmp_path):
    """The kept part of the committed register (its entries below DEC-1211, with what stands between them) is the
    build's, byte for byte, and holds exactly the archive's entries of class ``kept``. The entries from DEC-1211 on
    are the register's own and are not compared: the build writes them as the archive has them."""
    out = tmp_path / "rebuilt.md"
    done = _run(home, "--out", str(out))
    assert done.returncode == 0 and out.is_file(), f"exit {done.returncode}: {done.stderr[-800:]}"
    built, committed = out.read_text(encoding="utf-8"), (s.REPO / s.REGISTER_REL).read_text(encoding="utf-8")
    assert _kept_part(built).encode("utf-8") == _kept_part(committed).encode("utf-8"), \
        f"the kept part of the register rebuilt from the archive is not that of the committed {s.REGISTER_REL}"
    archive = s.entries((s.REPO / s.ARCHIVE_REL).read_text(encoding="utf-8"))
    wanted = [(record_id, text) for record_id, text in archive if s.classed_kept(record_id, text)]
    assert len(wanted) > 100 and s.entries(_kept_part(committed)) == wanted, \
        "the committed register's kept part is not exactly the archive's entries of class kept"
    assert s.entries(built) == [(record_id, text) for record_id, text in archive if s.kept(record_id, text)], \
        "a first build is not the archive's kept entries, then its entries from DEC-1211 on as it has them"


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
    """The rest is the first build's: the archive's kept entries and its entries from DEC-1211 on as the archive has
    them, and its kept part is the committed register's. The committed register's own entries from DEC-1211 on (live,
    amended in place, new ones appended) are not what a build from the archive gives, and are not compared."""
    committed = (s.REPO / s.REGISTER_REL).read_text(encoding="utf-8")
    archive_file = s.REPO / s.ARCHIVE_REL
    assert archive_file.is_file(), f"{s.ARCHIVE_REL} is not a file of this tree"
    archived = s.entries(archive_file.read_text(encoding="utf-8"))
    last = max(s.number_of(record_id) for record_id, _ in archived + s.entries(committed))
    entry = _late(f"DEC-{last + 1}", "wintergreen")
    archive, out = tmp_path / "archive.md", tmp_path / "out.md"
    archive.write_text(archive_file.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + entry + "\n", encoding="utf-8")
    done = _run(home, "--archive", str(archive), "--out", str(out))
    assert done.returncode == 0, done.stderr[-800:]
    written = out.read_text(encoding="utf-8")
    assert entry in written, "the appended entry is not in the output verbatim"
    first_build = [(record_id, text) for record_id, text in archived if s.kept(record_id, text)]
    assert s.entries(written) == first_build + [(f"DEC-{last + 1}", entry)], "the existing entries changed"
    assert _kept_part(written) == _kept_part(committed), "the kept part is no longer the committed register's"


# ---------------------------------------------------------------- F1

def test_f1_real_the_committed_register_and_archive_check_clean(home):
    """Clean means the kept part: every kept entry of the archive is in the committed register with the archive's
    text. The committed register's entries from DEC-1211 on are live (DEC-1215's entry records its revert, which the
    archive's copy does not) and new ones follow that the archive lacks: neither is a failure line."""
    _ok(_run(home, "--check"))


@pytest.mark.parametrize("lost", [s.K_FIRST, s.K_SECOND])
def test_f1_a_register_that_lacks_a_kept_entry_is_named(built, home, tmp_path, lost):
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
    s.write(root, s.REGISTER_REL, s.without_entry(s.without_entry(text, s.K_FIRST), s.K_SECOND))
    done = _run(home, "--root", str(root), "--check")
    assert sorted(_lines(done)) == sorted(f"{MISSING} {lost}" for lost in (s.K_FIRST, s.K_SECOND))
    assert done.returncode == 1


def test_f1_a_decision_made_after_the_move_is_no_failure(built, home, tmp_path):
    root, text = built
    register = tmp_path / "register.md"
    register.write_text(text.rstrip("\n") + "\n\n" + _late(AFTER_THE_MOVE, "foxglove") + "\n", encoding="utf-8")
    _ok(_run(home, "--root", str(root), "--register", str(register), "--check"))


# ---------------------------------------------------------------- F2

def _one_character_changed(text: str, record_id: str, entry=s.ENTRY) -> str:
    last = entry[record_id].split("\n")[-1]
    assert text.count(last) == 1, f"premise: the last line of {record_id} stands once in the register"
    return text.replace(last, last[:-2] + "x" + last[-1])


@pytest.mark.parametrize("changed", [s.K_FIRST, s.K_SECOND])
def test_f2_a_kept_entry_whose_text_differs_by_one_character_is_named(built, home, tmp_path, changed):
    root, text = built
    register = tmp_path / "register.md"
    register.write_text(_one_character_changed(text, changed), encoding="utf-8")
    done = _run(home, "--root", str(root), "--register", str(register), "--check")
    assert _lines(done) == [f"{DIFFERS} {changed}"] and done.returncode == 1, \
        f"exit {done.returncode}: {done.stdout[-600:]} {done.stderr[-600:]}"


def test_f2_an_entry_from_dec_1211_on_that_differs_and_one_the_archive_lacks_are_no_failure(built, home, tmp_path):
    """The register in force is live from DEC-1211 on: one such entry amended in place (a line added, as DEC-1215's
    revert is recorded in its entry), another changed by one character, and a decision the archive does not hold at
    all appended. The check is clean. With a kept entry changed as well, that entry alone is named: the check still
    compares, and the live entries' differences are still no line."""
    root, text = built
    amended = s.ENTRY[s.K_LATE] + "\n- **Amended (2026-11-19):** the thistledown plan was reverted, as its item says."
    assert text.count(s.ENTRY[s.K_LATE]) == 1, "premise: the built register holds the late entry once"
    live = _one_character_changed(text.replace(s.ENTRY[s.K_LATE], amended), s.K_LATER)
    live = live.rstrip("\n") + "\n\n" + _late(AFTER_THE_MOVE, "foxglove") + "\n"
    held = dict(s.entries(live))
    assert held[s.K_LATE] == amended and held[s.K_LATER] != s.ENTRY[s.K_LATER] and AFTER_THE_MOVE in held, \
        "premise: the planted register's entries from DEC-1211 on differ from the archive's, and one is new"
    register = tmp_path / "register.md"
    register.write_text(live, encoding="utf-8")
    _ok(_run(home, "--root", str(root), "--register", str(register), "--check"))
    register.write_text(_one_character_changed(live, s.K_FIRST), encoding="utf-8")
    done = _run(home, "--root", str(root), "--register", str(register), "--check")
    assert _lines(done) == [f"{DIFFERS} {s.K_FIRST}"] and done.returncode == 1, \
        f"exit {done.returncode}: {done.stdout[-600:]} {done.stderr[-600:]}"


def test_f2_the_last_classed_id_is_still_held_to_the_archive(project, home, tmp_path):
    """The boundary: DEC-1210 is the last id audit 8 classed. A kept entry with that id is the archive's, so one
    character changed in it is named; DEC-1211 beside it, changed the same way, is not."""
    entry = {**s.ENTRY, LAST_CLASSED: (f"### {LAST_CLASSED} — The saltmarsh rule\n"
                                       "- **Status:** ACCEPTED (owner, 2026-11-16) · **Class:** kept\n"
                                       "- **Decision:** the saltmarsh sluice is opened at the ebb.")}
    order = (*s.ARCHIVE_ORDER[:-2], LAST_CLASSED, *s.ARCHIVE_ORDER[-2:])
    archive, out, register = tmp_path / "archive.md", tmp_path / "out.md", tmp_path / "register.md"
    archive.write_text(s.archive_text(order, entry), encoding="utf-8")
    done = _run(home, "--root", str(project), "--archive", str(archive), "--out", str(out))
    assert done.returncode == 0, done.stderr[-800:]
    text = out.read_text(encoding="utf-8")
    assert [record_id for record_id, _ in s.entries(text)] == [s.K_FIRST, s.K_SECOND, LAST_CLASSED, s.K_LATE, s.K_LATER]
    register.write_text(_one_character_changed(_one_character_changed(text, LAST_CLASSED, entry), s.K_LATE),
                        encoding="utf-8")
    done = _run(home, "--root", str(project), "--archive", str(archive), "--register", str(register), "--check")
    assert _lines(done) == [f"{DIFFERS} {LAST_CLASSED}"] and done.returncode == 1, \
        f"exit {done.returncode}: {done.stdout[-600:]} {done.stderr[-600:]}"
