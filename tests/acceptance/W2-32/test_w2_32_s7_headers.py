"""S7's note under DEC-1067 order (5), index-time method 1 (the CTO, 2026-11-04): contextual headers when embedded.

The note: each chunk is embedded with a deterministic header of its file path and the headings above it (title,
section); the keyword chunk and the evidence text unchanged; behind a setting off by default
(``governance/project/rebuild.yaml``: ``embed_headers: true|false``); switching it changes the manifest's embedding
recipe, so the next rebuild re-embeds.

- **On:** the text the stand-in embedder was sent for a chunk (the text its stored vector was made from) is a header
  followed by the chunk's own text (its file's lines, as the keyword index holds them). The header names the file's
  path and, in order, the headings the chunk lies under (title, section, subsection); it names no heading the chunk
  does not lie under and no word of the file's body. A file with no headings: the header names its path alone. The
  header is the same in two projects holding the same files. A chunk above the embedder's limit is sent header and
  all within the length the same chunk is sent at with the setting off.
- **Unchanged:** the keyword index (chunks, parents, the full-text rows), the evidence ``retrieve`` returns and the
  texts the reranker is given are the same with the setting on as off.
- **Off:** with no ``rebuild.yaml``, one without the key, or ``embed_headers: false``, the embedder is sent each chunk's
  own text exactly, as today.
- **Invalid:** any value but the booleans ``true`` and ``false`` (``yes``, ``1``, a quoted ``"true"``, a word) refuses
  with ``CONFIG_INVALID`` naming ``embed_headers``, and no chunk is sent to the embedder (never a guess of on or off).
- **Switched:** after a rebuild with it off, turning it on makes the store stale (a search that may not refresh
  answers unavailable, with no hit), the manifest's recipe changes, and the next rebuild re-embeds every chunk with its
  header; turning it off again does the same back.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pytest

import w2_32_support as s

SETTINGS_REL = "governance/project/rebuild.yaml"
LIMIT_CHARS = 16_384  # as test_w2_32_s7_dec1067.py: no limit of the embedder's context lies above it

MANUAL = "docs/tide-manual.md"
TITLE, PILOTS, NIGHT, LEDGER, FEES = ("Harbour pilotage handbook", "Pilot boats", "Night pilots", "Mooring ledger",
                                      "Harbour fees")
COLOURS = ("tarred", "hempen", "manila", "sisal", "coir")
MANUAL_TEXT = (
    f"# {TITLE}\n\nThe handbook gathers the standing orders of the quay.\n\n"
    f"## {PILOTS}\n\nPilot boats leave the quay at slack water.\n\n"
    f"### {NIGHT}\n\nNight pilots carry a green lantern on the bow.\n\n"
    f"## {LEDGER}\n\n"
    + "".join(f"Ledger line {i:02d}: the warden logs the {COLOURS[i % 5]} hawser at berth number {i}.\n"
              for i in range(40))
    + f"\n## {FEES}\n\nHarbour fees are paid in copper tokens at the gatehouse.\n")
HEADINGS = (TITLE, PILOTS, NIGHT, LEDGER, FEES)
MEMO = "docs/memo.md"
MEMO_TEXT = ("The quartermaster tallies brass buoys, oakum bales and spare cordage before winter.\n\n"
             "Spare oars are stacked beside the slipway.\n")
PLAIN = "docs/stores.txt"
PLAIN_TEXT = "Victualling: biscuit casks, salted cod and lime juice for the crossing.\n"
FILES = {**s.NOTES, MANUAL: MANUAL_TEXT, MEMO: MEMO_TEXT, PLAIN: PLAIN_TEXT}
QUESTION = "When do the night pilots carry a green lantern?"

LONG = "docs/ledger-table.md"
LONG_LINE = "".join(f"| ledger cell {i:05d} quill |" for i in range(1700)) + "\n"
LONG_TEXT = "# Ledger table\n\n" + LONG_LINE


# ---- planting and reading ----------------------------------------------------------------------------------------

def _settle(project, text, commit_it=True):
    """Write the project's ``rebuild.yaml`` (``None``: remove it); commit it unless ``commit_it`` is false (the file is
    read as it stands in the working tree, W2-M073)."""
    path = Path(project) / SETTINGS_REL
    if text is None:
        if path.exists():
            path.unlink()
    else:
        s.write(project, SETTINGS_REL, text)
    if commit_it:
        s.commit(project, "the rebuild settings")


def _settings_unindexed(project):
    """Give the project a path map whose settings file is in a namespace of its own, not indexed and not embedded, so
    switching the setting changes no indexed file: a store made stale by the switch is stale by the setting alone."""
    import yaml
    document = yaml.safe_load((Path(project) / s.PATH_MAP_REL).read_text(encoding="utf-8"))
    document["namespaces"]["project"]["paths"] = [s.PATH_MAP_REL, s.SECRETS_REL, s.MODELS_REL, ".gitignore"]
    document["namespaces"]["settings"] = {**s.namespace([SETTINGS_REL], "not embedded"),
                                          "lexical_policy": "not indexed"}
    s.write(project, s.PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    s.commit(project, "the settings file kept out of the index")


def _project(tmp_path, name, setting, files=FILES):
    """A planted project whose ``rebuild.yaml`` holds ``embed_headers: <setting>`` (``None``: no file)."""
    project = s.plant(tmp_path / name, files)
    if setting is not None:
        _settle(project, f"embed_headers: {setting}\n")
    return project


def _chunks(project):
    """``(path, start_line, end_line) -> text`` of every keyword chunk of an embedded file: its file's lines."""
    connection = sqlite3.connect(f"file:{Path(project) / s.STORE_REL}?mode=ro", uri=True)
    try:
        rows = connection.execute("SELECT chunk_id, path, start_line, end_line FROM lexical_chunk").fetchall()
    finally:
        connection.close()
    out = {}
    for chunk_id, path, start, end in rows:
        lines = (Path(project) / path).read_text(encoding="utf-8").splitlines(keepends=True)
        out[chunk_id] = ((path, start, end), "".join(lines[start - 1:end]))
    return out


