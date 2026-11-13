"""A narrowed register item carries its own entry's id, never its parent's (W2-133 S1, S3; DEC-1083).

Regression evidence only (DEC-136). ``register.leave_out`` narrows an expanded register item that touches a
superseded or done entry to its own chunk; the kept item's ``id``, ``entry``, ``status``, ``in_force`` and ``also``
are the narrowed chunk's, from its own lines. The planted register is committed in a temporary git repository and
indexed lexically (the secret filter stood in for); no vectors and no model. Today's chunker cuts the register at
every level 1-3 heading, so no parent over two entries arises from it: the parent items are planted, labelled as
``retrieve`` labels them (W2-92 S9's entry marks).
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
from gov.retrieval import lexical, retrieve, semantic  # noqa: E402

BEFORE = "c59e6cd84f9b8e91c9e7c9175c72cf4b3b05dee5"  # w2/W2-133 before the fix: integrate with the acceptance cases
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
REG = "docs/REG.md"
TAGS = "- **Tags:** domain: plan · scope: repository · lands in: none"
TEXT = ("# Register\n\nThe preface.\n\n"
        f"### DEC-100 — old\n- **Status:** SUPERSEDED by DEC-101\n{TAGS}\n- **Decision:** the old aster rule.\n\n"
        "## Interlude\n\nA note between the entries on the lotus rule.\n\n"
        f"### DEC-101 — new\n- **Status:** ACCEPTED · **Supersedes:** DEC-100\n{TAGS}\n"
        "- **Decision:** the new aster rule holds the quince clause.\n\n"
        f"### DEC-102 — a one-off\n- **Status:** ACCEPTED\n{TAGS} · done\n- **Decision:** the finished birch task.\n\n"
        f"### DEC-103 — later\n- **Status:** ACCEPTED · **Changed by:** DEC-101\n{TAGS}\n"
        "- **Decision:** the later cedar rule.\n")
MARK = ("entry", "status", "changed_by", "in_force", "not_in_force")
LABEL = ("id", *MARK, "also")


def _mark(rid, status, changed_by=(), why=None):
    """An entry mark as ``retrieve`` gives it (W2-92 S9)."""
    return {"entry": rid, "status": status, "changed_by": list(changed_by), "in_force": why is None,
            **({"not_in_force": why} if why else {})}


MARKS = {"DEC-100": _mark("DEC-100", "SUPERSEDED", why="SUPERSEDED"), "DEC-101": _mark("DEC-101", "ACCEPTED"),
         "DEC-102": _mark("DEC-102", "ACCEPTED"), "DEC-103": _mark("DEC-103", "ACCEPTED", ["DEC-101"])}


@pytest.fixture()
def root(tmp_path, monkeypatch):
    """A repository whose path map names a register of DEC-100 (superseded), DEC-101, DEC-102 (done) and DEC-103."""
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_a, **_k: {"available": False, "reason": "off", "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda root: False)
    monkeypatch.setattr(retrieve, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(retrieve, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})
    for rel, text in {".gitignore": ".gov-runtime/\n", "governance/project/path-map.yaml": f"decision_register: {REG}\n",
                      REG: TEXT}.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the register"]):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(tmp_path)})
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    return tmp_path


def _line(text):
    return TEXT.split("\n").index(text) + 1


def _chunk(root, heading):
    """The register's chunk that starts at ``heading``."""
    return next(chunk for chunk in lexical.chunks(root, REG) if chunk["start_line"] == _line(heading))


def _parent(first, last, chunk, entries):
    """A planted expanded parent over the lines ``first`` to ``last``, hit by ``chunk``, labelled as ``retrieve``
    labels it: the entry holding its first line, each other entry it touches in ``also``."""
    body = "".join(TEXT.splitlines(keepends=True)[first - 1:last])
    own, *others = entries
    return {"id": own, "sha256": hashlib.sha256(body.encode()).hexdigest(), "path": REG, "start_line": first,
            "end_line": last, "text": body, "chunk_id": chunk["chunk_id"], "routes": ["lexical"], "batch": 1,
            **MARKS[own], **({"also": [MARKS[rid] for rid in others]} if others else {})}


# -- S1: the narrowed item's id, entry, status, in_force and also are its own chunk's ------------------------------

def test_a_parent_over_superseded_dec_100_then_dec_101_narrows_to_dec_101_s_own_label(root):
    chunk = _chunk(root, "### DEC-101 — new")
    parent = _parent(_line("### DEC-100 — old"), chunk["end_line"], chunk, ["DEC-100", "DEC-101"])
    kept, left_out = register.leave_out(root, [parent])
    assert left_out == {"count": 1, "superseded": ["DEC-100"], "done": []}
    [item] = kept
    assert (item["start_line"], item["end_line"]) == (chunk["start_line"], chunk["end_line"])
    assert (item["id"], item["entry"], item["status"], item["in_force"]) == ("DEC-101", "DEC-101", "ACCEPTED", True)
    assert item["changed_by"] == [] and "not_in_force" not in item and "also" not in item


