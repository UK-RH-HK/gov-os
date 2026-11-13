---
type: probe
task: DAEO-qz4p
reviewer_session: 03dbe517-ebb8-4ccb-a20f-4e69b6eca79a
implementer_session: a82f27e5-55cd-4b14-847c-0bf134c67280
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 03ccf53d74b8e4793208df795301db8144317765
decisions_applied: [DEC-1101, DEC-1120, DEC-1112, DEC-1113, DEC-866, DEC-105, DEC-1073]
---

# Probe record: W2-173, the launch script's follow-ups for the memory audit

A fresh independent-auditor session (`03dbe517-ebb8-4ccb-a20f-4e69b6eca79a`) ran on Opus at high effort, class C3, with read-only tools. It probed head `03ccf53d74b8` of `w2/W2-173` and wrote nothing in the tree, which was clean when it started and when it finished. The implementers were:
- engineer eng-1 (`a82f27e5-55cd-4b14-847c-0bf134c67280`): the script and its schemas;
- test designer td-2: W2-149's support fixtures (`009642705`);
- engineer eng-2 (`3e07607e-d91e-41f4-88f8-521c69fec9bf`): W2-149's two unit cases (`d37564498`).

The findings were judged against ADR-0001's threat model (DEC-801). A finding counts toward a round only if an honest agent can hit it in ordinary work and it fails open or loses work. This is round 1, and its verdict is PASS.

## What was probed

- **S1 (effort).**
  - The check runs at stage 10, right after `resolve_brief` and before anything is built. Any value that is not one of the five strings refuses 10.
  - `session_flags` adds `--effort <v>` only when the brief names one, so the argv is the base sequence when there is none. The canary and the session both receive the flag.
  - The effort is recorded in `WALL.json` and in the counts (null before stage 10).
- **S2 (stop word).**
  - A writer or checker result whose `stopped` is one of the six words other than `none` sets `out.stopped` and refuses 21. This happens before the schema check and before delivery.
  - `none`, or no `stopped` at all, goes through as before.
  - Set-up A and the auditor are untouched. Both result schemas gain `stopped` as an optional property.
- **S3 (`check_notes`).**
  - It checks the heading, `## Questions`, one line per staged id in id order (five fields each), `## The set` and its five line prefixes.
  - The result's counts must equal the lines' counts.
  - The check runs before `deliver_file`.
- **S4 (`check_classes`).**
  - The keys must be exactly the ids in `input/misses.jsonl`. Each class must be one of the five, and each reason must be one line of at most 200 characters.
  - The five counts must match the classes. A repeated key or a JSON constant is refused.
  - The delivery and the `AUDITS.log` line both come after the check.
- **S5 / F3.**
  - The script's diff against `2f98aecbc` outside the four changes is limited to three things: the docstring, a restructure of `session_flags` and of the delivery `except` block that does not change behaviour, and `read_plain` reading the file before the check.
  - `CODES` is unchanged. No template file, path map, guard, approved list or brief changed.
- **F2.** Every refusal (21, and the 20s from the form checks) is raised before any write to the set's or the audit's folder.
- **F4.** `git diff --name-only 00a9e4ed9 03ccf53d74b8` lists 16 paths. Each matches the ticket's `allowed_paths`, or falls under the test designer's `tests/acceptance/W2-173/**`.
- **W2-149's tests.** td-2's and eng-2's changes replace planted products only, in checker.md §6's form and auditor.md §2 and §6's form. No assertion was removed or weakened.
- **Mutations.** The reviewer ran 12 planted mutations on a `git archive` copy of the head. Every one was caught by at least one suite. S3c (the set-line prefixes not checked) was caught by the unit file only (F3 below).

## What it found (4, all minor; none blocking, none fail open, none lose work)

| id | KPI | where | finding | the lead's triage |
|---|---|---|---|---|
| F1 | S5 | `indep-schemas/indep-counts.schema.json:17` | `--counts-only` on a counts.json written before this change (no `effort`) exits 17. At the base it printed the object. | Fails closed, and the file stays on disk. `effort` is required so that W2-149's closed-schema check (`required == properties`) holds. This is the risk the evidence named. **The CTO rules:** (a) required by design, no change (cost 0); (b) make `effort` optional, which needs W2-149's schema case revised (one small batch). Recommendation: (a). Readers of set-up A's earlier counts (`round1_files`) do not use the schema. |
| F2 | S4 | `indep_launch.py:1648` | A classes entry with a third key, or an empty `reason`, is delivered. auditor.md §6's form is `{class, reason}`, with one sentence as the reason. | Class and counts are still checked; the extra key lands in the audit folder. A follow-up row: refuse a key other than `class`/`reason` and an empty reason. A fix starts with a test-design batch (DEC-136). |
| F3 | S3 | `tests/acceptance/W2-173/test_w2_173_notes.py` | With the set-line prefix check removed, every acceptance case passes; only the unit file catches it. | A test gap, not runtime behaviour. A follow-up row: an acceptance case for a wrong `## The set` line. |
| F4 | S2 (out of scope) | `indep-briefs/memory-audit/checker.md:153` | A checker that stops as its brief §7 says is refused 20, not 21: the brief names no `stopped` word. | The evidence named this too. It fails closed. The fix belongs to the next revision of the memory-audit briefs (MEMORY-AUDIT-1, class (O), the owner's). |

## Verification at the probed head's parent (`d37564498`, the code head)

- `gov accept W2-173`: pass, 79/0/0.
- `gov accept W2-149`: 174/0/35. Every line passes except success-26, whose only 2 cases are live and run by the CTO.
- W2-149's and W2-173's unit files with `--optin lifted,breadth`: 161 passed.
- `lead_verify` (the whole suite, in parallel): 4072 tests, 7 failed, 41 skipped. All 7 are base reds:
  - six W2-96 signal cases (P-W2-121-5; W2-177);
  - `test_w2_02_green_here::test_core_schema_is_green_on_this_repository`, on `.tickets/DAEO-1k7y.md` (`type: bug`, from `518772b5c`).
- `03ccf53d74b8` adds only the evidence file.