def _sent(project, standin):
    """``(path, start_line, end_line) -> (chunk text, the text the stand-in made the chunk's stored vector from)``."""
    chunks = _chunks(project)
    return {chunks[chunk_id][0]: (chunks[chunk_id][1], standin.text_of.get(vector))
            for chunk_id, (_, vector) in s.vectors(project).items()}


def _header(sent, chunk):
    """What the embedder was sent ahead of the chunk's own text, or None when the text sent does not end with it."""
    body, whole = chunk.strip(), (sent or "").rstrip()
    if not body or not whole.endswith(body):
        return None
    return whole[:len(whole) - len(body)]


def _words(text):
    return set(re.findall(r"[a-z]{4,}", text.lower()))


def _body_words(path, text):
    """The file's words outside its headings and its path: none may be in a header."""
    body = "".join(line for line in text.splitlines(keepends=True) if not line.lstrip().startswith("#"))
    headings = " ".join(line for line in text.splitlines() if line.lstrip().startswith("#"))
    return _words(body) - _words(headings) - _words(path)


def _above(text, start_line):
    """The headings a chunk starting at ``start_line`` lies under, outermost first: those still open before its first
    non-blank line, less any its own first heading closes."""
    lines = text.splitlines()
    first = start_line
    while first <= len(lines) and not lines[first - 1].strip():
        first += 1
    stack = []
    for number, line in enumerate(lines, 1):
        found = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if number > first:
            break
        if found:
            level = len(found.group(1))
            stack = [entry for entry in stack if entry[0] < level]
            if number < first:
                stack.append((level, found.group(2)))
    return [heading for _, heading in stack]


def _names_in_order(header, headings):
    low = " ".join(header.lower().split())
    places = [low.find(heading.lower()) for heading in headings]
    return all(place >= 0 for place in places) and places == sorted(places)


def _store(envelope):
    return s.semantic_store(envelope)


def _headed(sent):
    """The chunks whose text sent holds more than their own text (the setting took effect)."""
    return [key for key, (chunk, text) in sent.items() if text is not None and text != chunk]


# ---- on: the header ----------------------------------------------------------------------------------------------

