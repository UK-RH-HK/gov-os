# W2-01 acceptance tests (DAEO-g0ip)

W2-01: gov close and traceability: the trailers base, the merge form, owner-accepted history, and the probe gate
after a merge-back. Profile FULL. The independent test designer wrote these tests from the ticket's KPI lines
and their sources (the WAVE_2 list and triage rows named in each line, DEC-704, DEC-734, DEC-436, DEC-490,
DEC-500, DEC-581, DEC-592), before the implementation, without reading `src/`.

## How they run

```
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
PYTHONPATH=/home/usain/gov-os-worktrees/W2-01/src \
python3 -m pytest tests/acceptance/W2-01 -q -p no:cacheprovider -rs
```

- **Which `gov` runs (DEC-732).** `w2_01_support.py` derives `REPO_ROOT` from its own location
  (`Path(__file__).resolve().parents[3]`) and `SRC = REPO_ROOT / "src"`. It reuses W1-30's support
  (`tests/acceptance/W1-30/w1_30_support.py`, imported by path as `base`), whose sandbox puts that same `SRC`
  first on every gov subprocess's `PYTHONPATH`; `w2_01_support` asserts `base.SRC == SRC`. So every
  `gov close` and `gov check` in these tests runs this worktree's `src/`, whichever checkout the tests are in.
  The fixture `code_under_test` asserts `src/gov/__init__.py` exists.
- **Repositories.** Every test builds its own git repository from scratch in pytest's `tmp_path`: a README, a
  `.gitignore`, the path map, a decision register, a capability, an ADR. The builder copies two single named
  files from this repository and nothing else: the trailers check declaration
  (`template/governance/kernel/checks/product-traceability-trailers.yaml`) and the ticket tool
  (`governance/kernel/bin/tk`). Nothing is read from or written to `governance/project/` of this repository,
  nothing is put under a `.gov-runtime/` folder, no folder of this repository is copied.
- **No network, no store build.** Nothing here needs `gov rebuild`: `gov close` loads what it needs itself,
  and `gov check` runs the declared check's own command. No test is `local_only`; no dev tier is used.
- **Deterministic.** Commit dates and authors are fixed by the builder (W1-30's `Project`); ids differ run to
  run, so the tests compare ids they made, never literal ones.
- **Through public interfaces only:** `gov close <T> --json` (API-0002 envelope), `gov check --json`, the
  check declaration's own command, and the files a close writes (the ticket, `docs/close/<T>/CL-<T>.md`).

## Files

| File | KPI lines |
|---|---|
| `test_w2_01_trailers_base.py` | 1, 6, 7 |
| `test_w2_01_merge_form.py` | 2, 8 |
| `test_w2_01_accepted_history.py` | 3, 10 |
| `test_w2_01_probe_merge_back.py` | 4, 9 |
| `test_w2_01_probe_rounds.py` | 5 |
| `w2_01_support.py`, `conftest.py` | the project builder, the fixtures, the readers |

W2-L175, W2-M263 and W2-M353 are not tested (the ticket says they need not be).

## The forms this suite fixes

The KPI lines leave some names open; DEC-734 says the README settles them. The implementation keeps these
names, or the lead changes this README and the tests together.

### The path map (`governance/project/path-map.yaml` of the project)

```yaml
trailers_base: "<commit>"          # DEC-704: commits before it are not judged
decision_register: docs/DECISION_REGISTER.md
accepted_history:                  # DEC-734
  - commit: "<full or abbreviated id>"
    decision: "DEC-nnn"
```

### Accepted history (DEC-734)

- An entry is **accepted** when the register the path map names (`decision_register`) holds `### DEC-nnn — …`
  whose status line reads `ACCEPTED (owner, …)` and whose text names the entry's commit (its first eight
  characters suffice).
- Made exact after implementation began (DEC-136; the review of round 1), so that only a genuine owner
  acceptance takes a commit out of judgement:
  - **The entry's own status line** is the line `- **Status:** …` of the entry. Text anywhere else in the entry
    (a quote above or below it, the decision text) is never its status: a PROPOSED entry that quotes
    `ACCEPTED (owner, …)` is not accepted.
  - **The owner** is the word `owner` alone, first in the parentheses: `ACCEPTED (owner-delegated to …)` and
    `ACCEPTED (owner's delegate, …)` are not the owner's acceptance.
  - **Nothing after it undoes it**: a status line `ACCEPTED (owner, …)` that goes on to say the decision is
    superseded or revoked (`… · superseded by DEC-nnn`, `…; revoked by DEC-nnn`) is not accepted.
  - **Names the commit**: the text holds a hexadecimal id (at least eight characters) that the commit's full id
    begins with. The commit's first characters inside a longer, different id do not name it.
