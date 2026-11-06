"""An evidence item over 4,000 characters is sent as its first 4,000, marked cut, its lines cited unchanged
(W2-135 S1-S3; DEC-1086 B, BUNDLE-BUDGET-1 (a)).

Regression evidence only (DEC-136). The planted repository holds a one-line JSON file of 24,575 characters (one chunk,
its own parent, so it is sent alone), a Markdown file with a 10,631-character line (a chunk of its own inside a section:
sent alone when the budget is too small to expand, inside its expanded section otherwise), a Markdown section of short
lines over 4,000 characters (an expanded parent's piece), and items at, just over and well under the cap. Accents
before the 4,000th character make characters and bytes differ. The store is built in a temporary git repository, with
the secret filter replaced, no vectors and no model: the lexical route only, the reranker a stand-in.
"""
from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.retrieval import lexical, retrieve, semantic, validate  # noqa: E402

BEFORE = "e3355def9f99977defeec32d164944d4966cf87a"  # w2/integrate before W2-135 (retrieve.py blob 1fb6a75b10b9)
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
CAP = 4000


def _one_line(word: str, total: int) -> str:
    """One line of JSON, ``total`` characters with its final newline, naming ``word``; accented before the cap."""
    head, tail = f'{{"name": "{word}", "note": "café crème à la carte", "rows": [', "]}\n"
    fill = total - len(head) - len(tail)
    rows = "0" + ", 0" * ((fill - 1) // 3)
    return head + rows + " " * (fill - len(rows)) + tail


TABLE, EDGE, OVER = "data/table.json", "data/edge.json", "data/over.json"
NOTES, GUIDE, SMALL = "docs/notes.md", "docs/guide.md", "docs/small.md"
LONG = ("The quokkaline line runs on and on, café by café, naïve and über. "
        + "It keeps going past the cap. " * 400)[:10631]
STEPS = "".join(f"- Step {n}: the worker checks the queue and moves on to the next task in its list.\n"
                if n != 35 else f"- Step {n}: the marmoset clause names the worker's last check.\n" for n in range(70))
FILES = {
    TABLE: _one_line("zephyrine", 24575),
    EDGE: _one_line("ocelot", CAP),
    OVER: _one_line("pangolin", CAP + 1),
    NOTES: "# Notes\n\nThe heliotrope note opens the file.\n\n## Long line\n\n" + LONG + "\n\nAfter the line, the end.\n",
    GUIDE: "# Guide\n\nA short preface.\n\n## Steps, étape par étape\n\n" + STEPS,
    SMALL: "# Small\n\nThe kumquat rule is short.\n",
}


def _lines(rel):
    return FILES[rel].splitlines(keepends=True)


def _span(rel, first, last):
    return "".join(_lines(rel)[first - 1:last])


LONG_LINE = _lines(NOTES).index(LONG + "\n") + 1
LONG_SECTION = (_lines(NOTES).index("## Long line\n") + 1, len(_lines(NOTES)))
STEPS_SECTION = (_lines(GUIDE).index("## Steps, étape par étape\n") + 1, len(_lines(GUIDE)))


def _stand_ins(monkeypatch, module, seen=None):
    """No model: the reranker keeps the order and, given ``seen``, records what it was sent."""
    def rerank(query, candidates, reranker=None):
        if seen is not None:
            seen.append((query, [(c["chunk_id"], c["text"]) for c in candidates]))
        return [dict(c) for c in candidates]
    monkeypatch.setattr(module, "rerank", rerank)
    monkeypatch.setattr(module, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})


