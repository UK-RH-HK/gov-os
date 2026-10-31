"""KPI success 3 [CAP-43] and success 1: release immutability, cases added from the first review of W2-16 (DEC-136).

A version is the same version wherever the repository already knows it (an older checkout, a record removed
later, an owner's tag), and whatever build metadata it carries; a release is built from the commit, never from
bytes the commit does not hold. Every repository is a temporary stand-in (``w2_16_support``); every tag here is
made by the case, unsigned, standing for the owner.
"""

from __future__ import annotations

import subprocess

import pytest

import w2_16_support as support


def _assert_refused_and_nothing_written(repo, sandbox, version, why):
    """As the release file's helper: refused, no traceback, the whole snapshot unchanged.

    **Rewritten (DEC-772, P-R3-A; Rewrite-Reason: DEC-772),** as the release file's helper: the call goes through
    the seam as the owner in person, and the refusal is held to be the build's own (``RELEASE_REFUSED``, the code
    accepted, a reason that is none of the caller checks'), not the caller checks' that DEC-772 put before it."""
    return support.assert_the_build_refuses(repo, sandbox, version, why)


def _tracked_at_head(repo, folder=support.RELEASES_REL):
    return [rel for rel in support.git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", folder).split("\n") if rel]


def _blob_sha256(repo, commit, rel):
    """The sha256 of ``rel`` as committed at ``commit`` (`git cat-file blob <commit>:<rel>`)."""
    data = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", f"{commit}:{rel}"], capture_output=True,
                          check=True).stdout
    return support.sha256_bytes(data)


# --------------------------------------------------------------------------
# Finding 1: the same version is refused wherever the repository already knows it
# --------------------------------------------------------------------------

@pytest.mark.parametrize("where", ("the first release's record commit", "the first release's own commit"))
def test_the_same_version_from_an_older_integration_commit_is_refused(releases, release_repo, sandbox, where):
    """HEAD detached at an older commit that w2/integrate contains, so the tree holds no record of the second
    release, which w2/integrate holds committed: building that version again is refused, nothing written."""
    record = releases.second
    older = releases.first.release_commit if where == "the first release's record commit" \
        else releases.first.built_from
    assert older != record.built_from
    support.git(release_repo, "checkout", "-q", "--detach", older)
    at_head = set(_tracked_at_head(release_repo))
    assert not (at_head & set(record.record_files)) and not support.porcelain_paths(release_repo), \
        f"this case needs a clean tree without the record of {record.version}"
    assert support.git(release_repo, "branch", "--list", "--contains", "HEAD", support.INTEGRATION_BRANCH).strip(), \
        f"this case needs a commit that {support.INTEGRATION_BRANCH} contains"
    _assert_refused_and_nothing_written(
        release_repo, sandbox, record.version,
        f"{support.INTEGRATION_BRANCH} holds release {record.version}'s record; HEAD is at {where}, older")


@pytest.mark.parametrize("which", ("first", "second"))
def test_the_same_version_after_its_record_was_removed_is_refused(releases, release_repo, sandbox, which):
    """The record of a release removed in a later commit on w2/integrate, then a new commit: building that version
    again is refused, nothing written (w2/integrate's history still holds the release)."""
    record = getattr(releases, which)
    support.git(release_repo, "rm", "-q", "--", *sorted(record.record_files))
    support.commit_all(release_repo, f"the record of release {record.version} removed")
    (release_repo / support.CHANGED_BY_SECOND_RELEASE).write_text("a change after the removal\n", encoding="utf-8")
    support.commit_all(release_repo, "a later integration commit")
    assert not (set(_tracked_at_head(release_repo)) & set(record.record_files)), \
        f"this case needs a tree without the record of {record.version}"
    assert support.git(release_repo, "log", "--format=%H", support.INTEGRATION_BRANCH, "--",
                       record.manifest_rel).strip(), "this case needs the record in w2/integrate's history"
    _assert_refused_and_nothing_written(
        release_repo, sandbox, record.version,
        f"release {record.version}'s record was committed on {support.INTEGRATION_BRANCH} and removed later")


@pytest.mark.parametrize("annotated", (False, True), ids=("lightweight tag", "annotated tag"))
def test_the_same_version_as_an_existing_owner_tag_is_refused(repo, sandbox, releases, annotated):
    """A tag v<version> already exists (the owner's, unsigned) and no record of that version is in the tree: building
    that version from a later w2/integrate commit is refused, nothing written. (`releases` shows the same pristine
    stand-in, with no such tag, releases this version.)"""
    version, tag = support.FIRST_VERSION, support.FIRST_TAG
    if annotated:
        support.git(repo, "tag", "-a", "-m", f"release {version}", tag)
    else:
        support.git(repo, "tag", tag)
    (repo / support.CHANGED_BY_SECOND_RELEASE).write_text("a later integration commit\n", encoding="utf-8")
    support.commit_all(repo, "a later integration commit")
    assert not _tracked_at_head(repo) and not support.porcelain_paths(repo), \
        "this case needs a clean tree with no release record"
    assert support.tags(repo) == [tag]
    _assert_refused_and_nothing_written(repo, sandbox, version,
                                        f"the tag {tag} already exists, on another commit")


