"""S22 (stage 10 takes the template's defaults), S23 (the trees leave out what the template says), S24 (set-up A's
inputs staged by rule, from the half's folder). DEC-1112 (3), DEC-1113.

The five planted set-up A briefs carry the approved briefs' front matter byte for byte (``SGX1_FRONT``, checked against
the approved hashes) and a planted body; the planted ``kinds.yaml`` carries a model per kind and the ``briefs:`` map
(README, "Set-up A's wiring"). The staged inputs are compared with the planted sources, never with the script's.
"""

from __future__ import annotations

import json
import os
import random
import stat

import pytest
import yaml

import w2_149_setup_a as sa
import w2_149_support as support
from w2_149_support import assert_good_launch, assert_nothing_built, assert_refused


def plant_for(world, flow, half):
    """What a flow reads from its half before it builds (nothing for the writers)."""
    if flow in ("labeller", "labeller-2", "overlap-auditor"):
        sa.plant_half(world, half, n_actions=48, n_cases=12)
    if flow == "overlap-auditor":
        return sa.plant_labels(world, half)
    return None


# -- S22 ------------------------------------------------------------------------------------------------------------

def test_s22_premise_the_planted_briefs_carry_the_approved_front_matter_byte_for_byte(world):
    for name, fm in support.SGX1_FRONT.items():
        assert support.sha256(fm.encode()) == support.SGX1_FRONT_SHA256[name], name
        data = world.blob("B", f"{support.BRIEFS_REL}/sgx1/{name}.md")
        assert data == (fm + support.SGX1_BODY).encode(), name
        front = yaml.safe_load(fm.strip().strip("-"))
        assert "model" not in front and "result_schema" not in front, name
        assert ("sample" in front) == name.startswith("writer"), name


def test_s22_the_template_s_kinds_yaml_gives_a_model_per_kind_and_the_five_briefs_entries():
    """The repository's own template (what the engineer changes): a model per kind; the briefs: map holding the five
    entries with their kind, flow, result schema (a file beside the script), sample (0 for the labellers and the
    auditor) and tree_exclude (the guard's and the launcher's code)."""
    doc = yaml.safe_load((support.TEMPLATE_SRC / "kinds.yaml").read_text())
    for kind in support.KINDS:
        model = (doc.get("kinds") or {}).get(kind, {}).get("model")
        assert isinstance(model, str) and model.strip(), f"kinds.yaml gives the {kind} kind no model"
    briefs = doc.get("briefs")
    assert isinstance(briefs, dict), "kinds.yaml has no briefs: map"
    want = {v[2]: (v[0], v[3], f) for f, v in sa.FLOW.items()}
    assert set(briefs) == set(want), sorted(briefs)
    for bid, (kind, flow, f) in want.items():
        e = briefs[bid]
        assert e.get("kind") == kind and e.get("flow") == flow, (bid, e)
        assert e.get("result_schema") == sa.SCHEMA[f], (bid, e)
        assert (support.SCHEMAS / sa.SCHEMA[f]).is_file(), f"indep-schemas/{sa.SCHEMA[f]} does not exist"
        assert set(e.get("tree_exclude") or []) == set(support.SGX1_TREE_EXCLUDE), (bid, e)
        if kind != "writer":
            assert e.get("sample") == 0 and not isinstance(e.get("sample"), bool), (bid, e)
        elif "sample" in e:
            assert isinstance(e["sample"], int) and not isinstance(e["sample"], bool), (bid, e)


@pytest.mark.parametrize("flow", sorted(sa.FLOW))
def test_s22_each_approved_set_up_a_brief_passes_stage_10_in_a_dry_build(world, flow):
    half = sa.HALVES[1] if flow == "writer-heldout" else sa.HALVES[0]
    plant_for(world, flow, half)
    run = sa.dry(world, flow, half, seed=5150)
    assert run.code == 0, run.why()
    assert run.line["status"] == "dry"
    m = json.loads((world.wall(run.line) / "WALL.json").read_text())
    kind = sa.FLOW[flow][0]
    assert m.get("model") == (sa.ENTRY_MODEL[flow] or sa.KIND_MODEL[kind]), m.get("model")
    assert m.get("result_schema") == sa.SCHEMA[flow], m.get("result_schema")
    assert m.get("brief_id") == sa.FLOW[flow][2] and m.get("flow") == sa.FLOW[flow][3], (m.get("brief_id"), m.get("flow"))
    assert world.calls() == [], "a --dry build started claude"