@pytest.fixture()
def project(tmp_path, monkeypatch):
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_a, **_k: {"available": False, "reason": "off", "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda root: False)
    _stand_ins(monkeypatch, retrieve)
    for rel, text in {".gitignore": ".gov-runtime/\n", **FILES}.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the planted files"]):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(tmp_path)})
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    return tmp_path


def _items(bundle, rel):
    return [item for item in bundle["evidence"] if item["path"] == rel]


def _chunk(root, rel, first, last):
    [chunk] = [c for c in lexical.chunks(root) if (c["path"], c["start_line"], c["end_line"]) == (rel, first, last)]
    return chunk


def _assert_cut(item, rel, first, last):
    """The item cites the whole span and carries its first CAP characters, marked cut."""
    full = _span(rel, first, last)
    assert (item["path"], item["start_line"], item["end_line"]) == (rel, first, last)
    assert item["sha256"] == hashlib.sha256(full.encode("utf-8")).hexdigest()  # of the full span, as today
    assert item["text"] == full[:CAP] and len(item["text"]) == CAP
    assert item["cut"] == {"chars": len(full), "sent": CAP}
    assert len(item["text"].encode("utf-8")) > CAP  # characters, not bytes: the accents lie before the cap


def test_the_planted_files_are_what_the_cases_need(project):
    assert len(FILES[TABLE]) == 24575 and len(_lines(TABLE)) == 1 and len(LONG) == 10631
    assert len(FILES[EDGE]) == CAP and len(FILES[OVER]) == CAP + 1
    assert len(_span(GUIDE, *STEPS_SECTION)) > CAP and all(len(line) < 120 for line in _lines(GUIDE))
    chunks = {(c["path"], c["start_line"], c["end_line"]) for c in lexical.chunks(project)}
    assert (TABLE, 1, 1) in chunks and (NOTES, LONG_LINE, LONG_LINE) in chunks  # each long line a chunk of its own
    assert len([c for c in chunks if c[0] == GUIDE and c[1] >= STEPS_SECTION[0]]) > 1  # the section in several chunks


# -- S1: over 4,000 characters, the first 4,000 sent and the cut named ------------------------------------------------

def test_a_one_line_file_of_24575_characters_is_sent_as_its_first_4000_marked_cut(project):
    [item] = _items(retrieve.retrieve(project, "zephyrine"), TABLE)
    _assert_cut(item, TABLE, 1, 1)
    assert item["cut"] == {"chars": 24575, "sent": CAP}
    assert item["chunk_id"] == _chunk(project, TABLE, 1, 1)["chunk_id"] and item["id"] == item["chunk_id"]


def test_a_10631_character_markdown_line_sent_alone_is_cut(project):
    bundle = retrieve.retrieve(project, "quokkaline", bundle_budget=100)  # too small to expand
    [item] = _items(bundle, NOTES)
    assert bundle["expansions"] == []
    _assert_cut(item, NOTES, LONG_LINE, LONG_LINE)
    assert item["cut"]["chars"] == 10631 + 1  # the line and its final newline, the text the item carried before
    assert item["chunk_id"] == _chunk(project, NOTES, LONG_LINE, LONG_LINE)["chunk_id"]


def test_the_expanded_section_holding_the_long_line_is_cut_as_a_piece(project):
    bundle = retrieve.retrieve(project, "quokkaline")
    [item] = _items(bundle, NOTES)
    assert [(e["start_line"], e["end_line"]) for e in bundle["expansions"]] == [LONG_SECTION]
    _assert_cut(item, NOTES, *LONG_SECTION)
    assert item["chunk_id"] == _chunk(project, NOTES, LONG_LINE, LONG_LINE)["chunk_id"]  # the child's, as today


def test_an_expanded_section_of_short_lines_over_4000_is_cut(project):
    bundle = retrieve.retrieve(project, "marmoset")
    [item] = _items(bundle, GUIDE)
    assert [(e["start_line"], e["end_line"]) for e in bundle["expansions"]] == [STEPS_SECTION]
    _assert_cut(item, GUIDE, *STEPS_SECTION)


def test_a_cut_item_still_validates_against_its_cited_lines(project):
    for query, kwargs in (("zephyrine", {}), ("quokkaline", {}), ("quokkaline", {"bundle_budget": 100}),
                          ("marmoset", {}), ("pangolin", {})):
        bundle = retrieve.retrieve(project, query, **kwargs)
        assert any("cut" in item for item in bundle["evidence"]), query
        errors = validate.validate(project, bundle)["errors"]
        assert not [e for e in errors if "index" in e], (query, errors)  # sha256 and the quoted text both hold


# -- S2: at or under 4,000 characters, sent as today -----------------------------------------------------------------

def test_an_item_of_exactly_4000_characters_is_sent_whole_with_no_cut_key(project):
    [item] = _items(retrieve.retrieve(project, "ocelot"), EDGE)
    assert item["text"] == FILES[EDGE] and len(item["text"]) == CAP and "cut" not in item


def test_an_item_of_4001_characters_is_cut(project):
    [item] = _items(retrieve.retrieve(project, "pangolin"), OVER)
    _assert_cut(item, OVER, 1, 1)
    assert item["cut"] == {"chars": CAP + 1, "sent": CAP}


def test_a_short_item_is_sent_whole_with_no_cut_key(project):
    [item] = _items(retrieve.retrieve(project, "kumquat"), SMALL)
    assert item["text"] == _span(SMALL, item["start_line"], item["end_line"]) and "cut" not in item


# -- S3: nothing else in a bundle changes ---------------------------------------------------------------------------

def _before(monkeypatch, seen):
    """``retrieve`` as it stood before W2-135, loaded from git; skipped where the history does not hold it."""
    shown = subprocess.run(["git", "-C", str(REPO), "show", f"{BEFORE}:src/gov/retrieval/retrieve.py"],
                           capture_output=True, text=True)
    if shown.returncode:
        pytest.skip(f"the history does not hold {BEFORE[:12]}: {shown.stderr.strip()}")
    spec = importlib.util.spec_from_loader("gov.retrieval._retrieve_before_w2_135", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(shown.stdout, "retrieve_before_w2_135.py", "exec"), module.__dict__)
    _stand_ins(monkeypatch, module, seen)
    return module


CALLS = [("zephyrine", {}), ("quokkaline", {}), ("quokkaline", {"bundle_budget": 100}), ("marmoset", {}),
         ("marmoset", {"bundle_budget": 100}), ("ocelot", {}), ("pangolin", {}), ("kumquat", {}), ("heliotrope", {}),
         ("worker queue task", {"batch_size": 2}), ("zephyrine quokkaline marmoset kumquat", {"batch_size": 1}),
         ("zephyrine quokkaline marmoset pangolin ocelot heliotrope", {})]


def test_the_bundle_is_the_same_before_and_after_but_for_the_cut_text_and_key(project, monkeypatch):
    # one test over every call, not parametrised: the opt-in lists keep only a parametrised test's first row
    old_seen, new_seen = [], []
    before = _before(monkeypatch, old_seen)
    _stand_ins(monkeypatch, retrieve, new_seen)
    cut, whole = 0, 0
    for query, kwargs in CALLS:
        old = before.retrieve(project, query, **kwargs)
        new = retrieve.retrieve(project, query, **kwargs)
        assert set(old) == set(new), (query, kwargs)
        for key in set(new) - {"evidence"}:  # the batches, budget (its used), gaps, continuation, expansions, repeats
            assert old[key] == new[key], (query, kwargs, key)
        assert len(old["evidence"]) == len(new["evidence"]), (query, kwargs)
        for was, now in zip(old["evidence"], new["evidence"]):  # the same items in the same order
            if len(was["text"]) > CAP:
                cut += 1
                assert now["text"] == was["text"][:CAP] and now["cut"] == {"chars": len(was["text"]), "sent": CAP}
                assert {k: v for k, v in now.items() if k not in ("text", "cut")} == \
                       {k: v for k, v in was.items() if k != "text"}, (query, kwargs)
            else:
                whole += 1
                assert was == now, (query, kwargs, now["path"])
    assert old_seen == new_seen and new_seen  # the reranker's input is unchanged
    assert cut >= 8 and whole >= 6, (cut, whole)


def test_the_budget_s_used_is_still_counted_on_the_full_text(project):
    bundle = retrieve.retrieve(project, "zephyrine")
    assert bundle["budget"]["bundle"]["used"] >= -(-24575 // retrieve.TOKEN_CHARS)  # over the limit, as today


def test_the_continuation_carries_on_the_same_before_and_after(project, monkeypatch):
    before = _before(monkeypatch, None)
    query = "zephyrine quokkaline marmoset kumquat"
    old = before.retrieve(project, query, batch_size=1)
    new = retrieve.retrieve(project, query, batch_size=1)
    assert new["continuation"] is not None and old["continuation"] == new["continuation"]
    while new["continuation"] is not None:
        old = before.retrieve(project, query, batch_size=1, continuation=old["continuation"])
        new = retrieve.retrieve(project, query, batch_size=1, continuation=new["continuation"])
        strip = lambda bundle: [{k: v for k, v in item.items() if k not in ("text", "cut")}  # noqa: E731
                                for item in bundle["evidence"]]
        assert strip(old) == strip(new) and old["continuation"] == new["continuation"]
        assert {k: v for k, v in old.items() if k != "evidence"} == {k: v for k, v in new.items() if k != "evidence"}
