"""KPI success 2 and failure 2: a symbol named in a plain question is asked of the code index with the code-graph
tool's own traversal, in small answers, and the file spans it returns join the fusion as a route."""

from __future__ import annotations

import json
import subprocess

import pytest

import w2_92_support as support

WHO_CALLS = f"who calls {support.LEAF}"
BOTH = f"who calls {support.LEAF} under {support.NAMED_DEC}"


def _calls_spans(bundle, callers):
    return [name for name in callers if not support.covers(bundle, *support.SPANS[name])]


def test_c0_premise_the_stand_in_sees_a_whole_graph_query_when_one_is_sent(api):
    """The detector itself: a query over every edge, sent through the recording stand-in, is named whole-graph, and
    one asking more rows than the cap is named over the cap. Green before and after the implementation."""
    path, log = api.tool_path(support.RECORDING)
    env = api.env(path)
    env.update({"CBM_RUNTIME_DIR": str(api.workdir / "tmp"), "CBM_CACHE_DIR": str(api.workdir / "tmp" / "cache")})
    for args in ({"project": "code", "query": "MATCH (a)-[r]->(b) RETURN a.name, b.name", "max_rows": 50},
                 {"project": "code", "query": f"MATCH (a) WHERE a.name = '{support.LEAF}' RETURN a.name",
                  "max_rows": support.ROW_CAP + 1}):
        subprocess.run([support.TOOL, "cli", "--quiet", "--json", "query_graph", json.dumps(args)], env=env,
                       capture_output=True, timeout=support.CALL_TIMEOUT_S, cwd=str(api.workdir / "elsewhere"),
                       stdin=subprocess.DEVNULL)
    sent = support.requests(log)
    assert [entry["tool"] for entry in sent] == ["query_graph", "query_graph"], sent
    assert support.whole_graph(sent[0], [support.LEAF]) and not support.over_the_cap(sent[0]), sent[0]
    assert not support.whole_graph(sent[1], [support.LEAF]) and support.over_the_cap(sent[1]), sent[1]


def test_c1_who_calls_a_symbol_brings_its_callers_spans(asked):
    """"who calls w92_leaf": the spans of w92_mid and w92_side (app/middle.py) reach the bundle (DEC-957, CAP-12)."""
    bundle, _ = asked("full", WHO_CALLS)
    missing = _calls_spans(bundle, support.CALLERS[support.LEAF])
    assert not missing, (
        f"the callers {missing} of {support.LEAF} ({[support.SPANS[name] for name in missing]}) are not in the "
        f"bundle of {WHO_CALLS!r}; it holds {support.items(bundle)}")


def test_c2_the_code_route_asks_the_tools_traversal_never_the_whole_graph_nor_over_the_cap(asked):
    """Failure 2: the code index is asked about the symbol by the tool's own traversal (``trace_path``,
    ``search_graph``, ``query_graph`` naming it); no request asks the whole graph or more rows than the cap."""
    _, sent = asked("full", WHO_CALLS)
    graph = [entry for entry in sent if entry["tool"] in support.GRAPH_QUESTIONS]
    assert any(support.names_a_symbol(entry, support.LEAF) for entry in graph), (
        f"the code-graph tool was not asked about {support.LEAF} by its own traversal; it was sent "
        f"{[(entry['tool'], entry['args']) for entry in sent]}")
    whole = [entry for entry in sent if support.whole_graph(entry, [support.LEAF])]
    assert not whole, f"a whole-graph query was sent to the code-graph tool (DEC-859): {whole}"
    over = [entry for entry in sent if support.over_the_cap(entry)]
    assert not over, f"a request over the tool's row cap of {support.ROW_CAP} was sent or refused: {over}"


def test_c3_a_question_naming_both_a_record_and_a_symbol_takes_both_routes(asked):
    bundle, sent = asked("full", BOTH)
    assert support.holds_text(bundle, support.NAMED_DEC_TEXT), \
        f"{support.NAMED_DEC}'s evidence is not in the bundle of {BOTH!r}: {support.items(bundle)}"
    missing = _calls_spans(bundle, support.CALLERS[support.LEAF])
    assert not missing, f"the callers {missing} are not in the bundle of {BOTH!r}: {support.items(bundle)}"
    assert not [entry for entry in sent if support.whole_graph(entry, [support.LEAF]) or support.over_the_cap(entry)]


def test_c4_the_command_takes_the_code_route_of_a_plain_question(api, planted):
    done, sent = api.command(planted("full"), WHO_CALLS)
    assert done.returncode == 0, f"gov retrieve failed (exit code {done.returncode}):\n{done.stderr[-2000:]}"
    envelope = json.loads(done.stdout)
    assert envelope.get("ok") is True, envelope
    missing = _calls_spans(envelope["result"], support.CALLERS[support.LEAF])
    assert not missing, f"the command's bundle lacks the callers {missing}: {support.items(envelope['result'])}"
    assert not [entry for entry in sent if support.whole_graph(entry, [support.LEAF]) or support.over_the_cap(entry)]


@pytest.mark.parametrize("question", ["who calls w92_nowhere", support.PLAIN_PHRASE], ids=["unknown", "none"])
def test_c5_a_question_naming_no_symbol_of_the_index_sends_no_whole_graph_query(asked, question):
    """A symbol the index does not hold, or no symbol at all: nothing whole-graph is asked to find that out."""
    _, sent = asked("full", question)
    bad = [entry for entry in sent if support.whole_graph(entry, ["w92_nowhere"]) or support.over_the_cap(entry)]
    assert not bad, f"{question!r} sent a whole-graph or over-cap request to the code-graph tool: {bad}"