def test_s22_a_front_matter_value_beats_the_entry(world):
    sa.plant_half(world, "tuning")
    support.next_second()
    run = world.launch(*world.args("labeller", brief="sgx1x/labeller-front", set_="tuning", seed=5150, dry=True),
                       env=sa.rules_env())
    assert run.code == 0, run.why()
    m = json.loads((world.wall(run.line) / "WALL.json").read_text())
    assert m.get("model") == "claude-front-model", m.get("model")
    assert m.get("result_schema") == "labeller-result.schema.json", m.get("result_schema")
    assert m.get("flow") == "sgx1-labeller-1"


@pytest.mark.parametrize("brief,kind,set_", [("sgx1x/writer-as-labeller", "labeller", "tuning"),
                                             ("sgx1x/labeller-as-auditor", "auditor", "memory-verdict-3")])
def test_s22_an_entry_of_another_kind_refuses_10(world, brief, kind, set_):
    """Every value is in the front matter, so only the entry's kind (writer, labeller) against the brief's refuses."""
    sa.plant_half(world, "tuning")
    before = world.built_state(kind)
    run = world.launch(*world.args(kind, brief=brief, set_=set_, dry=True), env=sa.rules_env())
    assert_refused(world, run, 10)
    assert_nothing_built(world, kind, before)
    assert_good_launch(world, "writer")


@pytest.mark.parametrize("brief", ["labeller", "sgx1x/labeller-unknown"])
def test_s22_a_labeller_brief_with_no_entry_refuses_10(world, brief):
    """The generic labeller brief (no brief: id) and one naming an id the map does not hold: the labeller kind runs
    set-up A's flows only."""
    before = world.built_state("labeller")
    run = world.launch(*world.args("labeller", brief=brief, dry=True), env=sa.rules_env())
    assert_refused(world, run, 10)
    assert_nothing_built(world, "labeller", before)


@pytest.mark.parametrize("brief,kind,flow", [("sgx1x/no-schema", "writer", "writer-tuning"),
                                             ("sgx1x/no-sample", "auditor", "overlap-auditor")])
def test_s22_a_value_found_nowhere_refuses_10_and_the_approved_brief_of_its_flow_builds(world, brief, kind, flow):
    """``w2-149-no-schema``: no result_schema in the front matter or the entry (the model is the kind's, the sample
    the entry's); ``w2-149-no-sample``: no sample anywhere. Then the approved brief of the same flow builds."""
    plant_for(world, flow, "tuning")
    before = world.built_state(kind)
    run = world.launch(*world.args(kind, brief=brief, set_="tuning", dry=True), env=sa.rules_env())
    assert_refused(world, run, 10)
    assert_nothing_built(world, kind, before)
    good = sa.dry(world, flow, "tuning", seed=5150)
    assert good.code == 0, good.why()


# -- S23 ------------------------------------------------------------------------------------------------------------

def test_s23_the_template_s_tree_exclude_leaves_out_the_briefs():
    lines = [x.strip() for x in (support.TEMPLATE_SRC / "tree-exclude.txt").read_text().splitlines()]
    assert "governance/project/indep-briefs/**" in lines, "tree-exclude.txt does not leave out the briefs"


def tree_files(tree):
    return sorted(os.path.relpath(os.path.join(dp, n), tree) for dp, _dn, fn in os.walk(tree) for n in fn)


def test_s23_a_set_up_a_tree_leaves_out_its_entry_s_globs_and_a_memory_writer_s_keeps_them(world):
    a = sa.dry(world, "writer-tuning", "tuning", seed=4242)
    assert a.code == 0, a.why()
    m = world.launch(*world.args("writer", seed=4242, dry=True))
    assert m.code == 0, m.why()
    ex = world.exclusions("B")
    tracked = world.tracked("B")
    globs = {"governance/project/indep-briefs/**", *support.SGX1_TREE_EXCLUDE}
    planted = [p for p in tracked if any(support.excluded(p, [g]) for g in globs)]
    assert {g for g in globs if any(support.excluded(p, [g]) for p in planted)} == globs, "premise: a file per glob"
    got_a, got_m = tree_files(world.tree(a.line)), tree_files(world.tree(m.line))
    briefs = [p for p in got_a + got_m if p.startswith("governance/project/indep-briefs/")]
    assert briefs == [], f"a tree holds the briefs: {briefs[:3]}"
    want_m = sorted(p for p in tracked if not support.excluded(p, ex)
                    and not support.excluded(p, ["governance/project/indep-briefs/**"]))
    assert got_m == want_m, (sorted(set(got_m) ^ set(want_m))[:6])
    want_a = sorted(p for p in want_m if not support.excluded(p, support.SGX1_TREE_EXCLUDE))
    assert got_a == want_a, (sorted(set(got_a) ^ set(want_a))[:6])
    for keep in (".claude/settings.json", "src/gov/guard/core.py", "src/gov/launch/run.py",
                 f"{support.TEMPLATE_REL}/wall_hook.py"):
        assert keep in got_m and keep not in got_a, keep