- An accepted commit is not judged by the trailer gate of `gov close` nor by the trailers check, and it is
  **listed**: under the key `accepted_history`, a list of `{"commit": <full id>, "decision": "DEC-nnn"}`, in
  `gov close`'s result (or in its error's details when the close refuses for something else), and in the JSON
  the trailers check's command prints.
- Any other entry is **refused**: a finding with `code: "ACCEPTED_HISTORY_REFUSED"` whose text names the
  entry's commit and decision and says why, in one of four forms (the test looks for the words, lowercased):

  | Entry | Words |
  |---|---|
  | the decision is not in the register | `no entry` |
  | the decision is in the register, not ACCEPTED (e.g. PROPOSED) | `not accepted` |
  | accepted by delegation (`ACCEPTED (orchestrator, delegated …)`) | `not the owner` |
  | the owner's ACCEPTED decision names another commit | `does not name` |
  | *added (DEC-136):* `ACCEPTED (owner-delegated to …)`, `ACCEPTED (owner's delegate, …)` | `not the owner` |
  | *added:* the owner's ACCEPTED status only quoted in an entry whose own status line is PROPOSED | `not accepted` |
  | *added:* `ACCEPTED (owner, …)` then superseded by another decision | `superseded` |
  | *added:* `ACCEPTED (owner, …)` then revoked by another decision | `revoked` |
  | *added:* the commit's first characters only inside a longer, different id | `does not name` |

  The refused entry's commit stays judged, and the close refuses (or the check is red).
- Nothing else takes a commit out of judgement: an entry takes out only the commit it names.

### The trailers base

- `gov close`'s result (and the error's details when it refuses) holds `trailers_base`: the full id of the base
  it used, or `null` when the path map names none (then the whole history is judged).
