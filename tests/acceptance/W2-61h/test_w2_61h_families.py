"""W2-61h, KPI S7 and failure line 4 -- source families in the measure (DAEO-h2k3; DEC-1078 (4), DEC-1079,
DEC-1068 (4)).

S7, as the ticket states it: the measure counts a gold source and its official copies as one **family**. The
families are declared in the path map (``evaluation_families:``, each a list of member path globs). An evidence item
in another member of the gold source's family counts as a hit on that source when **its text holds the gold span's
text** (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the
measure's per-question line; with no family declared, every score is as today; a run's kept outputs are re-scored
with families without running again. Failure line 4: a family hit counted on a member whose text does not hold the
gold span's text.

Everything here is planted in ``tmp_path``: a measured root (which is also the sets root) with its own path map, its
own set ``planted`` and its own questions, and a stand-in ``gov`` that returns chosen evidence (no store, no model,
no network; never this repository's sets, never ``~/gov-os-eval``). The measure is run as a command, from this
tree's ``src``.

Interface choices these tests make (S7 names the key and the behaviour, not these details):

- ``evaluation_families:`` is a top-level key of the path map, **a map of family name to a list of member globs**
  in the path map's glob language (``*`` stays in one folder);
- the kept outputs are read with ``python3 -m gov.retrieval.measure <set> ... --kept <dir>``, ``<dir>`` in the form
  ``~/gov-os-eval/runs/<point>/<name>-run<k>/`` takes (``drafts/d4b/measure_verdict.sh``): each ``gov retrieve``
  call's ``--json`` output as ``00001.json``, ``00002.json``, ... in call order, beside ``.n`` and ``.n.lock``; the
  output is the measure's own (text, or the record with ``--json``);
- a family hit is named by the member's path and the word "family" in the question's line.

Red on today's integrated code: every case but the one for "with no family declared, every score is as today",
which passes today by design (it guards today's figures). Each negative case carries a positive control in the same
run, so it is red until families work, then judges the negative.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SET = "planted"
TIMEOUT_S = 60.0

CONTRACT_MD = "docs/contract/CONTRACT.md"
CONTRACT_YAML = "docs/contract/contract.yaml"
CAP7 = "docs/contract/capabilities/CAP-7.md"
CAP7_READS = "docs/contract/capabilities/CAP-7-reads.md"
CAP7_HALF = "docs/contract/capabilities/CAP-7-half.md"
CAP7_BELOW = "docs/contract/capabilities/old/CAP-7.md"
CAP8 = "docs/contract/capabilities/CAP-8.md"
CAP9 = "docs/contract/capabilities/CAP-9.md"
COPY = "docs/notes/copy.md"
OTHER = "docs/notes/other.md"
ROLE = "template/governance/kernel/roles/engineer.md"
MOD = "src/pkg/mod.py"

FILES = {
    CONTRACT_MD: """\
        # The Contract

        ## CAP-7 Writes

        The guard refuses every write
            outside the **allowed paths** of the ticket.

        ## CAP-8 Reads

        Reads are open, save secrets and
        the held-out material.

        ## CAP-9 Retries

        A failed check is retried once, never twice.
        """,
    CONTRACT_YAML: """\
        capabilities:
          - id: CAP-7
            statement: "The guard refuses every write outside the allowed paths of the ticket."
          - id: CAP-8
            statement: >-
              Reads are open, save secrets and
              the held-out material.
          - id: CAP-9
            statement: "A failed check is retried once, never twice."
        """,
    # the same Markdown as CONTRACT.md's lines 5-6, wrapped and spaced otherwise
    CAP7: """\
        # CAP-7 Writes

        The guard refuses  every write outside the **allowed paths**\tof the ticket.
        """,
    # a member, but one word changed (write -> read)
    CAP7_READS: """\
        # CAP-7 Reads

        The guard refuses every read outside the **allowed paths** of the ticket.
        """,
    # a member holding only the first half of the gold span
    CAP7_HALF: """\
        # CAP-7 Writes, in part

        The guard refuses every write
        and records the refusal.
        """,
    # below the member glob's folder: ``*`` stays in one folder, so not a member
    CAP7_BELOW: """\
        # CAP-7 Writes

        The guard refuses every write
            outside the **allowed paths** of the ticket.
        """,
    CAP8: """\
        # CAP-8 Reads

        Reads are open, save **secrets** and the held-out material.
        """,
    CAP9: """\
        # CAP-9 Retries

        A failed check is
        retried once, never twice.
        """,
    # outside every family, holding CONTRACT.md's lines 5-6 byte for byte
    COPY: """\
        # A note

        The guard refuses every write
            outside the **allowed paths** of the ticket.
        """,
    OTHER: """\
        # Unrelated

        Nothing here bears on any question.
        """,
    # a member of another family (the kernel's), holding the same text
    ROLE: """\
        # Engineer

        The guard refuses every write
            outside the **allowed paths** of the ticket.
        """,
    MOD: """\
        def write(path):
            return refuse(path)


        LIMIT = 3
        """,
}

# Gold sources (each cited as the measure's question form takes it).
G7 = {"path": CONTRACT_MD, "lines": [5, 6]}                 # Markdown prose, wrapped and indented
G8_YAML = {"path": CONTRACT_YAML, "lines": [6, 7]}          # a YAML block value's lines
G9_HEADING = {"path": CONTRACT_MD, "heading": "## CAP-9 Retries"}  # a heading's section, lines 13-15
MOD_WRITE = {"path": MOD, "lines": [1, 2]}
MOD_LIMIT = {"path": MOD, "lines": [5, 5]}

FAMILIES = {
    "contract": [CONTRACT_MD, CONTRACT_YAML, "docs/contract/capabilities/*.md"],
    "kernel": ["template/governance/kernel/roles/*.md", ".claude/agents/*.md"],
}

# The CTO's scorer reads the per-question line with this (drafts/d4b/score.py): a family hit's naming must keep it.
SCORE_LINE = re.compile(r"\S+ \((visible|hidden)\): hit@5 (yes|no)(?: \(first gold rank (\d+)\))?.*full evidence "
                        r"(yes|no)")

STAND_IN = """\
#!{python}
# A stand-in gov: answers `retrieve` from responses.json beside it; keeps each answer as the measure's kept outputs
# are kept (drafts/d4b/measure_verdict.sh); in trip mode records every call and answers none.
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
conf = json.loads((HERE / "responses.json").read_text())
argv = sys.argv[1:]
with open(HERE / "calls.log", "a") as log:
    log.write(json.dumps(argv) + "\\n")
