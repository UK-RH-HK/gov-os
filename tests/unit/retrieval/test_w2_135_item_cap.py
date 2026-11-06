"""Each line of an evidence item over 4,000 characters is sent as its first 4,000, the item marked cut, its lines cited
unchanged; every other line is sent whole (W2-135 S1-S3, round 2; DEC-1086 B "a guard against one-line files only",
BUNDLE-BUDGET-1 (a)).

Regression evidence only (DEC-136). The planted repository holds a one-line JSON file of 24,575 characters (one chunk,
its own parent, so it is sent alone), a Markdown file with a 10,631-character line among ordinary lines (a chunk of its
own inside a section: sent alone when the budget is too small to expand, inside its expanded section otherwise), a
Markdown section of over 11,000 characters of ordinary lines whose one rare word lies past character 4,000 (an
expanded parent's piece, sent whole), and lines at and just over the cap. A line is measured without its newline, and
a cut line keeps its newline. Accents before the 4,000th character make characters and bytes differ. A second planted
repository holds a register for ``register.leave_out``'s narrowed items (the review's F2). The stores are built in
temporary git repositories, with the secret filter replaced, no vectors and no model: the lexical route only, the
reranker a stand-in.
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
from gov.decisions import register  # noqa: E402
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
                if n != 110 else f"- Step {n}: the marmoset clause names the worker's last check.\n" for n in range(136))
FILES = {
    TABLE: _one_line("zephyrine", 24575),
    EDGE: _one_line("ocelot", CAP + 1),  # a line of 4,000 characters and its newline: not over the cap
    OVER: _one_line("pangolin", CAP + 2),  # a line of 4,001 characters and its newline: over it
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


def _plant(root, files, monkeypatch):
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_a, **_k: {"available": False, "reason": "off", "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda root: False)
    _stand_ins(monkeypatch, retrieve)
    for rel, text in {".gitignore": ".gov-runtime/\n", **files}.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the planted files"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(root)})
    lexical.refresh(root)
    store.load(root)
    return root


@pytest.fixture()
def project(tmp_path, monkeypatch):
    return _plant(tmp_path, FILES, monkeypatch)


def _items(bundle, rel):
    return [item for item in bundle["evidence"] if item["path"] == rel]


def _chunk(root, rel, first, last):
    [chunk] = [c for c in lexical.chunks(root) if (c["path"], c["start_line"], c["end_line"]) == (rel, first, last)]
    return chunk


def _sent(rel, first, last):
    """The span's text as it should be sent: each line over CAP characters (without its newline) cut to its first CAP,
    its newline kept; and the numbers of the lines cut."""
    sent, cut = [], []
    for number, line in enumerate(_lines(rel)[first - 1:last], first):
        bare = line.rstrip("\n")
        if len(bare) > CAP:
            line, cut = bare[:CAP] + "\n", [*cut, number]
        sent.append(line)
    return "".join(sent), cut


def _assert_cut(item, rel, first, last, lines):
    """The item cites the whole span; only the lines ``lines`` are cut, each to its first CAP characters, its newline
    kept, and the item carries the cut key with the full and sent lengths."""
    full = _span(rel, first, last)
    text, cut = _sent(rel, first, last)
    assert cut == lines
    assert (item["path"], item["start_line"], item["end_line"]) == (rel, first, last)
    assert item["sha256"] == hashlib.sha256(full.encode("utf-8")).hexdigest()  # of the full span, as today
    assert item["text"] == text
    assert item["cut"] == {"chars": len(full), "sent": len(text), "lines": lines}
    for number in lines:  # characters, not bytes: the accents lie before the cap
        assert len(_lines(rel)[number - 1][:CAP].encode("utf-8")) > CAP


def test_the_planted_files_are_what_the_cases_need(project):
    assert len(FILES[TABLE]) == 24575 and len(_lines(TABLE)) == 1 and len(LONG) == 10631
    assert len(FILES[EDGE].rstrip("\n")) == CAP and len(FILES[OVER].rstrip("\n")) == CAP + 1
    steps = _span(GUIDE, *STEPS_SECTION)
    assert len(steps) > 11000 and all(len(line) < 120 for line in _lines(GUIDE))
    assert steps.index("marmoset") > CAP  # the rare word lies past the 4,000th character of its section (F1)
    chunks = {(c["path"], c["start_line"], c["end_line"]) for c in lexical.chunks(project)}
    assert (TABLE, 1, 1) in chunks and (NOTES, LONG_LINE, LONG_LINE) in chunks  # each long line a chunk of its own
    assert len([c for c in chunks if c[0] == GUIDE and c[1] >= STEPS_SECTION[0]]) > 1  # the section in several chunks


# -- the line cap itself ---------------------------------------------------------------------------------------------

def test_capped_measures_a_line_without_its_newline_and_keeps_the_newline():
    for end in ("\n", "\r\n", "\r", ""):
        at, over = "a" * CAP + end, "é" * (CAP + 1) + end
        assert retrieve.capped(at.encode(), 7) == (at, {})
        body = ("short\n" + over + "tail\n").encode() if end else ("short\n" + over).encode()
        text, cut = retrieve.capped(body, 7)
        expected = "short\n" + "é" * CAP + end + ("tail\n" if end else "")
        assert text == expected, repr(end)
        assert cut == {"cut": {"chars": len(body.decode()), "sent": len(expected), "lines": [8]}}


def test_capped_names_every_cut_line_by_its_number_in_the_file():
    body = ("x" * 5000 + "\nok\n" + "y" * 4001 + "\n" + "z" * 4000 + "\n").encode()
    text, cut = retrieve.capped(body, 20)
    assert text == "x" * CAP + "\nok\n" + "y" * CAP + "\n" + "z" * CAP + "\n"
    assert cut["cut"]["lines"] == [20, 22] and cut["cut"]["chars"] == len(body) and cut["cut"]["sent"] == len(text)


# -- S1: a line over 4,000 characters cut, the cut named; its neighbours whole ---------------------------------------

def test_a_one_line_file_of_24575_characters_is_sent_as_its_first_4000_marked_cut(project):
    [item] = _items(retrieve.retrieve(project, "zephyrine"), TABLE)
    _assert_cut(item, TABLE, 1, 1, [1])
    assert item["text"] == FILES[TABLE][:CAP] + "\n"
    assert item["cut"] == {"chars": 24575, "sent": CAP + 1, "lines": [1]}
    assert item["chunk_id"] == _chunk(project, TABLE, 1, 1)["chunk_id"] and item["id"] == item["chunk_id"]


def test_a_10631_character_markdown_line_sent_alone_is_cut(project):
    bundle = retrieve.retrieve(project, "quokkaline", bundle_budget=100)  # too small to expand
    [item] = _items(bundle, NOTES)
    assert bundle["expansions"] == []
    _assert_cut(item, NOTES, LONG_LINE, LONG_LINE, [LONG_LINE])
    assert item["cut"]["chars"] == 10631 + 1  # the line and its final newline, the text the item carried before
    assert item["chunk_id"] == _chunk(project, NOTES, LONG_LINE, LONG_LINE)["chunk_id"]


def test_in_the_expanded_section_only_the_long_line_is_cut_its_neighbours_whole(project):
    bundle = retrieve.retrieve(project, "quokkaline")
    [item] = _items(bundle, NOTES)
    assert [(e["start_line"], e["end_line"]) for e in bundle["expansions"]] == [LONG_SECTION]
    _assert_cut(item, NOTES, *LONG_SECTION, [LONG_LINE])
    before, after = item["text"].split(LONG[:CAP] + "\n")
    assert before == _span(NOTES, LONG_SECTION[0], LONG_LINE - 1)
    assert after == _span(NOTES, LONG_LINE + 1, LONG_SECTION[1])  # the line after it, and the end, sent whole
    assert item["chunk_id"] == _chunk(project, NOTES, LONG_LINE, LONG_LINE)["chunk_id"]  # the child's, as today


def test_a_line_of_4001_characters_is_cut_and_keeps_its_newline(project):
    [item] = _items(retrieve.retrieve(project, "pangolin"), OVER)
    _assert_cut(item, OVER, 1, 1, [1])
    assert item["text"] == FILES[OVER][:CAP] + "\n"
    assert item["cut"] == {"chars": CAP + 2, "sent": CAP + 1, "lines": [1]}


def test_a_cut_item_s_sha256_still_matches_its_cited_lines(project):
    # validate.py's TEXT_NOT_FOUND on a cut item is the ticket's known row: a cut line keeps its newline, so the sent
    # text is no substring of the span; only that code may name a cut item, and never an uncut one
    for query, kwargs in (("zephyrine", {}), ("quokkaline", {}), ("quokkaline", {"bundle_budget": 100}),
                          ("pangolin", {}), ("marmoset", {})):
        bundle = retrieve.retrieve(project, query, **kwargs)
        errors = [e for e in validate.validate(project, bundle)["errors"] if "index" in e]
        cut = {i for i, item in enumerate(bundle["evidence"]) if "cut" in item}
        assert all(e["code"] == "TEXT_NOT_FOUND" and e["index"] in cut for e in errors), (query, errors)
    assert cut == set() and errors == []  # marmoset: ordinary lines only, so nothing cut and nothing flagged


# -- S2: no line over 4,000 characters, sent as today, however long --------------------------------------------------

def test_an_expanded_section_of_11000_characters_of_ordinary_lines_is_sent_whole(project):
    bundle = retrieve.retrieve(project, "marmoset")
    [item] = _items(bundle, GUIDE)
    assert [(e["start_line"], e["end_line"]) for e in bundle["expansions"]] == [STEPS_SECTION]
    assert item["text"] == _span(GUIDE, *STEPS_SECTION) and len(item["text"]) > 11000 and "cut" not in item
    assert "marmoset" in item["text"]  # the hit line, past character 4,000, is sent (the review's F1)


def test_a_line_of_exactly_4000_characters_and_its_newline_is_sent_whole(project):
    [item] = _items(retrieve.retrieve(project, "ocelot"), EDGE)
    assert item["text"] == FILES[EDGE] and len(item["text"]) == CAP + 1 and "cut" not in item


def test_a_short_item_is_sent_whole_with_no_cut_key(project):
    [item] = _items(retrieve.retrieve(project, "kumquat"), SMALL)
    assert item["text"] == _span(SMALL, item["start_line"], item["end_line"]) and "cut" not in item


# -- S2, the review's F2: a narrowed register item's cut is its own -------------------------------------------------

REG = "docs/REG.md"
TAGS = "- **Tags:** domain: plan · scope: repository · lands in: none"
REG_LONG = ("- **Decision:** the yarrow clause, café by café, naïve and über, " + "and on it goes " * 400)[:4500]
REG_TEXT = ("# Register\n\nThe preface.\n\n"
            f"### DEC-100 — old\n- **Status:** SUPERSEDED by DEC-101\n{TAGS}\n- **Decision:** the old aster rule.\n\n"
            f"### DEC-101 — new\n- **Status:** ACCEPTED · **Supersedes:** DEC-100\n{TAGS}\n"
            "- **Note:** the quince clause is short.\n\n"
            + REG_LONG + "\n\n- **After:** the last line of DEC-101.\n")


def _reg_line(text):
    return REG_TEXT.split("\n").index(text) + 1


@pytest.fixture()
def registered(tmp_path, monkeypatch):
    """A repository whose path map names a register of DEC-100 (superseded by DEC-101) and DEC-101, which holds one
    line of 4,500 characters."""
    return _plant(tmp_path, {"governance/project/path-map.yaml": f"decision_register: {REG}\n", REG: REG_TEXT},
                  monkeypatch)


def _parent_over(root, chunk):
    """A planted parent from DEC-100's heading to the end of DEC-101 (so over the long line), hit by ``chunk``, sent
    as ``retrieve`` sends a span: cut at its long line, its cut key the parent's."""
    first, last = _reg_line("### DEC-100 — old"), len(REG_TEXT.splitlines())
    body = "".join(REG_TEXT.splitlines(keepends=True)[first - 1:last]).encode()
    text, cut = retrieve.capped(body, first)
    assert cut["cut"]["lines"] == [_reg_line(REG_LONG)]
    mark = {"entry": "DEC-100", "status": "SUPERSEDED", "changed_by": [], "in_force": False,
            "not_in_force": "SUPERSEDED"}
    also = [{"entry": "DEC-101", "status": "ACCEPTED", "changed_by": [], "in_force": True}]
    return {"id": "DEC-100", "sha256": hashlib.sha256(body).hexdigest(), "path": REG, "start_line": first,
            "end_line": last, "text": text, **cut, "chunk_id": chunk["chunk_id"], "routes": ["lexical"], "batch": 1,
            **mark, "also": also}


