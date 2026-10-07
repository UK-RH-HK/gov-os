"""KPI failure 2: ``framework.lock`` lacks the template tag or commit.

CAP-43's acceptance: the lock records the template tag, the commit and the
file-hash manifest, and ``gov doctor`` fails when any of them disagrees with
the installed kernel. DEC-023: the lock is the reference to Copier's answers
file plus the manifest generated at install.

The tag and the commit are those of the temporary template repository each
test builds; no tag is ever made in this repository. No key name of the lock is
fixed here beyond the manifest's: the cases look for the values.
"""

from __future__ import annotations

import pytest

import w1_39_support as support


def test_the_lock_names_the_template_tag(installed):
    """The lock of a project created from the release ``v0.1.0`` carries that tag."""
    assert support.FIRST_TAG in support.lock_text(installed), \
        f"{support.LOCK_REL} does not name the template tag {support.FIRST_TAG}"


def test_the_lock_names_the_template_commit(installed, pristine_source):
    """The lock carries the full id of the commit the release tag points at."""
    commit = pristine_source.first.commit
    assert commit in support.lock_text(installed), \
        f"{support.LOCK_REL} does not name the template commit {commit}"


def test_the_lock_of_an_untagged_template_commit_still_names_the_commit(copier_bin, source, sandbox, tmp_path):
    """A project created from a commit that carries no tag of its own: the lock names that commit, in full."""
    support.write_template_file(source, f"{support.KERNEL_REL}/w1_39_after_the_tag.md", "one more kernel file\n")
    later = support.release(source.path, None, "a commit after the release tag")
    assert later.commit != source.first.commit
    project = support.create_project(copier_bin, sandbox, source, tmp_path / "product", ref="HEAD")
    text = support.lock_text(project)
    assert later.commit in text, f"{support.LOCK_REL} does not name the template commit {later.commit}"
    assert source.first.commit not in text, \
        f"{support.LOCK_REL} names the commit of the tag {support.FIRST_TAG}, not the commit the project was created from"


def test_the_lock_refers_to_the_answers_file(installed, pristine_source):
    """DEC-023 and ADR-0002 (L7): the lock is the answers reference plus the manifest."""
    rel = pristine_source.answers_rel()
    assert rel in support.lock_text(installed), f"{support.LOCK_REL} does not refer to the answers file {rel}"


@pytest.mark.parametrize("what", ("tag", "commit"))
def test_doctor_fails_when_the_locks_tag_or_commit_disagrees_with_the_install(project, source, sandbox, what):
    """CAP-43: a lock whose tag or commit is not the one the project was installed from is not a match.

    Red until the doctor package is decided (``src/gov/doctor/`` is outside this ticket's paths).
    """
    recorded, other = {"tag": (support.FIRST_TAG, "v9.9.9"), "commit": (source.first.commit, "0" * 40)}[what]
    text = support.lock_text(project)
    assert recorded in text, f"{support.LOCK_REL} does not name the template {what} {recorded}"
    support.lock_path(project).write_text(text.replace(recorded, other), encoding="utf-8")
    result = support.doctor(project, sandbox)
    support.assert_not_a_match(result, f"the lock's {what} was changed from {recorded} to {other}")
    assert result.run.returncode != 0, \
        f"gov doctor exits 0 although the lock's {what} disagrees with the install\n{result.describe()}"