if argv[:1] == ["--version"]:
    print("stand-in 0")
    sys.exit(0)
if argv[:1] != ["retrieve"] or conf.get("trip"):
    sys.exit(3)
token = argv[argv.index("--continue") + 1] if "--continue" in argv else ""
question = argv[argv.index("--json") - 1]
page = conf["answers"][question][token]
out = json.dumps({{"ok": True, "result": {{"evidence": page["evidence"], "continuation": page.get("next")}}}})
if conf.get("keep"):
    keep = Path(conf["keep"])
    n = int((keep / ".n").read_text() or 0) + 1
    (keep / ".n").write_text(str(n))
    (keep / f"{{n:05d}}.json").write_text(out + "\\n")
print(out)
"""


class World:
    """A planted measured root with its path map, the set ``planted`` and a stand-in ``gov``."""

    def __init__(self, base: Path, families: dict | None):
        self.root = base / "root"
        self.bin = base / "bin"
        self.bin.mkdir(parents=True)
        for rel, text in FILES.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(text), encoding="utf-8")
        self.set_families(families)
        self.visible = self.root / "fixtures/evaluation" / SET / "visible"
        self.visible.mkdir(parents=True)
        self.answers: dict = {}
        self.gov = self.bin / "gov"
        self.gov.write_text(STAND_IN.format(python=sys.executable), encoding="utf-8")
        self.gov.chmod(0o755)
        self.respond()

    def set_families(self, families: dict | None) -> None:
        doc = {"evaluation_sets": {SET: {"visible": ["docs/sets/planted.md"],
                                         "hidden": [f"fixtures/evaluation/{SET}/hidden/**"],
                                         "measures": {"roles": ["engineer"]}}}}
        if families is not None:
            doc["evaluation_families"] = families
        path = self.root / "governance/project/path-map.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")

    def item(self, rel: str, first: int, last: int) -> dict:
        """An evidence item whose text is the planted file's own lines ``first`` to ``last``."""
        lines = (self.root / rel).read_text(encoding="utf-8").splitlines()
        return {"path": rel, "start_line": first, "end_line": last, "text": "\n".join(lines[first - 1:last])}

    def question(self, qid: str, sources: list, pages: list[list[dict]]) -> None:
        """A question and the pages the stand-in returns for it (each page after the first by a continuation)."""
        text = f"Planted question {qid}?"
        (self.visible / f"{qid}.yaml").write_text(
            yaml.safe_dump({"question": text, "gold_answer": "planted", "sources": sources}), encoding="utf-8")
        self.answers[text] = {("" if n == 0 else f"c{n}"): {"evidence": page,
                                                              "next": f"c{n + 1}" if n + 1 < len(pages) else None}
                              for n, page in enumerate(pages)}
        self.respond()

    def respond(self, keep: Path | None = None, trip: bool = False) -> None:
        conf = {"answers": self.answers, "keep": str(keep) if keep else None, "trip": trip}
        (self.bin / "responses.json").write_text(json.dumps(conf), encoding="utf-8")

    def calls(self) -> list[list[str]]:
        log = self.bin / "calls.log"
        return [json.loads(line) for line in log.read_text().splitlines()] if log.is_file() else []

    def measure(self, *extra: str) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if k not in ("GOV_TICKET", "PYTHONPATH")}
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        return subprocess.run([sys.executable, "-m", "gov.retrieval.measure", SET, "--root", str(self.root),
                               "--part", "visible", "--gov", str(self.gov), *extra],
                              cwd=self.root, env=env, capture_output=True, text=True, timeout=TIMEOUT_S)

    def run(self, *extra: str) -> tuple[dict, str]:
        """The measure's record (``--json``) and its text, from two runs over the same planted answers."""
        done = self.measure(*extra, "--json")
        assert done.returncode == 0, f"the measure failed (exit {done.returncode}): {done.stderr[-2000:]}"
        doc = json.loads(done.stdout)
        done = self.measure(*extra)
        assert done.returncode == 0, f"the measure failed (exit {done.returncode}): {done.stderr[-2000:]}"
        return doc, done.stdout


