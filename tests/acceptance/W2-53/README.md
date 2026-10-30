# W2-53 acceptance tests (DAEO-7rr2)

W2-53: the probe gate measures every later merge that holds a FULL ticket's probed commit against git's own merge
of its parents (DEC-750, DEC-754, P-5 (c)). DEC-757 widens the ticket with three more things:

- the owner-accepted known-red list, `accepted_reds`, which works as a ratchet;
- the integration side's edits of a ticket file;
- the named load-sensitive quarantine, `load_sensitive`.

The independent test designer (MR-3) wrote these tests from the ticket's KPI lines and DEC-757's, before the
implementation. They go only through public interfaces.

## How they run

```
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
PYTHONPATH=/home/usain/gov-os-worktrees/W2-53/src \
python3 -m pytest tests/acceptance/W2-53 -q -p no:cacheprovider -rs
```

- **This worktree's `src/` (DEC-732).** `w2_53_support.py` reuses W2-01's support unchanged, imported by path,
  and W2-01's support reuses W1-30's. Their sandbox puts the `src/` beside this `tests/` first on the
  `PYTHONPATH` of every process it starts: `gov close`, the close's own pytest runs, and the ratchet's function.
  The support asserts that the three supports agree on that `src/`. The fixture `code_under_test` asserts that
  `src/gov/__init__.py` is there. Set `PYTHONPATH` per command, never in a session's settings.
- **Public interfaces only.** The tests use:
  - `gov close <ticket> --json`, which answers in the API-0002 envelope and exits 3 on a refusal;
  - the path map, ticket files, probe records, the decision register and commit trailers;
  - the ratchet's one public function, run in its own process.

  No test reads a private part of the implementation.
- **Temporary repositories only.** Every project is built from scratch in `tmp_path` by W2-01's `Project`. It
  holds single named files and no folder of this repository. No test reads anything of `governance/project/`.
- **Deterministic, with no network.** A case that "fails under load" uses a stand-in that fails on its first run
  and passes on every later one. Each stand-in writes a record of each run, giving its process and the size of
  its session, into a folder outside the project. There is no real load and no timing.

## The files and the KPIs

Red reasons are as of the base commit `f082bc68`, before the implementation.

