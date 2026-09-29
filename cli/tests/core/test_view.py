import subprocess

import pytest

import repobuilder  # flat import: tests/core/conftest.py puts tests/fixtures/core/ on sys.path
from govbridge.core import view as viewmod

write_canonical_view = repobuilder.write_canonical_view


def test_resolve_view_named_refs_and_history(fixture_repo, view_path):
    cfg = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(cfg, repo=str(fixture_repo.root))
    assert resolved.named["records"].commit == fixture_repo.c3_moved
    assert resolved.named["product"].commit == fixture_repo.product_pin
    assert resolved.named["product"].status == viewmod.REF_OK
    assert resolved.named["evidence"].commit == fixture_repo.evidence_pin
    hist_names = {n for n, _ in resolved.history}
    assert hist_names == set(fixture_repo.history_refs)


def test_ref_moved_is_detected_for_a_pinned_ref_whose_branch_advanced(fixture_repo, tmp_path):
    # pin "evidence" to c1, but the evidence branch (built by repobuilder) now points at c2: a moved branch.
    p = tmp_path / "moved-view.yaml"
    write_canonical_view(p, fixture_repo, evidence_pin=fixture_repo.c1)
    cfg = viewmod.load_view(str(p))
    resolved = viewmod.resolve_view(cfg, repo=str(fixture_repo.root))
    assert resolved.named["evidence"].status == viewmod.REF_MOVED
    assert resolved.named["evidence"].commit == fixture_repo.c1  # pinned commit is followed, never the moved tip
    assert resolved.named["evidence"].current_tip == fixture_repo.c2


def test_partition_for_uses_dynamic_product_code_and_catch_all(fixture_repo, view_path):
    cfg = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(cfg, repo=str(fixture_repo.root))
    assert resolved.partition_for("runtime/src/init.rs").name == "product"
    assert resolved.partition_for("docs/NOTES.md").name == "records"
    assert resolved.partition_for("bin/anything").name == "product"  # PRODUCT_CODE included "bin"


def test_extract_top_level_str_list_is_generic():
    src = 'X = ["a", "b", "c"]\nY = 3\n'
    assert viewmod.extract_top_level_str_list(src, "X") == ["a", "b", "c"]
    with pytest.raises(ValueError):
        viewmod.extract_top_level_str_list(src, "MISSING")


def test_classify_occurrence_canonical_for_the_owning_commit(fixture_repo, view_path):
    cfg = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(cfg, repo=str(fixture_repo.root))
    c = resolved.classify_occurrence("runtime/src/init.rs", fixture_repo.product_pin)
    assert c.status == viewmod.VS_CANONICAL
    assert c.canonical_ref == "product"


def test_classify_occurrence_historical_when_blob_differs_from_canonical(fixture_repo, view_path):
    cfg = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(cfg, repo=str(fixture_repo.root))
    # docs/NOTES.md is owned by "records"; its canonical blob is the records tip's (c3_moved) content, which
    # differs from the content at c1.
    c = resolved.classify_occurrence("docs/NOTES.md", fixture_repo.c1)
    assert c.status == viewmod.VS_HISTORICAL_VERSION
    assert c.canonical_ref == "records"


def test_classify_occurrence_same_as_canonical_when_blob_matches(fixture_repo, view_path):
    cfg = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(cfg, repo=str(fixture_repo.root))
    # runtime/src/init.rs never changes between c1 and c2/c3 in the fixture, so a records-tip occurrence of it
    # (a non-owner ref, since "product" owns runtime/**) has the same blob as the canonical (product) copy.
    c = resolved.classify_occurrence("runtime/src/init.rs", fixture_repo.c3_moved)
    assert c.status == viewmod.VS_SAME_AS_CANONICAL
    assert c.canonical_ref == "product"


def test_classify_occurrence_history_only_for_a_path_that_exists_only_on_a_history_tip(fixture_repo, view_path):
    root = str(fixture_repo.root)
    # a detached commit, built ON TOP of the product-pinned commit so it never touches (or advances) "records",
    # "product" or "evidence" -- the only ref that will ever carry this path is the history tip we force below.
    subprocess.run(["git", "-C", root, "checkout", "-q", "--detach", fixture_repo.product_pin], check=True)
    repobuilder.write(fixture_repo.root, "only/in/history.txt", "only here\n")
    new_commit = repobuilder._commit(fixture_repo.root, "add history-only file")
    hist_branch = fixture_repo.history_refs[0].replace("refs/heads/", "")
    subprocess.run(["git", "-C", root, "branch", "-f", hist_branch, new_commit], check=True)
    subprocess.run(["git", "-C", root, "checkout", "-q", "records"], check=True)

    cfg = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(cfg, repo=root)
    assert resolved.named["records"].commit == fixture_repo.c3_moved  # untouched by the above
    c = resolved.classify_occurrence("only/in/history.txt", new_commit)
    assert c.status == viewmod.VS_HISTORY_ONLY
    assert c.canonical_commit == new_commit
