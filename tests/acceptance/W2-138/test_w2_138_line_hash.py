"""S4: each evidence item's sha256 is the sha256 of exactly the lines ``start_line`` to ``end_line`` of its path at
``result.store.commit`` (README, "The byte rule").

Every item of a set of planted searches, on both stores, is checked: an expanded parent, a chunk sent alone, a CRLF
file, a file with no final newline, a line over 4,000 characters (W2-135's ``cut``: the text is shortened, the hash
is not), a register entry, and every page of a paged question. The lines come from git (``git cat-file blob
<commit>:<path>``), never from the code under test.
"""

from __future__ import annotations

import hashlib

import w2_138_support as support

CALLS = [("quillwort", ()), ("quillwort", ("--bundle-budget", "200")), ("bergamot", ()), ("marjoram", ()),
         ("saffron", ()), ("juniper", ()), ("lantern", ("--batch-size", "1"))]


def _items(capsys, root):
    """``(item, run)`` of every evidence item of every call (each paged call followed to its end) on ``root``."""
    found = []
    for question, options in CALLS:
        run, pages = support.search(capsys, question, "--root", root, *options), 0
        while True:
            assert run.ok, run.describe()
            found += [(item, run) for item in run.result.get("evidence") or []]
            token, pages = run.result.get("continuation"), pages + 1
            if not token or pages >= 12:
                break
            run = support.search(capsys, question, "--root", root, *options, "--continue", token)
    return found


def _assert_coverage(found):
    """The premise: the checked items hold each planted kind, so the check is not empty."""
    paths = {item["path"] for item, _ in found}
    expected = {support.ALPHA, support.CRLF, support.TAIL, support.LONG, support.GAMMA, support.REGISTER}
    assert expected <= paths, f"premise: items from every planted file; missing {sorted(expected - paths)}"
    assert any((item["path"], item["start_line"], item["end_line"]) in
               {(e["path"], e["start_line"], e["end_line"]) for e in run.result.get("expansions") or []}
               for item, run in found), "premise: an expanded parent among the items"
    assert any("cut" in item for item, _ in found), "premise: an item with a line cut (W2-135) among the items"


def _assert_hashes(folder, found, commit_of):
    wrong = []
    for item, run in found:
        commit = commit_of(run)
        lines = support.lines_at(folder, commit, item["path"], item["start_line"], item["end_line"])
        if item.get("sha256") != hashlib.sha256(lines).hexdigest():
            wrong.append(f"{item['path']} {item['start_line']}-{item['end_line']} at {commit[:12]}: "
                         f"{item.get('sha256')} != {hashlib.sha256(lines).hexdigest()}")
    assert not wrong, "items whose sha256 is not the hash of their own lines:\n" + "\n".join(wrong)


def test_s4_every_item_s_sha256_is_the_hash_of_its_own_lines_at_result_store_commit(stores, capsys):
    for folder in (stores.a, stores.b):
        found = _items(capsys, folder)
        _assert_coverage(found)
        _assert_hashes(folder, found, lambda run: support.store_of(run)["commit"])


def test_s4_guard_every_item_s_sha256_is_the_hash_of_its_own_lines_at_the_commit_the_store_was_built_at(stores,
                                                                                                         capsys):
    for folder, commit in ((stores.a, stores.c1), (stores.b, stores.c2)):
        found = _items(capsys, folder)
        _assert_coverage(found)
        _assert_hashes(folder, found, lambda run, commit=commit: commit)
