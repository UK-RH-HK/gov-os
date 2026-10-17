"""KPI success 1, 2, 3 (the release side) and 5: `gov release <version>` and the record it builds.

Every release is built in a stand-in Gov OS repository in a temporary folder (``w2_16_support``), never in this
repository; its tags are made by the test, unsigned, standing for the owner.
"""

from __future__ import annotations

import json
import subprocess

import pytest
import yaml

import w2_16_support as support


@pytest.fixture(params=("first", "second"))
def record(request, releases):
    return getattr(releases, request.param)


# --------------------------------------------------------------------------
# KPI success 1 [CAP-43.b lite]: the release and its manifest
# --------------------------------------------------------------------------

def test_a_release_writes_its_record_under_docs_releases_and_changes_nothing_else(record):
    """The record is under docs/releases/; no tracked or untracked path outside it is touched (allowed paths)."""
    assert record.record_files and all(support.under(rel, support.RELEASES_REL) for rel in record.record_files), \
        record.describe()
    outside = [rel for rel in record.dirty_after_run if not support.under(rel, support.RELEASES_REL)]
    assert not outside, f"`gov release` left changes outside {support.RELEASES_REL}/: {outside}"


def test_the_manifest_holds_the_semantic_version(record):
    assert record.version in support.scalars(record.manifest), \
        f"the manifest does not hold the version {record.version}\n{record.describe()}"


def test_the_manifest_holds_the_full_commit_the_release_was_built_from(record):
    """The commit in full (40 hex digits): the clean w2/integrate commit `gov release` ran on."""
    assert record.built_from in support.scalars(record.manifest), (
        f"the manifest does not hold the full id of the commit it was built from, {record.built_from}\n"
        f"{record.describe()}")


def test_the_manifest_lists_every_shipped_file_with_its_sha256(record):
    """Every file of template/ at the release's commit, with the sha256 of its bytes in that commit."""
    listed = support.file_hashes(record.manifest)
    shipped = support.shipped_files(record.repo, record.built_from)
    wrong = [(rel, sorted(listed.get(rel, ())), digest) for rel, digest in sorted(shipped.items())
             if digest not in listed.get(rel, ())]
    assert shipped and not wrong, (
        f"{len(wrong)} of {len(shipped)} shipped files are absent from the manifest or listed with another hash "
        f"(path, listed, sha256): {wrong[:5]}\n{record.describe()}")


def test_the_second_release_lists_the_shipped_file_that_changed_with_its_new_hash(releases):
    """The two manifests differ where the shipped bytes differ: each release hashes its own commit."""
    rel = support.normalise_path(support.CHANGED_BY_SECOND_RELEASE)
    first = support.file_hashes(releases.first.manifest).get(rel, set())
    second = support.file_hashes(releases.second.manifest).get(rel, set())
    assert first and second and not (first & second), \
        f"{rel} changed between the releases; first manifest lists {first}, second lists {second}"


def test_the_manifest_holds_the_wheel_hash(record):
    """A sha256 under a key that names the wheel; a wheel file the record holds has that hash."""
    hashes = {str(leaf).lower() for trail, leaf in support.walk(record.manifest)
              if any("wheel" in key.lower() or key.lower().endswith(".whl") for key in trail)
              and isinstance(leaf, str) and support.SHA256_RE.fullmatch(leaf.strip().lower())}
    assert hashes, f"the manifest holds no sha256 under a key that names the wheel\n{record.describe()}"
    wheels = {rel: support.sha256_bytes(data) for rel, data in record.record_files.items() if rel.endswith(".whl")}
    wrong = {rel: digest for rel, digest in wheels.items() if digest not in hashes}
    assert not wrong, f"wheel files of the record whose sha256 the manifest does not give: {wrong}"


def test_the_manifest_holds_the_cli_version(record):
    """The version the release commit's pyproject.toml declares for the gov command line."""
    assert support.STAND_IN_CLI_VERSION in support.scalars(record.manifest), (
        f"the manifest does not hold the CLI version {support.STAND_IN_CLI_VERSION} that the release commit's "
        f"pyproject.toml declares\n{record.describe()}")


