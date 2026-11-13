"""KPI 6 (S6; W2-M126): the supplementary query is built from the ticket's KPI lines and its title.

The packet carries the query it used under ``supplementary_query``; it holds words of the KPI lines and is not the
title's first long word alone; a planted document that matches only words of the KPI lines (none of the title's)
reaches the supplementary block.

Red reason, today: the query is the title's first long word (``Harbour``), the packet does not carry it, and the
datum note, which holds none of the title's words, is never found.
"""

from __future__ import annotations

import re

import pytest

import w2_04_support as s

TICKET = "TK-W204-QUERY"
TITLE = "Harbour lamps, north quay"
KPI_LINES = ("The tide gauge records the vermilion datum at dawn.",)
FAILURE_LINES = ("A vermilion datum is recorded at noon.",)
DATUM_NOTE = "docs/notes/datum.md"


def _words(text):
    return {word.lower() for word in re.findall(r"[A-Za-z]+", text)}


TITLE_WORDS = _words(TITLE)
KPI_ONLY_WORDS = _words(" ".join(KPI_LINES)) - TITLE_WORDS


@pytest.fixture(scope="module")
def quay(retrieval_api, tmp_path_factory):
    note = f"# Gauge records\n\n{KPI_LINES[0]}\n\nThe gauge stands by the sea wall.\n"
    assert not _words(note) & TITLE_WORDS, "the fixture is wrong: the note holds a word of the title"
    files = {DATUM_NOTE: note,
             "docs/notes/lamps.md": f"# {TITLE}\n\nThe lamps of the north quay are lit at dusk.\n",
             "docs/charter/charter.md": s.record(s.CHARTER_ID, "charter", "ACTIVE", s.CHARTER_TEXT),
             f".tickets/{TICKET}.md": s.ticket(TICKET, TITLE, [s.CHARTER_ID], kpis=KPI_LINES, failure=FAILURE_LINES)}
    project = s.build_project(tmp_path_factory.mktemp("w2-04-query") / "repo", files)
    retrieval_api.build(project.root)
    return project


def test_the_packet_carries_the_query_built_from_the_kpi_lines_and_the_title(retrieval_api, quay):
    packet = retrieval_api.gov(quay.root, TICKET).packet
    assert s.K_QUERY in packet, f"the packet does not carry the query it used under `{s.K_QUERY}`: {sorted(packet)}"
    query = packet[s.K_QUERY]
    text = " ".join(query) if isinstance(query, list) else str(query)
    assert _words(text) & KPI_ONLY_WORDS, f"the query holds no word of the KPI lines that the title lacks: {query!r}"
    first_long = next(word for word in TITLE.split() if len(word) > 2)
    assert text.strip() != first_long, f"the query is the title's first long word alone: {query!r}"


def test_a_document_matching_only_the_kpi_lines_reaches_the_supplementary_block(retrieval_api, quay):
    packet = retrieval_api.gov(quay.root, TICKET).packet
    paths = [item["path"] for item in packet[s.K_SUPPLEMENTARY]]
    assert DATUM_NOTE in paths, f"the note that matches the KPI lines alone is not supplementary: {paths}"
