"""Fix under W2-88: ``FABRIC_INCOMPLETE`` names each file a store judged and holds in neither list, and each it holds in both [S1].

Evidence (W2-81's proving run on release 0.1.4): A9 stopped with ``FABRIC_INCOMPLETE`` "vectors: 2 file(s) judged and in
neither list" and named no file. W2-88 S1: "every tracked file is either indexed or named with its reason": a refusal that
says only a count breaks it.

KPI line: ``FABRIC_INCOMPLETE`` names each file that a store judged and holds in neither list (the vectors store and the
code graph, as well as the keyword store) and each file it holds in both lists: the message lists the paths, and
``details`` carries them (``details["missing"]``: the sorted paths in neither list, over every store; ``details["both"]``:
the sorted paths in two lists), so no refusal says only a count.

The interface the lead decided: a store's block in the A9 record's ``stores`` carries ``judged_files``, the sorted list of
the files the store judged; ``fabric.check_coverage(record, tracked)`` names every judged file in neither ``indexed`` nor
``refused``, and every file in both; a block with no ``judged_files`` (an older record) keeps the count message and still
raises as before. The keyword store ("lexical") judges every tracked file and needs no ``judged_files``.
"""

from __future__ import annotations

import shutil

import pytest
import yaml

import w2_88_support as W

TRACKED = ("README.md", "docs/guide.md", "lib/util.py", "assets/logo.bin", "config/settings.env", "archive/old.md")


def block(indexed=(), refused=(), judged=None, judged_files=None, **more):
    """A store's block of the A9 record: ``refused`` are paths (each given the reason ``not-embedded``)."""
    held = {"judged": len(set(indexed) | set(refused)) if judged is None else judged, "indexed": list(indexed),
            "refused": [{"path": path, "reason": "not-embedded"} for path in refused], "chunks": 0, "vectors": 0,
            "nodes": 0, "edges": 0, "seconds": 0.0, "peak_rss_bytes": 0, **more}
    if judged_files is not None:
        held["judged_files"] = sorted(judged_files)
    return held


def record(*, vectors=None, codegraph=None, lexical=None):
    """A record whose stores each list every file they judge, unless the case gives a block of its own."""
    everything = sorted(TRACKED)
    stores = {
        "record": block(),
        "lexical": lexical or block(indexed=everything),
        "vectors": vectors or block(indexed=everything, judged_files=everything),
        "codegraph": codegraph or block(indexed=["lib/util.py"], judged_files=["lib/util.py"]),
    }
    return {"stores": stores}


def coverage(stores_record, tracked=TRACKED):
    """The refusal ``check_coverage`` raises for the record (a test fails when it raises nothing)."""
    from gov.adopt import fabric
    from gov.cli.errors import GovError
    with pytest.raises(GovError) as raised:
        fabric.check_coverage(stores_record, tracked)
    error = raised.value
    assert error.code == "FABRIC_INCOMPLETE", f"the refusal is {error.code}, not FABRIC_INCOMPLETE"
    return error


def said(error):
    return str(getattr(error, "message", None) or error)


# ---- unit seam: fabric.check_coverage on a hand-built record -----------------------------------------------------

def test_a_complete_record_that_names_its_judged_files_raises_nothing():
    """(d) The success side: every judged file is in exactly one list of its store: no refusal."""
    from gov.adopt import fabric
    assert fabric.check_coverage(record(), TRACKED) is None


def test_a_vectors_file_judged_and_in_neither_list_is_named_in_the_message_and_in_details():
    """(a) Vectors judged three files; one is indexed, one refused, the third in neither: it is named."""
    files = ["docs/guide.md", "lib/util.py", "README.md"]
    vectors = block(indexed=["README.md"], refused=["docs/guide.md"], judged=3, judged_files=files)
    error = coverage(record(vectors=vectors))
    assert error.details.get("missing") == ["lib/util.py"], f"details['missing'] is {error.details.get('missing')!r}"
    assert "lib/util.py" in said(error), f"the message names no file: {said(error)!r}"
    assert "README.md" not in said(error) and "docs/guide.md" not in said(error), \
        f"the message names files that are in a list: {said(error)!r}"


