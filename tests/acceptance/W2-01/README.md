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

A merge commit carrying `Task: <ticket>` and `Role: …` and no `Implements:`, whose tree is the result of
merging its parents with nothing of its own, passes the trailer gate. It is listed in the close record's
`commits` like any other commit. A merge that adds its own change (a path whose content in the merge is that
of neither parent) is judged like any commit and refuses without `Implements:`.

### The probe gate

- **"The probed code"**: the files the gate guards since DEC-581, those inside the ticket's `allowed_paths` and
  its acceptance folder, and its ticket file (W1-30's settlement 33). **"Unchanged"**: each is, at the commit
  being closed, byte for byte what it is at the probed commit.
- After a merge of the integration branch into the ticket's branch and the merge-back, with the probed code
  unchanged, the gate passes. A merge that changes probed code (by hand resolution, inward or back) refuses,
  and the refusal names that merge.
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

### KPI 8 (failure) — a merge adding its own change outside the merged side refuses

| Test | Today |
|---|---|
| `test_a_merge_in_the_merge_form_that_adds_its_own_change_still_refuses[a file added inside the ticket's paths]` | passes today (guard) |
| `…[a file changed outside both sides]` (README.md) | passes today (guard) |
| `…[a file of the integration side changed]` | passes today (guard) |

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

### KPI 4 — probed, merged with integration and merged back passes the probe gate when the probed code is unchanged [W2-H047, W2-M202]

| Test | Today |
|---|---|
| `test_probed_then_merged_with_the_integration_branch_and_back_closes[every trailer]` | red: `PROBE_INVALID`, "ticket commit … changes src/example/feature.py after the probed commit" |
| `…[the merge form]` | red: `PROBE_INVALID` as above and `TRAILER_MISSING` on the inward merge |
| `test_probed_then_merged_with_the_integration_branch_closes_on_the_branch` | passes today (guard: the inward merge alone, closed on the branch) |

### KPI 9 (failure) — a hand-resolved merge changing probed code refuses the probe gate

| Test | Today |
|---|---|
| `test_a_hand_resolved_merge_into_the_branch_that_changes_probed_code_refuses` | passes today (guard) |
| `test_a_merge_back_that_changes_probed_code_by_hand_refuses[a probed file changed]`, `[a file added inside the ticket's paths]` | passes today (guard) |

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

## Not held

- The path-map schema does not name `accepted_history` (it is in W2-02's paths); no test asks it to.
- An entry reading `ACCEPTED (owner, …)` committed under `Role: orchestrator` (who committed the register
  entry, AR-7) is not held: the KPI line names the status, not the committer.
