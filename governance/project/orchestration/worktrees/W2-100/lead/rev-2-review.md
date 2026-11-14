# W2-100 (DAEO-uw5h): second narrow check, the follow-up to F1 and F3

- **Probed:** `f7637bd03e25` (follow-up `f8e7c0fad6c6..f7637bd03e25`: `3318e42f6c0c`, `05fcc8f2e`, `f7637bd03e25`)
- **Auditor session:** `f58efebb-5156-4c28-ac56-891f33c63c65`, independent auditor, fresh and read-only
- **task:** DAEO-uw5h
- **decisions:** DEC-959 (items 4 and 5), DEC-957, DEC-616, DEC-645, DEC-801, DEC-808, DEC-1010

## Result
Pass. F1 is settled: the summaries were out of the skill folders in runs 6, 7 and 8, which the listings, the timestamps and the transcripts all show, and each summaries file now discloses run 5's exposure. F3 is settled: api scenario 2 passes clearly in both clean runs at 1.0.2. Each skill has a clean 3/3 run at its current version: backend and security run 6 at 1.0.1; api and data runs 7 and 8 at 1.0.2.

## What I probed and found sound
- **The 1.0.2 text:**
  - It is method guidance: a rename asked for inside a version is made additive, and only what cannot be made additive is escalated; the old-client test is named apart from the agreement test; tests are named with their input or bad row in the return.
  - No scenario noun appears in any of the four SKILL.md files; fix 4 removed the nouns fix 3 had quoted, before any run.
  - Each skill's `check_domain_skill.py` passes, the validator exits 0, the versions agree, there is no permission line, and the security skill is untouched.
- **The records:** append-only; earlier entries unchanged since `b3503e0a3`; new entries equal the envelopes in order; run 6's fails stand.
- **The summaries:** form and content match the records and the sampled replies and judge replies; only the opening paragraph changed, and it is truthful.
- **Copies and scope:** both copies are equal to the source for all four skills; portability gives no `SOURCE_*` finding; the diff stays within the ticket's paths; the trailers are correct.

## Findings (all rows, none blocking)
| id | finding | ordinary work | consequence | scope |
|---|---|---|---|---|
| N1 | Fix 3's lines follow the judge's fail reasons and the 1.0.2 replies repeat their wording; sound method, no scenario nouns | yes, because a fix written from a failing output follows the judge's words | other | in |
| N2 | Fix 4 changed 1.0.2's text without a version bump; no run used the earlier 1.0.2 text | yes, because an amendment made before any run is easy to leave unversioned | other | in |
| N3 | Backend scenario 3, clean run 6, passes on the letter (no local guard); only one clean run for backend and security | yes, because one judged run can pass narrowly | other | in |
| N4 | api SKILL.md line 84 is longer than the file's wrap | yes | other | in |

## Refusals
One refusal: the Write of a script into my own TMPDIR was refused by quiet hours (DEC-991) and queued for the morning package. I did not retry it and did the work with read-only inline commands.

## Not run
Check 7 (tests); the lead runs them.
