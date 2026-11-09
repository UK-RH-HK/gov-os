"""S4 (the seed first), S5 (the content by rule), S6 (the seed drawn by the script), S20 (the second labeller's overlap).

The selection is recomputed here from the planted repository alone (``World.expected_selection``: ``git diff
--name-only <last audit> <commit>`` less ``tree-exclude.txt``, then ``random.Random(seed).sample`` of the other tracked
paths, sized by the brief's ``sample:``), never from the script.
"""

from __future__ import annotations

import json
import math
import os
import random
import re
import stat
import subprocess
import sys

import pytest

import w2_149_support as support
from w2_149_support import assert_good_launch, assert_refused


def files_under(root):
    for dp, _dn, fn in os.walk(root):
        for n in fn:
            yield os.path.join(dp, n)


# -- S4 -------------------------------------------------------------------------------------------------------------

def test_s4_the_seed_and_its_ledger_line_come_before_every_input_and_tree_file(world):
    run = world.launch(*world.args("writer", seed=31337, dry=True))
    assert run.code == 0, run.why()
    line = run.line
    wall, tree = world.wall(line), world.tree(line)
    seed = wall / "seed.txt"
    assert seed.read_bytes() == b"31337\n"
    assert stat.S_IMODE(os.stat(seed).st_mode) == 0o444
    seed_ns = os.stat(seed).st_mtime_ns
    later = list(files_under(wall / "input")) + list(files_under(tree))
    assert later, "no input or tree file"
    first = min(os.lstat(p).st_mtime_ns for p in later)
    assert seed_ns < first, "seed.txt is not earlier (ns) than every file under input/ and the tree"
    assert os.stat(world.ledger).st_mtime_ns < first, "the SEEDS.log line was not written before the content"
    mine = [x for x in world.ledger_lines() if x.get("run") == line["run"]]
    assert len(mine) == 1, world.ledger_lines()
    entry = mine[0]
    digest = support.sha_file(seed)
    assert entry["seed_sha256"] == digest and entry["seed"] == 31337
    assert entry["kind"] == "writer" and entry["commit"] == world.sha("B") and isinstance(entry["time"], str)
    assert json.loads((wall / "input/selection.json").read_text())["seed_sha256"] == digest
    manifest = json.loads((wall / "WALL.json").read_text())
    assert manifest["seed_sha256"] == digest and manifest["seeded_before_content"] is True
    assert line["seed_sha256"] == digest
    assert world.calls() == [], "a --dry build started claude"


def test_s4_a_seed_newer_than_the_input_refuses_13(world):
    """The forced reordering: the test hook, at ``after_input``, gives seed.txt a later mtime than the input's."""
    hook = world.write_hook({"after_input": [{"op": "future_mtime", "rel": "seed.txt"}]})
    run = world.launch(*world.args("writer", dry=True), env=hook)
    assert "after_input" in world.hook_points(), "the test hook's point after_input was not run"
    assert_refused(world, run, 13)
    assert world.calls() == []
    assert_good_launch(world, "writer")


def test_s4_a_missing_ledger_line_refuses_13(world):
    """The test hook, at ``after_input``, removes this run's SEEDS.log line."""
    hook = world.write_hook({"after_input": [{"op": "drop_ledger_line"}]})
    run = world.launch(*world.args("writer", dry=True), env=hook)
    assert "after_input" in world.hook_points(), "the test hook's point after_input was not run"
    assert_refused(world, run, 13)
    assert world.calls() == []
    assert_good_launch(world, "writer")


# -- S5 -------------------------------------------------------------------------------------------------------------

def test_s5_two_dry_builds_with_one_seed_select_the_rule_s_paths(world):
    runs = []
    for i in range(2):
        if i:
            support.next_second()
        run = world.launch(*world.args("writer", seed=12345, dry=True))
        assert run.code == 0, run.why()
        runs.append(run.line)
    a, b = (json.loads((world.wall(x) / "input/selection.json").read_text()) for x in runs)
    assert runs[0]["run"] != runs[1]["run"]
    assert a == b, "the same seed and commit gave different selections"
    changed, sample = world.expected_selection(12345, 5)
    assert changed, "premise: the planted diff has changed paths"
    assert a["commit"] == world.sha("B") and a["last_audit"] == world.sha("A")
    assert a["seed_sha256"] == support.sha256(b"12345\n")
    assert a["changed"] == changed, (a["changed"], changed)
    assert a["sample"] == sample, (a["sample"], sample)
    assert runs[0]["selection"]["changed"] == len(changed) and runs[0]["selection"]["sample"] == len(sample)


ALLOWED_OPTIONS = {"--sets-root", "--kind", "--brief", "--brief-sha256", "--commit", "--set", "--round", "--seed",
                   "--dry", "--counts-only", "--run", "--audit", "--help", "-h"}


def test_s5_the_argument_parser_offers_no_path_or_path_list_option(world):
    if not support.SCRIPT.is_file():
        pytest.fail("governance/project/orchestration/tools/indep_launch.py does not exist yet (W2-149 builds it)")
    p = subprocess.run([sys.executable, str(support.SCRIPT), "--help"], capture_output=True, text=True, timeout=60,
                       cwd=str(world.repo_path), env=world.base_env())
    assert p.returncode == 0, p.stderr
    options = set(re.findall(r"(?<![\w-])(--?[a-z][a-z0-9-]*)", p.stdout))
    extra = options - ALLOWED_OPTIONS
    assert not extra, f"options beyond the interface's: {sorted(extra)}"
    before = world.built_state("writer")
    run = world.launch(*world.args("writer", dry=True), "--paths", "docs/d01.md")
    assert run.code != 0, "an unknown path option was accepted"
    assert world.built_state("writer") == before