def test_with_the_setting_on_each_chunk_is_embedded_after_a_header_of_its_path_and_the_headings_above_it(
        tmp_path, needs_vectors, box, standin):
    project = _project(tmp_path, "on", "true")
    box.built(project)
    sent = {key: value for key, value in _sent(project, standin).items() if key[0] == MANUAL}
    assert len(sent) >= 5, f"premise: the manual is several chunks: {sorted(sent)}"
    continued = [key for key, (chunk, _) in sent.items() if _above(MANUAL_TEXT, key[1])[-1:] == [LEDGER]
                 and LEDGER not in chunk]
    assert continued, f"premise: a chunk of '{LEDGER}' that does not hold its heading: {sorted(sent)}"
    assert any(NIGHT in chunk and PILOTS not in chunk for chunk, _ in sent.values()), \
        f"premise: '{NIGHT}' is a chunk under '{PILOTS}' without it"
    body = _body_words(MANUAL, MANUAL_TEXT)
    for key, (chunk, text) in sorted(sent.items()):
        header = _header(text, chunk)
        assert header is not None and header.strip(), \
            f"{key}: the embedder was not sent a header followed by the chunk's text: {(text or '')[:300]!r}"
        assert MANUAL in header, f"{key}: the header does not name the file's path: {header!r}"
        above = _above(MANUAL_TEXT, key[1])
        assert _names_in_order(header, above), \
            f"{key}: the header does not name, in order, the headings the chunk lies under {above}: {header!r}"
        inside = [heading for heading in HEADINGS if heading in chunk]
        stray = [heading for heading in HEADINGS if heading not in above and heading not in inside
                 and heading.lower() in header.lower()]
        assert not stray, f"{key}: the header names headings the chunk does not lie under {stray}: {header!r}"
        leaked = sorted(_words(header) & body)
        assert not leaked, f"{key}: the header holds words of the file's body {leaked}: {header!r}"


def test_a_file_with_no_headings_is_embedded_after_a_header_of_its_path_alone(tmp_path, needs_vectors, box, standin):
    project = _project(tmp_path, "on", "true")
    box.built(project)
    sent = _sent(project, standin)
    for path, text_of_file in ((MEMO, MEMO_TEXT), (PLAIN, PLAIN_TEXT)):
        mine = {key: value for key, value in sent.items() if key[0] == path}
        assert mine, f"premise: {path} is embedded"
        body = _body_words(path, text_of_file)
        for key, (chunk, text) in mine.items():
            header = _header(text, chunk)
            assert header is not None and header.strip(), \
                f"{key}: the embedder was not sent a header followed by the chunk's text: {(text or '')[:300]!r}"
            assert path in header, f"{key}: the header does not name the file's path: {header!r}"
            leaked = sorted(_words(header) & body)
            others = [heading for heading in HEADINGS if heading.lower() in header.lower()]
            assert not leaked and not others, \
                f"{key}: a file with no headings is headed by its path alone, not {leaked or others}: {header!r}"


def test_the_header_is_deterministic(tmp_path, needs_vectors, box, standin):
    one = _project(tmp_path, "one", "true")
    two = _project(tmp_path / "elsewhere" / "deeper", "two", "true")
    box.built(one)
    first = _sent(one, standin)
    box.built(two)
    second = _sent(two, standin)
    assert _headed(first), "premise: the setting took effect (a chunk was sent with a header)"
    assert set(first) == set(second), "premise: the two projects hold the same chunks"
    differ = [key for key in first if first[key][1] != second[key][1]]
    assert not differ, f"the same chunk was sent two texts in two projects with the same files: " \
                       f"{[(first[key][1][:120], second[key][1][:120]) for key in differ[:2]]}"
    rooted = [key for key, (_, text) in first.items() if str(tmp_path) in (text or "")]
    assert not rooted, f"a header names the project's place on disk, not the file's path: {rooted[:3]}"


