"""S5 and failure lines 3-4: nothing else about the launch script changes, and the ticket's branch touches only its own
paths (DEC-1112 (3), DEC-1113).

S5's main check is W2-149's own acceptance cases, run unchanged by ``gov accept W2-149``; a diff of the script's text
outside the four changes is the reviewer's, never a test here. What this file adds:
- set-up A's flows keep their stop rule: a set-up A result with a stopped word still ends 20 (W2-149 S29), never S2's 21;
- failure line 3: the branch's ``git diff --name-only <base>...HEAD`` names none of the walls' template files, the path
  map, the guard, an approved list or a set-up A brief;
- failure line 4: it names only paths the ticket's ``allowed_paths`` match, plus ``tests/acceptance/W2-173/**``.

Readings: the base is the merge-base of HEAD with ``w2/integrate`` (``dac438772``, the ticket's claim commit, when no
merge-base is found); the ticket's own process records that ride a ticket's branch (its ticket file
``.tickets/DAEO-qz4p.md``, ``docs/checkpoints/DAEO-qz4p/**``, ``docs/probes/DAEO-qz4p/**``) count as its own paths
(W1-01's reading: a commit may touch its ticket's own file); "the guard" is ``src/gov/guard/**``, ``.claude/hooks/**``
and ``template/governance/kernel/hooks/**``; "an approved list" is any file named ``APPROVED``.
"""

from __future__ import annotations

import fnmatch

import yaml

import w2_173_support as s
from w2_173_support import sa, support

FORBIDDEN = ("governance/project/indep-walls/*", "governance/project/path-map.yaml", "src/gov/guard/*",
             ".claude/hooks/*", "template/governance/kernel/hooks/*", "governance/project/indep-briefs/sgx1/*",
             "*/APPROVED", "APPROVED")
OWN_RECORDS = (f".tickets/{s.TICKET_ID}.md", f"docs/checkpoints/{s.TICKET_ID}/*", f"docs/probes/{s.TICKET_ID}/*")


# -- S5: set-up A's stop rule unchanged ------------------------------------------------------------------------------

def test_s5_a_set_up_a_result_with_a_stopped_word_still_ends_20_not_21(world):
    """Green today (W2-149 S29): writer 1's result says it stopped; nothing lands in the half's folder; the code is 20."""
    out = sa.stopped_out(sa.writer_out("writer-tuning"), sa.STOP_WORD["writer-tuning"])
    run = sa.deliver(world, "writer-tuning", "tuning", out=out)
    assert run.code == 20, run.why()
    assert run.line["status"] == "rejected" and run.line["reason"] == "result", run.line
    assert not (world.half("tuning") / "planted" / "cases.jsonl").exists(), "writer 1's cases landed"


# -- failure lines 3 and 4: the branch's names -----------------------------------------------------------------------

def branch_names():
    tree = support.TREE
    try:
        base = support.git(tree, "merge-base", "HEAD", "w2/integrate").strip()
    except RuntimeError:
        base = support.git(tree, "rev-parse", "--verify", s.BASE_FALLBACK + "^{commit}").strip()
    names = [x for x in support.git(tree, "diff", "--name-only", "--no-renames", f"{base}...HEAD").splitlines()
             if x.strip()]
    return base, names


def ticket_allowed_paths():
    text = (support.TREE / ".tickets" / f"{s.TICKET_ID}.md").read_text()
    front = yaml.safe_load(text.split("\n---", 1)[0].lstrip("-\n"))
    paths = front.get("allowed_paths")
    assert isinstance(paths, list) and paths, "the ticket names no allowed_paths"
    return paths


def matched(path, globs):
    return any(fnmatch.fnmatch(path, g) for g in globs)


def test_f3_the_branch_changes_no_template_path_map_guard_approved_list_or_set_up_a_brief():
    base, names = branch_names()
    hit = [n for n in names if matched(n, FORBIDDEN)]
    assert hit == [], f"the branch (against {base[:12]}) changes controlled files: {hit}"


def test_f4_the_branch_changes_only_the_ticket_s_paths():
    base, names = branch_names()
    allowed = ticket_allowed_paths() + [f"tests/acceptance/{s.W2}/**"] + list(OWN_RECORDS)
    outside = [n for n in names if not matched(n, allowed)]
    assert outside == [], f"the branch (against {base[:12]}) changes paths outside the ticket's: {outside}"
