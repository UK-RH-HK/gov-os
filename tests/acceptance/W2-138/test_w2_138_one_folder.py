"""S2: the store is resolved once per search: every facet of one search reads the same folder, even when the link is
switched during the search (W2-116's R2-F1; README).

The seam: ``gov.retrieval.lexical.search``, the lexical facet's search, is wrapped so that the first time it returns,
the link is switched from store ``a`` (C1) to store ``b`` (C2), as a refresh switches it. The folder every store
read of the search is given is recorded as it stands at the call (``os.path.realpath`` of the root it is passed):
the lexical search itself, the semantic facet (the stand-in), the lexical chunks and parents, and the record graph.
Every one must be ``a``, and every evidence item's lines and sha256 must be ``a``'s. In ``b`` every line of the
alpha note sits two lines lower, so lines read through the switched link are not ``a``'s.
"""

from __future__ import annotations

import hashlib
import os

import pytest

import w2_138_support as support

from gov import records
from gov.retrieval import lexical, semantic

QUESTION = "quillwort"


def _record(monkeypatch, link, target):
    """The reads of every store function the search calls, and the switch after the first lexical search."""
    seen, state = [], {"switched": False, "after": 0}

    def where(name, root):
        seen.append((name, os.path.realpath(str(root)), state["switched"]))

    def wrap(module, name, switch=False):
        original = getattr(module, name)

        def wrapped(root, *args, **kwargs):
            where(f"{module.__name__}.{name}", root)
            answer = original(root, *args, **kwargs)
            if switch and not state["switched"]:
                support.switch(link, target)
                state["switched"] = True
            return answer
        monkeypatch.setattr(module, name, wrapped)

    wrap(lexical, "search", switch=True)
    for module, name in ((lexical, "chunks"), (lexical, "parent"), (records, "records"), (records, "edges")):
        wrap(module, name)

    def semantic_stand_in(root, *args, **kwargs):
        where("gov.retrieval.semantic.search", root)
        return {"available": True, "reason": None, "hits": []}
    monkeypatch.setattr(semantic, "search", semantic_stand_in)
    return seen, state


@pytest.mark.parametrize("given", ["root-link", "gov-store-link"])
def test_s2_one_search_reads_one_folder_when_the_link_is_switched_between_the_facets(stores, capsys, tmp_path,
                                                                                    monkeypatch, given):
    link = support.link_to(tmp_path / "stores" / "integration", stores.a)
    if given == "gov-store-link":
        monkeypatch.setenv("GOV_STORE", str(link))
        options = ()
    else:
        options = ("--root", link)
    seen, state = _record(monkeypatch, link, stores.b)
    run = support.search(capsys, QUESTION, *options)
    assert state["switched"], f"the seam was not reached: the search never called lexical.search\n{run.describe()}"
    assert os.path.realpath(link) == str(stores.b), "premise: the link was switched to b during the search"
    assert any(after for *_, after in seen), f"premise: the search read the store after the switch: {seen}"
    folders = {folder for _, folder, _ in seen}
    assert folders == {str(stores.a)}, (
        "one search read more than one store folder (or not the one the link named when it began, "
        f"{stores.a}):\n" + "\n".join(f"  {name}: {folder}{' (after the switch)' if after else ''}"
                                      for name, folder, after in seen))
    assert run.ok, run.describe()
    evidence = run.result.get("evidence") or []
    assert evidence, f"the search gave no evidence\n{run.describe()}"
    for item in evidence:
        lines = support.lines_at(stores.a, stores.c1, item["path"], item["start_line"], item["end_line"])
        assert item["sha256"] == hashlib.sha256(lines).hexdigest(), (
            f"{item['path']} {item['start_line']}-{item['end_line']}: its sha256 is not a's lines (read through the "
            "switched link?)")
        assert item["text"] == lines.decode("utf-8"), f"{item['path']}: its text is not a's lines"
