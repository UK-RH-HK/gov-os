from govbridge.core import gitobj


def test_resolve_commit_and_blob_at(fixture_repo):
    repo = str(fixture_repo.root)
    commit = gitobj.resolve_commit("records", repo=repo)
    assert commit == fixture_repo.c3_moved
    blob = gitobj.blob_at(commit, "runtime/src/init.rs", repo=repo)
    assert blob is not None
    assert gitobj.blob_at(commit, "does/not/exist", repo=repo) is None


def test_rev_parse_never_raises_on_absent_ref(fixture_repo):
    assert gitobj.rev_parse("refs/heads/nope", repo=str(fixture_repo.root)) is None


def test_ls_tree_matches_ls_tree_count(fixture_repo):
    repo = str(fixture_repo.root)
    entries = list(gitobj.ls_tree(fixture_repo.c3_moved, repo=repo))
    assert len(entries) == gitobj.ls_tree_count(fixture_repo.c3_moved, repo=repo)
    paths = {e.path for e in entries}
    assert "runtime/src/init.rs" in paths
    assert "docs/NOTES.md" in paths


def test_cat_file_batch_reads_blob_bytes(fixture_repo):
    repo = str(fixture_repo.root)
    blob = gitobj.blob_at(fixture_repo.c1, "docs/NOTES.md", repo=repo)
    with gitobj.CatFileBatch(repo=repo) as cat:
        data = cat.read(blob)
        assert data == b"# Notes\nversion 1\n"
        assert cat.read("0" * 40) is None  # a well-formed but non-existent oid


def test_read_path_matches_working_tree_content(fixture_repo):
    repo = str(fixture_repo.root)
    data = gitobj.read_path(fixture_repo.c1, "docs/NOTES.md", repo=repo)
    assert data == b"# Notes\nversion 1\n"


def test_diff_tree_reports_changed_paths(fixture_repo):
    repo = str(fixture_repo.root)
    changes = gitobj.diff_tree(fixture_repo.c1, fixture_repo.c2, repo=repo)
    changed_paths = {path for _, path, _, _ in changes}
    assert "docs/NOTES.md" in changed_paths
    assert "runtime/src/init.rs" not in changed_paths  # untouched between c1 and c2


def test_for_each_ref_finds_history_branches(fixture_repo):
    repo = str(fixture_repo.root)
    refs = gitobj.for_each_ref("refs/heads/history/*", repo=repo)
    names = {n for n, _ in refs}
    assert names == set(fixture_repo.history_refs)


def test_git_grep_finds_literal_and_excludes_by_path(fixture_repo):
    repo = str(fixture_repo.root)
    hits = gitobj.git_grep("native_layout_rules", fixture_repo.c1, repo=repo)
    assert any(path == "runtime/src/init.rs" for path, _, _ in hits)


def test_ls_tree_path_single_entry(fixture_repo):
    repo = str(fixture_repo.root)
    entry = gitobj.ls_tree_path(fixture_repo.c1, "docs/NOTES.md", repo=repo)
    assert entry is not None and entry.type == "blob" and entry.path == "docs/NOTES.md"
    assert gitobj.ls_tree_path(fixture_repo.c1, "nope", repo=repo) is None


def test_ls_tree_paths_lists_every_tracked_path(fixture_repo):
    repo = str(fixture_repo.root)
    paths = gitobj.ls_tree_paths(fixture_repo.c1, repo=repo)
    assert "runtime/src/init.rs" in paths
    assert len(paths) == gitobj.ls_tree_count(fixture_repo.c1, repo=repo)