def test_the_manifest_holds_the_schema_versions(record):
    """A part of the manifest named for schemas (not a file path) names every kernel schema, each with a value."""
    names = sorted(rel.rsplit("/", 1)[-1] for rel in support.shipped_files(record.repo, record.built_from)
                   if rel.startswith(support.SCHEMAS_REL + "/") and rel.endswith(".schema.json"))
    assert names, "the release commit ships no kernel schema"
    parts = [value for entry in support.dicts_in(record.manifest) for key, value in entry.items()
             if "schema" in str(key).lower() and "/" not in str(key) and not str(key).endswith(".json") and value]
    text = json.dumps(parts, default=str)
    missing = [name for name in names if name.removesuffix(".schema.json") not in text]
    assert parts and not missing, (
        f"the manifest's schema versions do not name {missing or names} (no non-empty part under a key that "
        f"names schemas, or schemas absent from it)\n{record.describe()}")


def test_the_manifest_holds_release_notes(record):
    notes = [value for entry in support.dicts_in(record.manifest) for key, value in entry.items()
             if "note" in str(key).lower() and support.collapse(json.dumps(value, default=str)).strip('"[]{} ')]
    assert notes, f"the manifest holds no release notes (a non-empty value under a key that names notes)\n" \
                  f"{record.describe()}"


def test_the_manifest_s_own_hash_is_in_the_record_and_a_reader_finds_it_equal(record):
    """The sha256 of the manifest's bytes is stated in the record beside it; recomputing it gives the same."""
    stated = [rel for rel, data in record.record_files.items()
              if rel != record.manifest_rel and record.manifest_hash.encode() in data]
    assert stated, (
        f"no file of the record beside the manifest states the manifest's sha256 {record.manifest_hash}\n"
        f"{record.describe()}")


# --------------------------------------------------------------------------
# KPI success 1, the failure side: no release from an unclean tree, another branch, or a bad version
# --------------------------------------------------------------------------

def _assert_refused_and_nothing_written(repo, sandbox, version, why):
    before = support.snapshot(repo)
    run = support.run_gov(repo, sandbox, "release", *((version,) if version is not None else ()))
    after = support.snapshot(repo)
    assert run.returncode != 0, f"`gov release` built a release although {why}\n{run.describe()}"
    assert "Traceback" not in run.output, f"`gov release` ended with a traceback where {why}\n{run.describe()}"
    changed = support.snapshot_difference(before, after)
    assert not changed, f"a refused release ({why}) wrote or changed: {changed[:10]}\n{run.describe()}"
    return run


def _dirty(repo, how):
    if how == "a tracked file changed":
        support.append_one_byte(repo / support.TAMPERED_REL)
    elif how == "a change staged":
        support.append_one_byte(repo / "pyproject.toml")
        support.git(repo, "add", "pyproject.toml")
    elif how == "an untracked file":
        (repo / "notes-in-progress.txt").write_text("not committed\n", encoding="utf-8")
    elif how == "an untracked file in the template":
        (repo / support.ADDED_REL).write_text("{}\n", encoding="utf-8")
    assert support.porcelain_paths(repo), f"this case needs a tree with {how}"


@pytest.mark.parametrize("how", ("a tracked file changed", "a change staged", "an untracked file",
                                 "an untracked file in the template"))
def test_no_release_from_a_tree_with_uncommitted_or_untracked_changes(releases, repo, sandbox, how):
    """Refused, and nothing written. (`releases` shows the same stand-in releases once its tree is clean.)"""
    _dirty(repo, how)
    _assert_refused_and_nothing_written(repo, sandbox, support.FIRST_VERSION, f"the tree has {how}")


@pytest.mark.parametrize("how", ("another branch", "a detached commit"))
def test_no_release_from_a_commit_that_is_not_on_w2_integrate(releases, repo, sandbox, how):
    """A clean commit that w2/integrate does not contain: refused, nothing written."""
    if how == "another branch":
        support.git(repo, "checkout", "-q", "-b", "w2/W2-99")
    else:
        support.git(repo, "checkout", "-q", "--detach")
    (repo / support.CHANGED_BY_SECOND_RELEASE).write_text("not on the integration branch\n", encoding="utf-8")
    support.commit_all(repo, "a commit off the integration branch")
    contained = support.git(repo, "branch", "--list", "--contains", "HEAD", support.INTEGRATION_BRANCH).strip()
    assert not contained and not support.porcelain_paths(repo), "this case needs a clean commit off w2/integrate"
    _assert_refused_and_nothing_written(repo, sandbox, support.FIRST_VERSION,
                                        f"HEAD is on {how}, not on {support.INTEGRATION_BRANCH}")


@pytest.mark.parametrize("version", ("1.4", "1.4.0.0", "latest", "01.4.0", "1.4.0-", "1.4.x"))
def test_no_release_with_a_version_that_is_not_a_semantic_version(releases, repo, sandbox, version):
    _assert_refused_and_nothing_written(repo, sandbox, version, f"{version!r} is not a semantic version")