def test_two_files_in_neither_list_are_both_named_sorted():
    files = ["README.md", "docs/guide.md", "lib/util.py"]
    vectors = block(indexed=["README.md"], judged=3, judged_files=files)
    error = coverage(record(vectors=vectors))
    assert error.details.get("missing") == ["docs/guide.md", "lib/util.py"]
    assert all(path in said(error) for path in ("docs/guide.md", "lib/util.py")), said(error)


def test_a_code_graph_file_judged_and_in_neither_list_is_named():
    codegraph = block(indexed=["lib/util.py"], judged=2, judged_files=["lib/util.py", "lib/other.py"])
    lexical = block(indexed=sorted(TRACKED + ("lib/other.py",)))
    error = coverage(record(lexical=lexical, codegraph=codegraph), TRACKED + ("lib/other.py",))
    assert error.details.get("missing") == ["lib/other.py"], f"details['missing'] is {error.details.get('missing')!r}"
    assert "lib/other.py" in said(error), said(error)


def test_the_missing_paths_are_collected_over_every_store_and_sorted():
    """details['missing'] is over every store: the keyword store's gap and the vectors store's gap in one list."""
    everything = sorted(TRACKED)
    lexical = block(indexed=[path for path in everything if path != "docs/guide.md"])
    vectors = block(indexed=[path for path in everything if path != "README.md"], judged=len(everything),
                    judged_files=everything)
    error = coverage(record(lexical=lexical, vectors=vectors))
    assert error.details.get("missing") == ["README.md", "docs/guide.md"], f"{error.details.get('missing')!r}"
    assert all(path in said(error) for path in ("README.md", "docs/guide.md")), said(error)


def test_a_file_the_keyword_store_leaves_in_neither_list_is_named_as_before():
    """(c) The keyword store judges every tracked file: a gap is a path in the message and in details['missing']."""
    lexical = block(indexed=[path for path in sorted(TRACKED) if path != "lib/util.py"])
    error = coverage(record(lexical=lexical))
    assert error.details.get("missing") == ["lib/util.py"]
    assert "lib/util.py" in said(error), f"the message names no file: {said(error)!r}"


def test_a_file_in_both_lists_of_the_code_graph_is_named_in_both_and_in_the_message():
    """(b) A file in a store's indexed list and in its refused list is a refusal of its own (details['both'])."""
    codegraph = block(indexed=["lib/util.py"], refused=["lib/util.py"], judged=1, judged_files=["lib/util.py"])
    error = coverage(record(codegraph=codegraph))
    assert error.details.get("both") == ["lib/util.py"], f"details['both'] is {error.details.get('both')!r}"
    assert "lib/util.py" in said(error), f"the message names no file: {said(error)!r}"
    assert not error.details.get("missing"), f"a file in both lists is not missing: {error.details.get('missing')!r}"


def test_files_in_both_lists_of_two_stores_are_collected_sorted():
    everything = sorted(TRACKED)
    lexical = block(indexed=everything, refused=["lib/util.py"])
    vectors = block(indexed=everything, refused=["README.md"], judged=len(everything), judged_files=everything)
    error = coverage(record(lexical=lexical, vectors=vectors))
    assert error.details.get("both") == ["README.md", "lib/util.py"], f"{error.details.get('both')!r}"
    assert all(path in said(error) for path in ("README.md", "lib/util.py")), said(error)


def test_a_missing_file_and_a_file_in_both_lists_are_each_named_under_its_own_key():
    files = ["README.md", "docs/guide.md", "lib/util.py"]
    vectors = block(indexed=["README.md"], refused=["README.md"], judged=3, judged_files=files)
    error = coverage(record(vectors=vectors))
    assert error.details.get("both") == ["README.md"] and error.details.get("missing") == ["docs/guide.md", "lib/util.py"], \
        f"both {error.details.get('both')!r}, missing {error.details.get('missing')!r}"


