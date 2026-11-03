"""W2-61h (DAEO-h2k3): the 4 new visible questions, ``q21.yaml`` to ``q24.yaml`` -- KPI lines S1, S2, S3 (the
visible share), S4, F2 and F3.

S1: "Twenty-eight new questions ... in the form W2-61's visible half takes; after writing, a recorded seeded draw,
stratified by category, sends 4 to the visible half ... (fixtures/evaluation/memory-retrieval/visible/q21.yaml to
q24.yaml in the repository ...)". S4: "Every gold source exists at the commit the auditor reads and holds the answer,
cited by path and heading or line". F2: "A question copied from or paraphrasing lens B's visible 20". F3: "A gold
source that does not hold its answer". S2: "Written by a session independent of the retrieval tickets", judged from
the record: the commits' trailers.

These cases read only this tree's tracked files and git record; they never open the sets root.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61h_support as s  # noqa: E402

# The designer's own reading of each new visible question's answer: a string its gold source must hold at HEAD
# (per entry; for an entry of alternatives, any one alternative holding it is enough) [S4, F3].
ANCHORS = {
    "q21.yaml": [["DEC-838", "300k", "compact"]],
    "q22.yaml": [["set_fault("], ["set_fault("], ["set_fault("]],
    "q23.yaml": [['MAP_REL = "governance/project/test-map.yaml"']],
    "q24.yaml": [["1800"], ["30"]],
}


def _new():
    missing = [name for name in s.NEW_VISIBLE if not (s.VISIBLE / name).is_file()]
    assert not missing, f"the new visible question files are missing: {missing}"
    return {name: s.load(s.VISIBLE / name) for name in s.NEW_VISIBLE}


def test_s1_the_four_new_visible_questions_are_in_the_question_form():
    """q21-q24 exist beside lens B's 20, each in the measure's question form with a category of S3's ten; every
    visible question id is distinct, and each new file names the commit it was written at, a commit of this
    repository."""
    new = _new()
    faults = [f"{name}: {', '.join(found)}" for name, data in new.items() if (found := s.form_faults(data))]
    assert not faults, "\n".join(faults)
    files = sorted(s.VISIBLE.glob("*.yaml"))
    ids = [str((s.load(f) or {}).get("id") or f.stem) for f in files]
    assert len(set(ids)) == len(ids), "the visible question ids are not distinct"
    unknown = [name for name, data in new.items() if not (data.get("commit") and s.commit_exists(str(data["commit"])))]
    assert not unknown, f"these files name no commit of this repository: {unknown}"


def test_s1_the_visible_four_are_the_stratified_draw_s_share():
    """A draw of 4 of the 28, stratified by category (the recorded method: 4 x count / 28, largest remainder, ties
    broken by the seed): one each from decision (5), exact-string (4) and callers (4), and one from the three
    categories of 3 (code-paraphrase, kernel-template, multi-file); never two from one category."""
    categories = [s.LABELS.get(data.get("category")) for data in _new().values()]
    assert len(set(categories)) == 4, f"the new visible four's categories: {sorted(map(str, categories))}"
    assert {"decision", "exact-string", "callers"} <= set(categories), sorted(map(str, categories))
    rest = set(categories) - {"decision", "exact-string", "callers"}
    assert rest <= {"code-paraphrase", "kernel-template", "multi-file"}, sorted(map(str, categories))


def test_s4_f3_every_new_visible_gold_source_resolves_at_head():
    """Each gold source of q21-q24 is a file at HEAD; a heading given is a line of it, or the stated lines are a span
    of it; a source cited by lines alone holds the same lines at HEAD as at the question's commit (no drift)."""
    faults = [f"{name}: source entry {n}: {why}" for name, data in _new().items() for n, why in s.source_faults(data)]
    assert not faults, "\n".join(faults)


def test_f3_each_new_visible_gold_source_holds_its_answer():
    """The resolved text of each source entry at HEAD (the measure's span) holds the designer's anchor for that
    entry's part of the answer."""
    faults = []
    for name, data in _new().items():
        texts = s.span_text(data)
        anchors = ANCHORS[name]
        if len(texts) != len(anchors):
            faults.append(f"{name}: {len(texts)} source entries, the designer's reading has {len(anchors)}")
            continue
        for n, (alternatives, needed) in enumerate(zip(texts, anchors), 1):
            if not any(all(word in text for word in needed) for text in alternatives):
                faults.append(f"{name}: source {n} does not hold {needed}")
    assert not faults, "\n".join(faults)


def test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one():
    """No question of q21-q24 is, case, spacing and punctuation aside, one of lens B's 20 (q01-q20) or another new
    one. A paraphrase is judged from the record (the README), not here."""
    lens_b = {s.normalised((s.load(s.VISIBLE / name) or {}).get("question", "")) for name in s.LENS_B}
    seen, faults = set(), []
    for name, data in _new().items():
        text = s.normalised(data.get("question", ""))
        if text in lens_b or text in seen:
            faults.append(name)
        seen.add(text)
    assert not faults, f"these new visible questions repeat another visible question: {faults}"


def test_s2_the_new_questions_and_these_tests_come_from_no_measured_role():
    """Every commit that writes q21-q24 or these tests carries ``Task: DAEO-h2k3`` (never a retrieval ticket's) and a
    ``Role`` outside the set's measured roles (the path map's ``measures.roles``); the ticket's own role and
    assignee are not measured roles either."""
    measured = set(s.measured_roles())
    assert {"engineer", "research"} <= measured, f"the set's measured roles: {sorted(measured)}"
    rels = [f"fixtures/evaluation/{s.SET}/visible/{name}" for name in s.NEW_VISIBLE] + ["tests/acceptance/W2-61h"]
    commits = s.commits_touching(rels)
    assert commits, "no commit writes the new visible questions"
    faults = []
    for commit in commits:
        found = s.trailers(commit)
        roles, tasks = found.get("role", []), found.get("task", [])
        if tasks != [s.TICKET] or len(roles) != 1 or roles[0] in measured:
            faults.append(f"{commit[:12]}: Task {tasks}, Role {roles}")
    assert not faults, "commits outside the ticket or from a measured role:\n" + "\n".join(faults)
    ticket = (s.REPO_ROOT / ".tickets" / f"{s.TICKET}.md").read_text(encoding="utf-8")
    front = yaml.safe_load(ticket.split("---", 2)[1])
    assert front.get("role") not in measured and front.get("assignee") not in measured, (
        f"the ticket's role {front.get('role')!r} / assignee {front.get('assignee')!r} is a measured role")


@pytest.mark.parametrize("name", s.NEW_VISIBLE)
def test_s4_no_new_visible_source_names_the_set_s_own_files(name):
    """No gold source of a new question is the set's declared report or under ``fixtures/evaluation/`` (an item from
    there is never a hit)."""
    data = _new()[name]
    declared = set(s.path_map_entry().get("visible") or [])
    bad = [a["path"] for e in s.entries(data) or [] for a in e
           if a["path"].removeprefix("./") in declared or a["path"].removeprefix("./").startswith("fixtures/evaluation/")]
    assert not bad, f"{name}: {bad}"
