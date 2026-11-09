"""W2-129 S17 and F7: planted ids in test fixtures (D-6 part 2; DEC-1109 (2), DEC-1098 (3) row 24).

In a Python test file (``tests/**/*.py``) an id inside a string literal that is not a docstring is a planted id: it
gives no UNKNOWN_ID, and an ENFORCES_SUPERSEDED that W2-55's propagation gives for that line is carried only when the
old id also stands on the line outside such a literal. Comments, docstrings, non-Python test files and a Python test
file that does not parse are judged as today; W2-55's module is unchanged.

One planted commit on a copy of repository A adds the files of ``S17_FILES`` (none of them cites DEC-108, so W2-55's
propagation names every line citing the superseded DEC-107); ``gov links --all`` runs once on it. Each unknown id is
used once, so no case rests on how the tool treats an id seen twice. The oracles are the planted text (``line_of``)
and W2-55's ``check_propagation``, never ``gov.links``.
"""

from __future__ import annotations

import subprocess
import sys

import pytest
import w2_129_support as support

PLANTED = "tests/unit/test_s17_planted.py"
COMMENTS = "tests/unit/test_s17_comments.py"
DOCSTRINGS = "tests/unit/test_s17_docstrings.py"
BROKEN = "tests/unit/test_s17_broken.py"
MIXED = "tests/unit/test_s17_mixed.py"
README = "tests/unit/README.md"
JSON = "tests/unit/fixtures/planted.json"

S17_FILES = {
    # Literals only: a planted register (an unknown DEC-981 and the superseded DEC-107), a record path (DEC-982) and
    # an f-string path (``TARGET``'s ticket). The module docstring names no id.
    PLANTED: '''\
"""The planted fixtures of a window check: a register, a record path and a test path."""

ACCEPTANCE = "tests/acceptance"

REGISTER = """\\
# Decision register

### DEC-981: A planted rule
- **Status:** ACCEPTED

### DEC-107: The old window
- **Status:** ACCEPTED

The old window is 300.
"""

RECORD = "records/decisions/DEC-982.md"
TARGET = f"{ACCEPTANCE}/W1-90/test_fixture.py"


def test_planted():
    assert REGISTER and RECORD and TARGET
''',
    # Literals on some lines (DEC-983, DEC-107), comments on others (DEC-984, DEC-107).
    COMMENTS: '''\
"""Window checks whose comments cite their decisions."""

PLANTED = "records/decisions/DEC-983.md"
OLD = "DEC-107"


def test_window():
    # DEC-984 fixes the window
    # DEC-107 set the old window
    assert PLANTED and OLD
''',
    # A module docstring (DEC-985) and a function's multi-line docstring (DEC-986).
    DOCSTRINGS: '''\
"""Window checks under DEC-985, the planted module's rule."""


def test_window():
    """The window holds.

    DEC-986 fixes it.
    """
    assert True
''',
    # A Python test file that does not parse: its "literal" ids (DEC-988, DEC-107) are judged as today.
    BROKEN: '''\
"""A test file that does not parse."""

REGISTER = "### DEC-988: a planted rule; DEC-107 the old window"


def broken(:
    pass
''',
    # The old id and an unknown id each in a literal and in a trailing comment on the same line.
    MIXED: '''\
"""A window check whose literal and comment share a line."""

WINDOW = "DEC-107"  # DEC-107 set the old window
RECORD = "records/decisions/DEC-989.md"  # DEC-989 is the planted record


def test_window():
    assert WINDOW and RECORD
''',
    # Non-Python test files: a README citation and an id in a JSON string.
    README: "# Unit tests\n\nThe window cases enforce DEC-107.\n",
    JSON: '{"decision": "DEC-107", "window": 300}\n',
}

# The literal places that must be quiet after S17: (path, needle of the line, the id).
QUIET_UNKNOWN = [(PLANTED, "### DEC-981", "DEC-981"), (PLANTED, "DEC-982.md", "DEC-982"),
                 (COMMENTS, "DEC-983.md", "DEC-983")]
QUIET_SUPERSEDED = [(PLANTED, "### DEC-107", "DEC-107"), (COMMENTS, 'OLD = "DEC-107"', "DEC-107")]