| KPI | File and tests | Why it is red today |
|---|---|---|
| **KPI 1** (DEC-750, DEC-754): every later merge holding the probed commit refuses, naming the merge, when a probed path is not git's own merge of its parents. This holds whatever task the merge names, or none; on the integration branch, inward, and for an octopus. | `test_w2_53_later_merges.py`: `…_on_the_integration_branch_…` (5 cases), `…_into_the_tickets_branch_…` (2), `test_an_octopus_merge_…` (2) | The probe gate judges only the merge-back, so the later merges close. The added-file removal, the set-back, both inward cases and the later octopus fail with "gov close was not refused". |
| **KPI 2** (P-5 (c)): a merge taking another ticket's whole version of a probed file is measured the same way. | `test_w2_53_later_merges.py`: `…taking_another_tickets_whole_version_refuses_…` on `main` and inward; `…closes_where_gits_merge_gives_the_same` | The two refusing cases are not refused today. The passing case is a guard and passes. |
| **KPI 3** (DEC-754): a reopened FULL ticket whose earlier round was merged back before its final probe closes when the closed head holds the final probed code. | `test_w2_53_reopened.py` (2 cases) | "brings the final probed code" is refused with PROBE_INVALID: "ticket commit <round one's merge-back> changes src/example/feature.py after the probed commit". The case that keeps round one's code refuses; it is a guard and passes. |
| **KPI 4** (W2-H047, W2-M202): a merge that is git's own merge, and another ticket's merge holding the probed commit on neither side, pass as before. W2-01's cases stay green. | `test_w2_53_later_merges.py`: `test_a_later_merge_that_is_gits_own_merge_of_its_parents_closes` (4 layouts). Also W2-01's own suite. | "Both sides changed one probed file" is refused today with PROBE_INVALID ("in neither parent's version"). The other three layouts are guards and pass. |
| **KPI 5** (DEC-757): a red that `accepted_reds` lists by exact test id, with an ACCEPTED owner decision naming it, a reason and a fixing ticket, does not refuse. The close names it with its decision and fixing ticket. An entry counts only when its adding commit carries `Role: owner`. | `test_w2_53_accepted_reds.py`: `test_listed_reds_with_the_owners_decision_…`, `test_an_entry_whose_test_the_close_did_not_run_…`. `test_w2_53_ratchet_core.py` (7 cases). | There is no list today: every red refuses with CHECK_FAILED, and a closed answer has no `accepted_reds`. `gov.close.ratchet` does not exist (`ModuleNotFoundError`). |
| **KPI 6** (DEC-757): a change to the ticket's file after the probe is no change to the probed code when its commit has `Role: orchestrator` or `owner`, names the ticket in `Task:`, and changes only that file. | `test_w2_53_ticket_file_edits.py`: the orchestrator's edit on the branch; the owner's edit (probe gate only, see P-1); the edit on `main`, merged back only, or merged in and then back | Refused with PROBE_INVALID: "merge-back … brings the probed commit but not the probed code: .tickets/PROJ-tkfl.md differ". |
| **KPI 7** (DEC-757): a listed `load_sensitive` test that fails in the run is run again alone. When it passes alone the close does not refuse, and it reports the run and the re-run. | `test_w2_53_load_sensitive.py`: `…passes_alone_does_not_refuse_…`, `test_a_function_entry_covers_every_parameter_set_…` | Nothing is re-run today (the stand-in shows one run). The close refuses with CHECK_FAILED. |
| **KPI 8**: the orchestrator closes DAEO-7rr2 itself, for real. | **No test.** The orchestrator's real close shows it. | — |
| **Failure 1**: an acceptance test added on the branch before the probe, then removed or changed by a later merge, refuses. | `test_w2_53_later_merges.py`: the "acceptance test removed" and "acceptance test changed" ways | Removal is not refused today. The change case passes today, as a guard. |
| **Failure 2**: a merge whose own merge git cannot compute or read is judged against the probed code and never passes by default. | `test_w2_53_later_merges.py`: `…whose_parents_conflict_…` (resolved to the other side refuses; resolved to the probed version closes); `…git_cannot_read_never_passes` | Resolved to the other side is not refused today. The other two are guards and pass. |
| **Failure 3**: a red off the list refuses. A listed red that passes refuses, naming the entry to remove. An entry without `Role: owner`, or without an ACCEPTED owner decision naming the test id, is refused, naming the entry. | `test_w2_53_accepted_reds.py`: `…does_not_cover_by_its_exact_id…` (5), `…that_passes_refuses_…`, `…the_owner_did_not_add_…` (3), `…without_an_accepted_owner_decision_…` (4). `test_w2_53_ratchet_core.py`. | The 5 uncovered cases refuse today, as guards. The others fail: a listed red that passes closes today, and no ACCEPTED_RED_* finding exists. |
| **Failure 4**: a ticket-file change on the ticket's own side, or an integration-side commit that changes more, still refuses. | `test_w2_53_ticket_file_edits.py`: the engineer's and the test designer's edits; the orchestrator's commit that changes more; the orchestrator's edit naming no task | They refuse today, as guards, and they must stay refused. |
| **Failure 5**: a listed test that fails alone too refuses. A test not on `load_sensitive` is never re-run. An entry without `Role: owner` is refused, naming it. | `test_w2_53_load_sensitive.py`: `…fails_alone_too_refuses…`, `…not_on_load_sensitive_is_never_run_again` (2), `…owner_did_not_add_is_refused…` | There is no re-run and no LOAD_SENSITIVE_* finding today. "On neither list" refuses today, as a guard. |

Counts: 57 tests in 6 files.

