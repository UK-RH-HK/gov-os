---
type: probe
task: DAEO-zflj
reviewer_session: f5a53e74-8d76-4f77-8621-04a6d53a9cd2
implementer_session: 9e7270bd-8656-46f8-92f0-98d5c1cbdc4c
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: cbb7004cf3905627acf8be9d799358dd935c5cee
---

# Probe record: W2-02 (DAEO-zflj), run 5 (DEC-872, DEC-874)

## Summary

- **What was probed.** Head `cbb7004cf3905627acf8be9d799358dd935c5cee` of `w2/W2-02`. It holds:
  - run 5's merge-back `dbea81c8` of `w2/integrate` (`6855cdf3`: W2-54's run 5, DEC-873 to DEC-878);
  - run 4's merge-back `666f56d1` of `c74a7d43`;
  - the lead's checkpoints `4ce16df2` and `cbb7004c`.

  The ticket's own change, unchanged since run 3, was written by three product-spec sessions:
  - `81eac9a7` (session `031282e8-c63d-482d-8d58-5356fdb6f680`);
  - `5aff5f6d` (session `ed40c613-47ca-4754-971b-1bc18668fa8e`);
  - `f2776ce2` (session `9e7270bd-8656-46f8-92f0-98d5c1cbdc4c`, the last implementer).

  Its acceptance tests are `ae25761d`, `c7827891` and `f8af6d8a`, by the independent test designer.
- **Who probed.** A fresh read-only reviewer:
  - role `independent-auditor`, session `f5a53e74-8d76-4f77-8621-04a6d53a9cd2`, 2026-10-21, effort max;
  - started through `gov launch` under its OS sandbox, with the reading tools alone;
  - commissioned by the ticket lead for the orchestrator, and judged by the lead under the orchestrator's rules (DEC-137).

  It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree.
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries.
  - Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
  - Only "yes" with "fails open" or "loses work" fails the probe.
  - The lead's judgement: no finding is both; R1 to R7 are rows.

## The reviewer's record

### What was probed

- **Head:** `cbb7004c` on `w2/W2-02`: run 5's merge-back `dbea81c8` of `w2/integrate` (`6855cdf3`) and the lead's checkpoint.
- **Step 0:** (a) the write outside the worktree failed (read-only file system); (b) `git hash-object -w` and `git update-index --refresh` worked. `gov.__file__` was this worktree's `src/gov/__init__.py`.
- **Retrieval:** `gov retrieve` gave FACET_UNAVAILABLE (stale), so the register was read by name. No code-graph tool was available in the session; Grep and Read were used on named folders.
- **Refusals:** one read (a search from the repository root) and one write (a Bash redirect whose target the guard could not resolve); neither was retried.
- **Suites:**
  - W2-02 acceptance: 53 passed.
  - W2-54's audit-report and green-here files: 28 passed, with DEC-874's four corrected cases passing on `[HEAD]` and `[4ce16df2]`.
  - `tests/unit/check`: 130 passed.
- **Areas:**
  - the close type against the real `CL-DAEO-7rr2.md` and the writer in `src/gov/close/command.py`;
  - the `STANDALONE_TYPES` resolution and W2-54's audit-report behaviour;
  - both merge-backs against git's own merges (`666f56d1`, `dbea81c8`), and their trailers;
  - who wrote the acceptance tests, and the ticket's paths;
  - the KPI lines.
- **Own probes:** 50 core-schema probes in projects built from scratch, plus the `wbs_id` grammar against 11 ids.

### What was found

Classification: 0 findings fail the probe (yes + fails open or loses work); 7 rows.

#### Sound

- **The close type and core-schema.**
  - Core-schema is green on this repository, so no ordinary close is refused by its pre-close check.
  - Every close record `gov close` writes passes, including for lower-case and digit ticket prefixes.
  - A close record missing `task`, `state_class`, `id` or `status` is refused, naming the field.
  - An unknown type is SCHEMA_UNKNOWN_TYPE.
  - A type with no schema file, an empty schema or a non-JSON schema is unmeasured, not green.
- **W2-54's behaviour is kept.**
  - A record in `docs/audit/` with no `type` is an audit report.
  - A missing `milestone` and a missing `pack_sha256` are each named.
  - DEC-874's four corrected cases pass with W2-02's types present.
- **Both merge-backs.**
  - `666f56d1` differs from git's merge only in `src/gov/check/schema.py`. That file is resolved to W2-02's side and holds every line W2-54 added.
  - `dbea81c8`'s tree is exactly git's merge.
  - Both carry `Task: DAEO-zflj`, `Role: orchestrator` and `Implements: DEC-441`, and neither used `-s ours`.
- **Acceptance tests.**
  - Only W2-02's suite and W1-26's one test (DEC-746) differ under `tests/acceptance/`, all by the independent test designer.
  - Every revision carries `Rewrite-Reason:`.
- **The `wbs_id` grammar.** `W2-15a`, `W2-15` and `W10-123z` are accepted. `W2-15ab`, `W2-15A`, `W2-1`, `W2-1a`, `w2-15a` and `W2-` are refused.
- **The adoption verdict.**
  - Its three values and named conditions are enforced.
  - An `accepted` condition needs its DEC or ADR owner entry.
  - Every refusal names the field and its place.

#### Rows

- **R1: on a standalone schema, top-level keywords the check cannot read (`if`/`then`, `additionalProperties`) are skipped, not refused.** No kernel schema has one today. Severity: low.
  - Ordinary work: no, because it needs a future schema edit, which that ticket's own acceptance tests would hold.
  - Consequence: fails open (for such a future schema only).
- **R2: a verdict record with no shared frontmatter passes when `common.schema.json` is missing.** Severity: low.
  - Ordinary work: no, because Copier installs the whole schema folder; it takes a broken kernel.
  - Consequence: fails open (for that broken kernel only).
- **R3: an empty conditions list makes a valid verdict.** DEC-741 sets no minimum; whether the verdict agrees with its conditions belongs to W2-52 and W2-28. Severity: low.
  - Ordinary work: yes, because an agent might write an empty placeholder list.
  - Consequence: other.
- **R4: the shared fields, and non-standalone types such as `close`, are checked for presence only, not shape.** This is W2-64's full validator (DEC-872 item 2). Severity: low.
  - Ordinary work: no, because `gov close` always writes these fields in their right shape; a wrong one takes a hand edit.
  - Consequence: other.
- **R5: patterns accept a value with a trailing newline** (Python's end-of-text anchor), now in the nested checks too. This predates the ticket. Severity: low.
  - Ordinary work: no, because ids are not written as block scalars.
  - Consequence: other.
- **R6: `src/gov/context/__init__.py` keeps a work-breakdown form without the DEC-730 suffix,** so an external reference with the id `W2-15a` is not refused as a held id. This is outside W2-02's paths. Severity: low.
  - Ordinary work: no, because it needs such an id in the external-references file.
  - Consequence: other.
- **R7: "unmeasured, not green" now applies to every mapped type.** A project whose installed kernel lacks a schema file for a type it has records of is refused at a close that touches governance files, until `copier update`. For close records nothing changes: they were an unknown type there before. Severity: informational.
  - Ordinary work: yes, because a project can run a newer gov package than its installed kernel.
  - Consequence: other (fails closed, naming the missing file; nothing lost).

### Judgement

Pass. No finding is both ordinary work and fails open or loses work. The rows go as follows:
- R1, R2, R4 and R5: the Wave 3 hardening pass or W2-64;
- R3: W2-52 and W2-28's agreement rule;
- R6: the ticket that owns `src/gov/context/`;
- R7: KPI line 3's intended fail-closed behaviour.