- **A base move** (the path map's `trailers_base` changed by a commit, from an earlier base or from none) is
  reported by `gov close` and by the trailers check's command as an object holding `commits_out_of_judgement`
  (an integer) at any depth of the output. The number is `git rev-list --count <old>..<new>` (or
  `--count <new>` when there was no base). The report does not fail the check: the command still exits 0 and
  prints the report. A project that never recorded a base reports no move. (Package P-2 below asks the lead to
  confirm this form.)

### The merge form (DEC-436)

Restated after implementation began (DEC-136; the review of round 1 found the earlier definition, "a path whose
content in the merge is that of neither parent", too weak and too strict at once):

- A merge commit carrying `Task: <ticket>` and `Role: …` and no `Implements:` **carries nothing of its own when
  its tree is the tree that merging its parents gives** (git's own merge of the two parents, without a
  conflict). Such a merge passes the trailer gate, and is listed in the close record's `commits` like any other
  commit. Both sides changing different lines of one file, merged by git without a conflict, is such a merge.
- Any other merge is judged like any commit and refuses without `Implements:`: one that adds or changes a path
  (as before), one that removes a path the merge of its parents keeps, and one that keeps one side's whole
  version of a file both sides changed (dropping the other side's change).
- **A merge whose parents conflict** has no tree that merging its parents gives: its resolution is its own,
  whichever side's version it took. It is judged like any commit and refuses without `Implements:`.

### The probe gate

- **"The probed code"**: the files the gate guards since DEC-581, those inside the ticket's `allowed_paths` and
  its acceptance folder, and its ticket file (W1-30's settlement 33). **"Unchanged"**: each is, at the commit
  being closed, byte for byte what it is at the probed commit.
- After a merge of the integration branch into the ticket's branch and the merge-back, with the probed code
  unchanged, the gate passes. A merge that changes probed code (by hand resolution, inward or back) refuses,
  and the refusal names that merge.
- Made exact after implementation began (DEC-136): the measure is the probed code itself (DEC-505). At each
  merge after the probed commit, the probed code is what it is at the probed commit; a merge where it is not
  refuses and is named, whichever parent's version it took: a conflict on a probed file resolved to the
  integration side's version, a probed file the ticket added removed, a merge-back made from the integration
  side with git's `ours` strategy (none of the ticket's code reaches the closed head).
- Restated in the second batch after implementation began (DEC-136, DEC-739): **the merge-back that brings the
  probed commit into the closed branch is measured by the probed code whatever task it names**: the ticket's
  `Task:`, another ticket's `Task:`, or none (a plain `git merge`, as git writes it, with no trailer). One that
  drops or replaces the probed code refuses, and the refusal names it. A commit that names another ticket stays
  that ticket's (DEC-490) for every other commit, not for this merge-back.
- **Rounds (KPI 5).** Of several probe records, the record of the final code decides (its probed commit is the
  latest, nothing of the probed code changed after it). An earlier round's record (its probed commit an
  ancestor of the later one) neither passes nor refuses, in whichever order the files' names sort. A failing
  record of the final code refuses with its judgement (`judgement` in the refusal). Both readings of W2-M209
  ("only the latest record" or "each record against its own round") meet these tests.

## KPI lines → tests, and the red reasons

"Red today" quotes what the code of `src/` at the ticket's start does. "Passes today" tests are guards: the
behaviour they hold is right today and must stay right.

### KPI 1 — the trailer gate reads `trailers_base` and does not judge commits before it [DEC-704, W2-M238, W2-M250]

| Test | Today |
|---|---|
| `test_a_ticket_commit_before_the_base_does_not_refuse_the_close[creating commit without Implements]` | red: `TRAILER_MISSING`, "commit … lacks Implements: trailer" on the commit before the base |
| `…[claim commit with Task: only]` | red: same (also "lacks Role: trailer") |
| `…[an engineer commit without Implements]` | red: same |
| `test_before_and_after_the_base_only_the_commit_after_it_is_named` | red: the commit before the base is named in the refusal |

### KPI 6 — the creating commit and clones without a base are judged as the base rule says; the output names the base; a move is reported with its count [W2-M251, W2-M266]

| Test | Today |
|---|---|
| `test_the_close_names_the_base_it_used[the full id]`, `[an abbreviated id]` | red: the close's result holds no `trailers_base` |
| `test_a_project_without_a_base_is_judged_whole_and_the_close_says_no_base_was_used` | red: no `trailers_base: null` in the result |
| `test_the_traceability_check_reports_a_move_of_the_base_with_its_count[from an earlier base]`, `[from no base]` | red: the command prints nothing when green (no `commits_out_of_judgement`) |
| `test_the_close_reports_a_move_of_the_base_with_its_count[from an earlier base]`, `[from no base]` | red: the close succeeds, but its result holds no `commits_out_of_judgement` |
| `test_a_project_that_never_recorded_a_base_reports_no_move` | passes today (guard): nothing reports a move |

The creating commit before the base is held by KPI 1's first case. The creating commit *after* the base, and
a clone with no base, are package P-1: not tested beyond "the output names the base used".

### KPI 7 (failure) — a commit after the base without Task/Role/Implements refuses

| Test | Today |
|---|---|
| `test_a_commit_after_the_base_without_a_trailer_still_refuses[without Implements]`, `[without Role]`, `[without Task]` | passes today (guard) |

### KPI 2 — a merge of the integration branch in the merge form passes [W2-M165]

| Test | Today |
|---|---|
| `test_a_merge_of_the_integration_branch_in_the_merge_form_passes_the_trailer_gate[one merge]`, `[two merges]` | red: `TRAILER_MISSING`, "commit … lacks Implements: trailer" on each merge |
| `test_the_merge_form_after_more_work_on_the_branch_still_passes` | red: same |
| *added (DEC-136):* `test_a_conflict_free_merge_where_both_sides_changed_one_file_passes` | red at `4204b89d`: refused with `TRAILER_MISSING`, "commit … lacks Implements: trailer" on the merge (judged as a merge with a change of its own) |

### KPI 8 (failure) — a merge adding its own change outside the merged side refuses

| Test | Today |
|---|---|
| `test_a_merge_in_the_merge_form_that_adds_its_own_change_still_refuses[a file added inside the ticket's paths]` | passes today (guard) |
| `…[a file changed outside both sides]` (README.md) | passes today (guard) |
| `…[a file of the integration side changed]` | passes today (guard) |
| *added:* `test_a_merge_in_the_merge_form_that_removes_a_file_the_ticket_added_refuses` | red at `4204b89d`: the close succeeds ("gov close was not refused") |
| *added:* `test_a_merge_in_the_merge_form_that_keeps_one_sides_whole_file_refuses` | red at `4204b89d`: the close succeeds |
| *added:* `test_a_merge_in_the_merge_form_whose_parents_conflict_refuses` (resolved to the branch's version) | red at `4204b89d`: the close succeeds |

### KPI 3 — accepted history is listed with its DEC id and fails neither close nor check [AR-3, W2-M147, W2-L235]

| Test | Today |
|---|---|
| `test_a_ticket_commit_an_owner_decision_names_is_accepted_and_listed_by_the_close[the full id]`, `[an abbreviated id]` | red: `TRAILER_MISSING` on the claim commit the owner accepted |
| `test_accepted_history_of_a_closed_ticket_does_not_fail_a_later_close` | red: the trailers check is red on the old commit, so the close refuses |
| `test_the_check_of_a_later_commit_is_green_and_lists_the_accepted_commit` | red: the command exits 1 with `MISSING_IMPLEMENTS_TRAILER` on the accepted commit |

### KPI 10 (failure) — an entry without an ACCEPTED owner decision is refused

| Test | Today |
|---|---|
| `test_a_refused_entry_refuses_the_close_and_its_commit_stays_judged[no decision]`, `[not accepted]`, `[accepted by delegation]`, `[names another commit]` | red: the close refuses, but with no `ACCEPTED_HISTORY_REFUSED` finding |
| `test_a_refused_entry_makes_the_check_red_and_its_commit_stays_judged[…the same four…]` | red: the check is red, but with no `ACCEPTED_HISTORY_REFUSED` finding |
| `test_an_entry_takes_out_only_the_commit_it_names` | red: the accepted claim commit is judged too |
| *added (DEC-136):* `test_an_entry_without_a_genuine_owner_acceptance_refuses_the_close[owner-delegated]`, `[the owner's delegate]`, `[superseded]`, `[revoked]`, `[quoted in a proposed entry]`, `[named only inside a longer id]` | red at `4204b89d`: the close succeeds; the entry is taken as accepted |
| *added:* `test_an_entry_without_a_genuine_owner_acceptance_makes_the_check_red[…the same six…]` | red at `4204b89d`: `gov check` reports the trailers check GREEN |

### KPI 4 — probed, merged with integration and merged back passes the probe gate when the probed code is unchanged [W2-H047, W2-M202]

| Test | Today |
|---|---|
| `test_probed_then_merged_with_the_integration_branch_and_back_closes[every trailer]` | red: `PROBE_INVALID`, "ticket commit … changes src/example/feature.py after the probed commit" |
| `…[the merge form]` | red: `PROBE_INVALID` as above and `TRAILER_MISSING` on the inward merge |
| `test_probed_then_merged_with_the_integration_branch_closes_on_the_branch` | passes today (guard: the inward merge alone, closed on the branch) |
| *added (DEC-136, DEC-739):* `test_a_plain_merge_back_of_the_unchanged_probed_code_closes[merged back only]`, `[merged in, then back]` (the merge-back a plain `git merge`, no trailer) | red at `d582aee6` (both): refused with `PROBE_INVALID`, "commit … names no task and changes src/example/feature.py after the probed commit: the probe is stale", and `WORK_WITHOUT_TASK`, "… work on PROJ-prbk that no ticket measured", on the merge-back (judged against its first parent; see package P-4) |

### KPI 9 (failure) — a hand-resolved merge changing probed code refuses the probe gate

| Test | Today |
|---|---|
| `test_a_hand_resolved_merge_into_the_branch_that_changes_probed_code_refuses` | passes today (guard) |
| `test_a_merge_back_that_changes_probed_code_by_hand_refuses[a probed file changed]`, `[a file added inside the ticket's paths]` | passes today (guard) |
| *added (DEC-136):* `test_a_merge_back_that_drops_probed_code_refuses_and_names_the_merge_back[<how>-<layout>]`: how ∈ {`a conflict on a probed file resolved to the integration side`, `a probed file the ticket added removed`, `made from the integration side with the ours strategy`} × layout ∈ {`merged back only`, `merged in, then back`} (KPI 4's layout); the wrong merge is always the merge-back | red at `4204b89d` (all six): the close succeeds ("gov close was not refused") |
| *added:* `test_a_merge_into_the_branch_resolved_to_the_integration_side_refuses` (inward, then merged back) | passes at `4204b89d` (guard for "inward") |
| *added (DEC-136, DEC-739):* `test_a_merge_back_naming_no_task_or_another_that_drops_probed_code_refuses_and_names_it[<names>-<how>-<layout>]`: names `no task` (a plain `git merge`, no trailer) × the three ways above × both layouts (6); names `another ticket's task` (`Task: PROJ-othr`) × the three ways, `merged back only` (3), and with the `ours` strategy, `merged in, then back` (1); the wrong merge is always the merge-back | red at `d582aee6` (all ten): the close succeeds ("gov close was not refused") |

### KPI 5 — a reopened FULL ticket with an earlier-round record and a passing later one passes [W2-M209, W2-L111]

| Test | Today |
|---|---|
| `test_a_reopened_ticket_with_an_earlier_record_and_a_passing_later_one_closes[the later record under a round name]` | red: `PROBE_INVALID`, "ticket commit … changes src/example/feature.py after the probed commit" (round one's record) |
| `…[the earlier record under a round name]` | red: same |
| `test_a_fix_round_after_a_failing_probe_closes_on_the_passing_record_of_the_fix` | red: `PROBE_INVALID`, "the probe's judgement is 'fail', not pass or passed" (round one's record) |
| `test_a_reopened_ticket_with_only_the_earlier_record_still_refuses` | passes today (guard) |
| `test_a_failing_later_record_beside_a_passing_earlier_one_refuses[the later record under a round name]` | passes today (the gate happens to read the failing record first) |
| `…[the earlier record under a round name]` | red: refused, but by round one's record ("changes … after the probed commit"), not by the final record's judgement; the gate ends at its first finding |

W1-30's `test_a_failing_probe_record_beside_a_passing_one_refuses` (two records of the same final code) is not
reversed and stands. No earlier ticket's test is reversed by these KPI lines; none was changed.

## Counts at the red run

46 tests: 33 red, 13 pass today (the guards listed above, and one ordering of KPI 5's failing-later case).
By file: trailers base 11 red / 4 pass; merge form 3 / 3; accepted history 13 / 0; probe merge-back 2 / 4;
probe rounds 4 / 2.

## Added after implementation began (DEC-136)

The independent review of round 1 (`dbdb4d4e`) found behaviours the tests missed. A fresh test designer added
them, within the KPI lines, without reading `src/`; red run against the implementation at `4204b89d`.

| Added | KPI line | Red at `4204b89d` |
|---|---|---|
| `test_a_merge_back_that_drops_probed_code_refuses_and_names_the_merge_back` (6 cases) | 9 (failure), 4's layout | 6 red: the close succeeds |
| `test_a_merge_into_the_branch_resolved_to_the_integration_side_refuses` | 9 (failure) | passes (guard) |
| `test_a_conflict_free_merge_where_both_sides_changed_one_file_passes` | 2 | red: `TRAILER_MISSING` on the merge |
| `test_a_merge_in_the_merge_form_that_removes_a_file_the_ticket_added_refuses` | 8 (failure) | red: the close succeeds |
| `test_a_merge_in_the_merge_form_that_keeps_one_sides_whole_file_refuses` | 8 (failure) | red: the close succeeds |
| `test_a_merge_in_the_merge_form_whose_parents_conflict_refuses` | 8 (failure) | red: the close succeeds |
| `test_an_entry_without_a_genuine_owner_acceptance_refuses_the_close` (6 cases) | 10 (failure) | 6 red: the close succeeds |
| `test_an_entry_without_a_genuine_owner_acceptance_makes_the_check_red` (6 cases) | 10 (failure) | 6 red: the check is GREEN |

23 tests added: 22 red, 1 guard. The suite now holds 69 tests; the 46 earlier ones all still pass at `4204b89d`.

**Forms changed, each with its reason:**

- *The merge form* (above): restated as "its tree is the tree that merging its parents gives", and a merge whose
  parents conflict is judged like any commit. Reason: behaviours 2 and 3 of the review; the earlier wording
  passed a merge that removed the ticket's file or dropped one side's change, and refused a conflict-free merge
  where both sides changed one file.
- *Accepted history* (above): the entry's own status line, the word `owner` alone, nothing after it undoing it,
  naming by a prefix of the commit's id; four reason words added (`not the owner` and `not accepted` for new
  forms, `superseded`, `revoked`). Reason: behaviour 4 of the review.
- *The probe gate* (above): the measure is the probed code at each merge after the probed commit, whichever
  parent's version a merge took. Reason: behaviour 1 of the review.

**Existing tests changed:** none; no earlier assertion is reversed by the restated forms. `w2_01_support.py`
gained two helpers on new lines (`merge_by_hand`: a merge that may also remove paths or use git's `ours`
strategy; `content_at`: a file's text at a commit); no earlier line of it changed.

### Second batch: the merge-back that names no task, or another ticket's (DEC-136, DEC-739)

The second and last review (`docs/probes/DAEO-g0ip/PR-DAEO-g0ip.md`, probed `f74b361b`, judgement fail) found
that a merge-back naming no task, or another ticket's task, that drops or replaces the probed code passes the
close. The owner allowed one extra round for it (DEC-739, beyond DEC-413). A fresh test designer added it as
described behaviour, within KPI 4 and KPI 9, without reading `src/`; red run against the implementation at
`d582aee6`.

| Added | KPI line | Reason | Red at `d582aee6` |
|---|---|---|---|
| `test_a_merge_back_naming_no_task_or_another_that_drops_probed_code_refuses_and_names_it` (10 cases) | 9 (failure), alone and in 4's layout | DEC-739; the second review's first finding | 10 red: the close succeeds |
| `test_a_plain_merge_back_of_the_unchanged_probed_code_closes` (2 cases) | 4 (guard) | DEC-739: KPI 4's success line in the most common merge layout (131 of the last 300 merges on `main` carry no `Task:`) | 2 red: `PROBE_INVALID` and `WORK_WITHOUT_TASK` on the merge-back (package P-4) |

12 tests added: all 12 red. The suite now holds 81 tests; the 69 earlier ones all still pass at `d582aee6`.

**Forms changed, each with its reason:** *the probe gate* (above): the sentence "A commit that names another
ticket stays that ticket's (DEC-490)" is restated so that it holds for every commit but the merge-back that
brings the probed commit into the closed branch, which is measured by the probed code whatever task it names.
Reason: DEC-739.

**Existing tests changed:** none. `test_w2_01_probe_merge_back.py` gained the two tests and one helper
(`_merged_back_naming`) on new lines; `w2_01_support.py` is unchanged.

## Packages for the lead

- **P-1 — the creating commit after the base, and a clone with no base (KPI 6).** Reading A: the
  ticket-creating commit is exempt from `Implements:` (it has nothing to implement yet). Reading B: it is judged
  like any commit after the base. A clone whose path map names no base: is the whole history judged (today's
  rule, held by `test_a_project_without_a_base_is_judged_whole_…`), or is a base derived? Not tested beyond
  "the output names the base used" until the lead says which. Recommendation: B (DEC-704 names no exemption);
  confidence medium. Reversible: one parametrize row.
- **P-2 — the form of the base-move report.** Fixed above (`commits_out_of_judgement`, the rev-list count, in
  the check command's output and in the close's result, not failing the check). Confirm or rename; the change is
  in `w2_01_support.MOVED_COUNT_FIELD` and this README.
- **P-3 — `gov check` drops the check's extra keys.** Through `gov check`, only `findings` and the reason
  survive, and any finding makes a hard-block check red. So the accepted listing and the base report are held
  in the check command's own output, and only the status (GREEN/RED) through `gov check`. Showing the listing
  in `gov check --json` needs a runner change outside this ticket's paths; recommend a follow-up in the runner's
  ticket.
- **P-4 — the task-less rule and a plain merge-back of the unchanged probed code (second batch).** DEC-490
  says a commit naming no task that changes a path inside the ticket's allowed paths refuses (work no ticket
  measured) and, after the probed commit, makes the probe stale. Today a plain merge-back is judged against its
  first parent, so bringing the probed code unchanged counts as such a change, and KPI 4's guard is refused. The
  guard holds that the merge-back of exactly the probed code is measured (by the probe) and not "after" it
  (DEC-505, DEC-739). Option (a): the task-less rule measures a merge-back that brings the probed commit by the
  probed code, as the probe gate does (the guard as written; the rule stands for every other task-less commit).
  Option (b): a plain merge-back refuses until it carries the ticket's `Task:` (the guard is dropped; 131 of the
  last 300 merges on `main` would refuse). Recommendation: (a), confidence medium-high. Reversible: the guard
  is one test; cost of (a) is inside the fix the ten refusal cases already ask for.

## Not held

- The path-map schema does not name `accepted_history` (it is in W2-02's paths); no test asks it to.
- An entry reading `ACCEPTED (owner, …)` committed under `Role: orchestrator` (who committed the register
  entry, AR-7) is not held: the KPI line names the status, not the committer.