# -- S24 ------------------------------------------------------------------------------------------------------------

def test_s24_premise_the_seal_commits_are_one_change_each(world):
    for key in ("PU", "PC"):
        diff = support.git(world.repo_path, "diff", "--name-only", world.sha("B"), world.sha(key)).split()
        assert diff == ["governance/project/path-map.yaml"], (key, diff)
    pm = {k: yaml.safe_load(world.blob(k, "governance/project/path-map.yaml")) for k in ("B", "PU", "PC")}
    glob = "fixtures/evaluation/sandbox-guard-exp-1/hidden/**"
    assert pm["B"]["evaluation_sets"]["sandbox-guard-exp-1"]["hidden"] == [glob]
    assert glob in pm["B"]["sets_root_hidden"]["hidden"]
    assert "sandbox-guard-exp-1" not in (pm["PU"]["evaluation_sets"] or {}) and glob in pm["PU"]["sets_root_hidden"]["hidden"]
    assert pm["PC"]["evaluation_sets"]["sandbox-guard-exp-1"]["hidden"] == [glob]
    assert glob not in pm["PC"]["sets_root_hidden"]["hidden"]


def read_only(wall):
    inp = wall / "input"
    assert stat.S_IMODE(os.stat(inp).st_mode) & 0o222 == 0, "input/ is writable"
    for dp, dn, fn in os.walk(inp):
        for n in dn + fn:
            assert stat.S_IMODE(os.stat(os.path.join(dp, n)).st_mode) & 0o222 == 0, f"{n} is writable"


def test_s24_writer_1_stages_its_selection_by_s5_s_rule(world):
    """Writer 1's one input is S5's selection, unchanged by set-up A: less tree-exclude.txt (which leaves out the
    briefs, S23); the entry's tree_exclude limits the tree, not the pool of places; the front matter's sample: 400
    (more than the planted repository holds)."""
    run = sa.dry(world, "writer-tuning", "tuning", seed=4242)
    assert run.code == 0, run.why()
    wall = world.wall(run.line)
    assert sa.input_listing(wall) == ["selection.json"]
    sel = json.loads((wall / "input/selection.json").read_text())
    ex = world.exclusions("B") + ["governance/project/indep-briefs/**"]
    tracked = world.tracked("B")
    diff = support.git(world.repo_path, "diff", "--name-only", "-z", world.sha("A"), world.sha("B")).split("\0")
    changed = sorted(p for p in diff if p and p in set(tracked) and not support.excluded(p, ex))
    others = [p for p in tracked if not support.excluded(p, ex) and p not in changed]
    assert sel["changed"] == changed, (sel["changed"], changed)
    assert sel["sample"] == random.Random(4242).sample(others, min(400, len(others)))
    read_only(wall)


@pytest.mark.parametrize("commit,sealed", [("B", True), ("PU", False), ("PC", False)])
def test_s24_writer_2_s_seal_json_says_whether_the_seal_is_in_the_path_map(world, commit, sealed):
    run = sa.dry(world, "writer-heldout", "held-out", seed=4242, commit=commit)
    assert run.code == 0, run.why()
    wall = world.wall(run.line)
    assert sa.input_listing(wall) == ["seal.json", "selection.json"]
    assert json.loads((wall / "input/seal.json").read_text()) == {"sealed": sealed}
    read_only(wall)


@pytest.mark.parametrize("half", sa.HALVES)
def test_s24_labeller_1_round_1_stages_the_half_s_lines_kept_to_the_brief_s_fields(world, half):
    sa.plant_half(world, half)
    run = sa.dry(world, "labeller", half, seed=5150, round_=1)
    assert run.code == 0, run.why()
    wall = world.wall(run.line)
    assert sa.input_listing(wall) == ["actions.jsonl", "cases.jsonl", "half.json"]
    assert json.loads((wall / "input/half.json").read_text()) == {"half": half, "pin": world.sha("B")}
    actions, cases = sa.staged(world, half)
    assert sa.read_jsonl(wall / "input/actions.jsonl") == actions
    assert sa.read_jsonl(wall / "input/cases.jsonl") == cases
    data = sa.wall_bytes(wall)
    assert sa.WHAT_CAME_BACK.encode() not in data and sa.PLANTED_EXTRA.encode() not in data
    read_only(wall)


