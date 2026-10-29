"""W2-69 (K3): deleted text does not survive a rebuild.

Success: "Deleted text does not survive a rebuild: after a full rebuild, text
deleted from a SQLite store is in neither its rows nor its free pages, so a secret
removed from the sources leaves no residue the check would find, or miss [DEC-897
item 1]." It covers every SQLite store a rebuild writes: the record store with its
lexical and semantic indexes, and the code-graph store the code-graph tool builds.

Failure: "Deleted text left in a store's free pages after a rebuild."

Every case runs ``gov rebuild --json`` (a full rebuild, never ``--no-embeddings``)
in a temporary project of its own, with this worktree's code. The semantic index is
built against a stand-in embedder on a loopback port (vectors from a hash of each
text, 1,024 floats each, as the pinned model's), so it is rebuilt and its deleted
vectors free pages, with no model and no network; the runner's user site is given
to the rebuild so that ``sqlite_vec`` is found under the temporary HOME. The cases
that do not need the code-graph store hide the code-graph tool from PATH, so no
daemon starts and they can run beside other suites; the one case of the code-graph
store needs the tool, skips without it, and runs alone (README).
"""

from __future__ import annotations

import importlib.util
import shutil

import pytest

import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
PAGES = 40
KEPT = 5          # pages 0..4 stay; the rest are deleted between the two rebuilds
WORD = support.marker("gonewordalpha")
ADDED_VALUE = "zqxw" + "69added" + "604217"
ADDED_RULE = ('\n[[rules]]\nid = "w2-69-added"\ndescription = "A rule the W2-69 test adds after the rebuild"\n'
              "regex = '''zqxw69added[0-9]{6}'''\nkeywords = [\"zqxw69added\"]\n")

needs_vectors = pytest.mark.skipif(importlib.util.find_spec("sqlite_vec") is None,
                                   reason="sqlite_vec is not installed: the semantic index cannot be built")


def _files(word_page=7, word=WORD):
    files = {f"docs/page{n:02d}.md": f"# Page {n}\n\n" + support.prose(4000, f"page{n}")
             + (f"\nThe word {word} is on this page.\n" if n == word_page else "") for n in range(PAGES)}
    files["src/app.py"] = (f"def {WORD}_handler():\n    return 1\n\n\ndef keeper():\n    return {WORD}_handler()\n")
    return files


@pytest.fixture()
def embedder():
    stand_in = support.EmbedderStandIn()
    yield stand_in
    stand_in.close()


def _sqlite_report(project):
    return {str(path.relative_to(project)): support.free_pages(path) for path in support.sqlite_files(project / R)}


def _assert_rebuilt(run, what, code=False):
    assert support.store_status(run, "lexical") == "recreated", f"{what}: the lexical index was not recreated"
    assert support.store_status(run, "semantic") == "recreated", (
        f"{what}: the semantic index was not recreated against the stand-in embedder\n{run.describe()}")
    if code:
        assert support.store_status(run, "codeintel") == "recreated", (
            f"{what}: the code-graph store was not recreated\n{run.describe()}")


@needs_vectors
def test_after_a_full_rebuild_no_sqlite_store_has_a_free_page(sandbox, embedder):
    project = support.make_rebuild_project(sandbox, _files())
    env = support.rebuild_environment(sandbox, embedder, with_code_tool=False)
    first = support.rebuild(project, env)
    _assert_rebuilt(first, "the first rebuild")
    stores = _sqlite_report(project)
    assert f"{R}/store.db" in stores, f"premise: the rebuild wrote the record store: {sorted(stores)}"
    assert all(count == 0 for count in stores.values()), f"after the first rebuild, free pages: {stores}"
    for n in range(KEPT, PAGES):
        (project / f"docs/page{n:02d}.md").unlink()
    support.commit_all(project, "most pages deleted")
    second = support.rebuild(project, env)
    _assert_rebuilt(second, "the rebuild after the deletion")
    stores = _sqlite_report(project)
    assert all(count == 0 for count in stores.values()), (
        f"after a full rebuild that followed the deletion of {PAGES - KEPT} of {PAGES} pages, SQLite stores still "
        f"hold free pages (not compacted): { {rel: n for rel, n in stores.items() if n} }")


