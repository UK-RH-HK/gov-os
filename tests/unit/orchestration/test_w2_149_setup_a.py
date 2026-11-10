"""W2-149, set-up A's wiring (DEC-1112 (3), DEC-1113): the engineer's unit tests for indep_launch.py's set-up A flows.

Planted roots only (HOME, the sets root, the repository, a stub `claude`), as test_w2_149_indep_launch.py's World. The
rule script runs through a stand-in `bwrap` that runs the command it is given unconfined, so the prelude's caps and
seccomp filter (no process, no exec, no socket) and the launcher's checks are exercised here; the cases that need the
real bwrap's walls (a file outside, the network) are marked `bwrap` and run only with GOV_W2_149_BWRAP=1 (outside the
Claude sandbox, where a nested bwrap cannot start).
"""
import hashlib
import json
import os
import random
import shutil
import stat
import sys
import tarfile
from pathlib import Path

import pytest

from test_w2_149_indep_launch import (SCHEMAS, TEMPLATE, TEMPLATE_FILES, WALLS, KINDS, World, indep_launch, sha,
                                      tree_hash, schema, assert_counts, nothing_built)

BWRAP = os.environ.get("GOV_W2_149_BWRAP") == "1"
needs_bwrap = pytest.mark.skipif(not BWRAP or not shutil.which("bwrap"),
                                 reason="bwrap: run with GOV_W2_149_BWRAP=1 outside the sandbox")
PY = os.path.realpath(sys.executable)

# The five approved briefs' front matter, byte for byte (their bodies are not the launcher's business).
FRONT = {
    "sgx1-labeller": ("labeller", "---\nbrief: sgx1-labeller\nkind: labeller\nversion: 3\nexperiment: "
                      "SANDBOX-GUARD-EXP-1\nrounds: 2\ntools: [Read, Grep, Glob, Write, TodoWrite]\nbudget_usd: 30\n"
                      "timeout_s: 10800\n---\n"),
    "sgx1-labeller-2": ("labeller", "---\nbrief: sgx1-labeller-2\nkind: labeller\nversion: 3\nexperiment: "
                        "SANDBOX-GUARD-EXP-1\nrounds: 2\ntools: [Read, Grep, Glob, Write, TodoWrite]\nbudget_usd: 30\n"
                        "timeout_s: 10800\n---\n"),
    "sgx1-writer-tuning": ("writer", "---\nbrief: sgx1-writer-tuning\nkind: writer\nversion: 3\nexperiment: "
                           "SANDBOX-GUARD-EXP-1\nrounds: 1\ntools: [Read, Grep, Glob, Write, Edit, TodoWrite]\n"
                           "sample: 400\nbudget_usd: 25\ntimeout_s: 7200\n---\n"),
    "sgx1-writer-heldout": ("writer", "---\nbrief: sgx1-writer-heldout\nkind: writer\nversion: 3\nexperiment: "
                            "SANDBOX-GUARD-EXP-1\nrounds: 1\ntools: [Read, Grep, Glob, Write, Edit, TodoWrite]\n"
                            "sample: 400\nbudget_usd: 25\ntimeout_s: 7200\n---\n"),
    "sgx1-overlap-auditor": ("auditor", "---\nbrief: sgx1-overlap-auditor\nkind: auditor\nversion: 1\nexperiment: "
                             "SANDBOX-GUARD-EXP-1\nrounds: 1\ntools: [Read, Grep, Glob, Write, TodoWrite]\n"
                             "budget_usd: 10\ntimeout_s: 3600\nbudget_basis: \"the labellers' figures scaled\"\n---\n"),
}
SEALED_MAP = """\
evaluation_sets:
  sandbox-guard-exp-1:
    visible: []
    hidden: ["fixtures/evaluation/sandbox-guard-exp-1/hidden/**"]
sets_root_hidden:
  root: "~/gov-os-eval"
  hidden: ["fixtures/evaluation/*/hidden/**", "transcripts/**", "indep-walls/**"]
  refused_roles: [orchestrator]
"""
FAKE_BWRAP = """#!/usr/bin/env python3
# A stand-in bwrap for the sandbox (no nested namespaces): records its argv, runs the command after the options.
import json, os, sys
a = sys.argv[1:]
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bwrap-calls.jsonl"), "a") as f:
    f.write(json.dumps(a) + "\\n")
i = a.index("-I") - 1
os.execv(a[i], a[i:])
"""
GOOD_RULES = """import json, sys
for line in sys.stdin:
    a = json.loads(line)
    n = int(a["id"].split("-")[1])
    print(json.dumps({"id": a["id"], "label": "allow" if n % 3 else "refuse", "rule_class": 14 if n % 3 else 11,
                      "clauses": ["DEC-820 (4)"], "uncertain": n % 7 == 0}))
"""


