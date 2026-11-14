import json
from pathlib import Path

W = Path("/home/usain/gov-os-worktrees/W2-130")
log = json.loads((W / ".gov-runtime/scratch/lead/log/aud-pin2-1.json").read_text())
r, sess = log["result"], log["session_id"]
head = "a300346eb04be6980e0d38e72aca4e630dc992b5"
front = f"""---
type: probe
task: DAEO-q8cl
reviewer_session: {sess}
implementer_session: "independent-test-designer session 37c7bdce-0b08-42f6-b1eb-800d3e4170c9 (commit ed0e54dfecfb6b1f6dfebefcfec360f599923f10)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: {head}
decisions_applied: [DEC-1156, DEC-1164, DEC-1073, DEC-1010]
---

# Probe record: W2-130 (DAEO-q8cl), pin run 2's narrow independent check (a decided-behaviour test revision)

A fresh independent-auditor session (`{sess}`) ran on `claude-opus-5-5` at high effort, class C2, read-only, with
JUDGEMENT.md word for word in its brief. It probed head `{head[:12]}` of `w2/W2-130` (the lead's merge of
`w2/W2-130-tests`), narrow: this revision only, since `67364dbea`. It wrote nothing (`git status` empty; sandbox trial
file absent; its tripwire's only changes are the CTO's commit `1d5af6d75` (P1-MORNING-20261114, Role orchestrator) on
the main tree and the store trees following it, made by other sessions while it ran).

What it probed: the CTO's answers under DEC-1164 (18) and DEC-1156 (7) (listed for the owner's reading): F1 confirmed
(the pin is the record's `counts-after.measured_at`, 6b62de94e); P-W2-130-PIN-S4 (a) (S4's three HEAD-reading cases
pinned at `counts-after.measured_at`, S4's Verify "on HEAD" re-baselined to the record's measured tree); F4 (every
pinned case runs `gov links` from the pinned tree's own `src`). One independent test designer commit, `ed0e54dfe`:
the three S4 cases on `pinned_findings(measured_at)`; one `measured_at` check in `w2_130_support.py`; `child_env`,
`run_links`, `links_json` with an optional `src`; the pinned tool for the three S4 cases, S8's counts and left cases
(at `measured_at`), S8's before-counts case (at 232efc47d) and the two propose-sources cases (at each commit's parent).
No record, README, ticket or source was edited; every README-mapped case name kept.

Its verdict is **PASS**: five items pass, two findings, none blocking (neither in scope with ordinary work yes and
fails open or loses work).

## The lead's judgement of the findings

- **F1** (out of scope: the F3 cases' `variant_findings` still runs the branch's `gov links` on fixed historical trees;
  the README and `test_w2_130_audit.py` say "HEAD's tool", both outside this run's paths). Ordinary work: yes, because
  changes to `gov links` are planned under D-6. Consequence: other (a false red or a weaker check over a fixed history;
  nothing fails open, nothing is lost). A row, brought to the CTO in the lead's return.
- **F2** (out of scope, item 6: `test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack` and
  `test_s4_no_record_lists_per_ticket_ids_that_name_no_record` still read HEAD's tickets and HEAD's tool; a ticket
  closed or reopened after the land, or a new unknown id on a live ticket, turns them red; reproduced in a scratch
  clone). Ordinary work: yes, because tickets are closed and reopened routinely. Consequence: other (a false red on a
  re-run of `gov accept W2-130`; fails closed). Brought to the CTO as a package in the lead's return, shaped like
  P-W2-130-PIN-S4.

The lead's own runs at `{head[:12]}`: the two changed record and sources files 24 passed; `gov accept W2-130` 81
passed, 0 failed (all twelve lines); `gov accept W2-175` 51 passed, 0 failed; the scoped run (DEC-968) of
`tests/acceptance/W2-130` and `tests/acceptance/W2-175` 132 passed.

## The auditor's return, word for word

"""
out = W / "docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin2.md"
out.write_text(front + r.rstrip() + "\n", encoding="utf-8")
print("ok", out)