def test_no_release_without_a_version(releases, repo, sandbox):
    _assert_refused_and_nothing_written(repo, sandbox, None, "no version is given")


# --------------------------------------------------------------------------
# KPI success 2 (CAP-02.c stays in Wave 3, DEC-722): agents never tag, nothing is signed
# --------------------------------------------------------------------------

def test_building_a_release_creates_no_tag(record):
    assert record.tags_after_run == record.tags_before, (
        f"`gov release {record.version}` created tags: before {record.tags_before}, after "
        f"{record.tags_after_run} (the owner tags the release commit)")


def test_building_a_release_signs_nothing(record):
    """No signed commit, no signature file in the record (the release is pinned and hash-verified, not signed)."""
    signed = [commit for commit in record.commits_by_release
              if "gpgsig" in support.git(record.repo, "cat-file", "commit", commit)]
    assert not signed, f"`gov release {record.version}` made signed commits: {signed}"
    signatures = [rel for rel in record.record_files if rel.lower().endswith(support.SIGNATURE_SUFFIXES)]
    assert not signatures, f"the record of {record.version} holds signature files: {signatures}"


# --------------------------------------------------------------------------
# KPI success 3 [CAP-43]: a release is immutable
# --------------------------------------------------------------------------

@pytest.mark.parametrize("which", ("first", "second"))
def test_the_same_version_from_another_commit_is_refused_and_its_record_left_as_it_was(releases, release_repo,
                                                                                      sandbox, which):
    """A clean w2/integrate commit after the release: building that version again is refused; the existing
    record is byte for byte what it was (the snapshot holds every file, the record's among them)."""
    record = getattr(releases, which)
    (release_repo / support.CHANGED_BY_SECOND_RELEASE).write_text("a later change\n", encoding="utf-8")
    support.commit_all(release_repo, "a later integration commit")
    before = {rel: (release_repo / rel).read_bytes() for rel in record.record_files}
    assert before == record.record_files
    _assert_refused_and_nothing_written(release_repo, sandbox, record.version,
                                        f"release {record.version} already exists, built from another commit")


# --------------------------------------------------------------------------
# KPI success 5 [W2-L002, W2-L014]: the vendored skills' licence and version in the release
# --------------------------------------------------------------------------

def _vendored_version(record):
    text = subprocess.run(["git", "-C", str(record.repo), "show",
                           f"{record.built_from}:{support.TEMPLATE_REL}/{support.VENDORED_RECORD_REL}"],
                          capture_output=True, text=True, check=True).stdout
    version = str(yaml.safe_load(text)["version"])
    assert version and version != record.version
    return version


def test_the_release_holds_the_vendored_skills_version(record):
    """A part of the manifest gives the vendored skills' version (DEC-246's v6.4.2) beside their name."""
    version = _vendored_version(record)
    accepted = {version, version.removeprefix("v")}

    def names_them(text):
        return "superpowers" in text.lower() or all(skill in text for skill in support.VENDORED_SKILLS)

    by_trail = [trail for trail, leaf in support.walk(record.manifest)
                if isinstance(leaf, str) and leaf in accepted and names_them(" ".join(trail))]
    by_map = [entry for entry in support.dicts_in(record.manifest)
              if any(isinstance(value, str) and value in accepted for value in entry.values())
              and names_them(json.dumps(entry))]
    assert by_trail or by_map, (
        f"no part of the manifest gives the vendored skills' version {version} beside their name (superpowers "
        f"or the three skills)\n{record.describe()}")


def test_the_release_holds_the_vendored_skills_upstream_licence(record):
    """The upstream licence's text is in the record (a file of it, or a value of the manifest)."""
    licence = subprocess.run(["git", "-C", str(record.repo), "show",
                              f"{record.built_from}:{support.TEMPLATE_REL}/{support.VENDOR_LICENCE_REL}"],
                             capture_output=True, text=True, check=True).stdout
    wanted = support.collapse(licence)
    assert len(wanted) > 200
    in_files = [rel for rel, data in record.record_files.items()
                if wanted in support.collapse(data.decode("utf-8", "replace"))]
    in_values = [value for value in support.scalars(record.manifest) if wanted in support.collapse(value)]
    assert in_files or in_values, (
        f"the record of {record.version} does not hold the vendored skills' upstream licence "
        f"({support.VENDOR_LICENCE_REL}); today it is only in the vendor folder\n{record.describe()}")
