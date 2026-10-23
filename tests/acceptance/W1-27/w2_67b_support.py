"""Small helpers for W2-67's second batch of W1-27 revisions (I4 F1): files of a small project, and doctor's
moved-path references read from its ``path_compliance`` section (``w2_67_doctor.section``)."""

from __future__ import annotations

import w1_27_support as support
import w2_67_doctor


def write_committed(project, relative, text, message=None):
    """Write one file of the project and commit it."""
    path = project / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    support.commit_all(project, message or f"add {relative}")
    return path


def move_committed(project, old_relative, new_relative):
    """Add a file at ``old_relative``, commit, move it to ``new_relative``, commit: a moved path git records."""
    old = write_committed(project, old_relative, "# a module that moves\n")
    new = project / new_relative
    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new)
    support.commit_all(project, f"move {old_relative} to {new_relative}")
    return new


def moved_references(run):
    """``path_compliance.moved_references``: a list of entries, wherever doctor put the section."""
    found = w2_67_doctor.section(run, "path_compliance").get("moved_references")
    assert isinstance(found, list), f"path_compliance.moved_references is not a list\n{run.describe()}"
    return found


def references_to(references, old_path, referenced_in):
    """The entries reporting ``old_path`` as referenced in ``referenced_in``."""
    return [ref for ref in references
            if isinstance(ref, dict) and ref.get("old_path") == old_path and ref.get("referenced_in") == referenced_in]