@pytest.mark.parametrize("kind,round_", [("writer", 2), ("checker", 1), ("auditor", 1), ("labeller", 1)])
def test_s5_the_kind_s_inputs_are_read_only_copies_from_the_sets_root(world, kind, round_):
    sr = world.sr
    hidden = sr / "fixtures/evaluation/memory-verdict-3/hidden"
    if kind == "writer":
        support.write_file(sr, "fixtures/evaluation/memory-verdict-3/XCHECK-r1.md", "# the checker's notes\n")
    run = world.launch(*world.args(kind, round_=round_, set_=None if kind != "writer" else "memory-verdict-3",
                                   dry=True))
    assert run.code == 0, run.why()
    inp = world.wall(run.line) / "input"
    want = {"selection.json": None}
    if kind in ("writer", "checker", "auditor"):
        for p in files_under(hidden):
            want["set/" + os.path.relpath(p, hidden)] = open(p, "rb").read()
    if kind == "writer":
        want["notes.md"] = (sr / "fixtures/evaluation/memory-verdict-3/XCHECK-r1.md").read_bytes()
    if kind == "auditor":
        want["misses.jsonl"] = (sr / "runs/audit-1/misses.jsonl").read_bytes()
    if kind == "labeller":
        want["rulebook.md"] = (sr / support.SEALED / "rulebook.md").read_bytes()
        want["actions.jsonl"] = (sr / support.SEALED / "corpus/actions-r1.jsonl").read_bytes()
    got = {os.path.relpath(p, inp): p for p in files_under(inp)}
    assert set(got) == set(want), (sorted(got), sorted(want))
    for rel, data in want.items():
        if data is not None:
            assert open(got[rel], "rb").read() == data, rel
        assert stat.S_IMODE(os.stat(got[rel]).st_mode) & 0o222 == 0, f"input/{rel} is writable"
    assert stat.S_IMODE(os.stat(inp).st_mode) & 0o222 == 0, "input/ is writable"


# -- S6 -------------------------------------------------------------------------------------------------------------

def test_s6_two_real_builds_draw_different_63_bit_seeds(world):
    lines = []
    for set_ in ("memory-verdict-4", "memory-verdict-5"):  # each writer delivers a new set
        run = world.deliver("writer", set_=set_)
        assert run.code == 0, run.why()
        lines.append(run.line)
    seeds = []
    for line in lines:
        mine = [x for x in world.ledger_lines() if x.get("run") == line["run"]]
        assert len(mine) == 1
        s = mine[0]["seed"]
        assert isinstance(s, int) and 0 <= s < 2 ** 63
        assert mine[0]["seed_sha256"] == support.sha256(f"{s}\n".encode()) == line["seed_sha256"]
        seeds.append(s)
    assert seeds[0] != seeds[1], "two real builds drew the same seed"


# -- S20 ------------------------------------------------------------------------------------------------------------

def overlap_ids(world):
    text = (world.sr / support.SEALED / "corpus/actions-r1.jsonl").read_text()
    return [json.loads(x)["id"] for x in text.splitlines() if x.strip()]


def test_s20_the_overlap_is_ten_percent_rounded_up_drawn_with_the_second_run_s_seed(world):
    ids = overlap_ids(world)
    k = math.ceil(len(ids) / 10)
    assert len(ids) == 23 and k == 3, "premise: 23 actions, 2.3 rounds up to 3"
    want = random.Random(777).sample(ids, k)
    lines = []
    for i in range(2):
        if i:
            support.next_second()
        run = world.launch(*world.args("labeller", round_=2, seed=777, dry=True))
        assert run.code == 0, run.why()
        lines.append(run.line)
    sel = [json.loads((world.wall(x) / "input/selection.json").read_text()) for x in lines]
    assert sel[0]["overlap"] == sel[1]["overlap"] == want, (sel[0].get("overlap"), want)
    by_id = {json.loads(x)["id"]: x for x in
             (world.sr / support.SEALED / "corpus/actions-r1.jsonl").read_text().splitlines() if x.strip()}
    own = [x for x in (world.sr / support.SEALED / "corpus/actions-r2.jsonl").read_text().splitlines() if x.strip()]
    staged = [x for x in (world.wall(lines[0]) / "input/actions.jsonl").read_text().splitlines() if x.strip()]
    assert sorted(staged) == sorted(own + [by_id[i] for i in want])
    assert lines[0]["selection"]["overlap"] == k


def test_s20_no_other_input_differs_between_the_two_labellers(world):
    r1 = world.launch(*world.args("labeller", round_=1, seed=777, dry=True))
    assert r1.code == 0, r1.why()
    r2 = world.launch(*world.args("labeller", round_=2, seed=777, dry=True))
    assert r2.code == 0, r2.why()
    w1, w2 = world.wall(r1.line), world.wall(r2.line)
    assert sorted(os.listdir(w1 / "input")) == sorted(os.listdir(w2 / "input"))
    assert (w1 / "input/rulebook.md").read_bytes() == (w2 / "input/rulebook.md").read_bytes()
    assert (w1 / "brief.md").read_bytes() == (w2 / "brief.md").read_bytes()
    s1, s2 = (json.loads((w / "input/selection.json").read_text()) for w in (w1, w2))
    s1.pop("overlap", None)
    s2.pop("overlap", None)
    assert s1 == s2, "the two labellers' selections differ beside the overlap"
    assert (w1 / "input/actions.jsonl").read_bytes() == (world.sr / support.SEALED / "corpus/actions-r1.jsonl").read_bytes()
