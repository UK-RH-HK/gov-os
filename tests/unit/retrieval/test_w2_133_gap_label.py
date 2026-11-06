"""A register item that starts in the preface or a gap carries its chunk id, not the entry it touches further down
(W2-133 S2, S3; DEC-1083).

Regression evidence only (DEC-136). The planted register holds a preface, a gap (``## Interlude``) before DEC-476 and
DEC-999 after it; DEC-476 is long enough to be cut into several chunks under one parent. Today's chunker cuts the
register at every level 1-3 heading, so no parent over a gap and an entry arises from it: ``lexical.parent`` is stood
in to widen two sections (the gap's over DEC-476, DEC-476's over DEC-999). The store is built in a temporary git
repository, with the secret filter replaced, no vectors and no model: the lexical route only.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.retrieval import lexical, retrieve, semantic  # noqa: E402

BEFORE = "c59e6cd84f9b8e91c9e7c9175c72cf4b3b05dee5"  # w2/W2-133 before the fix: integrate with the acceptance cases
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
REGISTER = "decisions/REGISTER.md"
FILLER = "".join(f"- **Note {n}:** the pool's rule is applied to each worker, one by one.\n" for n in range(40))
TEXT = ("# Decision register\n\nThe register's preface names the zinnia rule.\n\n"
        "## Interlude\n\nA note before the pool on the lotus rule.\n\n"
        "### DEC-476 — The pool\n- **Status:** ACCEPTED\n- **Decision:** the pool holds marigold workers.\n"
        f"{FILLER}- **Last:** the tamarind clause closes the entry.\n\n"
        "### DEC-999 — The queue\n- **Status:** ACCEPTED\n- **Decision:** the queue holds juniper tasks.\n")
MARK = ("entry", "status", "changed_by", "in_force", "not_in_force")
LABEL = ("id", *MARK, "also")


def _line(text):
    return TEXT.split("\n").index(text) + 1


GAP, POOL, QUEUE = _line("## Interlude"), _line("### DEC-476 — The pool"), _line("### DEC-999 — The queue")
POOL_END, QUEUE_END = _line("- **Last:** the tamarind clause closes the entry."), len(TEXT.rstrip("\n").split("\n"))


def _stand_ins(monkeypatch, module):
    """No model: no reranker, no semantic route."""
    monkeypatch.setattr(module, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(module, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A repository whose path map names the register; the gap's and DEC-476's parents widened."""
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_a, **_k: {"available": False, "reason": "off", "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda root: False)
    _stand_ins(monkeypatch, retrieve)
    for rel, text in {".gitignore": ".gov-runtime/\n", "governance/project/path-map.yaml":
                      f"decision_register: {REGISTER}\n", REGISTER: TEXT}.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the register"]):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(tmp_path)})
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    real, widened = lexical.parent, {GAP: POOL_END, POOL: QUEUE_END}

    def parent(root, parent_id):
        found = real(root, parent_id)
        return found and {**found, "end_line": widened.get(found["start_line"], found["end_line"])}

    monkeypatch.setattr(lexical, "parent", parent)
    return tmp_path


def _register_items(bundle):
    return [item for item in bundle["evidence"] if item["path"] == REGISTER]


def _label(item):
    return {key: item[key] for key in LABEL if key in item}


# -- S2: the entry holding the first line, or the chunk id ----------------------------------------------------------

def test_the_planted_parents_are_what_the_cases_need(project):
    sections = {chunk["start_line"]: lexical.parent(project, chunk["parent_id"]) for chunk in lexical.chunks(project)
                if chunk["path"] == REGISTER}
    assert (sections[GAP]["start_line"], sections[GAP]["end_line"]) == (GAP, POOL_END)
    assert (sections[POOL]["start_line"], sections[POOL]["end_line"]) == (POOL, QUEUE_END)
    assert len([start for start in sections if POOL <= start <= POOL_END]) > 1  # DEC-476 is cut into chunks


def test_an_item_starting_in_a_gap_before_dec_476_carries_its_chunk_id(project):
    [item] = _register_items(retrieve.retrieve(project, "lotus"))
    assert (item["start_line"], item["end_line"]) == (GAP, POOL_END)  # the gap, then the whole of DEC-476
    assert item["id"] == item["chunk_id"] and item["id"] != "DEC-476"
    assert not {key for key in MARK if key in item}, item  # no entry of its own
    assert [mark["entry"] for mark in item["also"]] == ["DEC-476"]  # the entry it touches, named beside
    assert item["also"][0] == {"entry": "DEC-476", "status": "ACCEPTED", "changed_by": [], "in_force": True}


def test_an_item_starting_inside_dec_476_carries_dec_476(project):
    items = _register_items(retrieve.retrieve(project, "tamarind", bundle_budget=60))  # too small to expand
    assert [(item["id"], item["entry"], item["end_line"]) for item in items] == [("DEC-476", "DEC-476", QUEUE - 1)]
    assert POOL < items[0]["start_line"] and "also" not in items[0]  # a child inside the entry, not its heading


def test_a_parent_starting_inside_dec_476_over_dec_999_carries_dec_476_and_names_dec_999(project):
    [item] = _register_items(retrieve.retrieve(project, "marigold"))
    assert (item["start_line"], item["end_line"]) == (POOL, QUEUE_END)
    assert (item["id"], item["entry"], item["status"], item["in_force"]) == ("DEC-476", "DEC-476", "ACCEPTED", True)
    assert [mark["entry"] for mark in item["also"]] == ["DEC-999"]


def test_a_preface_item_carries_its_chunk_id_and_no_mark(project):
    [item] = _register_items(retrieve.retrieve(project, "zinnia"))
    assert item["start_line"] == 1 and item["id"] == item["chunk_id"] and not set(LABEL[1:]) & set(item)


def test_every_register_item_s_id_agrees_with_its_entry_key(project):
    for query in ("lotus", "tamarind", "marigold", "zinnia", "juniper", "pool rule worker"):
        for item in _register_items(retrieve.retrieve(project, query)):
            assert item["id"] == item.get("entry", item["chunk_id"]), (query, item["start_line"])


# -- S3: nothing else in a bundle changes ---------------------------------------------------------------------------

def _before(monkeypatch):
    """``retrieve`` as it stood before the fix, loaded from git; skipped where the history does not hold it."""
    shown = subprocess.run(["git", "-C", str(REPO), "show", f"{BEFORE}:src/gov/retrieval/retrieve.py"],
                           capture_output=True, text=True)
    if shown.returncode:
        pytest.skip(f"the history does not hold {BEFORE[:12]}: {shown.stderr.strip()}")
    spec = importlib.util.spec_from_loader("gov.retrieval._retrieve_before_w2_133", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(shown.stdout, "retrieve_before_w2_133.py", "exec"), module.__dict__)
    _stand_ins(monkeypatch, module)
    return module


CALLS = [("lotus", {}), ("tamarind", {}), ("tamarind", {"bundle_budget": 60}), ("marigold", {}), ("zinnia", {}),
         ("juniper", {}), ("pool rule worker", {}), ("pool rule worker", {"batch_size": 1}),
         ("lotus marigold juniper", {"batch_size": 2}), ("label", {"ids": ["DEC-476"], "radius": 1})]


def test_the_bundle_is_the_same_before_and_after_but_for_a_gap_starter_s_label(project, monkeypatch):
    # one test over every call, not parametrised: the opt-in lists keep only a parametrised test's first row
    before, gap_starters, inside = _before(monkeypatch), 0, 0
    for query, kwargs in CALLS:
        old = before.retrieve(project, query, **kwargs)
        new = retrieve.retrieve(project, query, **kwargs)
        assert set(old) == set(new), (query, kwargs)
        for key in set(new) - {"evidence"}:  # the batches, budget, gaps, continuation, expansions, drops, facets
            assert old[key] == new[key], (query, kwargs, key)
        assert len(old["evidence"]) == len(new["evidence"]), (query, kwargs)
        for was, now in zip(old["evidence"], new["evidence"]):  # the same items in the same order
            assert {k: v for k, v in was.items() if k not in LABEL} == {k: v for k, v in now.items() if k not in LABEL}
            if now["path"] == REGISTER and now["start_line"] < POOL and "also" in now:  # a gap starter: its label
                gap_starters += 1
                assert was["id"] == was["entry"] == "DEC-476" and now["id"] == now["chunk_id"], (query, kwargs)
                assert now["also"] == [{k: was[k] for k in MARK if k in was}, *was.get("also", ())]
            else:  # every other item, a register item inside an entry among them, is the same as before
                inside += now["path"] == REGISTER and now["start_line"] >= POOL
                assert was == now, (query, kwargs, now["start_line"])
    assert gap_starters >= 2 and inside >= 4, (gap_starters, inside)


def test_the_continuation_carries_on_the_same_before_and_after(project, monkeypatch):
    before = _before(monkeypatch)
    old = before.retrieve(project, "lotus marigold juniper", batch_size=1)
    new = retrieve.retrieve(project, "lotus marigold juniper", batch_size=1)
    assert new["continuation"] is not None and old["continuation"] == new["continuation"]
    old_next = before.retrieve(project, "lotus marigold juniper", batch_size=1, continuation=old["continuation"])
    new_next = retrieve.retrieve(project, "lotus marigold juniper", batch_size=1, continuation=new["continuation"])
    strip = lambda bundle: [{k: v for k, v in item.items() if k not in LABEL} for item in bundle["evidence"]]  # noqa
    assert strip(old_next) == strip(new_next) and old_next["continuation"] == new_next["continuation"]
