"""W2-128 round 1: the link lines (LINK-INTEGRITY §5, DEC-1073 (5)(c)), the CIT-P record's draft, and the
dependency fields' template part (DEC-1088 (3)). The refusals READS_MISSING, NEEDS_MISSING and WAITS_ON_MISSING are
round 2 (README).

Each string test asks for the substance of §5's lines for that template (the field names and words the lines
quote), never their wording; a {CMD:name} counts as its run form in facts.yaml.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys

import pytest
import yaml

import w2_128_support as s

# §5's lines per template: (needles every one present in the template, case-insensitive) and units that must exist
# (all needles of each tuple in one unit).
LINK_LINES = {
    # Every role (T-0, the commit form; D5 row 10)
    "brief": {"text": ("w2 id", "accepted", "discoveries", "proposed"),
              "units": [("task: {id}",), ("role: {role}",), ("implements: {impl}",)]},
    # Filing a ticket (T-1; §5's orchestrator lines for a ticket)
    "ticket": {"text": ("sources", "depends_on", "closes", "bracket"), "units": []},
    # Research (T-2; D5 row 17)
    "role-research": {"text": ("decisions:",), "units": []},
    # Product-spec (T-3; D5 row 13)
    "role-product-spec": {"text": ("decisions:", "decisions_read:", "decisions_carried:", "contract.yaml"),
                          "units": [("accepted", "[")]},
    # Test designers (T-4; D5 row 15)
    "role-test-designer": {"text": ("task:", "node id", "acceptance_tests.path"), "units": []},
    # Engineers (T-5; D5 row 14)
    "role-engineer": {"text": (), "units": [("comment", "accepted")]},
    # Auditors and reviewers (T-6; D5 row 16)
    "role-reviewer": {"text": ("task: {id}", "decisions:"), "units": [("superseded", "proposed", "both")]},
    # Leads (T-7; D5 row 12)
    "role-lead": {"text": ("decisions_applied", "task: {id}"),
                  "units": [("gov links --since {base}", "first line", "evidence"), ("discoveries",),
                            ("implements:", "sources:")]},
    # The orchestrator, the CTO (T-8; D5 row 11)
    "role-cto": {"text": ("under:", "changes:", "supersedes:", "changed by:", "superseded by", "head~1",
                          "decided-by:", "task: decision-record", "closes:", "constrains:", "depends_on:"),
                 "units": []},
    # The record templates
    "decision-record": {"text": ("under:", "changes:", "changed by", "supersed"), "units": []},
    "lesson": {"text": ("sources:", "constrains:"), "units": []},
    "failure": {"text": ("sources:", "constrains:"), "units": []},
    "research": {"text": ("decisions:",), "units": []},
    "checkpoint": {"text": ("task:", "decisions_applied:"), "units": []},
}


@pytest.mark.parametrize("stem", sorted(LINK_LINES))
def test_s14_template_carries_its_link_lines(stem):
    data = s.facts_or_empty()
    text = s.template(stem)
    whole = s.fold(" ".join(s.expanded(unit, data) for unit in s.units(text)))
    missing = [needle for needle in LINK_LINES[stem]["text"] if s.fold(needle) not in whole]
    assert not missing, f"{stem}.md lacks LINK-INTEGRITY §5's {missing}"
    for needles in LINK_LINES[stem]["units"]:
        assert s.units_with(stem, *needles), f"{stem}.md has no line holding {needles} (LINK-INTEGRITY §5)"


# --- the planted records: gov links on a record filled from each template's example --------------------------------

PLANTED = {
    "lesson": "docs/lessons/L-0000.md",
    "failure": "docs/failures/FAIL-0000.md",
    "research": "docs/research/RES-0000.md",
    "checkpoint": "docs/checkpoints/CP-0000.md",
    "decision-record": "docs/adr/ADR-0000.md",
    "ticket": ".tickets/DAEO-xxxx.md",
}


FILLED_TICKET = "DAEO-t8mp"  # this ticket; its file is planted beside a record template's example


def _example(stem: str) -> str:
    """The record a template's example gives, filled: a record template with its ticket placeholder ({ID}, or the
    example id DAEO-0000 / DAEO-xxxx) set to this ticket's id; T-1's yaml skeleton as a ticket's front matter, as
    it stands (its id is its own)."""
    text = s.template(stem)
    if stem != "ticket":
        return re.sub(r"\bDAEO-(?:0000|xxxx)\b", FILLED_TICKET, text.replace("{ID}", FILLED_TICKET))
    _, body = s.split(text)
    blocks = [content for info, content in s.fenced_blocks(body) if info.split()[:1] == ["yaml"]]
    assert len(blocks) == 1, "ticket.md has no single yaml skeleton to plant"
    skeleton = yaml.safe_load(blocks[0])
    assert isinstance(skeleton, dict) and skeleton.get("id"), "ticket.md's skeleton has no id"
    return "---\n" + blocks[0].strip("\n") + "\n---\n# the planted ticket\n"


def _judge(tmp_path, rel: str, text: str) -> tuple[dict | None, int, str]:
    """A temporary repository holding the register, the path map and the one planted record, judged by
    ``gov links --all --json`` (this tree's code). One record a repository: a planted ticket's prefix would
    otherwise make another template's placeholder id (``DAEO-0000``) read as a ticket id."""
    tree = tmp_path / "repo"
    (tree / "governance/project").mkdir(parents=True)
    (tree / "docs").mkdir()
    shutil.copy(s.REGISTER, tree / "docs/DECISION_REGISTER.md")
    shutil.copy(s.REPO / "governance/project/path-map.yaml", tree / "governance/project/path-map.yaml")
    (tree / rel).parent.mkdir(parents=True, exist_ok=True)
    (tree / rel).write_text(text, encoding="utf-8")
    if not rel.startswith(".tickets/"):
        (tree / ".tickets").mkdir()
        shutil.copy(s.REPO / f".tickets/{FILLED_TICKET}.md", tree / f".tickets/{FILLED_TICKET}.md")
    s.git(tree, "init", "-q")
    s.git(tree, "add", "-A")
    s.git(tree, "commit", "-q", "-m", "plant")
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "links", "--all", "--json", "--root", str(tree)],
                          capture_output=True, text=True, env=s.sealed_env(tmp_path), timeout=120)
    try:
        answer = json.loads(done.stdout)
    except ValueError:
        answer = None
    return answer, done.returncode, done.stderr[-500:]