def by_id(doc: dict) -> dict:
    return {q["id"]: q for q in doc["questions"]}


def line_of(text: str, qid: str) -> str:
    found = [line for line in text.splitlines() if line.startswith(f"{qid} (visible): ")]
    assert found, f"no per-question line for {qid} in:\n{text}"
    return found[0]


def figures(q: dict) -> tuple:
    return (q["hit_at_5"], q["first_gold_rank"], q["in_bundle"], q["full_evidence"], q["pieces_found"],
            q["pieces_needed"])


def names_family_hit(line: str, member: str) -> bool:
    return "famil" in line.lower() and member in line


@pytest.fixture
def world(tmp_path):
    return World(tmp_path, FAMILIES)


# --------------------------------------------------------------------------------------------------------------------
# A family hit, and its naming
# --------------------------------------------------------------------------------------------------------------------

def test_s7_a_family_member_holding_the_gold_text_is_a_hit_named_in_the_line(world):
    """q01: the gold is CONTRACT.md's prose; the second item is contract.yaml's entry holding that text: a hit at
    rank 2. q02: two entries, the first matched on its own path, the second (a heading's section of CONTRACT.md) only
    by the generated capability page: full evidence, 2 of 2. Each family hit is named in the question's line."""
    w = world
    w.question("q01", [G7], [[w.item(OTHER, 1, 3), w.item(CONTRACT_YAML, 2, 3)]])
    w.question("q02", [MOD_WRITE, G9_HEADING], [[w.item(MOD, 1, 2), w.item(CAP9, 1, 4)]])
    doc, text = w.run()
    q = by_id(doc)
    assert figures(q["q01"]) == (True, 2, True, True, 1, 1)
    assert figures(q["q02"]) == (True, 1, True, True, 2, 2)
    assert (doc["total"]["hit_at_5"]["count"], doc["total"]["full_evidence"]["count"]) == (2, 2)
    assert names_family_hit(line_of(text, "q01"), CONTRACT_YAML), line_of(text, "q01")
    assert names_family_hit(line_of(text, "q02"), CAP9), line_of(text, "q02")
    for qid in ("q01", "q02"):   # the line keeps the form the CTO's scorer reads
        assert SCORE_LINE.match(line_of(text, qid)), line_of(text, qid)


# --------------------------------------------------------------------------------------------------------------------
# Normalisation: whitespace, and Markdown or YAML formatting
# --------------------------------------------------------------------------------------------------------------------

