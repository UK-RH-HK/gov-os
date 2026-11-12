"""Planted stand-ins for W2-171's unit tests: a fake ``gov`` (in a ``pin-<12 hex>`` folder) that answers ``retrieve`` with
planted ranks, a fake ``claude``, the visible-40 control set, and the planted measured state of an audit. Everything lives
under pytest's ``tmp_path``: never a real search, a real model call, the sets root ``~/gov-os-eval`` or a GPU."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml

from gov.memaudit import declare

from .conftest import AUDIT, question

FAKE_GOV = '''#!%(python)s
import json, os, sys
here = os.path.dirname(os.path.realpath(__file__))
args = sys.argv[1:]
if args[:1] == ["--version"]:
    print("gov fake 0")
    sys.exit(0)
if args[:1] != ["retrieve"]:
    sys.exit(2)
plan = json.load(open(os.path.join(here, "plan.json")))
question = args[-2] if args[-1] == "--json" else args[-1]
log = os.path.join(here, "calls.jsonl")
nth = 1
if os.path.exists(log):
    nth += sum(1 for line in open(log) if json.loads(line)["q"] == question)
with open(log, "a") as f:
    f.write(json.dumps({"q": question, "nth": nth, "role": os.environ.get("GOV_ROLE"),
                        "store": os.environ.get("GOV_STORE"), "ticket": os.environ.get("GOV_TICKET"),
                        "cwd": os.getcwd(), "argv": args}) + "\\n")
spec = dict(plan["questions"].get(question, plan["default"]))
spec.update(plan.get("overrides", {}).get(question + "|" + str(nth), {}))
if spec.get("mutate_store"):
    with open(spec["mutate_store"], "ab") as f:
        f.write(b"x")
if spec.get("exit"):
    sys.stderr.write("fake gov failure\\n")
    sys.exit(spec["exit"])
evidence = [{"path": p, "start_line": a, "end_line": b, "text": t, "routes": r} for p, a, b, t, r in spec["evidence"]]
result = {"stopping_reason": "SATURATED", "evidence": evidence,
          "facets": {"lexical": {"available": spec.get("lexical", True), "reason": None},
                     "semantic": {"available": spec.get("semantic", True), "reason": None}},
          "rerank": {"by": spec.get("rerank_by", "service")}, "gaps": [], "continuation": None}
if spec.get("pool_fallback"):
    result["pool"] = {"fallback": True}
print(json.dumps({"ok": True, "result": result}))
'''

FILLER = [("docs/filler/f%d.md" % i, 1, 2, "filler text %d" % i, ["lexical"]) for i in range(1, 30)]


def evidence_at(q: dict, rank: int | None, routes=("lexical", "semantic")) -> list:
    """Evidence items with the question's first gold place at ``rank`` (None: no gold place, 6 fillers)."""
    if rank is None:
        return [list(x) for x in FILLER[:6]]
    first = q["sources"][0]
    src = first[0] if isinstance(first, list) else first
    gold = [src["path"], src["lines"][0], src["lines"][1], "the gold text", list(routes)]
    return [list(x) for x in FILLER[:rank - 1]] + [gold]