def _reg_chunk(root, line):
    return next(c for c in lexical.chunks(root, REG) if c["start_line"] <= line <= c["end_line"])


def test_a_register_item_narrowed_to_ordinary_lines_drops_its_parent_s_cut_key(registered):
    chunk = _reg_chunk(registered, _reg_line("- **Note:** the quince clause is short."))
    assert not chunk["start_line"] <= _reg_line(REG_LONG) <= chunk["end_line"]
    [item], left_out = register.leave_out(registered, [_parent_over(registered, chunk)])
    assert left_out == {"count": 1, "superseded": ["DEC-100"], "done": []}
    assert (item["start_line"], item["end_line"]) == (chunk["start_line"], chunk["end_line"])
    assert item["text"] == "".join(REG_TEXT.splitlines(keepends=True)[chunk["start_line"] - 1:chunk["end_line"]])
    assert "cut" not in item and item["id"] == "DEC-101"


def test_a_register_item_narrowed_to_its_long_line_carries_a_cut_of_its_own(registered):
    line = _reg_line(REG_LONG)
    chunk = _reg_chunk(registered, line)
    [item], _ = register.leave_out(registered, [_parent_over(registered, chunk)])
    full = "".join(REG_TEXT.splitlines(keepends=True)[chunk["start_line"] - 1:chunk["end_line"]])
    assert (item["start_line"], item["end_line"]) == (chunk["start_line"], chunk["end_line"])
    assert item["sha256"] == hashlib.sha256(full.encode()).hexdigest()  # of the narrowed span, in full
    assert item["text"] == full.replace(REG_LONG, REG_LONG[:CAP]) and len(item["text"]) < len(full)
    assert item["cut"] == {"chars": len(full), "sent": len(item["text"]), "lines": [line]}
    # the same text and cut key ``retrieve`` gives that chunk sent alone
    [alone] = [found for found in retrieve.retrieve(registered, "yarrow", bundle_budget=1)["evidence"]
               if found["path"] == REG and found["chunk_id"] == chunk["chunk_id"]]
    assert (alone["text"], alone["cut"], alone["sha256"]) == (item["text"], item["cut"], item["sha256"])


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


