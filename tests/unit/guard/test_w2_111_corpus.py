"""Builder tests for W2-111 (DEC-1184 (3), failure-4): the speed-up changes no decision.

The corpus (``test_w2_111_corpus.json``) holds calls the guard's rule suites handed the product guard before W2-111
(``tests/unit/guard/`` with its opt-in rows, W2-42a's parser corpus among them, and W1-02's and W1-05's cases but
this ticket's revised ones, which were not recorded), and W2-111's own calls at, in and above the trees.  Each was
decided before the change on the planted repository of ``test_w2_111_plant`` (155 trees beside the project, one
nested, one through a link, a locked and a gone one, a hidden part, a runs root) for the engineer, the test designer,
the auditor and no role: ``decide`` (the hook's entry), ``policy_refusal`` (the read rules) and ``has_install``.
Those answers, reasons included, are the expected ones.  The whole recorded corpus (``size.recorded``) was run
before and after the change by the ticket's corpus script with no answer differing; this case keeps W2-111's own
calls and a fixed share of the rest (``size.kept``), so that it runs in about a minute.
Regression evidence only (DEC-136).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gov.guard.decide import decide  # noqa: E402
from gov.guard.install import has_install  # noqa: E402
from gov.guard.reads import policy_refusal  # noqa: E402
from test_w2_111_plant import TICKET, plant  # noqa: E402

CORPUS = Path(__file__).resolve().parent / "test_w2_111_corpus.json"
ROLES = ["engineer", "independent-test-designer", "independent-auditor", None]


def fill(obj, places):
    text = json.dumps(obj)
    for k, v in places.items():
        text = text.replace("{" + k + "}", v)
    return json.loads(text)


def unfill(text, places):
    for k in ("P", "TR", "H", "B"):  # P, TR and H lie in B
        text = text.replace(places[k], "{" + k + "}")
    return text


def answers(call, places):
    """The call's answer for each role: [role, decide's decision, its reason, the read rules' refusal, install]."""
    c = fill(call, places)
    tool, tin, cwd, sub = c["tool_name"], c["tool_input"], c["cwd"] or places["P"], c["subagent"]
    rows = []
    for role in ROLES:
        try:
            d = list(decide(tool, tin, places["P"], role, TICKET, sub, cwd))
        except Exception as exc:
            d = ["raised", type(exc).__name__]
        try:
            p = policy_refusal(tool, tin, places["P"], cwd, role, TICKET, sub)
        except Exception as exc:
            p = "raised " + type(exc).__name__
        inst = None
        if tool == "Bash" and isinstance(tin.get("command"), str):
            try:
                inst = has_install(tin["command"])
            except Exception as exc:
                inst = "raised " + type(exc).__name__
        rows.append([role, d[0], unfill(str(d[1]), places), unfill(p, places), inst])
    return rows


@pytest.fixture(scope="module")
def places(tmp_path_factory):
    out = plant(str(tmp_path_factory.mktemp("w2_111_corpus")))
    out["T"] = os.path.join(out["B"], "elsewhere")
    return out


@pytest.fixture(scope="module")
def corpus():
    return json.loads(CORPUS.read_text())


def test_the_corpus_is_the_size_recorded(corpus):
    kept, expected = corpus["size"]["kept"], [[corpus["answers"][k] for k in ks] for ks in corpus["expected"]]
    assert len(corpus["calls"]) == len(expected) == kept["calls"]
    assert sum(r[1] != "allow" for rows in expected for r in rows) == kept["refused"]
    assert sum(bool(r[3]) for rows in expected for r in rows) == kept["refused_read_rules"]


def test_every_decision_of_the_corpus_is_the_same_as_before(places, corpus, monkeypatch):
    monkeypatch.setenv("HOME", places["H"])
    monkeypatch.chdir(places["P"])
    differ = []
    for i, (call, keys) in enumerate(zip(corpus["calls"], corpus["expected"])):
        want = [corpus["answers"][k] for k in keys]
        got = answers(call, places)
        if got != want:
            differ.append((i, call, want, got))
    assert not differ, json.dumps(differ[:5], indent=1)
