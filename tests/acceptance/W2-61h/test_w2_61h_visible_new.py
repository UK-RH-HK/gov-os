"""W2-61h (DAEO-h2k3): the 4 new visible questions, ``q21.yaml`` to ``q24.yaml`` -- KPI lines S1, S2, S3 (the
visible share), S4, F2 and F3.

S1: "Twenty-eight new questions ... in the form W2-61's visible half takes; after writing, a recorded seeded draw,
stratified by category, sends 4 to the visible half ... (fixtures/evaluation/memory-retrieval/visible/q21.yaml to
q24.yaml in the repository ...)". S4: "Every gold source exists at the commit the auditor reads and holds the answer,
cited by path and heading or line". F2: "A question copied from or paraphrasing lens B's visible 20". F3: "A gold
source that does not hold its answer". S2: "Written by a session independent of the retrieval tickets", judged from
the record: the commits' ``Role`` trailers (the CTO's decision of 2026-11-03, P2: by the role, not the ``Task``,
since D-4's cut rewrote these tests under the coordination ticket's id).

These cases read only this tree's tracked files and git record; they never open the sets root.
"""

from __future__ import annotations

import subprocess
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


# S2's writers (the CTO's decision of 2026-11-03, P2): the independent test designer, the owner, and the orchestrator,
# which landed the designer's seeded draw (6dca09f0, re-made from c5c10072); never a role the set measures.
S2_WRITERS = ("independent-test-designer", "owner", "orchestrator")
S2_RELS = [f"fixtures/evaluation/{s.SET}/visible/{name}" for name in s.NEW_VISIBLE] + ["tests/acceptance/W2-61h"]


def _s2_faults(root, measured):
    """``(commits, faults)``: every non-merge commit reachable from ``root``'s HEAD that writes q21-q24 or these
    tests, and those whose ``Role`` trailers are not exactly one of ``S2_WRITERS`` outside ``measured``."""
    log = subprocess.run(["git", "-C", str(root), "log", "--no-merges", "--format=%H", "HEAD", "--", *S2_RELS],
                         capture_output=True, text=True, timeout=s.TIMEOUT_S)
    commits = log.stdout.split()
    faults = []
    for commit in commits:
        done = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%(trailers:key=Role,valueonly,unfold)",
                               commit], capture_output=True, text=True, timeout=s.TIMEOUT_S)
        roles = [line.strip() for line in done.stdout.splitlines() if line.strip()]
        if len(roles) != 1 or roles[0] not in S2_WRITERS or roles[0] in measured:
            faults.append(f"{commit[:12]}: Role {roles}")
    return commits, faults


def test_s2_the_new_questions_and_these_tests_come_from_no_measured_role():
    """Every commit that writes q21-q24 or these tests carries exactly one ``Role``, the independent test designer's,
    the owner's or the orchestrator's, never one of the set's measured roles (the path map's ``measures.roles``);
    the ``Task`` is not judged (D-4's cut wrote these tests under the coordination ticket, DEC-1063). The ticket's
    own role and assignee are not measured roles either."""
    measured = set(s.measured_roles())
    assert {"engineer", "research"} <= measured, f"the set's measured roles: {sorted(measured)}"
    assert not measured & set(S2_WRITERS), f"a writer role is measured: {sorted(measured & set(S2_WRITERS))}"
    commits, faults = _s2_faults(s.REPO_ROOT, measured)
    assert commits, "no commit writes the new visible questions"
    assert not faults, "commits from a measured role or no writer role:\n" + "\n".join(faults)
    ticket = (s.REPO_ROOT / ".tickets" / f"{s.TICKET}.md").read_text(encoding="utf-8")
    front = yaml.safe_load(ticket.split("---", 2)[1])
    assert front.get("role") not in measured and front.get("assignee") not in measured, (
        f"the ticket's role {front.get('role')!r} / assignee {front.get('assignee')!r} is a measured role")


# The engineer's row first: it is the representative the full run keeps (``rep:`` in tests/optin-lifted-breadth.txt).
@pytest.mark.parametrize("role, red", [("engineer", True), ("research", True), (None, True), ("product-spec", True),
                                       ("independent-test-designer", False), ("owner", False),
                                       ("orchestrator", False)])
def test_s2_judges_the_role_on_a_planted_commit(tmp_path, role, red):
    """S2's rule on a planted repository: a designer's commit writes q21, then one more commit under ``role`` (none:
    no ``Role`` trailer) writes q22 under the coordination ticket's ``Task``; the rule finds that commit, and
    faults it exactly when the role is not a writer's (an engineer's or research's is red, whatever the Task). The
    full run keeps the engineer's row; the others are ``breadth``'s."""
    repo = tmp_path / "repo"
    rel = Path(S2_RELS[0]).parent
    (repo / rel).mkdir(parents=True)

    def commit(name, trailers):
        (repo / rel / name).write_text(f"id: {name}\n", encoding="utf-8")
        args = [arg for key, value in trailers for arg in ("--trailer", f"{key}: {value}")]
        for cmd in (["add", "-A"], ["commit", "-q", "-m", f"write {name}", *args]):
            done = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *cmd],
                                  capture_output=True, text=True, timeout=s.TIMEOUT_S)
            assert done.returncode == 0, done.stderr

    subprocess.run(["git", "init", "-q", str(repo)], check=True, timeout=s.TIMEOUT_S)
    commit("q21.yaml", [("Task", s.TICKET), ("Role", "independent-test-designer")])
    commit("q22.yaml", [("Task", "DAEO-sdxk"), *([("Role", role)] if role else [])])
    commits, faults = _s2_faults(repo, {"engineer", "research"})
    assert len(commits) == 2, f"the rule found {len(commits)} commits, not the 2 planted"
    assert len(faults) == (1 if red else 0), f"role {role!r}: faults {faults}"


@pytest.mark.parametrize("name", s.NEW_VISIBLE)
def test_s4_no_new_visible_source_names_the_set_s_own_files(name):
    """No gold source of a new question is the set's declared report or under ``fixtures/evaluation/`` (an item from
    there is never a hit)."""
    data = _new()[name]
    declared = set(s.path_map_entry().get("visible") or [])
    bad = [a["path"] for e in s.entries(data) or [] for a in e
           if a["path"].removeprefix("./") in declared or a["path"].removeprefix("./").startswith("fixtures/evaluation/")]
    assert not bad, f"{name}: {bad}"
