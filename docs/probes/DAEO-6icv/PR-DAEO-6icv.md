---
type: probe
task: DAEO-6icv
reviewer_session: c324d1ca-8a75-43d0-9ca1-7c006195c7dc
implementer_session: 9784c9b7-f14d-4f47-b37f-27211b3d19ee
fix_implementer_session: a116b758-80e7-4430-a8a1-fe53f84ec12c
records_implementer_session: fad698e6-c98d-4c63-a213-b18c0321e8ce
test_designer_session: 8ec9e7ec-6045-4491-8b61-e15767a0fcdf
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 0b0d4cb3053db6f64a7275d904fc41b3cc26ed18
decisions_applied: [DEC-959, DEC-957, DEC-616, DEC-645, DEC-801, DEC-802, DEC-808, DEC-1010]
---

# Probe record: W2-101 (DAEO-6icv), domain skills B (frontend, ui-ux, devops): the narrow independent check, round 1 (STANDARD)

## The lead's judgement

**Fail.** The reviewer (a fresh read-only Opus session, effort high) found one blocking finding, F1, which is in
scope, reachable in ordinary work and fails open. The lead does not decide a FAIL away (DEC-1010). F1's fix lies outside
the ticket's paths and outside its Interface ("No product code changes"), so it goes to the CTO as a package with
options. F2 to F6 are rows. Everything else the check probed is sound (see the reviewer's record below).

The lead's own verification at the same head (`lead_verify`, 6312 tests) found one more red that the review did not
name. It is recorded here as **L1** for the same next batch (DEC-802):

**L1, the lead's finding: W2-11's output-class case refuses the three skills' `output:` value.**
`tests/acceptance/W2-11/test_w2_11_round2.py::test_every_write_step_lies_in_the_skills_output_class[frontend|ui-ux|devops]`
fails with: `output is neither none nor a path class: "the ticket's own allowed paths"`.
- Ordinary work: yes, because it is the committed text, and the case runs in every full suite.
- Consequence: other (a red case, which fails closed; nothing passes that should not).
- Scope: in.
- The fix raises each skill's version, which needs a fresh `gov skilleval` run. That run would leak the summaries
  under F1, so the fix waits on F1's decision instead of running now.

The other reds at this head, none caused by a defect in this change:
- the six W2-101 `.claude/skills/` copy cases and W2-11's `test_the_skill_carries_one_version_in_all_four_places[*]`
  (3): `.claude/skills/<skill>/` arrives only with the copies ACT, after the owner's yes (DEC-315, DEC-1112 (3));
- `tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request`:
  red when run alone, and red alone on the base tree too (`33d10146e`, tests only on the base). Not caused by this
  ticket.

Threat model (DEC-801, DEC-808): honest agent mistakes and plausible accidents in ordinary work. Only "ordinary work:
yes" together with "fails open" or "loses work" fails a round.

## What was probed

- Branch `w2/W2-101`, base `2748a2b19622` (the interface merge), head `0b0d4cb3053d`.
- `b465043d5c79`, `fb784e756147`, `c0f72460ec39` (product-spec `9784c9b7-…`): scenarios first, then the skills and
  I1, then the copies.
- `33d10146ee6d` (independent test designer `8ec9e7ec-…`), merged at `b27f27354`.
- `9905c9951763`, `33484a699983` (product-spec fix `a116b758-…`): frontend scenario 3 made judgeable; the skill made
  consistent (P1), version 1.1.0.
- `0b0d4cb3053d` (product-spec `fad698e6-…`): the harness's records of three real `gov skilleval` runs, the summaries,
  the copies.

## The reviewer's findings (verbatim)

**F1, blocking: the scenario summaries would be visible to the session under test in a future `gov skilleval` run.** Scope: in.
- **What happens:** `scenario-summaries.md` sits in each skill folder. `gov skilleval` copies that folder into the session's workspace and excludes only `scenarios.md` and `scenario-records.yaml`.
- **Why it matters:** the summaries describe the expected behaviour and the judge's reasons (for example "ranked the open question P1 … the part the diagnostic run failed"). The sessions do look in that folder: they listed its files and followed the `scenarios.md` link. So the next run after any change to the skill text could pass on the leaked answers rather than on the text.
- **The present records are clean:** the summaries were committed at 02:02:40, after the last run at 01:59, and the captured workspaces held only SKILL.md and the check script.
- **What should happen:** the session sees the skill's text alone.
- Ordinary work: yes, because re-running `gov skilleval` after changing the skill's text is the template's own rule, and nothing deliberate is needed.
- Consequence: fails open (the scenario gate can pass a regressed skill).
- **What would reverse it:** the harness or the placement keeping the summaries out of the session's copy.

**F2, row: permission lines the check does not catch.** Scope: in.
- The check does not refuse a blockquote, table row or prose permission line, or a camelCase `allowedTools`. A mixed ``` and ~~~ fence, or a duplicate Sources heading at the top, also gets past the order rules.
- Only front-matter keys grant anything, and the validator's closed key list catches `allowedTools`.
- Ordinary work: no, because these need an odd construction.
- Consequence: other.
- **What would reverse it:** a body line that changes the guard's or Claude Code's permissions.

**F3, row: the permission check also reads fenced lines.** Scope: in.
- A devops example showing a GitHub Actions `permissions:` block would be wrongly refused.
- Ordinary work: yes, because a CI example is a plausible future edit.
- Consequence: other (it fails closed).
- **What would reverse it:** the check skipping fences for the permission rule.

**F4, row: an ambiguous pass line in frontend scenario 1.** Scope: in.
- "removes the `outline: none` without a replacement focus style" can be read as forbidding a replacement focus style, against the scenario's own "a visible focus style stays".
- Ordinary work: yes (a judge's misreading). Consequence: other.
- **What would reverse it:** the phrase reading as a noun phrase naming the fault. The final reply passes under either reading.

**F5, row: one unexplained failure in ui-ux.** Scope: in.
- ui-ux run 1 scenario 2 failed at version 1.0.0 with no capture; the same text later passed twice. It is recorded honestly, but no cause is known.
- Ordinary work: no, because it is a model-variance observation, not a defect. Consequence: other.
- **What would reverse it:** a capture of the failure showing a cause in the text.

**F6, row: an Interface clause with no W2-101 counterpart.** Scope: in (the suite's fidelity).
- The Interface's "F2" clause (a P2 route) is W2-100's text. The suite rightly maps by content and names it untested.
- Ordinary work: no. Consequence: other.

## The reviewer's record (verbatim, REVIEW_MD)

### Review: W2-101 (DAEO-6icv) narrow independent check, head `0b0d4cb3053d`
task: DAEO-6icv
decisions: DEC-959, DEC-957, DEC-616, DEC-645, CAP-24.b, DEC-315, DEC-1112, DEC-995, DEC-996, DEC-801, DEC-802, DEC-808, DEC-1010

**Probed and sound:**
- I1: byte-equal copies; all 8 sections, 5 parts and area points named when absent (22 + 8 plants); permission lines named with line numbers, front matter and fences included; real skills PASS.
- No fail-open way for a skill missing a section, part or point to pass.
- Skills: the five parts and §2.7's points present; template order; validator clean; bodies under 150 lines; escalation consistent with DEC-957; no grant, no write outside the paths; a safe method.
- Scenarios added before the text. The frontend fix made scenario 3 judgeable and kept its P1 expectation, so it is not weakened.
- Records are harness-shaped, the last three entries pass at the current version, and the summaries are 1:1 by `run_at` and faithful to the capture (four spot-checks). The capture is a pass-through and a fair reading.
- Copies identical. Scope and trailers clean.

**F1 (blocking):** `scenario-summaries.md` in the skill folder is copied into the session's workspace by `gov skilleval`, which excludes only `scenarios.md` and `scenario-records.yaml`. The next run would leak the expected answers to the session under test.
- Ordinary work: yes, because re-running after a text change is the rule.
- Consequence: fails open.
- Options: (a) harness ignore, recommended, riding along (DEC-802); (b) Interface move; (c) entry criterion.

**F2 (row):** body forms of a permission line (blockquote, table, prose, camelCase) not refused; mixed fences or a duplicate Sources heading pass. Ordinary work: no. Consequence: other.

**F3 (row):** a fenced CI `permissions:` example would be refused (fails closed). Ordinary work: yes. Consequence: other.

**F4 (row):** frontend scenario 1's pass line wording on the focus style is ambiguous. Ordinary work: yes. Consequence: other.

**F5 (row):** ui-ux run 1 scenario 2 failed at 1.0.0 without a capture, then passed twice. Ordinary work: no. Consequence: other.

**F6 (row):** the Interface's W2-100 "F2" clause has no counterpart here; the suite says so. Ordinary work: no. Consequence: other.

## The reviewer's verdict (verbatim)

```verdict
{"kpis": [{"kpi": "w2-101-narrow", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```
