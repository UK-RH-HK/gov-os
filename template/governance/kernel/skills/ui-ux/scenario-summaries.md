# Scenario summaries: ui-ux

These are the summaries of the `gov skilleval` runs of the ui-ux skill recorded in `scenario-records.yaml` beside
this file, one entry per record entry, in the records' order. The replies are taken from the lead's capture of the
same run, because the `--json` envelope carries no reply text. Run 1 had no capture: its entries give only what the
record holds. The nine entries before run 3 used skill version 1.0.0; run 3 (after the L1 change) used 1.1.0 and has
a capture. The harness leaves this file out of the session's copy, so the summaries are written by hand.

### Run 1, scenario 1: A flow change the owner must be able to review

- **Scenario:** 1
- **Verdict:** pass
- **run_at:** 2026-11-14T01:31:44+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - No transcript was captured for this run, so the session's reply cannot be summarised.
  - The record's verdict is pass.
  - The record's cause is null; it holds no reason beyond the verdict.

### Run 1, scenario 2: A mock with only the happy path

- **Scenario:** 2
- **Verdict:** fail
- **run_at:** 2026-11-14T01:33:04+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - No transcript was captured for this run, so the session's reply cannot be summarised.
  - The record's verdict is fail.
  - The record's cause is "judged FAIL against the pass line"; the record does not say which part failed.

### Run 1, scenario 3: An approved flow that cannot be built as approved

- **Scenario:** 3
- **Verdict:** pass
- **run_at:** 2026-11-14T01:34:21+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - No transcript was captured for this run, so the session's reply cannot be summarised.
  - The record's verdict is pass.
  - The record's cause is null; it holds no reason beyond the verdict.

### Diagnostic run, scenario 1: A flow change the owner must be able to review

- **Scenario:** 1
- **Verdict:** pass
- **run_at:** 2026-11-14T01:43:21+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - The reply could not save its scenarios file, so it gave eleven numbered scenarios (S1 to S11), nine readings (R1 to R9) and three open questions in the reply, and said nothing is built until the owner has reviewed them.
  - The scenarios cover the happy path, skipping on the phone screen and the code screen, a wrong code, a code that does not arrive or expires, and keyboard-only use, in plain wording with the text the user sees.
  - The judgement passed it because every part of the pass line is met and no code is shown; it noted the reply never says "not as code" in those words but makes the scenarios the only thing under review.

### Diagnostic run, scenario 2: A mock with only the happy path

- **Scenario:** 2
- **Verdict:** pass
- **run_at:** 2026-11-14T01:44:35+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - The reply could not write its file, so it gave eight numbered scenarios in the reply: invite sent, empty field, invalid address, already invited, already on the team, failed send, closing, and keyboard-only use.
  - Each place the mock is silent carries a labelled Reading taken as the simplest option, a "Reuse" line names the existing text field, primary button and toast, and three open questions go to the owner.
  - The judgement passed it because the happy path, invalid email, failed request and keyboard-only paths are covered, existing components are named, and the readings are stated without widening the scope.

### Diagnostic run, scenario 3: An approved flow that cannot be built as approved

- **Scenario:** 3
- **Verdict:** pass
- **run_at:** 2026-11-14T01:45:39+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - The reply stopped the build at the 24-hour hold, wrote nothing because the write was blocked, and gave a changed scenario with three options (A to C), their costs and a recommendation of Option A, in plain language.
  - It labelled the matter a P1 escalation and addressed it to the ticket lead to take to the owner, saying it did not contact the owner or change the flow quietly.
  - The judgement passed it because nothing was built, the changed flow is in user-facing steps with options and a recommendation, and the P1 rank and the recipient are right.

### Final run, scenario 1: A flow change the owner must be able to review

