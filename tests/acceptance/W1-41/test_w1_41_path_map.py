"""Stages A3 (the target path map) and A4 (the batched plan) [CAP-06.b, CAP-06.d, CAP-44.b, CAP-44.j].

The caller gives A3 a proposal (``--map <file>``): the artefacts that are not kept, each with its action and its
target. The tool checks it against the inventory and the classification, adds what the graphs say, and records the
path map. Every case that proposes a move in a project whose path map turns code intelligence on needs the code
graph, so the code index tool (W1-16) must be able to run (README, "Where the cases can run").
"""

from __future__ import annotations

import json

import pytest

import w1_41_support as support

LONG, PART_1, PART_2, MIXED = "docs/long.md", "docs/part-1.md", "docs/part-2.md", "docs/mixed.md"
EIGHT_FILES = {
    LONG: "# Long\n\nFirst half.\n\nSecond half.\n",
    PART_1: "# Part one\n",
    PART_2: "# Part two\n",
    MIXED: "# Mixed\n\nA paragraph that belongs elsewhere.\n",
}


def _eight_actions():
    return [
        support.entry("pyproject.toml", "KEEP"),
        support.entry(support.GUIDE, "MOVE", support.GUIDE_TARGET, batch=1),
        support.entry(support.NOTES, "RENAME", "docs/tides.txt", batch=1),
        support.entry(LONG, "SPLIT", ["docs/long-a.md", "docs/long-b.md"], batch=2),
        support.entry(PART_1, "MERGE", "docs/parts.md", batch=2),
        support.entry(PART_2, "MERGE", "docs/parts.md", batch=2),
        support.entry(MIXED, "EXTRACT", "docs/extracted.md", batch=2),
        support.entry(".cursorrules", "RETIRE", kind="rule-file"),
        support.entry("legacy/memory/index.md", "DELETE_FROM_ACTIVE_TREE"),
    ]


def _refused_at_a3(adoption, interface, entries, *names, any_of=()):
    """A0 to A2 succeed; A3 with ``entries`` is refused and leaves no path map behind."""
    adoption.through("A2")
    before = support.snapshot(adoption.project, skip=(".git", ".gov-runtime"))
    head = support.head(adoption.project)
    run = adoption.run("A3", *adoption.map_argument(entries))
    support.assert_refused(run, interface, *names, any_of=any_of)
    changed = support.snapshot_difference(before, support.snapshot(adoption.project, skip=(".git", ".gov-runtime")))
    assert not changed, f"the refused A3 wrote in the project: {changed}\n{run.describe()}"
    assert support.head(adoption.project) == head, f"the refused A3 committed\n{run.describe()}"
    return run


# --------------------------------------------------------------------------
# CAP-06.b: one of the eight actions for every artefact
# --------------------------------------------------------------------------

def test_every_artefact_has_exactly_one_of_the_eight_actions(adoption, project):
    """Every inventoried artefact is in the path map once, with one action of the eight. What the proposal does
    not name is kept: nothing is moved, retired or deleted by default."""
    baseline = set(support.tree(project))
    proposal = support.legacy_proposal()
    adoption.through("A3", proposal)
    entries = adoption.map_entries()
    missing = sorted(baseline - set(entries))
    assert not missing, f"artefacts without an entry in the path map: {missing}"
    outside = {rel: item.get("action") for rel, item in entries.items() if item.get("action") not in support.ACTIONS}
    assert not outside, f"entries whose action is not one of the eight: {outside}"
    named = {item["path"]: item["action"] for item in proposal}
    wrong = {rel: entries[rel]["action"] for rel in baseline
             if entries[rel]["action"] != named.get(rel, "KEEP")}
    assert not wrong, f"entries whose action is not the proposed one, or not KEEP where none was proposed: {wrong}"


def test_each_of_the_eight_actions_is_recorded_as_proposed(tmp_path, adopt_in):
    project = support.build_project(tmp_path / "eight", extra=EIGHT_FILES)
    adoption = adopt_in(project)
    proposal = _eight_actions()
    adoption.through("A3", proposal)
    entries = adoption.map_entries()
    assert {item["action"] for item in proposal} == set(support.ACTIONS)
    for item in proposal:
        recorded = entries[item["path"]]
        assert recorded.get("action") == item["action"], \
            f"{item['path']}: recorded as {recorded.get('action')}, proposed as {item['action']}"
        for key in ("target", "targets"):
            if key in item:
                assert recorded.get(key) == item[key], f"{item['path']}: the record does not carry its {key}"


