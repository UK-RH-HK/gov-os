---
type: probe
task: DAEO-cv58
reviewer_session: 8258087c-2fbf-4188-90b0-654376ed6fae
implementer_session: "6bed9fa7-2e08-41e0-85a8-b867b50bd47c"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 02533b5ebe374f6abb36adcf4102f0b8d1ed596e
decisions_applied: [DEC-1120, DEC-1156, DEC-801, DEC-808, DEC-1010]
---
# W2-60a (DAEO-cv58): check of the live fixture's effort revision

**Scope.** This is the test-only path case from the 2026-11-15 reopening (DEC-1156 (7)). The live fixture passed `--effort low` after `--`, which is below W2-184's floor (DEC-1120 (3)).

**Probed and found sound.**
- **One file changed.** The diff from base to head touches only `tests/acceptance/W2-60a/test_w2_60a_live_sessions.py`. Nothing under `src/` or `pyproject.toml` changed.
- **Trailers.** The designer commit 03226d030198 has one trailer block: `Task: DAEO-cv58`, `Role: independent-test-designer`, `Rewrite-Reason: DEC-1120 (3), DEC-1156 (7)`.
- **Launch arguments.** Only `--effort low` was removed. Every other argument is unchanged. There are still 6 cases, and no assertion was removed.
- **The record's effort assertion can still fail.** It now compares against the fixture role's default (`DEFAULTS[ENGINEER][1]`, high). The fixture project has no criticality file, so the launcher takes the role file's default line. With no `--effort`, no trial and no probe, it records that default's effort and passes `--effort high` to the CLI (`launcher.py:683-690, 747-748, 820, 828`). A record with any other effort fails the assertion.
- **Docstring.** Only the cost paragraph changed, and it states the new effort and the floor correctly.
- **Lead's live run.** `live.out` and `live-junit.xml` show 6 passed, 0 errors, 0 failures, timestamped 11 s after the merge commit.
- **Collection.** `--collect-only` through the heavy slot collected the same 6 node ids.

**Findings.**

F1: `tests/acceptance/W2-60a/README.md:210-212` still says the live session is launched with `--effort low` and that there are 5 cases. The test now launches at the role's own effort (high), and there are 6 cases. The README should say so.
- Ordinary work: yes, because someone rerunning the live case by hand from the README's command line would get the floor's `LAUNCH_REFUSED`.
- Consequence: other (a documentation mismatch; nothing fails open, no work is lost).
- scope: out (the reopen's allowed path is the live test file only).
- Reversed by: a README revision stating the role's effort and 6 cases, or a decision that the README need not follow its fixtures.
- Disposition: a recorded row, fixed at the next legitimate touch of the README by a test designer (DEC-802). Not a round.

```verdict
{"kpis": [{"kpi": "w2-60a-effort-fixture-check", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