def test_a_headed_chunk_stays_within_the_embedders_limit(tmp_path, needs_vectors, box, standin):
    files = {**s.NOTES, LONG: LONG_TEXT}
    off = _project(tmp_path, "off", None, files)
    box.built(off)
    plain = [text for (path, _, _), (_, text) in _sent(off, standin).items() if path == LONG]
    assert plain and all(text for text in plain), "premise: the long chunk is embedded with the setting off"
    on = _project(tmp_path, "on", "true", files)
    envelope = box.built(on)
    headed = {key: value for key, value in _sent(on, standin).items() if key[0] == LONG}
    assert headed, "the long chunk has no vector with the setting on"
    for key, (chunk, text) in headed.items():
        start = chunk.strip()[:60]
        place = (text or "").find(start)
        assert place > 0 and LONG in text[:place], \
            f"{key}: the long chunk was not sent after a header naming its path: {(text or '')[:200]!r}"
        assert chunk.strip().startswith(text[place:].rstrip()), \
            f"{key}: what follows the header is not the chunk's first part: {text[place:place + 200]!r}"
        assert len(text) <= max(len(found) for found in plain) and len(text) <= LIMIT_CHARS, \
            f"{key}: header and chunk were sent as {len(text)} characters, past the limit the chunk is sent at " \
            f"with the setting off ({max(len(found) for found in plain)})"
    assert LONG in json.dumps(envelope.get("result") or {}), \
        f"the rebuild's report does not name the chunk embedded from its first part: {_store(envelope)}"


# ---- on: what does not change ------------------------------------------------------------------------------------

def _keyword_index(project):
    """The keyword index of the embedded files: chunk and parent rows of ``docs/**`` and ``README.md``, and every
    full-text row but the settings file's."""
    connection = sqlite3.connect(f"file:{Path(project) / s.STORE_REL}?mode=ro", uri=True)
    try:
        chunks = sorted(connection.execute(
            "SELECT chunk_id, path, start_line, end_line, parent_id FROM lexical_chunk "
            "WHERE path LIKE 'docs/%' OR path = 'README.md'").fetchall())
        parents = sorted(connection.execute(
            "SELECT parent_id, path, kind, start_line, end_line FROM lexical_parent "
            "WHERE path LIKE 'docs/%' OR path = 'README.md'").fetchall())
        columns = [row[1] for row in connection.execute("PRAGMA table_info(lexical_fts)")]
        texts = sorted(map(repr, (row for row in connection.execute(
            f"SELECT {', '.join(columns)} FROM lexical_fts") if "embed_headers" not in repr(row))))
    finally:
        connection.close()
    return {"chunks": chunks, "parents": parents, "full text": texts}


def test_the_keyword_chunk_and_the_evidence_are_unchanged_with_the_setting_on(tmp_path, needs_vectors, box, standin):
    off = _project(tmp_path, "off", "false")
    on = _project(tmp_path, "on", "true")
    box.built(off)
    box.built(on)
    assert _headed(_sent(on, standin)), "premise: the setting took effect (a chunk was sent with a header)"
    before, after = _keyword_index(off), _keyword_index(on)
    for part in before:
        assert before[part] == after[part], f"the keyword index's {part} differ with the setting on"
    plain = s.result(box.call("retrieve", root=str(off), query=QUESTION, reranker="constant"))
    headed = s.result(box.call("retrieve", root=str(on), query=QUESTION, reranker="constant"))
    assert headed["evidence"], "premise: the question is answered with the setting on"
    lines = {}
    for item in headed["evidence"]:
        text = (Path(on) / item["path"]).read_text(encoding="utf-8").splitlines(keepends=True)
        lines[item["path"], item["start_line"], item["end_line"]] = item["text"]
        assert item["text"] == "".join(text[item["start_line"] - 1:item["end_line"]]), \
            f"the evidence for {item['path']}:{item['start_line']}-{item['end_line']} is not its lines: " \
            f"{item['text'][:200]!r}"
    common = [(key, item["text"]) for item in plain["evidence"]
              if (key := (item["path"], item["start_line"], item["end_line"])) in lines]
    assert common, "premise: the two answers cite a span in common"
    assert all(lines[key] == text for key, text in common), "the evidence text differs with the setting on"


