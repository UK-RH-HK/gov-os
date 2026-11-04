"""DEC-1068 (M1), a note within S7: a file-level index beside the chunk index (the CTO's note of 2026-11-04 ~09:30).

The note: a vector per file from its path, headings and opening; a file hit expanded to its best chunks; behind
``file_level_index`` in ``governance/project/rebuild.yaml``, off by default; the loader refuses an invalid value with
``CONFIG_INVALID`` naming the key; measured on the visible half and kept only if it wins.

- **The corpus:** ``docs/mate-notes.md``, small, whose title and two sections each hold one of the question's three
  word pairs (``semaphore codebook``, ``pennant hoists``, ``halyard drill``), so no single chunk holds more than one
  pair; and 42 notes, each dense in one pair (in its heading and twice in its body), which out-rank the target's chunks
  in both the keyword and the semantic route. Its path holds none of the question's words, so the keyword index's
  path terms do not reach it either. Worked out from the stand-in's own vectors (a premise of each case): the target's
  file vector (its path, its headings and its opening) is the nearest file to the question, and its best chunk is its
  ``Pennant hoists`` section.
- **On:** that best chunk is in ``retrieve``'s evidence; **off** (no file, no key, ``false``) it is not, and the bundle
  and the semantic route's answer are today's, byte for byte.
- **Switched:** turning it on after a rebuild makes the store stale (a search that may not refresh answers
  unavailable, with no hit) until the next rebuild; turning it off again does the same back.
- **Invalid:** ``yes``, ``1``, a quoted ``"true"``, a word: ``gov rebuild`` refuses with ``CONFIG_INVALID`` naming
  ``file_level_index``, and no chunk is sent to the embedder.
"""

from __future__ import annotations

import json
import math
import re
import sqlite3
import struct
from pathlib import Path

import pytest

import w2_32_methods as m
import w2_32_support as s

TARGET = "docs/mate-notes.md"
TARGET_TEXT = ("# Semaphore codebook\n\nKept aboard by mates.\n\n"
               "## Pennant hoists\n\nAt noon.\n\n"
               "## Halyard drill\n\nAt dusk daily.\n")
BEST = "Pennant hoists"
PAIRS = ("semaphore codebook", "pennant hoists", "halyard drill")
DISTRACTORS = {f"docs/log-{n:02d}.md": f"# {PAIRS[n % 3].capitalize()} {n}\n\n{PAIRS[n % 3]} {PAIRS[n % 3]}\n"
               for n in range(42)}
FILES = {**s.NOTES, **DISTRACTORS, TARGET: TARGET_TEXT}
QUESTION = "Which file covers semaphore codebook, pennant hoists and halyard drill?"


def _cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


def _file_text(path, text):
    """A file's path, headings and opening (its first line that is no heading), as the note names them."""
    lines = [line for line in text.splitlines() if line.strip()]
    headings = [line.lstrip("#").strip() for line in lines if line.startswith("#")]
    opening = next((line for line in lines if not line.startswith("#")), "")
    return " ".join([path, *headings, opening])


def _premise_of_the_corpus():
    question = s.stand_in_vector(s.PIN_MODEL, QUESTION)
    near = {path: _cosine(question, s.stand_in_vector(s.PIN_MODEL, _file_text(path, text)))
            for path, text in FILES.items()}
    first = max(near, key=near.get)
    assert first == TARGET, f"premise: the target's file vector is the nearest file ({first}: {near[first]:.3f}, " \
                            f"the target: {near[TARGET]:.3f})"
    assert not re.search(r"semaphore|codebook|pennant|hoists|halyard|drill", TARGET), "premise: no question word in its path"


def _build(tmp_path, box, name, setting=None, settings_text=None):
    project = m.plant(tmp_path / name, FILES)
    text = settings_text if settings_text is not None else (None if setting is None else f"{m.M1_KEY}: {setting}\n")
    m.settle(project, m.M1_SETTINGS_REL, text)
    box.built(project)
    return project


