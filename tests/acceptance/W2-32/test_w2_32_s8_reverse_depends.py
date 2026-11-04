"""DEC-1068 (M3), a note within S8: the reverse ``depends_on`` edge in the closure (the CTO's note of 2026-11-04 ~09:30).

The note: a question naming a record also reaches the records that depend on it; behind
``closure_reverse_depends_on``, off by default; the loader refuses an invalid value with ``CONFIG_INVALID`` naming the
key. The setting's file is ``w2_32_methods.M3_SETTINGS_REL`` (``rebuild.yaml``; ``retrieval.yaml`` if the engineer
states it is query-time).

- **Today's closure already reaches the direct dependents** (probed on integrate ``bfd60400``): the closure follows the
  store's typed edges both ways, ``DEPENDS_ON`` among them, so ``Which tickets depend on DAEO-quay?`` reaches
  ``DAEO-buoy`` (``depends_on: [DAEO-quay]``) by the closure at any radius; a ticket two hops away (``DAEO-sail``,
  ``depends_on: [DAEO-buoy]``) is not reached. The case here is a guard: with the setting off or on, the direct
  dependent is reached by the closure. "Off does not reach it" is not written: it would change today's answers
  (returned to the CTO as a decision, the return's ``proposed_decisions``).
- **Invalid:** ``yes``, ``1``, a quoted ``"true"``, a word: ``CONFIG_INVALID`` naming ``closure_reverse_depends_on``,
  from ``gov rebuild`` or, if the setting is read at query time, from ``retrieve``.
"""

from __future__ import annotations

import pytest
import yaml

import w2_32_methods as m
import w2_32_support as s

A, B, C = "DAEO-quay", "DAEO-buoy", "DAEO-sail"
QUESTION = f"Which tickets depend on {A}?"


def _ticket(tid, title, deps=()):
    front = {"id": tid, "type": "task", "status": "open", "title": title}
    if deps:
        front["depends_on"] = list(deps)
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {title}\n\nThe crew see to {title.lower()}.\n"


FILES = {**s.NOTES,
         f".tickets/{A}.md": _ticket(A, "Quay lamp repairs"),
         f".tickets/{B}.md": _ticket(B, "Buoy repainting", [A]),
         f".tickets/{C}.md": _ticket(C, "Sail mending", [B])}
TICKETS = {"tickets": s.namespace([".tickets/**"], "embedded")}


def _by_closure(bundle, path):
    return [item for item in bundle["evidence"] if item["path"] == path and "closure" in (item.get("routes") or [])]


@pytest.mark.parametrize("setting", [None, "false", "true"], ids=["absent", "false", "true"])
def test_a_question_naming_a_record_reaches_the_records_that_depend_on_it(tmp_path, needs_vectors, box, standin,
                                                                          setting):
    project = m.plant(tmp_path / "project", FILES, TICKETS)
    m.settle(project, m.M3_SETTINGS_REL, None if setting is None else f"{m.M3_KEY}: {setting}\n")
    box.built(project)
    bundle = s.result(box.call("retrieve", root=str(project), query=QUESTION, reranker="constant", radius=0))
    assert _by_closure(bundle, f".tickets/{A}.md"), f"premise: the question's record {A} is reached by the closure"
    assert _by_closure(bundle, f".tickets/{B}.md"), \
        f"{B} depends on {A}; a question naming {A} does not reach it by the closure ({m.M3_KEY}: {setting}): " \
        f"{[(item['path'], item.get('routes')) for item in bundle['evidence']][:10]}"


@pytest.mark.parametrize("value", m.INVALID)
def test_an_invalid_closure_reverse_depends_on_is_config_invalid_naming_the_key(tmp_path, needs_vectors, box, standin,
                                                                               value):
    project = m.plant(tmp_path / "project", FILES, TICKETS)
    m.settle(project, m.M3_SETTINGS_REL, f"{m.M3_KEY}: {value}\n")
    envelope = box.rebuild(project)
    answers = [m.answer_text(envelope)]
    if envelope.get("ok") is True:  # the setting read at query time: retrieve refuses it
        answers.append(m.answer_text(box.call("retrieve", root=str(project), query=QUESTION, reranker="constant")))
    assert any("CONFIG_INVALID" in answer and m.M3_KEY in answer for answer in answers), \
        f"{m.M3_KEY}: {value} was not refused with CONFIG_INVALID naming the key: {answers[-1][:1500]}"