NORMALISED = {
    # the same Markdown, wrapped, indented and spaced otherwise (two spaces, a tab)
    "whitespace": (G7, CAP7, (1, 3)),
    # Markdown prose with **emphasis** against the same sentence as a quoted YAML value under its key
    "markdown-prose-against-yaml-value": (G7, CONTRACT_YAML, (2, 3)),
    # a YAML folded block value's lines against the same sentence as one line of Markdown prose with **emphasis**
    "yaml-value-against-markdown-prose": (G8_YAML, CAP8, (1, 3)),
    # a `##` heading's section against the generated page's `#` heading and the body wrapped otherwise
    "heading-level": (G9_HEADING, CAP9, (1, 4)),
}


@pytest.mark.parametrize("case", list(NORMALISED))
def test_s7_normalised_text_still_matches(world, case):
    gold, member, (first, last) = NORMALISED[case]
    w = world
    w.question("q01", [gold], [[w.item(member, first, last)]])
    doc, text = w.run()
    assert figures(by_id(doc)["q01"]) == (True, 1, True, True, 1, 1), f"{case}: no family hit"
    assert names_family_hit(line_of(text, "q01"), member), line_of(text, "q01")


# --------------------------------------------------------------------------------------------------------------------
# Failure line 4: a member whose text does not hold the gold span's text is no hit
# --------------------------------------------------------------------------------------------------------------------

NOT_HELD = {
    # one word changed: the text is near, not the same
    "a-word-changed": (CAP7_READS, (1, 3)),
    # the member holds only the first half of the gold span
    "half-the-span": (CAP7_HALF, (1, 4)),
    # the member's item covers the same line numbers as the gold span (5-6) but holds other text: path alone
    "same-lines-other-text": (CONTRACT_YAML, (5, 6)),
}


@pytest.mark.parametrize("case", list(NOT_HELD))
def test_s7_f4_a_member_whose_text_does_not_hold_the_gold_is_no_hit(world, case):
    member, (first, last) = NOT_HELD[case]
    w = world
    w.question("q01", [G7], [[w.item(CAP7, 1, 3)]])                      # the control: a family hit
    w.question("q02", [G7], [[w.item(member, first, last)]])
    doc, text = w.run()
    q = by_id(doc)
    assert figures(q["q01"]) == (True, 1, True, True, 1, 1), "the control: families are not counted at all"
    assert figures(q["q02"]) == (False, None, False, False, 0, 1), f"{case}: a family hit counted on a member " \
                                                                   "whose text does not hold the gold span's text"
    assert member not in line_of(text, "q02"), line_of(text, "q02")


# --------------------------------------------------------------------------------------------------------------------
# Never by text outside the family: a file outside the gold source's family is no hit
# --------------------------------------------------------------------------------------------------------------------

OUTSIDE = {
    # in no family, holding CONTRACT.md's lines 5-6 byte for byte
    "in-no-family": (COPY, (3, 4)),
    # a member of another family (the kernel's), holding the same text
    "in-another-family": (ROLE, (3, 4)),
    # one folder below the member glob `docs/contract/capabilities/*.md`: `*` stays in one folder
    "a-folder-below-the-glob": (CAP7_BELOW, (3, 4)),
}


@pytest.mark.parametrize("case", list(OUTSIDE))
def test_s7_a_file_outside_the_family_is_no_hit_by_its_text(world, case):
    path, (first, last) = OUTSIDE[case]
    w = world
    w.question("q01", [G7], [[w.item(CAP7, 1, 3)]])                      # the control: a family hit
    w.question("q02", [G7], [[w.item(path, first, last)]])
    doc, text = w.run()
    q = by_id(doc)
    assert figures(q["q01"]) == (True, 1, True, True, 1, 1), "the control: families are not counted at all"
    assert figures(q["q02"]) == (False, None, False, False, 0, 1), f"{case}: a hit outside the gold's family"
    assert path not in line_of(text, "q02"), line_of(text, "q02")


# --------------------------------------------------------------------------------------------------------------------
# With no family declared, every score is as today
# --------------------------------------------------------------------------------------------------------------------