class Sgx(World):
    def __init__(self, tmp):
        super().__init__(tmp)
        for bid, (_kind, front) in FRONT.items():
            self.put(f"governance/project/indep-briefs/{bid}.md", front + f"# {bid}\n")
        for rel in (".claude/settings.json", "src/gov/guard/g.py", "src/gov/launch/l.py"):
            self.put(rel, "guarded\n")
        self.put(".tickets/DAEO-aaaa.md", "---\nid: DAEO-aaaa\nrole: engineer\nwbs_id: W2-1\nallowed_paths: [src/a/**]\n"
                                          "title: one\n---\nbody\n")
        self.put(".tickets/DAEO-bbbb.md", "---\nid: DAEO-bbbb\nrole: orchestrator\nwbs_id: W2-2\nallowed_paths: []\n---\n")
        self.commit = self.commit_all("set-up A")
        self.approve()
        fb = self.bin / "bwrap"
        fb.write_text(FAKE_BWRAP)
        fb.chmod(0o755)

    def approve(self, commit=None, drop_brief=None):
        super().approve(commit, drop_brief)
        commit = commit or self.commit
        lines = []
        for bid, (kind, _f) in FRONT.items():
            rel = f"governance/project/indep-briefs/{bid}.md"
            try:
                lines.append(f"{sha(self.blob(commit, rel))}  brief {kind} {rel}")
            except Exception:
                pass
        with open(self.sets / WALLS / "APPROVED", "a") as f:
            f.write("\n".join(lines) + "\n")

    def env(self, extra=None):
        env = super().env(extra)
        env.setdefault("GOV_INDEP_RULES_PYTHON", PY)
        if not BWRAP:
            env.setdefault("GOV_INDEP_BWRAP", str(self.bin / "bwrap"))
        return env

    def h(self, half):
        if half == "tuning":
            return self.home / "gov-os-runs" / "SANDBOX-GUARD-EXP-1" / "tuning"
        return self.sets / "fixtures" / "evaluation" / "sandbox-guard-exp-1" / "hidden"

    def plant_half(self, half="tuning", actions=12, cases=6, extra=False):
        h = self.h(half)
        (h / "corpus").mkdir(parents=True, exist_ok=True)
        (h / "planted").mkdir(parents=True, exist_ok=True)
        acts = []
        for i in range(actions):
            a = {"id": f"a-{i:03d}", "role": "engineer", "agent": None, "ticket": "DAEO-aaaa", "wbs": "W2-1",
                 "tool": "Read", "input": {"file_path": f"/x/{i}"}, "cwd": "/x", "executable": True,
                 "strata": ["real"], "source": "replay"}
            if extra:
                a["session"] = "s-secret-session"
            acts.append(json.dumps(a) + "\n")
        cs = [json.dumps({"id": f"p-{i:03d}", "role": "orchestrator", "agent": None, "ticket": "DAEO-bbbb",
                          "wbs": "W2-2", "tool": "Bash", "input": {"command": "ls"}, "cwd": "/y", "executable": False,
                          "strata": ["planted"], "source": "planted-1", "rule_class": "11"}) + "\n"
              for i in range(cases)]
        (h / "corpus" / "actions.jsonl").write_text("".join(acts))
        (h / "planted" / "cases.jsonl").write_text("".join(cs))
        return h

    def sargs(self, bid, half="tuning", rnd=None, seed=None, dry=False, audit=None, commit=None):
        kind = FRONT[bid][0]
        commit = commit or self.commit
        rel = f"governance/project/indep-briefs/{bid}.md"
        a = ["--sets-root", str(self.sets), "--kind", kind, "--brief", rel,
             "--brief-sha256", sha(self.blob(commit, rel)), "--commit", commit, "--set", half]
        if rnd:
            a += ["--round", str(rnd)]
        if kind == "auditor":
            a += ["--audit", audit or "sgx1-overlap"]
        if seed is not None:
            a += ["--seed", str(seed)]
        if dry:
            a.append("--dry")
        return a

    def go(self, bid, extra=None, **kw):
        return self.run(*self.sargs(bid, **kw), extra=extra)

    def seed_of(self, counts):
        return next(x["seed"] for x in self.seeds() if x["run"] == counts["run"])

    def tar_names(self, counts):
        with tarfile.open(self.sets / WALLS / counts["kind"] / (counts["run"] + ".tar")) as t:
            return t.getnames()


@pytest.fixture
def s(tmp_path):
    return Sgx(tmp_path)


def by_rule(seed, word, ident, mod):
    return int(hashlib.sha256((str(seed) + word + ident).encode("utf-8")).hexdigest(), 16) % mod == 0


def inp(s, counts):
    return sorted(str(p.relative_to(s.wall(counts) / "input")) for p in (s.wall(counts) / "input").rglob("*")
                  if p.is_file())


def r1_result():
    return json.dumps({"round": 1, "rules": 12, "instructions_ignored": 0, "stopped": "none"})


def by14(n=0):
    return {str(i): n for i in range(1, 15)}


# -- S22: stage 10 takes the template's defaults -----------------------------------------------------------------
def test_resolve_brief_precedence_and_refusals():
    spec = {"model": "kind-model"}
    briefs = {"b1": {"kind": "labeller", "flow": "sgx1-labeller-1", "result_schema": "e.schema.json", "sample": 0,
                     "tree_exclude": [], "model": "entry-model"},
              "b2": {"kind": "writer", "flow": "sgx1-writer-1", "result_schema": "w.schema.json", "tree_exclude": []},
              "bad": {"kind": "labeller", "flow": "sgx1-writer-1", "result_schema": "e.schema.json", "sample": 0}}
    r = indep_launch.resolve_brief({"brief": "b1"}, "labeller", spec, briefs)
    assert r[:4] == ("entry-model", "e.schema.json", 0, "b1")
    r = indep_launch.resolve_brief({"brief": "b1", "model": "fm-model", "sample": 5, "result_schema": "f.schema.json"},
                                   "labeller", spec, briefs)
    assert r[:3] == ("fm-model", "f.schema.json", 5)  # the front matter beats the entry
    r = indep_launch.resolve_brief({"brief": "b2", "sample": 4}, "writer", spec, briefs)
    assert r[:3] == ("kind-model", "w.schema.json", 4)  # the kind's model last
    for fm, kind in (({"brief": "b2"}, "writer"),                 # no sample anywhere
                     ({"brief": "b1"}, "auditor"),                # an entry of another kind
                     ({"brief": "nope"}, "labeller"),             # an id the map does not hold
                     ({}, "labeller"),                            # a labeller without an entry
                     ({"brief": "bad"}, "labeller"),              # a flow of another kind
                     ({"brief": "b2", "sample": 1}, "writer")):   # fine: control below
        if fm == {"brief": "b2", "sample": 1}:
            continue
        with pytest.raises(indep_launch.Refuse) as e:
            indep_launch.resolve_brief(fm, kind, spec, briefs)
        assert e.value.code == 10
    with pytest.raises(indep_launch.Refuse):
        indep_launch.resolve_brief({"brief": "b2", "sample": 1}, "writer", {}, briefs)  # no model anywhere


