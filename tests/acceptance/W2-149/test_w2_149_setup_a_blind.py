"""F36 and F38 closed (DEC-1112 (3), the CTO's decision; DEC-1113 (2): the overlap auditor decides from the decisions
alone, blind): S27 changed (every dispute side's ``reason`` is staged as ``""``, whatever the labellers wrote; x/y stay
in the seeded order and the other label fields stay), S23 changed (the overlap auditor's ``briefs:`` entry also leaves
out of its tree every file that states which dispute side is which labeller's; the other four set-up A entries keep
their exclusions, and a brief with no entry keeps all of these files).

Written from the ticket's S23 and S27 lines and its last note; the interface is this folder's README ("Set-up A's
wiring: the interface", marked (F36) and (F38)). The planted ``kinds.yaml``'s five set-up A entries carry this tree's
own template entries' ``tree_exclude`` (``w2_149_support.template_entry_excludes``), so a dry build exercises the
template as it stands; the planted repository holds one file under each of the auditor's further globs
(``w2_149_support.TELL_FILES`` and the planted tickets), none left out by ``tree-exclude.txt``.
"""

from __future__ import annotations

import os

import pytest
import yaml

import w2_149_setup_a as sa
import w2_149_support as support

BRIEFS_GLOB = "governance/project/indep-briefs/**"
REASON1 = "R1-W2149-labeller-one-reason"
REASON2 = "R2-W2149-labeller-two-reason"


def tree_files(tree):
    return sorted(os.path.relpath(os.path.join(dp, n), tree) for dp, _dn, fn in os.walk(tree) for n in fn)


def tells(world, key="B"):
    """The tracked files at ``key`` under the overlap auditor's further globs that tree-exclude.txt keeps; premise:
    every one of the six globs has one."""
    ex = world.exclusions(key)
    files = [p for p in world.tracked(key)
             if support.excluded(p, support.AUDITOR_TREE_EXCLUDE) and not support.excluded(p, ex)]
    for g in support.AUDITOR_TREE_EXCLUDE:
        assert any(support.excluded(p, [g]) for p in files), f"premise: the planted commit holds no file under {g}"
    return files


# -- S27 (F36): every dispute side's reason blanked ------------------------------------------------------------------

def test_s27_two_reasons_are_both_blanked_and_the_other_label_fields_stay_in_the_seeded_order(world):
    """Disputes where both labellers wrote a reason (labeller 1's hand lines, labeller 2's every line) are staged with
    both reasons "": no reason text of either labeller enters the wall; label, rule_class and clauses stay as each
    file has them, x/y in the order random.Random(seed) draws."""
    sa.plant_half(world, "tuning", n_actions=48, n_cases=12)
    planted = sa.plant_labels(world, "tuning")
    h = world.half("tuning")
    planted["lines1"] = [dict(x, reason=f"{REASON1} {x['id']}") if x["reason"] else x for x in planted["lines1"]]
    planted["lines2"] = [dict(x, reason=f"{REASON2} {x['id']}") for x in planted["lines2"]]
    support.write_file(h, "labels/labels.jsonl", sa.jsonl(planted["lines1"]))
    support.write_file(h, "labels/labels-2.jsonl", sa.jsonl(planted["lines2"]))
    ids_run = sorted(planted["undecided"])[:40]
    one = {x["id"]: x for x in planted["lines1"]}
    two = {x["id"]: x for x in planted["lines2"]}
    both = [i for i in ids_run if one[i]["reason"] and two[i]["reason"]]
    assert len(both) >= 10, "premise: disputes where both sides carry a reason are in the run"
    run = sa.dry(world, "overlap-auditor", "tuning", seed=5150)
    assert run.code == 0, run.why()
    wall = world.wall(run.line)
    rows = sa.read_jsonl(wall / "input/disputes.jsonl")
    got = {x["id"]: x for x in rows}
    order = sa.xy(5150, ids_run)
    for i in both:
        assert (got[i]["x"]["reason"], got[i]["y"]["reason"]) == ("", ""), ("a labeller's reason was staged", got[i])
        side = {1: one[i], 2: two[i]}
        a, b = order[i]
        for k in ("label", "rule_class", "clauses"):
            assert (got[i]["x"][k], got[i]["y"][k]) == (side[a][k], side[b][k]), (k, got[i])
    assert all(r["x"]["reason"] == "" and r["y"]["reason"] == "" for r in rows), "a dispute keeps a reason"
    assert rows == sa.expected_disputes(world, "tuning", planted, 5150, ids_run)
    for mark in (REASON1, REASON2):
        assert sa.files_holding([wall, world.tree(run.line)], mark) == [], f"{mark} reached the wall"


