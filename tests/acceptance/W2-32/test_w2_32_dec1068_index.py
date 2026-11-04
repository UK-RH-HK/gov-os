"""DEC-1068's index-time methods M2, M5 and M4 (the ticket's note "DEC-1068, the five index-time methods"; notes
within S7 and S8). Each is behind a setting of ``governance/project/rebuild.yaml``, absent = off; the loader validates
it, ``CONFIG_INVALID`` naming the key.

- **M2, code chunks cut on definitions** (``chunk_code_by_definition``): a Python file's chunks begin at each
  top-level ``def``/``class`` and each method (the lines before it in its chunk blank or comments alone), no chunk
  runs on into one, every line is in a chunk, today's parents are kept and each chunk lies inside the parent it names;
  the other files' chunks are as today.
- **M5, one span per register entry** (``chunk_register_by_entry``): the register's (the path map's
  ``decision_register``) chunks are one per ``### DEC-`` entry, the entry as the store reads it (to the next heading
  outside a fenced block); a long entry is split within it; no chunk spans two entries; the chunks of an entry name
  one parent, the entry's span; the other files' chunks are as today.
- **M4, identifier tokenisation in the keyword index** (``lexical_split_identifiers``): a keyword search for a part
  of an identifier (``seed`` of ``rebuild_slot_seed``; ``Seeded`` and ``Rebuild`` of ``SeededRebuild``; ``trimmer`` of
  ``gov.lantern.wick_trimmer``) or of a path's segment (``ballast`` of ``tools/heavy_ballast.sh``) finds the chunk
  and the line; the whole identifier still finds what it finds today; no chunk changes.
- **Off:** no file, a file without the keys, or the three ``false``: today's chunks (spans and ids) and today's
  keyword answers exactly (``w2_32_dec1068_today.json``, recorded on integrate's head).
- **Switched:** turning a setting on, or off again, makes the store stale (the keyword route, and for M2 and M5 the
  vectors, answer unavailable without a rebuild); a refresh of the keyword index and the next rebuild build what the
  setting says; off again gives today's chunks back.
- **Invalid:** ``yes``, ``1``, a quoted ``"true"`` or a word refuses the rebuild with ``CONFIG_INVALID`` naming the key,
  and nothing is embedded.
"""

from __future__ import annotations

import json

import pytest

import w2_32_index_methods as m
import w2_32_support as s

QUESTION = "When does the harbour master publish the tide tables?"
OTHERS_THAN = {m.M2: set(m.PYTHON), m.M5: {m.REGISTER_REL}, m.M4: set()}  # the files each method may change


@pytest.fixture
def planted(tmp_path, needs_vectors):
    return m.plant(tmp_path / "project")


def _built(box, project, text):
    m.settle(project, text)
    box.built(project)
    return m.index(project)


# ---- off: today ----------------------------------------------------------------------------------------------------

OFF = {"no-file": None, "no-key": m.CONTROL, "false": m.CONTROL + "".join(f"{key}: false\n" for key in m.KEYS)}


@pytest.mark.parametrize("settings", list(OFF), ids=list(OFF))
def test_with_the_settings_off_the_chunks_are_todays(planted, box, standin, settings):
    got, today = _built(box, planted, OFF[settings]), m.today()
    assert m.spans(got["chunks"]) == m.spans(today["chunks"]), \
        f"with the settings off ({settings}) the chunks differ from today's: " \
        f"{sorted(set(m.spans(got['chunks'])) ^ set(m.spans(today['chunks'])))[:6]}"
    assert [chunk[6:] for chunk in got["chunks"]] == [chunk[6:] for chunk in today["chunks"]], \
        f"with the settings off ({settings}) the chunk or parent ids differ from today's: an upgrade with the " \
        f"settings off would make every store stale"
    assert got["parents"] == today["parents"], f"with the settings off ({settings}) the parents differ from today's"