@pytest.fixture(scope="module")
def s17(full, tmp_path_factory):
    """A copy of repository A with the S17 files committed, and ``gov links --all`` on it (unchecked)."""
    shas = support.clone(full, tmp_path_factory.mktemp("w2-129-s17") / "repo")
    for rel, text in S17_FILES.items():
        support.write(shas["repo"], rel, text)
    shas["s17"] = support.commit(shas["repo"], "the planted fixtures",
                                 {"Task": "DAEO-t005", "Implements": "DEC-100", "Role": "independent-test-designer"}, 8)
    return shas, support.spawn(shas["repo"], "--all")


@pytest.fixture()
def repo(s17):
    return s17[0]["repo"]


@pytest.fixture()
def out(s17):
    return support.Output(s17[1])


def line(repo, path, needle):
    return support.line_of(repo, path, needle)


def found_at(out, code, path, number, rid):
    """The findings of ``code`` at ``path:number`` whose first field names ``rid``."""
    return [f for f in out.findings if f.code == code and f.path == path and f.line == number and rid in f.head]


def propagation_lines(repo) -> set[tuple[str, int]]:
    """``(path, line)`` of each place W2-55's ``check_propagation`` names (the S7 oracle)."""
    sys.path.insert(0, str(support.src_dir()))
    from gov.decisions.propagation import check_propagation

    places = set()
    for finding in check_propagation(repo):
        where = finding["message"].split(" ", 1)[0]
        path, _, number = where.rpartition(":")
        places.add((path, int(number)))
    return places


# ---------------------------------------------------------------------------------- planted, now quiet (red)

def test_s17_an_unknown_id_in_a_non_docstring_literal_of_a_python_test_file_gives_no_unknown_id(out, repo):
    """S17 (1), F7: DEC-981 (in a planted register string), DEC-982 (in a record path) and ``TARGET``'s ticket id
    (in an f-string path) give no UNKNOWN_ID; nor does DEC-983, a literal in a file whose comment DEC-984 is still found."""
    control = found_at(out, "UNKNOWN_ID", COMMENTS, line(repo, COMMENTS, "# DEC-984"), "DEC-984")
    assert control, "the control is missing: no UNKNOWN_ID for DEC-984 in a comment of a test file"
    assert not [f for f in out.findings if f.code == "UNKNOWN_ID" and f.path == PLANTED], \
        [f for f in out.findings if f.code == "UNKNOWN_ID" and f.path == PLANTED]
    for path, needle, rid in QUIET_UNKNOWN:
        number = line(repo, path, needle)
        assert not [f for f in out.findings if f.code == "UNKNOWN_ID" and f.path == path and f.line == number], \
            f"a planted literal id still reported as UNKNOWN_ID: {rid} at {path}:{number}"


def test_s17_a_superseded_id_only_inside_a_planted_literal_is_not_carried(out, repo):
    """S17 (2), F7: W2-55 names DEC-107 inside the planted register string and inside ``OLD = "DEC-107"``; neither
    line is carried, while the comment ``# DEC-107`` of the same file is."""
    places = propagation_lines(repo)
    for path, needle, _ in QUIET_SUPERSEDED:
        assert (path, line(repo, path, needle)) in places, f"premise: W2-55 does not name {path}'s {needle!r}"
    control = found_at(out, "ENFORCES_SUPERSEDED", COMMENTS, line(repo, COMMENTS, "# DEC-107"), "DEC-107")
    assert control, "the control is missing: the comment's ENFORCES_SUPERSEDED is not carried"
    assert not [f for f in out.findings if f.code == "ENFORCES_SUPERSEDED" and f.path == PLANTED], \
        [f for f in out.findings if f.code == "ENFORCES_SUPERSEDED" and f.path == PLANTED]
    for path, needle, rid in QUIET_SUPERSEDED:
        number = line(repo, path, needle)
        assert not found_at(out, "ENFORCES_SUPERSEDED", path, number, rid), \
            f"a planted literal still carried as ENFORCES_SUPERSEDED: {path}:{number}"


# --------------------------------------------------------------------------------- still judged (guards)

def test_s17_guard_ids_in_comments_are_judged(out, repo):
    """S17 (3), F7: an unknown id in a comment gives UNKNOWN_ID and the superseded id in a comment is carried, in a
    file whose other lines hold planted literals."""
    assert found_at(out, "UNKNOWN_ID", COMMENTS, line(repo, COMMENTS, "# DEC-984"), "DEC-984"), \
        "no UNKNOWN_ID for DEC-984 in a comment"
    assert found_at(out, "ENFORCES_SUPERSEDED", COMMENTS, line(repo, COMMENTS, "# DEC-107"), "DEC-107"), \
        "no ENFORCES_SUPERSEDED for DEC-107 in a comment"