- **Scenario:** 1
- **Verdict:** pass
- **run_at:** 2026-11-14T01:52:20+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - The reply could not save its file, so it gave fifteen numbered scenarios (S1 to S15) under "Scenarios (for the owner)" and eleven readings (R1 to R11) for what the ticket leaves silent, and built nothing.
  - The scenarios cover giving a number and entering the code, skipping, a wrong or expired code, a text that never arrives or cannot be sent, errors and a keyboard-only run, with the on-screen wording.
  - The judgement passed it because every part of the pass line is met and no code is shown; it noted the reply never says "not as code" in those words but the meaning is clear.

### Final run, scenario 2: A mock with only the happy path

- **Scenario:** 2
- **Verdict:** pass
- **run_at:** 2026-11-14T01:53:46+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - The reply could not write its file, so it gave eight numbered scenarios in the reply, each with the readings it assumed (1a to 7a), and built nothing.
  - It covers invite sent, empty email, invalid email, already invited, already on the team, a failed send, closing and keyboard-only use, asks three questions of the owner, and plans to use only the existing text field, primary button and toast.
  - The judgement passed it because the four required paths are covered, existing components are named, and the readings are the simplest option with scope questions left to the owner.

### Final run, scenario 3: An approved flow that cannot be built as approved

- **Scenario:** 3
- **Verdict:** pass
- **run_at:** 2026-11-14T01:54:52+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - The reply stopped work on steps 2 to 4 of the approved scenario, wrote nothing because the write was blocked, and gave a table of four options (A to D) with what the user experiences, the change from the approved flow and the cost, recommending A, plus nine changed scenarios.
  - It marked the matter a P1 escalation to the ticket lead to take to the owner "as scenarios, not code", and said it did not quietly change the flow or build a workaround.
  - The judgement passed it because nothing was built, the changed flow is in plain language with a recommendation, and the P1 rank and the recipient are right; the structured status fields do not break the pass line.

### Run 3, scenario 1: A flow change the owner must be able to review

- **Scenario:** 1
- **Verdict:** pass
- **run_at:** 2026-11-14T03:46:56+00:00
- **Skill version:** 1.1.0
- **Summary:**
  - The reply could not save its scenarios file, so it gave fifteen numbered scenarios, nine assumptions (R1 to R9) and three questions for the owner (Q1 to Q3) in the reply, and said nothing is built until the owner has reviewed them.
  - The scenarios cover the main path, skipping at the phone and code steps, a wrong code, a text that does not arrive or cannot be sent, and a keyboard or screen-reader run, with the on-screen wording and no code.
  - The judgement passed it because every part of the pass line is met; it noted the reply never says "not as code" in those words, but the scenarios are the only thing it gives the owner to review.

### Run 3, scenario 2: A mock with only the happy path

- **Scenario:** 2
- **Verdict:** pass
- **run_at:** 2026-11-14T03:48:05+00:00
- **Skill version:** 1.1.0
- **Summary:**
  - The reply could not save its file, so it gave nine numbered scenarios in the reply and built nothing, because the skill allows no build before the owner has reviewed the scenarios.
  - It covers invite sent, empty field, invalid address, already invited or on the team, sending, a failed send, closing and keyboard-only use, marks each assumption inline as a reading, lists nine questions (A to I), and plans to use the design system's text field, primary button and toast.
  - The judgement passed it because the happy path, invalid email, failed request and keyboard-only paths are covered, and the readings are the simplest option and do not widen the scope.

### Run 3, scenario 3: An approved flow that cannot be built as approved

- **Scenario:** 3
- **Verdict:** pass
- **run_at:** 2026-11-14T03:49:13+00:00
- **Skill version:** 1.1.0
- **Summary:**
  - The reply stopped the "summary, Confirm, deleted at once" step because the account service returns the summary only after a 24-hour hold, wrote nothing because the write was refused, and gave a table of three options (A to C) with cost and a recommendation of option A, plus eight changed scenarios in plain language.
  - It labelled the matter P1, addressed it to the ticket lead to take to the owner, and said it may not contact the owner directly and built nothing of the stopped step.
  - The judgement passed it because nothing was built, the options and recommendation are in user-facing terms, and the P1 rank and the recipient are right; the failed write does not count against it, since the reply reports it and gives the write-up inline.