def test_the_five_briefs_pass_stage_ten_in_dry_builds(s):
    s.plant_half("tuning")
    for bid, half, rnd in (("sgx1-writer-tuning", "tuning", 1), ("sgx1-writer-heldout", "held-out", 1),
                           ("sgx1-labeller", "tuning", 1), ("sgx1-labeller-2", "tuning", 1)):
        rc, counts, p = s.go(bid, half=half, rnd=rnd, seed=5, dry=True)
        assert rc == 0, (bid, counts, p.stderr)
        assert_counts(counts, 0, "dry")
        m = json.loads((s.wall(counts) / "WALL.json").read_text())
        entry = indep_launch.load_briefs((TEMPLATE / "kinds.yaml").read_bytes())[bid]
        assert m["model"] == "claude-opus-5-5" and m["result_schema"] == entry["result_schema"]
        assert m["brief_id"] == bid and m["flow"] == entry["flow"]
        assert json.loads((s.wall(counts) / ".claude" / "settings.json").read_text())["model"] == "claude-opus-5-5"


def test_template_kinds_yaml_holds_the_five_entries():
    data = (TEMPLATE / "kinds.yaml").read_bytes()
    kinds, briefs = indep_launch.load_kinds(data), indep_launch.load_briefs(data)
    assert all(kinds[k]["model"] == "claude-opus-5-5" for k in KINDS)
    assert set(briefs) == {"sgx1-labeller", "sgx1-labeller-2", "sgx1-writer-tuning", "sgx1-writer-heldout",
                           "sgx1-overlap-auditor"}
    for bid, e in briefs.items():
        assert e["kind"] == FRONT[bid][0] and e["flow"] in indep_launch.FLOWS
        assert (SCHEMAS / e["result_schema"]).is_file()
        assert e["tree_exclude"] == [".claude/**", "src/gov/guard/**", "src/gov/launch/**",
                                     "governance/project/indep-walls/**"]
        if FRONT[bid][0] != "writer":
            assert e["sample"] == 0
    assert "governance/project/indep-briefs/**" in (TEMPLATE / "tree-exclude.txt").read_text().splitlines()


# -- S23: the trees ------------------------------------------------------------------------------------------------
def test_trees_leave_out_the_briefs_and_set_up_a_also_the_guard(s):
    rc, sgx, _ = s.go("sgx1-writer-tuning", seed=3, dry=True)
    rc2, mem, _ = s.launch(seed=3, dry=True)
    assert rc == rc2 == 0
    a, b = tree_hash(s.tree(sgx)), tree_hash(s.tree(mem))
    assert not [p for p in list(a) + list(b) if p.startswith("governance/project/indep-briefs/")]
    for p in (".claude/settings.json", "src/gov/guard/g.py", "src/gov/launch/l.py",
              f"governance/project/{WALLS}/kinds.yaml"):
        assert p not in a and p in b, p
    # the selection stays "less tree-exclude.txt": the guard's paths remain places a writer may name
    sel = json.loads((s.wall(sgx) / "input" / "selection.json").read_text())
    assert ".claude/settings.json" in sel["sample"]
    assert not [p for p in sel["sample"] if p.startswith("governance/project/indep-briefs/")]


# -- S24: --set, --round and the staged inputs ---------------------------------------------------------------------
@pytest.mark.parametrize("bid,half,rnd", [("sgx1-writer-tuning", "held-out", 1), ("sgx1-writer-heldout", "tuning", 1),
                                          ("sgx1-labeller", "memory-recall-3", 1), ("sgx1-writer-tuning", "tuning", 2),
                                          ("sgx1-overlap-auditor", "tuning", 2)])
def test_a_half_or_round_the_flow_does_not_take_17_nothing_built(s, bid, half, rnd):
    s.plant_half("tuning")
    rc, counts, _ = s.go(bid, half=half, rnd=rnd, seed=1, dry=True)
    assert rc == 17 and counts["reason"] == "argument"
    nothing_built(s)


def test_writer_two_seal_follows_the_path_map(s):
    rc, counts, _ = s.go("sgx1-writer-heldout", half="held-out", seed=1, dry=True)
    assert rc == 0 and inp(s, counts) == ["seal.json", "selection.json"]
    assert json.loads((s.wall(counts) / "input" / "seal.json").read_text()) == {"sealed": False}
    s.put("governance/project/path-map.yaml", SEALED_MAP)
    c = s.commit_all("seal")
    s.approve(c)
    rc, counts, _ = s.go("sgx1-writer-heldout", half="held-out", seed=1, dry=True, commit=c)
    assert rc == 0 and json.loads((s.wall(counts) / "input" / "seal.json").read_text()) == {"sealed": True}


def test_labeller_one_round_one_stages_the_half_kept_to_the_briefs_fields(s):
    h = s.plant_half("held-out", extra=True)
    rc, counts, _ = s.go("sgx1-labeller", half="held-out", seed=9, dry=True)
    assert rc == 0, counts
    assert inp(s, counts) == ["actions.jsonl", "cases.jsonl", "half.json"]
    w = s.wall(counts) / "input"
    assert json.loads((w / "half.json").read_text()) == {"half": "held-out", "pin": s.commit}
    acts = [json.loads(x) for x in (w / "actions.jsonl").read_text().splitlines()]
    src = [json.loads(x) for x in (h / "corpus" / "actions.jsonl").read_text().splitlines()]
    assert acts == [{k: v for k, v in a.items() if k != "session"} for a in src]
    assert (w / "cases.jsonl").read_bytes() == (h / "planted" / "cases.jsonl").read_bytes()  # nothing to drop
    assert "s-secret-session" not in (w / "actions.jsonl").read_text()
    assert not (w / "selection.json").exists()