@pytest.mark.parametrize("settings", list(OFF), ids=list(OFF))
def test_with_the_settings_off_the_keyword_answers_are_todays(planted, box, standin, settings):
    _built(box, planted, OFF[settings])
    got, today = m.answers(box, planted), m.today()["answers"]
    differ = {query: (got[query], today[query]) for query in m.QUERIES if got[query] != today[query]}
    assert not differ, f"with the settings off ({settings}) the keyword answers differ from today's " \
                       f"(got, today): {json.dumps(differ)[:1500]}"


# ---- M2 ------------------------------------------------------------------------------------------------------------

def test_m2_on_python_chunks_begin_at_each_definition_with_the_parents_kept(planted, box, standin):
    today = m.spans(m.today()["chunks"], m.PYTHON)
    assert any(chunk[0] == m.CODE_REL and chunk[1] < 61 <= chunk[2] and chunk[1] != 61 for chunk in today), \
        "premise: today a module chunk runs on into the class TideTable (line 61)"
    got = _built(box, planted, m.setting(m.M2, "true"))
    problems = m.m2_problems(got["chunks"], got["parents"])
    assert not problems, f"with {m.M2} on:\n" + "\n".join(problems)


def test_m2_on_changes_no_other_files_chunks(planted, box, standin):
    got = _built(box, planted, m.setting(m.M2, "true"))
    others = set(m.PLANTED) - OTHERS_THAN[m.M2]
    assert m.spans(got["chunks"], others) == m.spans(m.today()["chunks"], others), \
        f"with {m.M2} on, files that are not Python were chunked otherwise than today"


# ---- M5 ------------------------------------------------------------------------------------------------------------

def test_m5_on_the_registers_chunks_are_one_span_per_entry(planted, box, standin):
    assert m.m5_problems(m.today()["chunks"]), "premise: today's chunks of the register break M5 (DEC-902's fenced " \
                                               "'#' lines cut it)"
    got = _built(box, planted, m.setting(m.M5, "true"))
    problems = m.m5_problems(got["chunks"])
    assert not problems, f"with {m.M5} on:\n" + "\n".join(problems)


def test_m5_on_changes_no_other_files_chunks(planted, box, standin):
    got = _built(box, planted, m.setting(m.M5, "true"))
    others = set(m.PLANTED) - OTHERS_THAN[m.M5]
    assert m.spans(got["chunks"], others) == m.spans(m.today()["chunks"], others), \
        f"with {m.M5} on, files other than the register were chunked otherwise than today"


# ---- M4 ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("query,rel,line", m.PARTS, ids=[query for query, _, _ in m.PARTS])
def test_m4_on_a_part_of_an_identifier_or_a_path_finds_its_chunk(planted, box, standin, query, rel, line):
    today = m.today()["answers"][query]
    assert not any(item[0] == rel for item in today["ranked"]) and not today["hits"], \
        f"premise: today {query!r} finds nothing in {rel}: {today}"
    _built(box, planted, m.setting(m.M4, "true"))
    answer = m.search(box, planted, query)
    assert answer["available"], f"with {m.M4} on the keyword route answered unavailable ({answer['reason']})"
    assert any(item[0] == rel and item[1] <= line <= item[2] for item in answer["ranked"]), \
        f"with {m.M4} on, {query!r} does not find the chunk of {rel} holding line {line} " \
        f"({m.FILES[rel].splitlines()[line - 1]!r}): {answer['ranked'][:6]}"
    expected = [rel, line, m.FILES[rel].splitlines()[line - 1]]
    assert expected in answer["hits"], f"with {m.M4} on, {query!r} does not hit {rel}:{line}: {answer['hits'][:6]}"
    for path, number, text in answer["hits"]:
        assert m.FILES[path].splitlines()[number - 1] == text, \
            f"with {m.M4} on, a hit's text is not its file's line ({path}:{number}): {text!r}"


@pytest.mark.parametrize("query,rel,line", m.WHOLES, ids=[query for query, _, _ in m.WHOLES])
def test_m4_on_the_whole_identifier_still_matches(planted, box, standin, query, rel, line):
    today = m.today()["answers"][query]
    assert [rel, line, m.FILES[rel].splitlines()[line - 1]] in today["hits"], f"premise: today {query!r} hits {rel}"
    _built(box, planted, m.setting(m.M4, "true"))
    answer = m.search(box, planted, query)
    assert answer["hits"] == today["hits"], \
        f"with {m.M4} on, {query!r} hits {answer['hits']} where today it hits {today['hits']}"
    assert any(item[0] == rel and item[1] <= line <= item[2] for item in answer["ranked"]), \
        f"with {m.M4} on, {query!r} no longer finds the chunk of {rel}: {answer['ranked'][:6]}"


