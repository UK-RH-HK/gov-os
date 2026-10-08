"""KPI failure 1: an overlay file is overwritten by ``copier update``.
KPI success 2, second half: the update procedure is documented.

The overlay is ``governance/project/`` (ADR-0002 section 5; DEC-023: overlay
files are listed in ``_skip_if_exists``). The template ships one file there, a
path map, which an update never overwrites (DEC-493). A later release is made
in the temporary template repository: a second commit and the tag ``v0.2.0``.
No tag is made in this repository.

The update procedure is documented in two places that reach a product
repository (DEC-488): the template's messages after copy and after update,
which Copier prints when it runs, and a comment header of the generated lock.
"""

from __future__ import annotations

import pytest

import w1_39_support as support

OVERLAY_FILES = ("governance/project/policies/local.yaml", "governance/project/notes/local.md")
PROJECT_TEXT = "owner: the project\nvalue: 1\n"
TEMPLATE_V1_TEXT = "owner: the template\nvalue: 1\n"
TEMPLATE_V2_TEXT = "owner: the template\nvalue: 2\nadded: by the second release\n"


def _a_hook(source):
    hooks = source.plain_files(support.HOOKS_REL)
    assert hooks, "the template source has no hook"
    return sorted(hooks)[0]


def _second_release(source, overlay=(), path_map=None):
    """The second release: one kernel file changed, one added, the template's own text for ``overlay`` files, and
    ``path_map`` as the path map it ships when one is given."""
    changed = _a_hook(source)
    with open(source.template / changed, "ab") as handle:
        handle.write(b"\n# changed by the second release\n")
    added = f"{support.KERNEL_REL}/w1_39_second_release.md"
    support.write_template_file(source, added, "added by the second release\n")
    for rel in overlay:
        support.write_template_file(source, rel, TEMPLATE_V2_TEXT)
    if path_map is not None:
        support.write_template_file(source, support.PATH_MAP_REL, path_map)
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


@pytest.mark.parametrize("state", ("edited by the project", "as the copy created it"))
def test_update_keeps_the_path_map_when_the_release_ships_a_different_one(copier_bin, source, project, sandbox, state):
    """The path map the copy created is the project's from then on: a release that ships another does not replace it.

    DEC-493: the template ships a minimal path map that an update never overwrites. Edited by the project or
    not, the file is byte for byte what it was before the update: no merge, no conflict mark, no reject file.
    """
    shipped = support.path_map_text(project)
    before = shipped
    if state == "edited by the project":
        before = support.edited_by_the_project(shipped)
        (project / support.PATH_MAP_REL).write_text(before, encoding="utf-8")
        support.commit_all(project, "the project's edit of its path map")
    later = support.shipped_by_a_later_release(shipped)
    assert later not in (shipped, before)
    _second_release(source, path_map=later)
    done = _updated(copier_bin, sandbox, source, project)
    assert (project / support.PATH_MAP_REL).read_text(encoding="utf-8") == before, \
        f"`copier update` changed {support.PATH_MAP_REL} ({state})\n{done.describe()}"
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

def _missing_from(text):
    """The words of the procedure that ``text`` lacks; line breaks and comment marks inside a phrase are passed over."""
    flat = " ".join(text.replace("#", " ").split())
    return [word for word in support.PROCEDURE_WORDS if word not in flat]


def test_copier_prints_the_update_procedure_after_a_copy(copy_run):
    """The template's message after copy states the procedure: Copier prints it when it creates a project.

    The procedure names ``copier update``, the answers file (never edited by hand, DEC-023), ``gov doctor``
    (the check that follows, CAP-02), and the adapter generation step, which the copy does not run (DEC-488).
    """
    missing = _missing_from(copy_run.printed)
    assert not missing, (
        f"what `copier copy` printed does not state the update procedure: it lacks {missing} "
        f"(of {list(support.PROCEDURE_WORDS)})\n{copy_run.describe()}"
    )


def test_copier_prints_the_update_procedure_after_an_update(copier_bin, source, project, sandbox):
    """The template's message after update states the procedure: Copier prints it when it updates a project."""
    _second_release(source)
    done = _updated(copier_bin, sandbox, source, project)
    missing = _missing_from(done.printed)
    assert not missing, (
        f"what `copier update` printed does not state the update procedure: it lacks {missing} "
        f"(of {list(support.PROCEDURE_WORDS)})\n{done.describe()}"
    )


def test_the_generated_lock_states_the_update_procedure_in_its_comment_header(installed):
    """The lock of a created project begins with a comment header that states the procedure."""
    header = support.lock_header(installed)
    assert header.strip(), f"{support.LOCK_REL} of the created project has no comment header"
    missing = _missing_from(header)
    assert not missing, (
        f"the comment header of {support.LOCK_REL} does not state the update procedure: it lacks {missing} "
        f"(of {list(support.PROCEDURE_WORDS)})\nheader:\n{header}"
    )
    assert support.manifest_of(installed), f"{support.LOCK_REL} with its header is no longer a lock with a manifest"


def test_the_lock_keeps_its_comment_header_after_an_update(copier_bin, source, project, sandbox):
    """The lock is written again by an update; the procedure is still at its head."""
    _second_release(source)
    _updated(copier_bin, sandbox, source, project)
    missing = _missing_from(support.lock_header(project))
    assert not missing, f"after an update the comment header of {support.LOCK_REL} lacks {missing}"