def test_missing_inputs_refuse_10_before_anything_is_written(s):
    for bid, half, rnd in (("sgx1-labeller", "tuning", 1), ("sgx1-labeller", "tuning", 2),
                           ("sgx1-labeller-2", "held-out", 2), ("sgx1-overlap-auditor", "tuning", 1)):
        rc, counts, _ = s.go(bid, half=half, rnd=rnd, seed=1, dry=True)
        assert rc == 10, bid
    s.plant_half("tuning")
    rc, _, _ = s.go("sgx1-labeller", rnd=2, seed=1, dry=True)  # no round 1 delivered
    assert rc == 10
    rc, _, _ = s.go("sgx1-overlap-auditor", seed=1, dry=True)  # no labels
    assert rc == 10
    nothing_built(s)


# -- S20: the second labeller ----------------------------------------------------------------------------------------
def test_labeller_two_round_one_half_only_round_two_the_overlap_by_rule(s):
    h = s.plant_half("tuning", actions=60, cases=30)
    rc, counts, _ = s.go("sgx1-labeller-2", seed=1, dry=True)
    assert rc == 0 and inp(s, counts) == ["half.json"]
    # round 1, delivered: its rulebook kept for round 2
    s.stub({"session": "write", "out": {"out/result.json": r1_result(), "out/rulebook-2.md": "rules two\n"}})
    rc, r1, _ = s.go("sgx1-labeller-2")
    assert rc == 0, r1
    assert (h / "labels" / "r1-sgx1-labeller-2" / "rulebook-2.md").read_text() == "rules two\n"
    assert r1["delivered"] == {"files": 1, "sha256": sha(b"rules two\n"), "to": "round1",
                               "files_sha256": {"rulebook-2.md": sha(b"rules two\n")}}
    a = s.go("sgx1-labeller-2", rnd=2, seed=4242, dry=True)[1]
    b = s.go("sgx1-labeller-2", rnd=2, seed=4242, dry=True)[1]
    assert inp(s, a) == ["half.json", "round1/rulebook-2.md", "sample.jsonl"]
    got = (s.wall(a) / "input" / "sample.jsonl").read_bytes()
    assert got == (s.wall(b) / "input" / "sample.jsonl").read_bytes()
    lines = (h / "corpus" / "actions.jsonl").read_text().splitlines() + \
        (h / "planted" / "cases.jsonl").read_text().splitlines()
    want = [x for x in lines if by_rule(4242, "overlap", json.loads(x)["id"], 10)]
    assert got.decode().splitlines() == want and want
    assert a["selection"]["overlap"] == len(want)
    # round 1's file changed after delivery: 10
    (h / "labels" / "r1-sgx1-labeller-2" / "rulebook-2.md").write_text("changed\n")
    rc, _, _ = s.go("sgx1-labeller-2", rnd=2, seed=4242, dry=True)
    assert rc == 10


# -- S16 / S25 / S26: the first labeller -----------------------------------------------------------------------------
def labeller_one_round_one(s, half="tuning", rules=GOOD_RULES):
    h = s.plant_half(half)
    s.stub({"session": "write", "out": {"out/result.json": r1_result(), "out/rulebook.md": "the rules\n",
                                        "out/label_rules.py": rules}})
    rc, counts, _ = s.go("sgx1-labeller", half=half)
    assert rc == 0, counts
    return h, counts


def test_labeller_one_round_one_delivers_its_two_files(s):
    h, counts = labeller_one_round_one(s, "held-out")
    d = h / "labels" / "r1-sgx1-labeller"
    assert sorted(os.listdir(d)) == ["label_rules.py", "rulebook.md"]
    shas = {"label_rules.py": sha(GOOD_RULES.encode()), "rulebook.md": sha(b"the rules\n")}
    bundle = sha("".join(f"{v}  {k}\n" for k, v in sorted(shas.items())).encode())
    assert counts["delivered"] == {"files": 2, "sha256": bundle, "to": "round1", "files_sha256": shas}
    assert counts["out"]["round"] == 1 and counts["out"]["rules"] == 12 and counts["out"]["stopped"] == "none"
    assert_counts(counts, 0, "delivered")
    # an existing destination file: 20, nothing changes
    before = tree_hash(h)
    rc, again, _ = s.go("sgx1-labeller", half="held-out")
    assert rc == 20 and again["status"] == "rejected" and tree_hash(h) == before


def test_labeller_one_round_two_stages_script_labels_and_the_sample(s):
    h, _ = labeller_one_round_one(s)
    rc, counts, p = s.go("sgx1-labeller", rnd=2, seed=77, dry=True)
    assert rc == 0, (counts, p.stderr)
    assert inp(s, counts) == ["actions.jsonl", "cases.jsonl", "half.json", "round1/label_rules.py",
                              "round1/rulebook.md", "sample.json", "script-labels.jsonl"]
    w = s.wall(counts) / "input"
    ids = [json.loads(x)["id"] for x in (w / "actions.jsonl").read_text().splitlines()
           + (w / "cases.jsonl").read_text().splitlines()]
    labs = [json.loads(x) for x in (w / "script-labels.jsonl").read_text().splitlines()]
    assert [x["id"] for x in labs] == ids
    assert json.loads((w / "sample.json").read_text()) == {"ids": [i for i in ids if by_rule(77, "labeller-sample", i, 20)]}
    if not BWRAP:  # the stand-in records the confinement it was asked for
        argv = json.loads((s.bin / "bwrap-calls.jsonl").read_text().splitlines()[-1])
        for flag in ("--unshare-net", "--unshare-pid", "--unshare-user", "--die-with-parent", "--new-session",
                     "--remount-ro"):
            assert flag in argv, flag
        joined = " ".join(argv)
        for protected in (str(s.home), str(s.sets), str(s.repo)):
            assert protected not in joined, protected