def test_the_rerankers_input_is_unchanged_with_the_setting_on(tmp_path, needs_vectors, box, standin):
    read = {}
    for setting in ("false", "true"):
        project = _project(tmp_path, setting, setting)
        box.built(project)
        if setting == "true":
            assert _headed(_sent(project, standin)), "premise: the setting took effect (a chunk was sent with a header)"
        record = Path(box.workdir) / f"rerank-{setting}.jsonl"
        s.result(box.call("retrieve", root=str(project), query=QUESTION, reranker=f"record:{record}:lantern",
                          radius=0))
        given = [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines()] \
            if record.exists() else []
        chunks = list(_chunks(project).values())
        by_chunk = {}
        for text in given:
            holding = [key for key, chunk in chunks if chunk.strip() and chunk.strip() in text]
            if holding:
                by_chunk[max(holding, key=lambda key: key[2] - key[1])] = text
        read[setting] = by_chunk
    common = set(read["false"]) & set(read["true"])
    assert len(common) >= 3 and any(key[0] == MANUAL for key in common), \
        f"premise: the reranker read the same chunks in both projects: {sorted(common)}"
    differ = [key for key in common if read["false"][key] != read["true"][key]]
    assert not differ, f"the reranker was given another text with the setting on: " \
                       f"{[(read['false'][key][:120], read['true'][key][:120]) for key in differ[:2]]}"


# ---- off: as today -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("settings", [None, "slow_after_s: 1800\n", "embed_headers: false\n"],
                         ids=["no-file", "no-key", "false"])
def test_with_the_setting_absent_or_false_the_embedder_receives_the_chunk_as_today(
        tmp_path, needs_vectors, box, standin, settings):
    project = s.plant(tmp_path / "project", FILES)
    if settings is not None:
        _settle(project, settings)
    box.built(project)
    sent = _sent(project, standin)
    assert sent and {MANUAL, MEMO, PLAIN} <= {key[0] for key in sent}, f"premise: the files are embedded: {sent}"
    changed = [(key, text[:160]) for key, (chunk, text) in sorted(sent.items()) if text != chunk]
    assert not changed, f"with the setting off the embedder is sent each chunk's own text exactly: {changed[:3]}"


# ---- invalid -------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["yes", "1", '"true"', "headers"])
def test_an_invalid_setting_is_refused_with_config_invalid_naming_the_key(tmp_path, needs_vectors, box, standin, value):
    project = _project(tmp_path, "project", value)
    envelope = box.rebuild(project)
    answer = json.dumps({key: item for key, item in envelope.items() if key != "_stderr"})
    assert "CONFIG_INVALID" in answer and "embed_headers" in answer, \
        f"embed_headers: {value} was not refused with CONFIG_INVALID naming the key: {answer[:2000]}"
    sent = standin.texts_embedded()
    assert not sent, f"embed_headers: {value} was refused, yet {len(sent)} texts were sent to the embedder"
    assert not s.vector_paths(project), f"embed_headers: {value}: vectors were stored under an invalid setting"


# ---- switched ------------------------------------------------------------------------------------------------------

def test_switching_the_setting_makes_the_store_stale_and_the_next_rebuild_re_embeds_every_chunk(
        tmp_path, needs_vectors, box, standin):
    project = _project(tmp_path, "project", None)
    _settings_unindexed(project)
    box.built(project)
    first = _sent(project, standin)
    assert first and not _headed(first), "premise: the default build sends each chunk's own text"
    recipe = s.result(box.call("manifest", root=str(project)))
    for setting in ("true", "false"):
        _settle(project, f"embed_headers: {setting}\n", commit_it=False)
        stale = s.result(box.call("semantic_search", root=str(project), query=QUESTION))
        assert stale["available"] is False and stale["hits"] == [], \
            f"after switching embed_headers to {setting} without a rebuild, the store was answered from: " \
            f"{json.dumps(stale)[:600]}"
        box.built(project)
        sent = _sent(project, standin)
        assert set(sent) == set(first), f"the same chunks have vectors after switching to {setting}"
        if setting == "true":
            plain = [key for key, (chunk, text) in sent.items()
                     if not (_header(text, chunk) or "").strip() or key[0] not in (_header(text, chunk) or "")]
            assert not plain, f"after switching on, chunks were not re-embedded with their header: {plain[:4]}"
        else:
            headed = _headed(sent)
            assert not headed, f"after switching off, chunks kept a vector made with a header: {headed[:4]}"
        renewed = s.result(box.call("manifest", root=str(project)))
        assert renewed != recipe, f"switching embed_headers to {setting} left the manifest's recipe as it was: {renewed}"
        recipe = renewed