def test_s17_guard_ids_in_module_and_function_docstrings_are_judged(out, repo):
    """S17 (3), F7: a docstring is not a planted literal: DEC-985 (module) and DEC-986 (a function's multi-line
    docstring) each give UNKNOWN_ID at their line."""
    for needle, rid in (("under DEC-985", "DEC-985"), ("DEC-986 fixes it.", "DEC-986")):
        number = line(repo, DOCSTRINGS, needle)
        assert found_at(out, "UNKNOWN_ID", DOCSTRINGS, number, rid), f"no UNKNOWN_ID for {rid} at {DOCSTRINGS}:{number}"


def test_s17_guard_non_python_test_files_are_judged(out, repo):
    """S17 (3), F7: a test folder's README.md citing DEC-107, and a JSON fixture holding it in a string, are each
    carried as ENFORCES_SUPERSEDED (W2-55 names both)."""
    places = propagation_lines(repo)
    for path, needle in ((README, "enforce DEC-107"), (JSON, '"DEC-107"')):
        number = line(repo, path, needle)
        assert (path, number) in places, f"premise: W2-55 does not name {path}:{number}"
        assert found_at(out, "ENFORCES_SUPERSEDED", path, number, "DEC-107"), \
            f"no ENFORCES_SUPERSEDED carried at {path}:{number}"


def test_s17_guard_a_python_test_file_that_does_not_parse_is_judged_as_today(out, repo):
    """S17 (3), F7: in a file with a syntax error, DEC-988 gives UNKNOWN_ID and DEC-107 is carried, on the line where
    a parsed file would have held them in a literal."""
    number = line(repo, BROKEN, "REGISTER = ")
    assert found_at(out, "UNKNOWN_ID", BROKEN, number, "DEC-988"), f"no UNKNOWN_ID for DEC-988 at {BROKEN}:{number}"
    assert (BROKEN, number) in propagation_lines(repo), f"premise: W2-55 does not name {BROKEN}:{number}"
    assert found_at(out, "ENFORCES_SUPERSEDED", BROKEN, number, "DEC-107"), \
        f"no ENFORCES_SUPERSEDED carried at {BROKEN}:{number}"


def test_s17_guard_a_line_with_the_id_in_a_literal_and_in_a_trailing_comment_is_judged(out, repo):
    """S17 (2) and (3), F7: ``WINDOW = "DEC-107"  # DEC-107 ...`` is carried (the old id stands outside the literal);
    ``RECORD = "...DEC-989.md"  # DEC-989 ...`` gives UNKNOWN_ID (the comment's id)."""
    window = line(repo, MIXED, "WINDOW = ")
    assert (MIXED, window) in propagation_lines(repo), f"premise: W2-55 does not name {MIXED}:{window}"
    assert found_at(out, "ENFORCES_SUPERSEDED", MIXED, window, "DEC-107"), \
        f"no ENFORCES_SUPERSEDED carried at {MIXED}:{window}"
    record = line(repo, MIXED, "RECORD = ")
    assert found_at(out, "UNKNOWN_ID", MIXED, record, "DEC-989"), f"no UNKNOWN_ID for DEC-989 at {MIXED}:{record}"


# ----------------------------------------------------------------------------------------- W2-55 unchanged

def test_s17_w2_55_propagation_still_names_the_planted_literal_lines(repo):
    """S17 (4): ``python3 -m gov.decisions.propagation`` in the planted repository still reports the planted
    register's DEC-107 line and ``OLD = "DEC-107"`` (the carrying is the filter, not the module)."""
    done = subprocess.run([sys.executable, "-m", "gov.decisions.propagation"], cwd=repo, capture_output=True,
                          text=True, timeout=120, env=support.child_env())
    assert done.returncode == 1, (done.returncode, done.stdout, done.stderr)
    for path, needle, rid in QUIET_SUPERSEDED:
        where = f"{path}:{line(repo, path, needle)} "
        assert any(where in row and rid in row for row in done.stdout.splitlines()), (where, done.stdout)