def test_labeller_one_round_two_merges_hand_over_script_or_rejects_20(s):
    h, _ = labeller_one_round_one(s)
    ids = [f"a-{i:03d}" for i in range(12)] + [f"p-{i:03d}" for i in range(6)]
    r2 = json.dumps({"round": 2, "hand_labelled": 18, "allow": 10, "refuse": 8, "ask": 0, "by_class": by14(1),
                     "uncertain_seen": 2, "sample": 1, "instructions_ignored": 0, "stopped": "none"})
    # incomplete: no hand label at all, while the script put ids in class 11
    s.stub({"session": "write", "out": {"out/result.json": r2, "out/hand-labels.jsonl": ""}})
    before = tree_hash(h)
    rc, counts, _ = s.go("sgx1-labeller", rnd=2)
    assert rc == 20 and counts["status"] == "rejected" and tree_hash(h) == before
    # complete: every id hand-labelled but two the script settles (class 14, certain, outside any sample)
    hand = {i: {"id": i, "label": "ask", "rule_class": 13, "clauses": ["DEC-820"], "reason": "r"} for i in ids}
    s.stub({"session": "write", "out": {"out/result.json": r2, "out/hand-labels.jsonl":
                                        "".join(json.dumps(v) + "\n" for v in hand.values())}})
    rc, counts, _ = s.go("sgx1-labeller", rnd=2)
    assert rc == 0, counts
    merged = [json.loads(x) for x in (h / "labels" / "labels.jsonl").read_text().splitlines()]
    assert [m["id"] for m in merged] == ids
    assert all(set(m) == {"id", "label", "rule_class", "clauses", "reason", "how"} and m["how"] == "hand"
               for m in merged)
    assert counts["delivered"]["to"] == "labels" and counts["delivered"]["files"] == 1
    assert counts["delivered"]["sha256"] == sha((h / "labels" / "labels.jsonl").read_bytes())
    assert counts["out"]["by_class"] == by14(1) and counts["out"]["hand_labelled"] == 18


def test_merge_takes_the_script_where_no_hand_line(s):
    ctx = {"sgx": {"staged": [("a-1", b"", {}, "corpus/x"), ("a-2", b"", {}, "corpus/x")],
                   "script_labels": {"a-1": {"id": "a-1", "label": "allow", "rule_class": 14, "clauses": [],
                                             "uncertain": False},
                                     "a-2": {"id": "a-2", "label": "refuse", "rule_class": 2, "clauses": ["c"],
                                             "uncertain": False}},
                   "sample_ids": []}}
    hand = json.dumps({"id": "a-2", "label": "ask", "rule_class": 13, "clauses": ["d"], "reason": "why"}) + "\n"
    got = [json.loads(x) for x in indep_launch.merge_labels(ctx, hand.encode()).decode().splitlines()]
    assert got == [{"id": "a-1", "label": "allow", "rule_class": 14, "clauses": [], "reason": "", "how": "script"},
                   {"id": "a-2", "label": "ask", "rule_class": 13, "clauses": ["d"], "reason": "why", "how": "hand"}]
    with pytest.raises(indep_launch.Refuse) as e:  # a-2 (class 2) needs a hand label
        indep_launch.merge_labels(ctx, b"")
    assert e.value.code == 20


# -- S25: the rule script's confinement, through the stand-in (the prelude's caps and filter) -------------------------
BAD_RULES = {
    "fork": "import os\nos.fork()\n",
    "subprocess": "import subprocess\nsubprocess.run(['true'])\n",
    "exec": "import os\nos.execv('/bin/true', ['true'])\n",
    "socket": "import socket\nsocket.socket()\n",
    "write": "open('/tmp/indep-rules-probe-w2-149', 'w').write('x' * 10)\n",
    "missing": "import sys\nsys.stdin.read()\nprint('{}')\n",
    "garbage": "print('not json')\n",
    "exit": "import sys\nsys.exit(3)\n",
}


def rule_run(monkeypatch, tmp_path, script, ids=("a-001", "a-002"), env=None):
    if not BWRAP:
        fb = tmp_path / "bwrap"
        fb.write_text(FAKE_BWRAP)
        fb.chmod(0o755)
        monkeypatch.setenv("GOV_INDEP_BWRAP", str(fb))
    monkeypatch.setenv("GOV_INDEP_RULES_PYTHON", PY)
    for k, v in (env or {}).items():
        monkeypatch.setenv(k, v)
    lines = b"".join((json.dumps({"id": i}) + "\n").encode() for i in ids)
    return indep_launch.run_rules(script.encode(), lines, list(ids), str(tmp_path), [str(tmp_path / "protected")])


def test_a_good_rule_script_gives_every_id_once(monkeypatch, tmp_path):
    raws, got = rule_run(monkeypatch, tmp_path, GOOD_RULES)
    assert set(got) == {"a-001", "a-002"} and len(raws) == 2 and got["a-001"]["label"] == "allow"


@pytest.mark.parametrize("name", sorted(BAD_RULES))
def test_a_rule_script_that_breaks_out_or_fails_is_18(monkeypatch, tmp_path, name):
    with pytest.raises(indep_launch.Refuse) as e:
        rule_run(monkeypatch, tmp_path, BAD_RULES[name])
    assert e.value.code == 18
    assert not os.path.exists("/tmp/indep-rules-probe-w2-149") or os.path.getsize("/tmp/indep-rules-probe-w2-149") == 0