| File | Tests | Fail today | Pass today (guards) |
|---|---|---|---|
| later merges | 19 | 10 | 9 |
| reopened | 2 | 1 | 1 |
| ticket-file edits | 8 | 4 | 4 |
| accepted reds | 15 | 10 | 5 |
| ratchet core | 7 | 7 | 0 |
| load-sensitive | 6 | 5 | 1 |

## The forms this suite fixes

Each form is settled here so that the tests can hold to it. The engineer meets each one as stated. A dispute goes
back as a package.

**R-1, the test id.** An entry's `test` is a pytest node id relative to the project's root,
`<file>::<function>[<parameter set>]`. The owner's first entries use this form, for example
`tests/acceptance/W1-42/test_w1_42_exit_report.py::test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]`.

- In `accepted_reds`, an entry covers exactly its own id. These do not cover a red:
  - another parameter set;
  - the bare function;
  - the same name in another file;
  - a prefix of the name.
- In `load_sensitive`, an entry may also be `<file>::<function>`. It then covers every parameter set of that
  function.

The keys and fields are DEC-757's and are never renamed:

- `accepted_reds: [{test, decision, reason, fixed_by}]`
- `load_sensitive: [{test, decision, reason}]`

Both are YAML lists of mappings in the path map.

**R-2, the decision.** An entry's `decision` must be an entry of the project's register whose status is the
owner's acceptance. The status forms are W2-01's: `ACCEPTED (owner, <date>)`, not superseded or revoked. The
decision names a test id when its text holds two things:

- the test's own name, meaning what follows the last `::`, with its parameter set, as a whole word;
- its file path.

A refused entry's finding says why, in these words:

| Why the entry is refused | Words in the finding |
|---|---|
| The decision is not in the register | `no entry` |
| The status is not ACCEPTED | `not accepted` |
| It was accepted by someone other than the owner, such as a delegated decision | `not the owner` |
| The text does not name the test id | `does not name` |

**R-3, the commit that added an entry.** An entry's adding commits are every commit of the closed head's history
whose path map holds the entry (the same `test` and `decision`) while none of its parents' path maps does. Each
adding commit must carry `Role: owner` in its **final trailer block**, as git reads it. A `Role: owner` line
elsewhere in the message does not count.

- An entry that fails this rule, or R-2, does not count. It covers nothing, and it is refused with
  `ACCEPTED_RED_REFUSED` or `LOAD_SENSITIVE_REFUSED`.
- The finding names the entry's test id. In the commit case it also names the adding commit, by its first 7
  characters.
- The owner's other entries still count.

**R-4, what a close reports.**

- **Listed reds.** Under `accepted_reds`, in the result of a close or in the details of a refusal, there is a list
  of reports `{test, decision, reason, fixed_by, result}`. `result` is `"failed"` for a listed red that was red
  in this run (a failure or an error), which is covered, or `"not run"`.
- **A listed red that passes.** It has the finding `ACCEPTED_RED_PASSES`, which names the entry and says to remove
  it.
- **A red off the list.** It keeps today's refusal, which names the test.
- **Re-runs.** Under `load_sensitive` there is a list of reports `{test, decision, in_run, alone}`, where `in_run`
  and `alone` are each `"passed"` or `"failed"`. One report is given per re-run node id. A listed test that fails
  alone too has the finding `LOAD_SENSITIVE_FAILED_ALONE`, which names the test.
- **"Alone".** The test runs in a process of its own whose pytest session holds that one test, one node id per
  process.

**R-5, an entry whose test was not run.** It covers nothing and refuses nothing. The close reports it with
`result: "not run"`. A ticket's close does not run every test, and a removed case is the owner's to drop.

**R-6, the ratchet's core.** The core is one public function, which W2-19 reuses (DEC-757):

```
gov.close.ratchet.apply_accepted_reds(root, results, commit="HEAD") -> dict
```

- `results` maps a test id to one of `passed`, `failed`, `error` or `skipped`. A red is `failed` or `error`; a
  skipped test is no red.