def test_a_record_without_judged_files_keeps_the_count_message_and_still_raises():
    """An older record (no ``judged_files``): the refusal says the count, as before; it must still be FABRIC_INCOMPLETE
    with ``vectors`` named (green on the base: it guards the old behaviour)."""
    vectors = block(indexed=["README.md"], judged=3)
    error = coverage(record(vectors=vectors))
    assert "vectors" in said(error) and "judged and in neither list" in said(error), said(error)


# ---- the record a good A9 run writes -----------------------------------------------------------------------------

def test_a_good_run_records_the_judged_files_of_the_vectors_store_and_the_code_graph(worlds):
    """The stores carry ``judged_files``, a sorted list as long as ``judged`` (red on the base: the key is absent)."""
    stores = worlds.a9("default").record()["stores"]
    for name in ("vectors", "codegraph"):
        files = stores[name].get("judged_files")
        assert isinstance(files, list), f"stores.{name} has no list judged_files: {sorted(stores[name])}"
        assert files == sorted(files), f"stores.{name}.judged_files is not sorted"
        judged = stores[name]["judged"]
        judged = len(judged) if isinstance(judged, list) else judged
        assert len(files) == judged, f"stores.{name}: {len(files)} judged_files for judged = {judged}"
        listed = set(stores[name]["indexed"]) | {item["path"] for item in stores[name]["refused"]}
        assert set(files) <= listed, f"stores.{name} judged files that no list names: {sorted(set(files) - listed)}"


# ---- end to end: two namespaces of the path map match the same files (the adopter's own case) -------------------

OVERLAP = {"docs-private": {"paths": ["docs/**"], "embedding_policy": "not embedded"}}


@pytest.fixture(scope="module")
def overlapping(tmp_path_factory, embedder):
    """A planted adoption whose path map puts ``docs/**`` in two namespaces (embedded first, not embedded second) after
    the first, through A8 and then A9 (the adopter's rust-workspace put ``audits/**`` in two namespaces)."""
    base = tmp_path_factory.mktemp("overlap")
    try:
        box = W.make_box(base)
        project = W.plant_adoption(box, "harbour")
        path_map = project / W.S124.PATH_MAP_REL
        document = yaml.safe_load(path_map.read_text(encoding="utf-8"))
        template = next(iter(document["namespaces"].values()))
        document["namespaces"].update({name: {**template, **spec} for name, spec in OVERLAP.items()})
        path_map.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        W.commit_all(project, "two namespaces of the path map match docs/**")
        adoption = W.Adoption(project, box, embedder.host)
        failed = adoption.chain("A8")
        run = adoption.a9(base / "a9-out") if failed is None else None
        yield failed, run
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_a9_over_a_path_map_with_overlapping_namespaces_names_the_files_it_stops_on(overlapping):
    """The plant reproduces the adopter's refusal on the base ("vectors: 2 file(s) judged and in neither list"). The
    refusal must name each file: the message lists the paths and details carries them, every one under ``docs/``."""
    failed, run = overlapping
    assert failed is None, f"the planted adoption did not reach A8: {failed.describe()}"
    W.assert_offered(run, "A9")
    W.assert_refused(run, "FABRIC_INCOMPLETE", "A9 over overlapping namespaces")
    details = run.error.get("details") or {}
    named = list(details.get("missing") or []) + list(details.get("both") or [])
    assert named, f"the refusal names no file in details: {run.error!r}"
    message = run.error.get("message", "")
    assert all(path in message for path in named), f"the message does not name {named}: {message!r}"
    assert all(path.startswith("docs/") for path in named), f"files named outside the overlapping namespaces: {named}"
    assert details.get("missing") == sorted(details.get("missing") or []), "details['missing'] is not sorted"