# -- S23 (F38): the overlap auditor's tree leaves out every file that tells the sides apart --------------------------

def test_s23_the_template_s_overlap_auditor_entry_also_leaves_out_every_file_that_tells_the_sides_apart():
    """This tree's own template (what the engineer changes): the overlap auditor's entry's tree_exclude is the four
    globs and the six further ones; the other four set-up A entries keep exactly the four."""
    doc = yaml.safe_load((support.TEMPLATE_SRC / "kinds.yaml").read_text())
    briefs = doc.get("briefs") or {}
    aud = briefs.get("sgx1-overlap-auditor") or {}
    tx = list(aud.get("tree_exclude") or [])
    missing = [g for g in support.AUDITOR_TREE_EXCLUDE if g not in tx]
    assert missing == [], f"the overlap auditor's entry does not leave out {missing}"
    assert set(tx) == set(support.SGX1_TREE_EXCLUDE) | set(support.AUDITOR_TREE_EXCLUDE), tx
    for bid in support.SGX1_IDS:
        if bid != "sgx1-overlap-auditor":
            got = set((briefs.get(bid) or {}).get("tree_exclude") or [])
            assert got == set(support.SGX1_TREE_EXCLUDE), (bid, sorted(got))


def test_s23_the_overlap_auditor_s_tree_holds_none_of_the_files_that_tell_the_sides_apart(world):
    """A dry build at the planted commit holding a file under each further glob: the auditor's tree is the archive
    less tree-exclude.txt, less the four globs and less the six; no tell's text is anywhere in its wall or tree; its
    tickets still arrive in input/tickets.jsonl (the exclusion limits the tree, not the staging)."""
    sa.plant_half(world, "tuning", n_actions=48, n_cases=12)
    sa.plant_labels(world, "tuning")
    planted_tells = tells(world)
    run = sa.dry(world, "overlap-auditor", "tuning", seed=5150)
    assert run.code == 0, run.why()
    got = tree_files(world.tree(run.line))
    held = [p for p in got if support.excluded(p, support.AUDITOR_TREE_EXCLUDE)]
    assert held == [], f"the overlap auditor's tree holds {len(held)} of {len(planted_tells)} tells: {held[:6]}"
    ex = world.exclusions("B")
    want = sorted(p for p in world.tracked("B") if not support.excluded(p, ex)
                  and not support.excluded(p, [BRIEFS_GLOB])
                  and not support.excluded(p, support.SGX1_TREE_EXCLUDE)
                  and not support.excluded(p, support.AUDITOR_TREE_EXCLUDE))
    assert got == want, sorted(set(got) ^ set(want))[:6]
    roots = [world.wall(run.line), world.tree(run.line)]
    for mark in (support.TELL_MARK, support.TICKET_MARK):
        assert sa.files_holding(roots, mark) == [], f"{mark} is in the auditor's wall or tree"
    ids_run = []
    for x in sa.read_jsonl(world.wall(run.line) / "input/disputes.jsonl"):
        ids_run.append(x["id"])
    tickets = sa.read_jsonl(world.wall(run.line) / "input/tickets.jsonl")
    assert sorted(tickets, key=lambda t: t["id"]) == sa.expected_tickets(world, "tuning", ids_run)


OTHERS = ("writer-tuning", "writer-heldout", "labeller", "labeller-2", "memory-writer", "memory-auditor")


@pytest.mark.parametrize("who", OTHERS)
def test_s23_every_other_tree_still_holds_the_files_the_overlap_auditor_s_leaves_out(world, who):
    """The other four set-up A entries keep their own exclusions (the four globs only), and a brief with no entry
    (a memory writer's, a memory auditor's: the same kind as the overlap auditor) keeps every one of these files."""
    planted_tells = tells(world)
    if who.startswith("memory-"):
        run = world.launch(*world.args(who.split("-", 1)[1], seed=4242, dry=True))
    else:
        half = "held-out" if who == "writer-heldout" else "tuning"
        if who in ("labeller", "labeller-2"):
            sa.plant_half(world, half, n_actions=48, n_cases=12)
        run = sa.dry(world, who, half, seed=4242, round_=1 if who.startswith("labeller") else None)
    assert run.code == 0, run.why()
    got = set(tree_files(world.tree(run.line)))
    missing = sorted(p for p in planted_tells if p not in got)
    assert missing == [], f"{who}'s tree leaves out {missing}"
    if not who.startswith("memory-"):
        assert not any(support.excluded(p, support.SGX1_TREE_EXCLUDE) for p in got), "the entry's four globs held"
