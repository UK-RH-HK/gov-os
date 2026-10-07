"""KPI failure 1: an overlay file is overwritten by ``copier update``.
KPI success 2, second half: the update procedure is documented.

The overlay is ``governance/project/`` (ADR-0002 section 5; DEC-023: overlay
files are listed in ``_skip_if_exists``). A later release is made in the
temporary template repository: a second commit and the tag ``v0.2.0``. No tag
is made in this repository.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w1_39_support as support

OVERLAY_FILES = ("governance/project/path-map.yaml", "governance/project/policies/local.yaml")
PROJECT_TEXT = "owner: the project\nvalue: 1\n"
TEMPLATE_V1_TEXT = "owner: the template\nvalue: 1\n"
TEMPLATE_V2_TEXT = "owner: the template\nvalue: 2\nadded: by the second release\n"


def _a_hook(source):
    hooks = source.plain_files(support.HOOKS_REL)
    assert hooks, "the template source has no hook"
    return sorted(hooks)[0]


def _second_release(source, overlay=()):
    """The second release: one kernel file changed, one added, and the template's own text for ``overlay`` files."""
    changed = _a_hook(source)
    with open(source.template / changed, "ab") as handle:
        handle.write(b"\n# changed by the second release\n")
    added = f"{support.KERNEL_REL}/w1_39_second_release.md"
    support.write_template_file(source, added, "added by the second release\n")
    for rel in overlay:
        support.write_template_file(source, rel, TEMPLATE_V2_TEXT)
    return support.release(source.path, support.SECOND_TAG, "the second release"), changed, added


def _updated(copier_bin, sandbox, source, project):
    done = support.update(copier_bin, sandbox, source, project)
    assert done.returncode == 0, f"`copier update` failed\n{done.describe()}"
    return done


# --------------------------------------------------------------------------
# The overlay survives an update
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rel", OVERLAY_FILES)
def test_update_keeps_an_overlay_file_the_project_wrote(copier_bin, source, project, sandbox, rel):
    """The project wrote the file; the second release ships its own text at that path; the project's stays."""
    (project / rel).parent.mkdir(parents=True, exist_ok=True)
    (project / rel).write_text(PROJECT_TEXT, encoding="utf-8")
    support.commit_all(project, "the project's overlay")
    _second_release(source, overlay=(rel,))
    done = _updated(copier_bin, sandbox, source, project)
    assert (project / rel).read_text(encoding="utf-8") == PROJECT_TEXT, \
        f"`copier update` overwrote the overlay file {rel}\n{done.describe()}"


@pytest.mark.parametrize("rel", OVERLAY_FILES)
def test_update_keeps_an_overlay_file_the_template_shipped_and_the_project_edited(
        copier_bin, source, sandbox, tmp_path, rel):
    """Both releases ship the file; the project edited its copy; the edit stays, without a merge or a conflict mark."""
    support.write_template_file(source, rel, TEMPLATE_V1_TEXT)
    support.git(source.path, "tag", "-d", support.FIRST_TAG)
    support.release(source.path, support.FIRST_TAG, "a first release that ships an overlay file")
    project = support.create_project(copier_bin, sandbox, source, tmp_path / "product")
    assert (project / rel).is_file(), f"`copier copy` did not create {rel}, which the release ships"
    (project / rel).write_text(PROJECT_TEXT, encoding="utf-8")
    support.commit_all(project, "the project's edit of its overlay")
    _second_release(source, overlay=(rel,))
    done = _updated(copier_bin, sandbox, source, project)
    assert (project / rel).read_text(encoding="utf-8") == PROJECT_TEXT, \
        f"`copier update` changed the overlay file {rel}\n{done.describe()}"
    rejects = [name for name in support.files_under(project, support.OVERLAY_REL) if name.endswith((".rej", ".orig"))]
    assert not rejects, f"`copier update` left reject files in the overlay: {rejects}"