def test_a_parent_whose_first_entry_is_done_narrows_to_the_next_entry_with_its_changers(root):
    chunk = _chunk(root, "### DEC-103 — later")
    parent = _parent(_line("### DEC-102 — a one-off"), chunk["end_line"], chunk, ["DEC-102", "DEC-103"])
    [item], left_out = register.leave_out(root, [parent])
    assert left_out == {"count": 1, "superseded": [], "done": ["DEC-102"]}
    assert {key: item[key] for key in LABEL if key in item} == {"id": "DEC-103", **MARKS["DEC-103"]}


def test_a_narrowed_chunk_in_a_gap_carries_its_chunk_id_and_no_entry(root):
    chunk = _chunk(root, "## Interlude")
    parent = _parent(_line("### DEC-100 — old"), chunk["end_line"], chunk, ["DEC-100"])
    [item], _ = register.leave_out(root, [parent])
    assert item["id"] == chunk["chunk_id"]
    assert not {key: item[key] for key in LABEL[1:] if key in item}, item


def test_the_narrowed_label_is_the_label_retrieve_gives_the_same_chunk(root):
    chunk = _chunk(root, "### DEC-101 — new")
    parent = _parent(_line("### DEC-100 — old"), chunk["end_line"], chunk, ["DEC-100", "DEC-101"])
    [item], _ = register.leave_out(root, [parent])
    [alone] = [found for found in retrieve.retrieve(root, "quince")["evidence"] if found["path"] == REG]
    assert (alone["start_line"], alone["end_line"]) == (item["start_line"], item["end_line"])
    assert {key: alone[key] for key in LABEL if key in alone} == {key: item[key] for key in LABEL if key in item}
    assert (alone["sha256"], alone["text"]) == (item["sha256"], item["text"])


def test_an_item_without_entry_marks_takes_its_chunk_s_id_and_gains_no_mark(root):
    chunk = _chunk(root, "### DEC-101 — new")
    parent = {key: value for key, value in _parent(_line("### DEC-100 — old"), chunk["end_line"], chunk,
                                                   ["DEC-100", "DEC-101"]).items() if key not in LABEL[1:]}
    [item], _ = register.leave_out(root, [parent])  # as supplementary's items are: an id and no marks
    assert item["id"] == "DEC-101" and not set(LABEL[1:]) & set(item)


def test_an_item_that_touches_no_left_out_entry_is_kept_as_it_is(root):
    chunk = _chunk(root, "### DEC-101 — new")
    parent = _parent(chunk["start_line"], chunk["end_line"], chunk, ["DEC-101"])
    assert register.leave_out(root, [parent]) == ([parent], None)


# -- S3: nothing else in the kept items changes ---------------------------------------------------------------------

def _before():
    """``register`` as it stood before the fix, loaded from git; skipped where the history does not hold it."""
    shown = subprocess.run(["git", "-C", str(REPO), "show", f"{BEFORE}:src/gov/decisions/register.py"],
                           capture_output=True, text=True)
    if shown.returncode:
        pytest.skip(f"the history does not hold {BEFORE[:12]}: {shown.stderr.strip()}")
    spec = importlib.util.spec_from_loader("gov.decisions._register_before_w2_133", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(shown.stdout, "register_before_w2_133.py", "exec"), module.__dict__)
    return module


def test_leave_out_keeps_the_same_items_in_the_same_order_but_for_the_label(root):
    first = _chunk(root, "### DEC-101 — new")
    gap = _chunk(root, "## Interlude")
    later = _chunk(root, "### DEC-103 — later")
    old = _chunk(root, "### DEC-100 — old")
    other = {"id": "T-1", "path": "work/T-1.md", "start_line": 1, "end_line": 3, "chunk_id": "t", "batch": 1}
    evidence = [_parent(_line("### DEC-100 — old"), first["end_line"], first, ["DEC-100", "DEC-101"]), other,
                _parent(_line("### DEC-100 — old"), gap["end_line"], gap, ["DEC-100"]),
                _parent(old["start_line"], old["end_line"], old, ["DEC-100"]),  # its own chunk is out: left out
                _parent(_line("### DEC-102 — a one-off"), later["end_line"], later, ["DEC-102", "DEC-103"]),
                _parent(first["start_line"], first["end_line"], first, ["DEC-101"])]
    old_kept, old_left = _before().leave_out(root, [dict(item) for item in evidence])
    new_kept, new_left = register.leave_out(root, [dict(item) for item in evidence])
    assert old_left == new_left == {"count": 2, "superseded": ["DEC-100"], "done": ["DEC-102"]}
    assert len(old_kept) == len(new_kept) == 5
    for was, now in zip(old_kept, new_kept):
        assert {k: v for k, v in was.items() if k not in LABEL} == {k: v for k, v in now.items() if k not in LABEL}
        assert list(now)[0] == list(was)[0]  # the id keeps its place
    assert [now["id"] for now in new_kept] == ["DEC-101", "T-1", gap["chunk_id"], "DEC-103", "DEC-101"]
    assert [was["id"] for was in old_kept] == ["DEC-100", "T-1", "DEC-100", "DEC-102", "DEC-101"]  # the cause
    assert new_kept[1] == old_kept[1] == other and new_kept[4] == old_kept[4] == evidence[5]
