"""Write W2-100's two probe records under docs/probes/DAEO-uw5h/, each the reviewer's own record and verdict block
verbatim, with the lead's front matter, context and triage."""
from pathlib import Path

base = Path("/home/usain/gov-os-worktrees/W2-100")
lead = base / ".gov-runtime/scratch/lead"
out = base / "docs/probes/DAEO-uw5h"
out.mkdir(parents=True, exist_ok=True)

r1, v1 = (lead / "rev-1-review.md").read_text(), (lead / "rev-1-verdict.txt").read_text()
r2, v2 = (lead / "rev-2-review.md").read_text(), (lead / "rev-2-verdict.txt").read_text()

one = f"""---
type: probe
task: DAEO-uw5h
reviewer_session: ed998176-b05d-4462-acf4-bb4a4ede09e4
implementer_session: 836194c6-44c6-45a7-9218-ccff2a11ec57
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: f8e7c0fad6c6f07e48edb0d7e110625212089066
decisions_applied: [DEC-959, DEC-957, DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112, DEC-801, DEC-808, DEC-1010]
---

# Probe record: W2-100, the narrow independent check of the four domain skills (check 1)

A fresh independent-auditor session (`ed998176-b05d-4462-acf4-bb4a4ede09e4`) ran on Opus at high effort, class C2,
with read-only tools. It probed head `f8e7c0fad6c6` of `w2/W2-100` (base `627bcaa19351`, the merge of the ticket's
interface) and wrote nothing in the tree: `git status --porcelain` was empty when it finished. Its brief carried
JUDGEMENT.md word for word. The implementers were:
- product-spec ps-1 (`836194c6-44c6-45a7-9218-ccff2a11ec57`): `a7989493b` (the scenarios, before the text) and
  `c7686c533` (the four skills, `check_domain_skill.py`, the `.rulesync` copies);
- product-spec fix 1 (`2125e132-c077-4cfd-ac60-a0b45b32c215`): `fef53fb21`; batch 2 (`7f067bc9-4d95-4ebc-b18a-f72acb35c721`):
  `b266cf8a4`; fix 2 (`e859d446-e243-4df5-a8d4-f9164f30d36b`): `121c99a44`; batch 3
  (`08f87d1f-1380-43ae-b26b-e80355368346`): `b3503e0a3`;
- test designer td-1 (`3eb5fc04-64f6-4ceb-9fcd-89784d9aea97`): `d9379baaa`; td-2 (`4f0b240e-e96e-4619-b3fd-3c5a1c44b977`):
  `26a1a98ce`. The lead merged the tests as `8ce2dd268` and `f8e7c0fad`.

## The lead's triage (DEC-1010: a finding blocks only if in scope, ordinary work and fails open or loses work)

- **F1** (S4, in, ordinary work yes, other): run 5's passes were made with `scenario-summaries.md` in the session's
  skill folder. Not blocking; accepted and acted on in the same round (DEC-802): clean runs 6 to 8 with the summaries
  moved aside, and each summaries file now states it. Checked by check 2 (`PR-DAEO-uw5h-check2.md`).
- **F2** (S4, out, ordinary work yes, fails open): `gov skilleval` (W2-104's harness, `src/gov/skilleval/harness.py:167-168`)
  copies every file of a skill folder but `scenarios.md` and the record into the session, so a later run of these
  skills sees the summaries. Out of this ticket's scope and paths (`src/`): package P-W2-100-F2 to the CTO in the
  lead's return; an entry criterion for the next `gov skilleval` of any folder holding a summaries file (DEC-803).
- **F3** (S4, in, other): api scenario 2 had one clean fail and one borderline clean pass. Acted on: run 6 failed it
  again cleanly; the api text was fixed (1.0.2, `3318e42f6`, `05fcc8f2e`); clean runs 7 and 8 pass it.
- **F4** (F2, in, other): `fef53fb21` labels the defect "a security finding" in the Situation. A row (the scenario
  passed twice on the earlier wording).
- **F5** (F2, in, other): I1's below-P1 check is bound to the word "finding(s)", per the interface. A row for a later
  I1 revision (also vulnerability, weakness).

## The reviewer's record (verbatim)

{r1}
## The reviewer's verdict block (verbatim)

{v1}"""

two = f"""---
type: probe
task: DAEO-uw5h
reviewer_session: f58efebb-5156-4c28-ac56-891f33c63c65
implementer_session: e7e65139-de89-4fb9-989e-deb11099d7c2
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: f7637bd03e2597873c828243e789ea2293c22513
decisions_applied: [DEC-959, DEC-957, DEC-616, DEC-645, DEC-801, DEC-802, DEC-808, DEC-1010]
---

# Probe record: W2-100, the narrow check of the follow-up to check 1's F1 and F3 (check 2)

A fresh independent-auditor session (`f58efebb-5156-4c28-ac56-891f33c63c65`) ran on Opus at high effort, class C2,
with read-only tools. It probed head `f7637bd03e25` of `w2/W2-100`, the follow-up `f8e7c0fad6c6..f7637bd03e25` only,
and wrote nothing in the tree (`git status --porcelain` empty). Its brief carried JUDGEMENT.md word for word. The
implementers were product-spec fix 3 (`e7e65139-de89-4fb9-989e-deb11099d7c2`): `3318e42f6` (api and data 1.0.2, given
run 6's failing output only); fix 4 (`ab83a8f7-8935-4b63-a04a-c98244d61b40`): `05fcc8f2e` (the two examples that quoted
the scenarios' nouns made neutral, before any run at 1.0.2); summaries batch 4 (`0dde31c7-6850-43c7-bdb2-4c8c9a67cc68`):
`f7637bd03` (the records of clean runs 6 to 8 and their summaries). The lead ran the clean runs 6, 7 and 8.

## The lead's triage

All four findings are rows (none fails open or loses work): **N1** fix 3 follows the judge's reasons (sound method,
no scenario nouns); **N2** fix 4 amended 1.0.2's text without a new version, before any run or record at 1.0.2 (the
lead's call, recorded in fix 4's brief); **N3** backend scenario 3 passes on the letter in clean run 6, and backend and
security have one clean run each at their current version; **N4** api SKILL.md line 84 is longer than the file's wrap.

## The reviewer's record (verbatim)

{r2}
## The reviewer's verdict block (verbatim)

{v2}"""

(out / "PR-DAEO-uw5h-check1.md").write_text(one)
(out / "PR-DAEO-uw5h-check2.md").write_text(two)
print("written", len(one.splitlines()), len(two.splitlines()))