class FakeGov:
    """The fake ``gov`` of a plant, in ``<tmp>/share/pin-0123456789ab/bin`` (the folder W2-170's ``Plant`` made)."""

    def __init__(self, plant):
        self.plant = plant
        self.bin = Path(os.path.realpath(plant.gov)).parent
        self.plan = {"default": {"evidence": [list(x) for x in FILLER[:3]]}, "questions": {}, "overrides": {}}
        exe = self.bin / "gov"
        exe.write_text(FAKE_GOV % {"python": sys.executable}, encoding="utf-8")
        os.chmod(exe, 0o755)
        self.save()

    def save(self) -> None:
        (self.bin / "plan.json").write_text(json.dumps(self.plan), encoding="utf-8")

    def rank(self, q: dict, rank: int | None, **spec) -> None:
        self.plan["questions"][q["question"]] = {"evidence": evidence_at(q, rank), **spec}

    def override(self, text: str, nth: int, **spec) -> None:
        self.plan["overrides"][f"{text}|{nth}"] = spec

    def calls(self) -> list[dict]:
        log = self.bin / "calls.jsonl"
        return [json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []


def control_questions(head: str) -> list[dict]:
    """The standing visible 40: ``v01`` to ``v40``, shaped as the audit's questions, each its own words."""
    out = []
    for i in range(1, 41):
        q = question(i, head)
        if q["category"] == "nonexistent-id":
            q["category"] = "decision"
        q.update(id=f"v{i:02d}", question=f"Control question number {i} about the planted file?")
        out.append(q)
    return out


def plant_control(plant, fake: FakeGov, hits: int = 34) -> list[dict]:
    """``memory-retrieval``'s visible 40 on the plant's sets root (its map entry too); ``hits`` of them at rank 1."""
    folder = plant.root / "fixtures/evaluation/memory-retrieval/visible"
    folder.mkdir(parents=True, exist_ok=True)
    (plant.root / "fixtures/evaluation/memory-retrieval/hidden").mkdir(parents=True, exist_ok=True)
    qs = control_questions(plant.repo["head"])
    for i, q in enumerate(qs, 1):
        (folder / f"{q['id']}.yaml").write_text(yaml.safe_dump(q, sort_keys=False), encoding="utf-8")
        fake.rank(q, 1 if i <= hits else None)
    p = {"map": plant.root / "governance/project/path-map.yaml"}
    code, text = declare.plan_map(p, "memory-retrieval")
    assert code is None and text is not None
    declare.write_map(p, text)
    fake.save()
    return qs


def set_control_hits(plant, fake: FakeGov, hits: int) -> None:
    for i, q in enumerate(control_questions(plant.repo["head"]), 1):
        fake.rank(q, 1 if i <= hits else None)
    fake.save()


def audit_ranks(plant) -> dict[str, int | None]:
    """The planted first gold rank of each audit question (cyclic, so every bucket of the figures is met)."""
    cycle = [1, 2, 3, 4, 5, 6, 8, 12, 20, 25, None]
    return {f"q{i:02d}": cycle[(i - 1) % len(cycle)] for i in range(1, 41)}


def plant_audit(plant, fake: FakeGov, ranks=None) -> dict:
    ranks = ranks or audit_ranks(plant)
    for qid, rank in ranks.items():
        fake.rank(plant.questions[qid], rank)
    fake.save()
    return ranks


def prepare(plant, control_hits: int = 34, ranks=None) -> tuple[FakeGov, dict]:
    """Pre-flight and void run clean, the fake ``gov`` and the control set planted: ``measure`` can run."""
    assert plant.cli(*plant.preflight_args()).returncode == 0
    plant.notes({})
    assert plant.cli(*plant.void_args()).returncode == 0
    fake = FakeGov(plant)
    plant_control(plant, fake, control_hits)
    return fake, plant_audit(plant, fake, ranks)


def measure_args(plant, *extra) -> list[str]:
    return ["measure", "--sets-root", str(plant.root), "--audit", AUDIT, "--repo", str(plant.repo["path"]),
            "--commit", plant.repo["head"], "--store", str(plant.store), "--gov", str(plant.gov), *extra]


# ---- the fake claude: one JSON on standard output, driven by a plan file next to it

FAKE_CLAUDE = '''#!%(python)s
import json, os, sys
here = os.path.dirname(os.path.realpath(__file__))
plan = json.load(open(os.path.join(here, "claude-plan.json")))
args = sys.argv[1:]
model = args[args.index("--model") + 1]
system = args[args.index("--system-prompt") + 1]
prompt = sys.stdin.read()
with open(os.path.join(here, "claude-calls.jsonl"), "a") as f:
    f.write(json.dumps({"model": model, "grader": system.startswith("You grade"), "argv": args[:3]}) + "\\n")
cost = plan.get("cost", 0.01)
if system.startswith("You grade"):
    said = prompt.split("Answer to grade: ", 1)[1]
    grade = "correct"
    for mark, g in plan["grades"].items():
        if mark in said:
            grade = g
    if "disagree" in plan and plan["disagree"] in said and model == "claude-sonnet-5-5":
        grade = "wrong"
    out = {"grade": grade, "reason": "r"}
else:
    question = prompt.split("\\n", 1)[0][len("Question: "):]
    bundles = prompt.count("=== Bundle ")
    spec = plan["readers"].get(question, plan["default"])
    step = spec["steps"][min(bundles, len(spec["steps"])) - 1]
    if step == "none":
        print("")
        sys.exit(0)
    out = step
print(json.dumps({"structured_output": out, "usage": {"input_tokens": 1, "output_tokens": 1},
                  "total_cost_usd": cost, "is_error": False}))
'''