@pytest.mark.parametrize("action", ["ARCHIVE", "COPY", "move", ""])
def test_an_action_outside_the_eight_is_refused(adoption, interface, action):
    entries = [support.entry(support.GUIDE, action, support.GUIDE_TARGET, batch=1)]
    _refused_at_a3(adoption, interface, entries, support.GUIDE)


def test_an_artefact_given_two_actions_is_refused(adoption, interface):
    entries = [support.entry(support.NOTES, "RETIRE"), support.entry(support.NOTES, "DELETE_FROM_ACTIVE_TREE")]
    _refused_at_a3(adoption, interface, entries, support.NOTES)


def test_a_path_the_inventory_does_not_hold_is_refused(adoption, interface):
    entries = [support.entry("docs/no-such-file.md", "RETIRE")]
    _refused_at_a3(adoption, interface, entries, "docs/no-such-file.md")


def test_a_move_without_a_target_is_refused(adoption, interface):
    _refused_at_a3(adoption, interface, [support.entry(support.NOTES, "MOVE", batch=1)], support.NOTES)


def test_a_move_onto_an_artefact_that_stays_is_refused(adoption, interface):
    """Two artefacts cannot end at one path: the kept file would be overwritten."""
    entries = [support.entry(support.NOTES, "MOVE", support.GUIDE, batch=1)]
    _refused_at_a3(adoption, interface, entries, support.GUIDE)


def test_a_proposal_that_cannot_be_read_is_refused(adoption, interface):
    """DEC-449: a proposal that cannot be read is not an empty proposal (which would keep everything)."""
    adoption.through("A2")
    head = support.head(adoption.project)
    path = support.write_proposal(adoption.sandbox, [])
    path.write_text("artefacts: [unclosed\n  - }\n", encoding="utf-8")
    run = adoption.run("A3", "--map", str(path))
    support.assert_refused(run, interface)
    assert support.head(adoption.project) == head, f"a path map was recorded from an unreadable proposal\n{run.describe()}"


# --------------------------------------------------------------------------
# CAP-06.d: importers, references and consumers; the plan rewrites or flags each
# --------------------------------------------------------------------------

def test_every_artefact_to_be_moved_carries_importers_references_and_consumers(adoption):
    adoption.through("A3", support.moves_proposal())
    entries = adoption.map_entries()
    for item in support.moves_proposal():
        recorded = entries[item["path"]]
        for key in ("importers", "references", "consumers"):
            assert isinstance(recorded.get(key), list), \
                f"{item['path']}: the path map does not record its {key} as a list ({recorded.get(key)!r})"


def test_the_importer_of_a_moved_module_is_read_from_the_code_graph(adoption):
    adoption.through("A3", support.moves_proposal())
    importers = json.dumps(adoption.map_entries()[support.UTIL].get("importers"))
    assert support.UTIL_IMPORTER in importers, \
        f"{support.UTIL}: its importer {support.UTIL_IMPORTER} is not recorded (importers: {importers})"


def test_the_references_and_consumers_of_a_moved_record_are_read_from_the_record_graph(adoption):
    """The moved record is depended on by another record (an edge of the record graph), and names a consumer in its
    own frontmatter."""
    adoption.through("A3", support.moves_proposal())
    recorded = adoption.map_entries()[support.MOVED_RECORD]
    references = json.dumps(recorded.get("references"))
    assert support.CITING_RECORD_ID in references or support.CITING_RECORD in references, \
        f"{support.MOVED_RECORD}: the record that depends on it is not among its references ({references})"
    consumers = json.dumps(recorded.get("consumers"))
    assert support.RECORD_CONSUMER in consumers, \
        f"{support.MOVED_RECORD}: the consumer its frontmatter names is not recorded ({consumers})"


def test_the_plan_rewrites_or_flags_every_importer_reference_and_consumer(adoption):
    adoption.through("A4", support.moves_proposal())
    plan = adoption.stages["A4"]
    handled = [item for item in support.base.find_records(plan.front, key="handling")]
    assert handled, f"{plan.record}: the plan handles no importer, reference or consumer"
    bad = [item for item in handled if item["handling"] not in ("rewrite", "flag")]
    assert not bad, f"{plan.record}: a handling that is neither 'rewrite' nor 'flag': {bad}"
    expected = {
        support.UTIL: (support.UTIL_IMPORTER,),
        support.MOVED_RECORD: (support.CITING_RECORD_ID, support.CITING_RECORD),
    }
    for moved, names in expected.items():
        hits = [item for item in handled
                if moved in json.dumps(item) and any(name in json.dumps(item) for name in names)]
        assert hits, f"{plan.record}: nothing rewrites or flags what depends on {moved} (one of {names})"