def test_the_bundle_is_the_same_before_and_after_but_for_the_cut_lines_and_key(project, monkeypatch):
    # one test over every call, not parametrised: the opt-in lists keep only a parametrised test's first row
    old_seen, new_seen = [], []
    before = _before(monkeypatch, old_seen)
    _stand_ins(monkeypatch, retrieve, new_seen)
    cut, whole, long_whole = 0, 0, 0
    for query, kwargs in CALLS:
        old = before.retrieve(project, query, **kwargs)
        new = retrieve.retrieve(project, query, **kwargs)
        assert set(old) == set(new), (query, kwargs)
        for key in set(new) - {"evidence"}:  # the batches, budget (its used), gaps, continuation, expansions, repeats
            assert old[key] == new[key], (query, kwargs, key)
        assert len(old["evidence"]) == len(new["evidence"]), (query, kwargs)
        for was, now in zip(old["evidence"], new["evidence"]):  # the same items in the same order
            text, lines = _sent(was["path"], was["start_line"], was["end_line"])
            assert was["text"] == _span(was["path"], was["start_line"], was["end_line"])
            if lines:
                cut += 1
                assert now["text"] == text
                assert now["cut"] == {"chars": len(was["text"]), "sent": len(text), "lines": lines}
                assert {k: v for k, v in now.items() if k not in ("text", "cut")} == \
                       {k: v for k, v in was.items() if k != "text"}, (query, kwargs)
            else:
                whole += 1
                long_whole += len(was["text"]) > CAP
                assert was == now, (query, kwargs, now["path"])
    assert old_seen == new_seen and new_seen  # the reranker's input is unchanged
    assert cut >= 6 and whole >= 6 and long_whole >= 2, (cut, whole, long_whole)


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
