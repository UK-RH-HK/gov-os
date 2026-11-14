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

### Review: W2-101 (DAEO-6icv) narrow independent check, round 2, head `1ef54a70037a`
task: DAEO-6icv
decisions: DEC-959, DEC-957, DEC-616, DEC-645, CAP-24.b, DEC-315, DEC-1112, DEC-801, DEC-802, DEC-803, DEC-808, DEC-1010
reviewer_session: 16ac2e36-37d9-4516-8841-a3601fc06a24
base: 0b0d4cb3053d
reviewer_wrote_nothing: true

**Verdict: pass.** F1 and L1 are fixed. F2 to F6 still hold as rows. F7 to F9 are new rows. Nothing blocks.

**Probed and sound:**
- **F1:** the harness (`harness.py:35`, lines 168–169) leaves `scenarios.md`, `scenario-records.yaml` and `scenario-summaries.md` out of the session's copy.
  - The unit case passed.
  - The real `run_scenario`, run with a stub model call, gave each session only SKILL.md and the check script.
  - Run 3's nine captured prompts and replies show no pass line, no expected answer and no summaries. Five sessions note that `scenarios.md` is missing.
- **L1:** `output: "<allowed_path>/** (one entry of the ticket's allowed_paths)"` is a path class under W2-11's reading.
  - The skills have no write targets; the output-class cases pass.
  - No code reads `output` as a grant.
  - Each body bounds its writes to the ticket's paths.
- **Records:**
  - The last three entries pass at the current version: frontend 1.2.0, ui-ux 1.1.0, devops 1.1.0.
  - Run 3 started after the skill-text commit, and nothing in the skill text changed after it.
  - The summaries are 1:1 by `run_at`.
  - Spot-checks against the capture are faithful: frontend scenario 2, ui-ux scenario 3, devops scenario 3.
  - The openings are true.
- **Copies:** `diff -r` against both rulesync copies is empty. No ticket file is under `.claude/`.
- **Scope:** only the 9 allowed folders and `docs/probes/DAEO-6icv/`.
- **Trailers:** each new commit carries `Task: DAEO-6icv`, a matching `Role:`, and `Implements:` ids from `sources:` only.
- **Checks:** the skills' checks give `PASS`; the validator returns no findings; bodies are 143, 130 and 144 lines.
- **Tests:** in a clone at the head, 6 failed, 500 passed, 1 skipped. With the 3 adapter cases run by name, the 9 reds are all the absent `.claude/skills/` copies, waiting for the copies ACT (DEC-315, DEC-1112 (3)). None is caused by this change.

**F1 (fixed):** the summaries are now kept out of the session's copy. Scope: in.
- Ordinary work: yes, because re-running after a text change is the rule; that path is now closed.
- Consequence: other (fixed).

**L1 (fixed):** W2-11's output-class case passes for all three skills. Scope: in.
- Ordinary work: yes, because the case runs in every full suite.
- Consequence: other.

**F2 (row):** permission lines in unusual body forms get past the check. Scope: in.
- Ordinary work: no, because they need an odd construction.
- Consequence: other.

**F3 (row):** a fenced CI `permissions:` example would be refused. Scope: in.
- Ordinary work: yes, because a CI example is a plausible future edit.
- Consequence: other (it fails closed).

**F4 (row):** frontend scenario 1's pass line is ambiguous. Scope: in.
- Ordinary work: yes, because a judge could misread it.
- Consequence: other.

**F5 (row):** ui-ux run 1 scenario 2 failed at 1.0.0 without a capture. Scope: in.
- Ordinary work: no, because it is model variance.
- Consequence: other.

**F6 (row):** the condensed Interface still uses W2-100's numbering, and its "F2" clause has no W2-101 counterpart. The suite maps by content. Scope: in.
- Ordinary work: no, because it is a numbering artefact the suite already maps.
- Consequence: other.

**F7 (row):** `<allowed_path>/**` matches any path with a slash under W2-11's reading, so the stray-write lint cannot catch a future step naming a path outside the ticket. The worker's root-level `Dockerfile` concern is moot: `write_targets` only collects code spans that contain a `/`. Scope: in.
- Ordinary work: no, because a domain skill naming a fixed out-of-ticket path is unusual, and its Output and checklist lines bound writes.
- Consequence: other (a lint only; the guard and sandbox decide).
- Reversed by: such a step passing W2-11 while `output` is read as a grant somewhere.

**F8 (row):** sessions tried `gov retrieve` from their temporary folder and were refused. A harness that granted tools could reach the summaries in the repository. Scope: out (W2-104's harness).
- Ordinary work: no, because the harness grants no tool.
- Consequence: fails open, only if turned on; an entry criterion for that ticket (DEC-803).
- Reversed by: a session reading the summaries under the current harness.

**F9 (row):** SKILL.md's `[scenarios.md](scenarios.md)` link is missing from the session's copy, and five of nine sessions remarked on it. Scope: in.
- Ordinary work: yes, because it happens on every run.
- Consequence: other (no effect on any verdict).

**Refusal:** one Bash `sed` read of W2-100's ticket `.tickets/DAEO-uw5h.md` was denied. It was not retried.

## The reviewer's verdict block (verbatim)

```verdict
{"kpis": [{"kpi": "w2-101-narrow-r2", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "L1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F8", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
