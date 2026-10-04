"""KPI success 4: the corpus is the whole tracked repository minus what the secret filter and the path map exclude;
there is no hand-kept include list [CAP-03.d].

"What the path map excludes" is a namespace whose ``memory_class`` is not ``governance``; the secret filter
``gov.secrets.indexable`` already drops both kinds (DEC-285). Each test changes the repository, never a
configuration of the index, and sees the corpus follow.
"""

from __future__ import annotations

import shutil

import pytest

import w1_17_support as support


def _found(api, root, query):
    return support.places(api.search(root, query))


def test_the_secret_filter_lets_the_fixture_corpus_through_and_nothing_else(caller, base, tmp_path):
    """The premise of this suite, and it passes before W1-17: it asks W1-15's filter, not the index. Every corpus
    file of the fixture is one an indexer may read; the product-data file and the two planted secrets are not."""
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine")
    root = support.clone(base, tmp_path / "repo")
    planted = [support.write(root, f"notes/planted-{kind}.md", f"# Notes\n\n{secret}\n")
               for kind, secret in support.SECRETS.items()]
    asked = [*support.CORPUS, support.PRODUCT_FILE, *planted]
    allowed = caller.call("indexable", root, asked, module="gov.secrets")
    assert allowed == list(support.CORPUS)


def test_every_tracked_governance_file_is_indexed_whatever_its_folder_or_extension(api, indexed):
    """Markdown, Python, TypeScript, JSON, a Makefile and a file with no extension, at the root and four folders
    deep: all in. Only tracked files are in."""
    first = set(indexed.report["indexed"])
    missing = sorted(set(support.CORPUS) - first)
    assert not missing, f"tracked governance files were not indexed: {missing}"
    assert support.PRODUCT_FILE not in first, "a product-data file was indexed"
    stray = sorted(first - set(support.tracked(indexed.root)))
    assert not stray, f"the index holds paths git does not track: {stray}"
    with_chunks = {record["path"] for record in api.chunks(indexed.root)}
    assert set(support.CORPUS) <= with_chunks, f"no chunk for: {sorted(set(support.CORPUS) - with_chunks)}"
    assert support.PRODUCT_FILE not in with_chunks


def test_a_new_tracked_file_under_a_new_folder_is_indexed_with_no_configuration_change(api, repo):
    """No include list: a folder and an extension nothing has named before are in the corpus once tracked."""
    api.refresh(repo)
    new = support.write(repo, "notes/new-area/2026/q4/finding.rst", "Title\n=====\n\nThe vermilion heron result.\n")
    support.commit(repo, "a new folder")
    assert _found(api, repo, "vermilion heron") == [(new, 4)]


def test_an_untracked_or_ignored_file_is_not_indexed(api, repo):
    support.write(repo, "notes/draft.md", "An untracked ochre falcon draft.\n")
    support.write(repo, "scratch-local/note.md", "An ignored ochre falcon note.\n")
    report = api.refresh(repo)
    assert not {"notes/draft.md", "scratch-local/note.md"} & set(report["indexed"]), report["indexed"]
    assert _found(api, repo, "ochre falcon") == []


def test_a_file_in_a_product_namespace_is_not_indexed(api, indexed):
    assert support.places(api.search(indexed.root, support.PRODUCT_WORD, refresh=False)) == []
    assert not support.files_holding(indexed.root / support.RUNTIME_REL, [support.PRODUCT_WORD]), \
        "product data stands in the store"


def test_the_path_map_decides_what_is_product_data(api, repo):
    """The file and its folder are unchanged; the map now classes the namespace as governance memory, and the
    notes as product data. The corpus follows the map both ways."""
    assert _found(api, repo, support.PRODUCT_WORD) == []
    assert _found(api, repo, support.TWIN) == support.occurrences(support.TWIN)
    namespaces = dict(support.NAMESPACES)
    namespaces["tenant-exports"] = (["tenant-exports/**"], "governance")
    namespaces["notes"] = (["notes/**"], "product")
    support.set_namespaces(repo, namespaces)
    support.commit(repo, "the map changes")
    assert _found(api, repo, support.PRODUCT_WORD) == [(support.PRODUCT_FILE, 3)]
    assert _found(api, repo, support.TWIN) == [(support.TWINS[1], 2)], "a file the map now excludes is still returned"


@pytest.mark.parametrize("kind", list(support.SECRETS))
def test_a_file_with_a_secret_is_not_indexed_and_the_secret_is_in_no_store(api, repo, kind):
    """The whole file is left out, its other lines too; a neighbour without a secret stays."""
    planted = support.write(repo, "notes/planted.md",
                            f"# Notes\n\nThe amber gull line.\n\n{support.SECRETS[kind]}\n\nNothing else.\n")
    neighbour = support.write(repo, "notes/neighbour.md", "# Notes\n\nThe amber gull line.\n")
    support.commit(repo, "two more notes")
    report = api.refresh(repo)
    assert planted not in report["indexed"], f"a file holding a {kind} was indexed"
    assert _found(api, repo, "amber gull") == [(neighbour, 3)]
    left = support.files_holding(repo / support.RUNTIME_REL, [support.SECRET_NEEDLES[kind]])
    assert not left, f"the {kind} stands in the derived store: {sorted(left)}"


def test_a_file_that_gains_a_secret_leaves_the_index(api, repo):
    """Indexed while clean; an edit adds a canary. Its earlier text is no longer returned and the store is clean."""
    rel = support.write(repo, "notes/rotating.md", "# Notes\n\nThe cobalt wren line.\n")
    support.commit(repo, "a clean note")
    assert _found(api, repo, "cobalt wren") == [(rel, 3)]
    support.write(repo, rel, f"# Notes\n\nThe cobalt wren line.\n\n{support.CANARY}\n")
    support.commit(repo, "the note gains a canary", date="2026-09-03T12:00:00+00:00")
    assert _found(api, repo, "cobalt wren") == []
    assert not support.files_holding(repo / support.RUNTIME_REL, [support.CANARY]), "the canary stands in the store"
