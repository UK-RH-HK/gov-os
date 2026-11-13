---
type: probe
task: DAEO-siiz
reviewer_session: 2bec81b2-9417-4692-bea5-d77452d66a55
implementer_session: 327b3072-8edb-4688-bf0e-aa07760f1471
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 643aeeef6ffb6fca20ab41533ecae8ade90b9548
---

# Probe record: W2-52, the lite A7 and A10 stage records

A fresh Independent Auditor session (`2bec81b2-9417-4692-bea5-d77452d66a55`, read-only tools, started outside the sandbox because its probes run A3, which needs the code graph's folder) probed the ticket's whole change (`29bef106..643aeeef`) and wrote nothing. The implementers were the engineer sessions `327b3072-8edb-4688-bf0e-aa07760f1471` (the gates, `bd9fdfec`) and `58b4fb7b-24d2-4d88-a79a-e82d302ed4eb` (`command.STAGES` and the skill's synced copies, `0baae787`). Judged against ADR-0001's threat model (DEC-801): a finding counts toward a round only if an honest agent can hit it in ordinary work and it fails open or loses work.

## What was probed

Head `643aeeef6ffb6fca20ab41533ecae8ade90b9548`, the whole change since `29bef106`. Every probe ran in a temporary harbour project built from scratch with `tests/acceptance/W2-52/w2_52_support.py`, on this worktree's `src/`.

- **Honest flows.** The stages ran in both orders: A6, A7, A8, A10, and A8 before A7. Each run left the tree clean and wrote only its own record, under `governance/adoption/`.
- **Running a gate again over its own record.** It was refused with `ADOPT_GATE_RECORDED` and nothing was written (DEC-796).
- **Failure paths.**
  - With no embedding endpoint, A10 committed a failing record with conditions 6 and 9 both `not met`.
  - An auditor's verdict of `PASS` in upper case gave `not met`.
  - An A6 record with no batches gave `not met`.
  - An auditor session equal to the adopter's was refused with `VERDICT_NOT_INDEPENDENT`, and nothing was written.
  - From reading the code: a record the gate stands on that is missing or unreadable is refused, with nothing written. A partial A8 `retired` list makes every check that reads it `not met`.
- **Scope.**
  - `command.py`: only the `STAGES` entries and the docstring list changed.
  - The adopt skill: only its A7 and A10 section changed, and both `.rulesync` copies are byte-identical to the template skill.
  - `stages.py`: the import line, the A7 and A10 routing in `run()`, and the two `STAGE` entries.
  - The acceptance tests are unchanged since the test designer's commit `d58e9bf2`.
- **Records name Wave 3.** Each record carries a `wave_3` field. A7's names CAP-47.a and condition (4) in full; A10's names A9, CAP-49 and CAP-47.a, and conditions (6) and (9) in full.
- **Suites.** The acceptance suite was run one file at a time: 65 passed. The unit file `tests/unit/adopt/test_lite_gates.py`: 14 passed.

## What it found

**F-1 (low): A10 does not check A8's dependency proof or its imports again.**
- What was done: after A8, a new ACTIVE decision was committed that cites the retired memory store by path and by id. In a separate copy, every rule file A8 had imported into `.rulesync/` was deleted. A10 was then run with an auditor's pass.
- What happened: A10 passed both times, with "the A8 retirement: met". It checks again only that the retired files are out of the tree and reachable at their ref, and it re-checks the chat extraction.
- What should have happened: A10 should hold the retirement to A8's own definition: no active record or rule cites the retired store, and the imported rules are still there.
- The auditor's `pass` is still required, and the retired content can still be reached at the archive ref.
- Ordinary work: yes, because writing a decision that mentions an old memory id, or tidying `.rulesync/`, after A8 is ordinary work.
- Consequence: other. The gate reports a narrower check than A8's invariant. It does not fail open on its own, because the auditor's pass is required. No work is lost, because the archive ref holds the content.

**F-2 (low): `stages.py` changed beyond its two `STAGE` entries.**
- What was done: the diff of `stages.py` was compared with the card's narrowing ("the A7 and A10 entries only").
- What happened: besides the import line and the `STAGE` entries, `run()` gained a two-line branch. It sends A7 and A10 to the gate without `project.chain`. Without that branch the entries cannot work, because `project.chain` fails on a stage that is not in `project.STAGES`.
- What should have happened: an edit that a decision names. DEC-800 counts the import line, "used only by the A7 and A10 routing", among the A7 and A10 entries. The lead reads that routing as this branch, and returns the reading for the owner to confirm.
- Ordinary work: no, because it is a question of the change's scope, not something an agent hits at run time.
- Consequence: other.

**F-3 (low): A7 checks where files are, and a passing record does not notice later drift.**
- What was done: after A6, the moved `docs/handbook/guide.md` was rewritten and committed. A7 was then run.
- What happened: A7 passed. It checks that each target is present and each origin is gone; it does not compare a target's content with the blob in the plan. In the same way, a passing A7 or A10 record stays `pass` if the project drifts after it was written.
- What should have happened: within the lite form this is acceptable. A6 itself checked that each batch moved files without changing them, and editing a file after the migration is legitimate. Whether the verdict should check a gate's record against HEAD is W2-28's question (the machine reader, DEC-795).
- Ordinary work: yes, because editing a moved file after the migration is ordinary work.
- Consequence: other. It does not fail open on what CAP-44.f checks.

## Judgement

pass. No finding is one that an honest agent can hit in ordinary work and that fails open or loses work. Every missing, unreadable or partial input that was tried ended in a refusal or a failing record, and so did every auditor's verdict other than `pass`; none ever gave `met`. F-1 and F-3 are residual rows, for W2-28 and the Wave 3 hardening pass. F-2 is returned to the owner to confirm the scope reading.
