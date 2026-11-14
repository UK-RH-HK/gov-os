## Findings

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