- The function reads the path map, the register and the history at `root`.
- It returns `{"ok": bool, "accepted_reds": [reports as R-4], "findings": [{"code", "test", "message"}]}`.
- The finding codes are `RED_NOT_ACCEPTED`, `ACCEPTED_RED_PASSES` and `ACCEPTED_RED_REFUSED`.
- `gov close` reaches the same verdict through it.

**R-7, "the ticket's own side".** DEC-757 item 3 defines the side by the commit, not by the branch it lies on. A
commit is **integration-side** when all three of these hold:

- its final trailer block carries `Role: orchestrator` or `Role: owner`;
- its `Task:` names the ticket;
- it changes the ticket's file and nothing else.

Every other commit that changes the ticket file after the probe is on the ticket's own side. That includes:

- a worker's commit;
- an integration role's commit that changes more;
- a commit that names no task (DEC-490).

Wherever the integration-side edit lies, on the branch or on `main`, the merges that carry it in are git's own
merges and pass. A refusal of an own-side edit names the edit, or the merge-back that carries it in.

**R-8, a later merge.** These are judged against the probed code:

- a merge git cannot merge without a conflict, judged on its resolution;
- a merge whose objects git cannot read, which never passes.

The refusal names the merge by its first 7 characters in a statement that says "probe". An octopus merge is
measured against git's own merge of all its parents.

## W2-01's cases this ticket touches

The ticket's KPIs touch these W2-01 tests:

- **`test_w2_01_probe_merge_back.py`**, through KPIs 1, 2 and 4: the later-merge cases
  (`test_a_later_merge_back_naming_another_ticket_…`, `test_a_later_merge_holding_the_probed_commit_…`,
  `test_another_tickets_merge_…`, `test_a_later_full_ticket_closes_…`), and every merge-back case, because the
  merge-back is now judged by the same rule.
- **`test_w2_01_probe_rounds.py`**, through KPI 3.
- **`test_w2_01_merge_form.py`**, indirectly, through the merges' trailers.

None of these cases contradicts DEC-754 or DEC-757, and none needs a revision. KPI 4 holds them green.

W1-30's probe tests are touched too. Its r14 case contradicts DEC-757 item 3 (package P-2). The engineer runs W1-30's
suite as well.

## Packages

**P-1. The owner's integration-side edit, against W1-50 (DEC-360, DEC-453).** W1-50's judgement has a finding for
every `Role: owner` commit among a ticket's commits. So a close after the owner's edit of the ticket file does not
succeed, whatever the probe gate decides.

- **Options:**
  - **(a)**, as tested: only the probe gate's part is held, and the owner's edit is no probe finding.
  - **(b)** W1-50, or the close, exempts an owner's integration-side commit. That change lies outside these paths
    and needs its own decision.
  - **(c)** drop the owner variant from KPI 6.
- **Recommendation:** (a), with a row in W1-50's ledger. Confidence: medium.

**P-2. W1-30's r14 test (earlier test, revision needed).** DEC-757 item 3 reverses
`test_a_commit_of_the_ticket_after_the_probed_one_that_changes_its_ticket_file_refuses`, where the commit is an
integration-side edit.

- **Recommendation:** a fresh W1-30 test designer rewrites it with a `Rewrite-Reason:` naming DEC-757. The commit
  becomes an engineer's, and the refusal stays. Confidence: medium-high.

**P-3. A ticket-file edit by an integration role naming another ticket's task.** DEC-757 item 3 does not say
whether such an edit refuses.

- **Options:**
  - **(a)** it refuses, as on the ticket's own side. This is stricter and matches W1-30 P-3 (b).
  - **(b)** it is not judged, as under W1-30's settlement 35.
- **Not tested.**
- **Recommendation:** (a). Confidence: medium.

**P-4. The latency decisions must name their files.** Under R-2, the owner's `load_sensitive` decision must name
each test's own name and its file. A register text that names only the ticket (W1-05) does not count.

- **Options:**
  - the owner writes the file paths into the register entry;
  - the naming rule is relaxed to the test's name alone.
- **Recommendation:** the former. Confidence: medium.
