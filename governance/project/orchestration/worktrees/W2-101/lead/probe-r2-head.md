---
type: probe
task: DAEO-6icv
reviewer_session: 16ac2e36-37d9-4516-8841-a3601fc06a24
implementer_session: c5303202-dc77-4b73-9906-d2016fa5025d
records_implementer_session: 42a47518-8137-41b1-a73b-3036d20868ab
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 1ef54a70037ac1f4e6bd64a680591b132e299bbf
round_1_probed_commit: 0b0d4cb3053db6f64a7275d904fc41b3cc26ed18
decisions_applied: [DEC-959, DEC-957, DEC-616, DEC-645, DEC-801, DEC-802, DEC-803, DEC-808, DEC-1010]
---

# Probe record: W2-101 (DAEO-6icv), domain skills B: the narrow independent check, round 2 (the last, DEC-1010)

A fresh independent-auditor session (`16ac2e36-37d9-4516-8841-a3601fc06a24`) ran on Opus at high effort, class C2,
read-only. It probed head `1ef54a70037a` of `w2/W2-101`, narrowly: round 1's F1 to F6 and the lead's L1
(`docs/probes/DAEO-6icv/PR-DAEO-6icv.md`), and anything the fixes broke. It wrote nothing in the tree (`git status
--porcelain` empty; launcher tripwire clean). Its brief carried `governance/project/briefs/JUDGEMENT.md` word for word.

What it probed (`0b0d4cb3053d..1ef54a70037a`):
- `57ea2d40bb9f`: the lead's `--no-ff` merge of `w2/integrate`, bringing W2-104's harness fix (`ac18ac2ab7c8`, landed
  as `c9f07ef3782b`; the CTO's reopen under DEC-1164 (18)): `gov skilleval` leaves `scenario-summaries.md` out of the
  session's copy (F1, option (a)), and the condensed Interface (CTX-1 (a)).
- `3cd17b73e3ee` (product-spec `c5303202-dc77-4b73-9906-d2016fa5025d`, given L1's failing output only): each skill's
  `output:` is the path class `"<allowed_path>/** (one entry of the ticket's allowed_paths)"`; versions frontend
  1.2.0, ui-ux 1.1.0, devops 1.1.0; copies refreshed.
- The lead's run 3 of the real `gov skilleval` (Opus, high) on all three skills, 03:43 to 03:55 UTC on 2026-11-14,
  after the skill text: 9 of 9 pass; each reply captured by the pass-through `claude` wrapper (capture lines 31 to 48).
- `1ef54a70037a` (product-spec `42a47518-8137-41b1-a73b-3036d20868ab`): run 3's records as the harness wrote them,
  nine new summary entries, each file's opening updated, and the copies.

## The lead's verification at `1ef54a70037a`

- `gov accept W2-101`: 271 passed, 6 failed; every KPI line passes but success-6 and failure-5, whose 6 failures are
  the same `.claude/skills/` cases counted under both.
- `lead_verify` (DEC-968): 6328 tests, 9 failed, 0 errors, 7 skipped (`.gov-runtime/scratch/lead/log/verify/`). The
  nine: `test_w2_101_copies.py::test_the_claude_copy_matches_the_kernel_source[frontend|ui-ux|devops]`,
  `::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill[frontend|ui-ux|devops]` (GENERATED_DIFFERS),
  and W2-11's `test_the_skill_carries_one_version_in_all_four_places[frontend|ui-ux|devops]`. Each fails because
  `.claude/skills/<skill>/` is absent. The copies ACT places it after the owner's yes (DEC-315, DEC-1112 (3)); it is
  outside the ticket's paths. None is in `skip_known.json`. The reviewer reproduced the same nine. W2-11's output-class
  cases (L1) pass. The run-2 reranker red (`test_w2_112_shared_reranker`) did not recur.

## The lead's triage

**Pass.** No finding is in scope, reachable in ordinary work and failing open or losing work. F1 and L1 are fixed.
F2 to F6 keep round 1's classification. F7, F8 and F9 are new rows:
- **F7:** the path class is broad for W2-11's stray-write check. Ordinary work: no. Consequence: other.
- **F8:** out of scope. It becomes an entry criterion for any ticket that gives the harness's sessions tools
  (DEC-803). Ordinary work: no. Consequence: fails open, only if that feature is switched on.
- **F9:** the `scenarios.md` link points at a file the harness leaves out. Ordinary work: yes. Consequence: other
  (noise; no verdict affected).

All of them go to the Wave 3 row list. This is the last round (DEC-1010); nothing goes to the owner from the review.

## The reviewer's record (verbatim, REVIEW_MD)

