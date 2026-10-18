# W2-52 Acceptance Tests — the lite A7 and A10 stage records

Ticket: `DAEO-siiz` · Profile: FULL · Covers: **CAP-44.f** (the lite A7 and A10 gates) and **CAP-44.h** (the lite
verdict's conditions (4), (6) and (9))

The Independent Test Designer (MR-3) wrote these tests before implementation. They come from the ticket's KPI
lines and Contract v4.2's CAP-44, CAP-44.f, CAP-44.h and CAP-44.k. Further sources are W2-49's CIT-P §3.2 and its
row on W2-24, W2-02's `adoption-verdict.schema.json` (read with `git show w2/W2-02:…`; nothing of it is copied
or merged), DEC-741 (answers F, H, I), DEC-722, DEC-090, DEC-006, DEC-738 item 1, DEC-449, DEC-454 and DEC-490.
The public behaviour of `gov adopt --lite`, `gov rebuild` and `gov doctor` was read from W1-41's README and
support and from what the commands answer today. No private part of an implementation was read, and no earlier
ticket's test was rewritten.

## Run

```
PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -m pytest tests/acceptance/W2-52 -q -p no:cacheprovider -rs
```

**65 cases in 5 files.** They use the standard library, PyYAML, pytest, and the support of W1-07 and W1-41. No
network and no model are used. The run takes 2 to 7 minutes, depending on the machine's load: the A10 gate
rebuilds the derived state.

