# Review: W2-101 (DAEO-6icv) narrow independent check, head `0b0d4cb3053d`
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