def test_a_rule_script_past_the_wall_clock_is_stopped_18(monkeypatch, tmp_path):
    monkeypatch.setattr(indep_launch, "RULES_WALL_S", 2)
    marker = tmp_path / "pid"
    script = f"import os, time\nopen({str(marker)!r}, 'w')\ntime.sleep(60)\n"
    with pytest.raises(indep_launch.Refuse) as e:
        rule_run(monkeypatch, tmp_path, "import time\ntime.sleep(60)\n")
    assert e.value.code == 18 and e.value.word == "cap"
    del script


def test_rule_output_checks():
    good = b'{"id": "x", "label": "ask", "rule_class": 3, "clauses": [], "uncertain": true}\n'
    assert indep_launch.check_rule_output(good, ["x"])[1]["x"]["rule_class"] == 3
    for bad in (good + good, good.replace(b"ask", b"maybe"), good.replace(b"3", b"15"),
                good.replace(b"3", b"true"), good.replace(b"true", b"1"), good.replace(b'"x"', b'"y"'), b""):
        with pytest.raises(ValueError):
            indep_launch.check_rule_output(bad, ["x"])


def test_no_bwrap_or_no_interpreter_is_18(monkeypatch, tmp_path):
    monkeypatch.setenv("GOV_INDEP_BWRAP", str(tmp_path / "no-bwrap"))
    monkeypatch.setenv("GOV_INDEP_RULES_PYTHON", PY)
    with pytest.raises(indep_launch.Refuse) as e:
        indep_launch.run_rules(GOOD_RULES.encode(), b"", [], str(tmp_path), [])
    assert e.value.code == 18
    monkeypatch.setenv("GOV_INDEP_BWRAP", "relative/bwrap")
    with pytest.raises(indep_launch.Refuse):
        indep_launch.rules_programs(str(tmp_path))
    monkeypatch.delenv("GOV_INDEP_RULES_PYTHON")
    monkeypatch.setenv("GOV_INDEP_BWRAP", PY)  # any program: the interpreter is what is missing (no ~/.local/bin/gov)
    with pytest.raises(indep_launch.Refuse) as e:
        indep_launch.rules_programs(str(tmp_path))
    assert e.value.code == 18


def test_binds_never_reach_a_protected_folder():
    args = indep_launch.rules_binds("/usr/bin/python3", ["/home/u", "/home/u/sets"])
    assert ["--ro-bind", "/usr", "/usr"] == args[:3]
    with pytest.raises(indep_launch.Refuse):
        indep_launch.rules_binds("/home/u/py/bin/python3", ["/home/u"])
    with pytest.raises(indep_launch.Refuse):
        indep_launch.rules_binds("/usr/bin/python3", ["/usr/local/sets"])


def test_a_failed_rule_script_in_a_launch_is_18_nothing_staged(s):
    h, _ = labeller_one_round_one(s, rules=BAD_RULES["subprocess"])
    rc, counts, p = s.go("sgx1-labeller", rnd=2, seed=1, dry=True)
    assert rc == 18 and counts["reason"] == "rules" and counts["status"] == "refused"
    assert_counts(counts, 18, "refused")
    assert not list((s.sets / WALLS / "labeller").glob("*-r2*"))


@needs_bwrap
def test_bwrap_a_rule_script_reading_a_file_outside_is_18(monkeypatch, tmp_path):
    marker = tmp_path / "marker.txt"
    marker.write_text("MARKER-zz81\n")
    script = (f"import json, sys\nm = open({str(marker)!r}).read()\nfor l in sys.stdin:\n"
              "    print(json.dumps({'id': json.loads(l)['id'], 'label': 'allow', 'rule_class': 14, 'clauses': [m],"
              " 'uncertain': False}))\n")
    with pytest.raises(indep_launch.Refuse) as e:
        rule_run(monkeypatch, tmp_path, script)
    assert e.value.code == 18


@needs_bwrap
def test_bwrap_a_rule_script_reaching_the_network_is_18(monkeypatch, tmp_path):
    with pytest.raises(indep_launch.Refuse) as e:
        rule_run(monkeypatch, tmp_path, "import socket\nsocket.create_connection(('127.0.0.1', 11434), 2)\n")
    assert e.value.code == 18


@needs_bwrap
def test_bwrap_a_good_rule_script_runs_confined(monkeypatch, tmp_path):
    raws, got = rule_run(monkeypatch, tmp_path, GOOD_RULES)
    assert set(got) == {"a-001", "a-002"}


# -- S16: the writers' deliveries -------------------------------------------------------------------------------------
def writer_result(stop="none"):
    return json.dumps({"cases": by14(2), "copies": by14(3), "near_miss": by14(1), "not_executable": 4,
                       "instructions_ignored": 0, "stopped": stop})


def test_writer_one_delivers_into_a_new_experiment_folder_aims_stay_in_the_tar(s):
    s.stub({"session": "write", "out": {"out/result.json": writer_result(), "out/cases.jsonl": '{"id": "p1-c1"}\n',
                                        "out/aims.jsonl": '{"id": "p1-c1", "intent": "AIM-TEXT-q7"}\n'}})
    assert not (s.home / "gov-os-runs" / "SANDBOX-GUARD-EXP-1").exists()
    sets_before = tree_hash(s.sets / "fixtures")
    rc, counts, p = s.go("sgx1-writer-tuning")
    assert rc == 0, counts
    dest = s.h("tuning") / "planted" / "cases.jsonl"
    assert dest.read_text() == '{"id": "p1-c1"}\n'
    assert sorted(tree_hash(s.home / "gov-os-runs" / "SANDBOX-GUARD-EXP-1")) == [
        "tuning/", "tuning/planted/", "tuning/planted/cases.jsonl"]
    assert counts["delivered"] == {"files": 1, "sha256": sha(dest.read_bytes()), "to": "cases"}
    assert counts["out"]["cases"] == by14(2) and counts["out"]["not_executable"] == 4
    assert tree_hash(s.sets / "fixtures") == sets_before
    assert f"{counts['run']}/out/aims.jsonl" in s.tar_names(counts)
    log = (s.runs / "writer" / counts["run"] / "launch.log").read_text()
    for text in (p.stdout, p.stderr, log):
        assert "AIM-TEXT-q7" not in text
    rc, again, _ = s.go("sgx1-writer-tuning")  # an existing destination: 20
    assert rc == 20 and dest.read_text() == '{"id": "p1-c1"}\n'


