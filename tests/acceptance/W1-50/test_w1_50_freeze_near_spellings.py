"""W1-50, KPI line 1 (DEC-402), review findings on the guard's reading of the flag (DEC-136).

"...the guard treats an empty file, or one without the marker, at the flag's
path as no freeze..."

Two groups, each asked through the hook command with the one question nothing
but a freeze denies (a Write by the engineer inside its ticket's paths):

- **Near spellings of the marker.** A flag written by hand, by another tool or
  on another system carries the word and is not the exact line ``gov pause``
  writes: another text encoding, an invisible character at the word,
  punctuation or quoting at the word, the word after another word. The guard
  cannot tell whether such a line is a marker line, so it freezes: a freeze
  that does not hold is the guard failing open (DEC-179). What stays no freeze
  is DEC-402's own case: a file that does not carry the word at all, whatever
  its encoding.
- **The runtime folder is not a folder.** A regular file at ``.gov-runtime``
  leaves no place for a flag: nothing is at the flag's path, no freeze. A
  dangling link at ``.gov-runtime`` hides the folder that would hold the
  flag: the guard cannot tell, frozen.

One case per form. The readings and their sources are in
``w1_50_freeze_README.md``.
"""

from __future__ import annotations

import codecs
import os

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import freeze_project, freeze_sandbox  # noqa: F401  fixtures

MARKER = support.A_MARKER_LINE                 # "FROZEN owner 2026-10-05T00:00:00Z\n"
REST = MARKER[len(support.MARKER_WORD):]       # " owner 2026-10-05T00:00:00Z\n"
BOM = codecs.BOM_UTF8

# form: the bytes of the file at the flag's path. Every one carries the word.
NEAR_SPELLINGS = {
    # the marker line in another text encoding
    "utf-16-le-with-a-byte-order-mark": codecs.BOM_UTF16_LE + MARKER.encode("utf-16-le"),
    "utf-16-be-with-a-byte-order-mark": codecs.BOM_UTF16_BE + MARKER.encode("utf-16-be"),
    "utf-16-without-a-byte-order-mark": MARKER.encode("utf-16-le"),
    "utf-32-with-a-byte-order-mark": codecs.BOM_UTF32_LE + MARKER.encode("utf-32-le"),
    "utf-32-without-a-byte-order-mark": MARKER.encode("utf-32-be"),
    "a-doubled-utf-8-byte-order-mark": BOM + BOM + MARKER.encode(),
    # an invisible character at the word
    "a-nul-before-the-word": b"\x00" + MARKER.encode(),
    "a-no-break-space-before-the-word": (" " + MARKER).encode(),
    "a-zero-width-space-before-the-word": ("​" + MARKER).encode(),
    "a-nul-right-after-the-word": b"FROZEN\x00" + REST.encode(),
    # punctuation or quoting at the word, and the word after another word
    "a-colon-at-the-word": ("FROZEN:" + REST).encode(),
    "a-comma-at-the-word": ("FROZEN," + REST).encode(),
    "a-full-stop-at-the-word": b"FROZEN.\n",
    "the-word-in-quotes": b'"FROZEN"\n',
    "the-word-after-a-comment-sign": ("# FROZEN" + REST).encode(),
    "the-word-as-the-value-of-a-key": b"state: FROZEN\n",
    "the-word-joined-to-another-by-an-underscore": b"FROZEN_BY: owner\n",
}

# form: the bytes of a file that does not carry the word. DEC-402: no freeze.
WITHOUT_THE_WORD = {
    "other-text-in-utf-16": codecs.BOM_UTF16_LE + "off\n".encode("utf-16-le"),
    "a-byte-order-mark-alone": BOM,
}


@pytest.fixture()
def project(freeze_project):  # noqa: F811
    return freeze_project


@pytest.fixture()
def sandbox(freeze_sandbox):  # noqa: F811
    return freeze_sandbox


@pytest.mark.parametrize("form", sorted(NEAR_SPELLINGS))
def test_a_near_spelling_of_the_marker_freezes(project, sandbox, form):
    support.assert_not_frozen(support.guard_write(project, sandbox), "before anything is at the flag's path, Write")
    support.put_text(project, NEAR_SPELLINGS[form])
    support.assert_frozen(
        support.guard_write(project, sandbox),
        f"with {form} at {support.FLAG_REL} ({NEAR_SPELLINGS[form][:48]!r}): the file carries the word, the guard "
        f"cannot tell that it is not a marker line, Write",
    )


@pytest.mark.parametrize("form", sorted(WITHOUT_THE_WORD))
def test_a_file_that_does_not_carry_the_word_is_no_freeze_in_any_encoding(project, sandbox, form):
    support.put_text(project, WITHOUT_THE_WORD[form])
    support.assert_not_frozen(support.guard_write(project, sandbox),
                              f"with {form} at {support.FLAG_REL} ({WITHOUT_THE_WORD[form]!r}), Write")


# --------------------------------------------------------------------------
# The runtime folder is not a folder
# --------------------------------------------------------------------------

def _calls(project, sandbox):
    yield "Write", support.guard_write(project, sandbox, "Write")
    yield "Edit", support.guard_write(project, sandbox, "Edit")
    command = f"echo changed > {support.OWN_REL}"
    yield f"Bash `{command}`", support.guard_bash(project, sandbox, command)


def test_a_project_without_a_runtime_folder_is_not_frozen(project, sandbox):
    """Must stay: a project that has never run anything has no ``.gov-runtime`` at all."""
    runtime = project / support.RUNTIME_REL
    assert not os.path.lexists(runtime), "the fixture project starts with a runtime folder"
    support.assert_not_frozen(support.guard_write(project, sandbox), f"with no {support.RUNTIME_REL} at all, Write")


def test_a_regular_file_where_the_runtime_folder_should_be_is_no_freeze(project, sandbox):
    """No flag can be at the path: the guard can tell. Empty and 0444: the shape of a sandbox placeholder."""
    runtime = project / support.RUNTIME_REL
    runtime.write_bytes(b"")
    runtime.chmod(0o444)
    for what, result in _calls(project, sandbox):
        support.assert_not_frozen(result, f"with an empty regular file at {support.RUNTIME_REL}, {what}")
    assert runtime.is_file() and not runtime.is_symlink() and runtime.stat().st_size == 0, \
        f"asking the guard changed what is at {support.RUNTIME_REL}"


def test_a_dangling_link_where_the_runtime_folder_should_be_freezes(project, sandbox):
    """The folder that would hold the flag cannot be reached: the guard cannot tell whether a freeze is set."""
    runtime = project / support.RUNTIME_REL
    assert not os.path.lexists(runtime), "the fixture project starts with a runtime folder"
    target = sandbox.elsewhere / "no-such-runtime-folder"
    runtime.symlink_to(target, target_is_directory=True)
    for what, result in _calls(project, sandbox):
        support.assert_frozen(result, f"with a dangling link at {support.RUNTIME_REL}, {what}")
    assert runtime.is_symlink() and not os.path.lexists(target), \
        f"asking the guard changed the link at {support.RUNTIME_REL}, or created its target"