def test_s7_with_no_family_declared_every_score_is_as_today(tmp_path):
    """The path map declares no family: the items that would be family hits count for nothing, and hit@5, full
    evidence and the first gold rank (MRR's input) are today's, per question and in total. Green today by design."""
    w = World(tmp_path, None)
    w.question("q01", [G7], [[w.item(OTHER, 1, 3), w.item(CONTRACT_YAML, 2, 3)]])
    w.question("q02", [MOD_WRITE, G9_HEADING], [[w.item(MOD, 1, 2), w.item(CAP9, 1, 4)]])
    w.question("q03", [MOD_LIMIT], [[w.item(OTHER, 1, 1), w.item(OTHER, 2, 2), w.item(OTHER, 3, 3),
                                     w.item(CAP7, 1, 1), w.item(CAP8, 1, 1), w.item(MOD, 5, 5)]])
    doc, text = w.run()
    q = by_id(doc)
    assert figures(q["q01"]) == (False, None, False, False, 0, 1)
    assert figures(q["q02"]) == (True, 1, True, False, 1, 2)
    assert figures(q["q03"]) == (False, 6, True, True, 1, 1)
    total = doc["total"]
    assert (total["questions"], total["hit_at_5"]["count"], total["hit_at_5"]["percent"],
            total["full_evidence"]["count"], total["full_evidence"]["percent"]) == (3, 1, 33.3, 1, 33.3)
    expected = {"q01": ("no", None, "no"), "q02": ("yes", "1", "no"), "q03": ("no", "6", "yes")}
    for qid, (hit, rank, full) in expected.items():
        line = line_of(text, qid)
        found = SCORE_LINE.match(line)
        assert found and (found[2], found[3], found[4]) == (hit, rank, full), line
        assert "famil" not in line.lower(), line
    assert "total: hit@5 1 of 3 (33.3 %, floor 85); full evidence 1 of 3 (33.3 %, target 99 %)" in text


# --------------------------------------------------------------------------------------------------------------------
# A run's kept outputs re-scored with families, without running again
# --------------------------------------------------------------------------------------------------------------------

def test_s7_kept_outputs_are_re_scored_with_families_without_running_again(tmp_path):
    """A run made before families existed keeps every call's output (q01 one call, q02 two by a continuation, q03
    one). Families are then declared, the retriever is replaced by one that answers nothing, and the kept outputs are
    re-scored: the family-aware figures, each call assigned to its own question, with no retrieval asked; and they
    equal a fresh run's with families."""
    w = World(tmp_path / "w", None)
    w.question("q01", [MOD_WRITE], [[w.item(MOD, 1, 2)]])
    w.question("q02", [MOD_LIMIT, G7], [[w.item(MOD, 5, 5)], [w.item(OTHER, 1, 3), w.item(CAP7, 1, 3)]])
    w.question("q03", [G9_HEADING], [[w.item(OTHER, 1, 3), w.item(CAP9, 1, 4)]])
    kept = tmp_path / "runs" / "point" / "name-run1"
    kept.mkdir(parents=True)
    (kept / ".n").write_text("")
    (kept / ".n.lock").write_text("")
    w.respond(keep=kept)
    done = w.measure()
    assert done.returncode == 0, f"the measure failed (exit {done.returncode}): {done.stderr[-2000:]}"
    assert sorted(p.name for p in kept.glob("*.json")) == [f"{n:05d}.json" for n in range(1, 5)]
    assert "hit@5 no" in line_of(done.stdout, "q03")            # before families: no hit

    w.set_families(FAMILIES)
    w.respond(trip=True)
    before = len(w.calls())
    doc, text = w.run("--kept", str(kept))
    asked = [c for c in w.calls()[before:] if c[:1] == ["retrieve"]]
    assert not asked, f"the re-score ran the retriever again: {len(asked)} retrieve calls"
    q = by_id(doc)
    assert figures(q["q01"]) == (True, 1, True, True, 1, 1)
    assert figures(q["q02"]) == (True, 1, True, True, 2, 2)
    assert figures(q["q03"]) == (True, 2, True, True, 1, 1)
    assert (q["q01"]["calls"], q["q02"]["calls"], q["q03"]["calls"]) == (1, 2, 1)
    assert names_family_hit(line_of(text, "q02"), CAP7), line_of(text, "q02")
    assert names_family_hit(line_of(text, "q03"), CAP9), line_of(text, "q03")

    fresh = World(tmp_path / "fresh", FAMILIES)
    for qid in ("q01", "q02", "q03"):
        src = yaml.safe_load((w.visible / f"{qid}.yaml").read_text())
        fresh.question(qid, src["sources"], [p["evidence"] for p in w.answers[src["question"]].values()])
    live, _ = fresh.run()
    keys = ("hit_at_5", "in_bundle", "full_evidence", "first_gold_rank", "pieces_found", "pieces_needed", "calls",
            "stacked_digest")
    for qid, one in by_id(live).items():
        assert {k: q[qid][k] for k in keys} == {k: one[k] for k in keys}, f"{qid}: the re-score differs from a run"