def _best_chunk(project, standin):
    """The target's chunk nearest the question by its stored vector (the semantic route's own measure), with the
    question's vector made from the text the stand-in was sent for it."""
    asked = [text for text in standin.texts_embedded(s.PIN_MODEL) if text.endswith(QUESTION)]
    assert asked, "premise: the question was sent to the stand-in embedder"
    question = s.stand_in_vector(s.PIN_MODEL, asked[-1])
    connection = sqlite3.connect(f"file:{Path(project) / s.STORE_REL}?mode=ro", uri=True)
    try:
        lines = {chunk_id: (start, end) for chunk_id, start, end in connection.execute(
            "SELECT chunk_id, start_line, end_line FROM lexical_chunk WHERE path = ?", (TARGET,))}
    finally:
        connection.close()
    scored = []
    for chunk_id, (path, vector) in s.vectors(project).items():
        if path == TARGET:
            values = [value for (value,) in struct.iter_unpack("f", vector)]
            scored.append((_cosine(question, values), lines[chunk_id]))
    assert scored, "premise: the target has vectors"
    top = max(score for score, _ in scored)
    return [span for score, span in scored if math.isclose(score, top, abs_tol=1e-6)]


def _target_items(bundle):
    return [(item["start_line"], item["end_line"]) for item in bundle["evidence"] if item["path"] == TARGET]


def _retrieve(box, project):
    return s.result(box.call("retrieve", root=str(project), query=QUESTION, reranker="constant", radius=0))


def test_with_the_file_level_index_on_a_question_spread_over_a_files_headings_reaches_its_best_chunk(
        tmp_path, needs_vectors, box, standin):
    _premise_of_the_corpus()
    off = _build(tmp_path, box, "off")
    assert not _target_items(_retrieve(box, off)), \
        "premise: with the file-level index off, no chunk of the target reaches the evidence"
    on = _build(tmp_path, box, "on", "true")
    bundle = _retrieve(box, on)  # the question's vector may come from the vector cache: its text is in the log above
    best = _best_chunk(on, standin)
    lines = TARGET_TEXT.splitlines()
    assert any(BEST in "\n".join(lines[start - 1:end]) for start, end in best), \
        f"premise: the target's best chunk is its '{BEST}' section: {best}"
    sent = _target_items(bundle)
    assert any(span in sent for span in best), \
        f"with {m.M1_KEY} on, the target's best chunk {best} is not in the evidence (the target's items: {sent}; " \
        f"the evidence: {s.first_paths(bundle['evidence'], 30)})"


@pytest.mark.parametrize("settings_text", ["slow_after_s: 1800\n", f"{m.M1_KEY}: false\n"], ids=["no-key", "false"])
def test_with_the_file_level_index_absent_or_false_the_answers_are_todays(
        tmp_path, needs_vectors, box, standin, settings_text):
    project = _build(tmp_path, box, "project")
    today = (_retrieve(box, project), s.result(box.call("semantic_search", root=str(project), query=QUESTION)))
    m.settle(project, m.M1_SETTINGS_REL, settings_text)
    box.built(project)
    off = (_retrieve(box, project), s.result(box.call("semantic_search", root=str(project), query=QUESTION)))
    for name, before, after in zip(("retrieve's bundle", "the semantic route's answer"), today, off):
        assert json.dumps(after, sort_keys=True) == json.dumps(before, sort_keys=True), \
            f"with {settings_text.strip()!r}, {name} is not today's"


def test_switching_the_file_level_index_makes_the_store_stale(tmp_path, needs_vectors, box, standin):
    project = _build(tmp_path, box, "project")
    for setting in ("true", "false"):
        m.settle(project, m.M1_SETTINGS_REL, f"{m.M1_KEY}: {setting}\n")
        stale = s.result(box.call("semantic_search", root=str(project), query=QUESTION))
        assert stale["available"] is False and stale["hits"] == [], \
            f"after switching {m.M1_KEY} to {setting} without a rebuild, the store was answered from: " \
            f"{json.dumps(stale)[:600]}"
        box.built(project)
        renewed = s.result(box.call("semantic_search", root=str(project), query=QUESTION))
        assert renewed["available"] is True, f"the rebuild after switching to {setting} did not renew the store"


@pytest.mark.parametrize("value", m.INVALID)
def test_an_invalid_file_level_index_is_config_invalid_naming_the_key(tmp_path, needs_vectors, box, standin, value):
    project = m.plant(tmp_path / "project", FILES)
    m.settle(project, m.M1_SETTINGS_REL, f"{m.M1_KEY}: {value}\n")
    answer = m.answer_text(box.rebuild(project))
    assert "CONFIG_INVALID" in answer and m.M1_KEY in answer, \
        f"{m.M1_KEY}: {value} was not refused with CONFIG_INVALID naming the key: {answer[:1500]}"
    assert not standin.texts_embedded(), f"{m.M1_KEY}: {value} was refused, yet texts were sent to the embedder"