def test_update_leaves_every_file_the_project_added_as_it_was(copier_bin, source, project, sandbox):
    """Tickets, decisions and the project's own code are not the template's: an update does not touch them."""
    own = {
        ".tickets/DAEO-zz01.md": "---\nid: DAEO-zz01\n---\n# a ticket of the project\n",
        "spec/decisions/0001-a-decision.md": "# a decision of the project\n",
        "src/app.py": "VALUE = 1\n",
        "governance/project/roster.yaml": "roles: []\n",
    }
    for rel, text in own.items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8")
    support.commit_all(project, "the project's own files")
    _second_release(source)
    done = _updated(copier_bin, sandbox, source, project)
    changed = [rel for rel, text in own.items()
               if not (project / rel).is_file() or (project / rel).read_text(encoding="utf-8") != text]
    assert not changed, f"`copier update` changed or removed the project's own files: {changed}\n{done.describe()}"


# --------------------------------------------------------------------------
# The update does update: the kernel and the lock follow the release
# --------------------------------------------------------------------------

def test_update_brings_the_kernel_of_the_second_release(copier_bin, source, project, sandbox):
    """The changed kernel file and the added one arrive: the overlay is spared, the kernel is not."""
    _, changed, added = _second_release(source)
    done = _updated(copier_bin, sandbox, source, project)
    assert (project / changed).read_bytes() == (source.template / changed).read_bytes(), \
        f"`copier update` did not bring the second release's {changed}\n{done.describe()}"
    assert (project / added).is_file(), f"`copier update` did not bring the added kernel file {added}"


def test_after_an_update_the_lock_names_the_second_release_and_its_files(copier_bin, source, project, sandbox):
    """The lock follows the update: the new tag, the new commit, and a manifest of the kernel as it now is."""
    second, _, added = _second_release(source)
    _updated(copier_bin, sandbox, source, project)
    text = support.lock_text(project)
    assert support.SECOND_TAG in text and second.commit in text, \
        f"after the update {support.LOCK_REL} does not name the tag {support.SECOND_TAG} and the commit {second.commit}"
    manifest = support.manifest_of(project)
    stale = [rel for rel in support.kernel_files(project) if manifest.get(rel) != support.sha256(project / rel)]
    assert not stale, f"after the update the manifest does not hold the sha256 of these kernel files: {stale[:5]}"
    assert added in manifest, f"after the update the manifest does not list the added kernel file {added}"


def test_after_an_update_doctor_reports_a_match(copier_bin, source, project, sandbox):
    """The documented procedure ends with ``gov doctor``: on an updated project its lock part is a measured MATCH."""
    _second_release(source)
    _updated(copier_bin, sandbox, source, project)
    result = support.doctor(project, sandbox)
    assert result.claims_match and not result.reports_drift and result.section.get("status") == "pass", \
        f"gov doctor does not report MATCH on a project updated to the second release\n{result.describe()}"


# --------------------------------------------------------------------------
# The update procedure is documented
# --------------------------------------------------------------------------

def _documents():
    """The texts of this repository's files within the ticket's allowed paths (the tests' own folder left out)."""
    root = support.REPO_ROOT
    paths = [root / support.COPIER_YML_REL]
    paths += sorted((root / "template").glob("copier-answers*"))
    paths += sorted((root / "template" / "governance").glob("framework.lock*"))
    lock_code = root / "src" / "gov" / "lock"
    paths += sorted(path for path in lock_code.rglob("*") if path.suffix in (".py", ".md", ".yaml", ".yml", ".txt"))
    found = {}
    for path in paths:
        if path.is_file():
            found[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8", errors="replace")
    return found


def _answers_name():
    path = support.REPO_ROOT / support.COPIER_YML_REL
    if not path.is_file():
        return support.DEFAULT_ANSWERS_REL
    return support.Source(support.REPO_ROOT, support.Release(None, "")).answers_rel()


def test_the_update_procedure_is_documented_in_one_place():
    """One file of the ticket's paths states the procedure: the command, the answers file it works from, the check.

    DEC-023: the update is ``copier update``, and the answers file is never
    edited by hand; DEC-027: the manifest is verified at install and update,
    which is ``gov doctor`` (CAP-02).
    """
    documents = _documents()
    assert documents, (
        "no file of the ticket's paths exists yet (copier.yml, template/copier-answers*, "
        "template/governance/framework.lock*, src/gov/lock/**): the update procedure is documented nowhere"
    )
    needed = ("copier update", Path(_answers_name()).name, "gov doctor")
    complete = [rel for rel, text in documents.items() if all(word in text for word in needed)]
    assert complete, (
        f"none of {sorted(documents)} states the update procedure: each lacks one of {list(needed)} "
        f"(the command, the answers file that is never edited by hand, the check that follows)"
    )
