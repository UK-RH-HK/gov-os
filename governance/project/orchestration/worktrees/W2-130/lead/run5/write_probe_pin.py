import json
from pathlib import Path

W = Path("/home/usain/gov-os-worktrees/W2-130")
log = json.loads((W / ".gov-runtime/scratch/lead/log/aud-pin-1.json").read_text())
r, sess = log["result"], log["session_id"]
head = "36d4539dbe433c4b27e94d7cb357ec8b79a5363f"
front = f"""---
type: probe
task: DAEO-q8cl
reviewer_session: {sess}
implementer_session: "independent-test-designer sessions a4392401-9f78-40f4-85ad-4356962dc905 (commit 35b6ac6bacae9aad1c5277e0cb5ac2b9f8973cd0) and 4709ba2f-1fe8-478a-94f8-83d7434eb53f (commit 6a0b84a81a5905d11bd105ba2c1459be3610cbb9)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: {head}
decisions_applied: [DEC-1156, DEC-1164, DEC-1073, DEC-1010]
---

# Probe record: W2-130 (DAEO-q8cl), the pin run's narrow independent check (a decided-behaviour test revision)

A fresh independent-auditor session (`{sess}`) ran on `claude-opus-5-5` at high effort, class C2, read-only, with
JUDGEMENT.md word for word in its brief. It probed head `{head[:12]}` of `w2/W2-130` (the lead's merge of
`w2/W2-130-tests`) and wrote nothing (its tripwire clean; sandbox trial file absent). What it probed: the reopen under
DEC-1164 (18) and DEC-1156 (7) for two decided-behaviour test revisions, made by two independent test designers:
`35b6ac6ba` (W2-130 S8's two cases run `gov links` at the record's pinned tree through `clone_at`, not HEAD; W2-175
S7's sha256 case reads each template at W2-175's landing `61cae50dc` through git) and `6a0b84a81` (the case names the
README maps name kept, the unmapped landing-ancestor case folded into the parametrised one). No record was edited.

Its verdict is **PASS**: five items pass, four findings, none blocking (none in scope with ordinary work yes and
fails open or loses work).

## The lead's judgement of the findings

- **F1** (the cases pin `counts-after.measured_at`, 6b62de94e, where the CTO's decided text names `counts-after.head`,
  57cbacfbf). The lead's measurement: at 57cbacfbf `gov links` gives UNLINKED_ID 1417 and UNKNOWN_ID 57 against the
  record's 1420 and 56, and `left.D-9` differs on five paths, so that pin stays red with the record unedited; at
  6b62de94e every count equals the record, which says it counted that tree, and the ticket's S8 Verify reads "at the
  record's last commit" (a2671a340, parent 6b62de94e). Ordinary work: yes, because the next reader of the reopen
  paragraph expects `counts-after.head`. Consequence: other. Brought to the CTO for confirmation in the lead's return.
- **F2** (`_measured_at` takes any descendant of `counts-after.head` that is an ancestor of HEAD). Ordinary work: no,
  because the record is a closed ticket's path and its counts must still equal `gov links` at the commit it names.
  Consequence: other. A row.
- **F3** (`w2_175_support.py`'s module docstring does not mention `LANDING`; the constant's comment and the test
  module's docstring do). Ordinary work: no. Consequence: other. A row; rides along in any later resume (DEC-802).
- **F4** (out of scope: the S8 cases run the current `src/gov/links` on the pinned tree; a planned D-6 change to
  `gov links` reading DEC-1123 (2)'s forms as linked would move the counts at 6b62de94e and turn S8 red again).
  Ordinary work: yes. Consequence: other (a false red, fails closed). Brought to the CTO in the lead's return: pin the
  tool too, or make that ticket's entry criteria include re-baselining W2-130 S8.

Out of scope and not judged here: `test_w2_130_sources.py::test_s4_every_unlinked_id_on_an_open_or_in_progress_ticket_at_head_is_listed_with_its_dec_1123_2_form`
is red at this head and at its base `f4511c723` (three UNLINKED_ID left by the CTO's `ce8ae4353` on `w2/integrate`);
the lead brings it to the CTO as a package.

## The auditor's return, word for word

"""
out = W / "docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin.md"
out.write_text(front + r.rstrip() + "\n", encoding="utf-8")
print("ok", out)