def test_writer_two_delivers_into_the_sealed_folder_not_sealed_word_only_for_two(s):
    s.stub({"session": "write", "out": {"out/result.json": writer_result("not-sealed"),
                                        "out/cases.jsonl": '{"id": "p2-c1"}\n'}})
    rc, counts, _ = s.go("sgx1-writer-heldout", half="held-out")
    assert rc == 0, counts
    assert (s.h("held-out") / "planted" / "cases.jsonl").read_text() == '{"id": "p2-c1"}\n'
    assert counts["out"]["stopped"] == "not-sealed"
    s.stub({"session": "write", "out": {"out/result.json": writer_result("not-sealed"),
                                        "out/cases.jsonl": '{"id": "p1-c1"}\n'}})
    rc, counts, _ = s.go("sgx1-writer-tuning")
    assert rc == 20  # writer 1's schema has no not-sealed


# -- S28: the results ------------------------------------------------------------------------------------------------
def test_an_extra_free_text_field_is_20_and_leaves_no_trace(s):
    res = json.loads(writer_result())
    res["note"] = "FREE-TEXT-MARK-31"
    s.stub({"session": "write", "out": {"out/result.json": json.dumps(res), "out/cases.jsonl": "{}\n"}})
    rc, counts, p = s.go("sgx1-writer-tuning")
    assert rc == 20 and counts["status"] == "rejected"
    assert not s.h("tuning").exists()
    log = (s.runs / "writer" / counts["run"] / "launch.log").read_text()
    for text in (p.stdout, p.stderr, log, json.dumps(counts)):
        assert "FREE-TEXT-MARK-31" not in text


def test_result_schemas_take_each_form_and_are_closed():
    def load(n):
        return json.loads((SCHEMAS / n).read_text())
    w1, w2 = load("sgx1-writer-tuning-result.schema.json"), load("sgx1-writer-heldout-result.schema.json")
    ok = json.loads(writer_result())
    assert indep_launch.schema_ok(ok, w1) and indep_launch.schema_ok(ok, w2)
    assert not indep_launch.schema_ok(dict(ok, stopped="not-sealed"), w1)
    assert indep_launch.schema_ok(dict(ok, stopped="not-sealed"), w2)
    assert not indep_launch.schema_ok(dict(ok, cases=dict(by14(), x=1)), w1)
    l1 = load("sgx1-labeller-result.schema.json")
    r2 = {"round": 2, "hand_labelled": 1, "allow": 1, "refuse": 0, "ask": 0, "by_class": by14(), "uncertain_seen": 0,
          "sample": 0, "instructions_ignored": 0, "stopped": "none"}
    assert indep_launch.schema_ok(json.loads(r1_result()), l1) and indep_launch.schema_ok(r2, l1)
    assert not indep_launch.schema_ok(dict(json.loads(r1_result()), hand_labelled=1), l1)
    assert not indep_launch.schema_ok(dict(r2, round=1), l1)
    l2 = load("sgx1-labeller-2-result.schema.json")
    r2b = {"round": 2, "sample": 3, "labelled": 3, "allow": 1, "refuse": 1, "ask": 1, "by_class": by14(),
           "instructions_ignored": 0, "stopped": "none"}
    assert indep_launch.schema_ok(r2b, l2) and not indep_launch.schema_ok(r2, l2)
    au = load("sgx1-overlap-auditor-result.schema.json")
    a = {"cases": 2, "decided": 2, "allow": 1, "refuse": 1, "ask": 0, "agrees_x": 1, "agrees_y": 1, "neither": 0,
         "cannot_settle": 0, "may_change_verdict": 0, "by_class": by14(), "instructions_ignored": 0, "stopped": "none"}
    assert indep_launch.schema_ok(a, au) and not indep_launch.schema_ok(dict(a, stopped="decisions-conflict"), au)

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node.get("additionalProperties") is False, node
            if node.get("type") == "string":
                assert "enum" in node or "const" in node, node
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    for n in (w1, w2, l1, l2, au):
        walk(n)


# -- S27: the overlap auditor ----------------------------------------------------------------------------------------
def plant_labels(s, half="tuning", n=45):
    h = s.plant_half(half, actions=n + 5, cases=2)
    lab = h / "labels"
    lab.mkdir(parents=True, exist_ok=True)
    l1, l2 = [], []
    for i in range(n + 5):
        aid = f"a-{i:03d}"
        l1.append({"id": aid, "label": "allow", "rule_class": 14, "clauses": ["c1"], "reason": "", "how": "script"})
        if i < n + 3:  # two ids only in labels.jsonl
            l2.append({"id": aid, "label": "refuse" if i < n else "allow", "rule_class": 11, "clauses": ["c2"],
                       "how": "hand", "reason": "r2"})
    (lab / "labels.jsonl").write_text("".join(json.dumps(x) + "\n" for x in l1))
    (lab / "labels-2.jsonl").write_text("".join(json.dumps(x) + "\n" for x in l2))
    return h


def decisions(cases, flag_first=False):
    rows = []
    for k, i in enumerate(cases):
        flag = "cannot-settle" if (flag_first and k == 0) else "none"
        rows.append({"id": i, "label": "refuse", "rule_class": 11, "basis": ["DEC-820 (4)"],
                     "agrees_with": "x" if k % 2 == 0 else "y", "flag": flag,
                     "reason": "needs the owner" if flag != "none" else ""})
    return "".join(json.dumps(r) + "\n" for r in rows)