# --------------------------------------------------------------------------
# Finding 4: build metadata does not make another version (semantic versioning: equal precedence)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("which", ("first", "second"))
def test_a_version_differing_only_by_build_metadata_from_a_recorded_one_is_refused(releases, release_repo,
                                                                                  sandbox, which):
    """`<V>+build.2` beside a recorded `<V>`, from a later clean w2/integrate commit: the same version, refused."""
    record = getattr(releases, which)
    (release_repo / support.CHANGED_BY_SECOND_RELEASE).write_text("a later change\n", encoding="utf-8")
    support.commit_all(release_repo, "a later integration commit")
    assert set(record.record_files) <= set(_tracked_at_head(release_repo))
    _assert_refused_and_nothing_written(
        release_repo, sandbox, f"{record.version}+build.2",
        f"release {record.version} exists and {record.version}+build.2 differs from it only by build metadata")


# --------------------------------------------------------------------------
# Finding 5: a release is built from the commit, never from bytes the commit does not hold
# --------------------------------------------------------------------------

@pytest.mark.parametrize("flag", ("--assume-unchanged", "--skip-worktree"))
def test_a_release_never_hashes_bytes_the_commit_does_not_hold(releases, repo, sandbox, flag):
    """A tracked template file edited and hidden from `git status` by `git update-index <flag>`: `gov release`
    either refuses and writes nothing, or its manifest gives that file the sha256 of its bytes at the commit
    (`git cat-file blob <commit>:template/<path>`), never the edited bytes' hash.

    **Rewritten (DEC-772, P-R3-A; Rewrite-Reason: DEC-772):** `gov release` ran as a child process, which DEC-772
    refuses before the build (its ancestry, its missing terminal), so the refusal branch passed whatever the build
    did. It now runs through the seam as the owner in person; the caller checks pass (the code accepted), and a
    refusal is held to be the build's own (`RELEASE_REFUSED`, a reason that is none of the caller checks'), with
    nothing written. The other branch is as it was."""
    rel = support.TAMPERED_REL
    commit = support.head(repo)
    committed = _blob_sha256(repo, commit, rel)
    support.append_one_byte(repo / rel)
    edited = support.sha256(repo / rel)
    support.git(repo, "update-index", flag, "--", rel)
    assert edited != committed and not support.porcelain_paths(repo), \
        f"this case needs an edited tracked file that `git status` does not show ({flag})"
    before = support.snapshot(repo)
    seam = support.release_through_the_seam(repo, sandbox, support.FIRST_VERSION)
    run = seam.as_run(support.FIRST_VERSION)
    support.assert_no_traceback(seam, flag)
    support.assert_the_code_was_accepted(seam, flag)
    if run.returncode != 0:
        assert seam.error.get("code") == support.RELEASE_REFUSED and seam.reason not in support.REASONS, (
            f"`gov release` was refused ({flag}), but not by the build's own rule: code {seam.error.get('code')!r}, "
            f"reason {seam.reason!r}\n{run.describe()}")
        changed = support.snapshot_difference(before, support.snapshot(repo))
        assert not changed, f"a refused release ({flag}) wrote or changed: {changed[:10]}\n{run.describe()}"
        return
    record = _record_left_by(repo, run, commit)
    listed = support.file_hashes(record.manifest).get(support.normalise_path(rel), set())
    assert edited not in listed, (
        f"the manifest of {support.FIRST_VERSION} gives {rel} the hash of bytes the commit {commit} does not hold "
        f"({flag} hid the edit): listed {sorted(listed)}, committed {committed}, edited {edited}\n{record.describe()}")
    assert listed == {committed}, (
        f"the manifest of {support.FIRST_VERSION} does not give {rel} the sha256 of its bytes at {commit}: listed "
        f"{sorted(listed)}, committed {committed}\n{record.describe()}")


def _record_left_by(repo, run, built_from):
    """The record a successful `gov release` left: files it committed after ``built_from`` and files it left
    uncommitted under docs/releases/ (read from disk), with its manifest found as the suite finds it."""
    after = support.head(repo)
    commits = support.git(repo, "rev-list", f"{built_from}..{after}").split()
    changed = set(support.git(repo, "diff", "--name-only", built_from, after).split())
    dirty = support.porcelain_paths(repo)
    changed |= {rel for rel in dirty if support.under(rel, support.RELEASES_REL)}
    files = {rel: (repo / rel).read_bytes() for rel in sorted(changed)
             if support.under(rel, support.RELEASES_REL) and (repo / rel).is_file()}
    assert files, f"`gov release` exited 0 and wrote no record under {support.RELEASES_REL}/\n{run.describe()}"
    record = support.ReleaseRecord(support.FIRST_VERSION, repo, run, built_from, after, [], support.tags(repo),
                                   commits, dirty, files)
    record.manifest_rel = support._find_manifest(record)
    return record