def round1_labeller_2(world, half):
    run = sa.deliver(world, "labeller-2", half, round_=1, out=sa.labeller2_r1_out())
    assert run.code == 0, run.why()
    return run


def test_s24_round_2_stages_round_1_s_delivered_files(world):
    sa.plant_half(world, "held-out")
    round1_labeller_2(world, "held-out")
    kept = world.half("held-out") / "labels/r1-sgx1-labeller-2/rulebook-2.md"
    assert kept.read_text() == sa.RULEBOOK_2
    run = sa.dry(world, "labeller-2", "held-out", seed=777, round_=2)
    assert run.code == 0, run.why()
    wall = world.wall(run.line)
    assert sa.input_listing(wall) == ["half.json", "round1/rulebook-2.md", "sample.jsonl"]
    assert (wall / "input/round1/rulebook-2.md").read_bytes() == kept.read_bytes()
    read_only(wall)


def test_s24_a_round_1_file_changed_since_its_counts_refuses_10(world):
    sa.plant_half(world, "tuning")
    round1_labeller_2(world, "tuning")
    kept = world.half("tuning") / "labels/r1-sgx1-labeller-2/rulebook-2.md"
    os.chmod(kept, 0o600)
    kept.write_bytes(support.flip_last_letter(kept.read_bytes()))
    before = world.built_state("labeller")
    support.next_second()
    run = world.launch(*sa.args(world, "labeller-2", "tuning", round_=2, seed=777, dry=True), env=sa.rules_env())
    assert_refused(world, run, 10)
    walls, trees, ledger = world.built_state("labeller")
    assert (walls, trees, ledger) == before, "something was built"


MISSING = {"labeller-actions": ("labeller", 1, "corpus/actions.jsonl"),
           "labeller-cases": ("labeller", 1, "planted/cases.jsonl"),
           "labeller-2-round-1": ("labeller-2", 2, None),
           "overlap-auditor-labels-2": ("overlap-auditor", None, "labels/labels-2.jsonl")}


@pytest.mark.parametrize("what", sorted(MISSING))
def test_s24_a_missing_input_refuses_10_before_anything_is_written(world, what):
    """Then, the input there, the same launch builds (so the 10 is the missing input's, not stage 10's)."""
    flow, round_, rel = MISSING[what]
    sa.plant_half(world, "tuning")
    if flow == "overlap-auditor":
        sa.plant_labels(world, "tuning")
    if rel:
        (world.half("tuning") / rel).unlink()
    kind = sa.FLOW[flow][0]
    before = world.built_state(kind)
    sr_before, exp_before = world.hashes(world.sr), world.hashes(world.exp)
    run = world.launch(*sa.args(world, flow, "tuning", round_=round_, seed=5150, dry=True), env=sa.rules_env())
    assert_refused(world, run, 10)
    assert_nothing_built(world, kind, before)
    assert world.hashes(world.sr) == sr_before and world.hashes(world.exp) == exp_before
    if flow == "labeller-2":
        assert round1_labeller_2(world, "tuning").code == 0
    elif flow == "overlap-auditor":
        sa.plant_labels(world, "tuning")
    else:
        sa.plant_half(world, "tuning")
    good = sa.dry(world, flow, "tuning", seed=5150, round_=round_)
    assert good.code == 0, good.why()


SET_MISMATCH = [("writer-tuning", "held-out"), ("writer-heldout", "tuning"), ("labeller", "memory-verdict-3"),
                ("labeller-2", "sandbox-guard-exp-1"), ("overlap-auditor", "memory-verdict-3")]


@pytest.mark.parametrize("flow,set_", SET_MISMATCH)
def test_s24_a_set_that_is_not_the_flow_s_half_refuses_17(world, flow, set_):
    for half in sa.HALVES:
        plant_for(world, flow, half)
    kind = sa.FLOW[flow][0]
    before = world.built_state(kind)
    run = world.launch(*world.args(kind, brief=sa.FLOW[flow][1], set_=set_, round_=1 if kind == "labeller" else None,
                                   dry=True), env=sa.rules_env())
    assert_refused(world, run, 17)
    assert_nothing_built(world, kind, before)