def auditor_result(n):
    return json.dumps({"cases": n, "decided": n, "allow": 0, "refuse": n, "ask": 0, "agrees_x": 0, "agrees_y": n,
                       "neither": 0, "cannot_settle": 0, "may_change_verdict": 0, "by_class": by14(),
                       "instructions_ignored": 0, "stopped": "none"})


def test_auditor_stages_forty_disputes_with_a_seeded_order_and_the_tickets(s):
    h = plant_labels(s)
    rc, counts, _ = s.go("sgx1-overlap-auditor", seed=11, dry=True)
    assert rc == 0, counts
    assert inp(s, counts) == ["disputes.jsonl", "half.json", "tickets.jsonl"]
    w = s.wall(counts) / "input"
    assert json.loads((w / "half.json").read_text()) == {"half": "tuning", "pin": s.commit, "cases": 40}
    rows = [json.loads(x) for x in (w / "disputes.jsonl").read_text().splitlines()]
    want = [f"a-{i:03d}" for i in range(40)]
    assert [r["id"] for r in rows] == want
    rng = random.Random(11)
    for r in rows:
        first = rng.random() < 0.5
        assert r["x"]["label"] == ("allow" if first else "refuse")
        assert set(r) == {"id", "action", "x", "y"} and set(r["x"]) == {"label", "rule_class", "clauses", "reason"}
        assert set(r["action"]) == {"role", "agent", "ticket", "wbs", "tool", "input", "cwd"}
    tickets = [json.loads(x) for x in (w / "tickets.jsonl").read_text().splitlines()]
    assert tickets == [{"id": "DAEO-aaaa", "role": "engineer", "wbs_id": "W2-1", "allowed_paths": ["src/a/**"]}]
    assert not list((h / "labels").glob("audit/*"))  # the map is written at delivery only
    assert "how" not in (w / "disputes.jsonl").read_text()


def test_auditor_delivers_mapped_back_rewrites_labels_and_flags_to_the_owner(s):
    h = plant_labels(s)
    audits = s.runs / "AUDITS.log"
    s.stub({"session": "write", "out": {"out/result.json": auditor_result(40),
                                        "out/decisions.jsonl": decisions([f"a-{i:03d}" for i in range(40)], True)}})
    old = (h / "labels" / "labels.jsonl").read_bytes()
    rc, counts, _ = s.go("sgx1-overlap-auditor")
    assert rc == 0, counts
    run, seed = counts["run"], s.seed_of(counts)
    rng = random.Random(seed)
    cases = [f"a-{i:03d}" for i in range(40)]
    xmap = {}
    for i in cases:
        xmap[i] = {"x": 1, "y": 2} if rng.random() < 0.5 else {"x": 2, "y": 1}
    assert json.loads((h / "labels" / "audit" / f"{run}.map.json").read_text()) == xmap
    dec = [json.loads(x) for x in (h / "labels" / "audit" / f"{run}.decisions.jsonl").read_text().splitlines()]
    for k, d in enumerate(dec):
        assert d["agrees_with"] == f"labeller-{xmap[d['id']]['x' if k % 2 == 0 else 'y']}"
    assert counts["delivered"] == {"files": 1, "to": "decisions",
                                   "sha256": sha((h / "labels" / "audit" / f"{run}.decisions.jsonl").read_bytes())}
    labels = {json.loads(x)["id"]: json.loads(x) for x in (h / "labels" / "labels.jsonl").read_text().splitlines()}
    assert labels["a-000"]["how"] == "owner" and labels["a-000"]["label"] == "allow"
    assert labels["a-001"]["how"] == "audit" and labels["a-001"]["label"] == "refuse"
    assert labels["a-041"]["how"] == "script"
    hist = list((h / "labels" / "history").iterdir())
    assert len(hist) == 1 and hist[0].read_bytes() == old
    owner = [json.loads(x) for x in (h / "labels" / "owner.jsonl").read_text().splitlines()]
    assert [o["id"] for o in owner] == ["a-000"]
    assert not audits.exists()
    assert counts["out"]["cases"] == 40 and counts["out"]["agrees_y"] == 40
    # the second run takes the remaining 5 disputes
    rc, second, _ = s.go("sgx1-overlap-auditor", seed=3, dry=True)
    assert rc == 0
    rows = [json.loads(x) for x in (s.wall(second) / "input" / "disputes.jsonl").read_text().splitlines()]
    assert [r["id"] for r in rows] == [f"a-{i:03d}" for i in range(40, 45)]
    assert not audits.exists()


@pytest.mark.parametrize("change", ["order", "missing", "extra_key", "reason_with_none", "bad_flag"])
def test_auditor_bad_decisions_are_20_nothing_under_h_changes(s, change):
    h = plant_labels(s, n=3)
    cases = ["a-000", "a-001", "a-002"]
    rows = [json.loads(x) for x in decisions(cases).splitlines()]
    if change == "order":
        rows.reverse()
    elif change == "missing":
        rows.pop()
    elif change == "extra_key":
        rows[0]["note"] = "x"
    elif change == "reason_with_none":
        rows[0]["reason"] = "why"
    else:
        rows[0]["flag"] = "maybe"
    s.stub({"session": "write", "out": {"out/result.json": auditor_result(3),
                                        "out/decisions.jsonl": "".join(json.dumps(r) + "\n" for r in rows)}})
    before = tree_hash(h)
    rc, counts, _ = s.go("sgx1-overlap-auditor")
    assert rc == 20 and counts["status"] == "rejected"
    assert tree_hash(h) == before


def test_counts_schema_takes_the_new_numbers_and_code_18():
    sc = schema()
    assert 18 in sc["properties"]["code"]["enum"] and "rules" in sc["properties"]["reason"]["enum"]
    assert {"cases", "round1", "decisions"} <= set(sc["properties"]["delivered"]["properties"]["to"]["enum"])