def test_a_code_graph_that_cannot_be_read_refuses_and_records_no_importers(adoption, interface):
    """DEC-449, DEC-454: where the code graph cannot be read (its tool is not on PATH), the tool refuses. It never
    records "no importers" for a module whose importers it did not establish."""
    adoption.through("A2")
    head = support.head(adoption.project)
    run = adoption.run("A3", *adoption.map_argument(support.moves_proposal()), without=(support.CODE_INDEX_TOOL,))
    support.assert_refused(run, interface, any_of=("code graph", "code index", "codeintel", support.CODE_INDEX_TOOL))
    assert support.head(adoption.project) == head, \
        f"a path map was recorded although the code graph could not be read\n{run.describe()}"


# --------------------------------------------------------------------------
# CAP-44.j: a healthy native layout is kept
# --------------------------------------------------------------------------

def test_a_native_package_layout_is_kept_where_nothing_else_is_proposed(adoption, project):
    adoption.through("A3", support.legacy_proposal())
    entries = adoption.map_entries()
    native = ("pyproject.toml", "src/app/__init__.py", support.NATIVE_FILE)
    moved = {rel: entries[rel]["action"] for rel in native if entries[rel]["action"] != "KEEP"}
    assert not moved, f"the path map does not keep the native package layout: {moved}"


def test_a_move_out_of_a_native_layout_without_a_justification_is_refused(adoption, interface):
    entries = [support.entry(support.NATIVE_FILE, "MOVE", support.NATIVE_TARGET, batch=1)]
    _refused_at_a3(adoption, interface, entries, support.NATIVE_FILE)


@pytest.mark.parametrize("given", ["materially_better", "migration_risk"])
def test_a_justification_that_states_only_one_of_the_two_grounds_is_refused(adoption, interface, given):
    """CAP-44.j names two grounds: the target structure is materially better, and the migration risk is
    justified. One of them is not both."""
    entries = [support.entry(support.NATIVE_FILE, "MOVE", support.NATIVE_TARGET, batch=1,
                             justification={given: "stated by the proposer"})]
    _refused_at_a3(adoption, interface, entries, support.NATIVE_FILE)


def test_a_justified_move_out_of_a_native_layout_is_recorded_with_both_grounds(adoption):
    better = "one flat modules folder serves the three services"
    risk = "one importer, covered by the package's tests"
    entries = [support.entry(support.NATIVE_FILE, "MOVE", support.NATIVE_TARGET, batch=1,
                             justification={"materially_better": better, "migration_risk": risk})]
    adoption.through("A3", entries)
    recorded = adoption.map_entries()[support.NATIVE_FILE]
    assert recorded.get("action") == "MOVE"
    said = json.dumps(recorded)
    assert better in said and risk in said, \
        f"{support.NATIVE_FILE}: the path map does not show both grounds of the move ({said})"


# --------------------------------------------------------------------------
# CAP-44.b: A4, batches with a rollback point each
# --------------------------------------------------------------------------

def test_the_plan_has_the_proposed_batches_each_with_its_own_rollback_point(adoption, project):
    baseline = support.tree(project)
    adoption.through("A4", support.moves_proposal())
    plan = adoption.stages["A4"]
    batches = plan.front.get("batches")
    assert isinstance(batches, list) and [item.get("batch") for item in batches] == [1, 2, 3], \
        f"{plan.record}: the plan does not hold the batches 1, 2, 3 in order"
    points = [item.get("rollback_point") for item in batches]
    assert all(isinstance(point, str) and point.startswith("refs/") for point in points), \
        f"{plan.record}: a batch without a rollback point that is a full ref name: {points}"
    assert len(set(points)) == 3, f"{plan.record}: the batches do not each have their own rollback point: {points}"
    expected = {1: {support.GUIDE}, 2: {support.NOTES, support.MOVED_RECORD}, 3: {support.UTIL}}
    for item in batches:
        paths = {artefact.get("path") for artefact in item.get("artefacts") or [] if isinstance(artefact, dict)}
        assert paths == expected[item["batch"]], \
            f"{plan.record}: batch {item['batch']} holds {sorted(paths)}, proposed {sorted(expected[item['batch']])}"
    # A plan moves nothing.
    problems = support.moved_nothing(project, baseline, [item["path"] for item in support.moves_proposal()])
    assert not problems, f"the plan moved something: {problems}"