**Which code runs.** Every `gov` the cases start is this worktree's own `src/`. W1-07's support writes the
console script that `[project.scripts] gov` names, and W1-41's `environment` puts
`/home/usain/gov-os-worktrees/W2-52/src` on the child's `PYTHONPATH`. `test_the_cases_run_this_worktrees_gov`
holds this: a child started in the cases' environment imports `gov` from under this worktree's `src/`. For the
suite process, the run line sets the same `PYTHONPATH`, and
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -c "import gov; print(gov.__file__)"` prints
`/home/usain/gov-os-worktrees/W2-52/src/gov/__init__.py`.

## Red run (before implementation)

Measured on `29bef106` with this suite on top, using the run line above: **58 failed, 7 passed in 158 s**, with
no skip (`sqlite_vec` is installed here).

- **54 cases are red because `gov adopt --lite --stage` does not offer A7 or A10.** Today it accepts only A0
  to A6 and A8, and that choice is where every gate run first stops. argparse answers with exit code 2 and
  `invalid choice: 'A7'` (or `'A10'`), and `assert_stage_taken` reports "gov adopt --lite does not take
  --stage A7". The count is 32 for A7 (28 in `test_w2_52_a7_gate.py`, 4 in `test_w2_52_verdict_conditions.py`)
  and 22 for A10 (`test_w2_52_a10_gate.py`). No failing case can be met by a refusal of an unknown stage:
  `assert_never_passes` fails on the usage error too.
- **4 cases are red because the adopt skill does not name the steps** (`test_w2_52_skill.py`). The skill says
  that A7 and A10 are Wave 3, and no block of it names A7 or A10 with the Independent Auditor and what each
  checks.
- **7 cases are green and stay green.** One is the W2-24 row
  (`test_a8_runs_after_a6_without_an_a7_record`). Another is the code check (`test_the_cases_run_this_worktrees_gov`).
  One guards the fixture (`test_the_fixture_auditors_record_is_readable`). The other four are the rows of
  `test_the_cases_read_conditions_as_cap_44_h_says`, which state the CAP-44.h rule the cases use.

**The cases can be met together.** A throwaway stand-in, kept in the designer's scratchpad and never in the
tree, wraps this worktree's `gov` and adds two gates written to this README. Against it, all 62 cases outside
the skill file passed. A plausible skill text, also kept outside the tree, passed the 4 skill cases, while
today's text fails them.

## The project every case builds

The cases use W1-41's "harbour" project (`build_project`). It has three move batches, every legacy rule file,
the memory store and the chat database retired, and the extraction record of the chat database. It also holds
the kernel's two canary declarations (`template/governance/kernel/canaries/lexical.yaml` and `semantic.yaml`),
copied one by one to `governance/kernel/canaries/` as an installed kernel holds them. The canary's phrase
therefore stands in the project, so each index's canary can hit (CAP-55, W1-22).

Two session fixtures carry the project forward, once each:

- `after_a6`: A0 to A6, with W1-41's stages as built and its A5 verdict.
- `after_a8`: A8 run straight after A6, with no A7. This is W2-24's fixture adoption.

Each case copies one of them into its own temporary folder, without `.gov-runtime/`, and gets a new sandbox. The
copy is of a temporary project the fixture built, never of this repository.

**No model.** The semantic index is built through a stand-in embedding endpoint on `127.0.0.1`. It uses W1-22's
deterministic word-hash vectors. `sqlite_vec` is reached through a folder that holds one link to the installed
package, as in W1-22's support. One case keeps W1-41's dead loopback address so that the semantic canary misses.
A case whose pass needs vectors is skipped, with that reason, where `sqlite_vec` is not installed.

## The interface the cases hold (readings; the engineer may dispute any point through the lead)

The KPI lines leave the interface open. Each point below is this suite's reading, chosen as close to the sources
and to the A5 precedent (W1-41, "The A5 verdict") as it could be.

1. **One stage per call, as for every stage.** The calls are `gov adopt --lite --stage A7 --verdict <path>
   [--json] [--session <id>]` and the same with `A10`. `<path>` is the Independent Auditor's committed record
   in the project (the A5 precedent: `--verdict`). The session that ran the stages runs the gate
   (`adopter-001`).
2. **What each gate stands on.** A7 stands on the A6 record, and A10 on the A8 record. A10 does not need an A7
   record: v4.2's A10 checks name A8, the rebuild and the canaries, and W2-24's row has A8 run without A7. A8
   still runs after A6 with no A7 record, and it runs after a passing A7 too.
3. **The auditor's record** is a Markdown record with frontmatter `id`, `type: evidence`, `status`,
   `state_class: EVIDENCE`, `stage: A7` (or `A10`), `verdict`, `auditor_session` and `checked`. `checked` is a
   list of `{record, sha256}` naming each stage record the auditor checked, with the sha256 of that record as it
   stands at HEAD. A7 checks the A3, A4, A5 and A6 records; A10 checks the A8 record. Only `verdict: pass`
   passes (DEC-490). The record is committed with `Role: independent-auditor` (DEC-454), and its
   `auditor_session` is none of the sessions that ran the stages (CAP-44.f: "a fresh Independent Auditor
   session"). This is the A5 rule (`path_map_hash`) applied to each record v4.2 names. The cases write it at
   `audit/adoption/a7-verdict.md` and `a10-verdict.md`. **The gate never passes** when this record does not
   exist, is not committed, cannot be read, states no `verdict`, is for another stage (the A5 verdict given to
   A7 or A10), was not committed by the auditor, comes from the adopter's session, leaves out a record the gate
   checks, or gives a hash that is not that record's.
4. **The gate also checks the project itself**, beyond the auditor's word (CAP-44.f: "A7 checks …", "A10
   checks …"). A gate never passes when what v4.2 says it checks is absent or failing:
   - **A7.** Every move of the A4 plan is in the project as A6 made it: the target is there and the origin is
     gone. The plan is the one A6 executed. The A3 path map is the one A5 reviewed (A5's `path_map_hash`).
   - **A10.** Every file A8 retired is still out of the active tree, and the record that holds what was
     extracted from the chat database is still there. The derived state is rebuilt from git: the cases delete
     `.gov-runtime/` before the gate, and the gate's record carries the digest that `gov rebuild` gives at the
     commit it checked (CAP-20). The canary of each index (`lexical`, `semantic`) hits; a miss is
     FACET_UNAVAILABLE (CAP-55).
5. **Its own stage record.** The gate commits a record of its own in the adoption run's own folder, the folder of
   the A0 record (today `governance/adoption/`). It lies at a path no other stage's record has, and the tree
   is clean afterwards. The record has `type: evidence`, `state_class: EVIDENCE`, a `status`, a record `id`
   and `stage: A7` or `A10`. The gate changes no file that was there (never over another stage's record),
   moves nothing and retires nothing. On a pass the envelope reads `ok: true`, exit code 0, `result.stage` and
   `result.record`.
6. **What the record names.** For A7: the paths of the A3, A4, A5 and A6 records, the auditor's record and its
   session. For A10: the A8 record, the auditor's record and its session, the rebuild's digest, the canaries,
   and each index by name. Both say what stays for Wave 3 (CAP-44.k; CIT-P §3.2): the words "Wave 3" (or
   "W3") and the ids `CAP-44.k` and `CAP-47.a`, and for A10 also `A9` and `CAP-49`. The text is matched in any
   case of letters, anywhere in the record.
7. **The conditions (W2-02's form; DEC-741 I (ii)).** The record gives one or more objects, at any depth of its
   frontmatter, with `name`, `source` and `state` (and `owner_entry` only where accepted), and no other key.
   The key that holds them is the implementation's choice. One condition's `name` names the gate (`A7` or
   `A10`). Each `source` names `CAP-44.f` or `CAP-44.h`. A passing gate's conditions are all `met`. **A gate
   never gives `accepted`**: only the owner accepts an exception (CAP-44.h; DEC-741 F).
8. **A gate that fails writes a failing record** (the failure line). The record is committed as in point 5,
   with at least one condition `not met` and none `accepted`, so a verdict that reads it cannot be
   ADOPTED_HEALTHY. The answer or the record names what failed. This holds for the auditor's `fail`,
   `inconclusive` and `pass_with_findings`, and for each check of point 4 that fails. **The envelope of a
   failing gate is left open** (`ok: false` with exit code 1, 3 or 4, or `ok: true`): the record is the
   evidence.
9. **Where the auditor's record is not a valid pass** (point 3), or the record a gate stands on is missing
   (point 2), the gate may either refuse or write a failing record. A refusal reads `ok: false`, exit code 1,
   3 or 4, writes nothing and names the cause. Neither may pass.
10. **How the verdict reads the records.** A verdict lists named conditions (W2-02), and CAP-44.h makes it
    ADOPTED_HEALTHY only when every lite condition is met. The two records each give the condition a verdict
    carries for its gate. The verdict itself is a fresh auditor's (W2-28, W2-30), so a missing A7 or A10 record
    is held where that auditor's method is written: the adopt skill says a missing gate record is a condition
    `not met`. See package P-1.
11. **The skill** (`template/governance/kernel/skills/adopt/SKILL.md`) is read as text in blocks (a list item
    with its continuation lines, or a paragraph). One block names A7, the auditor, A6, A3, A4 and A5. One block
    names A10, the auditor, A8, the rebuild ("rebuil…") and the canaries ("canar…"). For each gate, one block
    names it with "not met" and with "missing", "absent", or "no … record" / "without … record".

## KPI lines → tests

| KPI line | Tests | Red reason |
|---|---|---|
| **Success 1**: `gov adopt` runs the lite A7 and A10 gates; each writes its own stage record with its evidence [CAP-44.f] | `a7_gate`: `test_a7_passes_on_the_auditors_pass_and_is_recorded_as_its_own_stage`, `test_a7_writes_over_no_other_stages_record`; `a10_gate`: `test_a10_passes_on_the_auditors_pass_and_is_recorded_as_its_own_stage`, `test_a10_writes_over_no_other_stages_record`; every `assert_passed` and `assert_failing_record` (record committed, own path, own folder, nothing else changed) | `--stage` does not offer A7/A10 |
| … the adopt skill names both steps | `skill`: `test_the_adopt_skill_names_the_a7_step`, `test_the_adopt_skill_names_the_a10_step` | the skill names no such step |
| **Success 2**: each gate checks what v4.2 says. A7: the A6 migration against the A3 path map and the A4 plan reviewed at A5, by a fresh auditor | `a7_gate`: `test_a7_record_names_what_it_checked`; `test_a_migration_the_project_no_longer_holds_fails_a7` (2: moved back, target gone); `test_a_path_map_changed_after_its_a5_review_fails_a7`; `test_a_plan_that_is_not_the_one_executed_fails_a7`; `test_an_auditors_record_that_does_not_cover_a_checked_record_never_passes` (4: A3, A4, A5, A6); `test_an_auditors_record_about_another_a6_record_never_passes`; `test_an_auditors_record_not_committed_by_the_independent_auditor_never_passes` (3); `test_an_auditors_record_from_the_session_that_ran_the_stages_never_passes` | `--stage` does not offer A7 |
| … A10: the A8 extraction and retirement, the derived state rebuilt from git, the canary of each index (CAP-55), by a fresh auditor | `a10_gate`: `test_a10_record_names_the_a8_record_and_the_auditor`, `test_a10_record_carries_the_digest_of_the_derived_state_rebuilt_from_git`, `test_a10_record_names_the_canary_of_each_index`; `test_a_retirement_the_project_no_longer_holds_fails_a10` (3: rule file, memory store, chat database); `test_an_extraction_the_project_no_longer_holds_fails_a10`; `test_a_lexical_canary_miss_fails_a10`; `test_a_semantic_canary_miss_fails_a10`; `test_an_auditors_record_that_does_not_cover_the_a8_record_never_passes`; `test_an_auditors_record_about_another_a8_record_never_passes`; `test_an_auditors_record_not_committed_by_the_independent_auditor_never_passes`; `test_an_auditors_record_from_the_session_that_ran_a8_never_passes` | `--stage` does not offer A10 |
| … each record names what stays for Wave 3 | `test_a7_record_names_what_stays_for_wave_3`, `test_a10_record_names_what_stays_for_wave_3`, and the failing records of `test_an_auditor_who_does_not_pass_the_migration_gets_a_failing_a7_record` and `test_an_auditor_who_does_not_pass_the_memory_gets_a_failing_a10_record` | as above |
| **Success 3**: the adoption verdict (W2-02's type) reads both records as named conditions [CAP-44.h] | `a7_gate`: `test_a7_record_gives_a_met_condition_a_verdict_can_carry`; `a10_gate`: `test_a10_record_gives_a_met_condition_a_verdict_can_carry`; `verdict_conditions`: `test_the_a7_and_a10_records_each_give_a_condition_the_verdict_carries`, `test_a_verdict_reading_both_passing_records_can_be_healthy`, `test_the_conditions_say_where_they_come_from`; the rule: `test_the_cases_read_conditions_as_cap_44_h_says` (4, green) | `--stage` does not offer A7 (the protocol-order fixture stops at A7) |
| **Failure**: a lite gate that fails writes a failing record, and the verdict cannot be ADOPTED_HEALTHY | `test_an_auditor_who_does_not_pass_the_migration_gets_a_failing_a7_record` (3: fail, inconclusive, pass_with_findings), `test_an_auditor_who_does_not_pass_the_memory_gets_a_failing_a10_record`, and every failing case of the Success 2 rows (`assert_failing_record`: committed, a condition `not met`, none `accepted`, the CAP-44.h rule not healthy) | `--stage` does not offer A7/A10 |
| … a missing record is a named failure, never healthy | the record a gate stands on: `test_a_missing_a6_record_is_a_named_failure_of_a7`, `test_a_missing_a8_record_is_a_named_failure_of_a10`; the auditor's record: `test_an_auditors_record_that_does_not_exist_never_passes` (A7, A10), `test_an_auditors_record_written_and_not_committed_never_passes` (A7); the gate's own record read by the verdict: `skill`: `test_the_adopt_skill_says_a_missing_gate_record_is_a_condition_not_met` (2) — package P-1 | `--stage` / the skill |
| … (in its spirit) an unreadable or partial record is never read as healthy | `test_an_auditors_record_that_cannot_be_read_never_passes` (3: broken YAML, no frontmatter, no `verdict`), `test_a10_with_an_unreadable_auditors_record_never_passes`, `test_the_a5_verdict_given_to_a7_never_passes`, `test_the_a5_verdict_given_to_a10_never_passes` | `--stage` does not offer A7/A10 |
| **Unchanged**: A0 to A6 and A8 keep their behaviour; A8 runs after A6 without an A7 record (W2-24's row) | `unchanged`: `test_a8_runs_after_a6_without_an_a7_record` (green); the two session fixtures run A0 to A6 and A8 through W1-41's `ok`; `verdict_conditions`: `test_a8_runs_after_a7` | green / `--stage` does not offer A7 |
| DEC-732: the code under test is this worktree's | `unchanged`: `test_the_cases_run_this_worktrees_gov` (green) | — |

### Covers → tests

| Covers | Tests |
|---|---|
| CAP-44.f | everything in `test_w2_52_a7_gate.py` and `test_w2_52_a10_gate.py`; `test_w2_52_skill.py` (steps) |
| CAP-44.h | `test_*_record_gives_a_met_condition_a_verdict_can_carry` (2); all of `test_w2_52_verdict_conditions.py`; every failing-record case (conditions `not met`, never `accepted`, not healthy); `test_the_adopt_skill_says_a_missing_gate_record_is_a_condition_not_met` (2); condition (9): `test_a10_record_carries_the_digest_of_the_derived_state_rebuilt_from_git` |

## Not covered here, or left open

- **The verdict record itself.** Whether it is ADOPTED_HEALTHY, which conditions it lists, and whether it calls
  itself lite are for W2-02's type and the auditors of W2-28 and W2-30. The cases hold what the two records
  give it.
- **The envelope of a failing gate** (point 8), and which of refusing or writing a failing record a gate does
  for an invalid auditor's record (point 9).
- **Running a gate again** (a failing A7, then a new auditor's pass) is not covered. Neither is whether A7 may
  run after A8.
- **Whether A7's and A10's auditor sessions may be one session**, or the A5 auditor's. CAP-44.f says "a fresh
  … session" for each; the cases hold only that it is not a session that ran the stages.
- **A rebuild from git that fails.** No public way makes `gov rebuild` fail in the same way whatever the
  implementation, for example whether the gate rebuilds in place or in a fresh clone. The cases hold the
  rebuild positively (the derived state is deleted, and the digest matches); the auditor's `fail` covers the
  failing side.
- **The b-dev tier.** No `local_only` case is written: the KPI lines do not name b-dev, and W1-41's two dev-tier
  cases stay as they are.

## Earlier tests

None is rewritten, and none needs to be. No earlier case holds that `--stage` refuses A7 or A10. W1-41's
`STAGES` lists the eight stages W1-41 delivered, and its cases do not run A7 or A10. W1-36 holds the skill's
form; the skill's new steps must keep it (at most 2,500 tokens of body).

## Packages (in full in the designer's return)

- **P-1. How a verdict names a missing A7 or A10 record.** The failure line says "a missing record is a named
  failure, never healthy". This ticket's paths hold the gates, the stages and the skill; they hold no verdict
  writer and no command that lists a run's conditions. The cases chose this reading: the records give the
  conditions, and the skill tells the verdict's auditor that a missing gate record is a condition `not met`.
  The alternative is a reader in `lite_gates.py` with a command that lists a run's lite conditions and names a
  missing gate record as `not met`. That needs an interface decision, and perhaps W2-28's paths.