@needs_vectors
def test_a_word_deleted_from_the_sources_is_in_no_store_after_the_next_rebuild(sandbox, embedder):
    project = support.make_rebuild_project(sandbox, _files())
    env = support.rebuild_environment(sandbox, embedder, with_code_tool=False)
    _assert_rebuilt(support.rebuild(project, env), "the first rebuild")
    forms = support.word_forms(WORD)
    assert support.files_holding(project / R, forms), "premise: the word reached the stores at the first rebuild"
    assert any(support.fts_terms_holding(path, WORD, sandbox.elsewhere) for path in support.sqlite_files(project / R)), \
        "premise: the word is a term of a full-text index after the first rebuild"
    (project / "docs/page07.md").unlink()
    support.write(project / "src/app.py", "def keeper():\n    return 2\n")
    support.commit_all(project, "the word deleted from the sources")
    _assert_rebuilt(support.rebuild(project, env), "the rebuild after the deletion")
    holding = support.files_holding(project / R, forms)
    terms = {str(path.relative_to(project)): support.fts_terms_holding(path, WORD, sandbox.elsewhere)
             for path in support.sqlite_files(project / R)}
    terms = {rel: found for rel, found in terms.items() if found}
    assert not holding, (
        f"a word deleted from the sources is still in the bytes of {holding} after a full rebuild (in rows, a "
        f"full-text index or free space)")
    assert not terms, f"a word deleted from the sources is still a term of a full-text index after a rebuild: {terms}"


@needs_vectors
def test_a_secret_removed_from_the_sources_leaves_no_residue_the_check_finds(sandbox, embedder):
    """The value is no secret at the first rebuild, so it is indexed; it is deleted; after the next rebuild a rule
    that finds it is added: the check must be green, since nothing of it may be left."""
    files = _files(word=ADDED_VALUE)
    project = support.make_rebuild_project(sandbox, files)
    env = support.rebuild_environment(sandbox, embedder, with_code_tool=False)
    _assert_rebuilt(support.rebuild(project, env), "the first rebuild")
    assert support.files_holding(project / R, [ADDED_VALUE.encode(), ADDED_VALUE.lower().encode()]), (
        "premise: the value reached the stores at the first rebuild")
    rules = support.template_text() + ADDED_RULE
    assert "w2-69-added" in support.gitleaks_finds(f" {ADDED_VALUE} \n", rules), "premise: the added rule finds it"
    (project / "docs/page07.md").unlink()
    support.commit_all(project, "the value deleted from the sources")
    _assert_rebuilt(support.rebuild(project, env), "the rebuild after the deletion")
    with open(project / ".gitleaks.toml", "a", encoding="utf-8") as handle:
        handle.write(ADDED_RULE)
    run = support.run_check(sandbox, project, env=support.base_environment(sandbox))
    assert run.returncode == 0, (
        f"a value removed from the sources before the last full rebuild left a residue the check finds once a rule "
        f"names it\n{run.describe()}")


@pytest.mark.skipif(support.CODE_TOOL is None, reason="codebase-memory-mcp is not on PATH: no code-graph store")
@needs_vectors
def test_the_code_graph_store_holds_no_deleted_word_and_no_free_page_after_a_rebuild(sandbox, embedder):
    """Runs the code-graph tool's daemon: one of the cases that run alone (README)."""
    project = support.make_rebuild_project(sandbox, _files())
    env = support.rebuild_environment(sandbox, embedder, with_code_tool=True)
    daemon = support.code_daemon_dir(project)
    try:
        _assert_rebuilt(support.rebuild(project, env), "the first rebuild", code=True)
        graph = project / R / "codeintel"
        code_stores = [path for path in support.sqlite_files(graph)]
        assert code_stores, "premise: the code-graph tool wrote a SQLite store under .gov-runtime/codeintel/"
        forms = support.word_forms(WORD)
        assert support.files_holding(graph, forms), "premise: the word reached the code-graph store"
        (project / "docs/page07.md").unlink()
        support.write(project / "src/app.py", "def keeper():\n    return 2\n")
        for n in range(KEPT, PAGES):
            if n != 7:
                (project / f"docs/page{n:02d}.md").unlink()
        support.commit_all(project, "the word and most pages deleted")
        _assert_rebuilt(support.rebuild(project, env), "the rebuild after the deletion", code=True)
        stores = _sqlite_report(project)
        assert all(count == 0 for count in stores.values()), (
            f"after a full rebuild, SQLite stores hold free pages: { {r: n for r, n in stores.items() if n} }")
        holding = support.files_holding(project / R, forms)
        assert not holding, f"a word deleted from the sources is still in {holding} after a full rebuild"
    finally:
        if daemon is not None and daemon.is_dir():
            shutil.rmtree(daemon, ignore_errors=True)