def test_m4_on_changes_no_chunk(planted, box, standin):
    got = _built(box, planted, m.setting(m.M4, "true"))
    assert m.spans(got["chunks"]) == m.spans(m.today()["chunks"]) and got["parents"] == m.today()["parents"], \
        f"with {m.M4} on the chunks or parents differ from today's (it adds index terms alone)"


# ---- switched ------------------------------------------------------------------------------------------------------

def _problems(key, box, project, refresh=False):
    if key == m.M4:
        return m.m4_problems(box, project, refresh=refresh)
    if refresh:
        m.search(box, project, "lantern", refresh=True)
    got = m.index(project)
    return m.m2_problems(got["chunks"], got["parents"]) if key == m.M2 else m.m5_problems(got["chunks"])


def _stale(box, project, key, said):
    keyword = m.search(box, project, "lantern")
    assert keyword["available"] is False and keyword["hits"] == [] and keyword["ranked"] == [], \
        f"after {said} without a rebuild, the keyword route answered from the store: {json.dumps(keyword)[:600]}"
    if key in (m.M2, m.M5):  # the chunks changed, so the vectors were made from other chunks
        vectors = s.result(box.call("semantic_search", root=str(project), query=QUESTION))
        assert vectors["available"] is False and vectors["hits"] == [], \
            f"after {said} without a rebuild, the vectors were searched: {json.dumps(vectors)[:600]}"


@pytest.mark.parametrize("key", m.KEYS)
def test_switching_a_setting_makes_the_store_stale_and_the_next_build_follows_it(planted, box, standin, key):
    first = _built(box, planted, None)
    m.settle(planted, m.CONTROL)
    keyword = m.search(box, planted, "lantern")
    vectors = s.result(box.call("semantic_search", root=str(planted), query=QUESTION))
    assert keyword["available"] and vectors["available"], \
        f"premise: writing the settings file without the key leaves the store fresh: {keyword}, " \
        f"{json.dumps(vectors)[:400]}"
    m.settle(planted, m.setting(key, "true"))
    _stale(box, planted, key, f"switching {key} on")
    refreshed = _problems(key, box, planted, refresh=True)
    assert not refreshed, f"after switching {key} on, a refresh of the keyword index did not build what it says:\n" \
                          + "\n".join(refreshed)
    box.built(planted)
    rebuilt = _problems(key, box, planted)
    assert not rebuilt, f"after switching {key} on, the rebuild did not build what it says:\n" + "\n".join(rebuilt)
    m.settle(planted, m.setting(key, "false"))
    _stale(box, planted, key, f"switching {key} off again")
    box.built(planted)
    back = m.index(planted)
    assert m.spans(back["chunks"]) == m.spans(first["chunks"]), f"after switching {key} off again the chunks are " \
                                                                f"not today's"
    if key == m.M4:
        found = m.search(box, planted, "seed")
        assert not any(item[0] == m.SNAKE_REL for item in found["ranked"]), \
            f"after switching {key} off again, 'seed' still finds rebuild_slot_seed: {found['ranked'][:4]}"


# ---- invalid -------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["yes", "1", '"true"', "split"])
@pytest.mark.parametrize("key", m.KEYS)
def test_an_invalid_value_is_refused_with_config_invalid_naming_the_key(planted, box, standin, key, value):
    m.settle(planted, m.setting(key, value))
    envelope = box.rebuild(planted)
    answer = json.dumps({name: item for name, item in envelope.items() if name != "_stderr"})
    assert "CONFIG_INVALID" in answer and key in answer, \
        f"{key}: {value} was not refused with CONFIG_INVALID naming the key: {answer[:2000]}"
    sent = standin.texts_embedded()
    assert not sent, f"{key}: {value} was refused, yet {len(sent)} texts were sent to the embedder"