@pytest.mark.parametrize("stem", sorted(PLANTED))
def test_s14_gov_links_finds_nothing_on_a_record_planted_from_the_template(tmp_path, stem):
    rel = PLANTED[stem]
    answer, code, stderr = _judge(tmp_path, rel, _example(stem))
    assert isinstance(answer, dict) and answer.get("ok"), f"gov links could not judge the planted tree (exit {code}): {stderr}"
    found = [f"{f['code']} {f.get('ids')} line {f.get('line')}" for f in answer["result"]["findings"]
             if f.get("path") == rel]
    assert not found, f"gov links finds on {rel}, planted from {stem}.md: {found}"


# --- S17: the CIT-P record's draft ---------------------------------------------------------------------------------

def test_s17_the_cit_p_record_exists_naming_its_evidence_r2_r3_and_cap_33():
    text = s.read(s.CIT_P)
    assert "CAP-33" in text, "docs/changes/W2-128-CIT-P.md does not name CAP-33"
    for evidence in ("R2", "R3"):
        assert re.search(rf"\b{evidence}\b", text), f"docs/changes/W2-128-CIT-P.md does not name its evidence {evidence}"


# --- S19: the dependency fields in T-1 -----------------------------------------------------------------------------

def test_s19_t1_sets_reads_needs_and_waits_on_beside_allowed_paths_with_their_meanings():
    _, body = s.split(s.template("ticket"))
    blocks = [content for info, content in s.fenced_blocks(body) if info.split()[:1] == ["yaml"]]
    assert len(blocks) == 1, "ticket.md has no single yaml skeleton"
    skeleton = yaml.safe_load(blocks[0])
    assert isinstance(skeleton, dict), "ticket.md's skeleton is not a mapping"
    for key in ("allowed_paths", "reads", "needs", "waits_on"):
        assert key in skeleton, f"ticket.md's skeleton lacks {key}:"
    waits = skeleton["waits_on"]
    assert isinstance(waits, list), f"waits_on is not a list: {waits!r}"
    assert all(isinstance(item, dict) and {"on", "reason"} <= set(item) for item in waits), \
        f"waits_on items are not {{on, reason}} as YAML reads them (an unquoted on: is read as true): {waits!r}"
    raw = blocks[0].split("\n")
    outside = s.units(s.prose(body))
    for key in ("reads", "needs", "waits_on"):
        commented = any(re.match(rf"^\s*{key}:.*#\s*\S", line) for line in raw)
        explained = any(re.search(rf"`{key}:?`|\b{key}:\s+\S", unit) and len(unit) >= 40 for unit in outside)
        assert commented or explained, f"ticket.md gives {key}: no meaning (a comment or a line of its body)"
